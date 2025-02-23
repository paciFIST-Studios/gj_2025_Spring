# python imports
from math import sin
import time

# pygame imports
from pygame import Surface
from pygame.draw import (line as pygame_draw_line,
                         circle as pygame_draw_circle)

# engine imports
from src.engine.ui import Padding, EColor


def get_scaled_sin(x):
    return (sin(x ) /2) + 0.5


def render_breathe_box(surface: Surface, padding: Padding, color: EColor, width: int = 1, is_animated=True, breathe_ratio: float = 20):
    """ The "breathe box" is a box that rhythmically contracts, according to the value 'breathe_ratio'.  This value could range (20, 3)
    """
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

