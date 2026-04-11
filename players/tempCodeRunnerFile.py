"""Assigns priority to moves to improve Alpha-Beta pruning."""
        #if the move was found to be the best move for this board state we should check it first
        if tt_move and (move.ix, move.iy, move.fx, move.fy) == (tt_move.ix, tt_move.iy, tt_move.fx, tt_move.fy):
            return 100000

        #then we search moves that caused a cutoff
        cutoff = self.cutoff_moves.get(depth)
        if cutoff and (move.ix, move.iy, move.fx, move.fy) == (cutoff.ix, cutoff.iy, cutoff.fx, cutoff.fy):
            return 90000
        
        #we check moves that attack other pieces, generally good
        target = board.get_piece(move.fx, move.fy)
        if target:
            return 50000 + shapeFactors[target.shape]

        #finally we check the moves with recorded good scores (or return 0 if its a new move)
        return self.history_table.get((move.ix, move.iy, move.fx, move.fy), 0)