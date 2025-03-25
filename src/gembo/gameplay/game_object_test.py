import unittest

import pygame.surface

from src.test import AbstractTestBase as TestCase
from src.test.mock import MockEngine

from pygame.math import Vector2 as PyVector2
from pygame.surface import Surface as PySurface

from src.engine.resource import load_image
from src.gembo.gameplay import GameObject


class GameObjectTestCases(TestCase):

    class MockGameObject(GameObject):
        def __init__(self):
            super().__init__(engine=MockEngine())


    def test_framework_can_pass_a_test(self):
        self.assertTrue(True)


    # GameObject -------------------------------------------------------------------------------------------------------

    def test__classGameObject__canBeConstructed(self):
        self.assertIsNotNone(GameObject(None))

    def test__classGameObject__hasCorrectDefaultMembers(self):
        obj = self.MockGameObject()
        self.assertIsNotNone(obj)

        # _engine
        self.assertHasAttribute(obj, '_engine')
        self.assertIsNotNone(obj._engine)

        # _position
        self.assertHasAttribute(obj, '_position')
        self.assertIsNotNone(obj._position)
        self.assertIsInstance(obj._position, PyVector2)
        self.assertEqual(obj._position, PyVector2(-100, -100))

        # _position_offset
        self.assertHasAttribute(obj, '_rendering_offset')
        self.assertIsNotNone(obj._rendering_offset)
        self.assertIsInstance(obj._rendering_offset, PyVector2)
        self.assertEqual(obj._rendering_offset, PyVector2(0, 0))

        # _image
        self.assertHasAttribute(obj, '_image')
        self.assertIsNone(obj._image)

        # _render_layer
        self.assertHasAttribute(obj, '_render_layer')
        self.assertIsNotNone(obj._render_layer)
        self.assertIsInstance(obj._render_layer, int)
        self.assertEqual(obj._render_layer, 0)

        # _render_hidden
        self.assertHasAttribute(obj, '_render_hidden')
        self.assertIsNotNone(obj._render_hidden)
        self.assertIsInstance(obj._render_hidden, bool)
        self.assertFalse(obj._collision_hidden)

        # _collision_hidden
        self.assertHasAttribute(obj, '_collision_hidden')
        self.assertIsNotNone(obj._collision_hidden)
        self.assertIsInstance(obj._collision_hidden, bool)
        self.assertFalse(obj._collision_hidden)

    # fn init ----------------------------------------------------------------------------------------------------------

    def test__classGameObject__fnInit__exists(self):
        self.assertIsNotNone(self.MockGameObject.init)

    def test__classGameObject__fnInit__doesNotThrowError__whenCalled(self):
        obj = self.MockGameObject()
        try:
            obj.init()
            self.assertTrue(True)
        except:
            self.assertTrue(False)

    # fn is_colliding_with_position ------------------------------------------------------------------------------------

    def test__classGameObject__fnIsCollidingWithPosition__exists(self):
        self.assertIsNotNone(self.MockGameObject.is_colliding_with_position)

    def test__classGameObject__fnIsCollidingWithPosition__returnsFalse__whenCollisionIsHidden(self):
        obj = self.MockGameObject()
        obj._collision_hidden = True
        self.assertFalse(obj.is_colliding_with_position(None))

    # TODO: update
    def test__classGameObject__fnIsCollidingWithPosition__returnsTrue__whenCollisionOccurs(self):
        obj = self.MockGameObject()
        self.assertTrue(obj.is_colliding_with_position(None))

    # fn get_position --------------------------------------------------------------------------------------------------

    def test__classGameObject__fnGetPosition__exists(self):
        obj = self.MockGameObject()
        self.assertIsNotNone(obj.get_position)

    def test__classGameObject__fnGetPosition__returnsObjectPosition__whenCalled(self):
        obj = self.MockGameObject()
        pos = obj.get_position()
        self.assertIsNotNone(pos)
        self.assertIsInstance(pos, PyVector2)
        self.assertEqual(pos, PyVector2(-100, -100))
        obj._position = PyVector2(5, 5)
        pos = obj.get_position()
        self.assertIsNotNone(pos)
        self.assertIsInstance(pos, PyVector2)
        self.assertEqual(pos, PyVector2(5, 5))

    # fn set_position --------------------------------------------------------------------------------------------------

    def test__classGameObject__fnSetPosition__exists(self):
        obj = self.MockGameObject()
        self.assertIsNotNone(obj.set_position)

    def test__classGameObject__fnSetPosition__raisesAssertionError__ifCalledWithBadArg(self):
        obj = self.MockGameObject()
        self.assertRaises(AssertionError, obj.set_position, None)
        self.assertRaises(AssertionError, obj.set_position, 1)
        self.assertRaises(AssertionError, obj.set_position, (1, 1))
        self.assertRaises(AssertionError, obj.set_position, {})
        self.assertRaises(AssertionError, obj.set_position, [])

    def test__classGameObject__fnSetPosition__setsPosition__ifCalledWithGoodArg(self):
        obj = self.MockGameObject()
        pos1 = obj.get_position()
        obj.set_position(PyVector2(0, 0))
        pos2 = obj.get_position()
        self.assertNotEquals(pos1, pos2)

    # fn get_rendering_offset ------------------------------------------------------------------------------------------

    def test__classGameObject__fnGetRenderingOffset__exists(self):
        obj = self.MockGameObject()
        self.assertIsNotNone(obj.get_rendering_offset)

    def test__classGameObject__fnGetRenderingOffset__returnsValueOfRenderingOffset(self):
        obj = self.MockGameObject()
        off1 = obj.get_rendering_offset()
        obj._rendering_offset = PyVector2(123, 456)
        off2 = obj.get_rendering_offset()
        self.assertIsNotNone(off1)
        self.assertIsNotNone(off2)
        self.assertNotEquals(off1, off2)

    # fn set_rendering_offset ------------------------------------------------------------------------------------------

    def test__classGameObject__fnSetRenderingOffset__exists(self):
        obj = self.MockGameObject()
        self.assertIsNotNone(obj.set_rendering_offset)

    def test__classGameObject__fnSetRenderingOffset__raisesAssertionError__ifCalledWithBadArgs(self):
        obj = self.MockGameObject()
        self.assertRaises(AssertionError, obj.set_rendering_offset, None)
        self.assertRaises(AssertionError, obj.set_rendering_offset, 1)
        self.assertRaises(AssertionError, obj.set_rendering_offset, (1, 1))
        self.assertRaises(AssertionError, obj.set_rendering_offset, {})
        self.assertRaises(AssertionError, obj.set_rendering_offset, [])

    def test__classGameObject__fnSetRenderingOffset__setsRenderingOffset__ifCalledWithGoodArgs(self):
        obj = self.MockGameObject()
        off1 = obj.get_rendering_offset()
        test_vec = PyVector2(123, 456)
        obj.set_rendering_offset(test_vec)
        off2 = obj.get_rendering_offset()
        self.assertIsNotNone(off1)
        self.assertIsNotNone(off2)
        self.assertNotEquals(off1, off2)
        self.assertEqual(off2, test_vec)

    # fn get_image -----------------------------------------------------------------------------------------------------

    def test__classGameObject__fnGetImage__exists(self):
        obj = self.MockGameObject()
        self.assertIsNotNone(obj.get_image)

    def test__classGameObject__fnGetImage__returnsImageValue(self):
        obj = self.MockGameObject()
        obj._image = 1
        self.assertEqual(obj.get_image(), 1)
        obj._image = 2
        self.assertEqual(obj.get_image(), 2)

    # fn set_image -----------------------------------------------------------------------------------------------------

    def test__classGameObject__fnSetImage__exists(self):
        obj = self.MockGameObject()
        self.assertIsNotNone(obj.set_image)

    def test__classGameObject__fnSetImage__raisesAssertionError__ifCalledWithBadArgs(self):
        obj = self.MockGameObject()
        self.assertRaises(AssertionError, obj.set_image, None)
        self.assertRaises(AssertionError, obj.set_image, 1)
        self.assertRaises(AssertionError, obj.set_image, (1, 1))
        self.assertRaises(AssertionError, obj.set_image, {})
        self.assertRaises(AssertionError, obj.set_image, [])

    def test__classGameObject__fnSetImage__updatesTheImage__ifCalledWithGoodArgs(self):
        pass

    # fn render --------------------------------------------------------------------------------------------------------

    def test__classGameObject__fnRender__exists(self):
        obj = self.MockGameObject()
        self.assertIsNotNone(obj.render)

    def get_render_args(self):
        """ returns a GameObject and RenderSurface, which will work with blit

            eg:  obj, surf = self.get_render_args()
                 obj.blit(surf)  <- would render
        """
        obj = self.MockGameObject()
        obj.set_image(pygame.surface.Surface((1, 1)))
        surf = pygame.surface.Surface((1, 1))
        return obj, surf

    def test__classGameObject__fnRender__returnsTrue__whenGivenTestArgs(self):
        # for this test to pass:
        #   _render_hidden = False
        #   render_to: PySurface
        #   _image: PySurface
        #   _position: PyVector2
        #   _rendering_offset: PyVector2

        obj, surf = self.get_render_args()
        self.assertTrue(obj.render(surf))

    # RenderHidden
    def test__classGameObject__fnRender__returnsFalse__ifRenderHiddenIsTrue(self):
        obj, surf = self.get_render_args()
        obj._render_hidden = True
        self.assertFalse(obj.render(surf))

    # RenderTo
    def test__classGameObject__fnRender__returnsFalse__ifRenderToSurf__isNone(self):
        obj, _ = self.get_render_args()
        self.assertFalse(obj.render(None))

    def test__classGameObject__fnRender__returnsFalse__ifRenderToSurf__isNotPySurface(self):
        obj, _ = self.get_render_args()
        self.assertFalse(obj.render(1))

    # Image
    def test__classGameObject__fnRender__returnsFalse__ifImage__isNone(self):
        obj, surf = self.get_render_args()
        obj._image = None
        self.assertFalse(obj.render(surf))

    def test__classGameObject__fnRender__returnsFalse__ifImage__isNotPySurface(self):
        obj, surf = self.get_render_args()
        obj._image = 1
        self.assertFalse(obj.render(surf))

    # Position
    def test__classGameObject__fnRender__returnsFalse__ifPosition__isNone(self):
        obj, surf = self.get_render_args()
        obj._position = None
        self.assertFalse(obj.render(surf))

    def test__classGameObject__fnRender__returnsFalse__ifPosition__isNotPyVector2(self):
        obj, surf = self.get_render_args()
        obj._position = 1
        self.assertFalse(obj.render(surf))

    # RenderingOffset
    def test__classGameObject__fnRender__returnsFalse__ifRenderingOffset__isNone(self):
        obj, surf = self.get_render_args()
        obj._rendering_offset = None
        self.assertFalse(obj.render(surf))

    def test__classGameObject__fnRender__returnsFalse__ifRenderingOffset__isNotPyVector2(self):
        obj, surf = self.get_render_args()
        obj._rendering_offset = 1
        self.assertFalse(obj.render(surf))

    # fn update --------------------------------------------------------------------------------------------------------

    def test__classGameObject__fnUpdate__exists(self):
        obj = self.MockGameObject()
        self.assertIsNotNone(obj.update)




if __name__ == '__main__':
    unittest.main()
