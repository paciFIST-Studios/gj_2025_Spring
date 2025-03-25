import unittest
from src.test import AbstractTestBase as TestCase

import time

from src.engine.cache import ECacheStatus
from src.engine.cache import RegisteredCacheObject
from src.engine.cache import EngineCache

class CacheTestCases(TestCase):
    def test_framework_can_pass_a_test(self):
        self.assertTrue(True)


    # test utilities ---------------------------------------------------------------------------------------------------

    class MockEngine:
        @staticmethod
        def now():
            return time.time()



    @staticmethod
    def mock_fn_now():
        return time.time()


    # ECacheStatus -----------------------------------------------------------------------------------------------------

    def test__enumECacheStatus__Exists(self):
        self.assertIsNotNone(ECacheStatus)

    def test__enumECacheStatus__isUnchangedInLength(self):
        self.assertEqual(len(ECacheStatus), 5)

    def test__enumECacheStatus__returnsStringForValue(self):
        self.assertTrue(isinstance(ECacheStatus.NO_EVICT, str))

    def test__enumECacheStatus__containsExpectedValues(self):
        self.assertEqual('UNINIT', ECacheStatus.UNINIT)
        self.assertEqual('NO_EVICT', ECacheStatus.NO_EVICT)
        self.assertEqual('EVICT_ON_TIMEOUT', ECacheStatus.EVICT_ON_TIMEOUT)
        self.assertEqual('EVICT_ON_REQUEST', ECacheStatus.EVICT_ON_REQUEST)
        self.assertEqual('EVICT_ON_ANY', ECacheStatus.EVICT_ON_ANY)


    # RegisteredCacheObject --------------------------------------------------------------------------------------------

    def test__classRegisteredCacheObject__Exists(self):
        self.assertIsNotNone(RegisteredCacheObject)

    def test__classRegisteredCacheObject__isFrozenDataClass(self):
        self.assertTrue(RegisteredCacheObject().__dataclass_params__.frozen)

    def test__classRegisteredCacheObject__hasCorrectDefaultMembersAndValues(self):
        self.assertEqual(len(RegisteredCacheObject.__dict__.keys()), 19)
        rco = RegisteredCacheObject()

        self.assertTrue(hasattr(rco, 'cache_status'))
        self.assertTrue(isinstance(rco.cache_status, ECacheStatus))
        self.assertEqual(rco.cache_status, ECacheStatus.UNINIT)

        self.assertTrue(hasattr(rco, 'registered_time'))
        self.assertTrue(isinstance(rco.registered_time, float))
        self.assertEqual(rco.registered_time, 0.0)

        self.assertTrue(hasattr(rco, 'eviction_timeout_s'))
        self.assertTrue(isinstance(rco.eviction_timeout_s, float))
        self.assertEqual(rco.eviction_timeout_s, 0.0)

        self.assertTrue(hasattr(rco, 'eviction_permitted'))
        self.assertTrue(isinstance(rco.eviction_permitted, bool))
        self.assertEqual(rco.eviction_permitted, False)

        self.assertTrue(hasattr(rco, 'cached_data'))
        self.assertIsNone(rco.cached_data)


    # class EngineCache ------------------------------------------------------------------------------------------------

    def test__classEngineCache__Exists(self):
        self.assertIsNotNone(EngineCache)

    def test__classEngineCache__constructsWithExpectedValues(self):
        ec = EngineCache(fn_now=self.mock_fn_now)

        self.assertIsNotNone(ec)
        self.assertTrue(hasattr(ec, 'fn_now'))
        self.assertEqual(ec.fn_now, self.mock_fn_now)

        self.assertTrue(hasattr(ec, 'program_duration_objects'))
        self.assertTrue(isinstance(ec.program_duration_objects, dict))
        self.assertEqual(ec.program_duration_objects, {})

        self.assertTrue(hasattr(ec, 'eviction_objects'))
        self.assertTrue(isinstance(ec.eviction_objects, dict))
        self.assertEqual(ec.eviction_objects, {})


    # fn EngineCache.check_evictions -----------------------------------------------------------------------------------

    def test__classEngineCache__fnCheckEvictions__exists(self):
        self.assertIsNotNone(EngineCache.check_evictions)

    def test__classEngineCache__fnCheckEvictions__removes__evictOnTimeoutElements__whichArePastTheTimeout(self):
        cache = EngineCache(fn_now=self.mock_fn_now)
        key, value, status, _ = self.get_engine_cache_register_args()
        self.assertEqual(len(cache.eviction_objects), 0)
        self.assertTrue(cache.register(key, value, ECacheStatus.EVICT_ON_TIMEOUT))
        self.assertEqual(len(cache.eviction_objects), 1)

        self.assertTrue(cache.is_registered(key))
        cache.check_evictions()
        self.assertFalse(cache.is_registered(key))

    def test__classEngineCache__fnCheckEvictions__removes__evictOnAnyElements__whichArePastTheTimeout(self):
        cache = EngineCache(fn_now=self.mock_fn_now)
        key, value, status, _ = self.get_engine_cache_register_args()
        self.assertEqual(len(cache.eviction_objects), 0)
        self.assertTrue(cache.register(key, value, ECacheStatus.EVICT_ON_ANY))
        self.assertEqual(len(cache.eviction_objects), 1)

        self.assertTrue(cache.is_registered(key))
        cache.check_evictions()
        self.assertFalse(cache.is_registered(key))

    def test__classEngineCache__fnCheckEvictions__doesNotRemove__evictOnRequestElements__whenCalled(self):
        cache = EngineCache(fn_now=self.mock_fn_now)
        key, value, status, _ = self.get_engine_cache_register_args()
        self.assertEqual(len(cache.eviction_objects), 0)
        self.assertTrue(cache.register(key, value, ECacheStatus.EVICT_ON_REQUEST))
        self.assertEqual(len(cache.eviction_objects), 1)

        self.assertTrue(cache.is_registered(key))
        cache.check_evictions()
        self.assertTrue(cache.is_registered(key))

    def test__classEngineCache__fnCheckEvictions__doesNotRemove__noEvictElements__whenCalled(self):
        cache = EngineCache(fn_now=self.mock_fn_now)
        key, value, status, _ = self.get_engine_cache_register_args()
        self.assertEqual(len(cache.program_duration_objects), 0)
        self.assertTrue(cache.register(key, value, ECacheStatus.NO_EVICT))
        self.assertEqual(len(cache.program_duration_objects), 1)

        self.assertTrue(cache.is_registered(key))
        cache.check_evictions()
        self.assertTrue(cache.is_registered(key))


    # fn EngineCache.is_registered -------------------------------------------------------------------------------------

    def test__classEngineCache__fnIsRegistered__exists(self):
        self.assertIsNotNone(EngineCache.is_registered)

    def test__classEngineCache__fnIsRegistered__returnsFalse__forBadKeyArg(self):
        self.assertFalse(EngineCache(fn_now=self.mock_fn_now).is_registered(None))
        self.assertFalse(EngineCache(fn_now=self.mock_fn_now).is_registered(''))
        self.assertFalse(EngineCache(fn_now=self.mock_fn_now).is_registered(1))

    def test__classEngineCache__fnIsRegistered__returnsTrue__forKeyFoundInProgramDurationObjects(self):
        cache = EngineCache(fn_now=self.mock_fn_now)
        key, value, status, timeout = self.get_engine_cache_register_args()
        self.assertEqual(len(cache.program_duration_objects), 0)
        cache.register(key, value, ECacheStatus.NO_EVICT, timeout)
        self.assertEqual(len(cache.program_duration_objects), 1)

        self.assertTrue(cache.is_registered(key))

    def test__classEngineCache__fnIsRegistered__returnsTrue__forKeyFoundInEvictionObjects(self):
        cache = EngineCache(fn_now=self.mock_fn_now)
        key, value, status, timeout = self.get_engine_cache_register_args()
        self.assertEqual(len(cache.eviction_objects), 0)
        cache.register(key, value, ECacheStatus.EVICT_ON_ANY, timeout)
        self.assertEqual(len(cache.eviction_objects), 1)

        self.assertTrue(cache.is_registered(key))

    def test__classEngineCache__fnIsRegistered__returnsFalse__forNoKeyFound(self):
        cache = EngineCache(fn_now=self.mock_fn_now)
        key, value, status, timeout = self.get_engine_cache_register_args()
        self.assertEqual(len(cache.eviction_objects), 0)
        cache.register(key, value, ECacheStatus.EVICT_ON_ANY, timeout)
        self.assertEqual(len(cache.eviction_objects), 1)

        self.assertFalse(cache.is_registered('key2'))


    # fn EngineCache.register ------------------------------------------------------------------------------------------

    def test__classEngineCache__fnRegister__exists(self):
        self.assertIsNotNone(EngineCache.register)

    @staticmethod
    def get_engine_cache_register_args():
        rco = RegisteredCacheObject()
        return 'key', rco, ECacheStatus.EVICT_ON_ANY, 1.0

    def test__classEngineCache__fnRegister__returnsFalse__forBadKeyArg(self):
        cache = EngineCache(fn_now=self.mock_fn_now)
        key, value, status, timeout = self.get_engine_cache_register_args()
        self.assertFalse(cache.register(None, value, status, timeout))
        self.assertFalse(cache.register('', value, status, timeout))
        self.assertFalse(cache.register(1, value, status, timeout))

    def test__classEngineCache__fnRegister__returnsFalse__forBadValueArg(self):
        cache = EngineCache(fn_now=self.mock_fn_now)
        key, value, status, timeout = self.get_engine_cache_register_args()
        self.assertFalse(cache.register(key, None, status, timeout))

    def test__classEngineCache__fnRegister__returnsFalse__forBadStatusArg(self):
        cache = EngineCache(fn_now=self.mock_fn_now)
        key, value, status, timeout = self.get_engine_cache_register_args()
        self.assertFalse(cache.register(key, value, None, timeout))
        self.assertFalse(cache.register(key, value, '', timeout))
        self.assertFalse(cache.register(key, value, 1, timeout))
        self.assertFalse(cache.register(key, value, ECacheStatus.UNINIT, timeout))

    def test__classEngineCache__fnRegister__returnsFalse__forBadTimeoutArg(self):
        cache = EngineCache(fn_now=self.mock_fn_now)
        key, value, status, timeout = self.get_engine_cache_register_args()
        self.assertFalse(cache.register(key, value, status, None))
        self.assertFalse(cache.register(key, value, status, ''))

    def test__classEngineCache__fnRegister__returnsTrue__ifItRegistersAnObject(self):
        cache = EngineCache(fn_now=self.mock_fn_now)
        key, value, status, timeout = self.get_engine_cache_register_args()
        self.assertTrue(cache.register(key, value, status, timeout))
        self.assertTrue(cache.register('key2', value, ECacheStatus.EVICT_ON_REQUEST))

    def test__classEngineCache__fnRegister__returnsFalse__ifItTriesToRegisterTheSameKeyAgain(self):
        cache = EngineCache(fn_now=self.mock_fn_now)
        key, value, status, _ = self.get_engine_cache_register_args()
        self.assertTrue(cache.register(key, value, status))
        self.assertFalse(cache.register(key, value, status))

    def test__classEngineCache__fnRegister__registersEvictionObjectsInTheEvictionCache(self):
        cache = EngineCache(fn_now=self.mock_fn_now)
        key, value, status, _ = self.get_engine_cache_register_args()
        self.assertEqual(len(cache.eviction_objects), 0)
        self.assertTrue(cache.register(key, value, status))
        self.assertEqual(len(cache.eviction_objects), 1)
        self.assertEqual(len(cache.program_duration_objects), 0)

    def test__classEngineCache__fnRegister__registersNonEvictionObjectsInTheNonEvictionCache(self):
        cache = EngineCache(fn_now=self.mock_fn_now)
        key, value, status, _ = self.get_engine_cache_register_args()
        self.assertEqual(len(cache.program_duration_objects), 0)
        self.assertTrue(cache.register(key, value, ECacheStatus.NO_EVICT))
        self.assertEqual(len(cache.program_duration_objects), 1)
        self.assertEqual(len(cache.eviction_objects), 0)

    def test__classEngineCache__fnRegister__createsTheCorrectRegisteredCacheObject__forEvictionObjects(self):
        cache = EngineCache(fn_now=self.mock_fn_now)
        key, value, status, timeout = self.get_engine_cache_register_args()
        self.assertEqual(len(cache.eviction_objects), 0)
        self.assertTrue(cache.register(key, value, ECacheStatus.EVICT_ON_REQUEST, timeout))
        self.assertEqual(len(cache.eviction_objects), 1)

        rco = cache.eviction_objects[key]

        self.assertTrue(rco.eviction_permitted)
        self.assertEqual(rco.eviction_timeout_s, timeout)

    # fn EngineCache.evict ---------------------------------------------------------------------------------------------

    def test__classEngineCache__fnEvict__exists(self):
        self.assertIsNotNone(EngineCache.evict)

    def test__classEngineCache__fnEvict__returnsFalse__forBadKeyArg(self):
        cache = EngineCache(fn_now=self.mock_fn_now)
        self.assertFalse(cache.evict(None))
        self.assertFalse(cache.evict(''))
        self.assertFalse(cache.evict(1))

    def test__classEngineCache__fnEvict__returnsFalse__forKeyNotInEvictionObjects(self):
        cache = EngineCache(fn_now=self.mock_fn_now)
        self.assertFalse(cache.evict('key'))

    def test__classEngineCache__fnEvict__returnsEvictedValue__forSuccessfulEviction(self):
        cache = EngineCache(fn_now=self.mock_fn_now)
        key, value, status, timeout = self.get_engine_cache_register_args()
        self.assertEqual(len(cache.eviction_objects), 0)
        self.assertTrue(cache.register(key, value, ECacheStatus.EVICT_ON_REQUEST, timeout))
        self.assertEqual(len(cache.eviction_objects), 1)

        ret = cache.evict(key)

        self.assertTrue(ret.eviction_permitted)
        self.assertTrue(isinstance(ret, RegisteredCacheObject))
        self.assertEqual(ret.cache_status, ECacheStatus.EVICT_ON_REQUEST)
        self.assertEqual(ret.eviction_timeout_s, timeout)
        self.assertEqual(ret.cached_data, value)


if __name__ == '__main__':
    unittest.main()
