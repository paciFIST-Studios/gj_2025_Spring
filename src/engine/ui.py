
from dataclasses import dataclass

from enum import Enum


@dataclass()
class Padding:
    left: int
    top: int
    right: int
    bottom: int

    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

class EColor(str, Enum):
    """ The EColor enum is used to make it easy to work with a small number of defined colors
    """
    HIGHLIGHT_YELLOW = '#FFEB99'
    COOL_GREY = '#35454F'
    BLACK = '#000000'

    # trans colors
    LIGHT_BLUE = '#5BCEFA'
    PINK = '#F5A9B8'
    WHITE = '#FFFFFF'

    # streak colors
    DARK_PURPLE = '#4b1648'
    DARK_BLUE = '#111152'
    DARK_GREEN = '#003833'


