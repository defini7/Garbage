from enum import Enum


Coord = tuple[int, int]

class Algo(Enum):
    BFS = 0
    DFS = 1


DIRS = [(1, 0), (0, 1), (-1, 0), (0, -1)]


class Node:
    def __init__(self, state: Coord, parent=None):
        self.state = state
        self.parent = parent
        

class AStarNode(Node):
    def __init__(self, state: Coord, parent=None, local_dist=float('+inf'), global_dist=float('+inf')):
        super().__init__(state, parent)

        # Distance from the S point to that node
        self.local_dist = local_dist

        # self.local_dist + distance to the G node
        self.global_dist = global_dist
        
        self.visited = False


class StackFrontier:
    def __init__(self):
        self.data = []

    def contains(self, state: Coord):
        return any(state == n.state for n in self.data)

    def push(self, value):
        self.data.append(value)

    def pop(self):
        return self.data.pop()
    
    def empty(self):
        return len(self.data) == 0
    

class QueueFrontier(StackFrontier):
    def pop(self):
        return self.data.pop(0)
    

def heuristic(state1: Coord, state2: Coord) -> int:
    # Let's use the manhattan distance as a heuristic

    (x1, y1), (x2, y2) = state1, state2
    return abs(x2 - x1) + abs(y2 - y1)

    
class Maze:
    def __init__(self, filename):
        self.load(filename)

        self.solution = []

    def load(self, filename):
        with open(filename) as file:
            data = [l[:-1] if l[-1] == '\n' else l for l in file.readlines()]
        
        self.width = len(data[0])
        self.height = len(data)

        self.obstacles = []

        for y in range(self.height):
            row = []

            for x in range(self.width):
                match data[y][x]:
                    case 'S':
                        self.start = (x, y)
                        row.append(False)

                    case 'G':
                        self.goal = (x, y)
                        row.append(False)

                    case ' ': row.append(False)
                    case _: row.append(True)

            self.obstacles.append(row)
        
    def find_new_states(self, state: Coord) -> list[Coord]:
        x, y = state
        states = []

        for dir in DIRS:
            nx, ny = x + dir[0], y + dir[1]

            if 0 <= nx < self.width and 0 <= ny < self.height and not self.obstacles[ny][nx]:
                states.append((nx, ny))

        return states
    
    # Searches for a path from point S to point G,
    # notice that if there is more than one path,
    # then it will find only one of them and it
    # IS NOT guaranteed that it will be the optimal one.

    # Notice that it's called uninformed search simply
    # because we don't take into account anything related to our
    # problem except the all possible directions

    # In the informed search we would also take into account a
    # position of the goal node
    def uninformed_search(self, algo: Algo):
        self.explored_count = 0

        # The frontier is a data structure that can be either a stack or a queue,
        # it simply stores nodes that we want to explore.
        # By using the stack we apply DFS (depth-first search)
        # algorithm that simply visits the deepest node in the frontier, and by using
        # the queue we apply BFS (breadth-first search) algorithm that always expands the
        # shallowest node in the frontier, i.e. the next node to be explored is the earliest node
        # that was added to the frontier.
        # The "real world" difference is that in the unweighted graph (that we have) it IS guaranteed
        # that BFS will find the shortest path to the goal but there is NO guarantee that BFS will be faster
        # than DFS or vice-versa. So it's like a one-armed bandit

        match algo:
            case Algo.BFS: frontier = QueueFrontier()
            case Algo.DFS: frontier = StackFrontier()
            case _: raise Exception('The specified algorithm type is corrupted')

        # We want to avoid visiting cells more than once
        # so let's keep track of them, this approach is called "revised"
        visited = set()

        # Push the first cell into the frontier
        frontier.push(Node(self.start))

        while not frontier.empty():
            # Taking a node from the frontier
            node = frontier.pop()

            if node.state == self.goal:
                # We've reached the goal so lets save a path to it
                self.solution.clear()

                while node.parent:
                    self.solution.insert(0, node.state)
                    node = node.parent

                return True

            # Mark the node as explored
            visited.add(node.state)
            self.explored_count += 1

            # Append a new state to the frontier
            for s in self.find_new_states(node.state):
                if s not in visited and not frontier.contains(s):
                    frontier.push(Node(s, node))

        # The frontier is empty and we haven't found our path yet
        # so there is no path
        return False
    
    # AStar is a type of informed search algorithm because it knows the position
    # of each node in a graph and especially the position of its goal.

    # The approach here is to use the same GBFS algorithm as before but now we don't
    # choose the node to go next only relying on the heuristic function, now we also
    # take into the account an amount of steps that it took us to get to the cell
    # that we are about to visit, so on each iteration we calculate a distance to each neighbour
    # of the node taken from the frontier and see if the amount of steps that took us to get to
    # the neighbour from our current cell is less than the number of steps that took use to get
    # to the same neighbour previously from another node we update the neighbour's number of steps
    # from the beginning to get to that specific state (let's call that number - local distance),
    # so then we also update its global distance, i.e. the local distance + the heuristic of that
    # neighbouring node and the goal node and then if we haven't visited that neighbour yet we
    # add it to the frontier but at the end of the iteration of the loop it's very important to
    # set move the node with the minimum global distance to the front of the queue so we can
    # explore the nearest node to the goal (according to the heuristic function) firstly.

    def astar_search(self):
        self.explored_count = 0

        frontier = QueueFrontier()
        frontier.push(AStarNode(self.start, local_dist=0, global_dist=heuristic(self.start, self.goal)))

        visited = set()

        while not frontier.empty():
            node = frontier.pop()

            if node.state == self.goal:
                # We've reached the goal and the found path
                # is the shortest one

                self.solution.clear()

                # Lets construct the path
                while node.parent:
                    self.solution.insert(0, node.state)
                    node = node.parent

                return True

            visited.add(node.state)
            self.explored_count += 1

            dist_to_neighbour = node.local_dist + 1

            # Exploring all neighbours of the current node
            for s in self.find_new_states(node.state):
                n = AStarNode(s, node)

                # If the distance of the neighbour from the S node is
                # less than the distance from our current node then ...
                if dist_to_neighbour < n.local_dist:
                    # ... we update the neighbour's parent, its distance to the S node
                    # and its global distance = distance to the S node + distance to the G node
                    n.parent = node
                    n.local_dist = dist_to_neighbour
                    n.global_dist = n.local_dist + heuristic(s, self.goal)

                # We don't want to explore already visited nodes and we don't want to explore nodes
                # that are already must be explored
                if s not in visited and not frontier.contains(s):
                    frontier.push(n)

            # Sorting the frontier by the global goal in descending order
            # so on the next iteration we pick the nearest
            # node to the G node (according to the heuristic function)
            #frontier.data.sort(key=lambda n: n.global_dist)

            # ... or we can find the minima in the frontier and move it into the front
            if not frontier.empty():
                minima = min(frontier.data, key=lambda n: n.global_dist)

                frontier.data.remove(minima)
                frontier.data.insert(0, minima)


    def print(self):
        for y in range(self.height):
            for x, obstacle in enumerate(self.obstacles[y]):
                if obstacle:
                    print('#', end='')
                elif self.start == (x, y):
                    print('S', end='')
                elif self.goal == (x, y):
                    print('G', end='')
                elif (x, y) in self.solution:
                    print('+', end='')
                else:
                    print(' ', end='')
            print()


