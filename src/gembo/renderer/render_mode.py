# python imports

from abc import ABC, abstractmethod
from math import sin
import time

import pygame.font
from pygame.font import Font as pygame_font

# pygame imports
from pygame.surface import Surface
from pygame.draw import (line as pygame_draw_line,
                         circle as pygame_draw_circle)

# engine imports
from src.engine.ui import Padding, EColor

# game imports
from src.gembo.update_modes import EUpdateMode


def get_scaled_sin(x: float):
    """ returns a value between 0 and 1, based on x(float/int) radians

    Args:
        x(float/int) - a number of radians

    Returns:
        result(float) - a float between 0.0 and 1.0
                      - or None, if an invalid x
    """
    if isinstance(x, int) or isinstance(x, float):
        return (sin(x) * 0.5) + 0.5


def render_breathe_box(surface: Surface, padding: Padding, color: EColor, width: int = 1, is_animated=True, breathe_ratio: float = 20):
    """ The "breathe box" is a box that rhythmically contracts, according to the value 'breathe_ratio'.  This value could range (20, 3)
    """
    if surface is None or not isinstance(surface, Surface):
        return False
    elif padding is None or not isinstance(padding, Padding):
        return False
    elif color is None or not isinstance(color, EColor):
        return False
    elif width is None or not isinstance(width, int):
        return False
    elif is_animated is None or not isinstance(is_animated, bool):
        return False
    elif breathe_ratio is None or not isinstance(breathe_ratio, float):
        return False


    # don't delete this, it isn't using the surface from the outer scope
    surface_width, surface_height = surface.get_size()

    # line positions
    left = padding.left
    right = padding.right
    top = padding.top
    bottom = padding.bottom

    if is_animated:
        # this animation causes the lines to contract (is this cubic?)
        time_now = time.time()
        scaled_sin = get_scaled_sin(time_now)

        # offset both scales by an amount determined by that axis of the screen, and its length
        # this keeps the aspect ratio the same
        offset_w = surface_width / breathe_ratio * scaled_sin
        offset_h = surface_height / breathe_ratio * scaled_sin

        left += scaled_sin * offset_w
        right += scaled_sin * -offset_w
        top += scaled_sin * offset_h
        bottom += scaled_sin * -offset_h

        pygame_draw_line(surface, color, (left, top), (right, top), width)
        pygame_draw_line(surface, color, (left, top), (left, bottom), width)
        pygame_draw_line(surface, color, (right, top), (right, bottom), width)
        pygame_draw_line(surface, color, (left, bottom), (right, bottom), width)

        half_width = width/2
        width_minus_one = width - 1

        pygame_draw_circle(surface, color, (left, top), radius=half_width, width=width_minus_one)
        pygame_draw_circle(surface, color, (right, top), radius=half_width, width=width_minus_one)
        pygame_draw_circle(surface, color, (left, bottom), radius=half_width, width=width_minus_one)
        pygame_draw_circle(surface, color, (right, bottom), radius=half_width, width=width_minus_one)

    return True


class AbstractRenderMode(ABC):
    def __init__(self, engine, render_surface: Surface, mode: EUpdateMode, render_data: dict):
        self.engine = engine
        self.render_surface = render_surface
        self.game_mode = mode
        self.render_data = render_data

        self.surface_width, self.surface_height = self.render_surface.get_size()


    def value_or_default(self, key, default = None):
        if key and key in self.render_data:
            return self.render_data[key]
        return default

    @abstractmethod
    def render(self):
        """ all render modes need to override this fn with their own version """
        pass


# MenuBase
class RenderMenuBase(AbstractRenderMode):
    def __init__(self, engine, surface: Surface, mode: EUpdateMode, render_data: dict):
        super().__init__(engine, surface, mode, render_data)
        self.title_font = self.value_or_default('title_font')

    def render_menu_floor_box(self):
        line_padding = self.value_or_default('line_padding', 10)
        color = self.value_or_default('color', EColor.COOL_GREY)

        left = 0 + line_padding
        right = self.surface_width - line_padding
        top = 0 + line_padding
        bottom = self.surface_height - line_padding

        render_breathe_box(self.render_surface, Padding(left, top, right, bottom), color, True)

    def render_title_text(self, title_text):
        """ renders the given string as a title, at the top of the screen """

        renderable_text = self.title_font.render(title_text, True, self.engine.ui.get_highlight_color())

        # calculate centered on screen position
        total_width, _ = renderable_text.get_size()
        pos_y = 30
        pos_x = (self.surface_width/2) - (total_width/2)

        # blit
        self.render_surface.blit(renderable_text, (pos_x, pos_y))

    def render_horizontal_fill_bar(self, font: pygame_font, position: tuple[int, int], filled_count: int, sections_count: int):
        def _build_display_string(filled: int, sections: int):
            display = '['
            display += '+' * filled
            display += ' ' * (sections - filled)
            display += ']'
            return display

        display_string = _build_display_string(int(filled_count), int(sections_count))
        renderable_text = font.render(display_string, True, self.engine.ui.get_highlight_color())
        self.render_surface.blit(renderable_text, position)

    def render_on_off_toggle(self, font: pygame_font, position: tuple[int, int], is_on: bool):
        def _build_display_string(_is_on: bool):
            text = 'ON' if _is_on else 'OFF'
            display = f'< {text} >'
            return display

        display_string = _build_display_string(is_on)
        renderable_text = font.render(display_string, True, self.engine.ui.get_highlight_color())
        self.render_surface.blit(renderable_text, position)


    def render(self):
        pass
