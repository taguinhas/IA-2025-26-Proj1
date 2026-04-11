import unittest
from game.board import Board
from game.piece import Piece, Player, Shape, Size, Move
from utils.zobristHash import Zobrist

# Assuming your player is saved here, adjust the import if needed:
from players.minimaxPlayer import MinimaxPlayer, Strategy

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
        """
        Iterative Deepening should hit the TT when multiple move orders 
        lead to the same board state (transpositions).
        """
        # Create a "messy" board state where pieces are interacting.
        # This increases the chance that different move orders result in the same state.
        self.board.place_piece(Piece(Player.WHITE, Shape.SQUARE, Size.SMALL), 2, 3)
        self.board.place_piece(Piece(Player.WHITE, Shape.CIRCLE, Size.BIG), 3, 3)
        self.board.place_piece(Piece(Player.BLACK, Shape.TRIANGLE, Size.SMALL), 2, 2)
        self.board.place_piece(Piece(Player.BLACK, Shape.SQUARE, Size.BIG), 3, 2)
        self.board.hash_board()

        game = MockGame(self.board)
        
        # Increased depth to 4. 
        # Depth 1 & 2 populate the table. 
        # Depth 3 & 4 will revisit those states and also find transpositions.
        ai = MinimaxPlayer("TestAI", dummy_eval, 4, Strategy.IDS)
        
        move = ai.get_player_move(game)
        
        self.board.move_piece(move)

        ai.get_player_move(game)
        print(f"Recorded Hits: {ai.table_hits}")
        self.assertGreater(ai.table_hits, 0, "Transposition table is still not recording hits.")

    def test_avoid_immediate_loss(self):
        """If Black is about to win (reaching row 5), White MUST block or capture."""
        # Setup: White's turn. 
        # Black is at (1, 4), threatening to move to (1, 5) [Black's goal row] next turn.
        # White is at (1, 5) - right in the goal - and MUST capture Black at (1, 4).
        
        # Place White on its own 'home' row (which is Black's goal row)
        self.board.place_piece(Piece(Player.WHITE, Shape.SQUARE, Size.BIG), 1, 5)
        
        # Place Black one step away from victory
        self.board.place_piece(Piece(Player.BLACK, Shape.SQUARE, Size.SMALL), 1, 4)
        
        # Distraction piece for Black elsewhere
        self.board.place_piece(Piece(Player.BLACK, Shape.CIRCLE, Size.SMALL), 5, 0) 
        
        self.board.hash_board()
        self.board.print() # Verify row 4/5 interaction

        game = MockGame(self.board)
        
        # Depth 3: 
        # 1. White moves
        # 2. Black moves (AI sees if Black can reach y=5)
        # 3. Evaluation
        ai = MinimaxPlayer("TestAI", dummy_eval, depth=3)
        
        move = ai.get_player_move(game)
        
        print(move)
        self.assertIsNotNone(move)
        self.assertEqual(move.fx, 1, "AI failed to intercept the winning path at X=1")
        self.assertEqual(move.fy, 4, "AI failed to capture the piece at Y=4")
    
    def test_block_immediate_loss(self):
        """If Black is about to win (reaching row 5), White MUST block or capture."""
        # Setup: White's turn. 
        # Black is at (1, 4), threatening to move to (1, 5) [Black's goal row] next turn.
        # White is at (1, 5) - right in the goal - and MUST capture Black at (1, 4).
        
        # Place White on its own 'home' row (which is Black's goal row)
        self.board.place_piece(Piece(Player.WHITE, Shape.CIRCLE, Size.BIG), 0, 4)
                
        # Threatning to win
        self.board.place_piece(Piece(Player.BLACK, Shape.CIRCLE, Size.BIG), 5, 0) 
        
        self.board.hash_board()
        self.board.print() # Verify row 4/5 interaction

        game = MockGame(self.board)
        
        # Depth 3: 
        # 1. White moves
        # 2. Black moves (AI sees if Black can reach y=5)
        # 3. Evaluation
        ai = MinimaxPlayer("TestAI", dummy_eval, depth=3)
        
        move = ai.get_player_move(game)
        
        print(move)
        self.assertIsNotNone(move)
        self.assertEqual(move.fx, 1, "AI failed to defend home row")
        self.assertEqual(move.fy, 5, "AI failed to defend home row")

    def test_ai_on_terminal_board(self):
        """AI should return None if game is already over."""

        # No black pieces → white already won
        self.board.place_piece(Piece(Player.WHITE, Shape.SQUARE, Size.BIG), 0, 0)
        self.board.hash_board()

        game = MockGame(self.board)
        ai = MinimaxPlayer("TestAI", dummy_eval, depth=2)

        move = ai.get_player_move(game)

        self.assertIsNone(move)
    
    def test_minimax_does_not_corrupt_board(self):
        """Running minimax should not change board state."""

        p1 = Piece(Player.WHITE, Shape.SQUARE, Size.BIG)
        p2 = Piece(Player.BLACK, Shape.CIRCLE, Size.SMALL)

        self.board.place_piece(p1, 2, 2)
        self.board.place_piece(p2, 3, 3)
        self.board.hash_board()

        original_hash = self.board.current_hash

        game = MockGame(self.board)
        ai = MinimaxPlayer("TestAI", dummy_eval, depth=3)

        ai.get_player_move(game)

        self.assertEqual(self.board.current_hash, original_hash)

    def test_same_position_same_move(self):
        """AI should return same move for same board state."""

        p1 = Piece(Player.WHITE, Shape.SQUARE, Size.BIG)
        p2 = Piece(Player.BLACK, Shape.SQUARE, Size.BIG)
        self.board.place_piece(p1, 2, 2)
        self.board.place_piece(p2, 3, 4)
        self.board.hash_board()

        self.board.print()
        game = MockGame(self.board)
        ai = MinimaxPlayer("TestAI", dummy_eval, depth=2)

        move1 = ai.get_player_move(game)
        move2 = ai.get_player_move(game)

        self.assertEqual((move1.fx, move1.fy), (move2.fx, move2.fy))
if __name__ == '__main__':
    unittest.main()