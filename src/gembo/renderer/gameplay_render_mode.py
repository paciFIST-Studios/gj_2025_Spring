
# python

# pygame
from pygame.math import lerp as pygame_lerp
from pygame.time import set_timer as pygame_set_timer

# engine
from src.engine.time_utility import TimeConstants
from src.engine.utilities import clamp

# game
from src.gembo.renderer.render_mode import (RenderMode, Surface, EGameMode, EColor, Padding,
                                            render_breathe_box, pygame_draw_line, pygame_draw_circle)


# gameplay
class GameplayRenderMode(RenderMode):
    def __init__(self, engine, surface: Surface, mode: EGameMode, render_dict: dict):
        super().__init__(engine, surface, mode, render_dict)
        self._gameplay = self.value_or_default('gameplay')
        self._player = self.value_or_default('player')
        self._gem = self.value_or_default('gem')
        self._cactus = self.value_or_default('cactus')

        self._statistics = self.value_or_default('statistics')
        self._ui = self.value_or_default('ui')

        self.fn_get_total_playtime_s: callable = self.value_or_default('fn_get_total_playtime_s')
        self.fn_player_streak_popup_is_visible: callable = self.value_or_default('fn_player_streak_popup_is_visible')
        self.fn_player_streak_popup_is_animating: callable = self.value_or_default('fn_player_streak_popup_is_animating')

        self.EVENT__UNHIGHLIGHT_TIME_PLAYED = self.value_or_default('event_unhighlight_time_played')

        self.player_streak_font = self.value_or_default('player_streak_font')



    def render(self):
        self.render_gameplay_floor()
        self.render_gameplay_timer()
        self.render_gameplay_points()
        self.render_current_streak_popup()
        self.render_player_image()
        self.render_gem_image()
        self.render_cactus_image()


    def render_gameplay_floor(self):
        """ like render_menu_floor, but it responds to the player streak as part of the gameplay experience"""
        # line positions
        left = 0 + self._gameplay.floor_line_padding
        right = self.surface_width - self._gameplay.floor_line_padding
        top = 0 + self._gameplay.floor_line_padding
        bottom = self.surface_height - self._gameplay.floor_line_padding

        floor_line_color = self._gameplay.floor_line_color
        floor_line_width = self._gameplay.floor_line_width

        if self._gameplay.show_streak_popup():
            nth_frame = self._gameplay.gem_streak_advance_breath_box_color_every_n_frames
            frames = int(self.engine.frame_count / nth_frame)
            theme = [EColor.DARK_PURPLE, EColor.DARK_BLUE, EColor.DARK_GREEN]

            if frames % 3 == 0:
                floor_line_color = theme[0]
            elif frames % 3 == 1:
                floor_line_color = theme[1]
            elif frames % 3 == 2:
                floor_line_color = theme[2]

            floor_line_width = self._gameplay.gem_streak_length

        render_breathe_box(
            surface=self.render_surface,
            padding=Padding(left, top, right, bottom),
            color=floor_line_color,
            width=floor_line_width,
            is_animated=True,
            breathe_ratio=5.0
        )

    def render_gameplay_timer(self):
        """ shows total playtime since the file was reset """
        if self._ui.time_played_text_is_visible:
            playtime_s = self.fn_get_total_playtime_s()

            # assemble the timer string
            time_values = TimeConstants.slice_seconds_into_time_groups(playtime_s)
            timer_string = ''
            for key, value in time_values.items():
                abbreviation = TimeConstants.GET_TIME_UNITS_ABBREVIATION[key]
                timer_string += f'{int(value):02}{abbreviation} '

            # timer blinks yellow on every minute
            if '00s' in timer_string:
                self._ui.highlight_time_played_text()
                pygame_set_timer(self.EVENT__UNHIGHLIGHT_TIME_PLAYED,
                                      self._ui.time_played_text_highlight_timeout_ms)

            else:
                self._ui.unhighlight_time_played_text()

            # calculate centered-on-screen position for the gameplay timer
            gameplay_timer_renderable_text = self._gameplay.font.render(timer_string.strip(), True,
                                                                        self._ui.time_played_text_color)
            gameplay_timer_width, _ = gameplay_timer_renderable_text.get_size()
            _, pos_y = self._ui.time_played_text_position
            pos_x = (self.surface_width / 2) - (gameplay_timer_width / 2)

            # blit
            self.render_surface.blit(gameplay_timer_renderable_text, (pos_x, pos_y))


    def render_gameplay_points(self):
        """ shows the number of 'ripe' gems collected """
        if self._ui.point_total_text_is_visible:
            total = self._statistics.player_stats['total_points']

            # build points string
            point_total_string = f'{total}'
            point_total_renderable_text = self._gameplay.font.render(point_total_string, True, self._ui.point_total_text_color)

            # calculate centered on screen position
            point_total_width, _ = point_total_renderable_text.get_size()
            _, pos_y = self._ui.point_total_text_position
            pos_x = (self.surface_width/2) - (point_total_width/2)

            # blit
            self.render_surface.blit(point_total_renderable_text, (pos_x, pos_y))


    def render_current_streak_popup(self):
        """ shows a counter of the player's current 'ripe' gem streak """
        if self.fn_player_streak_popup_is_visible():
            streak = self._gameplay.gem_streak_length
            streak_string = f'x{streak}'
            streak_renderable_text = self.player_streak_font.render(streak_string, True, EColor.HIGHLIGHT_YELLOW)

            text_width, _ = streak_renderable_text.get_size()
            pos_x = (self.surface_width/2)-(text_width/2)

            final_pos_y = self.surface_height - 90
            pos_y = final_pos_y

            if self.fn_player_streak_popup_is_animating():
                now = self.engine.now()
                elapsed = now - self._gameplay.gem_streak_started_at_time
                duration_s = self._gameplay.gem_streak_popup_fly_in_duration_s
                t_progress = clamp(elapsed/duration_s, 0, 1)
                if t_progress == 1.0:
                    self._gameplay.gem_streak_popup_is_animating = False
                start_pos_y = self.surface_height + 90
                pos_y = pygame_lerp(start_pos_y, final_pos_y, t_progress)

            self.render_surface.blit(streak_renderable_text, (pos_x, pos_y))

            """ When the player starts a streak, they have 1 point.  We will hide the current_streak_popup,
            until the player has 3 points.  Then the popup should:
                * fly in - easing
                * show the number of the current streak
                * look visually engaging
                * play an extra sound
                * play a final "fireworks" when the streak ends
                * fly out - easing
            """


    def render_player_image(self):
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

        self.render_surface.blit(blit_image, self._player.position)



    def render_gem_image(self):
        if self._gameplay.gem_is_active:
            self.render_surface.blit(self._gem.image, self._gem.position)

    def render_cactus_image(self):
        if self._cactus.cactus_is_active:
            self.render_surface.blit(self._cactus.image, self._cactus.position)