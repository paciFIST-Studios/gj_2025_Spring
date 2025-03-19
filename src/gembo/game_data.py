from enum import IntEnum
import time

from pygame.math import Vector2
from pygame.event import custom_type as PygameUserEvent

from src.engine.animation import SpriteAnimator
from src.engine.cache import EngineCache
from src.engine.ui import EColor
from src.engine.utilities import clamp

# file path for the information stored about the play session
PLAYER_STATS_FILE = 'game.data'


class AudioData:
    def __init__(self):
        pass


class EngineData:
    def __init__(self):

        # the engine cache exists to store all resources that need to be retained in the game
        self.cache = EngineCache(fn_now=self.now)

        # user defined events, max? 8?
        self.EVENT__RESPAWN_GEM = PygameUserEvent()
        self.EVENT__SPOIL_GEM = PygameUserEvent()
        self.EVENT__UNHIGHLIGHT_GEM_COUNT = PygameUserEvent()
        self.EVENT__UNHIGHLIGHT_TIME_PLAYED = PygameUserEvent()
        self.EVENT__SWITCH_GAME_MODE = PygameUserEvent()
        self.EVENT__6 = PygameUserEvent()
        self.EVENT__7 = PygameUserEvent()
        self.EVENT__8 = PygameUserEvent()



        self.audio_is_muted = False
        self.last_frame_start = time.time()
        self.frame_time_start = time.time()

        # incremented counter of the number of frames which have occurred in the game
        self.frame_count = 0
        # average fps, if queried at this moment
        self.avg_fps = 0
        # if true, will print the avg fps to the console
        self.print_avg_fps = False
        # if true, will render the avg fps to the screen
        self.render_avg_fps = True

        # update the avg fps each time this interval passes
        self._avg_fps__update_interval_s = 1
        # used to record our last "evaluation" point, so we can calculate deltas
        self._avg_fps__last_interval_ended_at_time_s = self.now()
        self._avg_fps__frame_count_at_last_interval = 0

    def now(self):
        return self.frame_time_start

    def update_fps_counter(self, i_will_only_call_this_once_per_engine_frame=False):
        """ this fn should only ever be called once per frame, inside the lowest level of the game loop,
         don't call it please. The extra param exists as a reminder"""
        if not i_will_only_call_this_once_per_engine_frame:
            return

        # since we're called every fame, we do all our calculation in this fn
        self.frame_count += 1

        time_since_last_print = self.frame_time_start - self._avg_fps__last_interval_ended_at_time_s
        if time_since_last_print > self._avg_fps__update_interval_s:

            # perform the calculation
            delta_frames_over_interval = self.frame_count - self._avg_fps__frame_count_at_last_interval
            self.avg_fps = delta_frames_over_interval / self._avg_fps__update_interval_s

            # update these, so we don't lose the "now" information, which we'll use
            # during the next interval
            self._avg_fps__last_interval_ended_at_time_s = self.now()
            self._avg_fps__frame_count_at_last_interval = self.frame_count

        if self.print_avg_fps:
            print(f'fps: {self.avg_fps}')


class FontData:
    def __init__(self):
        self.lcd = None
        self.lcd_small = None
        self.lcd_big = None
        self.dos = None
        self.estrogen = None
        self.love = None
        self.open_dyslexic = None


