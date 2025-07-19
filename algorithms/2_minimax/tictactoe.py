from enum import Enum
from copy import deepcopy


class Player(Enum):
    X = -1
    N = 0
    O = 1

    def __int__(self):
        return self._value_
    

class State:
    def __init__(self, raw=None, turn=None):
        if raw is None:
            self.data = [
                [Player.N, Player.N, Player.N],
                [Player.N, Player.N, Player.N],
                [Player.N, Player.N, Player.N]
            ]
        else:
            self.data = raw

        # Let X start by default
        self.turn = Player.X if turn is None else turn

    # Returns the pair (x_won, o_won) or None if it is not a terminal state
    def terminal(self) -> Player | None:
        # Since we mark X as -1 and O as 1 let's
        # just sum up all values for each direction on the board
        # and if the sum is -3 then X wins, if the sum is 3 then
        # O wins, if there is neither 3 nor -3 then it's a tie

        # Check sums horizontally and vertically
        for i in range(3):
            # Horizontal sum
            h = sum(int(n) for n in self.data[i])

            # Vertical sum
            v = sum(int(self.data[j][i]) for j in range(3))

            # Either X or O won
            if -3 in (h, v): return Player.X
            if +3 in (h, v): return Player.O
            
        # Main diagonal sum
        d1 = sum(int(self.data[i][i]) for i in range(3))

        # Anti-diagonal sum
        d2 = sum(int(self.data[i][2 - i]) for i in range(3))

        # Somebody can also win with a filled diagonal
        if -3 in (d1, d2): return Player.X
        if +3 in (d1, d2): return Player.O

        if any(val == Player.N
            for row in self.data
            for val in row):
            return None
        
        # It's a tie
        return Player.N
    
    # Get all possible actions on this state, i.e. coordinates of each possible move
    def actions(self) -> list[tuple[int, int]]:
        res = []

        for y in range(3):
            for x in range(3):
                if self.data[y][x] == Player.N:
                    res.append((x, y))

        return res
    
    
    def min_value(self, max_value: int, min_value: int) -> int:
        term = self.terminal()

        if term is not None:
            # The game has been over
            return int(term)
        
        minima = 1 # since the highest possible value is 1

        # Find the lowest value among all actions since we are X
        for x, y in self.actions():
            # Build a new possible state
            new_data = deepcopy(self.data)
            new_data[y][x] = Player.X
            
            new_state = State(new_data, Player.O)

            # Get the value of the next state and compare it
            minima = min(minima, new_state.max_value(max_value, min_value))

            # HOWEVER, searching through all possible actions of the state is quite complex in terms
            # of computations so we can use a technique called Alpha-Beta pruning that in this case
            # allows us to upper-bound the value of the state based on the following actions of that state

            # Example:
            #            4                <- maximizer
            #   4       <=3      <=2      <- minimizer
            # 4 8 5    9 3 _    2 _ _     <- maximizer

            # You can see that in this case we didn't calculate the value of the third state
            # because we already have 3 that tells us that the minimum value of the previous state
            # is less than 3 and we know that the first value of the minimizer state is 4 so
            # we can be sure that we will pick at least 4 and in any case we won't pick the second action,
            # the same thing applies to the third state, i.e. its value is less than 2 so it becomes obvious
            # that we won't pick this path because we already have 4 as the first option (4 > 2)

            # In this case we've found it
            min_value = min(min_value, minima)

            if minima <= max_value:
                break

        return minima

    def max_value(self, max_value: int, min_value: int) -> int:
        term = self.terminal()

        if term is not None:
            # The game has been over
            return int(term)
        
        maxima = -1 # since the lowest possible value is -1

        # Find the highest value among all actions since we are O
        for x, y in self.actions():
            # Build a new possible state
            new_data = deepcopy(self.data)
            new_data[y][x] = Player.O
            
            new_state = State(new_data, Player.X)

            # Get the value of the next state and compare it
            maxima = max(maxima, new_state.min_value(max_value, min_value))

            # The same Alpha-Beta pruning technique as in min_value method but now
            # we apply it to the maximizer

            max_value = max(max_value, maxima)

            if maxima >= min_value:
                break

        return maxima


class Game:
    def __init__(self, initial_state=None, turn=None):
        self.state = State(initial_state, turn)

    def simulate(self):
        if self.state.turn == Player.X:
            winner = self.state.min_value(-1, 1)
        else:
            winner = self.state.max_value(-1, 1)

        match Player(winner):
            case Player.X: print('X won!')
            case Player.O: print('O won!')
            case Player.N: print('Tie!')


def construct_raw_state(raw: list[str]) -> list[list[Player]]:
    res = []

    for y in range(3):
        res.append([])

        for x in range(3):
            match raw[y][x]:
                case 'x': res[y].append(Player.X)
                case 'o': res[y].append(Player.O)
                case ' ': res[y].append(Player.N)

    return res


def read_file(filename: str) -> list[str]:
    with open(filename) as file:
        return [l[:-1] if l[-1] == '\n' else l for l in file.readlines()]
    

# WARNING! Don't use a blank state as an initial state because remember
# that there are 255168 possible states of tic-tac-toe game starting from the blank state

if __name__ == '__main__':
    from sys import argv, exit
    
    if len(argv) < 3:
        print('Usage: python3 tictactoe.py <file> <winner>')
        exit(1)

    match argv[2].lower():
        case 'x': winner = Player.X
        case 'o': winner = Player.O
        case _:
            print('Invalid winner, possible values: X/x, O/o')
            exit(1)


    g = Game(construct_raw_state(read_file(argv[1])), winner)
    g.simulate()

    # TODO: print the winning strategy
