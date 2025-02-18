
from dataclasses import dataclass
from enum import Enum, auto
import json
import math
import os.path

from pathlib import Path
from random import randint
import time


import pygame
from pygame.key import ScancodeWrapper
from pygame.locals import *


# CONSTANTS ------------------------------------------------------------------------------------------------------------

@dataclass()
class Padding:
    left: int
    top: int
    right: int
    bottom: int

    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

@dataclass(frozen=True)
class TimeConstants:
    SECONDS_IN_A_SECOND: int = 1
    SECONDS_IN_A_MINUTE: int = 60
    SECONDS_IN_AN_HOUR: int = 3_600 # 60 * 60
    SECONDS_IN_A_DAY: int = 86_400 # 60 * 60 * 24
    SECONDS_IN_A_WEEK: int = 604_800 # 60 * 60 * 24 * 7
    SECONDS_IN_A_MONTH: int = 2_592_000 # 60 * 60 * 24 * 30
    SECONDS_IN_A_YEAR: int =  31_536_000 # 60 * 60 * 24 * 365
    SECONDS_IN_A_DECADE: int = 315_360_000 # 60 * 60 * 24 * 366 * 10
    SECONDS_IN_A_CENTURY: int = 3_153_600_000 # 60 * 60 * 24 * 366 * 100
    SECONDS_IN_A_MILLENNIUM: int = 31_536_000_000 # 60 * 60 * 24 * 366 * 1000

    TIME_UNITS_PER_S = {
        # 'millenia': SECONDS_IN_A_MILLENNIUM,
        # 'centuries': SECONDS_IN_A_CENTURY,
        # 'decades': SECONDS_IN_A_DECADE,
        # 'years': SECONDS_IN_A_YEAR,
        # 'months': SECONDS_IN_A_MONTH,
        # 'weeks': SECONDS_IN_A_WEEK,
        # 'days': SECONDS_IN_A_DAY,
        'hours': SECONDS_IN_AN_HOUR,
        'minutes': SECONDS_IN_A_MINUTE,
        'seconds': SECONDS_IN_A_SECOND
    }

    GET_TIME_UNITS_ABBREVIATION = {
        # 'millenia': 'M',
        # 'centuries': 'C',
        # 'decades': 'DD',
        # 'years': 'y',
        # 'months': 'm',
        # 'weeks': 'w',
        # 'days': 'd',
        'hours': 'h',
        'minutes': 'm',
        'seconds': 's'
    }

    @staticmethod
    def get_unlocked_units(seconds):
        time_values = TimeConstants.slice_seconds_into_time_groups(seconds)
        is_unit_unlocked = {}
        for unit, value in time_values.items():
            if value:
                is_unit_unlocked[unit] = True
            else:
                is_unit_unlocked[unit] = False
        return is_unit_unlocked

    @staticmethod
    def slice_seconds_into_time_groups(seconds):
        time_values = {}
        for unit, value in TimeConstants.TIME_UNITS_PER_S.items():
            time_values[unit], seconds = divmod(seconds, value)
        return time_values


class EGameMode(Enum):
    """ The EGameMode enum shows which game modes exist in the game

        UNINIT - exists to show the game is not finishing being initialized
        DEMO_MODE - this is the main menu, but it also functions as the tutorial, and it plays itself some
        GAMEPLAY - the gameplay mode is where the "game" lives
        SETTINGS - manages changes to internal settings like: volume, muting, etc
        STATS - displays gameplay stats such as, longest streak, and times a streak has been reached
    """
    UNINIT = auto(), 'uninit'
    DEMO_MODE = auto(), 'demo'
    GAMEPLAY = auto(), 'gameplay'
    SETTINGS_MENU = auto(), 'settings'
    STATS_MENU = auto(), 'stats'
    ABOUT_MENU = auto(), 'about'

class EColor(str, Enum):
    """ The EColor enum is used to make it easy to work with a small number of defined colors
    """
    HIGHLIGHT_YELLOW = '#FFEB99'
    COOL_GREY = '#35454F'
    BLACK = '#000000'
    LIGHT_BLUE = '#5BCEFA'
    PINK = '#F5A9B8'
    WHITE = '#FFFFFF'


class AppData:
    def __init__(self):
        pass

class EngineData:
    def __init__(self):
        self.audio_is_muted = False


class ImageData:
    def __init__(self):
        pass

class AudioData:
    def __init__(self):
        pass

class FontData:
    def __init__(self):
        self.lcd = None
        self.lcd_small = None
        self.lcd_big = None
        self.dos = None
        self.estrogen = None
        self.love = None
        self.open_dyslexic = None


class GemData:
    """ the GemData class holds information, variables, and functions, which relate to the portrayal of the
    gem during gameplay.  This includes the images uses, sfx, position, respawn timeout, and more
    """
    def __init__(self):
        # this variable is used to blit the gem to
        self.image = None

        # this is the sound played when the player collects a gem
        self.pickup_sound = None

        # the blue gem is used to represent one that has "spoiled"
        self.blue_image = None
        self.blue_sfx = None

        # the yellow gem is used to represent one that is "ripe"
        self.yellow_image = None
        self.yellow_sfx = None

        # the position of the gem on screen
        self.position = pygame.math.Vector2()

        # after being picked up, when should the next gem appear
        self.respawn_timeout_ms = 500

        # how far away can the player be, before it counts as "touching" the gem
        self.pickup_radius = 70

    # the player only scores points for picking up "ripe" gems
    def is_ripe(self):
        return self.image == self.yellow_image


class PlayerData:
    """ the PlayerData class holds information and variables for representing the player's
    avatar, including images, position, speeds, and more
    """
    def __init__(self):
        # "Player" values relate to the player's avatar, and its characteristics
        self.image = None
        self.image_mirrored = None

        self.render_mirrored = False

        # player's current position
        self.position = pygame.math.Vector2()

        # the player should never move faster than this
        self.max_speed = 700

        # the player stops speeding up when they hit this speed
        self.top_speed = 627

        # the player should never move slower than this
        self.min_speed = 70

        # the starting speed the player moves at
        self.start_speed = 200

        # the player's current speed
        self.speed = 200

        # player speed slowly increases over this many seconds, from start speed to top speed
        self.reaches_top_speed_after_s = 60 * 5



