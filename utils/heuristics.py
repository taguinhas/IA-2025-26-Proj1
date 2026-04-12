from game.game import Game
from game.board import Board
from game.piece import Shape, Size, Player, Piece

shapeFactors = {
        Shape.TRIANGLE:1, 
        Shape.SQUARE:2, 
        Shape.CIRCLE:4
    }

sizeFactor = 5

posTable = [
    [15,15,15,15,15,15],
    [5, 5, 5, 5, 5, 5],
    [3, 3, 3, 3, 3, 3],
    [1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
]

#could be used if you want quicker games but beware the winrate will decrease
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

#all the following weights are pretty similar when paired against each other
#weights we gave "blindly"
WEIGHTS = {
    "Material": 100,
    "Safety": 40,
    "Position": 20,
    "Control": 10, 
    "Activity": 0,
}

#weights of the player from gen 59
training_weights = {
    "Material": 194,
    "Safety": 33,
    "Position": 1,
    "Control": 7
}

#weights after some human consideration
adjusted_weights = {
    "Material": 180,
    "Safety": 45,
    "Position": 15,
    "Control": 8
}

def evaluate_board(board: Board, depth, weights = adjusted_weights):
    """given a board gives an heuristic evaluation"""
    #all our heuristics follow the position rating used on chess. positive heuristics favor white, negative favor black

    #terminal check, don't want other heuristics to cause the ai to choose a slower win
    winner = board.check_winner()
    if winner == Player.WHITE:
        return 1000000 + depth
    if winner == Player.BLACK:
        return -1000000 - depth
    
    white_attacks = board.get_white_attack_map()
    black_attacks = board.get_black_attack_map()

    #having more material generally good
    material_score = material_eval_board(board)

    #encouraging the ai to advance the position and take more space on the board
    pos_score = position_with_table_eval_board(board, posTable)

    #having pieces with lots of available moves might be good
    #however it was very similar to control so we removed it
    #activity_score = activity_with_attack_map(white_attacks) - activity_with_attack_map(black_attacks)

    #having pieces with more attackers than defenders usually bad
    safe_score = safety_eval_board(board, white_attacks, black_attacks)

    #having attacks on certain key squares is usually good, was surprised that during training it got ignored.
    #possibly covered by the win condition and depth?
    control_score = control_eval_board(white_attacks, black_attacks, defensivecontrolTable)

    key = board.current_hash
    #only 1 player needs to be disencouraged form repeating moves
    repetition_penalty = (0 - board.history.get(key, 0) ** 2)*5

    total_score = ( 0
        + weights["Material"] * material_score
        + weights["Position"] * pos_score 
        #+ weights["Activity"] * activity_score 
        + weights["Safety"] * safe_score 
        + weights["Control"] * control_score
        + repetition_penalty
    )

    return total_score

def material_eval_board(board:Board) ->int:
    """given a board returns the sum of the values of each piece"""
    #shape value defined at shapeFactors
    #big pieces multiplied by sizeFactor
    materialScore = 0
    for line in board.board:
        for piece in line:
            if piece is None:
                continue
            ownerFactor = 1 if piece.owner == Player.WHITE else -1

            pieceScore = shapeFactors[piece.shape]
            if piece.size == Size.BIG:
                pieceScore *= sizeFactor
                
            materialScore += pieceScore * ownerFactor
    return materialScore

def position_with_table_eval_board(board:Board, posTable) ->int:
    """given a board and posTable returns the sum of squares of posTable with a piece at its location"""
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
    """returns a score that represents how safe the pieces are in a position.
    pieces with more attackers than defenders are deemed unsafe
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
                value *= sizeFactor

            score -= max(attackers - defenders, 0) * value * (1 if piece.owner == Player.WHITE else -1)

    return score

#unused
def activity_with_attack_map(attack_map) ->int:
    return sum(sum(row) for row in attack_map)

def control_eval_board(white_attacks, black_attacks, weight_table):
    """returns a score reflecting the ammount of attack each player has on key squares. weight of each square defined at weight_table"""
    control_score = 0
    for y in range(len(weight_table)):
        for x in range(len(weight_table[0])):
            control_score += white_attacks[y][x] * weight_table[y][x]
            control_score -= black_attacks[y][x] * weight_table[len(weight_table)-y-1][x]
    return control_score
