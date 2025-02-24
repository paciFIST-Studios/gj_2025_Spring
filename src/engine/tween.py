



def linear(t: float) -> float:
    return t

def easeIn(t: float) -> float:
    from math import cos, pi
    return -cos(t * pi/2) + 1

def easeInOut(t: float) -> float:
    from math import cos, pi
    return -(cos(pi * t) - 1) / 2

