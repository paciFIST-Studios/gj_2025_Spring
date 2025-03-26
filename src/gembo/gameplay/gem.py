from pygame.math import Vector2 as PyVector2
from pygame.surface import Surface as PySurface

from pygame.mixer import Sound as PySound

from src.gembo.gameplay.game_object import GameObject

class GemGameObject(GameObject):
    def __init__(self, engine):
        super().__init__(engine)
        self.pickup_sound: PySound = None
        self.blue_image: PySurface = None
        self.blue_sfx: PySound = None
        self.yellow_image: PySurface = None
        self.yellow_sfx: PySound = None
        self.respawn_timeout_ms: int = 0
        self.pickup_radius: int = 0

    def init(self):
        self.blue_image = self._engine.cache.lookup('loaded_image_surfaces')['gemBlue']
        self.blue_sfx = self._engine.cache.lookup('loaded_audio_sounds')['misc_menu_2']

        self.yellow_image = self._engine.cache.lookup('loaded_image_surfaces')['gemYellow']
        self.yellow_sfx = self._engine.cache.lookup('loaded_audio_sounds')['coin10']

        self.set_image(self.yellow_image)
        self.respawn_timeout_ms = 500
        self.pickup_radius = 70

    def is_ripe(self):
        return self._image == self.yellow_image

    def set_ripe(self, set_to: bool):
        """ True, sets to 'ripe' state
            False, sets to 'spoiled' state
         """
        if set_to is True:
            self._image = self.yellow_image
            self.pickup_sound = self.yellow_sfx
        else:
            self._image = self.blue_image
            self.pickup_sound = self.blue_sfx

    def is_colliding_with_position(self, pos: PyVector2) -> bool:
        if self._collision_hidden:
            distance = pos - self._position
            magnitude = distance.magnitude()
            if magnitude < self.pickup_radius:
                return True

        return False

