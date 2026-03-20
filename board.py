from Piece import Piece
class Board:
    def __init__(self, size:int):
        """
        Create an empty Board, must place pieces with Board.place_piece
        """
        self.size = size
        self.board = [[None for _ in range(size)] for _ in range(size)]


    def in_bounds(self, x:int, y:int) -> bool:
        """Check if a position is within the bounds of the Board"""
        return x >= 0 and x < self.size and y >= 0 and y < self.size

    def is_occupied(self, x:int, y:int) -> bool:
        """Check if position on the Board is occupied"""
        return self.board[y][x] is not None
    
    def place_piece(self, piece:Piece, x:int, y:int):
        """Place a piece on the Board, if position is already occupied old piece gets overwritten and returned"""
        old_piece = self.board[y][x]
        self.board[y][x] = piece
        return old_piece

    def remove_piece(self, x:int, y:int):
        """Clear position at position"""
        self.board[y][x] = None
    
    def get_piece(self, x:int, y:int):
        """Get Piece at position"""
        if(self.in_bounds(x, y)):
            return self.board[y][x]
        return None
    
    def move_piece(self, ix:int, iy:int, fx:int, fy:int):
        """Moves piece from (ix, iy) to (fx, fy). Returns captured piece"""
        if not self.in_bounds(fx, fy):
            raise ValueError(f"Board.move_piece: Final position ({fx}, {fy}) out of Bounds for Board of size {self.size}")
        
        moving = self.get_piece(ix, iy)
        if moving is None:
            raise ValueError(f"Board.move_piece: No piece at initial position ({ix}, {iy})")

        captured = self.place_piece(moving, fx, fy)
        if captured is not None and captured.owner == moving.owner:
            raise ValueError(f"Board.move_piece: Cannot capture your own piece. Pos:({fx}, {fy})")
        self.remove_piece(ix,iy)

        return captured
        