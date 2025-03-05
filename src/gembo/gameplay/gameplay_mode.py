
# python

# pygame
from pygame.math import lerp as pygame_lerp

# engine

# game
from src.gembo.gameplay import GameMode

class GamplayGameMode(GameMode):




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

    update_gameplay_player_speed()