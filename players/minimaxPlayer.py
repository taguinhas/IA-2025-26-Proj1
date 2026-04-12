from players.genericPlayer import genericPlayer
from game.game import Game
from game.board import Board
from game.piece import Move, Player
from utils.heuristics import shapeFactors
from enum import Enum

"""
different search strategies
ABPRUNING does regular minimax alpha beta with pruinning
ABTABLE alpha beta prunning but also uses a transposition table with zobrist hashing
IDS same as ABTABLE but uses iterative depth
IDSALLTABLE same as IDS but also uses:
    cutoff table to keep track of moves that caused cutoffs (more likely to be good moves)
    history table gives value to moves that are repeatedly better than previous (based on depth ^ 2 thanks to chatGPT's suggestion)
"""
class Strategy(Enum):
    ABPRUNING = 0
    ABTABLE = 1
    IDS = 3
    IDSALLTABLES = 4

class PruneFlags(Enum):
    EXACT = 0
    LOWERBOUND = 1
    UPPERBOUND = 2

class MinimaxPlayer(genericPlayer):
    score_weights = {
        "TT": 30000,
        "CO": 10000, 
        "CAP": 20000    
    }
    def __init__(self, name, eval_func, depth, strategy:Strategy = Strategy.IDSALLTABLES):
        super().__init__(name)          # pass name to base
        self.eval_func = eval_func
        self.depth = depth
        self.strategy = strategy

        self.transposition_table = {}
        self.cutoff_moves = {}
        self.history_table = {}
        self.tables_max_size = 500000

        #stats
        self.table_hits = 0 
        self.nodes = 0
        self.cutoffs = 0
    
    def get_player_move(self, game:Game):
        """Find the best move using the Minimax alpha-beta algorithm"""
        
        self.nodes = 0
        self.table_hits = 0
        self.cutoffs = 0
        self._trim_cache()

        board = game.board.copy()

        if board.current_hash == 0:
            board.hash_board()
        
        player = game.get_cur_player()
        best_move = None

        if self.strategy == Strategy.IDS or self.strategy == Strategy.IDSALLTABLES:
            for current_depth in range(1, self.depth + 1):
                val, move = self._search(board, current_depth, float('-inf'), float('inf'), player)
                best_move = move
                #print(f"Depth {current_depth} | Eval: {val} | Nodes: {self.nodes}")
                if abs(val) >= 1000000: 
                    break
        else:
            #standard AB or AB with Table
            _, best_move = self._search(board, self.depth, float('-inf'), float('inf'), player)
        #print(f"TT Hits: {self.table_hits} | Cutoffs: {self.cutoffs}")
        
        return best_move
    
    def _search(self, board:Board, depth, alpha, beta, player):
        """Main search function"""
        self.nodes += 1
        alpha_orig, beta_orig = alpha, beta
        state_hash = board.current_hash

        tt_move = None
        #first we search the TT table for this move
        if self.strategy != Strategy.ABPRUNING:
            tt_entry = self.transposition_table.get(state_hash)
            tt_move = tt_entry['move'] if tt_entry else None        
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

        #then check winners
        winner = board.check_winner()
        if winner == Player.WHITE:
            return 1000000 + depth, None
        if winner == Player.BLACK:
            return -1000000 - depth, None
        if depth == 0:
            return self.eval_func(board, depth), None
        
        #get moves
        moves = board.available_moves(player)
        if not moves:
            #this should never happen. Unlike chess there are no "illegal" moves 
            return self.eval_func(board, depth), None
        
        #sort moves by their predicted quality. usefull for better pruning
        moves.sort(key=lambda m: self._score_move(board, m, depth, tt_move), reverse=True)

        #search set up
        best_val = float('-inf') if player == Player.WHITE else float('inf')
        best_move = moves[0]
        next_player = Player.BLACK if player == Player.WHITE else Player.WHITE

        #main search. does both max and min to avoid duplicating code. "oldMinimaxPlayer" got extremely chaotic really quick
        for move in moves:
            captured = board.move_piece(move)
            new_val, _ = self._search(board, depth - 1, alpha, beta, next_player)
            board.undo_move(move, captured)

            key = (move.ix, move.iy, move.fx, move.fy)
            if player == Player.WHITE:
                if new_val > best_val:
                    best_val, best_move = new_val, move
        
                    if self.strategy == Strategy.IDSALLTABLES:
                        self.history_table[key] = self.history_table.get(key, 0) + depth * depth

                alpha = max(alpha, best_val)
            else:
                if new_val < best_val: 
                    best_val, best_move = new_val, move

                    if self.strategy == Strategy.IDSALLTABLES:
                        self.history_table[key] = self.history_table.get(key, 0) + depth * depth

                beta = min(beta, best_val)

            if beta <= alpha:
                if self.strategy == Strategy.IDSALLTABLES:
                    self.cutoffs += 1
                    self.cutoff_moves[depth] = move
                break
            
        #then we update the tables
        if self.strategy != Strategy.ABPRUNING:
            self._store_tt(state_hash, best_val, depth, best_move, alpha_orig, beta_orig)

        return best_val, best_move

    def _score_move(self, board:Board, move:Move, depth, tt_move):
        """Assigns priority to moves to improve Alpha-Beta pruning."""
        #check the moves with recorded good score
        score = self.history_table.get((move.ix, move.iy, move.fx, move.fy), 0)
        
        #if the move was found to be the best move for this board state we should check it first
        if tt_move and (move.ix, move.iy, move.fx, move.fy) == (tt_move.ix, tt_move.iy, tt_move.fx, tt_move.fy):
            score += self.score_weights['TT']

        #then we search moves that caused a cutoff
        cutoff = self.cutoff_moves.get(depth)
        if cutoff and (move.ix, move.iy, move.fx, move.fy) == (cutoff.ix, cutoff.iy, cutoff.fx, cutoff.fy):
            score += self.score_weights['CO']
        
        #we check moves that attack other pieces, generally good
        target = board.get_piece(move.fx, move.fy)
        if target:
            score += self.score_weights['CAP'] + shapeFactors[target.shape]

        return score
        
    def _store_tt(self, h, val, depth, move:Move, a_orig, b_orig):
        """stores TT"""
        if val <= a_orig: 
            flag = PruneFlags.UPPERBOUND
        elif val >= b_orig:
            flag = PruneFlags.LOWERBOUND
        else:
            flag = PruneFlags.EXACT
        self.transposition_table[h] = {
            'value': val,
            'depth': depth, 
            'flag': flag, 
            'move': move
        }

    def _trim_cache(self):
        """clears caches if they are above allowed size"""
        if len(self.transposition_table) > self.tables_max_size:
            self.transposition_table.clear()

        if len(self.cutoff_moves) > self.tables_max_size:
            self.cutoff_moves.clear()

        if len(self.history_table) > self.tables_max_size:
            self.history_table.clear()