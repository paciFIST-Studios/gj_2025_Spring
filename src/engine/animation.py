
class SpriteAnimation:
    def __init__(self, engine, animation_surfaces, duration_s):
        self.engine = engine
        assert hasattr(engine, 'now')

        self.animation_surfaces: list = animation_surfaces
        assert self.animation_surfaces is not None

        self.duration_s: float = duration_s
        assert self.duration_s is not None

        self.start_time = self.engine.now()
        self.loop_playing_animation: bool = False
        self.animation_playtime_before_pause_s = 0
        self.animation_is_paused = False

    def update_duration(self, new_duration_s):
        self.duration_s = new_duration_s

    def play(self, loop:bool=False):
        """ start anim from the beginning when called """
        self.loop_playing_animation = loop
        self.start_time = self.engine.now()

    def pause(self):
        """ stops the anim from playing """
        now = self.engine.now()
        elapsed_s = now - self.start_time
        self.animation_playtime_before_pause_s = elapsed_s
        self.animation_is_paused = True

    def unpause(self):
        """ cause the anim to resume play """
        now = self.engine.now()
        anim_restart_time = now - self.animation_playtime_before_pause_s
        self.start_time = anim_restart_time
        self.animation_is_paused = False

    def get_frame(self):
        """ retrieves the frame the anim should be playing at this moment """
        now = self.engine.now()
        elapsed_s = now - self.start_time

        if elapsed_s > self.duration_s:
            if not self.loop_playing_animation:
                return self.animation_surfaces[-1]

        # if time is elapsed and anim loops, it hits this code
        # if time is elapsed and anim does not loop, show final frame
        # if time is not elapsed, it hits this code

        if self.animation_is_paused:
            completion_percent = self.animation_playtime_before_pause_s / self.duration_s
        else:
            completion_percent = elapsed_s / self.duration_s

        steps = len(self.animation_surfaces)
        idx = int(steps * completion_percent)
        idx = idx % steps
#        idx = 0 if idx < 0 else idx if idx < steps-1 else steps-1
        return self.animation_surfaces[idx]





class SpriteAnimator:
    def __init__(self):
        self.animations = {}
        self.flipped_animations = {}

    def register_animation(self, name: str, animation: SpriteAnimation):
        if name not in self.animations:
            self.animations[name] = animation

    def update_animation_duration(self, name, new_duration_s):
        if name in self.animations:
            self.animations[name].update_duration(new_duration_s)

    def play_animation(self, name, loop=True):
        if name in self.animations:
            self.animations[name].play(loop)

    def pause_animation(self, name):
        if name in self.animations:
            self.animations[name].pause()

    def unpause_animation(self, name):
        if name in self.animations:
            self.animations[name].unpause()

    def get_animation_frame(self, name):
        if name in self.animations:
            return self.animations[name].get_frame()




