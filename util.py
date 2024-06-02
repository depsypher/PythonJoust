import math


SPAWN_POINTS = [
    [690, 270],     # right
    [376, 492],     # bottom
    [327, 141],     # top
    [48, 294],      # left
]

LANES = [84, 260, 470]


def wrapped_distance(x1, y1, x2, y2, width):
    """
    Calculates distance between two points on a playfield that wraps around on the x dimension
    Adapted from:
    https://blog.demofox.org/2017/10/01/calculating-the-distance-between-points-in-wrap-around-toroidal-space/
    :param x1: first point x
    :param y1: first point y
    :param x2: second point x
    :param y2: second point y
    :param width: playfield width
    :return:
    """
    dx = abs(x2 - x1)
    if dx > width / 2:
        dx = width - dx

    dy = y2 - y1
    return math.sqrt(dx * dx + dy * dy)