if __name__ == '__main__':
    from sys import argv, exit

    if len(argv) < 2:
        print('Usage: python maze.py <file>')
        exit(1)

    maze = Maze(argv[1])

    print('Before:')
    maze.print()

    maze.astar_search()
    print()
    print('Explored: ', maze.explored_count)

    print('\nAfter:')
    maze.print()

# But the problem with the BFS and DFS algorithms is that
# they can be slow because they are uninformed of the distance
# to the goal so they can make a wrong decision, i.e. they can
# choose a longer path.

# So here comes GBFS (Gready best-first search) algorithm that
# uses a thing called heuristic that helps us to get the approximate
# distance to the goal from the current state, most of the time we
# can use manhattan distance as a heuristic because it's easy to calculate
# in terms of performance and it fullfills next constraints for the heuristic function:
# 1) heuristic MUST NEVER overestimate the real distance between current state and the goal
# 2) for every n and for every n' with the step cost of c
#    where n' is the next node (state) after the n and
#    if h(n) is the heuristic function then h(n) <= h(n') + c
# Then we use this heuristic function to calculate the distance between each state and the goal state
# (in case of mazes we ignore every wall) and then we make a decission in what direction we should go
# simply by choosing the lowest value of the heuristic function among the node's neighbours.

# However sometimes this approach won't work, i.e. it can produce us a longer path or it can take more time
# than by using the BFS or DFS algorithms.

# Now we can try a different approach: let's take into account not only the heuristic but also a number of
# steps that it requires to get to the point with that heuristic, this algorithm is called A* (A-star).
