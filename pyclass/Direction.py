# Перечислить верхнюю левую, нижнюю правую и четыре неподвижные точки
from enum import Enum, auto


class Direction(Enum):
    LEFT = auto()
    TOP = auto()
    RIGHT = auto()
    BOTTOM = auto()

    LEFT_TOP = auto()
    RIGHT_TOP = auto()
    LEFT_BOTTOM = auto()
    RIGHT_BOTTOM = auto()