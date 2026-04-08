from game.game import Game
from heuristics import *
game = Game()
#game.load_board_from_file("boards/symmetrical.txt")
#game.load_board_from_file("boards/corner.txt")
#game.load_board_from_file("boards/upper_corner.txt")
#game.load_board_from_file("boards/central.txt")
#game.load_board_from_file("boards/central_no_mobility.txt")
#game.load_board_from_file("boards/defended.txt")
#game.load_board_from_file("boards/unsafe.txt")
#game.load_board_from_file("boards/material.txt")
#game.load_board_from_file("boards/generic_board.txt")
game.load_board_from_file("boards/win.txt")
game.print_board()

score = evaluate_board(game.board, Player.BLACK)
print(score)