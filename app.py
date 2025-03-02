# python imports
from pathlib import Path
from random import randint
import time


# pygame imports
import pygame
from pygame.key import ScancodeWrapper
from pygame.locals import *

# engine imports
from src.engine.animation import SpriteAnimator, SpriteAnimation
from src.engine.utilities import clamp, clamp_onscreen
from src.gembo.game_mode import EGameMode, GameModeData
from src.gembo.game_data import (AppData, AudioData, EngineData, FontData, GameplayData, GemData, CactusData,
                                 ImageData, MenuData, PlayerData, StatisticsData, SettingsData, UIData)
from src.gembo.renderer import (render_breathe_box, MainMenuRenderMode, StatsMenuRenderMode, SettingsMenuRenderMode,
                                AboutMenuRenderMode, GameplayRenderMode, DemoRenderMode)
from src.engine.input import EngineInput
from src.engine.resource import IMAGES_TO_LOAD, AUDIO_TO_LOAD, FONTS_TO_LOAD, DEFAULT_INPUT_MAPPING
from src.engine.resource import load_json, load_image, load_sound, load_font
from src.engine.resource import write_json
from src.engine.time_utility import TimeConstants
from src.engine.ui import Padding, EColor
from src.engine.tween import linear, easeInOut, easeIn


# CONSTANTS ------------------------------------------------------------------------------------------------------------





# GLOBALS --------------------------------------------------------------------------------------------------------------

