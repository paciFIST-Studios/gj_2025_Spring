# python imports
from math import sin
import time

# pygame imports
from pygame import Surface
from pygame.draw import (line as pygame_draw_line,
                         circle as pygame_draw_circle)

# engine imports
from src.gembo.game_mode import EGameMode
from src.gembo.game_data import MenuData
from src.engine.ui import Padding, EColor




class RenderMode:
    def __init__(self, engine, render_surface: Surface, mode: EGameMode, render_data: dict):
        self.engine = engine
        self.render_surface = render_surface
        self.game_mode = mode
        self.render_data = render_data

        w, h = self.render_surface.get_size()
        self.surface_width = w
        self.surface_height = h


    def value_or_default(self, key, default = None):
        if key in self.render_data:
            return self.render_data[key]
        return default


    def render(self):
        """ all render modes need to override this fn with their own version """
        pass


# MenuBase
class MenuRenderModeBase(RenderMode):
    def __init__(self, engine, surface: Surface, mode: EGameMode, render_data: dict):
        super().__init__(engine, surface, mode, render_data)

        self.title_font = self.value_or_default('title_font', None)
        self.time_played_text_position = self.value_or_default('time_played_text_position', (0, 0))

    def render_menu_floor_box(self):
        line_padding = self.value_or_default('line_padding', 10)
        color = self.value_or_default('color', EColor.COOL_GREY)

        left = 0 + line_padding
        right = self.surface_width - line_padding
        top = 0 + line_padding
        bottom = self.surface_height - line_padding

        render_breathe_box(self.render_surface, Padding(left, top, right, bottom), color, True)

    def render_title_text(self, title_text):
        """ renders the given string as a title, at the top of the screen """

        renderable_text = self.title_font.render(title_text, True, EColor.HIGHLIGHT_YELLOW)

        # calculate centered on screen position
        total_width, _ = renderable_text.get_size()
        _, pos_y = self.time_played_text_position
        pos_x = (self.surface_width/2) - (total_width/2)

        # blit
        self.render_surface.blit(renderable_text, (pos_x, pos_y))


# main menu
class MainMenuRenderMode(MenuRenderModeBase):
    def __init__(self, engine, surface: Surface, mode: EGameMode, render_dict: dict):
        super().__init__(engine, surface, mode, render_dict)
        self.menu = self.value_or_default('menu_data', [])


    def render(self):
        """  """
        self.render_menu_floor_box()
        self.render_title_text('Menu')
        self.render_menu_mode_options_text()



    def render_menu_mode_options_text(self):
        options_enums = self.menu.get_menu_options()
        options_strs = [MenuData.EMenuOptions.to_string(x) for x in options_enums]
        options = zip(options_enums, options_strs)

        y_pos = 90
        for option_enum, option_str in options:
            y_pos += 60
            color = EColor.COOL_GREY
            if option_enum == self.menu.selected_option:
                color = EColor.HIGHLIGHT_YELLOW
            renderable_text = self.title_font.render(option_str, True, color)
            text_width, _ = renderable_text.get_size()
            x_pos = (self.surface_width/2) - 90
            self.render_surface.blit(renderable_text, (x_pos, y_pos))


# stats
class StatsMenuRenderMode(MenuRenderModeBase):
    def __init__(self, engine, surface: Surface, mode: EGameMode, render_dict: dict):
        super().__init__(engine, surface, mode, render_dict)

        self.score_font = self.value_or_default('score_font')
        self._statistics = self.value_or_default('statistics')


    def render(self):
        self.render_menu_floor_box()
        self.render_title_text('Stats')
        self.render_stats_menu_stats()

    def render_stats_menu_stats(self):
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
        renderable_text = self.score_font.render(text, True, EColor.COOL_GREY)
        text_width, _ = renderable_text.get_size()
        x_pos = (self.surface_width / 2) - (text_width / 2)
        self.render_surface.blit(renderable_text, (x_pos, y_pos))

        y_pos += 30
        for streak, count in streaks_to_display:
            y_pos += 30

            streak_text = f'{streak}'
            streak_renderable_text = self.score_font.render(streak_text, True, EColor.COOL_GREY)
            streak_text_width, _ = renderable_text.get_size()
            x_pos = (self.surface_width / 2) - (streak_text_width / 2) + 30
            self.render_surface.blit(streak_renderable_text, (x_pos, y_pos))

            count_text = f'{count}'
            count_renderable_text = self.score_font.render(count_text, True, EColor.COOL_GREY)
            count_text_width, _ = renderable_text.get_size()
            x_pos = (self.surface_width / 1) - (count_text_width / 2)
            self.render_surface.blit(count_renderable_text, (x_pos, y_pos))


