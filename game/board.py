from game.piece import Piece, Player, Move

class InvalidMoveError(Exception):
    """Raised when a move violates game rules."""
    pass

class Board:
    def __init__(self, size:int):
        """
        Create an empty Board, must place pieces with Board.place_piece()
        """
        self.size = size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.game_over = False

    def in_bounds(self, x:int, y:int) -> bool:
        """Check if a position is within the bounds of the Board"""
        return x >= 0 and x < self.size and y >= 0 and y < self.size

    def is_occupied(self, x:int, y:int) -> bool:
        """Check if position on the Board is occupied"""
        return self.board[y][x] is not None
    
    def place_piece(self, piece:Piece, x:int, y:int):
        """Place a piece on the Board, if position is already occupied old piece gets overwritten and returned"""
        self.board[y][x] = piece

    def remove_piece(self, x:int, y:int):
        """Clear position at position"""
        self.board[y][x] = None
    
    def get_piece(self, x:int, y:int) -> Piece:
        """Get Piece at position"""
        if(self.in_bounds(x, y)):
            return self.board[y][x]
        return None
    
    def move_piece(self, move:Move):
        """Moves piece. requires "Move" Object. Returns captured piece"""
        if not self.in_bounds(move.fx, move.fy):
            raise InvalidMoveError(f"Board.move_piece: Final position ({move.fx}, {move.fy}) out of Bounds for Board of size {self.size}")
        
        moving = self.get_piece(move.ix, move.iy)
        if moving is None:
            raise InvalidMoveError(f"Board.move_piece: No piece at initial position ({move.ix}, {move.iy})")

        captured = self.get_piece(move.fx, move.fy)
        if captured is not None and captured.owner == moving.owner:
            raise InvalidMoveError(f"Board.move_piece: Cannot capture your own piece. Pos:({move.fx}, {move.fy})")
        self.place_piece(moving, move.fx, move.fy)
        self.remove_piece(move.ix,move.iy)

        return captured
        
    def get_attack_map(self, attacker: Player):
        """
        return a set with all the squares being attacked by attacker. usefull for goal check and heuristics
        """
        attacked = [[0 for _ in range(self.size)] for _ in range(self.size)]

        for y in range(self.size):
            for x in range(self.size):
                piece = self.get_piece(x, y)

                if piece is None or piece.owner != attacker:
                    continue

                moves = piece.get_moves(self, x, y)
                for move in moves:
                    attacked[move.fy][move.fx] += 1

        return attacked

    def available_moves(self, player:Player) -> list:
        moves = list()
        for y in range(self.size):
            for x in range(self.size):
                piece = self.get_piece(x, y)

                if piece is None or piece.owner != player:
                    continue

                moves += piece.get_moves(self, x, y)
        return moves

        
    def check_winner(self):
        white_attacks = self.get_attack_map(Player.WHITE)
        black_attacks = self.get_attack_map(Player.BLACK)

        #home attack win
        for x in range(self.size):
            #white goal
            piece = self.get_piece(x, 0)
            if piece and piece.owner == Player.WHITE:
                if black_attacks[0][x] == 0:
                    self.game_over = True
                    return Player.WHITE

            #black goal
            piece = self.get_piece(x, self.size - 1)
            if piece and piece.owner == Player.BLACK:
                if white_attacks[self.size - 1][x] == 0:
                    self.game_over = True
                    return Player.BLACK

        #elimination win
        has_white = False
        has_black = False

        for row in self.board:
            for piece in row:
                if piece:
                    if piece.owner == Player.WHITE:
                        has_white = True
                    else:
                        has_black = True

        if not has_white:
            self.game_over = True
            return Player.BLACK
        if not has_black:
            self.game_over = True
            return Player.WHITE

        return None