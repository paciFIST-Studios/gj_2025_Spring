import unittest

import time


from src.engine.animation import SpriteAnimation, SpriteAnimator


class AnimationTestCases(unittest.TestCase):
    class TestEngine:
        @staticmethod
        def now():
            return time.time()



    def assertThrows(self, exception_type, callable_fn, *args, **kwargs):
        """ any fn called from this fn will catch the exception given as exception_type.
        If that happens, unittest.assertTrue(True) is called.  If any other exception,
        or if no exception arises, then unittest.assertTrue(False) is called
        """
        try:
            callable_fn(*args, **kwargs)
            self.assertTrue(False)
        except exception_type as ex:
            self.assertTrue(True)
        except:
            self.assertTrue(False)


    def test_framework_can_pass_a_test(self):
        self.assertTrue(True)

    #-------------------------------------------------------------------------------------------------------------------
    # class Animation
    #-------------------------------------------------------------------------------------------------------------------

    def create_animation(self, surfaces=None, completion_time=None):
        if not surfaces:
            surfaces = []
        if not completion_time:
            completion_time = 1.0
        return SpriteAnimation(self.TestEngine, surfaces, completion_time)

    def test__classAnimation__ctor__throwsForNone__EngineArg(self):
        self.assertThrows(AssertionError, SpriteAnimation, None, [], 1)

    def test__classAnimation__ctor__throwsForNone__AnimSurfacesArg(self):
        self.assertThrows(AssertionError, SpriteAnimation, self.TestEngine, None, 1)

    def test__classAnimation__ctor__throwsForNone__CompletionTimeArg(self):
        self.assertThrows(AssertionError, SpriteAnimation, self.TestEngine, [], None)

    def test__classAnimation__fnInit__requiresEngineReferenceToConstruct(self):
        self.assertIsNotNone(SpriteAnimation(self.TestEngine, [], 1))

    def test__classAnimation__fnPlay__exists(self):
        self.assertIsNotNone(self.create_animation().play)

    def test__classAnimation__fnPlay__storesValueGivenInLoopPlayingAnimation(self):
        anim = self.create_animation()
        self.assertFalse(anim.loop_playing_animation)
        anim.play(loop=True)
        self.assertTrue(anim.loop_playing_animation)
        anim.play(loop=False)
        self.assertFalse(anim.loop_playing_animation)

    def test__classAnimation__fnGetFrame__returnsLastFrame__ifTimeIsElapsedAndAnimDoesNotLoop(self):
        frames = [0]
        anim = SpriteAnimation(self.TestEngine, frames, 0.0)
        anim.play()
        self.assertEqual(anim.get_frame(), 0)

    # todo: test calling pause does the right behaviour for storing elapsed time

    # todo: test calling unpause does the right behaviour for retrieving elapsed time

    # todo: test calling unpause is robust to doing that first

    #-------------------------------------------------------------------------------------------------------------------
    # class SpriteAnimator
    #-------------------------------------------------------------------------------------------------------------------

    # fn register_animation ---------------------------------------------------------------------------------------------

    def test__classSpriteAnimator__fnRegisterAnimation__exists(self):
        self.assertIsNotNone(SpriteAnimator().register_animation)

    def test__classSpriteAnimator__fnRegisterAnimation__registersAnAnimationForIdealParameters(self):
        span = SpriteAnimator()
        name = 'animation'
        animations = [1, 2, 3, 4, 6, 4, 4, 4]

        self.assertFalse(name in span.animations)
        span.register_animation(name, animations)
        self.assertTrue(name in span.animations)

        ret = span.animations[name]
        self.assertEqual(ret, animations)


    # fn play_animation ------------------------------------------------------------------------------------------------

    def test__classSpriteAnimator__fnPlayAnimation__exists(self):
        self.assertIsNotNone(SpriteAnimator().play_animation)







if __name__ == '__main__':
    unittest.main()
