from move import Move
from pprint import pprint

class GridPlayer:

    def __init__(self):
        self.counter = 0
        pass

    def tick(self, game_map, your_units, enemy_units, resources, turns_left):
        moves = []

        if self.counter == 15:
            moves.append(Move('1', 'MINE', 'DOWN'))
        else:
            moves.append(Move('1', 'DOWN'))

        self.counter += 1

        return moves
