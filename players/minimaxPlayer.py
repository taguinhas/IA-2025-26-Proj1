from players.genericPlayer import genericPlayer
from game.game import Game
from game.board import Board
from game.piece import Move, Player
from utils.heuristics import shapeFactors
from enum import Enum

class Strategy(Enum):
    ABPRUNING = 0
    ABTABLE = 1
    IDS = 3

class MinimaxPlayer(genericPlayer):
    
    def __init__(self, name, eval_func, depth, stategy:Strategy = 3):
        super().__init__(name)          # pass name to base
        self.eval_func = eval_func
        self.depth = depth
        self.transposition_table = {}
        self.table_hits = 0 # Track performance
        self.strategy = Strategy
    
    def get_player_move(self, game:Game):
        """Find the best move using the Minimax alpha-beta algorithm"""
        
        if self.strategy == 0:
            move = self.minimax_alpha_beta_search(game)
        elif self.strategy == 1:
            move = self.minimax_cached_ab_search(game)
        else:
            move = self.iterative_deepening_search(game)
        
        return move
    
    def minimax_alpha_beta_search(self, game:Game):
        '''
        Returns the move with the best minimax value.
        '''
        simulation_board = game.board.copy()
        player = game.get_cur_player()
        if player == Player.WHITE:
            eval, move = self.max_value(simulation_board, self.depth, float('-inf'), float('inf'))
        else:
            eval, move = self.min_value(simulation_board, self.depth, float('-inf'), float('inf'))
        print(f"Pos eval: {eval}")
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

        #gemini suggestion to improve prunning
        def score_move(move):
            score = 0
            target_piece = board.get_piece(move.fx, move.fy)
            if target_piece:
                # Prioritize capturing high-value pieces
                score += 100 + shapeFactors[target_piece.shape]

            # Prioritize moving toward the goal row
            if move.fy == 0:
                score += 50

            return score  
        
        moves.sort(key=score_move, reverse=True)      

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
        
        #gemini suggestion to improve prunning
        def score_move(move):
            score = 0
            target_piece = board.get_piece(move.fx, move.fy)
            if target_piece:
                # Prioritize capturing high-value pieces
                score += 100 + shapeFactors[target_piece.shape]

            # Prioritize moving toward the goal row
            if move.fy == 5:
                score += 50

            return score  
        
        moves.sort(key=score_move, reverse=True)  

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
    
    def minimax_cached_ab_search(self, game:Game):
        '''
        Returns the move with the best minimax value using a transposition_table and zobrist hashing.
        '''
        self.table_hits = 0

        simulation_board = game.board.copy()

        #shouldn't happen but idk
        if simulation_board.current_hash == 0:
            simulation_board.hash_board()

        player = game.get_cur_player()
        if player == Player.WHITE:
            eval, move = self.max_value_cache(simulation_board, self.depth, float('-inf'), float('inf'))
        else:
            eval, move = self.min_value_cache(simulation_board, self.depth, float('-inf'), float('inf'))
        print("pos eval:" + str(eval))
        print(f"Pos eval: {eval} | TT Hits: {self.table_hits}")
        return move
    
    def max_value_cache(self, board:Board, depth, alpha, beta):
        '''
        Returns the evaluation and the move with the max minimax value.
        '''
        state_hash = board.current_hash

        if state_hash in self.transposition_table:
            entry = self.transposition_table[state_hash]
            if entry['depth'] >= depth:
                self.table_hits += 1
                return entry['value'], entry['move']
            
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

        #gemini suggestion to improve prunning
        def score_move(move):
            score = 0
            target_piece = board.get_piece(move.fx, move.fy)
            if target_piece:
                # Prioritize capturing high-value pieces
                score += 100 + shapeFactors[target_piece.shape]

            # Prioritize moving toward the goal row
            if move.fy == 0:
                score += 50

            return score  
        
        moves.sort(key=score_move, reverse=True)      

        max_move = moves[0]

        for move in moves:
            captured = board.move_piece(move)
            new_value, _ = self.min_value_cache(board, depth - 1, alpha, beta)
            board.undo_move(move, captured)

            if(new_value > max_eval):
                max_eval, max_move = new_value, move
                alpha = max(alpha, max_eval)
            if beta <= alpha:
                return max_eval, max_move
            
        self.transposition_table[state_hash] = {
            'value': max_eval,
            'depth': depth,
            'move': max_move
        }
        return max_eval, max_move
        
    
    def min_value_cache(self, board:Board, depth, alpha, beta):
        '''
        Returns the evaluation and the move with the min minimax value.
        '''
        state_hash = board.current_hash

        if state_hash in self.transposition_table:
            entry = self.transposition_table[state_hash]
            if entry['depth'] >= depth:
                self.table_hits += 1
                return entry['value'], entry['move']
            
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
        
        #gemini suggestion to improve prunning
        def score_move(move):
            score = 0
            target_piece = board.get_piece(move.fx, move.fy)
            if target_piece:
                # Prioritize capturing high-value pieces
                score += 100 + shapeFactors[target_piece.shape]

            # Prioritize moving toward the goal row
            if move.fy == 5:
                score += 50

            return score  
        
        moves.sort(key=score_move, reverse=True)  

        min_move = moves[0]
        
        for move in moves:
            captured = board.move_piece(move)
            new_value, _ = self.max_value_cache(board, depth - 1, alpha, beta)
            board.undo_move(move,captured)

            if(new_value < min_eval):
                min_eval, min_move = new_value, move
                beta = min(beta, min_eval)

            if alpha >= min_eval:
                return min_eval, min_move
            
        self.transposition_table[state_hash] = {
            'value': min_eval,
            'depth': depth,
            'move': min_move
        }

        return min_eval, min_move
    
    def iterative_deepening_search(self, game:Game):
        '''
        Iterative deepening search utilizing the transposition table.
        Searches from depth 1 up to self.depth.
        '''
        self.table_hits = 0 # Reset counter for the whole search

        simulation_board = game.board.copy()
        
        #shouldn't happen but idk
        if simulation_board.current_hash == 0:
            simulation_board.hash_board()

        player = game.get_cur_player()
        best_move = None
        best_eval = 0

        # Loop from depth 1 up to our max depth
        for current_depth in range(1, self.depth + 1):
            if player == Player.WHITE:
                eval, move = self.max_value_cache(simulation_board, current_depth, float('-inf'), float('inf'))
            else:
                eval, move = self.min_value_cache(simulation_board, current_depth, float('-inf'), float('inf'))
            
            best_eval = eval
            best_move = move
            
            print(f"Depth {current_depth} completed | Eval: {best_eval} | TT Hits so far: {self.table_hits}")

            if abs(best_eval) > 500000:
                break

        print(f"Pos eval: {eval} | TT Hits: {self.table_hits}")
        return best_move