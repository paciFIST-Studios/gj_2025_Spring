
from enum import Enum, auto

class EGameMode(Enum):
    """ The EGameMode enum shows which game modes exist in the game

        UNINIT - exists to show the game is not finishing being initialized
        DEMO_MODE - this is the main menu, but it also functions as the tutorial, and it plays itself some
        GAMEPLAY_MODE - the gameplay mode is where the "game" lives
        MENU_MODE - manages access to other modes
        SETTINGS_MODE - manages changes to internal settings like: volume, muting, etc
        STATS_MODE - displays gameplay stats such as, longest streak, and times a streak has been reached
        ABOUT_MODE - displays an about page for the game
    """
    UNINIT = auto(), 'uninit'
    DEMO_MODE = auto(), 'demo'
    GAMEPLAY_MODE = auto(), 'gameplay'
    MENU_MODE = auto(), 'menu'
    SETTINGS_MODE = auto(), 'settings'
    STATS_MODE = auto(), 'stats'
    ABOUT_MODE = auto(), 'about'
    INVOKE_EXIT = auto(), 'exit'



class GameMode:
    """

    """
    def __init__(self, engine, game_mode_data: dict):
        self.engine = engine
        self.game_mode_data = game_mode_data

    def value_or_default(self, key, default = None):
        if key and key in self.game_mode_data:
            return self.game_mode_data[key]
        return default

    def update(self, delta_time_s: float):
        """ all game modes need to override this fn with their own version """
        pass



class GameModeManager:
    """ the GameModeManager class is used to represent information about the current game mode, as well
    as some "housekeeping" fns around changing game modes.
    """

    def __init__(self):
        self.current: EGameMode = EGameMode.UNINIT
        self.previous: EGameMode = EGameMode.UNINIT

        # after a game mode changes, every fn in the callables dict is called,
        # if it is in the array pertaining to that game mode
        self.on_mode_changed_callables = {}


        self.game_modes = {}


        # subscribe
        for mode in EGameMode:
            if mode != EGameMode.UNINIT:
                if mode not in self.on_mode_changed_callables:
                    self.on_mode_changed_callables[mode] = []
                # if self.print_current_game_mode not in self.callables[mode]:
                #     self.callables[mode].append(self.print_current_game_mode)

    def print_current_game_mode(self):
        print(f'game mode: {self.current}')

    def is_callable_registered(self, mode: EGameMode, fn: callable):
        if mode is None or not mode or fn is None or not fn:
            return None
        elif mode not in self.on_mode_changed_callables:
            return False
        elif fn not in self.on_mode_changed_callables:
            return False
        return True

    def get_callables_of_mode(self, mode: EGameMode):
        if mode is None:
            return None
        if mode not in self.on_mode_changed_callables:
            return None
        return self.on_mode_changed_callables[mode]

    def register_callable(self, mode: EGameMode, fn: callable) -> bool:
        # this fn also handles null checks
        if self.is_callable_registered(mode, fn):
            return True

        if not mode in self.on_mode_changed_callables:
            self.on_mode_changed_callables[mode] = []

        if fn not in self.on_mode_changed_callables[mode]:
            self.on_mode_changed_callables[mode].append(fn)

        return True

    def unregister_callable(self, mode: EGameMode, fn: callable) -> bool:
        if mode is not None and fn is not None:
            if mode in self.on_mode_changed_callables:
                if fn in self.on_mode_changed_callables[mode]:
                    index = self.on_mode_changed_callables[mode].index(fn)
                    self.on_mode_changed_callables[mode].pop(index)
                    return True
        return False

    def run_callables_for_mode(self, mode: EGameMode):
        assert mode in self.on_mode_changed_callables
        fns = self.on_mode_changed_callables[mode]
        for fn in fns:
            fn()

    def is_mode_registered(self, mode_enum: EGameMode, mode_class: GameMode) -> bool:
        if mode_enum is None or not mode_enum or mode_class is None or not mode_class:
            return None
        elif mode_enum not in self.game_modes:
            return False
        elif mode_class != self.game_modes[mode_enum]:
            return False
        return True

    def register_mode(self, mode_enum: EGameMode, mode_class: GameMode) -> bool:
        if self.is_mode_registered(mode_enum, mode_class):
            return True

        if mode_enum not in self.game_modes:
            self.game_modes[mode_enum] = []

        if mode_class not in self.game_modes[mode_enum]:
            self.game_modes[mode_enum] = mode_class

        return True

    def unregister_mode(self, mode_enum: EGameMode, mode_class: GameMode):
        if mode_enum is not None and mode_class is not None:
            if mode_enum in self.game_modes:
                if mode_class == self.game_modes[mode_enum]:
                    _ = self.game_modes.pop(mode_enum)
                    return True
        return False



    def set_mode__demo(self):
        self.previous = self.current
        self.current = EGameMode.DEMO_MODE
        self.run_callables_for_mode(self.current)

    def set_mode__gameplay(self):
        self.previous = self.current
        self.current = EGameMode.GAMEPLAY_MODE
        self.run_callables_for_mode(self.current)

    def set_mode__menu(self):
        self.previous = self.current
        self.current = EGameMode.MENU_MODE
        self.run_callables_for_mode(self.current)

    def set_mode__settings(self):
        self.previous = self.current
        self.current = EGameMode.SETTINGS_MODE
        self.run_callables_for_mode(self.current)

    def set_mode__stats(self):
        self.previous = self.current
        self.current = EGameMode.STATS_MODE
        self.run_callables_for_mode(self.current)

    def set_mode__about(self):
        self.previous = self.current
        self.current = EGameMode.ABOUT_MODE
        self.run_callables_for_mode(self.current)

    def set_mode__exit(self):
        self.previous = self.current
        self.current = EGameMode.INVOKE_EXIT
        self.run_callables_for_mode(self.current)

    def set_mode(self, mode: EGameMode):
        if mode == EGameMode.DEMO_MODE:
            self.set_mode__demo()
        elif mode == EGameMode.GAMEPLAY_MODE:
            self.set_mode__gameplay()
        elif mode == EGameMode.MENU_MODE:
            self.set_mode__menu()
        elif mode == EGameMode.SETTINGS_MODE:
            self.set_mode__settings()
        elif mode == EGameMode.STATS_MODE:
            self.set_mode__stats()
        elif mode == EGameMode.ABOUT_MODE:
            self.set_mode__about()
        elif mode == EGameMode.INVOKE_EXIT:
            self.set_mode__exit()


    def update(self, delta_time_s: float):
        if self.current in self.game_modes:
            self.game_modes[self.current].update(delta_time_s)
