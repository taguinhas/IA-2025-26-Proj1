from game.game import Game
from game.board import Board, InvalidMoveError
from game.piece import Piece, Player, Size, Shape
from heuristics import evaluate_board

from players.humanPlayer import HumanPlayer
from players.minimaxPlayer import MinimaxPlayer

from utils import player_names, size_names, shape_names

game = Game()
#game.load_board_from_file("boards/test.txt")
modes = {
    0: "Human vs Human",
    1: "Human vs MiniMax",
    2: "MiniMax vs MiniMax"
}

white_player = HumanPlayer("Lowly human")
black_player = HumanPlayer("Lowlier human")

depth = 4
while True:
    print("Choose game type:")
    for key, value in modes.items():
        print(str(key) + ": " + value)

    choice = int(input())
    match choice:
        case 0:
            white_player = HumanPlayer("Lowly human")
            black_player = HumanPlayer("Lowlier human")
            break
        case 1:
            print("White(0) or black (1)?")
            color = int(input())
            if color == 0:
                white_player = HumanPlayer("Lowly human")
                black_player = MinimaxPlayer("HumanDestroyer9000", evaluate_board, depth)
            else:
                black_player = HumanPlayer("Lowly human")
                white_player = MinimaxPlayer("HumanDestroyer9000", evaluate_board, depth)
            break

        case 2:
            white_player = MinimaxPlayer("HumanDestroyer9000", evaluate_board, depth)
            black_player = MinimaxPlayer("HumanDecimator9000", evaluate_board, depth)
            break

while(True):
    game.print_board()
    
    player = white_player if game.cur_player == Player.WHITE else black_player

    print(f"{player_names[game.cur_player]}'s turn")

    try:
        move = player.get_player_move(game)
        captured = game.board.move_piece(move)
        if captured is not None:
            print(f"Captured: {player_names[captured.owner]} {size_names[captured.size]} {shape_names[captured.shape]}!")

    except ValueError as e:
        print(f"Invalid input: {e}")
        continue
    except InvalidMoveError as e:
        print(f"Invalid Move: {e}")
        continue

    game.cur_player = Player.BLACK if game.cur_player == Player.WHITE else Player.WHITE
    winner = game.board.check_winner()
    if (winner is not None):
        print(f"Game over {player_names[winner]} wins!")
        break

