import unittest

from math import pi as PI

import pygame.surface

from src.gembo.renderer.render_mode import get_scaled_sin, render_breathe_box
from src.gembo.renderer.render_mode import AbstractRenderMode

from src.engine.ui import Padding, EColor

class RenderModesTestCases(unittest.TestCase):

    # test utilities ---------------------------------------------------------------------------------------------------



    # framework --------------------------------------------------------------------------------------------------------

    def test_framework_cn_pass_a_test(self):
        self.assertTrue(True)


    # fn get_scaled_sin ------------------------------------------------------------------------------------------------

    def test__fnGetScaledSin__exists(self):
        self.assertIsNotNone(get_scaled_sin)

    def test__fnGetScaledSin__returnsNone__forBadArgument(self):
        self.assertIsNone(get_scaled_sin({}))
        self.assertIsNone(get_scaled_sin([]))
        self.assertIsNone(get_scaled_sin(None))
        self.assertIsNone(get_scaled_sin('1'))


    def test__fnGetScaledSin__returnsFloat__forValidArgument(self):
        self.assertTrue(isinstance(get_scaled_sin(1), float))

    def test__fnGetScaledSin__hasCorrectExtents(self):
        self.assertEqual(get_scaled_sin(-PI/2), 0)
        self.assertEqual(get_scaled_sin(0), 0.5)
        self.assertEqual(get_scaled_sin(PI/2), 1)

    # fn render_breathe_box --------------------------------------------------------------------------------------------

    def test__fnRenderBreathBox__exists(self):
        self.assertIsNotNone(render_breathe_box)

    @staticmethod
    def get_render_breathe_box_args():
        return pygame.surface.Surface((1, 1)), Padding(1, 1, 1, 1), EColor.COOL_GREY, 1, True, 20.0

    def test__fnRenderBreatheBox__returnsFalse__forInvalidSurfaceArg(self):
        surface, padding, color, width, is_animated, ratio = self.get_render_breathe_box_args()
        self.assertFalse(render_breathe_box(None, padding, color, width, is_animated, ratio))
        self.assertFalse(render_breathe_box({}, padding, color, width, is_animated, ratio))

    def test__fnRenderBreatheBox__returnsFalse__forInvalidPaddingArg(self):
        surface, padding, color, width, is_animated, ratio = self.get_render_breathe_box_args()
        self.assertFalse(render_breathe_box(surface, None, color, width, is_animated, ratio))
        self.assertFalse(render_breathe_box(surface, {}, color, width, is_animated, ratio))

    def test__fnRenderBreatheBox__returnsFalse__forInvalidColorArg(self):
        surface, padding, color, width, is_animated, ratio = self.get_render_breathe_box_args()
        self.assertFalse(render_breathe_box(surface, padding, None, width, is_animated, ratio))
        self.assertFalse(render_breathe_box(surface, padding, {}, width, is_animated, ratio))

    def test__fnRenderBreatheBox__returnsFalse__forInvalidWidthArg(self):
        surface, padding, color, width, is_animated, ratio = self.get_render_breathe_box_args()
        self.assertFalse(render_breathe_box(surface, padding, color, None, is_animated, ratio))
        self.assertFalse(render_breathe_box(surface, padding, color, {}, is_animated, ratio))

    def test__fnRenderBreatheBox__returnsFalse__forInvalidIsAnimatedArg(self):
        surface, padding, color, width, is_animated, ratio = self.get_render_breathe_box_args()
        self.assertFalse(render_breathe_box(surface, padding, color, width, None, ratio))
        self.assertFalse(render_breathe_box(surface, padding, color, width, {}, ratio))

    def test__fnRenderBreatheBox__returnsFalse__forInvalidRatioArg(self):
        surface, padding, color, width, is_animated, ratio = self.get_render_breathe_box_args()
        self.assertFalse(render_breathe_box(surface, padding, color, width, is_animated, None))
        self.assertFalse(render_breathe_box(surface, padding, color, width, is_animated, {}))

    def test__fnRenderBreatheBox__returnsTrue__ifItFinishes(self):
        surface, padding, color, width, is_animated, ratio = self.get_render_breathe_box_args()
        self.assertTrue(render_breathe_box(surface, padding, color, width, is_animated, ratio))


    # class AbstractRenderMode -------------------------------------------------------------------------------------------------

    def test__classAbstractRenderMode__exists(self):
        self.assertIsNotNone(AbstractRenderMode)

    def test__classAbstractRenderMode__(self):




if __name__ == '__main__':
    unittest.main()
