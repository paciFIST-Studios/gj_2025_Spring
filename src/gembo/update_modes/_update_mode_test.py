import unittest

from enum import Enum

from src.gembo.update_modes import EUpdateMode, UpdateModeBase, UpdateModeManager


class UpdateModeTestCases(unittest.TestCase):

    # test utilities ---------------------------------------------------------------------------------------------------

    class MockUpdateMode(UpdateModeBase):
        def __init__(self):
            super().__init__(None, {})

        def update(self, delta_time_s: float, actions_this_frame: list):
            pass


    # test framework ---------------------------------------------------------------------------------------------------

    def test_framework_can_pass_a_test(self):
        self.assertTrue(True)

    # EUpdateMode --------------------------------------------------------------------------------------------------------

    def test__enumUpdateMode__exists(self):
        self.assertTrue(isinstance(EUpdateMode.UNINIT, Enum))

    def test__enumUpdateMode__hasExpectedLength(self):
        self.assertTrue(len(EUpdateMode) == 8)


    # UpdateModeManager --------------------------------------------------------------------------------------------------

    def test__classUpdateModeManager__exists(self):
        self.assertIsNotNone(UpdateModeManager())

    def test__classUpdateModeManager__hasVariableCurrent__setToUninitByDefault(self):
        umm = UpdateModeManager()
        self.assertEqual(umm.current, EUpdateMode.UNINIT)

    def test__classUpdateModeManager__hasVariableCallables__setToCorrectDefault(self):
        umm = UpdateModeManager()
        self.assertEqual(len(umm.on_mode_changed_callables), 7)
        for key in umm.on_mode_changed_callables.keys():
            subscribers_list = umm.on_mode_changed_callables[key]
            self.assertTrue(isinstance(subscribers_list, list))

    # fn is_callable_registered ----------------------------------------------------------------------------------------

    def test__classUpdateModeManager__hasFn__isCallableRegistered(self):
        self.assertIsNotNone(UpdateModeManager().is_callable_registered)

    def test__classUpdateModeManager__fnIsCallableRegistered__returnsNone__forInvalidArgs(self):
        fn = UpdateModeManager().is_callable_registered
        self.assertIsNone(fn(None, lambda: 1))
        self.assertIsNone(fn(1, None))

    def test__classUpdateModeManager__fnIsCallableRegistered__returnsFalse__ifUpdateModeNotInCallables(self):
        mode = 100
        fn = lambda: 1
        self.assertFalse(UpdateModeManager().is_callable_registered(mode, fn))

    def test__classUpdateModeManager__fnIsCallableRegistered__returnsFalse__ifFunctionNotInCallables(self):
        mode = 1
        fnA = lambda: 1
        fnB = lambda: 2
        umm = UpdateModeManager()
        umm.register_callable(mode, fnA)

        self.assertFalse(UpdateModeManager().is_callable_registered(mode, fnB))

    def test__classUpdateModeManager__fnIsCallableRegistered__returnsTrue__ifFunctionInCallables(self):
        mode = 1
        fnA = lambda: 1
        gmd = UpdateModeManager()
        gmd.register_callable(mode, fnA)
        self.assertFalse(UpdateModeManager().is_callable_registered(mode, fnA))


    # fn get_callables_of_mode -----------------------------------------------------------------------------------------

    def test__classUpdateModeManager__hasFn__getCallablesOfMode(self):
        self.assertIsNotNone(UpdateModeManager().get_callables_of_mode)

    def test__classUpdateModeManager__fnGetCallablesOfMode__returnsNone__forNoneArgs(self):
        self.assertIsNone(UpdateModeManager().get_callables_of_mode(None))

    def test__classUpdateModeManager__fnGetCallablesOfMode__returnsNone__forModeNotInCallables(self):
        self.assertIsNone(UpdateModeManager().get_callables_of_mode(1))

    def test__classUpdateModeManager__fnGetCallablesOfMode__returnsList__forDiscoveredCallables(self):
        result = UpdateModeManager().get_callables_of_mode(EUpdateMode.UPDATE_DEMO)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(len(result), 0)

    # fn register_callable ---------------------------------------------------------------------------------------------

    def test__classUpdateModeManager__hasFn__registerCallable(self):
        self.assertIsNotNone(UpdateModeManager().register_callable)

    def test__classUpdateModeManager__registerCallable__returnsTrue__ifCallable_IsNot_AlreadyRegistered(self):
        mode = 1
        fnA = lambda: 1
        umm = UpdateModeManager()
        self.assertTrue(umm.register_callable(mode, fnA))

    def test__classUpdateModeManager__registerCallable__returnsTrue__ifCallable_Is_AlreadyRegistered(self):
        mode = 1
        fnA = lambda: 1
        umm = UpdateModeManager()
        umm.register_callable(mode, fnA)
        self.assertTrue(umm.register_callable(mode, fnA))

    def test__classUpdateModeManager__registerCallable__doesNotReRegisterFn__ifCallable_Is_AlreadyRegistered(self):
        mode = EUpdateMode.UPDATE_GAMEPLAY
        fnA = lambda: 1
        umm = UpdateModeManager()

        self.assertTrue(len(umm.on_mode_changed_callables[mode]) < 2)
        umm.register_callable(mode, fnA)
        self.assertTrue(len(umm.on_mode_changed_callables[mode]) < 2)
        umm.register_callable(mode, fnA)
        self.assertTrue(len(umm.on_mode_changed_callables[mode]) < 2)
        umm.register_callable(mode, fnA)
        self.assertTrue(len(umm.on_mode_changed_callables[mode]) < 2)

    # fn unregister_callable -------------------------------------------------------------------------------------------

    def test__classUpdateModeManager__hasFn__unregisterCallable(self):
        self.assertIsNotNone(UpdateModeManager().unregister_callable)

    def test__classUpdateModeManager__fnUnregisterCallable__returnsFalse__forNoneArgs(self):
        self.assertFalse(UpdateModeManager().unregister_callable(None, None))

    def test__classUpdateModeManager__fnUnregisterCallable__returnsFalse__unknownUpdateMode(self):
        self.assertFalse(UpdateModeManager().unregister_callable(1, lambda: 1))

    def test__classUpdateModeManager__fnUnregisterCallable__returnsFalse__unknownFunction(self):
        mode = EUpdateMode.UPDATE_GAMEPLAY
        fnA = lambda: 1
        fnB = lambda: 2
        umm = UpdateModeManager()
        umm.register_callable(mode, fnA)
        self.assertFalse(umm.unregister_callable(mode, fnB))

    def test__classUpdateModeManager__fnUnregisterCallable__returnsTrue__forRegisteredFunction(self):
        mode = EUpdateMode.UPDATE_GAMEPLAY
        fnA = lambda: 1
        umm = UpdateModeManager()
        umm.register_callable(mode, fnA)
        self.assertTrue(umm.unregister_callable(mode, fnA))

    def test__classUpdateModeManager__fnUnregisterCallable__reducesCallableListSize__whenReturningTrue(self):
        mode = EUpdateMode.UPDATE_GAMEPLAY
        fnA = lambda: 1
        umm = UpdateModeManager()
        self.assertEqual(len(umm.get_callables_of_mode(mode)), 0)
        umm.register_callable(mode, fnA)
        self.assertEqual(len(umm.get_callables_of_mode(mode)), 1)
        self.assertTrue(umm.unregister_callable(mode, fnA))
        self.assertEqual(len(umm.get_callables_of_mode(mode)), 0)

    # fn run_callables_for_mode ----------------------------------------------------------------------------------------

    def test__classUpdateModeManager__hasFn__runCallablesForMode(self):
        self.assertIsNotNone(UpdateModeManager().run_callables_for_mode)

    def test__classUpdateModeManager__runCallablesForMode__willAssertForInvalidMode(self):
        try:
            UpdateModeManager().run_callables_for_mode(None)
        except AssertionError as ex:
            self.assertIsNotNone(ex)

        try:
            UpdateModeManager().run_callables_for_mode(1)
        except AssertionError as ex:
            self.assertIsNotNone(ex)

    def test__classUpdateModeManager__runCallablesForMode__runsAllSubscribedCallables__whenCalled(self):
        umm = UpdateModeManager()

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

        mode = EUpdateMode.UPDATE_GAMEPLAY

        self.assertTrue(umm.register_callable(mode, _fn1))
        self.assertTrue(umm.register_callable(mode, _fn2))
        self.assertTrue(umm.register_callable(mode, _fn3))

        self.assertFalse(fn1_has_run)
        self.assertFalse(fn2_has_run)
        self.assertFalse(fn3_has_run)

        umm.run_callables_for_mode(mode)

        self.assertTrue(fn1_has_run)
        self.assertTrue(fn2_has_run)
        self.assertTrue(fn3_has_run)

    # fn is_mode_registered --------------------------------------------------------------------------------------------

    def test__classUpdateModeManager__fnIsModeRegistered__exists(self):
        self.assertIsNotNone(UpdateModeManager.is_mode_registered)

    def test__classUpdateModeManager__fnIsModeRegistered__returnsNone__ForBadArgs(self):
        fn = UpdateModeManager().is_mode_registered
        self.assertIsNone(fn(EUpdateMode.UPDATE_DEMO, None))
        self.assertIsNone(fn(None, self.MockUpdateMode()))

    def test__classUpdateModeManager__fnIsModeRegistered__returnsFalse__ifEnumIsNotRegistered(self):
        self.assertFalse(UpdateModeManager().is_mode_registered(EUpdateMode.UPDATE_DEMO, {}))

    def test__classUpdateModeManager__fnIsModeRegistered__returnsFalse__ifUpdateModeIsNotRegistered(self):
        umm = UpdateModeManager()
        emode = EUpdateMode.UPDATE_DEMO
        mode = self.MockUpdateMode()
        self.assertFalse(umm.is_mode_registered(emode, mode))
        umm.register_mode(emode, mode)
        self.assertTrue(umm.is_mode_registered(emode, mode))
        self.assertFalse(umm.is_mode_registered(emode, self.MockUpdateMode()))

    def test__classUpdateModeManager__fnIsModeRegistered__returnsTrue__ifUpdateModeIsRegistered(self):
        umm = UpdateModeManager()
        emode = EUpdateMode.UPDATE_DEMO
        mode = self.MockUpdateMode()
        umm.register_mode(emode, mode)
        self.assertTrue(umm.is_mode_registered(emode, mode))

    # fn register_mode -------------------------------------------------------------------------------------------------

    def test__classUpdateModeManager__fnRegisterMode__exists(self):
        self.assertIsNotNone(UpdateModeManager().register_mode)

    def test__classUpdateModeManager__fnRegisterMode__returnsTrue__ifRegistrationIsSuccessful(self):
        umm = UpdateModeManager()
        emode = EUpdateMode.UPDATE_DEMO
        mode = self.MockUpdateMode()
        self.assertEqual(len(umm.game_modes), 0)
        self.assertTrue(umm.register_mode(emode, mode))
        self.assertEqual(len(umm.game_modes), 1)

    def test__classUpdateModeManager__fnRegisterMode__returnsTrue__ifModeIsAlreadyRegistered(self):
        umm = UpdateModeManager()
        emode = EUpdateMode.UPDATE_DEMO
        mode = self.MockUpdateMode()
        self.assertEqual(len(umm.game_modes), 0)
        self.assertTrue(umm.register_mode(emode, mode))
        self.assertEqual(len(umm.game_modes), 1)
        self.assertTrue(umm.register_mode(emode, mode))
        self.assertEqual(len(umm.game_modes), 1)

    # fn unregister_mode -----------------------------------------------------------------------------------------------

    def test__classUpdateModeManger__fnUnregisterMode__exists(self):
        self.assertIsNotNone(UpdateModeManager.unregister_mode)

    def test__classUpdateModeManager__fnUnregisterMode__returnsFalse__forNoneArgs(self):
        self.assertFalse(UpdateModeManager().unregister_mode(EUpdateMode.UPDATE_DEMO, None))
        self.assertFalse(UpdateModeManager().unregister_mode(None, self.MockUpdateMode()))

    def test__classUpdateModeManager__fnUnregisterMode__returnsFalse__forUntrackedEnum(self):
        umm = UpdateModeManager()
        emode = EUpdateMode.UPDATE_DEMO
        mode = self.MockUpdateMode()
        self.assertTrue(umm.register_mode(emode, mode))
        self.assertFalse(umm.unregister_mode(100, mode))

    def test__classUpdateModeManager__fnUnregisterMode__returnsFalse__forWrongUpdateModeClass(self):
        umm = UpdateModeManager()
        emode = EUpdateMode.UPDATE_DEMO
        mode = self.MockUpdateMode()
        self.assertTrue(umm.register_mode(emode, mode))
        self.assertFalse(umm.unregister_mode(emode, self.MockUpdateMode()))

    def test__classUpdateModeManager__fnUnregisterMode__returnsTrue__forSuccessfulUnregistration(self):
        umm = UpdateModeManager()
        emode = EUpdateMode.UPDATE_DEMO
        mode = self.MockUpdateMode()
        self.assertEqual(len(umm.game_modes), 0)
        self.assertTrue(umm.register_mode(emode, mode))
        self.assertEqual(len(umm.game_modes), 1)
        self.assertTrue(umm.unregister_mode(emode, mode))
        self.assertEqual(len(umm.game_modes), 0)


    # fn set_mode__demo ------------------------------------------------------------------------------------------------

    def test__classUpdateModeManager__hasFn__setDemoMode(self):
        self.assertIsNotNone(UpdateModeManager().set_mode__demo)

    def test__classUpdateModeManager__fnSetDemoMode__changesCurrentModeToDemoMode(self):
        umm = UpdateModeManager()
        self.assertEqual(umm.current, EUpdateMode.UNINIT)
        umm.set_mode__demo()
        self.assertEqual(umm.current, EUpdateMode.UPDATE_DEMO)

    def test__classUpdateModeManager__fnSetDemoMode__callsRegisteredCallable(self):
        umm = UpdateModeManager()
        mode = EUpdateMode.UPDATE_DEMO

        demo_mode_fn_called = False
        def _fn():
            nonlocal demo_mode_fn_called
            demo_mode_fn_called = True
        umm.register_callable(mode, _fn)

        self.assertFalse(demo_mode_fn_called)
        umm.set_mode__demo()
        self.assertTrue(demo_mode_fn_called)


    # fn set_mode__gameplay --------------------------------------------------------------------------------------------

    def test__classUpdateModeManager__hasFn__setGameplayMode(self):
        self.assertIsNotNone(UpdateModeManager().set_mode__gameplay)

    def test__classUpdateModeManager__fnSetGameplayMode__changesCurrentModeToGameplayMode(self):
        umm = UpdateModeManager()
        self.assertEqual(umm.current, EUpdateMode.UNINIT)
        umm.set_mode__gameplay()
        self.assertEqual(umm.current, EUpdateMode.UPDATE_GAMEPLAY)

    def test__classUpdateModeManager__fnSetGameplayMode__callsRegisteredCallable(self):
        umm = UpdateModeManager()
        mode = EUpdateMode.UPDATE_GAMEPLAY

        gameplay_mode_fn_called = False
        def _fn():
            nonlocal gameplay_mode_fn_called
            gameplay_mode_fn_called = True
        umm.register_callable(mode, _fn)

        self.assertFalse(gameplay_mode_fn_called)
        umm.set_mode__gameplay()
        self.assertTrue(gameplay_mode_fn_called)

    # fn set_mode__menu ------------------------------------------------------------------------------------------------

    def test__classUpdateModeManager__hasFn__setMenuMode(self):
        self.assertIsNotNone(UpdateModeManager().set_mode__menu)

    def test__classUpdateModeManager__fnSetMenuMode__changesCurrentModeToMenuMode(self):
        umm = UpdateModeManager()
        self.assertEqual(umm.current, EUpdateMode.UNINIT)
        umm.set_mode__menu()
        self.assertEqual(umm.current, EUpdateMode.UPDATE_MENU)

    def test__classUpdateModeManager__fnSetMenuMode__callsRegisteredCallable(self):
        umm = UpdateModeManager()
        mode = EUpdateMode.UPDATE_MENU

        menu_mode_fn_called = False
        def _fn():
            nonlocal menu_mode_fn_called
            menu_mode_fn_called = True
        umm.register_callable(mode, _fn)

        self.assertFalse(menu_mode_fn_called)
        umm.set_mode__menu()
        self.assertTrue(menu_mode_fn_called)

    # fn set_mode__settings --------------------------------------------------------------------------------------------

    def test__classUpdateModeManager__hasFn__setSettingsMenu(self):
        self.assertIsNotNone(UpdateModeManager().set_mode__settings)

    def test__classUpdateModeManager__fnSetSettingsMode__changesCurrentModeToSettingsMode(self):
        umm = UpdateModeManager()
        self.assertEqual(umm.current, EUpdateMode.UNINIT)
        umm.set_mode__settings()
        self.assertEqual(umm.current, EUpdateMode.UPDATE_SETTINGS)

    def test__classUpdateModeManager__fnSetSettingsMode__callsRegisteredCallable(self):
        umm = UpdateModeManager()
        mode = EUpdateMode.UPDATE_SETTINGS

        settings_mode_fn_called = False
        def _fn():
            nonlocal settings_mode_fn_called
            settings_mode_fn_called = True
        umm.register_callable(mode, _fn)

        self.assertFalse(settings_mode_fn_called)
        umm.set_mode__settings()
        self.assertTrue(settings_mode_fn_called)


    # fn set_mode__stats -----------------------------------------------------------------------------------------------

    def test__classUpdateModeManager__hasFn__setStatsMenu(self):
        self.assertIsNotNone(UpdateModeManager().set_mode__stats)

    def test__classUpdateModeManager__fnSetStatsMode__changesCurrentModeToStatsMode(self):
        umm = UpdateModeManager()
        self.assertEqual(umm.current, EUpdateMode.UNINIT)
        umm.set_mode__stats()
        self.assertEqual(umm.current, EUpdateMode.UPDATE_STATISTICS)

    def test__classUpdateModeManager__fnSetStatsMode__callsRegisteredCallable(self):
        umm = UpdateModeManager()
        mode = EUpdateMode.UPDATE_STATISTICS

        stats_mode_fn_called = False
        def _fn():
            nonlocal stats_mode_fn_called
            stats_mode_fn_called = True
        umm.register_callable(mode, _fn)

        self.assertFalse(stats_mode_fn_called)
        umm.set_mode__stats()
        self.assertTrue(stats_mode_fn_called)


    # fn set_mode__about -----------------------------------------------------------------------------------------------

    def test__classUpdateModeManager__hasFn__setAboutMenu(self):
        self.assertIsNotNone(UpdateModeManager().set_mode__about)

    def test__classUpdateModeManager__fnSetAboutMode__changesCurrentModeToAboutMode(self):
        umm = UpdateModeManager()
        self.assertEqual(umm.current, EUpdateMode.UNINIT)
        umm.set_mode__about()
        self.assertEqual(umm.current, EUpdateMode.UPDATE_ABOUT)

    def test__classUpdateModeManager__fnSetAboutMode__callsRegisteredCallable(self):
        umm = UpdateModeManager()
        mode = EUpdateMode.UPDATE_ABOUT

        about_mode_fn_called = False
        def _fn():
            nonlocal about_mode_fn_called
            about_mode_fn_called = True
        umm.register_callable(mode, _fn)

        self.assertFalse(about_mode_fn_called)
        umm.set_mode__about()
        self.assertTrue(about_mode_fn_called)

    # fn set_mode ------------------------------------------------------------------------------------------------------

    def test__classUpdateModeManager__hasFn__setMode(self):
        self.assertIsNotNone(UpdateModeManager().set_mode)

    def test__classUpdateModeManager__fnSetMode__worksForAllEnumeratredModes(self):
        umm = UpdateModeManager()
        fn_called = False
        def _fn():
            nonlocal fn_called
            fn_called = True
        fn = _fn

        modes = [x for x in EUpdateMode if x != EUpdateMode.UNINIT]
        for mode in modes:
            fn_called = False
            self.assertTrue(umm.register_callable(mode, fn))
            self.assertFalse(fn_called)
            umm.set_mode(mode)
            self.assertTrue(fn_called)

    # fn update --------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
