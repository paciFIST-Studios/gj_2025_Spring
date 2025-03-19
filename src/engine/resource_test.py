import unittest

import json
import os

from src.engine.resource import IMAGES_TO_LOAD, AUDIO_TO_LOAD, FONTS_TO_LOAD

from src.engine.resource import (load_text_file, load_json, load_font, load_image, load_sound)
from src.engine.resource import write_text_file, write_json


class ResourceTestCases(unittest.TestCase):

    # test utilities ---------------------------------------------------------------------------------------------------

    @staticmethod
    def get_json_test_object():
        return {
            'key-name': 'key-value',
            'key-with-array': [ 0, 1, 2, 3],
            'key-with-dict': {
                'sub-key': 'sub-key-value'
            }
        }

    @staticmethod
    def get_invalid_json():
        return r'{"key-name": "key-value", "key-with-array": [0, 1, 2, 3], "key-with-dict": {"sub-key": "sub-key-value"}'

    def assertRemoveFile(self, path: str):
        if os.path.exists(path):
            os.remove(path)
            self.assertFalse(os.path.exists(path))

    def setUp(self):
        self.test_file_path = 'deleteme.file'
        self.assertRemoveFile(self.test_file_path)

    def tearDown(self):
        self.assertRemoveFile(self.test_file_path)


    # framework test ---------------------------------------------------------------------------------------------------

    def test_framework_can_pass_a_test(self):
        self.assertTrue(True)


    # load lists -------------------------------------------------------------------------------------------------------

    def test__globalImagesToLoad__Exists(self):
        self.assertIsNotNone(IMAGES_TO_LOAD)

    def test__globalImagesToLoad__isExpectedSize(self):
        self.assertEqual(len(IMAGES_TO_LOAD), 27)

    def test__globalAudioToLoad__Exists(self):
        self.assertIsNotNone(AUDIO_TO_LOAD)

    def test__globalAudioToLoad__isExpectedSize(self):
        self.assertEqual(len(AUDIO_TO_LOAD), 7)

    def test__globalFontsToLoad__Exists(self):
        self.assertIsNotNone(FONTS_TO_LOAD)

    def test__globalFontsToLoad__isExpectedSize(self):
        self.assertEqual(len(FONTS_TO_LOAD), 7)


    #-------------------------------------------------------------------------------------------------------------------
    # test loaders
    #-------------------------------------------------------------------------------------------------------------------

    # fn load_test_file ------------------------------------------------------------------------------------------------

    def test__fnLoadTextFile__exists(self):
        self.assertIsNotNone(load_text_file)

    def test__fnLoadTextFile__returnsNone__forInvalidFilePath(self):
        self.assertIsNone(load_text_file('dsasasdsadsa'))

    def test__fnLoadTextFile__returnsText__forLoadableTextFile(self):
        contents = 'deleteme'
        with open(self.test_file_path, 'w') as outfile:
            outfile.write(contents)

        self.assertTrue(os.path.isfile(self.test_file_path))

        data = load_text_file(self.test_file_path)
        self.assertIsNotNone(data)
        self.assertTrue(isinstance(data, str))
        self.assertEqual(contents, data)

    # fn load_json -----------------------------------------------------------------------------------------------------

    def test__fnLoadJson__exists(self):
        self.assertIsNotNone(load_json)

    def test__fnLoadJson__returnsNone__forInvalidPath(self):
        self.assertIsNone(load_json('asdasdad'))

    def test__fnLoadJson__returnsJsonObject__forJsonFile(self):
        data = self.get_json_test_object()

        with open(self.test_file_path, 'w') as outfile:
            outfile.write(json.dumps(data))

        self.assertTrue(os.path.isfile(self.test_file_path))

        result = load_json(self.test_file_path)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(len(result.keys()), 3)


    def test__fnLoadJson__throwsException__forInvalidJsonInFile(self):
        with open(self.test_file_path, 'w') as outfile:
            outfile.write(self.get_invalid_json())

        self.assertTrue(os.path.isfile(self.test_file_path))

        # we can load something from this file as a text file
        self.assertIsNotNone(load_text_file(self.test_file_path))

        try:
            load_json(self.test_file_path)
            self.assertTrue(False)
        except json.decoder.JSONDecodeError as err:
            # the json is invalid, so it's meant to throw a json exception
            self.assertTrue(True)

        self.assertRemoveFile(self.test_file_path)


    # fn write_text_file -----------------------------------------------------------------------------------------------

    def test__fnWriteTextFile__exists(self):
        self.assertIsNotNone(write_text_file)

    def test__fnWriteTextFile__returnsTrue__ifWriteSucceeds(self):
        self.assertTrue(write_text_file(self.test_file_path, 'deleteme'))
        self.assertTrue(os.path.isfile(self.test_file_path))


    # fn write_json ----------------------------------------------------------------------------------------------------

    def test__fnWriteJson__exists(self):
        self.assertIsNotNone(write_json)

    def test__fnWriteJson__returnsTrue__ifWriteSucceeds(self):
        self.assertTrue(write_json(self.test_file_path, self.get_json_test_object()))
        self.assertTrue(os.path.isfile(self.test_file_path))

    # fn load_image ----------------------------------------------------------------------------------------------------

    def test__fnLoadImage__exists(self):
        self.assertIsNotNone(load_image)

    def test__fnLoadImage__returnsNone__forInvalidPath(self):
        self.assertIsNone(load_image('saddadsa'))

    # fn load_sound ----------------------------------------------------------------------------------------------------

    def test__fnLoadSound__exists(self):
        self.assertIsNotNone(load_sound)

    def test__fnLoadSound__returnsNone__forInvalidPath(self):
        self.assertIsNone(load_sound('asddadsa'))

    # fn load_font -----------------------------------------------------------------------------------------------------

    def test__fnLoadFont__exists(self):
        self.assertIsNotNone(load_font)

    def test__fnLoadFont__returnsNone__forInvalidPath(self):
        self.assertIsNone(load_font('asdsada', 10))


if __name__ == '__main__':
    unittest.main()
