import ctypes.wintypes
from dataclasses import dataclass

from enum import Enum


class ECacheStatus(str, Enum):
    """ Defines the eviction status of objects in the EngineCache

    NO_EVICT - this object should live for the entire program duration

    EVICT_ON_TIMEOUT - this object should be automatically removed, after the timeout passes

    EVICT_ON_REQUEST - this object should stay in the cache, until someone requests to remove it

    EVICT_ON_ANY - this object should be removed from the cache, whether through timeout or request--WHICHEVER COMES FIRST
    """
    UNINIT = 'UNINIT',
    NO_EVICT = 'NO_EVICT',
    EVICT_ON_TIMEOUT = 'EVICT_ON_TIMEOUT',
    EVICT_ON_REQUEST = 'EVICT_ON_REQUEST',
    EVICT_ON_ANY = 'EVICT_ON_ANY',


@dataclass(frozen=True)
class RegisteredCacheObject:
    """ This class wraps objects which are stored in the EngineCache.  When an object is wrapped, the wrapper
    is not permitted to change
    """
    cache_status: ECacheStatus = ECacheStatus.UNINIT
    registered_time: float = 0.0
    eviction_timeout_s: float = 0.0
    eviction_permitted: bool = False
    cached_data: any = None


class EngineCache:
    """ The EngineCache, is a centralized place for memory access, which will be used in the game
    """
    def __init__(self, engine):
        self.engine = engine
        self.program_duration_objects = {}
        self.eviction_objects = {}


    def check_evictions(self):
        """ Checks the cache of eviction objects, and removes any which can be
        evicted after timeout elapses
        """
        # you can't modify a collection while iterating over it,
        # so make a list of things to delete, while iterating the dict,
        # then iterate that list, and delete from the dict
        # alternatively, we could make a new dict, without the value
        to_remove = []

        # we're going to ignore objects in self.program_duration_objects,
        # b/c those are not evictable

        # iterate over the items in the dictionary
        for key in list(self.eviction_objects.keys()):
            eo = self.eviction_objects[key]
            assert eo.eviction_permitted
            if eo.cache_status in [ECacheStatus.EVICT_ON_TIMEOUT, ECacheStatus.EVICT_ON_ANY]:
                now = self.engine.now()
                if now - eo.registered_time > eo.eviction_timeout_s:
                    to_remove.append(key)

        for removal in to_remove:
            del self.eviction_objects[removal]


    def is_registered(self, key: str) -> bool:
        """ Returns true, if the key is registered with the EngineCache

        Args:
            key(str) - the key to find

        Returns:
            is_registered(bool) - if the key is registered with the EngineCache
                                  returns False for invalid key
        """
        if key is None or not key or not isinstance(key, str):
            print(f'invalid key')
            return False

        if key in self.program_duration_objects.keys():
            return True

        if key in self.eviction_objects.keys():
            return True

        return False


    def register(self, key: str, value, status: ECacheStatus, eviction_timeout_s = 0.0) -> bool:
        """ Registers this key and value with the EngineCache.

        Args:
            key(str) - the name of the key
            value(anything) - the value which is to be stored in the EngineCache
            status(ECacheStatus) - how this key-value-pair is to behave
            eviction_timeout_s(float) - if used, the key-value-pair will be automatically
                                        evicted from the EngineCache, when check_evictions
                                        is called, if this much time has elapsed since it
                                        was first registered

        Returns:
            bSuccessful(bool) - True if registration occurred, otherwise False
        """

        if key is None or not key or not isinstance(key, str):
            return False

        # the value could be anything at all, so we just need to make sure it's not None
        # no one is allowed to cache None as a value
        if value is None:
            return False

        if status is None or not isinstance(status, ECacheStatus) or status is ECacheStatus.UNINIT:
            return False

        if eviction_timeout_s is None or not isinstance(eviction_timeout_s, float):
            return False

        eviction_permitted = status is not ECacheStatus.NO_EVICT

        # not allowed to double register, or update a registration
        if key in self.eviction_objects:
            return False

        rco = RegisteredCacheObject(
            cache_status=status,
            registered_time=self.engine.now(),
            eviction_timeout_s=eviction_timeout_s,
            eviction_permitted=eviction_permitted,
            cached_data=value
        )

        if eviction_permitted:
            self.eviction_objects[key] = rco
        else:
            self.program_duration_objects[key] = rco

        return True

    def evict(self, key: str) -> bool:
        """ Removes the value associated with this key

        Args:
            key(str) - the name of the key to look for

        Returns:
            bSuccessful(bool) - True, if the eviction took place
                                False, if no eviction took place
                                False, if the key was invalid
        """
        if key is None or not key or not isinstance(key, str):
            return False

        if key not in self.eviction_objects:
            return False

        return self.eviction_objects.pop(key)


