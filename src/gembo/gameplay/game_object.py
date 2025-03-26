import pygame.math
from pygame.surface import Surface as PySurface
from pygame.math import Vector2 as PyVector2


class GameObject:
    def __init__(self, engine):
        self._engine = engine

        # the current position of this object
        self._position: PyVector2 = PyVector2(-100, -100)

        # the game object is rendered at position+position_offset
        self._rendering_offset: PyVector2 = PyVector2(0, 0)

        # the image, is a single PyGame Surface, which should be rendered in its entirety, as the position
        self._image: PySurface = None

        # rendering is sorted into layers, from back to front
        self._render_layer: int = 0

        # if true, this game object will not draw itself during the rendering phase
        self._do_not_render: bool = False

        # if true, this game object will return "no collision" for any collision detection
        self._collision_hidden: bool = False

        self.init()

    def init(self):
        pass

    def is_colliding_with_position(self, pos: PyVector2) -> bool:
        if self._collision_hidden:
            return False
        return True

    def get_position(self) -> PyVector2:
        return self._position

    def set_position(self, new_pos: PyVector2):
        """ Raises AssertionError if you try to set position to a type other than pygame.math.Vector2 """
        assert isinstance(new_pos, pygame.math.Vector2)
        self._position = new_pos

    def get_rendering_offset(self) -> PyVector2:
        return self._rendering_offset

    def set_rendering_offset(self, new_offset):
        """ Raises AssertionError if you try to set position to a type other than pygame.math.Vector2 """
        assert isinstance(new_offset, PyVector2)
        self._rendering_offset = new_offset

    def get_image(self) -> PySurface:
        return self._image

    def set_image(self, image):
        """ Raises AssertionError if you try to set position to a type other than pygame.surface.Surface """
        assert isinstance(image, PySurface)
        self._image = image


    def render(self, render_to: PySurface) -> bool:
        """ Render is called as the last step during a frame.  Classes derived from GameObject can override
         this fn as desired.  With an override, GameObjects are simply blitted using their image, position,
         and rendering offset
         """
        if self._do_not_render:
            return False
        elif render_to is None or not isinstance(render_to, PySurface):
            return False
        elif self._image is None or not isinstance(self._image, PySurface):
            return False
        elif self._position is None or not isinstance(self._position, PyVector2):
            return False
        elif self._rendering_offset is None or not isinstance(self._rendering_offset, PyVector2):
            return False

        render_image = self._image
        render_position = self._position + self._rendering_offset
        render_to.blit(render_image, render_position)
        return True


    def update(self, delta_time_s: float):
        pass

    def collision_update(self):
        """ Collision Update runs after the Update fn, and it resolves any
        collisions which may have occurred during the update """
        pass
