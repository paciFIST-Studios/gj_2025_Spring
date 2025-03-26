import unittest
from src.test import AbstractTestBase as TestCase
from src.test.mock import MockEngine

from pygame.math import Vector2 as PyVector2
from pygame.surface import Surface as PySurface
from pygame.mixer import Sound as PySound

from src.gembo.gameplay.gem import GemGameObject


class GemGameObjectTestCases(TestCase):

    class MockGemGameObject(GemGameObject):
        def __init__(self):
            super().__init__(engine=MockEngine())


    def test_framework_can_pass_a_test(self):
        self.assertTrue(True)

    # class GemGameObject ----------------------------------------------------------------------------------------------

    def test__classGemGameObject__canBeConstructed(self):
        self.assertIsNotNone(GemGameObject(MockEngine()))

    def test__classGemGameObject__hasCorrectDefaultMembers(self):
        obj = self.MockGemGameObject()
        self.assertIsNotNone(obj)

        # pickup sound
        self.assertHasAttribute(obj, 'pickup_sound')
        self.assertIsNone(obj.pickup_sound)

        # blue image
        self.assertHasAttribute(obj, 'blue_image')
        self.assertIsNone(obj.blue_image)

        # blue sfx
        self.assertHasAttribute(obj, 'blue_sfx')
        self.assertIsNone(obj.blue_sfx)

        # yellow image
        self.assertHasAttribute(obj, 'yellow_image')
        self.assertIsNone(obj.yellow_image)

        # yellow sfx
        self.assertHasAttribute(obj, 'yellow_sfx')
        self.assertIsNone(obj.yellow_sfx)

        # respawn timeout ms
        self.assertHasAttribute(obj, 'respawn_timeout_ms')
        self.assertIsInstance(obj.respawn_timeout_ms, int)
        self.assertEqual(obj.respawn_timeout_ms, 0)

        # pickup radius
        self.assertHasAttribute(obj, 'pickup_radius')
        self.assertIsInstance(obj.pickup_radius, int)
        self.assertEqual(obj.pickup_radius, 0)

    # fn init ----------------------------------------------------------------------------------------------------------

    def test__classGemGameObject__fnInit__exists(self):
        self.assertIsNotNone(self.MockGemGameObject().init)

    def test__classGemGameObject__fnInit__initializesMembersCorrectly(self):
        obj = self.MockGemGameObject()

        # blue_image
        self.assertIsNotNone(obj.blue_image)
        self.assertIsInstance(obj.blue_image, PySurface)

        # blue_sfx
        self.assertIsNotNone(obj.blue_sfx)
        self.assertIsInstance(obj.blue_sfx, PySound)

        # yellow_image
        self.assertIsNotNone(obj.yellow_image)
        self.assertIsInstance(obj.yellow_image, PySurface)

        # yellow_sfx
        self.assertIsNotNone(obj.yellow_sfx)
        self.assertIsInstance(obj.yellow_sfx, PySound)

        # respawn_timeout_ms
        self.assertEqual(obj.respawn_timeout_ms, 500)

        # pickup_radius
        self.assertEqual(obj.pickup_radius, 70)

    # fn is_ripe -------------------------------------------------------------------------------------------------------

    def test__classGemGameObject__fnIsRipe__exists(self):
        self.assertIsNotNone(self.MockGemGameObject().is_ripe)





if __name__ == '__main__':
    unittest.main()
