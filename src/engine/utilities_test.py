import random
import unittest

from src.engine.utilities import is_numerical, clamp


class UtilitiesTestCases(unittest.TestCase):
    def test_framework_can_pass_a_test(self):
        self.assertTrue(True)


    # fn is_numerical -> bool ------------------------------------------------------------------------------------------

    def test__fnIsNumerical__returnsTrue__forInt(self):
        self.assertTrue(is_numerical(int(0)))

    def test__fnIsNumerical__returnsTrue__forFloat(self):
        self.assertTrue(is_numerical(0.0))

    def test__fnIsNumerical__returnsFalse__forString(self):
        self.assertFalse(is_numerical('1'))

    def test__fnIsNumerical__returnsFalse__forList(self):
        self.assertFalse(is_numerical([]))

    def test__fnIsNumerical__returnsFalse__forDict(self):
        self.assertFalse(is_numerical({}))

    def test__fnIsNumerical__returnsFalse__forNone(self):
        self.assertFalse(is_numerical(None))

    # fn clamp -> bool -------------------------------------------------------------------------------------------------

    def test__fnClamp__returnsNone__forNonNumericalValue(self):
        self.assertIsNone(clamp(None, 0,1))
        self.assertIsNone(clamp(1, None,1))
        self.assertIsNone(clamp(1, 0,None))

    def test__fnClamp__returnsMin__forValueLowerThanMin(self):
        value, min, max = -1, 0, 1
        self.assertEqual(clamp(value, min, max), min)

    def test__fnClamp__returnsMax__forValueGreaterThanMax(self):
        value, min, max = 2, 0, 1
        self.assertEqual(clamp(value, min, max), max)

    def test__fnClamp__returnsValue__forValueInRange(self):
        value, min, max = random.random(), 0, 1
        self.assertEqual(clamp(value, min, max), value)



if __name__ == '__main__':
    unittest.main()
