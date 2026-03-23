from game.game import Game
from heuristics import eval_board
game = Game()
game.load_board_from_file("board1.txt")
game.print_board()
print(f"Board Value = {eval_board(game.board):+}")
