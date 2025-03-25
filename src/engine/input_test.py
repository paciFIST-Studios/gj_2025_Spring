import unittest
from src.test import AbstractTestBase as TestCase

import os.path


from src.engine.input import EngineInput, DefaultEngineInputMap, EngineInputMap, JsonEngineInputMap
from src.engine.resource import load_json, write_json


class InputTestCases(TestCase):

    def setUp(self):
        self.test_file_path = 'deleteme.file'
        if os.path.exists(self.test_file_path):
            self.assertRemoveFile(self.test_file_path)

    def tearDown(self):
        if os.path.exists(self.test_file_path):
            self.assertRemoveFile(self.test_file_path)


    # NOTE: moved to src.test.__init__ as of 20250324 -- Ellie
    #
    # def assertRemoveFile(self, path: str):
    #     if os.path.exists(path):
    #         os.remove(path)
    #         self.assertFalse(os.path.exists(path))

    @staticmethod
    def get_valid_input_mapping():
        return {
            'version': {
                'major': EngineInputMap.INPUT_MAP_VERSION_MAJOR,
                'minor': EngineInputMap.INPUT_MAP_VERSION_MINOR
            },
            'mappings': {
                'return': [13]
            }
        }


    def test_framework_can_pass_a_test(self):
        self.assertTrue(True)

    #-------------------------------------------------------------------------------------------------------------------
    # EngineInputMap
    #-------------------------------------------------------------------------------------------------------------------

    def test__classEngineInputMap__canConstruct(self):
        self.assertIsNotNone(EngineInputMap())

    def test__classEngineInputMap__ContainsCorrectMemberProperties(self):
        eim = EngineInputMap()
        self.assertTrue(hasattr(eim, 'key_to_action'))
        self.assertTrue(isinstance(eim.key_to_action, dict))
        self.assertTrue(hasattr(eim, 'action_to_keys'))
        self.assertTrue(isinstance(eim.action_to_keys, dict))

    # fn add_mapping ---------------------------------------------------------------------------------------------------

    def test__classEngineInputMap__fnAddMapping__exists(self):
        self.assertIsNotNone(EngineInputMap.add_mapping)

    def test__classEngineInputMap__fnAddMapping__doesNothingForNullArgs(self):
        eim = EngineInputMap()
        self.assertEqual(len(eim.key_to_action), 0)
        self.assertEqual(len(eim.action_to_keys), 0)

        eim.add_mapping(None, ['K_w', 'K_UP'])

        self.assertEqual(len(eim.key_to_action), 0)
        self.assertEqual(len(eim.action_to_keys), 0)

        eim.add_mapping('walk_up', None)

        self.assertEqual(len(eim.key_to_action), 0)
        self.assertEqual(len(eim.action_to_keys), 0)

    def test__classEngineInputMap__fnAddMapping__addsToBackingData__for_validArgs(self):
        eim = EngineInputMap()
        self.assertEqual(len(eim.key_to_action), 0)
        self.assertEqual(len(eim.action_to_keys), 0)

        eim.add_mapping('walk_up', ['K_w', 'K_UP'])
        self.assertEqual(len(eim.key_to_action), 2)
        self.assertEqual(len(eim.action_to_keys), 1)

    # fn get_from_key --------------------------------------------------------------------------------------------------

    def test__classEngineInputMap__fnGetFromKey__exists(self):
        self.assertIsNotNone(EngineInputMap.get_from_key)

    def test__classEngineInputMap__fnGetFromKey__returnsNone__forNoKeyFound(self):
        # returns none if there are no keys
        self.assertIsNone(EngineInputMap().get_from_key('key'))

        # returns non if there are keys, but no valid key was used
        eim = EngineInputMap()
        eim.add_mapping('walk_up', ['K_w', 'K_UP'])
        self.assertIsNone(eim.get_from_key('key'))

    # fn get_from_action -----------------------------------------------------------------------------------------------

    def test__classEngineInput__fnGetFromAction__exists(self):
        self.assertIsNotNone(EngineInputMap.get_from_action)

    def test__classEngineInputMap__fnGetFromAction__returnsActionMapping__forValidKey(self):
        eim = EngineInputMap()
        eim.add_mapping('walk_up', ['K_w', 'K_UP'])

        action = eim.get_from_key('K_w')
        self.assertIsNotNone(action)
        self.assertTrue(isinstance(action, str))
        self.assertEqual(action, 'walk_up')

    def test__classEngineInputMap__fnGetFromAction__returnsNone__forActionNotFound(self):
        # returns none if there are no actions
        self.assertIsNone(EngineInputMap().get_from_action('action'))

        # returns none if there are actions, but no valid action was used
        eim = EngineInputMap()
        eim.add_mapping('walk_up', ['K_w', 'K_UP'])
        self.assertIsNone(eim.get_from_action('action'))

    # fn get_current_actions -------------------------------------------------------------------------------------------

    def test__classEngineInputMap__fnGetCurrentActions__exists(self):
        self.assertIsNotNone(EngineInputMap.get_current_actions)

    # fn get_mappings --------------------------------------------------------------------------------------------------

    def test__classEngineInputMap__fnGetMappings__exists(self):
        self.assertIsNotNone(EngineInputMap.get_mappings)

    def test__classEngineInputMap__fnGetMappings__returnsDict(self):
        self.assertTrue(isinstance(EngineInputMap().get_mappings(), dict))

    def test__classEngineInputMap__fnGetMappings__returnsEmptyDict__ForNoMappings(self):
        self.assertEqual(EngineInputMap().get_mappings(), {})

    # fn export_mapping_to_json ----------------------------------------------------------------------------------------

    def test__classEngineInputMap__fnExportMappingToJson__exists(self):
        self.assertIsNotNone(EngineInputMap.export_mapping_to_json)

    def test__classEngineInputMap__fnExportMappingToJson__createsJsonFileAtCorrectPath(self):
        DefaultEngineInputMap().export_mapping_to_json(self.test_file_path)
        self.assertTrue(os.path.isfile(self.test_file_path))

    def test__classEngineInputMap__fnExportMappingToJson__createsJsonWithCorrectMajorMinorVersion(self):
        DefaultEngineInputMap().export_mapping_to_json(self.test_file_path)
        self.assertTrue(os.path.isfile(self.test_file_path))

        mapping = load_json(self.test_file_path)
        self.assertIsNotNone(mapping)
        self.assertTrue('version' in mapping)
        self.assertEqual(mapping['version']['major'], EngineInputMap.INPUT_MAP_VERSION_MAJOR)
        self.assertEqual(mapping['version']['minor'], EngineInputMap.INPUT_MAP_VERSION_MINOR)

    def test__classEngineInputMap__fnExportMappingToJson__createsIntactJsonMapping(self):
        DefaultEngineInputMap().export_mapping_to_json(self.test_file_path)
        self.assertTrue(os.path.isfile(self.test_file_path))

        mapping = load_json(self.test_file_path)
        self.assertIsNotNone(mapping)
        self.assertTrue('version' in mapping)
        self.assertTrue('mappings' in mapping)

        mapping_dict = mapping['mappings']
        mapping_keys = mapping_dict.keys()

        for action in mapping_keys:
            key = mapping_dict[action]
            self.assertIsNotNone(key)
            self.assertTrue(isinstance(key, list))
            self.assertTrue(len(key) > 0)

    #-------------------------------------------------------------------------------------------------------------------
    # DefaultEngineInputMap
    #-------------------------------------------------------------------------------------------------------------------

    def test__classDefaultEngineInputMap__canConstruct__withExpectedValues(self):
        deim = DefaultEngineInputMap()
        self.assertIsNotNone(deim)
        self.assertEqual(len(deim.action_to_keys), 6)
        self.assertEqual(len(deim.key_to_action), 10)

        self.assertTrue('move_up' in deim.action_to_keys.keys())
        self.assertTrue('move_down' in deim.action_to_keys.keys())
        self.assertTrue('move_left' in deim.action_to_keys.keys())
        self.assertTrue('move_right' in deim.action_to_keys.keys())
        self.assertTrue('return' in deim.action_to_keys.keys())
        self.assertTrue('escape' in deim.action_to_keys.keys())

    #-------------------------------------------------------------------------------------------------------------------
    # JsonEngineInputMap
    #-------------------------------------------------------------------------------------------------------------------

    def test__classJsonEngineInputMap__canConstruct__withNoneArgument(self):
        self.assertIsNotNone(JsonEngineInputMap(None))

    def test__classJsonEngineInputMap__hasNoDefaultMappings__whenConstructedWithNoneArgument(self):
        jeim = JsonEngineInputMap(None)
        self.assertEqual(len(jeim.action_to_keys), 0)
        self.assertEqual(len(jeim.key_to_action), 0)

    def test__classJsonEngineInputMap__canLoadValidMapping__fromValidFile(self):
        write_json(self.test_file_path, self.get_valid_input_mapping())
        self.assertTrue(os.path.isfile(self.test_file_path))

        jeim = JsonEngineInputMap(path=self.test_file_path)
        self.assertEqual(len(jeim.action_to_keys.keys()), 1)
        self.assertEqual(len(jeim.key_to_action.keys()), 1)


if __name__ == '__main__':
    unittest.main()