# settings
class SettingsMenuRenderMode(MenuRenderModeBase):
    def __init__(self, engine, surface: Surface, mode: EGameMode, render_dict: dict):
        super().__init__(engine, surface, mode, render_dict)
        self.settings = self.value_or_default('settings')
        self.selection_font = self.value_or_default('selection_font')


    def render(self):
        self.render_menu_floor_box()
        self.render_title_text('Settings')
        self.render_settings_mode_options_text()

    def render_settings_mode_options_text(self):
        options = self.settings.get_settings_options()

        x_pos, y_pos = 60, 90
        for settings_property, is_selected in options:
            string = settings_property
            color = EColor.HIGHLIGHT_YELLOW if is_selected else EColor.COOL_GREY
            text = self.selection_font.render(string, True, color)
            self.render_surface.blit(text, (x_pos, y_pos))
            y_pos += 60


# about
class AboutMenuRenderMode(MenuRenderModeBase):
    def __init__(self, engine, surface: Surface, mode: EGameMode, render_dict: dict):
        super().__init__(engine, surface, mode, render_dict)
        self.about_menu_font = self.value_or_default('about_menu_font')
        self.homily_font = self.value_or_default('homily_font')

    def render(self):
        self.render_menu_floor_box()
        self.render_ellie_loves_games()
        self.render_homily()

    def render_ellie_loves_games(self):
        ellie = 'ellie'
        loves = 'love\'s'
        games = 'games'

        ellie_renderable_text = self.about_menu_font.render(ellie, True, EColor.WHITE)
        loves_renderable_text = self.about_menu_font.render(loves, True, EColor.PINK)
        games_renderable_text = self.about_menu_font.render(games, True, EColor.LIGHT_BLUE)

        renderable_texts = [ellie_renderable_text, loves_renderable_text, games_renderable_text]

        y_pos = 90
        for renderable_text in renderable_texts:
            text_width, _ = renderable_text.get_size()
            x_pos = (self.surface_width / 2) - (text_width / 2)
            y_pos += 40
            self.render_surface.blit(renderable_text, (x_pos, y_pos))


    def render_homily(self):
        text1 = 'This one\'s for you Greg'
        # text1 = 'For my friend Greg'
        # text2 = 'who wanted to make small games.'

        renderable_text1 = self.homily_font.render(text1, True, EColor.COOL_GREY)
        # renderable_text2 = self.homily_font.render(text2, True, EColor.COOL_GREY)

        renderable_texts = [
            renderable_text1,
            #    renderable_text2
        ]

        y_pos = self.surface_height - 240
        for renderable_text in renderable_texts:
            text_width, _ = renderable_text.get_size()
            x_pos = (self.surface_width / 2) - (text_width / 2)
            y_pos += 30
            self.render_surface.blit(renderable_text, (x_pos, y_pos))


# demo
class DemoRenderMode(MenuRenderModeBase):
    def __init__(self, engine, surface: Surface, mode: EGameMode, render_dict: dict):
        super().__init__(engine, surface, mode, render_dict)
        self.demo_title_font = self.value_or_default('demo_title_font')
        self.window_title = self.value_or_default('window_title')

    def render(self):
        self.render_menu_floor_box()
        self.render_demo_title()

    def render_demo_title(self):
        demo_mode_title_string = self.window_title
        demo_mode_title_renderable_text = self.demo_title_font.render(demo_mode_title_string, True,
                                                                    EColor.HIGHLIGHT_YELLOW)

        # calculate centered on screen position
        text_width, _ = demo_mode_title_renderable_text.get_size()

        pos_y = 120
        pos_x = (self.surface_width / 2) - (text_width / 2)

        # blit
        self.render_surface.blit(demo_mode_title_renderable_text, (pos_x, pos_y))


