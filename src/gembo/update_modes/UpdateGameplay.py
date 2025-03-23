from dataclasses import dataclass
from random import randint

from pygame.math import Vector2 as PygameVector2
from pygame.time import set_timer as pygame_set_timer
from pygame.mixer import Sound as PygameSound

from src.engine.utilities import clamp, clamp_onscreen

from src.gembo.update_modes import UpdateModeBase, EUpdateMode


class UpdateGameplay(UpdateModeBase):

    def __init__(self, engine, game_mode_data: dict):
        super().__init__(engine, game_mode_data)

        self._display_surface = self.engine.cache.lookup('display_surface')

        self._gameplay = self.engine.cache.lookup('update_modes')
        self._game_mode = self.engine.cache.lookup('game_mode')
        self._player = self.engine.cache.lookup('player')
        self._gem = self.engine.cache.lookup('gem')
        self._cactus = self.engine.cache.lookup('cactus')

        self._statistics = self.engine.cache.lookup('statistics')
        self._ui = self.engine.cache.lookup('ui')

    # Gameplay Functions -----------------------------------------------------------------------------------------------

    def gem_overlaps_with_player(self):
        if self._gameplay.gem_is_active:
            distance = self._player.position - self._gem.position
            magnitude = distance.magnitude()
            if magnitude < self._gem.pickup_radius:
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
    def get_random_onscreen_coordinate(surface) -> PygameVector2:
        min_x, min_y = 0, 0
        max_x, max_y = surface.get_size()
        return PygameVector2( randint(min_x, max_x), randint(min_y, max_y) )


    @dataclass(frozen=True)
    class ExclusionZone:
        position: PygameVector2
        diameter: float


    @staticmethod
    def get_random_onscreen_coordinate_with_exclusion_zones(surface, exclusion_zones: list[ExclusionZone]):
        while True:
            coordinate = UpdateGameplay.get_random_onscreen_coordinate(surface)
            for ez in exclusion_zones:
                position, diameter = ez
                dist = coordinate - position
                if dist.length_squared() > diameter * diameter:
                    return coordinate




    def collect_gem(self):
        if self._game_mode.current != EUpdateMode.UPDATE_GAMEPLAY:
            return

        # set gem to not active, so it can be respawned
        self._gameplay.gem_is_active = False

        # emit the respawn event after timeout
        pygame_set_timer(self.engine.EVENT__RESPAWN_GEM, self._gem.respawn_timeout_ms)

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
            pygame_set_timer(self.engine.EVENT__UNHIGHLIGHT_GEM_COUNT, self._ui.point_total_text_highlight_duration_ms)

            # kick off the animation, if it hasn't been.  This is the only play that has authority to
            if not self.player_streak_popup_is_animating() and self.player_streak_popup__is_visible():
                self.player_streak_popup__start_animation()

            if self._gameplay.cactus_position_unchanged_for_n_ripe_gems > self._gameplay.cactus_respawn_every_n_gems:
                self.collide_with_cactus()
                self.place_cactus()

        # "spoiled" gems
        else:
            # if on a streak, it ends, and we calculate the stats to see if the player is on the scoreboard
            if self._gameplay.gem_streak_is_happening:
                self._gameplay.gem_streak_is_happening = False
                self._statistics.update_longest_streak(self._gameplay.gem_streak_length)
                self._statistics.update_streak_history(self._gameplay.gem_streak_length)

                # bug: saving the streak here causes the streak to be added to the play-time as minutes

            self._gameplay.gem_streak_length = 0

        if not self.engine.audio_is_muted:
            PygameSound.set_volume(self._gem.pickup_sound, 0.5)
            PygameSound.play(self._gem.pickup_sound)

        self._gameplay.last_gem_pickup_timestamp = self.engine.now()

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

        self._gem.position = PygameVector2(pos_x, pos_y)

        self._gem.image = self._gem.yellow_image
        pygame_set_timer(self.engine.EVENT__SPOIL_GEM, self._gameplay.gem_spoilage_timeout_ms)

        self._gameplay.gem_is_active = True

    def place_cactus(self):
        if self._cactus.cactus_is_active:
            return

        pos = self.get_random_onscreen_coordinate(self._display_surface)
        w, h = self._cactus.image.get_size()

        pos_x = clamp_onscreen(pos[0], 0, w)
        pos_y = clamp_onscreen(pos[1], 0, h)
        self._cactus.position = PygameVector2(pos_x, pos_y)
        self._cactus.cactus_is_active = True
        self._gameplay.cactus_position_unchanged_for_n_ripe_gems = 0

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

