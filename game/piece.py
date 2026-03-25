from enum import Enum


class Shape(Enum):
    SQUARE = 1
    TRIANGLE = 2
    CIRCLE = 3


class Size(Enum):
    SMALL = 1
    BIG = 2

class Player(Enum):
    WHITE = 0
    BLACK = 1
class Piece:
    orthogonal_dirs = [(1,0), (-1,0), (0,1), (0,-1)]
    diagonal_dirs = [(1,1), (1,-1), (-1,1), (-1,-1)]
    all_dirs = orthogonal_dirs + diagonal_dirs

    shape_directions = {
        Shape.SQUARE: orthogonal_dirs,
        Shape.TRIANGLE: diagonal_dirs,
        Shape.CIRCLE: all_dirs,
    }

    def __init__(self, owner:Player, shape:Shape, size:Size):
        self.owner = owner
        self.shape = shape
        self.size = size

    def get_moves(self, board, x:int, y:int):
        directions = self.shape_directions[self.shape]

        moves = []

        max_steps = 1 if self.size == Size.SMALL else board.size
        
        for dx, dy in directions:
            for step in range(1, max_steps + 1):

                fx = x + dx * step
                fy = y + dy * step

                if not board.in_bounds(fx, fy):
                    break
                
                piece = board.get_piece(fx, fy)

                if piece is not None:
                    if piece.owner != self.owner:
                        moves.append((fx, fy))
                    break
                moves.append((fx, fy))
        return moves