# gameplay
class GameplayRenderMode(RenderMode):
    def __init__(self, engine, surface: Surface, mode: EGameMode, render_dict: dict):
        super().__init__(engine, surface, mode, render_dict)

    # def render_active_gameplay(self):
    #     """ This fn renders things related to playing the game in gameplay mode.
    #
    #     fn: render_gameplay_floor: a breathe box, that can change color according to some logic
    #
    #     fn: render_gameplay_timer: a timer which shows to cumulative playtime since the save file started
    #
    #     fn: render_gameplay_points: a counter which shows the number of yellow gems which have been collected
    #
    #     fn: render_current_streak_popup: if the player is on a streak, this popup displays that information
    #
    #     fn: render_player_image: the image of the player, within the game
    #
    #     fn: render_gem_image: the image of the gem which is "in play"
    #     """
    #
    #     screen_width, screen_height = self.render_surface.get_size()
    #
    #     def render_gameplay_floor():
    #         """ like render_menu_floor, but it responds to the player streak as part of the gameplay experience"""
    #         # line positions
    #         left = 0 + self._gameplay.floor_line_padding
    #         right = screen_width - self._gameplay.floor_line_padding
    #         top = 0 + self._gameplay.floor_line_padding
    #         bottom = screen_height - self._gameplay.floor_line_padding
    #
    #         floor_line_color = self._gameplay.floor_line_color
    #         floor_line_width = self._gameplay.floor_line_width
    #
    #         if self._gameplay.show_streak_popup():
    #             nth_frame = self._gameplay.gem_streak_advance_breath_box_color_every_n_frames
    #             frames = int(self._engine.frame_count / nth_frame)
    #             theme = [EColor.DARK_PURPLE, EColor.DARK_BLUE, EColor.DARK_GREEN]
    #
    #             if frames % 3 == 0:
    #                 floor_line_color = theme[0]
    #             elif frames % 3 == 1:
    #                 floor_line_color = theme[1]
    #             elif frames % 3 == 2:
    #                 floor_line_color = theme[2]
    #
    #             floor_line_width = self._gameplay.gem_streak_length
    #
    #         render_breathe_box(
    #             surface=self._display_surface,
    #             padding=Padding(left, top, right, bottom),
    #             color=floor_line_color,
    #             width=floor_line_width,
    #             is_animated=True,
    #             breathe_ratio=5.0
    #         )
    #
    #     render_gameplay_floor()
    #
    #     def render_gameplay_timer():
    #         """ shows total playtime since the file was reset """
    #         if self._ui.time_played_text_is_visible:
    #             playtime_s = self.get_total_playtime_s()
    #
    #             # assemble the timer string
    #             time_values = TimeConstants.slice_seconds_into_time_groups(playtime_s)
    #             timer_string = ''
    #             for key, value in time_values.items():
    #                 abbreviation = TimeConstants.GET_TIME_UNITS_ABBREVIATION[key]
    #                 timer_string += f'{int(value):02}{abbreviation} '
    #
    #             # timer blinks yellow on every minute
    #             if '00s' in timer_string:
    #                 self._ui.highlight_time_played_text()
    #                 pygame.time.set_timer(self.EVENT__UNHIGHLIGHT_TIME_PLAYED,
    #                                       self._ui.time_played_text_highlight_timeout_ms)
    #
    #             else:
    #                 self._ui.unhighlight_time_played_text()
    #
    #             # calculate centered-on-screen position for the gameplay timer
    #             gameplay_timer_renderable_text = self._gameplay.font.render(timer_string.strip(), True,
    #                                                                         self._ui.time_played_text_color)
    #             gameplay_timer_width, _ = gameplay_timer_renderable_text.get_size()
    #             _, pos_y = self._ui.time_played_text_position
    #             pos_x = (screen_width / 2) - (gameplay_timer_width / 2)
    #
    #             # blit
    #             self._display_surface.blit(gameplay_timer_renderable_text, (pos_x, pos_y))
    #
    #     render_gameplay_timer()
    #
    #     def render_gameplay_points():
    #         """ shows the number of 'ripe' gems collected """
    #         if self._ui.point_total_text_is_visible:
    #             total = self._statistics.player_stats['total_points']
    #
    #             # build points string
    #             point_total_string = f'{total}'
    #             point_total_renderable_text = self._gameplay.font.render(point_total_string, True,
    #                                                                      self._ui.point_total_text_color)
    #
    #             # calculate centered on screen position
    #             point_total_width, _ = point_total_renderable_text.get_size()
    #             _, pos_y = self._ui.point_total_text_position
    #             pos_x = (screen_width / 2) - (point_total_width / 2)
    #
    #             # blit
    #             self._display_surface.blit(point_total_renderable_text, (pos_x, pos_y))
    #
    #     render_gameplay_points()
    #
    #     def render_current_streak_popup():
    #         """ shows a counter of the player's current 'ripe' gem streak """
    #         if self.player_streak_popup__is_visible():
    #             streak = self._gameplay.gem_streak_length
    #             streak_string = f'x{streak}'
    #             streak_renderable_text = self._font.lcd_big.render(streak_string, True, EColor.HIGHLIGHT_YELLOW)
    #
    #             text_width, _ = streak_renderable_text.get_size()
    #             pos_x = (screen_width / 2) - (text_width / 2)
    #
    #             final_pos_y = screen_height - 90
    #             pos_y = final_pos_y
    #
    #             if self.player_streak_popup_is_animating():
    #                 now = self._engine.now()
    #                 elapsed = now - self._gameplay.gem_streak_started_at_time
    #                 duration_s = self._gameplay.gem_streak_popup_fly_in_duration_s
    #                 t_progress = clamp(elapsed / duration_s, 0, 1)
    #                 if t_progress == 1.0:
    #                     self._gameplay.gem_streak_popup_is_animating = False
    #                 start_pos_y = screen_height + 90
    #                 pos_y = pygame.math.lerp(start_pos_y, final_pos_y, t_progress)
    #
    #             self._display_surface.blit(streak_renderable_text, (pos_x, pos_y))
    #
    #             """ When the player starts a streak, they have 1 point.  We will hide the current_streak_popup,
    #             until the player has 3 points.  Then the popup should:
    #                 * fly in - easing
    #                 * show the number of the current streak
    #                 * look visually engaging
    #                 * play an extra sound
    #                 * play a final "fireworks" when the streak ends
    #                 * fly out - easing
    #             """
    #
    #     render_current_streak_popup()
    #
    #     def render_player_image():
    #         """ The player image can be mirrored left or right, and anima
    #         """
    #         # handle "standing" case
    #         blit_image = self._player.image
    #         if self._player.render_mirrored:
    #             blit_image = self._player.image_mirrored
    #
    #         # handle "moving" case
    #         if self._player.is_moving:
    #             if self._player.render_mirrored:
    #                 blit_image = self._player.sprite_animator.get_animation_frame('walk_flipped')
    #             else:
    #                 blit_image = self._player.sprite_animator.get_animation_frame('walk')
    #
    #         self._display_surface.blit(blit_image, self._player.position)
    #
    #     render_player_image()
    #
    #     def render_gem_image():
    #         if self._gameplay.gem_is_active:
    #             self._display_surface.blit(self._gem.image, self._gem.position)
    #
    #     render_gem_image()


