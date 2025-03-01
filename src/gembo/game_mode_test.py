import unittest

from enum import Enum

from game_mode import EGameMode, GameModeData


class GameModeTestCases(unittest.TestCase):

    def test_framework_can_pass_a_test(self):
        self.assertTrue(True)

    # EGameMode --------------------------------------------------------------------------------------------------------

    def test__enumGameMode__exists(self):
        self.assertTrue(isinstance(EGameMode.UNINIT, Enum))

    def test__enumGameMode__hasExpectedLength(self):
        self.assertTrue(len(EGameMode) == 8)


    # GameModeData -----------------------------------------------------------------------------------------------------

    def test__classGameModeData__exists(self):
        self.assertIsNotNone(GameModeData())

    def test__classGameModeData__hasVariableCurrent__setToUninitByDefault(self):
        gmd = GameModeData()
        self.assertEqual(gmd.current, EGameMode.UNINIT)

    def test__classGameModeData__hasVariableCallables__setToCorrectDefault(self):
        gmd = GameModeData()
        self.assertEqual(len(gmd.callables), 7)
        for key in gmd.callables.keys():
            subscribers_list = gmd.callables[key]
            self.assertTrue(isinstance(subscribers_list, list))

    # fn is_callable_registered ----------------------------------------------------------------------------------------

    def test__classGameModeData__hasFn__isCallableRegistered(self):
        self.assertIsNotNone(GameModeData().is_callable_registered)

    def test__classGameModeData__fnIsCallableRegistered__returnsNone__forInvalidArgs(self):
        fn = GameModeData().is_callable_registered
        self.assertIsNone(fn(None, lambda: 1))
        self.assertIsNone(fn(1, None))

    def test__classGameModeData__fnIsCallableRegistered__returnsFalse__ifGameModeNotInCallables(self):
        mode = 100
        fn = lambda: 1
        self.assertFalse(GameModeData().is_callable_registered(mode, fn))

    def test__classGameModeData__fnIsCallableRegistered__returnsFalse__ifFunctionNotInCallables(self):
        mode = 1
        fnA = lambda: 1
        fnB = lambda: 2
        gmd = GameModeData()
        gmd.register_callable(mode, fnA)

        self.assertFalse(GameModeData().is_callable_registered(mode, fnB))

    def test__classGameModeData__fnIsCallableRegistered__returnsTrue__ifFunctionInCallables(self):
        mode = 1
        fnA = lambda: 1
        gmd = GameModeData()
        gmd.register_callable(mode, fnA)
        self.assertFalse(GameModeData().is_callable_registered(mode, fnA))


    # fn get_callables_of_mode -----------------------------------------------------------------------------------------

    def test__classGameModeData__hasFn__getCallablesOfMode(self):
        self.assertIsNotNone(GameModeData().get_callables_of_mode)

    def test__classGameModeData__fnGetCallablesOfMode__returnsNone__forNoneArgs(self):
        self.assertIsNone(GameModeData().get_callables_of_mode(None))

    def test__classGameModeData__fnGetCallablesOfMode__returnsNone__forModeNotInCallables(self):
        self.assertIsNone(GameModeData().get_callables_of_mode(1))

    def test__classGameModeData__fnGetCallablesOfMode__returnsList__forDiscoveredCallables(self):
        result = GameModeData().get_callables_of_mode(EGameMode.DEMO_MODE)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(len(result), 0)

    # fn register_callable ---------------------------------------------------------------------------------------------

    def test__classGameModeData__hasFn__registerCallable(self):
        self.assertIsNotNone(GameModeData().register_callable)

    def test__classGameModeData__registerCallable__returnsTrue__ifCallable_IsNot_AlreadyRegistered(self):
        mode = 1
        fnA = lambda: 1
        gmd = GameModeData()
        self.assertTrue(gmd.register_callable(mode, fnA))

    def test__classGameModeData__registerCallable__returnsTrue__ifCallable_Is_AlreadyRegistered(self):
        mode = 1
        fnA = lambda: 1
        gmd = GameModeData()
        gmd.register_callable(mode, fnA)
        self.assertTrue(gmd.register_callable(mode, fnA))

    def test__classGameModeData__registerCallable__doesNotReRegisterFn__ifCallable_Is_AlreadyRegistered(self):
        mode = EGameMode.GAMEPLAY_MODE
        fnA = lambda: 1
        gmd = GameModeData()

        self.assertTrue(len(gmd.callables[mode]) < 2)
        gmd.register_callable(mode, fnA)
        self.assertTrue(len(gmd.callables[mode]) < 2)
        gmd.register_callable(mode, fnA)
        self.assertTrue(len(gmd.callables[mode]) < 2)
        gmd.register_callable(mode, fnA)
        self.assertTrue(len(gmd.callables[mode]) < 2)

    # fn unregister_callable -------------------------------------------------------------------------------------------

    def test__classGameModeData__hasFn__unregisterCallable(self):
        self.assertIsNotNone(GameModeData().unregister_callable)

    def test__classGameModeData__fnUnregisterCallable__returnsFalse__forNoneArgs(self):
        self.assertFalse(GameModeData().unregister_callable(None, None))

    def test__classGameModeData__fnUnregisterCallable__returnsFalse__unknownGameMode(self):
        self.assertFalse(GameModeData().unregister_callable(1, lambda: 1))

    def test__classGameModeData__fnUnregisterCallable__returnsFalse__unknownFunction(self):
        mode = EGameMode.GAMEPLAY_MODE
        fnA = lambda: 1
        fnB = lambda: 2
        gmd = GameModeData()
        gmd.register_callable(mode, fnA)
        self.assertFalse(gmd.unregister_callable(mode, fnB))

    def test__classGameModeData__fnUnregisterCallable__returnsTrue__forRegisteredFunction(self):
        mode = EGameMode.GAMEPLAY_MODE
        fnA = lambda: 1
        gmd = GameModeData()
        gmd.register_callable(mode, fnA)
        self.assertTrue(gmd.unregister_callable(mode, fnA))

    def test__classGameModeData__fnUnregisterCallable__reducesCallableListSize__whenReturningTrue(self):
        mode = EGameMode.GAMEPLAY_MODE
        fnA = lambda: 1
        gmd = GameModeData()
        self.assertEqual(len(gmd.get_callables_of_mode(mode)), 0)
        gmd.register_callable(mode, fnA)
        self.assertEqual(len(gmd.get_callables_of_mode(mode)), 1)
        self.assertTrue(gmd.unregister_callable(mode, fnA))
        self.assertEqual(len(gmd.get_callables_of_mode(mode)), 0)

    # fn run_callables_for_mode ----------------------------------------------------------------------------------------

    def test__classGameModeData__hasFn__runCallablesForMode(self):
        self.assertIsNotNone(GameModeData().run_callables_for_mode)

    def test__classGameModeData__runCallablesForMode__willAssertForInvalidMode(self):
        try:
            GameModeData().run_callables_for_mode(None)
        except AssertionError as ex:
            self.assertIsNotNone(ex)

        try:
            GameModeData().run_callables_for_mode(1)
        except AssertionError as ex:
            self.assertIsNotNone(ex)

    def test__classGameModeData__runCallablesForMode__runsAllSubscribedCallables__whenCalled(self):
        gmd = GameModeData()

        # nonlocal, lets you get something from the outer scope
        fn1_has_run = False
        def _fn1():
            nonlocal fn1_has_run
            fn1_has_run = True

        fn2_has_run = False
        def _fn2():
            nonlocal fn2_has_run
            fn2_has_run = True

        fn3_has_run = False
        def _fn3():
            nonlocal fn3_has_run
            fn3_has_run = True

        mode = EGameMode.GAMEPLAY_MODE

        self.assertTrue(gmd.register_callable(mode, _fn1))
        self.assertTrue(gmd.register_callable(mode, _fn2))
        self.assertTrue(gmd.register_callable(mode, _fn3))

        self.assertFalse(fn1_has_run)
        self.assertFalse(fn2_has_run)
        self.assertFalse(fn3_has_run)

        gmd.run_callables_for_mode(mode)

        self.assertTrue(fn1_has_run)
        self.assertTrue(fn2_has_run)
        self.assertTrue(fn3_has_run)


    # fn set_mode__demo ------------------------------------------------------------------------------------------------

    def test__classGameModeData__hasFn__setDemoMode(self):
        self.assertIsNotNone(GameModeData().set_mode__demo)

    def test__classGameModeData__fnSetDemoMode__changesCurrentModeToDemoMode(self):
        gmd = GameModeData()
        self.assertEqual(gmd.current, EGameMode.UNINIT)
        gmd.set_mode__demo()
        self.assertEqual(gmd.current, EGameMode.DEMO_MODE)

    def test__classGameModeData__fnSetDemoMode__callsRegisteredCallable(self):
        gmd = GameModeData()
        mode = EGameMode.DEMO_MODE

        demo_mode_fn_called = False
        def _fn():
            nonlocal demo_mode_fn_called
            demo_mode_fn_called = True
        gmd.register_callable(mode, _fn)

        self.assertFalse(demo_mode_fn_called)
        gmd.set_mode__demo()
        self.assertTrue(demo_mode_fn_called)


    # fn set_mode__gameplay --------------------------------------------------------------------------------------------

    def test__classGameModeData__hasFn__setGameplayMode(self):
        self.assertIsNotNone(GameModeData().set_mode__gameplay)

    def test__classGameModeData__fnSetGameplayMode__changesCurrentModeToGameplayMode(self):
        gmd = GameModeData()
        self.assertEqual(gmd.current, EGameMode.UNINIT)
        gmd.set_mode__gameplay()
        self.assertEqual(gmd.current, EGameMode.GAMEPLAY_MODE)

    def test__classGameModeData__fnSetGameplayMode__callsRegisteredCallable(self):
        gmd = GameModeData()
        mode = EGameMode.GAMEPLAY_MODE

        gameplay_mode_fn_called = False
        def _fn():
            nonlocal gameplay_mode_fn_called
            gameplay_mode_fn_called = True
        gmd.register_callable(mode, _fn)

        self.assertFalse(gameplay_mode_fn_called)
        gmd.set_mode__gameplay()
        self.assertTrue(gameplay_mode_fn_called)

    # fn set_mode__menu ------------------------------------------------------------------------------------------------

    def test__classGameModeData__hasFn__setMenuMode(self):
        self.assertIsNotNone(GameModeData().set_mode__menu)

    def test__classGameModeData__fnSetMenuMode__changesCurrentModeToMenuMode(self):
        gmd = GameModeData()
        self.assertEqual(gmd.current, EGameMode.UNINIT)
        gmd.set_mode__menu()
        self.assertEqual(gmd.current, EGameMode.MENU_MODE)

    def test__classGameModeData__fnSetMenuMode__callsRegisteredCallable(self):
        gmd = GameModeData()
        mode = EGameMode.MENU_MODE

        menu_mode_fn_called = False
        def _fn():
            nonlocal menu_mode_fn_called
            menu_mode_fn_called = True
        gmd.register_callable(mode, _fn)

        self.assertFalse(menu_mode_fn_called)
        gmd.set_mode__menu()
        self.assertTrue(menu_mode_fn_called)

    # fn set_mode__settings --------------------------------------------------------------------------------------------

    def test__classGameModeData__hasFn__setSettingsMenu(self):
        self.assertIsNotNone(GameModeData().set_mode__settings)

    def test__classGameModeData__fnSetSettingsMode__changesCurrentModeToSettingsMode(self):
        gmd = GameModeData()
        self.assertEqual(gmd.current, EGameMode.UNINIT)
        gmd.set_mode__settings()
        self.assertEqual(gmd.current, EGameMode.SETTINGS_MODE)

    def test__classGameModeData__fnSetSettingsMode__callsRegisteredCallable(self):
        gmd = GameModeData()
        mode = EGameMode.SETTINGS_MODE

        settings_mode_fn_called = False
        def _fn():
            nonlocal settings_mode_fn_called
            settings_mode_fn_called = True
        gmd.register_callable(mode, _fn)

        self.assertFalse(settings_mode_fn_called)
        gmd.set_mode__settings()
        self.assertTrue(settings_mode_fn_called)


    # fn set_mode__stats -----------------------------------------------------------------------------------------------

    def test__classGameModeData__hasFn__setStatsMenu(self):
        self.assertIsNotNone(GameModeData().set_mode__stats)

    def test__classGameModeData__fnSetStatsMode__changesCurrentModeToStatsMode(self):
        gmd = GameModeData()
        self.assertEqual(gmd.current, EGameMode.UNINIT)
        gmd.set_mode__stats()
        self.assertEqual(gmd.current, EGameMode.STATS_MODE)

    def test__classGameModeData__fnSetStatsMode__callsRegisteredCallable(self):
        gmd = GameModeData()
        mode = EGameMode.STATS_MODE

        stats_mode_fn_called = False
        def _fn():
            nonlocal stats_mode_fn_called
            stats_mode_fn_called = True
        gmd.register_callable(mode, _fn)

        self.assertFalse(stats_mode_fn_called)
        gmd.set_mode__stats()
        self.assertTrue(stats_mode_fn_called)


    # fn set_mode__about -----------------------------------------------------------------------------------------------

    def test__classGameModeData__hasFn__setAboutMenu(self):
        self.assertIsNotNone(GameModeData().set_mode__about)

    def test__classGameModeData__fnSetAboutMode__changesCurrentModeToAboutMode(self):
        gmd = GameModeData()
        self.assertEqual(gmd.current, EGameMode.UNINIT)
        gmd.set_mode__about()
        self.assertEqual(gmd.current, EGameMode.ABOUT_MODE)

    def test__classGameModeData__fnSetAboutMode__callsRegisteredCallable(self):
        gmd = GameModeData()
        mode = EGameMode.ABOUT_MODE

        about_mode_fn_called = False
        def _fn():
            nonlocal about_mode_fn_called
            about_mode_fn_called = True
        gmd.register_callable(mode, _fn)

        self.assertFalse(about_mode_fn_called)
        gmd.set_mode__about()
        self.assertTrue(about_mode_fn_called)

    # fn set_mode ------------------------------------------------------------------------------------------------------

    def test__classGameModeData__hasFn__setMode(self):
        self.assertIsNotNone(GameModeData().set_mode)

    def test__classGameModeData__fnSetMode__worksForAllEnumeratredModes(self):
        gmd = GameModeData()
        fn_called = False
        def _fn():
            nonlocal fn_called
            fn_called = True
        fn = _fn

        modes = [x for x in EGameMode if x != EGameMode.UNINIT]
        for mode in modes:
            fn_called = False
            self.assertTrue(gmd.register_callable(mode, fn))
            self.assertFalse(fn_called)
            gmd.set_mode(mode)
            self.assertTrue(fn_called)

    # fn get_game_mode_nav_order ------------------------------------------------------------------------------------------------------------------

    # def test__classGameModeData__hasFn__getGameModeNavOrder(self):
    #     self.assertIsNotNone(GameModeData().get_game_mode_nav_order)
    #
    # def test__classGameModeData__fnGetGameModeNavOrder__returnValueHasExpectedLength(self):
    #     results = GameModeData().get_game_mode_nav_order()
    #     self.assertEqual(len(results), 5)
    #
    # def test__classGameModeData__fnGetGameModeNavOrder__returnsCorrectOrderingOfNavigableModes(self):
    #     nav = GameModeData().get_game_mode_nav_order()
    #     self.assertEqual(nav[0], EGameMode.DEMO_MODE)
    #     self.assertEqual(nav[1], EGameMode.GAMEPLAY_MODE)
    #     self.assertEqual(nav[2], EGameMode.STATS_MODE)
    #     self.assertEqual(nav[3], EGameMode.SETTINGS_MODE)
    #     self.assertEqual(nav[4], EGameMode.ABOUT_MODE)

    # fn cycle ---------------------------------------------------------------------------------------------------------

    # def test__classGameModeData__hasFn__cycle(self):
    #     self.assertIsNotNone(GameModeData().cycle)



    # def test__classGameModeData__hasFn__(self):
    #     self.assertIsNotNone(GameModeData().)


if __name__ == '__main__':
    unittest.main()
