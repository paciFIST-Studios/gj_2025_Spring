
from src.gembo.gameplay.game_mode import GameMode


class AboutGameMode(GameMode):
    def __init__(self, engine, game_mode_data: dict):
        super().__init__(engine, game_mode_data)

    def update(self, delta_time_s: float):
        pass

