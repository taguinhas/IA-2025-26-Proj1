from game.board import Board
from game.piece import Piece, Player, Size, Shape
class Game:
    def __init__(self):
        """
        Creates game with 6x6 board and populates it.
        """
        self.board = Board(6)
        self.populate_board()
        self.cur_player = Player.WHITE

    def populate_board(self):
        shapes = [Shape.SQUARE, Shape.TRIANGLE, Shape.CIRCLE, Shape.CIRCLE, Shape.TRIANGLE, Shape.SQUARE]
        for x, shape in enumerate(shapes):
            #Big white pieces
            self.board.place_piece(Piece(Player.WHITE, shape, Size.BIG),x, 5)

            #Small white pieces
            self.board.place_piece(Piece(Player.WHITE, shape, Size.SMALL),x, 4)

            #Big black pieces
            self.board.place_piece(Piece(Player.BLACK, shape, Size.BIG),x, 0)

            #Small black pieces
            self.board.place_piece(Piece(Player.BLACK, shape, Size.SMALL),x, 1)

    def print_board(self):
        shape_map = {
            Shape.SQUARE: "S",
            Shape.TRIANGLE: "T",
            Shape.CIRCLE: "C",
        }
        
        for y in range(self.board.size):
            row_str = ""

            for x in range(self.board.size):
                piece = self.board.get_piece(x,y)

                if piece is None:
                    row_str += " . "
                
                else:
                    owner = "W" if piece.owner == Player.WHITE else "B"
                    shape = shape_map[piece.shape]
                    
                    if piece.size == Size.BIG:
                        row_str += owner + shape + " "
                    else:
                        row_str += owner.lower() + shape.lower() + " "
            print(row_str)
                    
    def load_board_from_file(self, filename: str):
        shape_map = {
            "S": Shape.SQUARE,
            "T": Shape.TRIANGLE,
            "C": Shape.CIRCLE,
        }
    
        owner_map = {
            "W": Player.WHITE,
            "B": Player.BLACK,
        }
    
        with open(filename, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
    
        # Reset board
        self.board = Board(self.board.size)
    
        for y, line in enumerate(lines):
            tokens = line.split()
    
            for x, token in enumerate(tokens):
                if token == ".":
                    continue
                try:
                    owner = owner_map[token[0].upper()]
                    shape = shape_map[token[1].upper()]
                except KeyError:
                    raise Exception("Unrecognized token:" + token)
                
                size = Size.BIG if token.isupper() else Size.SMALL
    
                piece = Piece(owner, shape, size)
                self.board.place_piece(piece, x, y)