class GameplayData:
    """ the GameplayData class is used to represent the current state of gameplay, in EGameMode.Gameplay
    """
    def __init__(self):
        self._last_player_input_timestamp = time.time()


        self.player_is_on_gem_streak = False
        self.player_gem_streak_length = 0

        self.gem_is_active = False

        self.last_gem_pickup_time = time.time()
        self.gem_spoilage_timeout_ms = 1000

        self.current_font = None

        self.floor_line_width = 1
        self.floor_line_padding = 15
        self.floor_line_color = EColor.COOL_GREY


    def increment_gem_streak(self):
        self.player_is_on_gem_streak = True
        self.player_gem_streak_length += 1

    def should_switch_to_demo_mode(self):
        timeout = 30
        if time.time() - self._last_player_input_timestamp:
            pass
            # raise


class GameModeData:
    """ the GameModeData class is used to represent information about the current game mode, as well
    as some "housekeeping" fns around changing game modes.
    """
    def __init__(self):
        self.current : EGameMode = EGameMode.UNINIT

        # after a game mode changes, every fn in the callables dict is called,
        # if it is in the array pertaining to that game mode
        self.callables = {}

        # subscribe
        for mode in EGameMode:
            if mode != EGameMode.UNINIT:
                if mode not in self.callables:
                    self.callables[mode] = []
                if self.print_current_game_mode not in self.callables[mode]:
                    self.callables[mode].append(self.print_current_game_mode)


    def print_current_game_mode(self):
        print(f'game mode: {self.current}')


    def register_callable(self, mode: EGameMode, fn: callable):
        if not mode in self.callables:
            self.callables[mode] = []

        if not fn in self.callables[mode]:
            self.callables[mode].append(fn)

    # def unregister_callable(self, mode: EGameMode, fn: callable):
    #     if mode in self.callables:
    #         if fn in self.callables[mode]:
    #             index = self.callables[mode].index(fn)
    #             self.callables[mode].pop(index)


    def run_callables_for_mode(self, mode: EGameMode):
        assert mode in self.callables
        fns = self.callables[mode]
        for fn in fns:
            fn()

    def set_demo_mode(self):
        self.current = EGameMode.DEMO_MODE
        self.run_callables_for_mode(self.current)

    def set_gameplay_mode(self):
        self.current = EGameMode.GAMEPLAY
        self.run_callables_for_mode(self.current)

    def set_settings_menu(self):
        self.current = EGameMode.SETTINGS_MENU
        self.run_callables_for_mode(self.current)

    def set_stats_menu(self):
        self.current = EGameMode.STATS_MENU
        self.run_callables_for_mode(self.current)

    def set_about_menu(self):
        self.current = EGameMode.ABOUT_MENU
        self.run_callables_for_mode(self.current)

class StatisticsData:
    """ the StaticsData class represents information which has accrued during all play-sessions.
     These are things like: longest streak, number of times the player has hit an N-streak, etc"""
    def __init__(self):
        self.player_stats = {
            'total_play_time': 0.0,
            'total_gems_collected': 0,
            'total_points': 0,
            'longest_streak': 0,
            'player_streak_history':[]
        }
        self.player_stats_file_path = PLAYER_STATS_FILE

        self.playtime_for_all_prior_sessions_duration_s = 0
        self.playtime_this_session_started_at_time = None

        # after parsing player history, this holds a dict where keys are the length of a streak, and
        # values are the number of times that streak has been achieved
        self.streak_counts = None

    def add_one_point(self):
        self.player_stats['total_points'] += 1

    def collect_one_gem(self):
        self.player_stats['total_gems_collected'] += 1

    def get_points(self):
        return self.player_stats['total_points']

    def get_longest_streak(self):
        return self.player_stats['longest_streak']

    def get_streak_history(self):
        return self.player_stats['player_streak_history']

    def update_longest_streak(self, value):
        key = 'longest_streak'
        if not key in self.player_stats:
            self.player_stats[key] = value
        elif self.player_stats[key] < value:
            self.player_stats[key] = value
            print(f'New longest streak! {value}')

    def update_streak_history(self, value):
        key = 'player_streak_history'
        if not key in self.player_stats:
            self.layer_stats[key] = []
        self.player_stats[key].append((time.time(), value))
        print(f'Streak: {value}')

    def parse_player_history(self):
        def count_streak_lengths(data):
            streaks = [y for x,y in data]
            result = {}
            for streak in streaks:
                if streak not in result:
                    result[streak] = 1
                else:
                    result[streak] += 1
            return result

        history = self.get_streak_history()
        streaks = count_streak_lengths(history)
        self.streak_counts = streaks



class UIData:
    """ the UIData class holds information related to drawing UI on screen, regardless of which
    EGameMode uses that information
    """
    def __init__(self):
        # time played
        self.time_played_text_color = EColor.COOL_GREY
        self.time_played_text_position = None
        self.time_played_text_is_visible = True
        self.time_played_text_highlight_timeout_ms = 1000

        # total points
        self.point_total_text_color = EColor.COOL_GREY
        self.point_total_text_position = None
        self.point_total_text_is_visible = True
        self.point_total_text_highlight_duration_ms = 1000


    def highlight_time_played_text(self):
        self.time_played_text_color = EColor.HIGHLIGHT_YELLOW

    def unhighlight_time_played_text(self):
        self.time_played_text_color = EColor.COOL_GREY

    def highlight_total_points(self):
        self.point_total_text_color = EColor.HIGHLIGHT_YELLOW

    def unhighlight_total_points(self):
        self.point_total_text_color = EColor.COOL_GREY


# GLOBALS --------------------------------------------------------------------------------------------------------------

# aka: game resolution
APPLICATION_WINDOW_SIZE = (480, 640)

# file path for the information stored about the play session
PLAYER_STATS_FILE = 'game.data'

IMAGES_TO_LOAD = [
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Player/p1_stand.png',
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Items/gemBlue.png',
    '/home/ellie/git/gj_2025_Spring/resources/platformerGraphicsDeluxe_Updated/Items/gemYellow.png',
    '/home/ellie/git/gj_2025_Spring/resources/illegal.png',
]

