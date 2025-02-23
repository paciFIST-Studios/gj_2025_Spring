
from dataclasses import dataclass


@dataclass(frozen=True)
class TimeConstants:
    SECONDS_IN_A_SECOND: int = 1
    SECONDS_IN_A_MINUTE: int = 60
    SECONDS_IN_AN_HOUR: int = 3_600 # 60 * 60
    SECONDS_IN_A_DAY: int = 86_400 # 60 * 60 * 24
    SECONDS_IN_A_WEEK: int = 604_800 # 60 * 60 * 24 * 7
    SECONDS_IN_A_MONTH: int = 2_592_000 # 60 * 60 * 24 * 30
    SECONDS_IN_A_YEAR: int =  31_536_000 # 60 * 60 * 24 * 365
    SECONDS_IN_A_DECADE: int = 315_360_000 # 60 * 60 * 24 * 366 * 10
    SECONDS_IN_A_CENTURY: int = 3_153_600_000 # 60 * 60 * 24 * 366 * 100
    SECONDS_IN_A_MILLENNIUM: int = 31_536_000_000 # 60 * 60 * 24 * 366 * 1000

    TIME_UNITS_PER_S = {
        # 'millenia': SECONDS_IN_A_MILLENNIUM,
        # 'centuries': SECONDS_IN_A_CENTURY,
        # 'decades': SECONDS_IN_A_DECADE,
        # 'years': SECONDS_IN_A_YEAR,
        # 'months': SECONDS_IN_A_MONTH,
        # 'weeks': SECONDS_IN_A_WEEK,
        # 'days': SECONDS_IN_A_DAY,
        'hours': SECONDS_IN_AN_HOUR,
        'minutes': SECONDS_IN_A_MINUTE,
        'seconds': SECONDS_IN_A_SECOND
    }

    GET_TIME_UNITS_ABBREVIATION = {
        # 'millenia': 'M',
        # 'centuries': 'C',
        # 'decades': 'DD',
        # 'years': 'y',
        # 'months': 'm',
        # 'weeks': 'w',
        # 'days': 'd',
        'hours': 'h',
        'minutes': 'm',
        'seconds': 's'
    }

    @staticmethod
    def get_unlocked_units(seconds):
        time_values = TimeConstants.slice_seconds_into_time_groups(seconds)
        is_unit_unlocked = {}
        for unit, value in time_values.items():
            if value:
                is_unit_unlocked[unit] = True
            else:
                is_unit_unlocked[unit] = False
        return is_unit_unlocked

    @staticmethod
    def slice_seconds_into_time_groups(seconds):
        time_values = {}
        for unit, value in TimeConstants.TIME_UNITS_PER_S.items():
            time_values[unit], seconds = divmod(seconds, value)
        return time_values
