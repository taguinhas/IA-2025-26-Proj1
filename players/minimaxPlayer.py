from players.genericPlayer import genericPlayer
from game.game import Game
from game.board import Board
from game.piece import Move, Player

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
        if player == Player.WHITE:
            eval, move = self.max_value(game.board, self.depth, float('-inf'), float('inf'))
        else:
            eval, move = self.min_value(game.board, self.depth, float('-inf'), float('inf'))
        print("pos eval:" + str(eval))
        return move
    
    
    def max_value(self, board:Board, depth, alpha, beta):
        '''
        Returns the evaluation and the move with the max minimax value.
        '''
        player = Player.WHITE
        if depth == 0 or board.game_over:
            # Evaluate always from the perspective of the AI that started the search
            return self.eval_func(board, player), None
        
        # your code here

        max_eval = float("-inf")
        moves = board.available_moves(player)
        max_move = moves[0]
        for move in moves:
            new_state = self._simulate_move(board, move)
            new_value, _ = self.min_value(new_state, depth - 1, alpha, beta)
            if(new_value > max_eval):
                max_eval, max_move = new_value, move
                alpha = max(alpha, max_eval)
            if max_eval >= beta:
                return max_eval, max_move
            
        return max_eval, max_move
        
    def min_value(self, board:Board, depth, alpha, beta):
        '''
        Returns the evaluation and the move with the min minimax value.
        '''

        player = Player.BLACK
        if depth == 0 or board.game_over:
            # Evaluate always from the perspective of the AI that started the search
            return self.eval_func(board, player), None
        
        # your code here
        
        min_eval = float("inf")
        moves = board.available_moves(player)
        min_move = moves[0]
        
        for move in moves:
            new_state = self._simulate_move(board, move)
            new_value, _ = self.max_value(new_state, depth - 1, alpha, beta)
            if(new_value < min_eval):
                min_eval, min_move = new_value, move
                beta = min(beta, min_eval)
            if alpha >= min_eval:
                return min_eval, min_move
            
        return min_eval, min_move