AUDIO_TO_LOAD = [
    '/home/ellie/git/gj_2025_Spring/resources/GUI_Sound_Effects_by_Lokif/misc_menu_2.mp3',
    '/home/ellie/git/gj_2025_Spring/resources/GUI_Sound_Effects_by_Lokif/misc_menu_4.mp3',
    '/home/ellie/git/gj_2025_Spring/resources/GUI_Sound_Effects_by_Lokif/sharp_echo.mp3',
    '/home/ellie/git/gj_2025_Spring/resources/krank_sounds/unlink.mp3',
    '/home/ellie/git/gj_2025_Spring/resources/Luke.RUSTLTD/coin_sounds/coin7.mp3',
    '/home/ellie/git/gj_2025_Spring/resources/Luke.RUSTLTD/coin_sounds/coin10.mp3',
]

# NOTE: to have different font sizes, you need to pull them in at that size
FONTS_TO_LOAD = [
    ('lcd_big', 70, '/home/ellie/git/gj_2025_Spring/resources/LCD Mono/lcd_lcd_mono/LCDMonoWinTT/LCDM2N__.TTF'),
    ('lcd', 40, '/home/ellie/git/gj_2025_Spring/resources/LCD Mono/lcd_lcd_mono/LCDMonoWinTT/LCDM2N__.TTF'),
    ('lcd_small', 30, '/home/ellie/git/gj_2025_Spring/resources/LCD Mono/lcd_lcd_mono/LCDMonoWinTT/LCDM2N__.TTF'),
    ('dos', 30, '/home/ellie/git/gj_2025_Spring/resources/good_old_dos_font/GoodOldDOS.ttf'),
    ('estrogen', 60, '/home/ellie/git/gj_2025_Spring/resources/estrogen_font/estrogen/ESTROG__.ttf'),
    ('love', 24, '/home/ellie/git/gj_2025_Spring/resources/pil_love/pil_love.ttf'),
    ('open_dyslexic', 18, '/home/ellie/git/gj_2025_Spring/resources/open_dyslexic/OpenDyslexicAlta-Regular.otf')
]


# loaders --------------------------------------------------------------------------------------------------------------

def load_text_file(path):
    if os.path.isfile(path):
        with open(path, 'r') as infile:
            return infile.read()

def load_json(path):
    data = load_text_file(path)
    if data:
        return json.loads(data)

def write_text_file(path, data):
    with open(path, 'w') as outfile:
        outfile.write(data)

def write_json(path, obj):
    jstr = json.dumps(obj)
    write_text_file(path, jstr)

def load_image(path):
    if os.path.isfile(path):
        # note, calling convert, or convert_alpha here is crucial, b/c pygame will re-order the internal
        # color channels of the image, to match the running machine's hardware
        return pygame.image.load(path).convert_alpha()
    return None

def load_sound(path):
    if pygame.mixer and os.path.isfile(path):
        return pygame.mixer.Sound(path)
    return None

def load_font(path, size):
    if os.path.isfile(path):
        return pygame.font.Font(path, size)

# utilities ------------------------------------------------------------------------------------------------------------

def clamp(x, min, max):
    if x is None or min is None or max is None:
        return None
    elif x > max:
        return max
    elif x < min:
        return min
    else:
        return x



# Classes --------------------------------------------------------------------------------------------------------------

