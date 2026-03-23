from game.game import Game
from game.board import Board
from game.piece import Shape, Size, Owner, Piece

def material_eval_board(board:Board) ->int:
    boardValue = 0
    shapeFactors = {
        Shape.TRIANGLE:1,
        Shape.SQUARE:2,
        Shape.CIRCLE:3
    }

    
    for line in board.board:
        for piece in line:
            if piece is not None:
                shapeFactor = shapeFactors[piece.shape]
                sizeFactor = 3 if piece.size == Size.BIG else 1
                ownerFactor = 1 if piece.owner == Owner.WHITE else -1
                boardValue += shapeFactor * sizeFactor * ownerFactor
    return boardValue

            