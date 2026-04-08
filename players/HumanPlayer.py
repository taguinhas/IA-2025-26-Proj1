from utils import user_to_board_coords, player_names, size_names, shape_names
from game.game import Game
from game.board import Board, InvalidMoveError
from players.player import genericPlayer

class HumanPlayer(genericPlayer):
    def get_player_move(self, game:Game):
        board = game.board
        print("Which piece to move?(bottom left is (0,0))")
        user_ix = int(input("col number:"))
        user_iy = int(input("line number:"))

        board_ix, board_iy = user_to_board_coords(board, user_ix, user_iy)

        piece = board.get_piece(board_ix, board_iy)
        if piece is None:
            raise InvalidMoveError(f"No piece at ({user_iy}, {user_ix})")


        print(f"Moving {player_names[piece.owner]} {size_names[piece.size]} {shape_names[piece.shape]} at ({user_ix}, {user_iy})")
        available_moves = piece.get_moves(board, board_ix, board_iy)

        if(len(available_moves) == 0):
            raise InvalidMoveError("Piece has no available moves")

        print("Available moves:")
        for x, y in available_moves:
            user_x, user_y = user_to_board_coords(board, x, y)
            print(f"({user_x}, {user_y})")
        
        print("Move to where?")
        user_fx = int(input("col number:"))
        user_fy = int(input("line number:"))

        board_fx, board_fy = user_to_board_coords(board, user_fx, user_fy)

        if (board_fx, board_fy) not in available_moves:
            raise InvalidMoveError("Invalid destination for that piece")
        
        return board_ix, board_iy, board_fx, board_fy
