# python imports
from pathlib import Path
from random import randint
import time

# pygame imports
import pygame
from pygame.key import ScancodeWrapper
from pygame.locals import *

# other module imports
import pytweening

# engine imports
from src.engine.animation import SpriteAnimator, SpriteAnimation
from src.engine.utilities import clamp
from src.gembo.game_mode import EGameMode, GameModeData
from src.gembo.game_data import (AppData, AudioData, EngineData, FontData, GameplayData, GemData,
                                 ImageData,  PlayerData, StatisticsData, SettingsData, UIData)
from src.gembo.renderer import render_breathe_box
from src.engine.resource import IMAGES_TO_LOAD, AUDIO_TO_LOAD, FONTS_TO_LOAD
from src.engine.resource import load_json, load_image, load_sound, load_font
from src.engine.resource import write_json
from src.engine.time_utility import TimeConstants
from src.engine.ui import Padding, EColor
from src.engine.tween import linear, easeInOut, easeIn


# CONSTANTS ------------------------------------------------------------------------------------------------------------





# GLOBALS --------------------------------------------------------------------------------------------------------------

# aka: game resolution
APPLICATION_WINDOW_SIZE = (480, 640)




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
        self._gameplay = GameplayData(engine=self._engine)
        self._gem = GemData()
        self._player = PlayerData()

        # multi-session recording
        self._statistics = StatisticsData()

        self._settings = SettingsData(engine=self._engine)

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

        self._player.sprite_animator.play_animation('walk', loop=True)
        self._player.sprite_animator.play_animation('walk_flipped', loop=True)

        # now initialization is complete, set to demo mode for the main menu
        self._game_mode.set_mode__demo()

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
        def _escape_input(frame_input: ScancodeWrapper):
            if frame_input[K_ESCAPE]:
                return 'escape'
        def _return_input(frame_input: ScancodeWrapper):
            if frame_input[K_RETURN]:
                return 'return'

        keys = pygame.key.get_pressed()
        result = [
            _up_input(keys),
            _down_input(keys),
            _left_input(keys),
            _right_input(keys),
            _escape_input(keys),
            _return_input(keys),
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
                #self.save_gameplay_data()

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
        self._game_mode.register_callable(EGameMode.STATS_MODE, self._statistics.parse_player_history)

        self._statistics.playtime_this_session_started_at_time = time.time()

        return True


    def on_event(self, event):
        """ the engine's event fn """

        def _handle_engine_event(event):
            # handles quit event from the window
            if event.type == QUIT:
                self._running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                self._running = False
        _handle_engine_event(event)

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

        def _handle_settings_menu_event(event):
            if event.type == KEYDOWN:
                key = event.key

                # left
                if key == K_a or key == K_LEFT:
                    pass
                # right
                elif key == K_d or key == K_RIGHT:
                    pass
                # down
                elif key == K_s or key == K_DOWN:
                    self._settings.select_next()
                    pass
                # up
                elif key == K_w or key == K_UP:
                    self._settings.select_previous()
                    pass
                # enter
                elif key == K_RETURN:
                    pass
        _handle_settings_menu_event(event)

        def _handle_debug_event(event):
            if event.type == KEYDOWN:
                key = event.key

                if key == K_SPACE:
                    self.place_gem()
                elif key == K_RETURN:
                    self._game_mode.cycle()

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
        self._user_input_this_frame = self.collect_user_input()

        # record time of the last user input
        if len(self._user_input_this_frame) > 0:
            self._gameplay._last_player_input_timestamp = self._engine.now()

        if self._gameplay.should_switch_to_demo_mode():
            self._game_mode.set_mode__demo()


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

                self._player.is_moving = False
                for direction in ['move_left', 'move_right', 'move_up', 'move_down']:
                    if direction in self._user_input_this_frame:
                        self._player.is_moving = True
                        break


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
                    # calculate the progression of the player speed (0.0 -> 1.0), based on play session length
                    current_session_duration_s = time.time() - self._statistics.playtime_this_session_started_at_time
                    player_speed_progression = clamp((current_session_duration_s / self._player.reaches_top_speed_after_s), 0, 1.0)

                    # walk animation goes faster, as the player goes faster
                    # (maxes out as a small ratio of increase, over same duration)
                    def scale_walk_animation_duration(progression):
                        new_walk_duration = pygame.math.lerp(self._player.walk_animation_duration_s__slowest, self._player.walk_animation_duration_s__fastest, progression)
                        self._player.sprite_animator.update_animation_duration('walk', new_walk_duration)
                        self._player.sprite_animator.update_animation_duration('walk_flipped', new_walk_duration)
                    scale_walk_animation_duration(player_speed_progression)

                    return pygame.math.lerp(self._player.start_speed, self._player.top_speed, player_speed_progression)


                self._player.speed = get_player_speed()
                # print(f'player.speed_increase.lerp_t: {percent_complete:2.4}, player.speed: {self._player_speed:2.4}')

            update_gameplay_player_speed()

        #@self.settings_menu_only
        def update_settings_menu():
            pass

        #@self.demo_mode_only
        def update_demo_mode():
            # if the user presses a move button, then go to gameplay mode
            if len(self._user_input_this_frame) > 0:
                self._game_mode.set_mode__gameplay()


        #@self.stats_menu_only
        def update_stats_menu():
            # print(f'This is the stats menu loop!')
            pass

        # these fns all have a decorator on them, which checks the current game mode
        # before calling the function.  All future game modes will have to be in here too

        if self._game_mode.current == EGameMode.GAMEPLAY_MODE:
            update_gameplay()
        elif self._game_mode.current == EGameMode.SETTINGS_MODE:
            update_settings_menu()
        elif self._game_mode.current == EGameMode.DEMO_MODE:
            update_demo_mode()
        elif self._game_mode.current == EGameMode.STATS_MODE:
            update_stats_menu()
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

        # def render_menu_breadcrumbs():
        #     nav_color = EColor.COOL_GREY
        #     highlight_nav = False
        #     if highlight_nav:
        #         nav_color = EColor.HIGHLIGHT_YELLOW
        #
        #     # todo: slide this off the game screen when user has done input recently enough
        #     # todo: make a state machine for user input:
        #     #       playing, idle, away, each one happens after 15s, any input moves back to playing
        #
        #     nav_text = '[Enter] Change Game Mode'
        #     left_renderable_text = self._font.dos.render(nav_text, True, nav_color)
        #     nav_text_width, _ = left_renderable_text.get_size()
        #     xpos = screen_width/2 - nav_text_width/2
        #     ypos = screen_height - 50
        #     self._display_surface.blit(left_renderable_text, (xpos, ypos))
        #
        # render_menu_breadcrumbs()


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
                    if frames % 3 == 0:
                        floor_line_color = EColor.DARK_PURPLE
                    elif frames % 3 == 1:
                        floor_line_color = EColor.DARK_BLUE
                    elif frames % 3 == 2:
                        floor_line_color = EColor.DARK_GREEN

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
                """ The player image can be mirrored left or right, and the log
                """
                blit_image = self._player.image
                if self._player.render_mirrored:
                    blit_image = self._player.image_mirrored

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


        def render_settings_mode():
            """ This fn renders things related to using the menu in the settings mode

            fn render_settings_mode_box
            fn render_settings_mode_title_text
            fn render_settings_mode_options_text
            """
            def render_settings_mode_box():
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
            render_settings_mode_box()

            def render_settings_mode_title_text():
                settings_menu_title_string = 'Settings'
                settings_menu_title_renderable_text = self._font.lcd.render(settings_menu_title_string, True, EColor.HIGHLIGHT_YELLOW)

                # calculate centered on screen position
                point_total_width, _ = settings_menu_title_renderable_text.get_size()
                _, pos_y = self._ui.time_played_text_position
                pos_x = (screen_width/2) - (point_total_width/2)

                # blit
                self._display_surface.blit(settings_menu_title_renderable_text, (pos_x, pos_y))

            render_settings_mode_title_text()

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
        # scoreboard
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
                text1 = 'This one\'s for you Greg'
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
            self._running = False

        print_avg_fps = False
        print_fps_every_n_seconds = 1
        fps_last_printed = time.time()

        while self._running:

            self._engine.last_frame_start = self._engine.frame_time_start
            self._engine.frame_time_start = time.time()
            delta_time_s = self._engine.frame_time_start - self._engine.last_frame_start
            for event in pygame.event.get():
                self.on_event(event)
            self.on_update(delta_time_s)
            self.on_render()
            self._engine.frame_count += 1

            if print_avg_fps and self._engine.frame_time_start - fps_last_printed > print_fps_every_n_seconds:
                print(f'(avg)fps = {int(self._engine.frame_count / (self._engine.frame_time_start - self._app_start_time))}')
                fps_last_printed = self._engine.frame_time_start

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










