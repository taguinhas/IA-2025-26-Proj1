import unittest
import os
from game.game import Game
from game.piece import Player, Shape, Size


class TestGame(unittest.TestCase):

    def setUp(self):
        self.game = Game()

    def test_initial_board_population(self):
        """Game should initialize with correct number of pieces."""
        board = self.game.board

        # 6 columns × 4 rows filled = 24 pieces
        self.assertEqual(board.white_count, 12)
        self.assertEqual(board.black_count, 12)

        # Check a few known positions
        self.assertEqual(board.get_piece(0, 5).owner, Player.WHITE)  # big white
        self.assertEqual(board.get_piece(0, 4).size, Size.SMALL)     # small white
        self.assertEqual(board.get_piece(0, 0).owner, Player.BLACK)  # big black
        self.assertEqual(board.get_piece(0, 1).size, Size.SMALL)     # small black

    def test_turn_switching(self):
        """change_turn should correctly alternate players."""
        self.assertEqual(self.game.get_cur_player(), Player.WHITE)

        self.game.change_turn()
        self.assertEqual(self.game.get_cur_player(), Player.BLACK)

        self.game.change_turn()
        self.assertEqual(self.game.get_cur_player(), Player.WHITE)

    def test_get_cur_player_matches_board(self):
        """Game.get_cur_player should match board state."""
        self.assertEqual(
            self.game.get_cur_player(),
            self.game.board.get_cur_player()
        )

    def test_load_board_from_file(self):
        """Loading a board from file should correctly place pieces."""
        
        # Create a temporary test file
        filename = "test_board.txt"
        with open(filename, "w") as f:
            f.write(
                "WS . . . . .\n"
                ". bt . . . .\n"
                ". . . . . .\n"
                ". . . . . .\n"
                ". . . . . .\n"
                ". . . . . .\n"
            )

        self.game.load_board_from_file(filename)
        board = self.game.board

        # Check white square BIG at (0,0)
        piece1 = board.get_piece(0, 0)
        self.assertEqual(piece1.owner, Player.WHITE)
        self.assertEqual(piece1.shape, Shape.SQUARE)
        self.assertEqual(piece1.size, Size.BIG)

        # Check black triangle SMALL at (1,1)
        piece2 = board.get_piece(1, 1)
        self.assertEqual(piece2.owner, Player.BLACK)
        self.assertEqual(piece2.shape, Shape.TRIANGLE)
        self.assertEqual(piece2.size, Size.SMALL)

        os.remove(filename)

    def test_load_board_invalid_token(self):
        """Invalid tokens should raise an exception."""
        
        filename = "bad_board.txt"
        with open(filename, "w") as f:
            f.write("XX . . . . .\n")

        with self.assertRaises(Exception):
            self.game.load_board_from_file(filename)

        os.remove(filename)


if __name__ == '__main__':
    unittest.main()