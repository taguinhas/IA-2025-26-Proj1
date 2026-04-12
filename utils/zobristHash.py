from game.piece import Shape, Size, Player
import random

"""
Taken from https://en.wikipedia.org/wiki/Zobrist_hashing
adapted to alapo by our group
"""
class Zobrist:

    def __init__(self, size = 6):
        # fill a table of random numbers/bitstrings
        #table := a 2-d array of size 64×12
        self.table = [[random.getrandbits(64) for _ in  range(12)] for _ in range(size * size)]

        self.size = size 

        self.black_to_move = random.getrandbits(64)

    def get_piece_idx(self, piece):
        indices = {
            (Player.WHITE, Size.SMALL, Shape.TRIANGLE): 0,
            (Player.WHITE, Size.SMALL, Shape.SQUARE): 1,
            (Player.WHITE, Size.SMALL, Shape.CIRCLE): 2,
            (Player.WHITE, Size.BIG, Shape.TRIANGLE): 3,
            (Player.WHITE, Size.BIG, Shape.SQUARE): 4,
            (Player.WHITE, Size.BIG, Shape.CIRCLE): 5,
            (Player.BLACK, Size.SMALL, Shape.TRIANGLE): 6,
            (Player.BLACK, Size.SMALL, Shape.SQUARE): 7,
            (Player.BLACK, Size.SMALL, Shape.CIRCLE): 8,
            (Player.BLACK, Size.BIG, Shape.TRIANGLE): 9,
            (Player.BLACK, Size.BIG, Shape.SQUARE): 10,
            (Player.BLACK, Size.BIG, Shape.CIRCLE): 11,
        }
        return indices[(piece.owner, piece.size, piece.shape)]
    
    def hash(self, board, cur_player:Player):
        """return has for a given board"""
        #h := 0
        h = 0
        if cur_player == Player.BLACK:
            #h := h XOR table.black_to_move
            h = h ^ self.black_to_move
        for i in range(self.size):      # loop over the board positions
            for j in range(self.size):
                piece = board[i][j]
                if piece:
                    index = self.get_piece_idx(piece)
                    h = h ^ self.table[i*self.size + j][index]
                    #j := the piece at board[i], as listed in the constant indices, above
        return h
    
    def get_piece_hash(self, piece, x, y):
        return self.table[x + y* self.size][self.get_piece_idx(piece)]
    