class GameplayData:
    """ the GameplayData class is used to represent the current state of update_modes, in EGameMode.Gameplay
    """
    def __init__(self, engine = None):
        self.engine = engine

        # a value calculated as a play session progresses.  It maxes out
        self.game_ramp_up_progression = 0

        self._last_player_input_timestamp = time.time()

        # if a gem is active, a new gem cannot be placed
        self.gem_is_active = False
        # if the cactus is active, a new cactus cannot be placed
        self.cactus_is_active = False

        self.last_gem_pickup_time = self.engine.now()

        # when a gem "spoils", it is not worth any points
        self.gem_spoilage_timeout_ms = 1000

        # this font is used when rendering text during update_modes mode
        self.current_font = None

        self.floor_line_width = 1
        self.floor_line_padding = 15
        self.floor_line_color = EColor.COOL_GREY

        # relating to getting a gem streak
        self.gem_streak_is_happening = False
        self.gem_streak_length = 0
        self.gem_streak_popup_display_at_streak_length = 3
        self.gem_streak_started_at_time = self.engine.now()
        self.gem_streak_popup_fly_in_duration_s = 1.0

        self.gem_streak_popup_is_animating = False

        # tolerable values for this range from 7 to 4, with 4 being faster; crash when 0 (div/0)
        self.gem_streak_advance_breath_box_color_every_n_frames = 5

        # relating to getting a gem anti-streak (a streak of "spoiled" gems)
        self.gem_anti_streak_is_happening = False
        self.gem_anti_streak_length = 0
        self.gem_anti_streak_started_at_time = self.engine.now()

        # relating to when the cactus should reposition
        self.cactus_position_unchanged_for_n_ripe_gems = 0
        self.cactus_respawn_every_n_gems = 5

    def increment_gem_streak(self):
        if not self.gem_streak_is_happening:
            self.gem_streak_started_at_time = self.engine.now()

        # I'm worried about the streak/anti-streak logic, so I'm just putting in an assert
        assert not self.gem_anti_streak_is_happening

        self.gem_streak_is_happening = True
        self.gem_streak_length += 1
        self.cactus_position_unchanged_for_n_ripe_gems += 1

    def end_gem_streak(self):
        self.gem_streak_is_happening = False
        statistics = self.engine.cache.lookup('statistics')
        statistics.update_longest_streak(self.gem_streak_length)
        statistics.update_streak_history(self.gem_streak_length)
        self.gem_streak_length = 0

    def increment_gem_anti_streak(self):
        if not self.gem_anti_streak_is_happening:
            self.gem_anti_streak_started_at_time = self.engine.now()

        # I'm worried about the streak/anti-streak logic, so I'm just putting in an assert
        assert not self.gem_streak_is_happening

        self.gem_anti_streak_is_happening = True
        self.gem_anti_streak_length += 1

    def end_gem_anti_streak(self):
        self.gem_anti_streak_is_happening = False
        self.gem_anti_streak_length = 0

    def show_streak_popup(self):
        return self.gem_streak_is_happening and self.gem_streak_length >= self.gem_streak_popup_display_at_streak_length

    def should_switch_to_demo_mode(self):
        timeout_s = 30
        if self.engine.now() - self._last_player_input_timestamp > timeout_s:
            return True
        return False


class CactusData:
    def __init__(self):
        self.image = None
        # self.image_offset = Vector2(-18, -65)
        self.base_image = None

        self.base_image_offset = Vector2(18, 65)

        self.position = Vector2()
        self.collision_offset = Vector2(10,20)
        # 60 feels good at low speed
        self.collision_radius_start = 60
        # 90 feels good at high speed, but w/ more knockback
        self.collision_radius_end = 85
        self.collision_radius = self.collision_radius_start

        # 2 is good at slow speed
        self.collision_knockback_force_start = 2
        # 5 is good at medium
        self.collision_knockback_force_end = 10
        self.collision_knockback_force = self.collision_knockback_force_start

        self.cactus_is_active = False


