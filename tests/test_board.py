import unittest
from game.board import Board
from game.piece import Piece, Player, Move, Shape, Size
from utils.zobristHash import Zobrist

class TestBoard(unittest.TestCase):
    def setUp(self):
        self.size = 6
        self.zobrist = Zobrist(self.size)
        # Standard starting player: White
        self.board = Board(self.size, Player.WHITE, self.zobrist)
        self.board.hash_board()

    def test_placement_updates_counts(self):
        """Placing pieces should correctly update white_count and black_count."""
        p_white = Piece(Player.WHITE, Shape.SQUARE, Size.SMALL)
        p_black = Piece(Player.BLACK, Shape.CIRCLE, Size.BIG)
        
        self.board.place_piece(p_white, 0, 0)
        self.board.place_piece(p_black, 1, 1)
        
        self.assertEqual(self.board.white_count, 1)
        self.assertEqual(self.board.black_count, 1)
        
        self.board.remove_piece(0, 0)
        self.assertEqual(self.board.white_count, 0)

    def test_move_piece_and_turn_change(self):
        """Moving a piece should update the board, the turn, and the hash."""
        p = Piece(Player.WHITE, Shape.SQUARE, Size.BIG)
        self.board.place_piece(p, 3, 5)
        self.board.hash_board()
        
        initial_hash = self.board.current_hash
        move = Move(3, 5, 3, 4)
        
        self.board.move_piece(move)
        
        self.assertIsNone(self.board.get_piece(3, 5))
        self.assertEqual(self.board.get_piece(3, 4), p)
        self.assertEqual(self.board.get_cur_player(), Player.BLACK)
        self.assertNotEqual(self.board.current_hash, initial_hash)

    def test_undo_restores_state_perfectly(self):
        """Undo MUST restore board, turn, counts, and hash to original values."""
        p_white = Piece(Player.WHITE, Shape.SQUARE, Size.BIG)
        p_black = Piece(Player.BLACK, Shape.CIRCLE, Size.SMALL)
        
        self.board.place_piece(p_white, 2, 2)
        self.board.place_piece(p_black, 2, 1)
        self.board.hash_board()
        
        start_hash = self.board.current_hash
        start_white = self.board.white_count
        start_black = self.board.black_count
        
        # White captures Black
        move = Move(2, 2, 2, 1)
        captured = self.board.move_piece(move)
        
        self.assertEqual(self.board.black_count, start_black - 1)
        
        # Undo it
        self.board.undo_move(move, captured)
        
        self.assertEqual(self.board.current_hash, start_hash, "Hash not restored!")
        self.assertEqual(self.board.white_count, start_white)
        self.assertEqual(self.board.black_count, start_black)
        self.assertEqual(self.board.get_cur_player(), Player.WHITE)
        self.assertEqual(self.board.get_piece(2, 1), p_black)

    def test_win_by_elimination(self):
        """Game ends if a player has 0 pieces."""
        p_white = Piece(Player.WHITE, Shape.SQUARE, Size.SMALL)
        self.board.place_piece(p_white, 0, 0)
        
        # White exists, Black doesn't
        self.assertEqual(self.board.check_winner(), Player.WHITE)

    def test_win_by_goal_row(self):
        """A player wins if they reach the goal row and are NOT under attack."""
        # Setup: White piece at (2,0) [White's goal row]
        p_white = Piece(Player.WHITE, Shape.SQUARE, Size.SMALL)
        p_black = Piece(Player.BLACK, Shape.SQUARE, Size.SMALL)
        
        self.board.place_piece(p_white, 2, 0)
        self.board.place_piece(p_black, 5, 4) # Distant piece so white_count > 0
        
        # Case 1: No one attacks (2,0)
        self.assertEqual(self.board.check_winner(), Player.WHITE)
        
        # Case 2: Black attacks (2,0)
        # Move black piece to (2,5). A Big Square at (2,5) attacks (2,0).
        big_black_square = Piece(Player.BLACK, Shape.SQUARE, Size.BIG)
        self.board.place_piece(big_black_square, 2, 4)
        self.board.print()
        # Now White should NOT be the winner because (2,0) is under attack
        self.assertIsNone(self.board.check_winner())

if __name__ == '__main__':
    unittest.main()