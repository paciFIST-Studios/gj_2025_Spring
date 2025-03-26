
import time

import pygame.surface


class MockCache:
    @staticmethod
    def lookup(var):
        return_a_surface = [
            'surface', 'image',
            'cactus',
            'halfDirt'
        ]
        return_a_sound = [
            'sound', 'audio'
        ]

        if var in return_a_surface:
            return pygame.surface.Surface((1,1))
        elif var in return_a_sound:
            return pygame.mixer.Sound('')
        return var

class MockEngine:
    def __init__(self):
        self.cache = MockCache()

    @staticmethod
    def get_time():
        return time.time()

