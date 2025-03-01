import unittest

from resource import IMAGES_TO_LOAD, AUDIO_TO_LOAD, FONTS_TO_LOAD


class ResourceTestCases(unittest.TestCase):
    def test_framework_can_pass_a_test(self):
        self.assertTrue(True)


    # load lists -------------------------------------------------------------------------------------------------------

    def test__globalImagesToLoad__Exists(self):
        self.assertIsNotNone(IMAGES_TO_LOAD)

    def test__globalImagesToLoad__isExpectedSize(self):
        self.assertEqual(len(IMAGES_TO_LOAD), 22)

    def test__globalAudioToLoad__Exists(self):
        self.assertIsNotNone(AUDIO_TO_LOAD)

    def test__globalAudioToLoad__isExpectedSize(self):
        self.assertEqual(len(AUDIO_TO_LOAD), 6)

    def test__globalFontsToLoad__Exists(self):
        self.assertIsNotNone(FONTS_TO_LOAD)

    def test__globalFontsToLoad__isExpectedSize(self):
        self.assertEqual(len(FONTS_TO_LOAD), 7)

    # todo test loaders



if __name__ == '__main__':
    unittest.main()
