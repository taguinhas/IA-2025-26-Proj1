from abc import ABC, abstractmethod
from game.game import Game
from game.piece import Move
class genericPlayer(ABC):
    
    def __init__(self, name):
        self.name = name
    @abstractmethod
    def get_player_move(self, game:Game) -> Move:
        pass