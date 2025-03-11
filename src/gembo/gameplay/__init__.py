
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

    def update(self, delta_time_s: float, actions_this_frame: list):
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



# class GamplayGameMode(GameMode):
#
#     def update(self, delta_time_s: float, actions_this_frame):
#
#         def is_player_moving(player_input_actions: list):
#             """ the player is_moving flag is used when choosing the next animation frame """
#             for player_action in player_input_actions:
#                 if player_action.name in ['move_left', 'move_right', 'move_up', 'move_down']:
#                     return True
#             return False
#
#         self._player.is_moving = is_player_moving(actions_this_frame)
#
#
#         # collision update -----------------------------------------------------------------------------------------
#         #
#         # This code manages all collision checking.  Right now, the uses are: keeping the player's
#         # position clamped on screen, checking for an overlap between the player and the gem
#
#         def check_gameplay_collision__level_extents():
#             """ checks player collision with the map, and keeps the player position inside
#
#                 NOTE: This is also the only place where player movement is applied to player position
#             """
#             LEFT_COLLISION = 0
#             UP_COLLISION = 0
#
#             w, h = self._display_surface.get_size()
#             RIGHT_COLLISION = w
#             DOWN_COLLISION = h
#
#             for action in actions_this_frame:
#                 if action.name == 'move_left':
#                     displacement = -1 * self._player.speed * delta_time_s
#                     if self._player.position[0] + displacement > LEFT_COLLISION:
#                         self._player.position[0] += displacement
#                         self._player.render_mirrored = True
#
#                 if action.name == 'move_right':
#                     displacement = 1 * self._player.speed * delta_time_s
#                     sprite_width = self._player.image.get_width()
#                     if self._player.position[0] + displacement + sprite_width < RIGHT_COLLISION:
#                         self._player.position[0] += displacement
#                         self._player.render_mirrored = False
#
#                 if action.name == 'move_up':
#                     displacement = -1 * self._player.speed * delta_time_s
#                     if self._player.position[1] + displacement > UP_COLLISION:
#                         self._player.position[1] += displacement
#
#                 if action.name == 'move_down':
#                     displacement = 1 * self._player.speed * delta_time_s
#                     sprite_height = self._player.image.get_height()
#                     if self._player.position[1] + displacement + sprite_height < DOWN_COLLISION:
#                         self._player.position[1] += displacement
#         check_gameplay_collision__level_extents()
#
#         def check_gameplay_collision__gems():
#             """ collects a gem when the player touches one """
#             if self.gem_overlaps_with_player():
#                 self.collect_gem()
#         check_gameplay_collision__gems()
#
#         def check_gameplay_collision__cactus():
#             if self.cactus_overlaps_with_player():
#                 self.collide_with_cactus()
#         check_gameplay_collision__cactus()
#
#         # end collision update -------------------------------------------------------------------------------------
#
#
#         # Player update --------------------------------------------------------------------------------------------
#
#         def update_gameplay_player_speed():
#             def calculate_player_speed_update() -> float:
#                 """ player speed increases over the course of 5 minutes """
#                 # calculate the progression of the player speed (0.0 -> 1.0), based on play session length
#                 current_session_duration_s = time.time() - self._statistics.playtime_this_session_started_at_time
#                 player_speed_progression = clamp((current_session_duration_s / self._player.reaches_top_speed_after_s), 0, 1.0)
#
#                 # walk animation goes faster, as the player goes faster
#                 # (maxes out as a small ratio of increase, over same duration)
#                 def scale_walk_animation_duration(progression):
#                     """ the animation increases in speed over the same interval of time, as the player's movement """
#                     new_walk_duration = pygame.math.lerp(self._player.walk_animation_duration_s__slowest, self._player.walk_animation_duration_s__fastest, progression)
#                     self._player.sprite_animator.update_animation_duration('walk', new_walk_duration)
#                     self._player.sprite_animator.update_animation_duration('walk_flipped', new_walk_duration)
#                 scale_walk_animation_duration(player_speed_progression)
#
#                 return pygame.math.lerp(self._player.start_speed, self._player.top_speed, player_speed_progression)
#
#             self._player.speed = calculate_player_speed_update()
#
#         update_gameplay_player_speed()


# class AboutGameMode(GameMode):
#     def __init__(self, engine, game_mode_data: dict):
#         super().__init__(engine, game_mode_data)
