DIRS = [(1, 0), (0, 1), (-1, 0), (0, -1)]


class Node:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent


class StackFrontier:
    def __init__(self):
        self.data = []

    def contains(self, state: tuple[int, int]):
        return any(state == n.state for n in self.data)

    def push(self, value: Node):
        self.data.append(value)

    def pop(self) -> Node:
        return self.data.pop()
    
    def empty(self):
        return len(self.data) == 0
    

class QueueFrontier(StackFrontier):
    def pop(self) -> Node:
        return self.data.pop(0)

    
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
        
    def find_new_states(self, state) -> list[tuple[int, int]]:
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
    def uninformed_search(self):
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
        frontier = QueueFrontier() # StackFrontier()

        # We want to avoid visiting cells more than once
        # so let's keep track of them, this approach is called "revised"
        visited = set()

        # Push the first cell into the frontier
        frontier.push(Node(self.start))

        while True:
            if frontier.empty():
                # The frontier is empty and we haven't found our path yet
                # so there is no path
                return False
            
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


maze = Maze('maze1.txt')

print('Before:')
maze.print()

maze.uninformed_search()
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

# Let the heuristic be h(n) and the number of steps be g(n), let's explore their sum: h(n) + g(n).
# Now let's start from the initial state and go deeper into the maze. In BFS we were choosing the next node
# to explore in a random direction but in this case we will choose it based on h(n) + g(n) value for each node
# by choosing the minimum of them.
