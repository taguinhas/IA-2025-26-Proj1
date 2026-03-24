from game.game import Game
from game.board import Board
from game.piece import Shape, Size, Player, Piece
from utils import get_attack_map

shapeFactors = {
        Shape.TRIANGLE:1,
        Shape.SQUARE:2,
        Shape.CIRCLE:3
    }

posTableWithCenter = [
    [20,16,16,16,16,20],
    [6, 7, 8, 8, 7, 6 ],
    [3, 4, 5, 5, 4, 3 ],
    [2, 3, 4, 4, 3, 2 ],
    [1, 2, 3, 3, 2, 1 ],
    [0, 0, 1, 1, 0, 0 ],
]
"""
chess gives bigger values to pieces on the center because of board control,
however a piece on the edge is less likely to be captured so maybe for alapo its not better?
needs testing
maybe only use pos table for small pieces? since  big pieces can just skip the entire board?
"""
posTable = [
    [12,12,12,12,12,12],
    [6, 6, 6, 6, 6, 6 ],
    [3, 3, 3, 3, 3, 3 ],
    [2, 2, 2, 2, 2, 2 ],
    [1, 1, 1, 1, 1, 1 ],
    [0, 0, 0, 0, 0, 0 ],
]
"""
We could also do a table foreach piece(possibly overkill)
posTables = {
    Shape.SQUARE: [],
    Shape.TRIANGLE: [],
    Shape.CIRCLE: []
}
"""
"""
Weights need testing and tweaking
im really unsure about the pos values. im afraid it'll sacrifice pieces just to get them further on the board
"""
heuristicWeights = {
    "Material": 1,
    "Position": 1,
    "Activity": 1,
    "Safety": 1,
}


def evaluate_board(board: Board):
    white_attacks = get_attack_map(board, Player.WHITE)
    black_attacks = get_attack_map(board, Player.BLACK)

    material_score = material_eval_board(board)

    pos_score = position_with_table_eval_board(board, posTableWithCenter)

    activity_score = activity_eval_board(board)

    safe_score = safety_eval_board(board, white_attacks, black_attacks)


    total_score = (
         heuristicWeights["Material"] * material_score +
         heuristicWeights["Position"] * pos_score +
         heuristicWeights["Activity"] * activity_score +
         heuristicWeights["Safety"] * safe_score
    )

    return total_score

def material_eval_board(board:Board) ->int:
    materialScore = 0
    for line in board.board:
        for piece in line:
            if piece is None:
                continue
            ownerFactor = 1 if piece.owner == Player.WHITE else -1

            pieceScore = shapeFactors[piece.shape]
            if piece.size == Size.BIG:
                pieceScore *=3
                
            materialScore += pieceScore * ownerFactor
    return materialScore

def position_with_table_eval_board(board:Board, posTable) ->int:       
    posScore = 0
    for y in range(board.size):
        for x in range(board.size):
            piece = board.get_piece(x,y)
            if piece is None:
                continue

            ownerFactor = 1 if piece.owner == Player.WHITE else -1
            temp = posTable[y][x] if piece.owner == Player.WHITE else posTable[5 - y][x]
            posScore += temp * ownerFactor  
    return posScore

def safety_eval_board(board:Board, white_attacks, black_attacks) ->int:
    """requires attack maps(see utils.get_attack_map)"""
    safeScore = 0
    for y in range(board.size):
        for x in range(board.size):
            piece = board.get_piece(x, y)

            if piece is None:
                continue

            if (piece.owner == Player.WHITE):
                ownerFactor = 1
                enemy_attacks = black_attacks
            else:
                ownerFactor = -1
                enemy_attacks = white_attacks

            if enemy_attacks[y][x]:
                penalty = shapeFactors[piece.shape]

                if piece.size == Size.BIG:
                    penalty *= 3

                safeScore -= penalty * ownerFactor
    return safeScore

def activity_eval_board(board:Board) ->int:
    activityScore = 0
    for y in range(board.size):
        for x in range(board.size):
            piece = board.get_piece(x, y)

            if piece is None:
                continue

            ownerFactor = 1 if piece.owner == Player.WHITE else -1

            moves = piece.get_moves(board, x, y)

            activityScore += len(moves) * ownerFactor
    return activityScore

