from game.game import Game
from game.board import Board
from game.piece import Shape, Size, Player, Piece

shapeFactors = {
        Shape.TRIANGLE:1,
        Shape.SQUARE:3,
        Shape.CIRCLE:9
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
    [15, 15, 15, 15, 15, 15],
    [5, 5, 5, 5, 5, 5],
    [3, 3, 3, 3, 3, 3],
    [1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
]
"""
We could also do a table foreach piece(possibly overkill)
posTables = {
    Shape.SQUARE: [],
    Shape.TRIANGLE: [],
    Shape.CIRCLE: []
}
"""

agressivecontrolTable = [
    [8, 8, 8, 8, 8, 8 ],
    [3, 4, 5, 5, 4, 3 ],
    [2, 3, 4, 4, 3, 2 ],
    [1, 2, 3, 3, 2, 1 ],
    [0, 0, 0, 0, 0, 0 ],
    [0, 0, 0, 0, 0, 0 ],
]

defensivecontrolTable = [
    [8, 8, 8, 8, 8, 8 ],
    [3, 4, 5, 5, 4, 3 ],
    [1, 2, 3, 3, 2, 1 ],
    [1, 2, 3, 3, 2, 1 ],
    [3, 4, 5, 5, 4, 3 ],
    [8, 8, 8, 8, 8, 8 ],
]
"""
Weights need testing and tweaking
im really unsure about the pos values. im afraid it'll sacrifice pieces just to get them further on the board
"""
WEIGHTS = {
    "Material": 100,
    "Safety": 40,
    "Position": 20,
    "Control": 10, #temporary was 10
    #"Activity": 0, #temporary was 5
}

training_weights = {
    "Material": 194,
    "Safety": 33,
    "Position": 1,
    "Control": 7
}

adjusted_weights = {
    "Material": 180,
    "Safety": 45,
    "Position": 15,
    "Control": 8
}
def evaluate_board(board: Board, depth, weights = adjusted_weights):
    winner = board.check_winner()
    if winner == Player.WHITE:
        return 1000000 + depth
    if winner == Player.BLACK:
        return -1000000 - depth
    white_attacks = board.get_white_attack_map()
    black_attacks = board.get_black_attack_map()

    material_score = material_eval_board(board)

    pos_score = position_with_table_eval_board(board, posTable)

    #very similar logic to control, might not be needed
    #activity_score = activity_with_attack_map(white_attacks) - activity_with_attack_map(black_attacks)

    safe_score = safety_eval_board(board, white_attacks, black_attacks)

    controlScore = control_eval_board(white_attacks, black_attacks, defensivecontrolTable)

    key = board.current_hash
    #only 1 player needs to be disencouraged to repeat moves
    repetition_penalty = (0 - board.history.get(key, 0) ** 2)*5

    total_score = ( 0
        + weights["Material"] * material_score
        + weights["Position"] * pos_score 
        #+ weights["Activity"] * activity_score 
        + weights["Safety"] * safe_score 
        + weights["Control"] * controlScore
        + repetition_penalty
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

def safety_eval_board(board, white_attacks, black_attacks):
    """requires attack maps(see utils.get_attack_map)
    """
    score = 0

    for y in range(board.size):
        for x in range(board.size):
            piece = board.get_piece(x, y)
            if not piece:
                continue
            if piece.owner == Player.WHITE:
                attackers = black_attacks[y][x]
                defenders = white_attacks[y][x]
            else:
                attackers = white_attacks[y][x]
                defenders = black_attacks[y][x]
            if attackers == 0:
                continue

            value = shapeFactors[piece.shape]
            if piece.size == Size.BIG:
                value *= 3

            score -= max(attackers - defenders, 0) * value * (1 if piece.owner == Player.WHITE else -1)

    return score

#unused
def activity_with_attack_map(attack_map) ->int:
    return sum(sum(row) for row in attack_map)

def control_eval_board(white_attacks, black_attacks, weight_table):
    controlScore = 0
    for y in range(len(weight_table)):
        for x in range(len(weight_table[0])):
            controlScore += white_attacks[y][x] * weight_table[y][x]
            controlScore -= black_attacks[y][x] * weight_table[len(weight_table)-y-1][x]
    return controlScore
