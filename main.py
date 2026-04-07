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

player_names = {
    Player.WHITE: "White",
    Player.BLACK: "BLACK"
}

size_names = {
    Size.SMALL: "Small",
    Size.BIG: "Big"
}

shape_names = {
    Shape.SQUARE: "Square",
    Shape.TRIANGLE: "Triangle",
    Shape.CIRCLE: "Circle"
}

def user_to_board_coords(board:Board, x:int, y:int):
    return (x, board.size - y - 1)


def get_player_move(board:Board):
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

game = Game()
while(True):
    game.print_board()
    
    print(f"{player_names[game.cur_player]}'s turn")

    try:
        ix, iy, fx, fy = get_player_move(game.board)

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

