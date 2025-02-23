

def clamp(x, min, max):
    if not x or not min or not max:
        return None
    elif x > max:
        return max
    elif x < min:
        return min
    else:
        return x



class PID(object):


    def __init__(
            self,
            Kp=1.0,
            Ki=0.0,
            Kd=0.0,
            set_point=0.0,
            sample_time=0.01,
            output_limits=(None, None),
            auto_mode=True,
            proportional_on_measurement=False,
            differential_on_measurement=True,
            error_map=None,
            time_fn=None,
            starting_output=0.0,
    ):
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.set_point = set_point
        self.sample_time = sample_time

        self._min_output, self._max_output = None, None
        self._auto_mode = auto_mode
        self.proportional_on_measurement = proportional_on_measurement
        self.differential_on_measurement = differential_on_measurement
        self.error_map = error_map

        self._proportional = 0
        self._integral = 0
        self._derivative = 0

        self._last_time = None
        self._last_output = None


