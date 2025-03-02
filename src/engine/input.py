import dataclasses
import os.path

import pygame
from pygame.key import ScancodeWrapper
from pygame.locals import *

from src.engine.resource import load_json, write_json


class EngineInputMap:
    INPUT_MAP_VERSION_MAJOR: int = 0
    INPUT_MAP_VERSION_MINOR: int = 1

    def __init__(self):
        # maps a key, to the one action
        self.key_to_action = {}

        # maps an action name to all the keys which can trigger it
        self.action_to_keys = {}

    def add_mapping(self, action: str, keys: list):
        """ Adds the following action and its associated physical keys, as long as they are not already present """
        if action is None or keys is None:
            return
        if action not in self.action_to_keys:
            self.action_to_keys[action] = keys
        for key in keys:
            if key not in self.key_to_action:
                self.key_to_action[key] = action

    def get_from_key(self, key):
        """ returns the action associated with a key """
        if key and key in self.key_to_action:
            return self.key_to_action[key]

    def get_from_action(self, action: str):
        """ returns the keys associated with an action """
        if action and action in self.action_to_keys:
            return self.action_to_keys[action]

    def get_current_actions(self) -> list[str]:
        """ returns a lit of actions (user inputs) which are occurring right now """
        keys = self.key_to_action.keys()
        frame_input: ScancodeWrapper = pygame.key.get_pressed()

        action_list = []
        for key in keys:
            if frame_input[key]:
                action = self.key_to_action[key]
                if action not in action_list:
                    action_list.append(action)

        return action_list


    def get_mappings(self) -> dict:
        """ Returns a dictionary of input mappings

        Returns:
            mappings(dict) - a dictionary of input mappings, where actions are the keys,
            and the ID of the physical control input(s) is(are) the value
        """
        action_keys = self.action_to_keys.keys()
        mappings = {}
        for action in action_keys:
            keys = self.action_to_keys[action]
            mappings[action] = keys
        return mappings

    def export_mapping_to_json(self, path: str) -> bool:
        """ Saves the current mapping information to disk, as a json file.
        Major and Minor version numbers are affixed to the save file during this process.

        Args:
            path(str) - the path on disk, for saving the map file

        Returns:
            was_successful(bool)
        """
        mappings = self.get_mappings()
        export = {
            'version': {
                'major': self.INPUT_MAP_VERSION_MAJOR,
                'minor': self.INPUT_MAP_VERSION_MINOR
            },
            'mappings': mappings
        }
        return write_json(path, export)

class DefaultEngineInputMap(EngineInputMap):
    def __init__(self):
        super().__init__()

        self.add_mapping('move_up', [K_UP, K_w])
        self.add_mapping('move_down', [K_DOWN, K_s])

        self.add_mapping('move_left', [K_LEFT, K_a])
        self.add_mapping('move_right', [K_RIGHT, K_d])

        self.add_mapping('return', [K_RETURN])
        self.add_mapping('escape', [K_ESCAPE])


class JsonEngineInputMap(EngineInputMap):
    def __init__(self, path: str):
        super().__init__()
        self.path = path
        self.make_from_json()

    def make_from_json(self):
        """ Loads a json mapping file, and then adds those mappings for use """
        if self.path and os.path.isfile(self.path):
            obj = load_json(self.path)
            if 'mappings' in obj:
                for action in obj['mappings'].keys():
                    self.add_mapping(action, obj['mappings'][action])


class EngineInput:
    def __init__(self, engine, json_mapping_path: str = None):
        self.engine = engine
        self._actions_last_frame = None
        self._actions_this_frame = None

        if json_mapping_path and os.path.isfile(json_mapping_path):
            self.input_mapping = JsonEngineInputMap(json_mapping_path)
            self.loaded_input_mapping_path: str = json_mapping_path
        else:
            self.input_mapping = DefaultEngineInputMap()

    def collect_user_actions(self):
        """ This fn is called to update the user input """
        self._actions_last_frame = self._actions_this_frame
        self._actions_this_frame = self.input_mapping.get_current_actions()

    def action_is_starting(self, action: str) -> bool:
        """ returns true, if an action was NOT happening last frame, but is happening this frame """
        # if it's happening this frame, and was NOT last frame, then it's starting
        if action and action in self._actions_this_frame and not action in self._actions_last_frame:
            return True
        return False

    def action_is_held(self, action: str) -> bool:
        """ returns true, if an action was happening last frame, and is still happening this frame """
        # if it's happening this frame, and was also happening last frame
        if action and action in self._actions_last_frame and action in self._actions_this_frame:
            return True
        return False

    def action_is_stopping(self, action: str) -> bool:
        """ returns true, if an action was happening last frame, and is NOW happening this frame """
        # if it's NOT happening this frame, but was happening last frame
        if action and action in self._actions_last_frame and action not in self._actions_this_frame:
            return True
        return False

    def get_actions_this_frame(self):
        """
        Returns:
            tuple([actions: str], [starting: bool], [held: bool], [stopping: bool])

            returns a tuple of arrays, where each array holds different information about the actions
            being used this frame.
        """
        results = []
        for action in self._actions_this_frame:
            results.append(
                GameplayAction(action,
                               self.action_is_starting(action),
                               self.action_is_held(action),
                               self.action_is_stopping(action)))
        return results

@dataclasses.dataclass
class GameplayAction:
    """ exists to easily pass along the action, and 'state' of invoking that action """
    name: str
    is_starting: bool
    is_held: bool
    is_stopping: bool

