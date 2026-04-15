from game.game import Game
from game.board import Board, InvalidMoveError
from game.piece import Piece, Player, Size, Shape
from utils.heuristics import evaluate_board, heuristic_weights

from players.humanPlayer import HumanPlayer
from players.minimaxPlayer import MinimaxPlayer, Strategy

from utils.utils import player_names, size_names, shape_names
import time

game = Game()
#game.load_board_from_file("boards/test.txt")
modes = {
    0: "Human vs Human",
    1: "Human vs MiniMax",
    2: "MiniMax vs MiniMax"
}

white_player = HumanPlayer("Lowly human")
black_player = HumanPlayer("Lowlier human")

depth = 5
strat = Strategy.IDSALLTABLES
heuristics = heuristic_weights.ADJUSTED_WEIGHTS
white_ai = False
black_ai = False
white_times = list()
black_times = list()
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
                black_player = MinimaxPlayer("HumanDestroyer9000", evaluate_board, depth, strat, heuristics)
                black_ai = True
            else:
                black_player = HumanPlayer("Lowly human")
                white_player = MinimaxPlayer("HumanDestroyer9000", evaluate_board, depth, strat, heuristics)
                white_ai = True
            break

        case 2:
            white_player = MinimaxPlayer("HumanDestroyer9000", evaluate_board, depth, strat, heuristics)
            black_player = MinimaxPlayer("HumanDecimator9000", evaluate_board, depth, strat, heuristics)
            white_ai = True
            black_ai = True
            break
while(True):
    game.print_board()
    
    player = white_player if game.get_cur_player() == Player.WHITE else black_player
    print(f"{player_names[game.get_cur_player()]}'s turn")

    try:
        start = time.time()
        move = player.get_player_move(game)
        end = time.time()

        print(f"Time: {end - start:.4f}s")

        if (game.get_cur_player() == Player.WHITE):
            white_times.append(end-start)
        else:
            black_times.append(end-start)
        captured = game.board.move_piece(move)
        game.move_count += 1
        if captured is not None:
            print(f"Captured: {player_names[captured.owner]} {size_names[captured.size]} {shape_names[captured.shape]}!")

    except ValueError as e:
        print(f"Invalid input: {e}")
        continue
    except InvalidMoveError as e:
        print(f"Invalid Move: {e}")
        continue

    winner = game.board.check_winner()
    if (winner is not None):
        print(f"Game over {player_names[winner]} wins!")
        game.print_board()
        game.write_stats(winner, white_player, black_player, white_ai, black_ai, white_times, black_times)
        break
    