class App:
    INSTANCE = None

    # def gameplay_only(self, func):
    #     @functools.wraps(func)
    #     def wrapper_gameplay_only(*args, **kwargs):
    #         if self._game_mode == GameMode.GAMEPLAY:
    #             return func(*args, **kwargs)
    #     return wrapper_gameplay_only


    def get_elapsed_time(self) -> str:
        now = time.time()
        duration = now - self._app_start_time
        hours = int(duration) // 3600
        minutes = (int(duration) % 3600) // 60
        seconds = int(duration) % 60
        return f'{hours:02}h {minutes:02}m {seconds:02}s'

    def get_current_session_playtime_s(self):
        return time.time() - self._statistics.playtime_this_session_started_at_time

    def get_total_playtime_s(self):
        current = self.get_current_session_playtime_s()
        return current + self._statistics.player_stats['total_play_time']

    @staticmethod
    def get_scaled_sin(x):
        return (math.sin(x)/2) + 0.5

    def __init__(self):
        self.INSTANCE = self
        self._running = True
        self._display_surface = None

        self._app_window_title = 'Gembo'
        pygame.display.set_caption(self._app_window_title)
        self._app_start_time = time.time()
        self._app_clock = pygame.time.Clock()

        self._engine_frame_count = 0
        self._engine_frame_time_start = time.time()
        self._engine_last_frame_start = None

        # user defined events, 8 max
        self.EVENT__RESPAWN_GEM = pygame.event.custom_type()
        self.EVENT__SPOIL_GEM = pygame.event.custom_type()
        self.EVENT__UNHIGHLIGHT_GEM_COUNT = pygame.event.custom_type()
        self.EVENT__UNHIGHLIGHT_TIME_PLAYED = pygame.event.custom_type()
        self.EVENT__SWITCH_GAME_MODE = pygame.event.custom_type()
        self.EVENT__5 = pygame.event.custom_type()
        self.EVENT__6 = pygame.event.custom_type()
        self.EVENT__7 = pygame.event.custom_type()


        self._input_function_map = {}


        # loaders and resource dictionaries ----------------------------------------------------------------------------

        self._images_to_load = IMAGES_TO_LOAD
        self._loaded_image_surfaces = {}

        self._audio_to_load = AUDIO_TO_LOAD
        self._loaded_audio_sounds = {}

        self._display_fonts_to_load = FONTS_TO_LOAD
        self._loaded_display_fonts = {}

        # Memory Objects -----------------------------------------------------------------------------------------------

        # application/engine
        self._app = AppData()
        self._engine = EngineData()

        # resources
        self._image = ImageData()
        self._audio = AudioData()
        self._font = FontData()

        # game mode
        self._game_mode = GameModeData()

        # gameplay concepts
        self._gameplay = GameplayData()
        self._gem = GemData()
        self._player = PlayerData()

        # multi-session recording
        self._statistics = StatisticsData()

        # ui and rendering info
        self._ui = UIData()

        self._user_input_this_frame = None


    def initialize_images(self):
        for image_path in self._images_to_load:
            surface = load_image(image_path)
            # the stem is just the file name, w/o the extension
            name = Path(image_path).stem
            self._loaded_image_surfaces[name] = surface

        self._player.image = self._loaded_image_surfaces['p1_stand']
        self._gem.blue_image = self._loaded_image_surfaces['gemBlue']
        self._gem.yellow_image = self._loaded_image_surfaces['gemYellow']
        self._gem.image = self._gem.yellow_image

        self._player.image_mirrored = pygame.transform.flip(self._player.image, True, False)


    def initialize_sounds(self):
        for audio_path in self._audio_to_load:
            sound = load_sound(audio_path)
            name = Path(audio_path).stem
            self._loaded_audio_sounds[name] = sound

        self._gem.blue_sfx = self._loaded_audio_sounds['misc_menu_2']
        self._gem.yellow_sfx = self._loaded_audio_sounds['coin10']


    def initialize_font(self):
        for name, size, path in self._display_fonts_to_load:
            font = load_font(path, size)
            self._loaded_display_fonts[name] = font

        self._font.lcd_big = self._loaded_display_fonts['lcd_big']
        self._font.lcd = self._loaded_display_fonts['lcd']
        self._font.lcd_small = self._loaded_display_fonts['lcd_small']
        self._font.dos = self._loaded_display_fonts['dos']
        self._font.estrogen = self._loaded_display_fonts['estrogen']
        self._font.love = self._loaded_display_fonts['love']
        self._font.open_dyslexic = self._loaded_display_fonts['open_dyslexic']

        self._gameplay.font = self._font.lcd


    def initialize_gameplay(self):
        assert hasattr(self._game_mode, 'current')

        w, h = self._display_surface.get_size()
        self._ui.time_played_text_position = (w - 350, 30)
        self._ui.point_total_text_position = (w - 270, 80)

        # place the first gem, to start the cycle
        self.place_gem()

        stats = load_json(self._statistics.player_stats_file_path)
        if stats:
            self._statistics.player_stats = stats

        self._statistics.parse_player_history()

        self._player.speed = self._player.start_speed

        # now initialization is complete, set to demo mode for the main menu
        self._game_mode.set_demo_mode()

    def get_user_input_this_frame(self):
        return self._user_input_this_frame

    @staticmethod
    def collect_user_input() -> list[str]:
        def _up_input(frame_input: ScancodeWrapper):
            if frame_input[K_UP] or frame_input[K_w]:
                return 'move_up'
        def _down_input(frame_input: ScancodeWrapper):
            if frame_input[K_DOWN] or frame_input[K_s]:
                return 'move_down'
        def _left_input(frame_input: ScancodeWrapper):
            if frame_input[K_LEFT] or frame_input[K_a]:
                return 'move_left'
        def _right_input(frame_input: ScancodeWrapper):
            if frame_input[K_RIGHT] or frame_input[K_d]:
                return 'move_right'

        keys = pygame.key.get_pressed()
        result = [
            _up_input(keys),
            _down_input(keys),
            _left_input(keys),
            _right_input(keys),
        ]
        return [x for x in result if x]

    # Gameplay Functions -----------------------------------------------------------------------------------------------

    def gem_overlaps_with_player(self):
        if self._gameplay.gem_is_active:
            distance = self._player.position - self._gem.position
            magnitude = distance.magnitude()
            if magnitude < self._gem.pickup_radius:
                #print(f'collision: player{self._player_pos}, gem{self._gem_pos}, distance={magnitude:3.6}, collision_radius={self._gem_pickup_radius}')
                return True
        return False

    @staticmethod
    def get_random_onscreen_coordinate(surface):
        min_x, min_y = 0, 0
        max_x, max_y = surface.get_size()
        return randint(min_x, max_x), randint(min_y, max_y)


    def collect_gem(self):
        if self._game_mode.current != EGameMode.GAMEPLAY:
            return

        # set gem to not active, so it can be respawned
        self._gameplay.gem_is_active = False

        # emit the respawn event after timeout
        pygame.time.set_timer(self.EVENT__RESPAWN_GEM, self._gem.respawn_timeout_ms)

        # notify the stats that a gem has been collected
        self._statistics.collect_one_gem()

        # play this sound when picking up a gem
        self._gem.pickup_sound = self._gem.blue_sfx

        # "ripe" gems
        if self._gem.is_ripe():
            # the player is starting or continuing a streak
            self._gameplay.increment_gem_streak()
            # ripe gems are worth one point
            self._statistics.add_one_point()
            # update to play the "ripe gem sound"
            self._gem.pickup_sound = self._gem.yellow_sfx
            # highlight the total points text, in recognition of the point
            self._ui.highlight_total_points()
            # emit an event to turn off the highlight after a timeout
            pygame.time.set_timer(self.EVENT__UNHIGHLIGHT_GEM_COUNT, self._ui.point_total_text_highlight_duration_ms)

        # "spoiled" gems
        else:
            # if on a streak, it ends, and we calculate the stats to see if the player is on the scoreboard
            if self._gameplay.player_is_on_gem_streak:
                self._gameplay.player_is_on_gem_streak = False
                self._statistics.update_longest_streak(self._gameplay.player_gem_streak_length)
                self._statistics.update_streak_history(self._gameplay.player_gem_streak_length)

            self._gameplay.player_gem_streak_length = 0

        if not self._engine.audio_is_muted:
            pygame.mixer.Sound.play(self._gem.pickup_sound)

        self._gameplay.last_gem_pickup_timestamp = time.time()

    def spoil_gem(self):
        """ When a gem spoils, it is not worth points.  This fn changes the image """
        self._gem.image = self._gem.blue_image

    def place_gem(self):
        """ places a gem on screen, if there is not one already """
        # only want one gem at a time
        if self._gameplay.gem_is_active:
            return

        def _clamp_onscreen(value, min, max):
            if value < min:
                value = min - value
            if value > max:
                value = value - max
            return value

        pos = self.get_random_onscreen_coordinate(self._display_surface)
        w, h = self._gem.image.get_size()

        pos_x = _clamp_onscreen(pos[0], 0, w)
        pos_y = _clamp_onscreen(pos[1], 0, h)

        self._gem.position = pygame.math.Vector2(pos_x, pos_y)

        self._gem.image = self._gem.yellow_image
        pygame.time.set_timer(self.EVENT__SPOIL_GEM, self._gameplay.gem_spoilage_timeout_ms)

        self._gameplay.gem_is_active = True
        #print(f'gem placed: {self._gem_pos}, {self.get_elapsed_time()}')

    def should_display_player_streak_popup(self):
        display_streak_at_length = 3
        if self._gameplay.player_is_on_gem_streak:
            return self._gameplay.player_gem_streak_length >= display_streak_at_length
        return False

    #-------------------------------------------------------------------------------------------------------------------


    def on_init(self) -> bool:
        """ the engine's initialization fn """

        pygame.mixer.pre_init(44100, 16, 2, 4096)
        pygame.init()
        flags = pygame.HWSURFACE | pygame.DOUBLEBUF
        self._display_surface = pygame.display.set_mode(APPLICATION_WINDOW_SIZE, flags, 16)
        self._running = True

        self.initialize_images()
        self.initialize_sounds()
        self.initialize_font()
        self.initialize_gameplay()

        # register the parse_player_history fn w/ changing to the stats menu, so it's always ready
        # by the time we need to render it
        self._game_mode.register_callable(EGameMode.STATS_MENU, self._statistics.parse_player_history)

        self._statistics.playtime_this_session_started_at_time = time.time()

        return True


    def on_event(self, event):
        """ the engine's event fn """
        # check for quit
        if event.type == QUIT:
            self._running = False
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            self._running = False

        # check for custom events
        if event.type == self.EVENT__RESPAWN_GEM:
            self.place_gem()
        elif event.type == self.EVENT__SPOIL_GEM:
            self.spoil_gem()
        elif event.type == self.EVENT__UNHIGHLIGHT_GEM_COUNT:
            self._ui.unhighlight_total_points()
        elif event.type == self.EVENT__UNHIGHLIGHT_TIME_PLAYED:
            self._ui.unhighlight_time_played_text()


        # check for keys
        if event.type == KEYDOWN:
            key = event.key

            if key == K_SPACE:
                self.place_gem()
            elif key == 91:
                self._player.speed /= 1.1
                print(f'speed: {int(self._player.speed)}')
            elif key == 93:
                self._player.speed *= 1.1
                print(f'speed: {int(self._player.speed)}')
            elif key == K_1:
                self._game_mode.set_demo_mode()
            elif key == K_2:
                self._game_mode.set_gameplay_mode()
            elif key == K_3:
                self._game_mode.set_settings_menu()
            elif key == K_4:
                self._game_mode.set_stats_menu()
            elif key == K_5:
                self._game_mode.set_about_menu()


    def on_input(self, input_name):
        """ the engine's input fn """
        self._input_function_map[input_name]()


    def on_update(self, delta_time_s):
        """ the engine's update fn """
        self._user_input_this_frame = self.collect_user_input()

        #@self.gameplay_only
        def update_gameplay():
            # collision update ------------------------------------------------------------------------------------------------
            #
            # This code manages all collision checking.  Right now, the uses are: keeping the player's
            # position clamped on screen, checking for an overlap between the player and the gem

            def check_gameplay_collision__level_extents():
                """ checks player collision with the map, and keeps the player position inside """
                LEFT_COLLISION = 0
                UP_COLLISION = 0

                w, h = self._display_surface.get_size()
                RIGHT_COLLISION = w
                DOWN_COLLISION = h

                if 'move_left' in self._user_input_this_frame:
                    displacement = -1 * self._player.speed * delta_time_s
                    if self._player.position[0] + displacement > LEFT_COLLISION:
                        self._player.position[0] += displacement
                        self._player.render_mirrored = True

                if 'move_right' in self._user_input_this_frame:
                    displacement = 1 * self._player.speed * delta_time_s
                    sprite_width = self._player.image.get_width()
                    if self._player.position[0] + displacement + sprite_width < RIGHT_COLLISION:
                        self._player.position[0] += displacement
                        self._player.render_mirrored = False

                if 'move_up' in self._user_input_this_frame:
                    displacement = -1 * self._player.speed * delta_time_s
                    if self._player.position[1] + displacement > UP_COLLISION:
                        self._player.position[1] += displacement

                if 'move_down' in self._user_input_this_frame:
                    displacement = 1 * self._player.speed * delta_time_s
                    sprite_height = self._player.image.get_height()
                    if self._player.position[1] + displacement + sprite_height < DOWN_COLLISION:
                        self._player.position[1] += displacement
            check_gameplay_collision__level_extents()

            def check_gameplay_collision__gems():
                """ collects a gem when the player touches one """
                if self.gem_overlaps_with_player():
                    self.collect_gem()
            check_gameplay_collision__gems()

            # Player update ------------------------------------------------------------------------------------------------

            def update_gameplay_player_speed():
                def get_player_speed() -> float:
                    """ player speed increases over the course of 5 minutes """
                    current_session_duration_s = time.time() - self._statistics.playtime_this_session_started_at_time
                    player_speed_percentile = clamp((current_session_duration_s / self._player.reaches_top_speed_after_s), 0, 1.0)
                    return pygame.math.lerp(self._player.start_speed, self._player.top_speed, player_speed_percentile)

                self._player.speed = get_player_speed()
                # print(f'player.speed_increase.lerp_t: {percent_complete:2.4}, player.speed: {self._player_speed:2.4}')

            update_gameplay_player_speed()

        #@self.settings_menu_only
        def update_settings_menu():
            #print(f'This is the settings menu update loop!')
            pass

        #@self.demo_mode_only
        def update_demo_mode():
            # if the user presses a move button, then go to gameplay mode
            if len(self._user_input_this_frame) > 0:
                self._game_mode.set_gameplay_mode()


        #@self.stats_menu_only
        def update_stats_menu():
            # print(f'This is the stats menu loop!')
            pass

        # these fns all have a decorator on them, which checks the current game mode
        # before calling the function.  All future game modes will have to be in here too

        if self._game_mode.current == EGameMode.GAMEPLAY:
            update_gameplay()
        elif self._game_mode.current == EGameMode.SETTINGS_MENU:
            update_settings_menu()
        elif self._game_mode.current == EGameMode.DEMO_MODE:
            update_demo_mode()
        elif self._game_mode.current == EGameMode.STATS_MENU:
            update_stats_menu()


    # On Render --------------------------------------------------------------------------------------------------------
    #
    #   This rendering fn contains a suite of rendering fns used for all aspects of this game
    #   mostly, a single render function exists for each game mode, it contains as many interior
    #   fns as it needs

    def on_render(self):
        # clear the screen
        black = (0, 0, 0)
        self._display_surface.fill(EColor.BLACK)

        screen_width, screen_height = self._display_surface.get_size()
        assert_screen_width = screen_width
        assert_screen_height = screen_height

        def check_screen_width():
            assert screen_width == assert_screen_width
            assert screen_height == assert_screen_height


        def render_breathe_box(surface, padding: Padding, color: Color, width: int = 1, is_animated=True, breathe_ratio: float = 20):
            """ The "breathe box" is a box that rhythmically contracts, according to the value 'breathe_ratio'.  This value could range (20, 3)
            """
            surface_width, surface_height = surface.get_size()

            # line positions
            left = padding.left
            right = padding.right
            top = padding.top
            bottom = padding.bottom

            if is_animated:
                # this animation causes the lines to contract (is this cubic?)
                time_now = time.time()
                scaled_sin = self.get_scaled_sin(time_now)

                # offset both scales by an amount determined by that axis of the screen, and its length
                # this keeps the aspect ratio the same
                offset_w = surface_width / breathe_ratio * scaled_sin
                offset_h = surface_height / breathe_ratio * scaled_sin

                left += scaled_sin * offset_w
                right += scaled_sin * -offset_w
                top += scaled_sin * offset_h
                bottom += scaled_sin * -offset_h

                pygame.draw.line(surface, color, (left, top), (right, top), width)
                pygame.draw.line(surface, color, (left, top), (left, bottom), width)
                pygame.draw.line(surface, color, (right, top), (right, bottom), width)
                pygame.draw.line(surface, color, (left, bottom), (right, bottom), width)


        #@self.gameplay_only
        def render_active_gameplay():
            def render_gameplay_floor():
                check_screen_width()

                # line positions
                left = 0 + self._gameplay.floor_line_padding
                right = screen_width - self._gameplay.floor_line_padding
                top = 0 + self._gameplay.floor_line_padding
                bottom = screen_height - self._gameplay.floor_line_padding

                render_breathe_box(
                    surface=self._display_surface,
                    padding=Padding(left, top, right, bottom),
                    color=self._gameplay.floor_line_color,
                    width=self._gameplay.floor_line_width,
                    is_animated=True,
                    breathe_ratio=5.0
                )
            render_gameplay_floor()

            def render_gameplay_timer():
                if self._ui.time_played_text_is_visible:
                    playtime_s = self.get_total_playtime_s()

                    # assemble the timer string
                    time_values = TimeConstants.slice_seconds_into_time_groups(playtime_s)
                    timer_string = ''
                    for key, value in time_values.items():
                        abbreviation = TimeConstants.GET_TIME_UNITS_ABBREVIATION[key]
                        timer_string += f'{int(value):02}{abbreviation} '

                    # timer blinks yellow on every minute
                    if '00s' in timer_string:
                        self._ui.highlight_time_played_text()
                        pygame.time.set_timer(self.EVENT__UNHIGHLIGHT_TIME_PLAYED, self._ui.time_played_text_highlight_timeout_ms)
                    else:
                        self._ui.unhighlight_time_played_text()

                    # calculate centered-on-screen position for the gameplay timer
                    gameplay_timer_renderable_text = self._gameplay.font.render(timer_string.strip(), True, self._ui.time_played_text_color)
                    gameplay_timer_width, _ = gameplay_timer_renderable_text.get_size()
                    _, pos_y = self._ui.time_played_text_position
                    pos_x = (screen_width/2) - (gameplay_timer_width/2)

                    # blit
                    self._display_surface.blit(gameplay_timer_renderable_text, (pos_x, pos_y))
            render_gameplay_timer()

            def render_gameplay_points():
                if self._ui.point_total_text_is_visible:
                    total = self._statistics.player_stats['total_points']

                    # build points string
                    point_total_string = f'{total}'
                    point_total_renderable_text = self._gameplay.font.render(point_total_string, True, self._ui.point_total_text_color)

                    # calculate centered on screen position
                    point_total_width, _ = point_total_renderable_text.get_size()
                    _, pos_y = self._ui.point_total_text_position
                    pos_x = (screen_width/2) - (point_total_width/2)

                    # blit
                    self._display_surface.blit(point_total_renderable_text, (pos_x, pos_y))
            render_gameplay_points()

            def render_current_streak_popup():
                if self.should_display_player_streak_popup():
                    streak = self._gameplay.player_gem_streak_length
                    streak_string = f'x{streak}'
                    streak_renderable_text = self._font.lcd_big.render(streak_string, True, EColor.HIGHLIGHT_YELLOW)

                    text_width, _ = streak_renderable_text.get_size()
                    pos_y = screen_height - 90
                    pos_x = (screen_width/2)-(text_width/2)

                    self._display_surface.blit(streak_renderable_text, (pos_x, pos_y))

                    """ When the player starts a streak, they have 1 point.  We will hide the current_streak_popup,
                    until the player has 3 points.  Then the popup should:
                        * fly in - easing
                        * show the number of the current streak
                        * look visually engaging
                        * play an extra sound
                        * play a final "fireworks" when the streak ends
                        * fly out - easing
                    
                    """
                    pass
            render_current_streak_popup()

            def render_player_image():
                blit_image = self._player.image

                if self._player.render_mirrored:
                    blit_image = self._player.image_mirrored

                self._display_surface.blit(blit_image, self._player.position)
            render_player_image()

            def render_gem():
                if self._gameplay.gem_is_active:
                    self._display_surface.blit(self._gem.image, self._gem.position)
            render_gem()


        #@self.settings_menu_only
        def render_settings_menu():
            def render_settings_menu_box():
                # line positions
                left = 0 + self._gameplay.floor_line_padding
                right = screen_width - self._gameplay.floor_line_padding
                top = 0 + self._gameplay.floor_line_padding
                bottom = screen_height - self._gameplay.floor_line_padding

                render_breathe_box(
                    surface=self._display_surface,
                    padding=Padding(left, top, right, bottom),
                    color=self._gameplay.floor_line_color,
                    is_animated=True)
            render_settings_menu_box()

            def render_settings_menu_title_text():
                settings_menu_title_string = 'Settings'
                settings_menu_title_renderable_text = self._font.lcd.render(settings_menu_title_string, True, EColor.HIGHLIGHT_YELLOW)

                # calculate centered on screen position
                point_total_width, _ = settings_menu_title_renderable_text.get_size()
                _, pos_y = self._ui.time_played_text_position
                pos_x = (screen_width/2) - (point_total_width/2)

                # blit
                self._display_surface.blit(settings_menu_title_renderable_text, (pos_x, pos_y))

            render_settings_menu_title_text()

            def render_settings_menu_options_text():
                options = [
                    'mute',
                    'sfx_volume',
                    'audio_volume',
                    'input_bindings'
                ]

                x_pos, y_pos = 60, 90
                for opt in options:
                    string = opt
                    color = EColor.COOL_GREY
                    text = self._font.lcd_small.render(string, True, color)
                    self._display_surface.blit(text, (x_pos, y_pos))
                    y_pos += 60

            render_settings_menu_options_text()


        #@self.demo_mode_only
        def render_demo_mode():
            def render_box():
                # line positions
                left = 0 + self._gameplay.floor_line_padding
                right = screen_width - self._gameplay.floor_line_padding
                top = 0 + self._gameplay.floor_line_padding
                bottom = screen_height - self._gameplay.floor_line_padding

                render_breathe_box(
                    surface=self._display_surface,
                    padding=Padding(left, top, right, bottom),
                    color=self._gameplay.floor_line_color,
                    is_animated=True)

            render_box()

            def render_demo_title():
                demo_mode_title_string = self._app_window_title
                demo_mode_title_renderable_text = self._font.lcd_big.render(demo_mode_title_string, True, EColor.HIGHLIGHT_YELLOW)

                # calculate centered on screen position
                text_width, _ = demo_mode_title_renderable_text.get_size()

                pos_y = 120
                pos_x = (screen_width/2) - (text_width/2)

                # blit
                self._display_surface.blit(demo_mode_title_renderable_text, (pos_x, pos_y))

            render_demo_title()

        #@self.stats_menu_only
        def render_stats_menu():
            def render_stats_menu_box():
                # line positions
                left = 0 + self._gameplay.floor_line_padding
                right = screen_width - self._gameplay.floor_line_padding
                top = 0 + self._gameplay.floor_line_padding
                bottom = screen_height - self._gameplay.floor_line_padding

                render_breathe_box(
                    surface=self._display_surface,
                    padding=Padding(left, top, right, bottom),
                    color=self._gameplay.floor_line_color,
                    is_animated=True)
            render_stats_menu_box()

            def render_stats_menu_title_text():
                stats_menu_title_string = 'Stats'
                stats_menu_title_renderable_text = self._font.lcd.render(stats_menu_title_string, True, EColor.HIGHLIGHT_YELLOW)

                # calculate centered on screen position
                text_width, _ = stats_menu_title_renderable_text.get_size()
                pos_y = 30
                pos_x = (screen_width/2) - (text_width/2)

                # blit
                self._display_surface.blit(stats_menu_title_renderable_text, (pos_x, pos_y))
            render_stats_menu_title_text()

            def render_stats_menu_stats():
                assert self._statistics.streak_counts
                streaks = list(
                    reversed(
                        sorted(
                            [(x, y) for x, y in self._statistics.streak_counts.items()]
                        )
                    )
                )

                y_pos = 90

                text = f'Streak        Count'
                renderable_text = self._font.lcd_small.render(text, True, EColor.COOL_GREY)
                text_width, _ = renderable_text.get_size()
                x_pos = (screen_width/2) - (text_width/2)
                self._display_surface.blit(renderable_text, (x_pos, y_pos))

                y_pos += 30
                for streak, count in streaks:
                    text = f'{streak}            {count}'
                    renderable_text = self._font.lcd_small.render(text, True, EColor.COOL_GREY)
                    text_width, _ = renderable_text.get_size()
                    x_pos = (screen_width/2) - (text_width/2)
                    y_pos += 30
                    self._display_surface.blit(renderable_text, (x_pos, y_pos))
            render_stats_menu_stats()

        def render_about_menu():
            def render_stats_menu_box():
                # line positions
                left = 0 + self._gameplay.floor_line_padding
                right = screen_width - self._gameplay.floor_line_padding
                top = 0 + self._gameplay.floor_line_padding
                bottom = screen_height - self._gameplay.floor_line_padding

                surface = self._display_surface
                color = self._gameplay.floor_line_color
                width = self._gameplay.floor_line_width
                pygame.draw.line(surface, color, (left, top), (right, top), width)
                pygame.draw.line(surface, color, (left, top), (left, bottom), width)
                pygame.draw.line(surface, color, (right, top), (right, bottom), width)
                pygame.draw.line(surface, color, (left, bottom), (right, bottom), width)
            render_stats_menu_box()

            def render_ellie_loves_games():
                ellie = 'ellie'
                loves = 'love\'s'
                games = 'games'

                ellie_renderable_text = self._font.estrogen.render(ellie, True, EColor.WHITE)
                loves_renderable_text = self._font.estrogen.render(loves, True, EColor.PINK)
                games_renderable_text = self._font.estrogen.render(games, True, EColor.LIGHT_BLUE)

                renderable_texts = [ ellie_renderable_text, loves_renderable_text, games_renderable_text]

                y_pos = 90
                for renderable_text in renderable_texts:
                    text_width, _ = renderable_text.get_size()
                    x_pos = (screen_width/2) - (text_width/2)
                    y_pos += 40
                    self._display_surface.blit(renderable_text, (x_pos, y_pos))
            render_ellie_loves_games()

            def homily():
                text1 = 'Dedicated to my friend Greg,'
                text2 = 'who wanted to make small games.'

                renderable_text1 = self._font.open_dyslexic.render(text1, True, EColor.COOL_GREY)
                renderable_text2 = self._font.open_dyslexic.render(text2, True, EColor.COOL_GREY)

                renderable_texts = [renderable_text1, renderable_text2]

                y_pos = screen_height - 240
                for renderable_text in renderable_texts:
                    text_width, _ = renderable_text.get_size()
                    x_pos = (screen_width/2) - (text_width/2)
                    y_pos += 30
                    self._display_surface.blit(renderable_text, (x_pos, y_pos))
            homily()


        # --------------------------------------------------------------------------------------------------------------
        # Render for the correct mode
        # --------------------------------------------------------------------------------------------------------------

        if self._game_mode.current == EGameMode.GAMEPLAY:
            render_active_gameplay()
        elif self._game_mode.current == EGameMode.SETTINGS_MENU:
            render_settings_menu()
        elif self._game_mode.current == EGameMode.DEMO_MODE:
            render_demo_mode()
        elif self._game_mode.current == EGameMode.STATS_MENU:
            render_stats_menu()
        elif self._game_mode.current == EGameMode.ABOUT_MENU:
            render_about_menu()

        pygame.display.flip()


    def cleanup_gameplay(self):
        self._statistics.player_stats['total_play_time'] = self.get_total_playtime_s()
        write_json(self._statistics.player_stats_file_path, self._statistics.player_stats)


    def on_cleanup(self):
        """ this fn is called when shutting down the game """
        self.cleanup_gameplay()
        pygame.quit()



    def on_execute(self):
        """ this fn runs the game engine """
        if not self.on_init():
            self._running = False

        print_avg_fps = False
        print_fps_every_n_seconds = 1
        fps_last_printed = time.time()

        while self._running:

            self._engine_last_frame_start = self._engine_frame_time_start
            self._engine_frame_time_start = time.time()
            delta_time_s = self._engine_frame_time_start - self._engine_last_frame_start
            for event in pygame.event.get():
                self.on_event(event)
            self.on_update(delta_time_s)
            self.on_render()
            self._engine_frame_count += 1

            if print_avg_fps and self._engine_frame_time_start - fps_last_printed > print_fps_every_n_seconds:
                print(f'(avg)fps = {int(self._engine_frame_count / (self._engine_frame_time_start - self._app_start_time))}')
                fps_last_printed = self._engine_frame_time_start

            # budget to 30 fps / 32ms
            frame_time_budget = 0.032
            if delta_time_s < frame_time_budget:
                sleep_for = frame_time_budget - delta_time_s
                time.sleep(sleep_for)

        self.on_cleanup()



