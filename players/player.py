from abc import ABC, abstractmethod
from game.game import Game
class genericPlayer(ABC):
    @abstractmethod
    def get_player_move(self, game:Game):
        pass