from players.player import genericPlayer
from game.game import Game

class MinimaxPlayer(genericPlayer):
    def get_player_move(self, game:Game):
        move = self.minimax_alpha_beta_search(game)
        return move
    
    def minimax_alpha_beta_search(self, game):
        pass