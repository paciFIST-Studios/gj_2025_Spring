import unittest
from src.test import AbstractTestBase as TestCase

import time

from pygame.math import Vector2 as PyVector2
from pygame.surface import Surface as PySurface

from src.gembo.gameplay.cactus import CactusGameObject
from src.test.mock import MockEngine


class CactusTestCases(TestCase):

    class MockCactusGameObject(CactusGameObject):
        def __init__(self):
            super().__init__(engine=MockEngine())

    def test_framework_can_pass_a_test(self):
        self.assertTrue(True)

    # class CactusGameObject -------------------------------------------------------------------------------------------

    def test__classCactusGameObject__canBeConstructed(self):
        # note: this uses the actual object, not the mock
        self.assertIsNotNone(CactusGameObject(MockEngine()))

    def test__classCactusGameObject__hasCorrectDefaultMembers_onConstruction(self):
        obj = self.MockCactusGameObject()
        self.assertIsNotNone(obj)

        # cactus_base_image
        self.assertHasAttribute(obj, 'cactus_base_image')
        self.assertIsNone(obj.cactus_base_image)
        # this doesn't have a type until during __init__
        # self.assertIsInstance(obj.cactus_base_image, PySurface)

        # cactus_base_image_render_offset
        self.assertHasAttribute(obj, 'cactus_base_image_render_offset')
        self.assertIsNotNone(obj.cactus_base_image_render_offset)
        self.assertIsInstance(obj.cactus_base_image_render_offset, PyVector2)

        # collision_offset
        self.assertHasAttribute(obj, 'collision_offset')
        self.assertIsNotNone(obj.collision_offset)
        self.assertIsInstance(obj.collision_offset, PyVector2)

        # collision_radius_min
        self.assertHasAttribute(obj, 'collision_radius_min')
        self.assertIsNotNone(obj.collision_radius_min)
        self.assertIsInstance(obj.collision_radius_min, int)
        self.assertEqual(obj.collision_radius_min, 0)

        # collision_radius_max
        self.assertHasAttribute(obj, 'collision_radius_max')
        self.assertIsNotNone(obj.collision_radius_max)
        self.assertIsInstance(obj.collision_radius_max, int)
        self.assertEqual(obj.collision_radius_max, 1)

        # collision_radius
        self.assertHasAttribute(obj, 'collision_radius')
        self.assertIsNotNone(obj.collision_radius)
        self.assertIsInstance(obj.collision_radius, int)
        self.assertEqual(obj.collision_radius, 0)

        # collision_knockback_force_min
        self.assertHasAttribute(obj, 'collision_knockback_force_min')
        self.assertIsNotNone(obj.collision_knockback_force_min)
        self.assertIsInstance(obj.collision_knockback_force_min, int)
        self.assertEqual(obj.collision_knockback_force_min, 0)

        # collision_knockback_force_max
        self.assertHasAttribute(obj, 'collision_knockback_force_max')
        self.assertIsNotNone(obj.collision_knockback_force_max)
        self.assertIsInstance(obj.collision_knockback_force_max, int)
        self.assertEqual(obj.collision_knockback_force_max, 1)

        # collision_knockback_force
        self.assertHasAttribute(obj, 'collision_knockback_force')
        self.assertIsNotNone(obj.collision_knockback_force)
        self.assertIsInstance(obj.collision_knockback_force, int)
        self.assertEqual(obj.collision_knockback_force, 0)

        # is_active
        self.assertHasAttribute(obj, 'is_active')
        self.assertIsNotNone(obj.is_active)
        self.assertFalse(obj.is_active)

    # fn init ----------------------------------------------------------------------------------------------------------

    def test__classCactusGameObject__fnInit__exists(self):
        self.assertIsNotNone(self.MockCactusGameObject().init)

    def test__classCactusGameObject__fnInit__initializesClassMembersCorrectly__whenCalled(self):
        obj = self.MockCactusGameObject()
        obj.init()

        # _image
        self.assertIsNotNone(obj._image)
        self.assertIsInstance(obj._image, PySurface)

        # cactus_base_image
        self.assertIsNotNone(obj.cactus_base_image)
        self.assertIsInstance(obj.cactus_base_image, PySurface)

        # cactus_base_image_render_offset
        self.assertIsNotNone(obj.cactus_base_image_render_offset)
        self.assertIsInstance(obj.cactus_base_image_render_offset, PyVector2)
        self.assertEqual(obj.cactus_base_image_render_offset, PyVector2(18, 65))

        # collision_offset
        self.assertIsNotNone(obj.collision_offset)
        self.assertIsInstance(obj.collision_offset, PyVector2)
        self.assertEqual(obj.collision_offset, PyVector2(10, 20))

        # collision_radius_min
        self.assertIsNotNone(obj.collision_radius_min)
        self.assertIsInstance(obj.collision_radius_min, int)
        self.assertEqual(obj.collision_radius_min, 60)

        # collision_radius_max
        self.assertIsNotNone(obj.collision_radius_max)
        self.assertIsInstance(obj.collision_radius_max, int)
        self.assertEqual(obj.collision_radius_max, 85)

        # collision_radius
        self.assertIsNotNone(obj.collision_radius)
        self.assertIsInstance(obj.collision_radius, int)
        self.assertEqual(obj.collision_radius, obj.collision_radius_min)

        # collision_knockback_force_min
        self.assertIsNotNone(obj.collision_knockback_force_min)
        self.assertIsInstance(obj.collision_knockback_force_min, int)
        self.assertEqual(obj.collision_knockback_force_min, 2)

        # collision_knockback_force_max
        self.assertIsNotNone(obj.collision_knockback_force_max)
        self.assertIsInstance(obj.collision_knockback_force_max, int)
        self.assertEqual(obj.collision_knockback_force_max, 10)

        # collision_knockback_force
        self.assertIsNotNone(obj.collision_knockback_force)
        self.assertIsInstance(obj.collision_knockback_force, int)
        self.assertEqual(obj.collision_knockback_force, obj.collision_knockback_force)

    # fn is_colliding_with_position ------------------------------------------------------------------------------------

    def test__classCactusGameObject__fnIsCollidingWithPosition__exists(self):
        self.assertIsNotNone(self.MockCactusGameObject().is_colliding_with_position)

    def test__classCactusGameObject__fnIsCollidingWithPosition__returnsFalse__ifCactusIsInactive(self):
        obj = self.MockCactusGameObject()
        colliding_position = PyVector2(100, 100)
        obj.collision_radius = 1
        obj.set_position(colliding_position)
        obj.is_active = True
        self.assertTrue(obj.is_colliding_with_position(colliding_position))
        obj.is_active = False
        self.assertFalse(obj.is_colliding_with_position(colliding_position))

    def test__classCactusGameObject__fnIsCollidingWithPosition__returnsTrue__forGenuineCollision(self):
        obj = self.MockCactusGameObject()
        colliding_position = PyVector2(100, 100)
        obj.collision_radius = 1
        obj.set_position(colliding_position)
        obj.is_active = True
        self.assertTrue(obj.is_colliding_with_position(colliding_position))

    def test__classCactusGameObject__fnIsCollidingWithPosition__returnsFalse__forGenuineNonCollision(self):
        obj = self.MockCactusGameObject()
        colliding_position = PyVector2(100, 100)
        obj.collision_radius = 1
        obj.set_position(colliding_position)
        obj.is_active = True
        self.assertTrue(obj.is_colliding_with_position(colliding_position))
        obj.set_position(PyVector2(0, 0))
        self.assertFalse(obj.is_colliding_with_position(colliding_position))

    # fn place_cactus --------------------------------------------------------------------------------------------------

    # is this actually just a gameplay logic fn?


    # fn collide_with_cactus -------------------------------------------------------------------------------------------

    def test__classCactusGameObject__fnCollideWithCactus__exists(self):
        self.assertIsNotNone(self.MockCactusGameObject().collide_with_cactus)

    def test__classCactusGameObject__fnCollideWithCactus__setsIsActiveToFalse(self):
        obj = self.MockCactusGameObject()
        obj.is_active = True
        self.assertTrue(obj.is_active)
        obj.collide_with_cactus()
        self.assertFalse(obj.is_active)

    # fn render --------------------------------------------------------------------------------------------------------

    def test__classCactusGameObject__fnRender__exists(self):
        self.assertIsNotNone(self.MockCactusGameObject().render)

    def test__classCactusGameObject__fnRender__returnsTrue__forRenderSuccess(self):
        # needs a surface to render int
        render_to = PySurface((1,1))
        test_surface = render_to
        obj = self.MockCactusGameObject()
        # won't render if inactive
        obj.is_active = True
        # needs an image for the cactus itself
        obj.set_image(test_surface)
        # needs an image for the base of the cactus
        obj.cactus_base_image = test_surface

        self.assertTrue(obj.render(render_to))

    def test__classCactusGameObject__fnRender__returnsFalse__ifRenderHidden(self):
        # needs a surface to render int
        render_to = PySurface((1,1))
        test_surface = render_to
        obj = self.MockCactusGameObject()
        # won't render if inactive
        obj.is_active = True
        # needs an image for the cactus itself
        obj.set_image(test_surface)
        # needs an image for the base of the cactus
        obj.cactus_base_image = test_surface

        self.assertTrue(obj.render(render_to))
        obj._do_not_render = True
        self.assertFalse(obj.render(render_to))

    def test__classCactusGameObject__fnRender__returnsFalse__ifInactive(self):
        # needs a surface to render int
        render_to = PySurface((1,1))
        test_surface = render_to
        obj = self.MockCactusGameObject()
        # won't render if inactive
        obj.is_active = True
        # needs an image for the cactus itself
        obj.set_image(test_surface)
        # needs an image for the base of the cactus
        obj.cactus_base_image = test_surface

        self.assertTrue(obj.render(render_to))
        obj.is_active = False
        self.assertFalse(obj.render(render_to))


if __name__ == '__main__':
    unittest.main()

