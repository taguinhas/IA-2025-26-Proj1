from Board import Board
from Piece import Piece, Owner, Size, Shape

class Game:
    def __init__(self):
        """
        Creates game with 6x6 board and populates it.
        """
        self.board = Board(6)
        self.populate_board()

    def populate_board(self):
        shapes = [Shape.SQUARE, Shape.TRIANGLE, Shape.CIRCLE, Shape.CIRCLE, Shape.TRIANGLE, Shape.SQUARE]
        for x, shape in enumerate(shapes):
            #Big white pieces
            self.board.place_piece(Piece(Owner.WHITE, shape, Size.BIG),x, 0)

            #Small white pieces
            self.board.place_piece(Piece(Owner.WHITE, shape, Size.SMALL),x, 1)

            #Big black pieces
            self.board.place_piece(Piece(Owner.BLACK, shape, Size.BIG),x, 5)

            #Small black pieces
            self.board.place_piece(Piece(Owner.BLACK, shape, Size.SMALL),x, 4)

    def print_board(self):
        shape_map = {
            Shape.SQUARE: "S",
            Shape.TRIANGLE: "T",
            Shape.CIRCLE: "C",
        }
        
        board_str = ""
        
        for y in range(self.board.size):
            row_str = ""

            for x in range(self.board.size):
                piece = self.board.get_piece(x,y)

                if piece is None:
                    row_str += " . "
                
                else:
                    owner = "W" if piece.owner == Owner.WHITE else "B"
                    shape = shape_map[piece.shape]
                    
                    if piece.size == Size.BIG:
                        row_str += owner + shape + " "
                    else:
                        row_str += owner.lower() + shape.lower() + " "
            
            board_str = row_str + "\n" + board_str
        
        print(board_str)
                    
