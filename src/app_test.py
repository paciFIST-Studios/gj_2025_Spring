import unittest

"""
Note:

    In order to discover all of the tests in one place, and run only a single configuration,
    we need to specify all of the test case classes here.  Thanks!

"""


# engine tests
from src.engine.animation_test import AnimationTestCases
from src.engine.input_test import InputTestCases
from src.engine.resource_test import ResourceTestCases
from src.engine.time_utility_test import TimeTestCases
from src.engine.utilities_test import UtilitiesTestCases

# game tests
from src.gembo.game_data_test import GameDataTestCases
from src.gembo.gameplay.module_test import GameModeTestCases


if __name__ == '__main__':
    unittest.main()
