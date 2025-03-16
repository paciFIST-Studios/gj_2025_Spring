import abc
from abc import ABC

from enum import Enum, auto

class EUpdateMode(Enum):
    """ The EUpdateMode enum shows which update-modes exist in the game.  UpdateModes handle a simulation, which needs
    to evolve over time, and each UpdateMode will have an associated Update fn.

        UNINIT - exists to show the game is not finishing being initialized
        UPDATE_DEMO - this is the main menu, but it also functions as the tutorial, and it plays itself some
        UPDATE_GAMEPLAY - where the "game" lives
        UPDATE_MENU - manages access to other modes
        UPDATE_SETTINGS - manages changes to internal settings like: volume, muting, etc
        UPDATE_STATS - calculates stats such as, longest streak, and times a streak has been reached
        UPDATE_ABOUT - manages an about page for the game
        INVOKE_EXIT - exits the application
    """
    UNINIT = auto(), 'uninit'
    UPDATE_DEMO = auto(), 'demo'
    UPDATE_GAMEPLAY = auto(), 'gameplay'
    UPDATE_MENU = auto(), 'menu'
    UPDATE_SETTINGS = auto(), 'settings'
    UPDATE_STATISTICS = auto(), 'stats'
    UPDATE_ABOUT = auto(), 'about'
    INVOKE_EXIT = auto(), 'exit'


class UpdateModeBase(ABC):
    """

    """
    def __init__(self, engine, game_mode_data: dict):
        self.engine = engine
        self.update_mode_data = game_mode_data

    def value_or_default(self, key, default = None):
        if key and key in self.update_mode_data:
            return self.update_mode_data[key]
        return default

    @abc.abstractmethod
    def update(self, delta_time_s: float, actions_this_frame: list):
        """ all game modes need to override this fn with their own version """
        pass


class UpdateModeManager:
    """ the UpdateModeManager class is used to represent information about the current game mode, as well
    as some "housekeeping" fns around changing game modes.
    """

    def __init__(self):
        self.current: EUpdateMode = EUpdateMode.UNINIT
        self.previous: EUpdateMode = EUpdateMode.UNINIT

        # after a game mode changes, every fn in the callables dict is called,
        # if it is in the array pertaining to that game mode
        self.on_mode_changed_callables = {}

        self.game_modes = {}

        # subscriber-lists
        for mode in EUpdateMode:
            if mode != EUpdateMode.UNINIT:
                if mode not in self.on_mode_changed_callables:
                    self.on_mode_changed_callables[mode] = []


    def print_current_game_mode(self):
        print(f'update mode: {self.current}')

    def is_callable_registered(self, mode: EUpdateMode, fn: callable):
        if mode is None or not mode or fn is None or not fn:
            return None
        elif mode not in self.on_mode_changed_callables:
            return False
        elif fn not in self.on_mode_changed_callables:
            return False
        return True

    def get_current(self) -> UpdateModeBase:
        if self.current in self.game_modes:
            return self.game_modes.get(self.current)


    def get_callables_of_mode(self, mode: EUpdateMode):
        if mode is None:
            return None
        if mode not in self.on_mode_changed_callables:
            return None
        return self.on_mode_changed_callables[mode]

    def register_callable(self, mode: EUpdateMode, fn: callable) -> bool:
        # this fn also handles null checks
        if self.is_callable_registered(mode, fn):
            return True

        if not mode in self.on_mode_changed_callables:
            self.on_mode_changed_callables[mode] = []

        if fn not in self.on_mode_changed_callables[mode]:
            self.on_mode_changed_callables[mode].append(fn)

        return True

    def unregister_callable(self, mode: EUpdateMode, fn: callable) -> bool:
        if mode is not None and fn is not None:
            if mode in self.on_mode_changed_callables:
                if fn in self.on_mode_changed_callables[mode]:
                    index = self.on_mode_changed_callables[mode].index(fn)
                    self.on_mode_changed_callables[mode].pop(index)
                    return True
        return False

    def run_callables_for_mode(self, mode: EUpdateMode):
        assert mode in self.on_mode_changed_callables
        fns = self.on_mode_changed_callables[mode]
        for fn in fns:
            fn()

    def is_mode_registered(self, mode_enum: EUpdateMode, mode_class: UpdateModeBase) -> bool:
        if mode_enum is None or not mode_enum or mode_class is None or not mode_class:
            return None
        elif mode_enum not in self.game_modes:
            return False
        elif mode_class != self.game_modes[mode_enum]:
            return False
        return True

    def register_mode(self, mode_enum: EUpdateMode, mode_class: UpdateModeBase) -> bool:
        if self.is_mode_registered(mode_enum, mode_class):
            return True

        if mode_enum not in self.game_modes:
            self.game_modes[mode_enum] = []

        if mode_class not in self.game_modes[mode_enum]:
            self.game_modes[mode_enum] = mode_class

        return True

    def unregister_mode(self, mode_enum: EUpdateMode, mode_class: UpdateModeBase):
        if mode_enum is not None and mode_class is not None:
            if mode_enum in self.game_modes:
                if mode_class == self.game_modes[mode_enum]:
                    _ = self.game_modes.pop(mode_enum)
                    return True
        return False



    def set_mode__demo(self):
        self.previous = self.current
        self.current = EUpdateMode.UPDATE_DEMO
        self.run_callables_for_mode(self.current)

    def set_mode__gameplay(self):
        self.previous = self.current
        self.current = EUpdateMode.UPDATE_GAMEPLAY
        self.run_callables_for_mode(self.current)

    def set_mode__menu(self):
        self.previous = self.current
        self.current = EUpdateMode.UPDATE_MENU
        self.run_callables_for_mode(self.current)

    def set_mode__settings(self):
        self.previous = self.current
        self.current = EUpdateMode.UPDATE_SETTINGS
        self.run_callables_for_mode(self.current)

    def set_mode__stats(self):
        self.previous = self.current
        self.current = EUpdateMode.UPDATE_STATISTICS
        self.run_callables_for_mode(self.current)

    def set_mode__about(self):
        self.previous = self.current
        self.current = EUpdateMode.UPDATE_ABOUT
        self.run_callables_for_mode(self.current)

    def set_mode__exit(self):
        self.previous = self.current
        self.current = EUpdateMode.INVOKE_EXIT
        self.run_callables_for_mode(self.current)

    def set_mode(self, mode: EUpdateMode):
        if mode == EUpdateMode.UPDATE_DEMO:
            self.set_mode__demo()
        elif mode == EUpdateMode.UPDATE_GAMEPLAY:
            self.set_mode__gameplay()
        elif mode == EUpdateMode.UPDATE_MENU:
            self.set_mode__menu()
        elif mode == EUpdateMode.UPDATE_SETTINGS:
            self.set_mode__settings()
        elif mode == EUpdateMode.UPDATE_STATISTICS:
            self.set_mode__stats()
        elif mode == EUpdateMode.UPDATE_ABOUT:
            self.set_mode__about()
        elif mode == EUpdateMode.INVOKE_EXIT:
            self.set_mode__exit()


    def update(self, delta_time_s: float):
        if self.current in self.game_modes:
            self.game_modes[self.current].update(delta_time_s)
