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
        self.white_count = 0
        self.black_count = 0
        self._white_attack_map = None
        self._black_attack_map = None
        self._atk_maps_updated = False

    def in_bounds(self, x:int, y:int) -> bool:
        """Check if a position is within the bounds of the Board"""
        return x >= 0 and x < self.size and y >= 0 and y < self.size

    def is_occupied(self, x:int, y:int) -> bool:
        """Check if position on the Board is occupied"""
        return self.board[y][x] is not None
    
    def place_piece(self, piece:Piece, x:int, y:int):
        """Place a piece on the Board, if position is already occupied old piece gets overwritten and returned"""
        self.board[y][x] = piece
        self.add_count(piece)

        self._atk_maps_updated = False


    def remove_piece(self, x:int, y:int):
        """Clear position at position"""

        piece = self.get_piece(x, y)
        self.sub_count(piece)

        self.board[y][x] = None
        self._atk_maps_updated = False
    
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
        self.sub_count(captured)

        self.place_piece(moving, move.fx, move.fy)
        self.remove_piece(move.ix,move.iy)

        return captured
        
    def _update_attack_map(self):
        """
        return a set with all the squares being attacked by attacker. usefull for goal check and heuristics
        """
        white_attacks = [[0 for _ in range(self.size)] for _ in range(self.size)]
        black_attacks = [[0 for _ in range(self.size)] for _ in range(self.size)]
        for y in range(self.size):
            for x in range(self.size):
                piece = self.get_piece(x, y)

                if piece is None:
                    continue

                moves = piece.get_moves(self, x, y)
                if(piece.owner == Player.WHITE):
                    for move in moves:
                        white_attacks[move.fy][move.fx] += 1
                else:
                    for move in moves:
                        black_attacks[move.fy][move.fx] += 1
        self._white_attack_map = white_attacks
        self._black_attack_map = black_attacks
        self._atk_maps_updated = True       


    def available_moves(self, player:Player) -> list:
        player_moves = list()
        white_attacks = [[0 for _ in range(self.size)] for _ in range(self.size)]
        black_attacks = [[0 for _ in range(self.size)] for _ in range(self.size)]

        for y in range(self.size):
            for x in range(self.size):
                piece = self.get_piece(x, y)

                if piece is None:
                    continue
                
                #this logic is not needed for available moves, 
                #however since we need to run this a lot for the ai it might be worth to caculate here anyways
                moves = piece.get_moves(self, x, y)
                if(piece.owner == Player.WHITE):
                    for move in moves:
                        white_attacks[move.fy][move.fx] += 1
                else:
                    for move in moves:
                        black_attacks[move.fy][move.fx] += 1

                if piece.owner == player:
                    player_moves += moves

        self._white_attack_map = white_attacks
        self._black_attack_map = black_attacks
        self._atk_maps_updated = True       

        return player_moves

    def get_white_attack_map(self):
        if not self._atk_maps_updated:
            self._update_attack_map()
        return self._white_attack_map
    
    def get_black_attack_map(self):
        if not self._atk_maps_updated:
            self._update_attack_map()
        return self._black_attack_map
        
    def check_winner(self):
        #elimination win
        if self.white_count == 0:
            return Player.BLACK
        if self.black_count == 0:
            return Player.WHITE
        
        

        white_goal = 0
        black_goal = self.size - 1
        #home attack win
        for x in range(self.size):
            #white goal
            piece = self.get_piece(x, white_goal)
            if piece and piece.owner == Player.WHITE:
                black_attacks = self.get_black_attack_map()
                if black_attacks[white_goal][x] == 0:
                    return Player.WHITE

            #black goal
            piece = self.get_piece(x, black_goal)
            if piece and piece.owner == Player.BLACK:
                white_attacks = self.get_white_attack_map()
                if white_attacks[black_goal][x] == 0:
                    return Player.BLACK

        return None
    
    def undo_move(self, move: Move, captured_piece: Piece):
        """Reverses a move and restores any captured piece"""
        moving_piece = self.get_piece(move.fx, move.fy)

        self.board[move.iy][move.ix] = moving_piece
        self.board[move.fy][move.fx] = captured_piece
    
        if captured_piece:
            self.add_count(captured_piece)

        self._atk_maps_updated = False


    def copy(self):
        new_board = Board(self.size)
        new_board.board = [row[:] for row in self.board]
        new_board.white_count = self.white_count
        new_board.black_count = self.black_count
        return new_board
    
    def add_count(self, piece:Piece):
        if piece:
            if piece.owner == Player.WHITE:
                self.white_count += 1
            else:
                self.black_count += 1

    def sub_count(self, piece:Piece):
        if piece:
            if piece.owner == Player.WHITE:
                self.white_count -= 1
            else:
                self.black_count -= 1