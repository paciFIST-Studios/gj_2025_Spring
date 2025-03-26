from pygame.math import Vector2 as PyVector2
from pygame.surface import Surface as PySurface

from src.gembo.gameplay.game_object import GameObject


class CactusGameObject(GameObject):
    def __init__(self, engine):
        super().__init__(engine)
        self.cactus_base_image: PySurface = None
        self.cactus_base_image_render_offset: PyVector2 = PyVector2()

        self.collision_offset: PyVector2 = PyVector2()
        self.collision_radius_min: int = 0
        self.collision_radius_max: int = 1
        self.collision_radius: int = 0

        self.collision_knockback_force_min: int = 0
        self.collision_knockback_force_max: int = 1
        self.collision_knockback_force: int = 0

        self.is_active: bool = False


    def init(self):
        """ sets the settings for this object """
        # get the images from the engine cache
        self._image = self._engine.cache.lookup('loaded_image_surfaces')['cactus']
        self.cactus_base_image = self._engine.cache.lookup('loaded_image_surfaces')['halfDirt']
        self.cactus_base_image_render_offset = PyVector2(18, 65)
        self.collision_offset = PyVector2(10, 20)

        self.collision_radius_min = 60
        self.collision_radius_max = 85
        self.collision_radius = self.collision_radius_min
        self.collision_knockback_force_min = 2
        self.collision_knockback_force_max = 10
        self.collision_knockback_force = self.collision_knockback_force_min

    def is_colliding_with_position(self, pos: PyVector2) -> bool:
        if self.is_active:
            distance = pos - self._position
            magnitude = distance.magnitude()
            if magnitude < self.collision_radius:
                return True
        return False

    def place_cactus(self):
        # if self._cactus.cactus_is_active:
        #     return
        #
        # pos = self.get_random_onscreen_coordinate(self._display_surface)
        # w, h = self._cactus.image.get_size()
        #
        # pos_x = clamp_onscreen(pos[0], 0, w)
        # pos_y = clamp_onscreen(pos[1], 0, h)
        # self._cactus.position = PygameVector2(pos_x, pos_y)
        # self._cactus.cactus_is_active = True
        # self._gameplay.cactus_position_unchanged_for_n_ripe_gems = 0
        pass

    def collide_with_cactus(self):
        self.is_active = False

    def update(self, delta_time_s: float):
        pass

    def render(self, render_to: PySurface) -> bool:
        if self._do_not_render:
            return False
        elif not self.is_active:
            return False

        # render base of cactus
        base_image = self.cactus_base_image
        base_image_pos = self._position + self.cactus_base_image_render_offset + self._rendering_offset
        render_to.blit(base_image, base_image_pos)

        # render cactus... of cactus
        image = self._image
        image_pos = self._position + self._rendering_offset
        render_to.blit(image, image_pos)

        return True

