from players.genericPlayer import genericPlayer
from game.game import Game
from game.board import Board
from game.piece import Move

import copy

class MinimaxPlayer(genericPlayer):
    
    def __init__(self, name, eval_func, depth):
        super().__init__(name)          # pass name to base
        self.eval_func = eval_func
        self.depth = depth
    
    
    def _simulate_move(self, board:Board, move):
        """Create a copy of game_state with the move applied"""
        
        new_board = copy.deepcopy(board)
        new_board.move_piece(move)
        return new_board
    
    
    def get_player_move(self, game:Game):
        """Find the best move using the Minimax alpha-beta algorithm"""
        
        move = self.minimax_alpha_beta_search(game)
        return move
    
    
    def minimax_alpha_beta_search(self, game:Game):
        '''
        Returns the move with the best minimax value.
        '''
        
        player = game.cur_player
        _, move = self.max_value(game.board, self.depth, float('-inf'), float('inf'), player)
        return move
    
    
    def max_value(self, board:Board, depth, alpha, beta, original_player):
        '''
        Returns the evaluation and the move with the max minimax value.
        '''
        
        if depth == 0 or board.game_over:
            # Evaluate always from the perspective of the AI that started the search
            return self.eval_func(board, original_player), None
        
        # your code here

        max_eval = float("-inf")
        for move in board.available_moves(original_player):
            new_state = self._simulate_move(board, move)
            new_value, _ = self.min_value(new_state, depth - 1, alpha, beta, original_player)
            if(new_value > max_eval):
                max_eval, max_move = new_value, move
                alpha = max(alpha, max_eval)
            if alpha >= beta:
                return max_eval, max_move
            
        return max_eval, max_move
        
    def min_value(self, board:Board, depth, alpha, beta, original_player):
        '''
        Returns the evaluation and the move with the min minimax value.
        '''

        if depth == 0 or board.game_over:
            # Evaluate always from the perspective of the AI that started the search
            return self.eval_func(board, original_player), None
        
        # your code here
        
        min_eval = float("inf")
        for move in board.available_moves():
            new_state = self._simulate_move(board, move)
            new_value, _ = self.min_value(new_state, depth - 1, alpha, beta, original_player)
            if(new_value < min_eval):
                min_eval, min_move = new_value, move
                alpha = max(alpha, min_eval)
            if alpha >= beta:
                return min_eval, min_move
            
        return min_eval, min_move