if __name__ == '__main__':
    application = App()
    application.on_execute()




#-----------------------------------------------------------------------------------------------------------------------
# Devlog
#-----------------------------------------------------------------------------------------------------------------------
"""
    Todo:

        put tutorial on demo screen
            - it should be the player character moving in a loop, first getting a yellow gem, and gaining a point,
                and being excited, and one getting a blue gem, and getting nothing
                - this loop just kind of continues while the player is on this screen

        find out if scrollable lists will be a thing or not
        
        find out if tweening alpha values for face in will be a thing or not
        
        find out if tweening position values for animations will be a thing or not

        find out what kind of options you need to include
        
        find out how to make an input selector
            - just have a: press input for "move_left", press input for "move_right", etc
            - have a pause button, which brings up the choice of options or scoreboard
                - choose left or right
                - press pause again to unpause

        if left alone for 30 seconds, goes back to demo mode

        find out how we can spawn gems inside a certain radius to player

        find out how we can spawn gems within a certain deviation from player's forward motion

        find out if we can squash and stretch player image and tween that for animations

        - make it so we can spawn gems in a pattern-over-time, so the player can simply travel that direction to pick up the gems, in a "coin ship victory procession"
            - some content will be:
                - player chases those designs, picking up gems


    Thoughts about:
        1. visual effects
            a. so, right now, we've got a game, and it's basically playable.  The experience is engaging, but doesn't
                require a large amount of thought, you just kind of play for a while, and you see lights and hear sounds
            b. we need to add:
                i. something that raises the energy every time you get a new point, while the streak thing is up
                ii. show some kind of particle effect when you pick up the a new point, while on a streak
                iii. the streak meter should maybe grow in size, overtaking the entire level at streak of 100?
                iv. camera shake, whenever the streak is a multiple of 5
                v. something for multiples of 10?

        2. scoreboard
            a. we need to show the top 10 only, or have the ability to scroll
            b. new PB lets person type in a name, of the length of the PB, capping at 240?
            c. can see the platform wide high scores?
                i. all time
                ii. hourly
                iii. daily
                iv. weekly
                
        


    Thoughts about:
        1. Gameplay
            a. over the course of 15 minutes, the player speed will increase from start speed to cap speed (happens each time you play)
            b. player can dive for a gem, and not be able to move for several frames when they land
            c. the gameplay floor padding will start at -1, and the "spring" in with a wobble, and come to rest
                d. the padding size will slowly oscillate over its natural extents
                e. the gameplay floor will "spring" each minute
            f. there is a "joy" mode, where many gems drop, and they do not spoil until joy mode runs out
                (it lasts like 15 seconds)
                g. each time you get one, it takes longer until the next one.  The first 3 happen on the hour.
                // #IF_WITH PAYMENTS
                    h. you can pay to halve it
                    i. you can pay to double it
                #ENDIF // PAYMENTS








    
    Thoughts about:
        1. gem-behaviour
            * micro-state: if the gem is picked up within 1-2 frames of when it is spawned, then something special 
                            happens, and occurrences of the special event, are the only "player" stat that increments.
                            This situation is meant to occur, only during the happenstance, that gem(s) spawn on top of
                            the player, and are therefore immediately collected.  When this happens, you get a point.
                            The only stat in the game, is how many points you have.  Other than that, a simple timer
                            is shown, showing the hours, minutes, seconds you've been playing.  You can pause, and on
                            the pause screen are: {'tutorial_button', 'settings_button', 'reset_button', 'exit_button'}

            * spawning-patterns: mostly it should be random, but interspersed with that, should be patterns of spawning
                                 there are no pickups, there is only the one gem
            
            * progression: to facilitate player progression, there are various "on-fire" states, which are induced when
                            the player gains a point.  These are non-gameplay changes.  They are changes in how the tone
                            of the moment, is represented to the player.
                            
                            * on-fire, examples:
                                - footprints/trail
                                - aura(about-the-whole-of-ones-person)
                                - iteratively-changing-background
                                - changing colors
                                - background text, slowly changing over time
                            
                            
                            * default examples:
                                - a cool little dust cloud when you change direction more than 90
                                
                                
        




"""










