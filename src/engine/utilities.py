

def is_numerical(value) -> bool:
    """ Returns true, if the value is a type of number: int, float;
    otherwise returns false
    """
    if isinstance(value, int) or isinstance(value, float):
        return True
    else:
        return False


def clamp(value, min, max):
    """ Tries to cast the supplied value to a numeric class, and returns a
    value between [min and max], inclusive

    Args:
        value(numerical) - the value which is to be constrained
        min(numerical) - the smallest allowed return value
        max(numerical) - the largest allowed return value

    Returns:
        clamped(numerical) - a returned value ranging from min to max (inclusive)
    """
    if not is_numerical(value) or not is_numerical(min) or not is_numerical(max):
        return None

    if value > max:
        return max
    elif value < min:
        return min
    else:
        return value


def clamp_onscreen(value, min, max):
    """ a type of clamp used to keep the value on screen

    Args:
        value(numerical) - the value which is to be constrained
        min(numerical) - the smallest allowed returned value
        max(numerical) - the largest allowed return value

    Returns:
        clamped(numerical) - a returned value ranging from min to max (inclusive)
    """
    if not is_numerical(value) or not is_numerical(min) or not is_numerical(max):
        return None

    if value < min:
        value = min - value
    if value > max:
        value = value - max
    return value
