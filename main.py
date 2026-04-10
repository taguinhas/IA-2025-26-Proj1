from game.game import Game
from game.board import Board, InvalidMoveError
from game.piece import Piece, Player, Size, Shape

import pygame

pygame.init()
WIDTH = 1000
HEIGHT = 900
screen = pygame.display.set_mode([WIDTH, HEIGHT])
font = pygame.font.Font('freesansbold.ttf', 20)
big_font = pygame.font.Font('freesansbold.ttf', 50)
timer = pygame.time.Clock()
fps = 60

run = True

while run:
    timer.tick(fps)
    screen.fill('dark gray')

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.flip()
pygame.quit() 
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
game_mode = -1

white_player = HumanPlayer("Lowly human")
black_player = HumanPlayer("Lowlier human")

depth = 4
while(game_mode == -1):
    print("Choose game type:")
    for key, value in modes.items():
        print(str(key) + ": " + value)

    choice = int(input())
    match choice:
        case 0:
            white_player = HumanPlayer("Lowly human")
            black_player = HumanPlayer("Lowlier human")
            game_mode = 0

        case 1:
            print("White(0) or black (1)?")
            color = int(input())
            if color == 0:
                white_player = HumanPlayer("Lowly human")
                black_player = MinimaxPlayer("HumanDestroyer9000", evaluate_board, depth)
            else:
                black_player = HumanPlayer("Lowly human")
                white_player = MinimaxPlayer("HumanDestroyer9000", evaluate_board, depth)
            game_mode = 1

        case 2:
            white_player = MinimaxPlayer("HumanDestroyer9000", evaluate_board, depth)
            black_player = MinimaxPlayer("HumanDecimator9000", evaluate_board, depth)
            game_mode = 2 

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

