#tests generated using Gemini
import unittest
from utils.zobristHash import Zobrist
from game.piece import Piece, Player, Shape, Size

class TestZobrist(unittest.TestCase):
    def setUp(self):
        self.size = 6
        self.zobrist = Zobrist(self.size)

    def test_consistent_hashing(self):
        """Identical boards and turns must result in the same hash."""
        p1 = Piece(Player.WHITE, Shape.SQUARE, Size.BIG)
        
        # Create two separate boards with the same piece at (2,3)
        board1 = [[None for _ in range(self.size)] for _ in range(self.size)]
        board2 = [[None for _ in range(self.size)] for _ in range(self.size)]
        board1[2][3] = p1
        board2[2][3] = p1
        
        h1 = self.zobrist.hash(board1, Player.WHITE)
        h2 = self.zobrist.hash(board2, Player.WHITE)
        
        self.assertEqual(h1, h2, "Same board state should produce same hash.")

    def test_turn_independence(self):
        """Changing the turn MUST change the hash."""
        board = [[None for _ in range(self.size)] for _ in range(self.size)]
        h_white = self.zobrist.hash(board, Player.WHITE)
        h_black = self.zobrist.hash(board, Player.BLACK)
        
        self.assertNotEqual(h_white, h_black, "Hash must account for whose turn it is.")

    def test_incremental_integrity(self):
        """XORing a piece hash twice should return to the original hash (reversibility)."""
        p1 = Piece(Player.WHITE, Shape.TRIANGLE, Size.SMALL)
        x, y = 2, 2
        
        start_h = 123456789  # Dummy initial hash
        piece_h = self.zobrist.get_piece_hash(p1, x, y)
        
        # XOR once (Add piece)
        new_h = start_h ^ piece_h
        self.assertNotEqual(start_h, new_h)
        
        # XOR twice (Remove piece)
        restored_h = new_h ^ piece_h
        self.assertEqual(start_h, restored_h, "XORing twice should restore the original hash.")

    def test_full_vs_incremental(self):
        """Full board hash should match manual XORing of pieces."""
        p1 = Piece(Player.WHITE, Shape.CIRCLE, Size.BIG)
        p2 = Piece(Player.BLACK, Shape.SQUARE, Size.SMALL)
        
        # Setup board with pieces at (0,0) and (5,5)
        board = [[None for _ in range(self.size)] for _ in range(self.size)]
        board[0][0] = p1
        board[5][5] = p2
        
        # Calculate expected hash manually:
        # 1. Start with Turn hash (it's Black's turn in this test)
        expected_h = self.zobrist.black_to_move 
        # 2. XOR the pieces using your 1D index logic (y*size + x)
        expected_h ^= self.zobrist.get_piece_hash(p1, 0, 0)
        expected_h ^= self.zobrist.get_piece_hash(p2, 5, 5)
        
        actual_h = self.zobrist.hash(board, Player.BLACK)
        
        self.assertEqual(actual_h, expected_h, "Full hash calculation doesn't match incremental logic.")

if __name__ == '__main__':
    unittest.main()