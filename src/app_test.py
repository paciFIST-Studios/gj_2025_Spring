import os.path
import unittest

from app import rename_with_timestamp

"""
Note:

    In order to discover all of the tests in one place, and run only a single configuration,
    we need to specify all of the test case classes here.  Thanks!

"""


# engine tests
from src.engine.animation_test import AnimationTestCases
from src.engine.cache_test import CacheTestCases
from src.engine.input_test import InputTestCases
from src.engine.resource_test import ResourceTestCases
from src.engine.time_utility_test import TimeTestCases
from src.engine.utilities_test import UtilitiesTestCases

# game tests
from src.gembo.update_modes._update_mode_test import UpdateModeTestCases
from src.gembo.game_data_test import GameDataTestCases
from src.gembo.gameplay.game_object_test import GameObjectTestCases
from src.gembo.gameplay.cactus_test import CactusTestCases

# profiler tests -------------------------------------------------------------------------------------------------------

class ProfilerTestCases(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def create_test_file(self, path):
        with open(path, 'w'):
            pass

    def assertCreateFile(self, path):
        self.create_test_file(path)
        self.assertTrue(os.path.isfile(path))

    def assertFileRemoved(self, path):
        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                os.rmdir(path)
        self.assertFalse(os.path.exists(path))

    def test_framework_can_pass_a_test(self):
        self.assertTrue(True)

    def test__fnRenameWithTimestamp__exists(self):
        self.assertIsNotNone(rename_with_timestamp)

    def test__fnRenameWithTimestamp__returnsFalse__forBadPath(self):
        self.assertFalse(rename_with_timestamp('asd'))

    def test__fnRenameWithTimestamp__returnsFalse__forDirectoryPath(self):
        self.assertFalse(rename_with_timestamp('docs'))

    def test__fnRenameWithTimestamp__returnsTrue__ifRenameWasSuccessful(self):
        file_path = 'deleteme.plz'
        self.assertCreateFile(file_path)

        renamed = rename_with_timestamp(file_path)
        self.assertIsNotNone(renamed)
        self.assertTrue(os.path.isfile(renamed))
        self.assertFalse(os.path.isfile(file_path))

        self.assertFileRemoved(renamed)



if __name__ == '__main__':
    unittest.main()
