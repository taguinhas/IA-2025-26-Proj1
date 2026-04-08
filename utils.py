from game.board import Board
from game.piece import Player, Shape, Size

def user_to_board_coords(board:Board, x:int, y:int):
    return (x, board.size - y - 1)

def get_attack_map(board:Board, attacker: Player):
    """
    return a set with all the squares being attacked by attacker. usefull for goal check and heuristics
    """
    attacked = [[0 for _ in range(board.size)] for _ in range(board.size)]

    for y in range(board.size):
        for x in range(board.size):
            piece = board.get_piece(x, y)

            if piece is None or piece.owner != attacker:
                continue

            moves = piece.get_moves(board, x, y)
            for fx, fy in moves:
                attacked[fy][fx] += 1

    return attacked

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