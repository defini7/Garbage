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
        # If some of the nodes are blank then the game hasn't been over yet
        for y in range(3):
            for x in range(3):
                if self.data[y][x] == Player.N:
                    return None

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
    
    def min_value(self) -> int:
        term = self.terminal()

        if term is not None:
            # The game has been over
            return int(term)
        
        minima = 1 # since the highest possible value is 1

        # Find the lowest value among all actions since we are X
        for x, y in self.actions():
            # Build a new possible state
            cur_state = deepcopy(self.data)
            cur_state[y][x] = Player.X
            
            new_state = State(cur_state, Player.O)

            # Get the value of the next state and compare it
            minima = min(minima, new_state.max_value())

        return minima

    def max_value(self) -> int:
        term = self.terminal()

        if term is not None:
            # The game has been over
            return int(term)
        
        maxima = -1 # since the lowest possible value is -1

        # Find the highest value among all actions since we are O
        for x, y in self.actions():
            # Build a new possible state
            cur_state = deepcopy(self.data)
            cur_state[y][x] = Player.O
            
            new_state = State(cur_state, Player.X)

            # Get the value of the next state and compare it
            maxima = max(maxima, new_state.min_value())

        return maxima


class Game:
    def __init__(self, initial_state=None, turn=None):
        self.state = State(initial_state, turn)

    def simulate(self):
        if self.state.turn == Player.X:
            winner = self.state.min_value()
        else:
            winner = self.state.max_value()

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
    

g = Game(construct_raw_state(read_file('state3_o.txt')), Player.O)
g.simulate()
