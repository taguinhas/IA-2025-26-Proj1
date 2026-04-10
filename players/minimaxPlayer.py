from players.genericPlayer import genericPlayer
from game.game import Game
from game.board import Board
from game.piece import Move, Player

class MinimaxPlayer(genericPlayer):
    
    def __init__(self, name, eval_func, depth):
        super().__init__(name)          # pass name to base
        self.eval_func = eval_func
        self.depth = depth
    
    def get_player_move(self, game:Game):
        """Find the best move using the Minimax alpha-beta algorithm"""
        
        move = self.minimax_alpha_beta_search(game)
        return move
    
    
    def minimax_alpha_beta_search(self, game:Game):
        '''
        Returns the move with the best minimax value.
        '''
        simulation_board = game.board.copy()
        player = game.cur_player
        if player == Player.WHITE:
            eval, move = self.max_value(simulation_board, self.depth, float('-inf'), float('inf'))
        else:
            eval, move = self.min_value(simulation_board, self.depth, float('-inf'), float('inf'))
        print("pos eval:" + str(eval))
        return move
    
    
    def max_value(self, board:Board, depth, alpha, beta):
        '''
        Returns the evaluation and the move with the max minimax value.
        '''
        winner = board.check_winner()
        if winner == Player.WHITE:
            return 1000000 + depth, None 
        if winner == Player.BLACK:
            return -1000000 - depth, None
        if depth == 0:
            return self.eval_func(board, depth), None

        max_eval = float("-inf")
        moves = board.available_moves(Player.WHITE)
        if not moves: 
            return self.eval_func(board, depth), None
        
        max_move = moves[0]

        for move in moves:
            captured = board.move_piece(move)
            new_value, _ = self.min_value(board, depth - 1, alpha, beta)
            board.undo_move(move, captured)

            if(new_value > max_eval):
                max_eval, max_move = new_value, move
                alpha = max(alpha, max_eval)
            if beta <= alpha:
                return max_eval, max_move
            
        return max_eval, max_move
        
    
    def min_value(self, board:Board, depth, alpha, beta):
        '''
        Returns the evaluation and the move with the min minimax value.
        '''
        winner = board.check_winner()
        if winner == Player.WHITE:
            return 1000000 + depth, None 
        if winner == Player.BLACK:
            return -1000000 - depth, None
        if depth == 0:
            return self.eval_func(board,  depth), None
        
        min_eval = float("inf")
        moves = board.available_moves(Player.BLACK)
        if not moves: 
            return self.eval_func(board, depth), None
        
        min_move = moves[0]
        
        for move in moves:
            captured = board.move_piece(move)
            new_value, _ = self.max_value(board, depth - 1, alpha, beta)
            board.undo_move(move,captured)

            if(new_value < min_eval):
                min_eval, min_move = new_value, move
                beta = min(beta, min_eval)

            if alpha >= min_eval:
                return min_eval, min_move
            
        return min_eval, min_move