def get_scaled_sin(x):
    return (sin(x ) /2) + 0.5


def render_breathe_box(surface: Surface, padding: Padding, color: EColor, width: int = 1, is_animated=True, breathe_ratio: float = 20):
    """ The "breathe box" is a box that rhythmically contracts, according to the value 'breathe_ratio'.  This value could range (20, 3)
    """
    # don't delete this, it isn't using the surface from the outer scope
    surface_width, surface_height = surface.get_size()

    # line positions
    left = padding.left
    right = padding.right
    top = padding.top
    bottom = padding.bottom

    if is_animated:
        # this animation causes the lines to contract (is this cubic?)
        time_now = time.time()
        scaled_sin = get_scaled_sin(time_now)

        # offset both scales by an amount determined by that axis of the screen, and its length
        # this keeps the aspect ratio the same
        offset_w = surface_width / breathe_ratio * scaled_sin
        offset_h = surface_height / breathe_ratio * scaled_sin

        left += scaled_sin * offset_w
        right += scaled_sin * -offset_w
        top += scaled_sin * offset_h
        bottom += scaled_sin * -offset_h

        pygame_draw_line(surface, color, (left, top), (right, top), width)
        pygame_draw_line(surface, color, (left, top), (left, bottom), width)
        pygame_draw_line(surface, color, (right, top), (right, bottom), width)
        pygame_draw_line(surface, color, (left, bottom), (right, bottom), width)

        half_width = width/2
        width_minus_one = width - 1

        pygame_draw_circle(surface, color, (left, top), radius=half_width, width=width_minus_one)
        pygame_draw_circle(surface, color, (right, top), radius=half_width, width=width_minus_one)
        pygame_draw_circle(surface, color, (left, bottom), radius=half_width, width=width_minus_one)
        pygame_draw_circle(surface, color, (right, bottom), radius=half_width, width=width_minus_one)



