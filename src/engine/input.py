import dataclasses

import pygame
from pygame.key import ScancodeWrapper
from pygame.locals import *


class EngineInputMap:
    def __init__(self):
        # maps a key, to the one action
        self.key_to_action = {}

        # maps an action name to all the keys which can trigger it
        self.action_to_keys = {}

    def add_mapping(self, action: str, keys: list):
        if action is None or keys is None:
            return
        if action not in self.action_to_keys:
            self.action_to_keys[action] = keys
        for key in keys:
            if key not in self.key_to_action:
                self.key_to_action[key] = action

    def get_from_key(self, key):
        if key and key in self.key_to_action:
            return self.key_to_action[key]

    def get_from_action(self, action: str):
        if action and action in self.action_to_keys:
            return self.action_to_keys[action]

    def get_current_actions(self) -> list[str]:
        keys = self.key_to_action.keys()
        frame_input: ScancodeWrapper = pygame.key.get_pressed()

        action_list = []
        for key in keys:
            if frame_input[key]:
                action = self.key_to_action[key]
                if action not in action_list:
                    action_list.append(action)

        return action_list





class DefaultEngineInputMap(EngineInputMap):
    def __init__(self):
        super().__init__()

        self.add_mapping('move_up', [K_UP, K_w])
        self.add_mapping('move_down', [K_DOWN, K_s])

        self.add_mapping('move_left', [K_LEFT, K_a])
        self.add_mapping('move_right', [K_RIGHT, K_d])

        self.add_mapping('return', [K_RETURN])
        self.add_mapping('escape', [K_ESCAPE])

# todo: make a way to build this from JSON


class EngineInput:
    def __init__(self, engine):
        self.engine = engine
        self._actions_last_frame = None
        self._actions_this_frame = None

        self.input_mapping = DefaultEngineInputMap()

    def collect_user_actions(self):
        self._actions_last_frame = self._actions_this_frame
        self._actions_this_frame = self.input_mapping.get_current_actions()

    def action_is_starting(self, action: str) -> bool:
        # if it's happening this frame, and was NOT last frame, then it's starting
        if action and action in self._actions_this_frame and not action in self._actions_last_frame:
            return True
        return False

    def action_is_held(self, action: str) -> bool:
        # if it's happening this frame, and was also happening last frame
        if action and action in self._actions_last_frame and action in self._actions_this_frame:
            return True
        return False

    def action_is_stopping(self, action: str) -> bool:
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
    name: str
    is_starting: bool
    is_held: bool
    is_stopping: bool