# aka: game resolution
APPLICATION_WINDOW_SIZE = (480, 640)
#APPLICATION_WINDOW_SIZE = (540, 720)


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

    def __init__(self):
        self.INSTANCE = self
        self.running = True
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

        self.input = EngineInput(self._engine, '')

        # resources
        self._image = ImageData()
        self._audio = AudioData()
        self._font = FontData()

        # game mode
        self._game_mode = GameModeData()

        # gameplay concepts
        self._gameplay = GameplayData(engine=self._engine)
        self._gem = GemData()
        self._player = PlayerData()
        self._cactus = CactusData()

        # multi-session recording
        self._menu = MenuData(self._engine, self.change_game_mode)
        self._statistics = StatisticsData()

        self._settings = SettingsData(engine=self._engine)

        # ui and rendering info
        self._ui = UIData()

        self._render_modes = {}

        self._user_input_this_frame = None

    def get_gameplay_data(self):
        return self._gameplay

    def get_gem_data(self):
        return self._gem

    def get_player_data(self):
        return self._player

    def get_menu_data(self):
        return self._menu


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


        p1_walk_anim_surfaces = [
            self._loaded_image_surfaces['p1_walk01'],
            self._loaded_image_surfaces['p1_walk02'],
            self._loaded_image_surfaces['p1_walk03'],
            self._loaded_image_surfaces['p1_walk04'],
            self._loaded_image_surfaces['p1_walk05'],
            self._loaded_image_surfaces['p1_walk06'],
            self._loaded_image_surfaces['p1_walk07'],
            self._loaded_image_surfaces['p1_walk08'],
        ]
        p1_walk_anim = SpriteAnimation(self._engine, p1_walk_anim_surfaces, 1.0)
        self._player.sprite_animator.register_animation('walk', p1_walk_anim)

        p1_walk_flipped_anim_surfaces = [
            pygame.transform.flip(self._loaded_image_surfaces['p1_walk01'], True, False),
            pygame.transform.flip(self._loaded_image_surfaces['p1_walk02'], True, False),
            pygame.transform.flip(self._loaded_image_surfaces['p1_walk03'], True, False),
            pygame.transform.flip(self._loaded_image_surfaces['p1_walk04'], True, False),
            pygame.transform.flip(self._loaded_image_surfaces['p1_walk05'], True, False),
            pygame.transform.flip(self._loaded_image_surfaces['p1_walk06'], True, False),
            pygame.transform.flip(self._loaded_image_surfaces['p1_walk07'], True, False),
            pygame.transform.flip(self._loaded_image_surfaces['p1_walk08'], True, False),
        ]
        p1_walk_flipped_anim = SpriteAnimation(self._engine, p1_walk_flipped_anim_surfaces, 1.0)
        self._player.sprite_animator.register_animation('walk_flipped', p1_walk_flipped_anim)

        self._cactus.image = self._loaded_image_surfaces['cactus']


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

        self.place_cactus()

        stats = load_json(self._statistics.player_stats_file_path)
        if stats:
            self._statistics.player_stats = stats

        self._statistics.parse_player_history()

        self._player.speed = self._player.start_speed

        self._player.sprite_animator.play_animation('walk', loop=True)
        self._player.sprite_animator.play_animation('walk_flipped', loop=True)


    def initialize_render_modes(self):
        engine = self._engine
        surface = self._display_surface

        # main menu
        self._render_modes[EGameMode.MENU_MODE] = MainMenuRenderMode(engine, surface, EGameMode.MENU_MODE, {
            'title_font': self._font.lcd,
            'title_text': 'menu',
            'floor_line_padding': self._gameplay.floor_line_padding,
            'floor_line_color': self._gameplay.floor_line_color,
            'menu_data': self._menu
        })

        # stats
        self._render_modes[EGameMode.STATS_MODE] = StatsMenuRenderMode(engine, surface, EGameMode.SETTINGS_MODE, {
            'title_font': self._font.lcd,
            'title_text': 'stats',
            'score_font': self._font.lcd_small,
            'floor_line_padding': self._gameplay.floor_line_padding,
            'floor_line_color': self._gameplay.floor_line_color,
        })

        # settings
        self._render_modes[EGameMode.SETTINGS_MODE] = SettingsMenuRenderMode(engine, surface, EGameMode.SETTINGS_MODE, {
            'title_font': self._font.lcd,
            'title_text': 'settings',
            'floor_line_padding': self._gameplay.floor_line_padding,
            'floor_line_color': self._gameplay.floor_line_color,
        })

        # about
        self._render_modes[EGameMode.ABOUT_MODE] = AboutMenuRenderMode(engine, surface, EGameMode.ABOUT_MODE, {
            'about_menu_font': self._font.estrogen,
            'floor_line_padding': self._gameplay.floor_line_padding,
            'floor_line_color': self._gameplay.floor_line_color,
        })

        # demo
        self._render_modes[EGameMode.DEMO_MODE] = DemoRenderMode(engine, surface, EGameMode.DEMO_MODE, {
            'title_font': self._font.lcd,
        })

        # gameplay
        self._render_modes[EGameMode.GAMEPLAY_MODE] = GameplayRenderMode(engine, surface, EGameMode.GAMEPLAY_MODE, {
            'title_font': self._font.lcd,
        })


    # Gameplay Functions -----------------------------------------------------------------------------------------------

    def gem_overlaps_with_player(self):
        if self._gameplay.gem_is_active:
            distance = self._player.position - self._gem.position
            magnitude = distance.magnitude()
            if magnitude < self._gem.pickup_radius:
                # print(f'collision: player{self._player_pos}, gem{self._gem_pos}, distance={magnitude:3.6}, collision_radius={self._gem_pickup_radius}')
                return True
        return False

    def cactus_overlaps_with_player(self):
        if self._gameplay.cactus_is_active:
            distance = self._player.position - self._cactus.position
            magnitude = distance.magnitude()
            if magnitude < self._cactus.collision_radius:
                return True
        return False

    @staticmethod
    def get_random_onscreen_coordinate(surface):
        min_x, min_y = 0, 0
        max_x, max_y = surface.get_size()
        return randint(min_x, max_x), randint(min_y, max_y)

    @staticmethod
    def get_player_onscreen_coordinate(surface):
        return None

    @staticmethod
    def get_onscreen_coordinate_with_respect_to_play(surface, min_dist_from_player, max_dist_from_player):
        pass

    @staticmethod
    def get_unreachable_onscreen_coordinate(surface):
        pass


    def collect_gem(self):
        if self._game_mode.current != EGameMode.GAMEPLAY_MODE:
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

            # kick off the animation, if it hasn't been.  This is the only play that has authority to
            if not self.player_streak_popup_is_animating() and self.player_streak_popup__is_visible():
                self.player_streak_popup__start_animation()

        # "spoiled" gems
        else:
            # if on a streak, it ends, and we calculate the stats to see if the player is on the scoreboard
            if self._gameplay.gem_streak_is_happening:
                self._gameplay.gem_streak_is_happening = False
                self._statistics.update_longest_streak(self._gameplay.gem_streak_length)
                self._statistics.update_streak_history(self._gameplay.gem_streak_length)

                # bug: saving the streak here causes the streak to be added to the play-time as minutes

            self._gameplay.gem_streak_length = 0

        if not self._engine.audio_is_muted:
            pygame.mixer.Sound.set_volume(self._gem.pickup_sound, 0.5)
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

        pos = self.get_random_onscreen_coordinate(self._display_surface)
        w, h = self._gem.image.get_size()

        pos_x = clamp_onscreen(pos[0], 0, w)
        pos_y = clamp_onscreen(pos[1], 0, h)

        self._gem.position = pygame.math.Vector2(pos_x, pos_y)

        self._gem.image = self._gem.yellow_image
        pygame.time.set_timer(self.EVENT__SPOIL_GEM, self._gameplay.gem_spoilage_timeout_ms)

        self._gameplay.gem_is_active = True
        #print(f'gem placed: {self._gem_pos}, {self.get_elapsed_time()}')

    def place_cactus(self):
        if self._cactus.cactus_is_active:
            return

        pos = self.get_random_onscreen_coordinate(self._display_surface)
        w, h = self._cactus.image.get_size()

        pos_x = clamp_onscreen(pos[0], 0, w)
        pos_y = clamp_onscreen(pos[1], 0, h)
        self._cactus.position = pygame.math.Vector2(pos_x, pos_y)
        self._cactus.cactus_is_active = True

    def collide_with_cactus(self):
        self._cactus.cactus_is_active = False

    def player_streak_popup__is_visible(self):
        display_streak_at_length = 3
        if self._gameplay.gem_streak_is_happening:
            return self._gameplay.gem_streak_length >= display_streak_at_length
        return False

    def player_streak_popup__start_animation(self):
        self._gameplay.gem_streak_popup_is_animating = True

    def player_streak_popup_is_animating(self):
        return self._gameplay.gem_streak_popup_is_animating

    #-------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def convert_enum__menu_mode_to_game_mode(value: MenuData.EMenuOptions):
        if value == MenuData.EMenuOptions.STATS_MENU:
            return EGameMode.STATS_MODE
        elif value == MenuData.EMenuOptions.SETTINGS_MENU:
            return EGameMode.SETTINGS_MODE
        elif value == MenuData.EMenuOptions.ABOUT_MENU:
            return EGameMode.ABOUT_MODE
        elif value == MenuData.EMenuOptions.INVOKE_QUIT_GAME:
            return EGameMode.INVOKE_EXIT

    def change_game_mode(self, new_mode: EGameMode):
        if new_mode == EGameMode.DEMO_MODE:
            self._game_mode.set_mode__demo()
        elif new_mode == EGameMode.GAMEPLAY_MODE:
            self._game_mode.set_mode__gameplay()
        elif new_mode == EGameMode.STATS_MODE:
            self._game_mode.set_mode__stats()
        elif new_mode == EGameMode.SETTINGS_MODE:
            self._game_mode.set_mode__settings()
        elif new_mode == EGameMode.ABOUT_MODE:
            self._game_mode.set_mode__about()
        elif new_mode == EGameMode.INVOKE_EXIT:
            self.running = not self.running

    #-------------------------------------------------------------------------------------------------------------------


    def on_init(self) -> bool:
        """ the engine's initialization fn """

        pygame.mixer.pre_init(44100, 16, 2, 4096)
        pygame.init()
        flags = pygame.HWSURFACE | pygame.DOUBLEBUF
        self._display_surface = pygame.display.set_mode(APPLICATION_WINDOW_SIZE, flags, 16)
        self.running = True

        self.initialize_images()
        self.initialize_sounds()
        self.initialize_font()
        self.initialize_gameplay()
        self.initialize_render_modes()

        # register the parse_player_history fn w/ changing to the stats menu, so it's always ready
        # by the time we need to render it
        self._game_mode.register_callable(EGameMode.STATS_MODE, self._statistics.parse_player_history)

        self._statistics.playtime_this_session_started_at_time = time.time()

        # now initialization is complete, set to demo mode for the main menu
        self.change_game_mode(EGameMode.DEMO_MODE)

        return True


    def on_event(self, event):
        """ the engine's event fn """

        def _handle_engine_event(event):
            # handles quit event from the window
            if event.type == QUIT:
                self.running = False
        _handle_engine_event(event)

        def _handle_menu_state_event(event):
            # press escape
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                current_mode = self._game_mode.current

                transition_to_main_menu = [EGameMode.GAMEPLAY_MODE, EGameMode.STATS_MODE, EGameMode.SETTINGS_MODE, EGameMode.ABOUT_MODE]
                transition_to_gameplay = [EGameMode.DEMO_MODE, EGameMode.MENU_MODE]

                if current_mode in transition_to_main_menu:
                    self._game_mode.set_mode__menu()
                elif current_mode in transition_to_gameplay:
                    self._game_mode.set_mode__gameplay()

        _handle_menu_state_event(event)


        def _handle_game_event(event):
            if event.type == self.EVENT__RESPAWN_GEM:
                self.place_gem()
            elif event.type == self.EVENT__SPOIL_GEM:
                self.spoil_gem()
            elif event.type == self.EVENT__UNHIGHLIGHT_GEM_COUNT:
                self._ui.unhighlight_total_points()
            elif event.type == self.EVENT__UNHIGHLIGHT_TIME_PLAYED:
                self._ui.unhighlight_time_played_text()
        _handle_game_event(event)

        # def _handle_settings_menu_event(event):
        #     if event.type == KEYDOWN:
        #         key = event.key
        #
        #         # left
        #         if key == K_a or key == K_LEFT:
        #             pass
        #         # right
        #         elif key == K_d or key == K_RIGHT:
        #             pass
        #         # down
        #         elif key == K_s or key == K_DOWN:
        #             #self._settings.select_next()
        #             pass
        #         # up
        #         elif key == K_w or key == K_UP:
        #             #self._settings.select_previous()
        #             pass
        #         # enter
        #         elif key == K_RETURN:
        #             pass
        # _handle_settings_menu_event(event)

        def _handle_debug_event(event):
            if event.type == KEYDOWN:
                key = event.key

                if key == K_SPACE:
                    self.place_gem()
                elif key == K_RETURN:
                    pass

                # elif key == K_KP_PLUS:
                #     self._gameplay.gem_streak_advance_breath_box_color_every_n_frames += 1
                #     print(f'advance color every {self._gameplay.gem_streak_advance_breath_box_color_every_n_frames} frames')
                # elif key == K_KP_MINUS:
                #     self._gameplay.gem_streak_advance_breath_box_color_every_n_frames -= 1
                #     print(f'advance color every {self._gameplay.gem_streak_advance_breath_box_color_every_n_frames} frames')

                elif key == K_KP_PLUS:
                    self._gameplay.increment_gem_streak()

        _handle_debug_event(event)
    # on_event


    def on_update(self, delta_time_s):
        """ the engine's update fn """
        self.input.collect_user_actions()
        actions_this_frame = self.input.get_actions_this_frame()

        # record time of the last user input
        if len(actions_this_frame) > 0:
            self._gameplay._last_player_input_timestamp = self._engine.now()

        # auto switch to demo mode when idle for too long
        if self._gameplay.should_switch_to_demo_mode():
            self._game_mode.set_mode__demo()


        #---------------------------------------------------------------------------------------------------------------
        # Gameplay Update
        #---------------------------------------------------------------------------------------------------------------

        def update_gameplay():
            def is_player_moving(player_input_actions: list):
                """ the player is_moving flag is used when choosing the next animation frame """
                for player_action in player_input_actions:
                    if player_action.name in ['move_left', 'move_right', 'move_up', 'move_down']:
                        return True
                return False

            self._player.is_moving = is_player_moving(actions_this_frame)


            # collision update -----------------------------------------------------------------------------------------
            #
            # This code manages all collision checking.  Right now, the uses are: keeping the player's
            # position clamped on screen, checking for an overlap between the player and the gem

            def check_gameplay_collision__level_extents():
                """ checks player collision with the map, and keeps the player position inside

                    NOTE: This is also the only place where player movement is applied to player position
                """
                LEFT_COLLISION = 0
                UP_COLLISION = 0

                w, h = self._display_surface.get_size()
                RIGHT_COLLISION = w
                DOWN_COLLISION = h

                for action in actions_this_frame:
                    if action.name == 'move_left':
                        displacement = -1 * self._player.speed * delta_time_s
                        if self._player.position[0] + displacement > LEFT_COLLISION:
                            self._player.position[0] += displacement
                            self._player.render_mirrored = True

                    if action.name == 'move_right':
                        displacement = 1 * self._player.speed * delta_time_s
                        sprite_width = self._player.image.get_width()
                        if self._player.position[0] + displacement + sprite_width < RIGHT_COLLISION:
                            self._player.position[0] += displacement
                            self._player.render_mirrored = False

                    if action.name == 'move_up':
                        displacement = -1 * self._player.speed * delta_time_s
                        if self._player.position[1] + displacement > UP_COLLISION:
                            self._player.position[1] += displacement

                    if action.name == 'move_down':
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

            def check_gameplay_collision__cactus():
                if self.cactus_overlaps_with_player():
                    self.collide_with_cactus()
            check_gameplay_collision__cactus()

            # end collision update -------------------------------------------------------------------------------------


            # Player update --------------------------------------------------------------------------------------------

            def update_gameplay_player_speed():
                def calculate_player_speed_update() -> float:
                    """ player speed increases over the course of 5 minutes """
                    # calculate the progression of the player speed (0.0 -> 1.0), based on play session length
                    current_session_duration_s = time.time() - self._statistics.playtime_this_session_started_at_time
                    player_speed_progression = clamp((current_session_duration_s / self._player.reaches_top_speed_after_s), 0, 1.0)

                    # walk animation goes faster, as the player goes faster
                    # (maxes out as a small ratio of increase, over same duration)
                    def scale_walk_animation_duration(progression):
                        """ the animation increases in speed over the same interval of time, as the player's movement """
                        new_walk_duration = pygame.math.lerp(self._player.walk_animation_duration_s__slowest, self._player.walk_animation_duration_s__fastest, progression)
                        self._player.sprite_animator.update_animation_duration('walk', new_walk_duration)
                        self._player.sprite_animator.update_animation_duration('walk_flipped', new_walk_duration)
                    scale_walk_animation_duration(player_speed_progression)

                    return pygame.math.lerp(self._player.start_speed, self._player.top_speed, player_speed_progression)

                self._player.speed = calculate_player_speed_update()
                # print(f'player.speed_increase.lerp_t: {percent_complete:2.4}, player.speed: {self._player_speed:2.4}')

            update_gameplay_player_speed()

        #---------------------------------------------------------------------------------------------------------------
        # MenuMode Update
        #---------------------------------------------------------------------------------------------------------------

        def update_menu_mode():
            for action in actions_this_frame:
                # there's some bug which was causing 'return' to count as a match for 'escape'--I don't know how or why
                # to solve it, just skip over 'escape' if we find it here.  Toggling the menu is handled at the engine
                # level, because it's common to all game modes
                if action.name == 'escape':
                    continue
                if action.is_starting:
                    if action.name == 'move_up':
                        self._menu.select_previous()
                    elif action.name == 'move_down':
                        self._menu.select_next()
                    elif action.name == 'return':
                        selected_menu_mode = self._menu.get_selection()
                        new_game_mode = self.convert_enum__menu_mode_to_game_mode(selected_menu_mode)
                        self.change_game_mode(new_game_mode)


        #---------------------------------------------------------------------------------------------------------------
        # SettingsMode Update
        #---------------------------------------------------------------------------------------------------------------

        #@self.settings_menu_only
        def update_settings_mode():
            for action in actions_this_frame:
                if action.name == 'escape':
                    continue
                if action.is_starting:
                    if action.name == 'move_up':
                        self._settings.select_previous()
                    elif action.name == 'move_down':
                        self._settings.select_next()
                    # elif action.name == 'return':
                    #     selected_settings_mode = self._settings.get_selection()

        #---------------------------------------------------------------------------------------------------------------
        # DemoMode Update
        #---------------------------------------------------------------------------------------------------------------

        #@self.demo_mode_only
        def update_demo_mode():
            # auto transition from demo mode to gameplay on user input
            if len(actions_this_frame) > 0:
                self.change_game_mode(EGameMode.GAMEPLAY_MODE)

            # update position of player.image on demo mode
                # yellow gem
                    # player moves to yellow gem
                    # player picks up yellow gem
                    # player gets point

                # spoilage
                    # player moves to yellow gem
                    # yellow gem becomes blue gem
                    # player picks up blue gem
                    # (player does not get point)

        #---------------------------------------------------------------------------------------------------------------
        # StatsMode Update
        #---------------------------------------------------------------------------------------------------------------

        #@self.stats_menu_only
        def update_stats_mode():
            # user_input = get_user_input()
            # if up/down: -> cycle through stats
            pass


        if self._game_mode.current == EGameMode.GAMEPLAY_MODE:
            update_gameplay()
        elif self._game_mode.current == EGameMode.MENU_MODE:
            update_menu_mode()
        elif self._game_mode.current == EGameMode.SETTINGS_MODE:
            update_settings_mode()
        elif self._game_mode.current == EGameMode.DEMO_MODE:
            update_demo_mode()
        elif self._game_mode.current == EGameMode.STATS_MODE:
            update_stats_mode()
    # on_update

    # On Render --------------------------------------------------------------------------------------------------------
    #
    #   This rendering fn contains a suite of rendering fns used for all aspects of this game
    #   mostly, a single render function exists for each game mode, it contains as many interior
    #   fns as it needs

    def on_render(self):
        # clear the screen
        self._display_surface.fill(EColor.BLACK)

        screen_width, screen_height = self._display_surface.get_size()

        def render_debug_info():
            if self._engine.render_avg_fps:
                message = f'fps: {self._engine.avg_fps}'
                renderable_text = self._font.open_dyslexic.render(message, True, EColor.COOL_GREY)
                text_width, text_height = renderable_text.get_size()
                x_pos = screen_width - text_width - 10
                y_pos = screen_height - text_height - 10
                self._display_surface.blit(renderable_text, (x_pos, y_pos))
        render_debug_info()


        def render_menu_floor_box():
            """ renders the breath box in menu mode """
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


        def render_title_text(title_text: str):
            """ renders the given string as a title, at the top of the screen """

            renderable_text = self._font.lcd.render(title_text, True, EColor.HIGHLIGHT_YELLOW)

            # calculate centered on screen position
            total_width, _ = renderable_text.get_size()
            _, pos_y = self._ui.time_played_text_position
            pos_x = (screen_width/2) - (total_width/2)

            # blit
            self._display_surface.blit(renderable_text, (pos_x, pos_y))


        def render_active_gameplay():
            """ This fn renders things related to playing the game in gameplay mode.

            fn: render_gameplay_floor: a breathe box, that can change color according to some logic

            fn: render_gameplay_timer: a timer which shows to cumulative playtime since the save file started

            fn: render_gameplay_points: a counter which shows the number of yellow gems which have been collected

            fn: render_current_streak_popup: if the player is on a streak, this popup displays that information

            fn: render_player_image: the image of the player, within the game

            fn: render_gem_image: the image of the gem which is "in play"
            """

            def render_gameplay_floor():
                """ like render_menu_floor, but it responds to the player streak as part of the gameplay experience"""
                # line positions
                left = 0 + self._gameplay.floor_line_padding
                right = screen_width - self._gameplay.floor_line_padding
                top = 0 + self._gameplay.floor_line_padding
                bottom = screen_height - self._gameplay.floor_line_padding

                floor_line_color = self._gameplay.floor_line_color
                floor_line_width = self._gameplay.floor_line_width

                if self._gameplay.show_streak_popup():
                    nth_frame = self._gameplay.gem_streak_advance_breath_box_color_every_n_frames
                    frames = int(self._engine.frame_count / nth_frame)
                    theme = [EColor.DARK_PURPLE, EColor.DARK_BLUE, EColor.DARK_GREEN]

                    if frames % 3 == 0:
                        floor_line_color = theme[0]
                    elif frames % 3 == 1:
                        floor_line_color = theme[1]
                    elif frames % 3 == 2:
                        floor_line_color = theme[2]

                    floor_line_width = self._gameplay.gem_streak_length

                render_breathe_box(
                    surface=self._display_surface,
                    padding=Padding(left, top, right, bottom),
                    color=floor_line_color,
                    width=floor_line_width,
                    is_animated=True,
                    breathe_ratio=5.0
                )
            render_gameplay_floor()


            def render_gameplay_timer():
                """ shows total playtime since the file was reset """
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
                """ shows the number of 'ripe' gems collected """
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
                """ shows a counter of the player's current 'ripe' gem streak """
                if self.player_streak_popup__is_visible():
                    streak = self._gameplay.gem_streak_length
                    streak_string = f'x{streak}'
                    streak_renderable_text = self._font.lcd_big.render(streak_string, True, EColor.HIGHLIGHT_YELLOW)

                    text_width, _ = streak_renderable_text.get_size()
                    pos_x = (screen_width/2)-(text_width/2)

                    final_pos_y = screen_height - 90
                    pos_y = final_pos_y

                    if self.player_streak_popup_is_animating():
                        now = self._engine.now()
                        elapsed = now - self._gameplay.gem_streak_started_at_time
                        duration_s = self._gameplay.gem_streak_popup_fly_in_duration_s
                        t_progress = clamp(elapsed/duration_s, 0, 1)
                        if t_progress == 1.0:
                            self._gameplay.gem_streak_popup_is_animating = False
                        start_pos_y = screen_height + 90
                        pos_y = pygame.math.lerp(start_pos_y, final_pos_y, t_progress)

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
            render_current_streak_popup()

            def render_player_image():
                """ The player image can be mirrored left or right, and anima
                """
                # handle "standing" case
                blit_image = self._player.image
                if self._player.render_mirrored:
                    blit_image = self._player.image_mirrored

                # handle "moving" case
                if self._player.is_moving:
                    if self._player.render_mirrored:
                        blit_image = self._player.sprite_animator.get_animation_frame('walk_flipped')
                    else:
                        blit_image = self._player.sprite_animator.get_animation_frame('walk')

                self._display_surface.blit(blit_image, self._player.position)
            render_player_image()

            def render_gem_image():
                if self._gameplay.gem_is_active:
                    self._display_surface.blit(self._gem.image, self._gem.position)
            render_gem_image()

        def render_menu_mode():
            """  """
            render_menu_floor_box()
            render_title_text('Menu')

            def render_menu_mode_options_text():
                options_enums = self._menu.get_menu_options()
                options_strs = [MenuData.EMenuOptions.to_string(x) for x in options_enums]
                options = zip(options_enums, options_strs)

                y_pos = 90
                for option_enum, option_str in options:
                    y_pos += 60
                    color = EColor.COOL_GREY
                    if option_enum == self._menu.selected_option:
                        color = EColor.HIGHLIGHT_YELLOW
                    renderable_text = self._font.lcd.render(option_str, True, color)
                    text_width, _ = renderable_text.get_size()
                    x_pos = (screen_width/2) - 90
                    self._display_surface.blit(renderable_text, (x_pos, y_pos))
            render_menu_mode_options_text()


        def render_settings_mode():
            """ This fn renders things related to using the menu in the settings mode

            fn render_settings_mode_title_text
            fn render_settings_mode_options_text
            """
            render_menu_floor_box()
            render_title_text('Settings')

            def render_settings_mode_options_text():
                options = self._settings.get_settings_options()

                x_pos, y_pos = 60, 90
                for settings_property, is_selected in options:
                    string = settings_property
                    color = EColor.HIGHLIGHT_YELLOW if is_selected else EColor.COOL_GREY
                    text = self._font.lcd_small.render(string, True, color)
                    self._display_surface.blit(text, (x_pos, y_pos))
                    y_pos += 60

            render_settings_mode_options_text()


        #@self.demo_mode_only
        def render_demo_mode():
            # render_menu_floor_box()

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
        # scoreboard
        def render_stats_menu():
            render_menu_floor_box()
            render_title_text('Stats')

            def render_stats_menu_stats():
                assert self._statistics.streak_counts
                streaks = list(
                    reversed(
                        sorted(
                            [(x, y) for x, y in self._statistics.streak_counts.items()]
                        )
                    )
                )

                streaks_to_display = streaks[:self._statistics.display_n_top_streaks]

                y_pos = 90

                text = f'Streak        Count'
                renderable_text = self._font.lcd_small.render(text, True, EColor.COOL_GREY)
                text_width, _ = renderable_text.get_size()
                x_pos = (screen_width/2) - (text_width/2)
                self._display_surface.blit(renderable_text, (x_pos, y_pos))

                y_pos += 30
                for streak, count in streaks_to_display:
                    y_pos += 30

                    streak_text = f'{streak}'
                    streak_renderable_text = self._font.lcd_small.render(streak_text, True, EColor.COOL_GREY)
                    streak_text_width, _ = renderable_text.get_size()
                    x_pos = (screen_width/2) - (streak_text_width/2) + 30
                    self._display_surface.blit(streak_renderable_text, (x_pos, y_pos))

                    count_text = f'{count}'
                    count_renderable_text = self._font.lcd_small.render(count_text, True, EColor.COOL_GREY)
                    count_text_width, _ = renderable_text.get_size()
                    x_pos = (screen_width/1) - (count_text_width/2)
                    self._display_surface.blit(count_renderable_text, (x_pos, y_pos))

            render_stats_menu_stats()

        def render_about_menu():
            render_menu_floor_box()

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
                text1 = 'This one\'s for you Greg'
                # text1 = 'For my friend Greg'
                # text2 = 'who wanted to make small games.'

                renderable_text1 = self._font.open_dyslexic.render(text1, True, EColor.COOL_GREY)
                # renderable_text2 = self._font.open_dyslexic.render(text2, True, EColor.COOL_GREY)

                renderable_texts = [
                    renderable_text1,
                #    renderable_text2
                ]

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

        if self._game_mode.current == EGameMode.MENU_MODE:
            self._render_modes[self._game_mode.current].render()


        if self._game_mode.current == EGameMode.GAMEPLAY_MODE:
            render_active_gameplay()
        elif self._game_mode.current == EGameMode.SETTINGS_MODE:
            render_settings_mode()
        elif self._game_mode.current == EGameMode.DEMO_MODE:
            render_demo_mode()
        elif self._game_mode.current == EGameMode.STATS_MODE:
            render_stats_menu()
        elif self._game_mode.current == EGameMode.ABOUT_MODE:
            render_about_menu()

        pygame.display.flip()
    # on_render


    def save_gameplay_data(self):
        self._statistics.player_stats['total_play_time'] = self.get_total_playtime_s()
        write_json(self._statistics.player_stats_file_path, self._statistics.player_stats)

    def cleanup_gameplay(self):
        self.save_gameplay_data()

    def on_cleanup(self):
        """ this fn is called when shutting down the game """
        self.cleanup_gameplay()
        pygame.quit()



    def on_execute(self):
        """ this fn runs the game engine """
        if not self.on_init():
            self.running = False

        self._engine.time_slept = 0

        while self.running:
            self._engine.last_frame_start = self._engine.frame_time_start
            self._engine.frame_time_start = time.time()
            delta_time_s = self._engine.frame_time_start - self._engine.last_frame_start
            for event in pygame.event.get():
                self.on_event(event)
            self.on_update(delta_time_s)
            self.on_render()

            self._engine.update_fps_counter(i_will_only_call_this_once_per_engine_frame=True)

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
    todo:
    
        make tweening work for animating fly in of gem streak popup
        make tweaning work for "jiggle" animation of selected settings value
        make it so you can enter 5 characters of text when you get a high score
            those initials should be displayed on the stats page
            those initials should scrolls when highlighted

                    




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


        2. design
            there should be a mode where you try to collect "ripe" gems as fast as possible (default)
            there should also be a mode where you only collect blue gems, and when you play this way, "ripe" gems spawn
                as barriers, and "spoiled" gems spawn in collectable places.  If you get enough "spoiled" gems, 
                something happens
                When you're on a "blue streak", if a gem spawns on you, it ends the streak, so maybe don't allow those
                    to spawn within a certain radius of the player






    
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










