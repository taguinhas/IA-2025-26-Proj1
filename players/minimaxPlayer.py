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

class PruneFlags(Enum):
    EXACT = 0
    LOWERBOUND = 1
    UPPERBOUND = 2

class MinimaxPlayer(genericPlayer):
    
    def __init__(self, name, eval_func, depth, strategy:Strategy = Strategy.IDS):
        super().__init__(name)          # pass name to base
        self.eval_func = eval_func
        self.depth = depth
        self.transposition_table = {}
        self.cutoff_moves = {}
        self.strategy = strategy

        # Track performance
        self.table_hits = 0 
        self.nodes = 0
    
    def get_player_move(self, game:Game):
        """Find the best move using the Minimax alpha-beta algorithm"""
        
        self.nodes = 0
        if self.strategy == Strategy.ABPRUNING:
            move = self.minimax_alpha_beta_search(game)
        elif self.strategy == Strategy.ABTABLE:
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
        print(f"Nodes: {self.nodes}") 
        return move
    
    
    def max_value(self, board:Board, depth, alpha, beta):
        self.nodes += 1
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
        self.nodes += 1
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
        print(f"Pos eval: {eval} ")
        print(f"Nodes: {self.nodes} | TT Hits: {self.table_hits}") 
        return move
    
    def max_value_cache(self, board:Board, depth, alpha, beta):
        '''
        Returns the evaluation and the move with the max minimax value.
        '''
        self.nodes += 1

        alpha_orig = alpha
        beta_orig = beta

        state_hash = board.current_hash

        tt_entry = self.transposition_table.get(state_hash)
        if tt_entry and tt_entry['depth'] >= depth:
            self.table_hits += 1
            if tt_entry['flag'] == PruneFlags.EXACT:
                return tt_entry['value'], tt_entry['move']

            elif tt_entry['flag'] == PruneFlags.LOWERBOUND:
                alpha = max(alpha, tt_entry['value'])

            elif tt_entry['flag'] == PruneFlags.UPPERBOUND:
                beta = min(beta, tt_entry['value'])

            if alpha >= beta:
                return tt_entry['value'], tt_entry['move']
        best_tt_move = tt_entry['move'] if tt_entry else None
            
        winner = board.check_winner()
        if winner == Player.WHITE:
            return 1000000 + depth, None 
        if winner == Player.BLACK:
            return -1000000 - depth, None
        if depth == 0:
            return self.eval_func(board, depth), None

        moves = board.available_moves(Player.WHITE)
        if not moves: 
            return self.eval_func(board, depth), None

        #gemini suggestion to improve prunning
        def score_move(m):
            if best_tt_move and (m.ix, m.iy, m.fx, m.fy) == (best_tt_move.ix, best_tt_move.iy, best_tt_move.fx, best_tt_move.fy):
                return 10000
            target = board.get_piece(m.fx, m.fy)
            return (100 + shapeFactors[target.shape]) if target else 0
        
        moves.sort(key=score_move, reverse=True)      

        max_eval = float("-inf")
        max_move = moves[0]

        for move in moves:
            captured = board.move_piece(move)
            new_value, _ = self.min_value_cache(board, depth - 1, alpha, beta)
            board.undo_move(move, captured)

            if(new_value > max_eval):
                max_eval = new_value
                max_move = move

            alpha = max(alpha, max_eval)
            if beta <= alpha:
                break
            
        if max_eval <= alpha_orig:
            flag = PruneFlags.UPPERBOUND
        elif max_eval >= beta_orig:
            flag = PruneFlags.LOWERBOUND
        else:
            flag = PruneFlags.EXACT

        self.transposition_table[state_hash] = {
            'value': max_eval,
            'depth': depth,
            'flag': flag,
            'move': max_move
        }
        return max_eval, max_move
        
    
    def min_value_cache(self, board:Board, depth, alpha, beta):
        '''
        Returns the evaluation and the move with the min minimax value.
        '''
        self.nodes += 1

        alpha_orig = alpha
        beta_orig = beta

        state_hash = board.current_hash

        tt_entry = self.transposition_table.get(state_hash)
        if tt_entry and tt_entry['depth'] >= depth:
            self.table_hits += 1
            if tt_entry['flag'] == PruneFlags.EXACT:
                return tt_entry['value'], tt_entry['move']

            elif tt_entry['flag'] == PruneFlags.LOWERBOUND:
                alpha = max(alpha, tt_entry['value'])

            elif tt_entry['flag'] == PruneFlags.UPPERBOUND:
                beta = min(beta, tt_entry['value'])

            if alpha >= beta:
                return tt_entry['value'], tt_entry['move']
        best_tt_move = tt_entry['move'] if tt_entry else None

        winner = board.check_winner()
        if winner == Player.WHITE:
            return 1000000 + depth, None 
        if winner == Player.BLACK:
            return -1000000 - depth, None
        if depth == 0:
            return self.eval_func(board,  depth), None
        
        moves = board.available_moves(Player.BLACK)
        if not moves: 
            return self.eval_func(board, depth), None
        
        #gemini suggestion to improve prunning
        def score_move(m):
            if best_tt_move and (m.ix, m.iy, m.fx, m.fy) == (best_tt_move.ix, best_tt_move.iy, best_tt_move.fx, best_tt_move.fy):
                return 10000
            target = board.get_piece(m.fx, m.fy)
            return (100 + shapeFactors[target.shape]) if target else 0
        
        moves.sort(key=score_move, reverse=True)  

        min_eval = float("inf")
        min_move = moves[0]
        
        for move in moves:
            captured = board.move_piece(move)
            new_value, _ = self.max_value_cache(board, depth - 1, alpha, beta)
            board.undo_move(move,captured)

            if(new_value < min_eval):
                min_eval = new_value
                min_move = move
            beta = min(beta, min_eval)

            if alpha >= min_eval:
                break
            
        if min_eval <= alpha_orig:
            flag = PruneFlags.UPPERBOUND
        elif min_eval >= beta_orig:
            flag = PruneFlags.LOWERBOUND
        else:
            flag = PruneFlags.EXACT

        self.transposition_table[state_hash] = {
            'value': min_eval,
            'depth': depth,
            'flag': flag,
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
                eval, move = self.max_value_cache2(simulation_board, current_depth, float('-inf'), float('inf'))
            else:
                eval, move = self.min_value_cache2(simulation_board, current_depth, float('-inf'), float('inf'))
            
            best_eval = eval
            best_move = move
            
            print(f"Depth {current_depth} completed | Eval: {best_eval}")
            print(f"Nodes: {self.nodes} | TT Hits: {self.table_hits}")
            if abs(best_eval) >= 1000000:
                break

        print(f"Pos eval: {eval}")
        print(f"Nodes: {self.nodes} | TT Hits: {self.table_hits}")

        return best_move
    
    def max_value_cache2(self, board:Board, depth, alpha, beta):
        '''
        Returns the evaluation and the move with the max minimax value.
        '''
        self.nodes += 1

        alpha_orig = alpha
        beta_orig = beta

        state_hash = board.current_hash

        tt_entry = self.transposition_table.get(state_hash)
        if tt_entry and tt_entry['depth'] >= depth:
            self.table_hits += 1
            if tt_entry['flag'] == PruneFlags.EXACT:
                return tt_entry['value'], tt_entry['move']

            elif tt_entry['flag'] == PruneFlags.LOWERBOUND:
                alpha = max(alpha, tt_entry['value'])

            elif tt_entry['flag'] == PruneFlags.UPPERBOUND:
                beta = min(beta, tt_entry['value'])

            if alpha >= beta:
                return tt_entry['value'], tt_entry['move']
        best_tt_move = tt_entry['move'] if tt_entry else None
            
        winner = board.check_winner()
        if winner == Player.WHITE:
            return 1000000 + depth, None 
        if winner == Player.BLACK:
            return -1000000 - depth, None
        if depth == 0:
            return self.eval_func(board, depth), None

        moves = board.available_moves(Player.WHITE)
        if not moves: 
            return self.eval_func(board, depth), None

        #gemini suggestion to improve prunning
        def score_move(m):
            score = 0
        
            # Killer move bonus
            cutoff = self.cutoff_moves.get(depth)
            if cutoff and (m.ix, m.iy, m.fx, m.fy) == (cutoff.ix, cutoff.iy, cutoff.fx, cutoff.fy):
                score += 10000
        
            # TT move bonus
            if best_tt_move and (m.ix, m.iy, m.fx, m.fy) == (best_tt_move.ix, best_tt_move.iy, best_tt_move.fx, best_tt_move.fy):
                score += 9000
        
            target = board.get_piece(m.fx, m.fy)
            if target:
                score += 100 + shapeFactors[target.shape]
        
            return score
        
        moves.sort(key=score_move, reverse=True)      

        max_eval = float("-inf")
        max_move = moves[0]

        for move in moves:
            captured = board.move_piece(move)
            new_value, _ = self.min_value_cache2(board, depth - 1, alpha, beta)
            board.undo_move(move, captured)

            if(new_value > max_eval):
                max_eval = new_value
                max_move = move

            alpha = max(alpha, max_eval)
            if beta <= alpha:
                self.cutoff_moves[depth] = move
                break
            
        if max_eval <= alpha_orig:
            flag = PruneFlags.UPPERBOUND
        elif max_eval >= beta_orig:
            flag = PruneFlags.LOWERBOUND
        else:
            flag = PruneFlags.EXACT

        self.transposition_table[state_hash] = {
            'value': max_eval,
            'depth': depth,
            'flag': flag,
            'move': max_move
        }
        return max_eval, max_move
        
    
    def min_value_cache2(self, board:Board, depth, alpha, beta):
        '''
        Returns the evaluation and the move with the min minimax value.
        '''
        self.nodes += 1

        alpha_orig = alpha
        beta_orig = beta

        state_hash = board.current_hash

        tt_entry = self.transposition_table.get(state_hash)
        if tt_entry and tt_entry['depth'] >= depth:
            self.table_hits += 1
            if tt_entry['flag'] == PruneFlags.EXACT:
                return tt_entry['value'], tt_entry['move']

            elif tt_entry['flag'] == PruneFlags.LOWERBOUND:
                alpha = max(alpha, tt_entry['value'])

            elif tt_entry['flag'] == PruneFlags.UPPERBOUND:
                beta = min(beta, tt_entry['value'])

            if alpha >= beta:
                return tt_entry['value'], tt_entry['move']
        best_tt_move = tt_entry['move'] if tt_entry else None

        winner = board.check_winner()
        if winner == Player.WHITE:
            return 1000000 + depth, None 
        if winner == Player.BLACK:
            return -1000000 - depth, None
        if depth == 0:
            return self.eval_func(board,  depth), None
        
        moves = board.available_moves(Player.BLACK)
        if not moves: 
            return self.eval_func(board, depth), None
        
        #gemini suggestion to improve prunning
        def score_move(m):
            score = 0

            # Killer move bonus
            cutoff = self.cutoff_moves.get(depth)
            if cutoff and (m.ix, m.iy, m.fx, m.fy) == (cutoff.ix, cutoff.iy, cutoff.fx, cutoff.fy):
                score += 10000

            # TT move bonus
            if best_tt_move and (m.ix, m.iy, m.fx, m.fy) == (best_tt_move.ix, best_tt_move.iy, best_tt_move.fx, best_tt_move.fy):
                score += 9000

            target = board.get_piece(m.fx, m.fy)
            if target:
                score += 100 + shapeFactors[target.shape]

            return score
        
        moves.sort(key=score_move, reverse=True)  

        min_eval = float("inf")
        min_move = moves[0]
        
        for move in moves:
            captured = board.move_piece(move)
            new_value, _ = self.max_value_cache2(board, depth - 1, alpha, beta)
            board.undo_move(move,captured)

            if(new_value < min_eval):
                min_eval = new_value
                min_move = move
            beta = min(beta, min_eval)

            if alpha >= min_eval:
                self.cutoff_moves[depth] = move
                break
            
        if min_eval <= alpha_orig:
            flag = PruneFlags.UPPERBOUND
        elif min_eval >= beta_orig:
            flag = PruneFlags.LOWERBOUND
        else:
            flag = PruneFlags.EXACT

        self.transposition_table[state_hash] = {
            'value': min_eval,
            'depth': depth,
            'flag': flag,
            'move': min_move
        }

        return min_eval, min_move