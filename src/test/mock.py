
import time

import pygame.surface


class MockPygameSurfaceDict(dict):
    """ This is a dictionary, which returns a static PySurface object for any key """
    SURFACE = pygame.surface.Surface((1,1))

    def __getitem__(self, key):
        return MockPygameSurfaceDict.SURFACE


class MockPygameSoundDict(dict):
    """ This is a dictionary, which returns a static PySound object for any key """
    SOUND = None

    def __init__(self):
        super().__init__(self)
        # we don't have access to the Sound class if pygame.mixer is not initialized,
        # so initializing it here is a necessary step to make it testable
        if not pygame.mixer.get_init():
            pygame.mixer.init()

    def __getitem__(self, key):
        return MockPygameSoundDict.SOUND


class MockCache:
    """ This cache exists, so we can test code which requests resources that have already been loaded.
     Right now, that's only images and sounds (also fonts), but it will grow over time
    """
    IMAGE_SURFACE = MockPygameSurfaceDict()
    AUDIO_SOUND = MockPygameSoundDict()

    @staticmethod
    def lookup(var):
        return_a_surface = [
            'surface', 'image',
            'loaded_image_surfaces'
        ]
        return_a_sound = [
            'sound', 'audio',
            'loaded_audio_sounds'
        ]

        if var in return_a_surface:
            return MockCache.IMAGE_SURFACE
        elif var in return_a_sound:
            return MockCache.AUDIO_SOUND
        return var


class MockEngine:
    def __init__(self):
        self.cache = MockCache()

    @staticmethod
    def get_time():
        return time.time()

