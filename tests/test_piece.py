#tests generated using Gemini
import unittest
from game.piece import Piece, Player, Shape, Size, Move

# A simple "fake" board to test piece logic without needing the real Board class
class MockBoard:
    def __init__(self, size=6):
        self.size = size
        self.pieces = {} # Maps (x, y) -> Piece object

    def in_bounds(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size

    def get_piece(self, x, y):
        return self.pieces.get((x, y))

class TestPiece(unittest.TestCase):
    def setUp(self):
        self.board = MockBoard(6)

    def test_small_square_movement(self):
        """Small Square should move exactly 1 step orthogonally."""
        p = Piece(Player.WHITE, Shape.SQUARE, Size.SMALL)
        # Place at center (2,2)
        moves = p.get_moves(self.board, 2, 2)
        
        # Should have 4 moves: (2,1), (2,3), (1,2), (3,2)
        self.assertEqual(len(moves), 4)
        for m in moves:
            # Check that distance is exactly 1
            dist = abs(m.fx - 2) + abs(m.fy - 2)
            self.assertEqual(dist, 1)

    def test_big_triangle_sliding(self):
        """Big Triangle should slide diagonally to the edges."""
        p = Piece(Player.WHITE, Shape.TRIANGLE, Size.BIG)
        moves = p.get_moves(self.board, 0, 0)
        
        # From (0,0), can only move towards (5,5) diagonally
        # Moves: (1,1), (2,2), (3,3), (4,4), (5,5)
        self.assertEqual(len(moves), 5)
        self.assertTrue(any(m.fx == 5 and m.fy == 5 for m in moves))

    def test_collision_logic(self):
        """Should stop BEFORE friend and ON enemy (capture)."""
        white_p = Piece(Player.WHITE, Shape.CIRCLE, Size.BIG)
        friend = Piece(Player.WHITE, Shape.SQUARE, Size.SMALL)
        enemy = Piece(Player.BLACK, Shape.SQUARE, Size.SMALL)
        
        self.board.pieces[(2, 0)] = friend # Block North at (2,0)
        self.board.pieces[(0, 2)] = enemy  # Capture West at (0,2)
        
        moves = white_p.get_moves(self.board, 2, 2)
        
        # FIX: (2,1) IS a valid move because it's an empty square before the friend
        self.assertTrue(any(m.fx == 2 and m.fy == 1 for m in moves), "Should be able to move to (2,1)")
        
        # But (2,0) should NOT be there because it's a friend
        self.assertFalse(any(m.fx == 2 and m.fy == 0 for m in moves), "Should NOT be able to capture friend at (2,0)")
        
        # Check West (Enemy): Should include (0,2) but nothing further
        self.assertTrue(any(m.fx == 0 and m.fy == 2 for m in moves), "Should be able to capture enemy at (0,2)")

    def test_out_of_bounds(self):
        """Should not generate moves off the board."""
        p = Piece(Player.WHITE, Shape.SQUARE, Size.SMALL)
        moves = p.get_moves(self.board, 0, 0)
        
        # At (0,0), Square can only move to (1,0) and (0,1)
        self.assertEqual(len(moves), 2)
        for m in moves:
            self.assertTrue(self.board.in_bounds(m.fx, m.fy))

if __name__ == '__main__':
    unittest.main()