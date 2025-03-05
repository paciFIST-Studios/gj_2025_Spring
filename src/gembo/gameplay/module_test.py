import unittest

from enum import Enum

from src.gembo.gameplay import EGameMode, GameMode, GameModeManager


class GameModeTestCases(unittest.TestCase):

    def test_framework_can_pass_a_test(self):
        self.assertTrue(True)

    # EGameMode --------------------------------------------------------------------------------------------------------

    def test__enumGameMode__exists(self):
        self.assertTrue(isinstance(EGameMode.UNINIT, Enum))

    def test__enumGameMode__hasExpectedLength(self):
        self.assertTrue(len(EGameMode) == 8)


    # GameModeManager --------------------------------------------------------------------------------------------------

    def test__classGameModeManager__exists(self):
        self.assertIsNotNone(GameModeManager())

    def test__classGameModeManager__hasVariableCurrent__setToUninitByDefault(self):
        gmd = GameModeManager()
        self.assertEqual(gmd.current, EGameMode.UNINIT)

    def test__classGameModeManager__hasVariableCallables__setToCorrectDefault(self):
        gmd = GameModeManager()
        self.assertEqual(len(gmd.on_mode_changed_callables), 7)
        for key in gmd.on_mode_changed_callables.keys():
            subscribers_list = gmd.on_mode_changed_callables[key]
            self.assertTrue(isinstance(subscribers_list, list))

    # fn is_callable_registered ----------------------------------------------------------------------------------------

    def test__classGameModeManager__hasFn__isCallableRegistered(self):
        self.assertIsNotNone(GameModeManager().is_callable_registered)

    def test__classGameModeManager__fnIsCallableRegistered__returnsNone__forInvalidArgs(self):
        fn = GameModeManager().is_callable_registered
        self.assertIsNone(fn(None, lambda: 1))
        self.assertIsNone(fn(1, None))

    def test__classGameModeManager__fnIsCallableRegistered__returnsFalse__ifGameModeNotInCallables(self):
        mode = 100
        fn = lambda: 1
        self.assertFalse(GameModeManager().is_callable_registered(mode, fn))

    def test__classGameModeManager__fnIsCallableRegistered__returnsFalse__ifFunctionNotInCallables(self):
        mode = 1
        fnA = lambda: 1
        fnB = lambda: 2
        gmd = GameModeManager()
        gmd.register_callable(mode, fnA)

        self.assertFalse(GameModeManager().is_callable_registered(mode, fnB))

    def test__classGameModeManager__fnIsCallableRegistered__returnsTrue__ifFunctionInCallables(self):
        mode = 1
        fnA = lambda: 1
        gmd = GameModeManager()
        gmd.register_callable(mode, fnA)
        self.assertFalse(GameModeManager().is_callable_registered(mode, fnA))


    # fn get_callables_of_mode -----------------------------------------------------------------------------------------

    def test__classGameModeManager__hasFn__getCallablesOfMode(self):
        self.assertIsNotNone(GameModeManager().get_callables_of_mode)

    def test__classGameModeManager__fnGetCallablesOfMode__returnsNone__forNoneArgs(self):
        self.assertIsNone(GameModeManager().get_callables_of_mode(None))

    def test__classGameModeManager__fnGetCallablesOfMode__returnsNone__forModeNotInCallables(self):
        self.assertIsNone(GameModeManager().get_callables_of_mode(1))

    def test__classGameModeManager__fnGetCallablesOfMode__returnsList__forDiscoveredCallables(self):
        result = GameModeManager().get_callables_of_mode(EGameMode.DEMO_MODE)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(len(result), 0)

    # fn register_callable ---------------------------------------------------------------------------------------------

    def test__classGameModeManager__hasFn__registerCallable(self):
        self.assertIsNotNone(GameModeManager().register_callable)

    def test__classGameModeManager__registerCallable__returnsTrue__ifCallable_IsNot_AlreadyRegistered(self):
        mode = 1
        fnA = lambda: 1
        gmd = GameModeManager()
        self.assertTrue(gmd.register_callable(mode, fnA))

    def test__classGameModeManager__registerCallable__returnsTrue__ifCallable_Is_AlreadyRegistered(self):
        mode = 1
        fnA = lambda: 1
        gmd = GameModeManager()
        gmd.register_callable(mode, fnA)
        self.assertTrue(gmd.register_callable(mode, fnA))

    def test__classGameModeManager__registerCallable__doesNotReRegisterFn__ifCallable_Is_AlreadyRegistered(self):
        mode = EGameMode.GAMEPLAY_MODE
        fnA = lambda: 1
        gmd = GameModeManager()

        self.assertTrue(len(gmd.on_mode_changed_callables[mode]) < 2)
        gmd.register_callable(mode, fnA)
        self.assertTrue(len(gmd.on_mode_changed_callables[mode]) < 2)
        gmd.register_callable(mode, fnA)
        self.assertTrue(len(gmd.on_mode_changed_callables[mode]) < 2)
        gmd.register_callable(mode, fnA)
        self.assertTrue(len(gmd.on_mode_changed_callables[mode]) < 2)

    # fn unregister_callable -------------------------------------------------------------------------------------------

    def test__classGameModeManager__hasFn__unregisterCallable(self):
        self.assertIsNotNone(GameModeManager().unregister_callable)

    def test__classGameModeManager__fnUnregisterCallable__returnsFalse__forNoneArgs(self):
        self.assertFalse(GameModeManager().unregister_callable(None, None))

    def test__classGameModeManager__fnUnregisterCallable__returnsFalse__unknownGameMode(self):
        self.assertFalse(GameModeManager().unregister_callable(1, lambda: 1))

    def test__classGameModeManager__fnUnregisterCallable__returnsFalse__unknownFunction(self):
        mode = EGameMode.GAMEPLAY_MODE
        fnA = lambda: 1
        fnB = lambda: 2
        gmd = GameModeManager()
        gmd.register_callable(mode, fnA)
        self.assertFalse(gmd.unregister_callable(mode, fnB))

    def test__classGameModeManager__fnUnregisterCallable__returnsTrue__forRegisteredFunction(self):
        mode = EGameMode.GAMEPLAY_MODE
        fnA = lambda: 1
        gmd = GameModeManager()
        gmd.register_callable(mode, fnA)
        self.assertTrue(gmd.unregister_callable(mode, fnA))

    def test__classGameModeManager__fnUnregisterCallable__reducesCallableListSize__whenReturningTrue(self):
        mode = EGameMode.GAMEPLAY_MODE
        fnA = lambda: 1
        gmd = GameModeManager()
        self.assertEqual(len(gmd.get_callables_of_mode(mode)), 0)
        gmd.register_callable(mode, fnA)
        self.assertEqual(len(gmd.get_callables_of_mode(mode)), 1)
        self.assertTrue(gmd.unregister_callable(mode, fnA))
        self.assertEqual(len(gmd.get_callables_of_mode(mode)), 0)

    # fn run_callables_for_mode ----------------------------------------------------------------------------------------

    def test__classGameModeManager__hasFn__runCallablesForMode(self):
        self.assertIsNotNone(GameModeManager().run_callables_for_mode)

    def test__classGameModeManager__runCallablesForMode__willAssertForInvalidMode(self):
        try:
            GameModeManager().run_callables_for_mode(None)
        except AssertionError as ex:
            self.assertIsNotNone(ex)

        try:
            GameModeManager().run_callables_for_mode(1)
        except AssertionError as ex:
            self.assertIsNotNone(ex)

    def test__classGameModeManager__runCallablesForMode__runsAllSubscribedCallables__whenCalled(self):
        gmd = GameModeManager()

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

    # fn is_mode_registered --------------------------------------------------------------------------------------------

    def test__classGameModeManager__fnIsModeRegistered__exists(self):
        self.assertIsNotNone(GameModeManager.is_mode_registered)

    def test__classGameModeManager__fnIsModeRegistered__returnsNone__ForBadArgs(self):
        fn = GameModeManager().is_mode_registered
        self.assertIsNone(fn(EGameMode.DEMO_MODE, None))
        self.assertIsNone(fn(None, GameMode(None, {})))

    def test__classGameModeManager__fnIsModeRegistered__returnsFalse__ifEnumIsNotRegistered(self):
        self.assertFalse(GameModeManager().is_mode_registered(EGameMode.DEMO_MODE, {}))

    def test__classGameModeManager__fnIsModeRegistered__returnsFalse__ifGameModeIsNotRegistered(self):
        gmm = GameModeManager()
        emode = EGameMode.DEMO_MODE
        mode = GameMode(None, {})
        self.assertFalse(gmm.is_mode_registered(emode, mode))
        gmm.register_mode(emode, mode)
        self.assertTrue(gmm.is_mode_registered(emode, mode))
        self.assertFalse(gmm.is_mode_registered(emode, GameMode(None, {})))

    def test__classGameModeManager__fnIsModeRegistered__returnsTrue__ifGameModeIsRegistered(self):
        gmm = GameModeManager()
        emode = EGameMode.DEMO_MODE
        mode = GameMode(None, {})
        gmm.register_mode(emode, mode)
        self.assertTrue(gmm.is_mode_registered(emode, mode))

    # fn register_mode -------------------------------------------------------------------------------------------------

    def test__classGameModeManager__fnRegisterMode__exists(self):
        self.assertIsNotNone(GameModeManager().register_mode)

    def test__classGameModeManager__fnRegisterMode__returnsTrue__ifRegistrationIsSuccessful(self):
        gmm = GameModeManager()
        emode = EGameMode.DEMO_MODE
        mode = GameMode(None, {})
        self.assertEqual(len(gmm.game_modes), 0)
        self.assertTrue(gmm.register_mode(emode, mode))
        self.assertEqual(len(gmm.game_modes), 1)

    def test__classGameModeManager__fnRegisterMode__returnsTrue__ifModeIsAlreadyRegistered(self):
        gmm = GameModeManager()
        emode = EGameMode.DEMO_MODE
        mode = GameMode(None, {})
        self.assertEqual(len(gmm.game_modes), 0)
        self.assertTrue(gmm.register_mode(emode, mode))
        self.assertEqual(len(gmm.game_modes), 1)
        self.assertTrue(gmm.register_mode(emode, mode))
        self.assertEqual(len(gmm.game_modes), 1)

    # fn unregister_mode -----------------------------------------------------------------------------------------------

    def test__classGameModeManger__fnUnregisterMode__exists(self):
        self.assertIsNotNone(GameModeManager.unregister_mode)

    def test__classGameModeManager__fnUnregisterMode__returnsFalse__forNoneArgs(self):
        self.assertFalse(GameModeManager().unregister_mode(EGameMode.DEMO_MODE, None))
        self.assertFalse(GameModeManager().unregister_mode(None, GameMode(None, {})))

    def test__classGameModeManager__fnUnregisterMode__returnsFalse__forUntrackedEnum(self):
        gmm = GameModeManager()
        emode = EGameMode.DEMO_MODE
        mode = GameMode(None, {})
        self.assertTrue(gmm.register_mode(emode, mode))
        self.assertFalse(gmm.unregister_mode(100, mode))

    def test__classGameModeManager__fnUnregisterMode__returnsFalse__forWrongGameModeClass(self):
        gmm = GameModeManager()
        emode = EGameMode.DEMO_MODE
        mode = GameMode(None, {})
        self.assertTrue(gmm.register_mode(emode, mode))
        self.assertFalse(gmm.unregister_mode(emode, GameMode(None, {})))

    def test__classGameModeManager__fnUnregisterMode__returnsTrue__forSuccessfulUnregistration(self):
        gmm = GameModeManager()
        emode = EGameMode.DEMO_MODE
        mode = GameMode(None, {})
        self.assertEqual(len(gmm.game_modes), 0)
        self.assertTrue(gmm.register_mode(emode, mode))
        self.assertEqual(len(gmm.game_modes), 1)
        self.assertTrue(gmm.unregister_mode(emode, mode))
        self.assertEqual(len(gmm.game_modes), 0)


    # fn set_mode__demo ------------------------------------------------------------------------------------------------

    def test__classGameModeManager__hasFn__setDemoMode(self):
        self.assertIsNotNone(GameModeManager().set_mode__demo)

    def test__classGameModeManager__fnSetDemoMode__changesCurrentModeToDemoMode(self):
        gmd = GameModeManager()
        self.assertEqual(gmd.current, EGameMode.UNINIT)
        gmd.set_mode__demo()
        self.assertEqual(gmd.current, EGameMode.DEMO_MODE)

    def test__classGameModeManager__fnSetDemoMode__callsRegisteredCallable(self):
        gmd = GameModeManager()
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

    def test__classGameModeManager__hasFn__setGameplayMode(self):
        self.assertIsNotNone(GameModeManager().set_mode__gameplay)

    def test__classGameModeManager__fnSetGameplayMode__changesCurrentModeToGameplayMode(self):
        gmd = GameModeManager()
        self.assertEqual(gmd.current, EGameMode.UNINIT)
        gmd.set_mode__gameplay()
        self.assertEqual(gmd.current, EGameMode.GAMEPLAY_MODE)

    def test__classGameModeManager__fnSetGameplayMode__callsRegisteredCallable(self):
        gmd = GameModeManager()
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

    def test__classGameModeManager__hasFn__setMenuMode(self):
        self.assertIsNotNone(GameModeManager().set_mode__menu)

    def test__classGameModeManager__fnSetMenuMode__changesCurrentModeToMenuMode(self):
        gmd = GameModeManager()
        self.assertEqual(gmd.current, EGameMode.UNINIT)
        gmd.set_mode__menu()
        self.assertEqual(gmd.current, EGameMode.MENU_MODE)

    def test__classGameModeManager__fnSetMenuMode__callsRegisteredCallable(self):
        gmd = GameModeManager()
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

    def test__classGameModeManager__hasFn__setSettingsMenu(self):
        self.assertIsNotNone(GameModeManager().set_mode__settings)

    def test__classGameModeManager__fnSetSettingsMode__changesCurrentModeToSettingsMode(self):
        gmd = GameModeManager()
        self.assertEqual(gmd.current, EGameMode.UNINIT)
        gmd.set_mode__settings()
        self.assertEqual(gmd.current, EGameMode.SETTINGS_MODE)

    def test__classGameModeManager__fnSetSettingsMode__callsRegisteredCallable(self):
        gmd = GameModeManager()
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

    def test__classGameModeManager__hasFn__setStatsMenu(self):
        self.assertIsNotNone(GameModeManager().set_mode__stats)

    def test__classGameModeManager__fnSetStatsMode__changesCurrentModeToStatsMode(self):
        gmd = GameModeManager()
        self.assertEqual(gmd.current, EGameMode.UNINIT)
        gmd.set_mode__stats()
        self.assertEqual(gmd.current, EGameMode.STATS_MODE)

    def test__classGameModeManager__fnSetStatsMode__callsRegisteredCallable(self):
        gmd = GameModeManager()
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

    def test__classGameModeManager__hasFn__setAboutMenu(self):
        self.assertIsNotNone(GameModeManager().set_mode__about)

    def test__classGameModeManager__fnSetAboutMode__changesCurrentModeToAboutMode(self):
        gmd = GameModeManager()
        self.assertEqual(gmd.current, EGameMode.UNINIT)
        gmd.set_mode__about()
        self.assertEqual(gmd.current, EGameMode.ABOUT_MODE)

    def test__classGameModeManager__fnSetAboutMode__callsRegisteredCallable(self):
        gmd = GameModeManager()
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

    def test__classGameModeManager__hasFn__setMode(self):
        self.assertIsNotNone(GameModeManager().set_mode)

    def test__classGameModeManager__fnSetMode__worksForAllEnumeratredModes(self):
        gmd = GameModeManager()
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

    # fn update --------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
