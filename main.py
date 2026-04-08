from game.game import Game
from game.board import Board, InvalidMoveError
from game.piece import Piece, Player, Size, Shape

from players.player import genericPlayer
from players.humanPlayer import HumanPlayer
from players.minimaxPlayer import MinimaxPlayer

from utils import player_names, size_names, shape_names

game = Game()

modes = {
    0: "Human vs Human",
    1: "Human vs MiniMax",
    2: "MiniMax vs MiniMax"
}
game_mode = -1

white_player = HumanPlayer()
black_player = HumanPlayer()

while(game_mode == -1):
    print("Choose game type:")
    for key, value in modes.items():
        print(str(key) + ": " + value)

    choice = int(input())
    match choice:
        case 0:
            white_player = HumanPlayer()
            black_player = HumanPlayer()
            game_mode = 0

        case 1:
            white_player = HumanPlayer()
            black_player = MinimaxPlayer()
            game_mode = 1

        case 2:
            white_player = MinimaxPlayer()
            black_player = MinimaxPlayer()
            game_mode = 2 


while(True):
    game.print_board()
    
    player = white_player if game.cur_player == Player.WHITE else black_player

    print(f"{player_names[game.cur_player]}'s turn")

    try:

        ix, iy, fx, fy = player.get_player_move(game)

        captured = game.board.move_piece(ix, iy, fx, fy)
        if captured is not None:
            print(f"Captured: {player_names[captured.owner]} {size_names[captured.size]} {shape_names[captured.shape]}!")

    except ValueError as e:
        print(f"Invalid input: {e}")
        continue
    except InvalidMoveError as e:
        print(f"Invalid Move: {e}")
        continue

    game.cur_player = Player.BLACK if game.cur_player == Player.WHITE else Player.WHITE
    winner = game.check_winner()
    if (winner is not None):
        print(f"Game over {player_names[winner]} wins!")
        break

