import unittest
from game.board import Board
from game.piece import Piece, Player, Shape, Size, Move
from utils.zobristHash import Zobrist

# Assuming your player is saved here, adjust the import if needed:
from players.minimaxPlayer import MinimaxPlayer 

# A very basic evaluation function for testing purposes
def dummy_eval(board, depth):
    # Simple material advantage
    return (board.white_count * 10) - (board.black_count * 10)

class MockGame:
    """Mock Game class to pass to get_player_move without needing the full Game loop"""
    def __init__(self, board):
        self.board = board

    def get_cur_player(self):
        return self.board.get_cur_player()

class TestMinimaxPlayer(unittest.TestCase):
    def setUp(self):
        self.zobrist = Zobrist(6)
        self.board = Board(6, Player.WHITE, self.zobrist)
        self.board.hash_board()

    def test_find_forced_win_elimination(self):
        """AI should immediately find the move that captures the last enemy piece."""
        # White has a big piece, Black has one small piece right next to it
        p_white = Piece(Player.WHITE, Shape.SQUARE, Size.BIG)
        p_black = Piece(Player.BLACK, Shape.TRIANGLE, Size.SMALL)
        
        self.board.place_piece(p_white, 2, 2)
        self.board.place_piece(p_black, 2, 1) # Directly above White
        self.board.hash_board()
        
        game = MockGame(self.board)
        ai = MinimaxPlayer("TestAI", dummy_eval, depth=2)
        
        move = ai.get_player_move(game)
        
        self.assertIsNotNone(move, "AI returned None instead of a winning move")
        self.assertEqual(move.fx, 2, "AI did not capture the piece!")
        self.assertEqual(move.fy, 1, "AI did not capture the piece!")

    def test_transposition_table_hits_during_id(self):
        """Iterative Deepening MUST hit the transposition table on depth 2+"""
        # Populate the board with a few pieces to give it a branching factor
        self.board.place_piece(Piece(Player.WHITE, Shape.SQUARE, Size.SMALL), 0, 5)
        self.board.place_piece(Piece(Player.WHITE, Shape.CIRCLE, Size.BIG), 1, 5)
        self.board.place_piece(Piece(Player.BLACK, Shape.TRIANGLE, Size.SMALL), 5, 0)
        self.board.place_piece(Piece(Player.BLACK, Shape.SQUARE, Size.BIG), 4, 0)
        self.board.hash_board()

        game = MockGame(self.board)
        
        # We need at least depth 2 to ensure Iterative Deepening searches 
        # depth 1 (caching states), then depth 2 (hitting those cached states).
        ai = MinimaxPlayer("TestAI", dummy_eval, depth=2)
        
        ai.get_player_move(game)
        
        self.assertGreater(ai.table_hits, 0, "Transposition table is not being used! 0 hits recorded.")

    def test_avoid_immediate_loss(self):
        """If Black is about to win, White MUST block or capture, not make a random move."""
        # Setup: It is White's turn. 
        # Black is at (1, 1), threatening to step on (1, 0) [White's goal row] next turn to win.
        # White is at (1, 2) and MUST capture Black at (1, 1) to prevent the loss.
        self.board.place_piece(Piece(Player.WHITE, Shape.SQUARE, Size.BIG), 1, 2)
        self.board.place_piece(Piece(Player.BLACK, Shape.SQUARE, Size.SMALL), 1, 1)
        self.board.place_piece(Piece(Player.BLACK, Shape.CIRCLE, Size.BIG), 5, 5) # Distraction piece
        self.board.hash_board()

        game = MockGame(self.board)
        
        # Depth 3 is required:
        # Depth 1: White moves
        # Depth 2: Black moves (AI sees Black wins if White didn't block)
        # Depth 3: Evaluates the consequences
        ai = MinimaxPlayer("TestAI", dummy_eval, depth=3)
        
        move = ai.get_player_move(game)
        
        self.assertIsNotNone(move)
        self.assertEqual(move.fx, 1, "AI failed to block the winning threat!")
        self.assertEqual(move.fy, 1, "AI failed to capture the threatening piece!")

if __name__ == '__main__':
    unittest.main()