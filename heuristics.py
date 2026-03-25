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

posTableWithCenter2 = [
    [10,16,16,16,16,10],
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

controlTable = [
    [8, 8, 8, 8, 8, 8 ],
    [3, 4, 5, 5, 4, 3 ],
    [2, 3, 4, 4, 3, 2 ],
    [1, 2, 3, 3, 2, 1 ],
    [0, 0, 0, 0, 0, 0 ],
    [0, 0, 0, 0, 0, 0 ],
]

"""
Weights need testing and tweaking
im really unsure about the pos values. im afraid it'll sacrifice pieces just to get them further on the board
"""
heuristicWeights = {
    "Material": 1,
    "Position": 1,
    "Activity": 1,
    "Safety": 1,
    "Control": 1,
}


def evaluate_board(board: Board):
    white_attacks = get_attack_map(board, Player.WHITE)
    black_attacks = get_attack_map(board, Player.BLACK)

    material_score = material_eval_board(board)

    pos_score = position_with_table_eval_board(board, posTableWithCenter)

    #very similar logic to control, might not be needed
    activity_score = activity_eval_board(board)

    safe_score = safety_eval_board(board, white_attacks, black_attacks)

    controlScore = control_eval_board(white_attacks, black_attacks, controlTable)

    total_score = (
         heuristicWeights["Material"] * material_score +
         heuristicWeights["Position"] * pos_score +
         heuristicWeights["Activity"] * activity_score +
         heuristicWeights["Safety"] * safe_score +
         heuristicWeights["Control"] * controlScore
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

def position_with_columns_eval_board(board:Board, posTable) ->int:
    """TODO:take columns into account"""  
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

def safety_eval_board(board, white_attacks, black_attacks):
    """requires attack maps(see utils.get_attack_map)
    """
    safeScore = 0

    for y in range(board.size):
        for x in range(board.size):
            piece = board.get_piece(x, y)
            if piece is None:
                continue

            if piece.owner == Player.WHITE:
                danger = black_attacks[y][x] - white_attacks[y][x]
                ownerFactor = 1
            else:
                danger = white_attacks[y][x] - black_attacks[y][x]
                ownerFactor = -1

            # only care if actually in danger
            if danger <= 0:
                safeScore += 0.2 * (-danger) * ownerFactor

            else:
                penalty = danger * shapeFactors[piece.shape]

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

def control_eval_board(white_attacks, black_attacks, weight_table):
    controlScore = 0
    for y in range(len(weight_table)):
        for x in range(len(weight_table[0])):
            controlScore += white_attacks[y][x] * weight_table[y][x]
            controlScore -= black_attacks[y][x] * weight_table[len(weight_table)-y-1][x]
    return controlScore
