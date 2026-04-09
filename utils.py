from game.board import Board
from game.piece import Player, Shape, Size

def user_to_board_coords(board:Board, x:int, y:int):
    return (x, board.size - y - 1)

player_names = {
    Player.WHITE: "White",
    Player.BLACK: "Black"
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