class GemData:
    """ the GemData class holds information, variables, and functions, which relate to the portrayal of the
    gem during update_modes.  This includes the images uses, sfx, position, respawn timeout, and more
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
        self.position = Vector2()

        # after being picked up, when should the next gem appear
        self.respawn_timeout_ms = 500

        # how far away can the player be, before it counts as "touching" the gem
        self.pickup_radius = 70

    # the player only scores points for picking up "ripe" gems
    def is_ripe(self):
        return self.image == self.yellow_image


class ImageData:
    def __init__(self):
        pass


class MenuData:
    class EMenuOptions(IntEnum):
        STATS_MENU = 0
        SETTINGS_MENU = 1
        INPUT_BINDINGS_MENU = 2
        ABOUT_MENU = 3
        INVOKE_QUIT_GAME = 4

        @staticmethod
        def to_string(enum):
            if enum == MenuData.EMenuOptions.STATS_MENU:
                return 'stats'
            elif enum == MenuData.EMenuOptions.SETTINGS_MENU:
                return 'settings'
            elif enum == MenuData.EMenuOptions.INPUT_BINDINGS_MENU:
                return 'input'
            elif enum == MenuData.EMenuOptions.ABOUT_MENU:
                return 'about'
            elif enum == MenuData.EMenuOptions.INVOKE_QUIT_GAME:
                return 'quit'

    def __init__(self, fn_now, change_menu_fn: callable):
        self.fn_now = fn_now
        self.change_menu_fn = change_menu_fn

        self.selected_option_last_changed_time = time.time()
        self.selected_option_timeout_s = 0.00

        self.options = [
            MenuData.EMenuOptions.STATS_MENU,
            MenuData.EMenuOptions.SETTINGS_MENU,
            MenuData.EMenuOptions.INPUT_BINDINGS_MENU,
            MenuData.EMenuOptions.ABOUT_MENU,
            MenuData.EMenuOptions.INVOKE_QUIT_GAME,
        ]

        self.selected_option = self.options[0]

    def get_selection(self):
        return self.selected_option

    def select_next(self):
        if self.selected_option is None:
            self.selected_option = MenuData.EMenuOptions.STATS_MENU

        if self.allow_selection_change():
            idx = (int(self.selected_option) + 1) % len(MenuData.EMenuOptions)
            self.selected_option = MenuData.EMenuOptions(idx)
            self.selected_option_last_changed_time = self.fn_now()

    def select_previous(self):
        if self.selected_option is None:
            self.selected_option = MenuData.EMenuOptions.STATS_MENU

        if self.allow_selection_change():
            idx = (int(self.selected_option) - 1) % len(MenuData.EMenuOptions)
            self.selected_option = MenuData.EMenuOptions(idx)
            self.selected_option_last_changed_time = self.fn_now()

    def get_menu_options(self):
        return self.options


    def allow_selection_change(self) -> bool:
        now = self.fn_now()
        timeout = self.selected_option_timeout_s
        last = self.selected_option_last_changed_time
        if now - last > timeout:
            return True
        return False




class PlayerData:
    """ the PlayerData class holds information and variables for representing the player's
    avatar, including images, position, speeds, and more
    """
    def __init__(self):
        # the "default" player avatar
        self.image = None
        # the player avatar, mirrored across the x-axis
        self.image_mirrored = None

        # if true, will render the mirrored image
        self.render_mirrored = False

        # player's current position
        self.position = Vector2()

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

        # settings for choosing animation frames
        self.sprite_animator = SpriteAnimator()
        self.walk_animation_duration_s__slowest = 1.0
        self.walk_animation_duration_s__fastest = 0.5

        # if false, renders the player as a still image
        self.is_moving = False


class SettingsData:
    class ESettingsProperties(IntEnum):
        SFX_VOLUME = 0,
        MUTE_AUDIO = 1,
        HIGHLIGHT_COLOR = 2,

        @staticmethod
        def to_string(enum):
            if enum == SettingsData.ESettingsProperties.SFX_VOLUME:
                return 'sfx'
            elif enum == SettingsData.ESettingsProperties.MUTE_AUDIO:
                return 'mute'
            elif enum == SettingsData.ESettingsProperties.HIGHLIGHT_COLOR:
                return 'color'

    def __init__(self, fn_now):
        self.fn_now = fn_now

        self.sfx_volume : float = 1.0
        self.mute_audio = False

        self.launch_bind_controls_menu = False

        self.selected_property : SettingsData.ESettingsProperties = None
        self.selected_property_last_changed_time = time.time()
        self.selected_property_timeout_s = 0.00

        self.colors = []
        self.color_idx = 0

    def get_selected_value(self, settings_property: ESettingsProperties):
        if settings_property == SettingsData.ESettingsProperties.SFX_VOLUME:
            return self.sfx_volume
        elif settings_property == SettingsData.ESettingsProperties.MUTE_AUDIO:
            return self.mute_audio
        elif settings_property == SettingsData.ESettingsProperties.HIGHLIGHT_COLOR:
            return 'yellow'

    def modify_selected_property_left(self):
        if self.selected_property == SettingsData.ESettingsProperties.SFX_VOLUME:
            # decrease volume
            self.sfx_volume = clamp(self.sfx_volume-0.1, 0, 1)
        elif self.selected_property == SettingsData.ESettingsProperties.MUTE_AUDIO:
            # toggle
            self.mute_audio = not self.mute_audio
        elif self.selected_property == SettingsData.ESettingsProperties.HIGHLIGHT_COLOR:
            pass

    def modify_selected_property_right(self):
        if self.selected_property == SettingsData.ESettingsProperties.SFX_VOLUME:
            # increase volume
            self.sfx_volume = clamp(self.sfx_volume+0.1, 0, 1)
        elif self.selected_property == SettingsData.ESettingsProperties.MUTE_AUDIO:
            # toggle
            self.mute_audio = not self.mute_audio
        elif self.selected_property == SettingsData.ESettingsProperties.HIGHLIGHT_COLOR:
            pass

    def select_settings_property(self, settings_property: ESettingsProperties):
        self.selected_property = settings_property

    def get_settings_options(self):
        """ Returns a list of tuples, where each tuple contains the stringified settings property,
        and a bool, which is true if that property is selected
        """
        result = []
        for prop in SettingsData.ESettingsProperties:
            is_selected = self.selected_property == prop
            value = self.get_selected_value(prop)
            result.append((SettingsData.ESettingsProperties.to_string(prop), is_selected, value))
        return result

    def allow_selection_change(self) -> bool:
        now = self.fn_now()
        timeout = self.selected_property_timeout_s
        last = self.selected_property_last_changed_time
        if now - last > timeout:
            return True
        return False

    def select_next(self):
        if self.selected_property is None:
            # setting this choice, allows us to move to SFX_VOLUME next
            self.selected_property = SettingsData.ESettingsProperties.HIGHLIGHT_COLOR

        if self.allow_selection_change():
            idx = (int(self.selected_property) + 1) % len(SettingsData.ESettingsProperties)
            self.selected_property = SettingsData.ESettingsProperties(idx)
            self.selected_property_last_changed_time = self.fn_now()

    def select_previous(self):
        if self.selected_property is None:
            # setting this choice, allows us to move to HIGHLIGHT_COLOR next
            self.selected_property = SettingsData.ESettingsProperties.SFX_VOLUME

        if self.allow_selection_change():
            idx = (int(self.selected_property) - 1) % len(SettingsData.ESettingsProperties)
            self.selected_property = SettingsData.ESettingsProperties(idx)
            self.selected_property_last_changed_time = self.fn_now()


class StatisticsData:
    """ the StaticsData class represents information which has accrued during all play-sessions.
     These are things like: longest streak, number of times the player has hit an N-streak, etc
     """
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

        # this many of the top streaks will be displayed
        self.display_n_top_streaks = 10

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
            self.player_stats[key] = []
        self.player_stats[key].append((time.time(), value))
        # print(f'Streak: {value}')

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
        self.highlight_color = EColor.HIGHLIGHT_YELLOW
        self.unhighlight_color = EColor.COOL_GREY
        self.highlight_colors = [
            EColor.HIGHLIGHT_YELLOW,
            EColor.PINK,
            EColor.WHITE,
            EColor.LIGHT_BLUE,
        ]

        # time played
        self.time_played_text_color = self.unhighlight_color
        self.time_played_text_position = None
        self.time_played_text_is_visible = True
        self.time_played_text_highlight_timeout_ms = 1000
        # self.time_played_fly_in_tweener = pytweening.easeInCubic

        # total points
        self.point_total_text_color = self.unhighlight_color
        self.point_total_text_position = None
        self.point_total_text_is_visible = True
        self.point_total_text_highlight_duration_ms = 1000
        # self.point_total_fly_in_tweener = pytweening.easeInCubic

    def get_highlight_color(self):
        return self.highlight_color

    def get_unhighlight_color(self):
        return self.unhighlight_color

    def highlight_time_played_text(self):
        self.time_played_text_color = self.highlight_color

    def unhighlight_time_played_text(self):
        self.time_played_text_color = self.unhighlight_color

    def highlight_total_points(self):
        self.point_total_text_color = self.highlight_color

    def unhighlight_total_points(self):
        self.point_total_text_color = self.unhighlight_color

