from game.game import Game
from heuristics import *
game = Game()
game.load_board_from_file("boards/central.txt")
game.print_board()

score = evaluate_board(game.board)
print(score)