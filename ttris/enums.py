from enum import Enum


class RotationDirection(Enum):
    CLOCKWISE = 1
    COUNTERCLOCKWISE = -1
    FLIP180 = 2


class TSpinType(Enum):
    NONE = 0
    MINI = 1
    TSPIN = 2

    def __bool__(self):
        # NONE is falsy, everything else is truthy
        return self.value != 0


class MinoType(Enum):
    NO_MINO = 0
    MINO_I = 1
    MINO_O = 2
    MINO_T = 3
    MINO_S = 4
    MINO_Z = 5
    MINO_J = 6
    MINO_L = 7

    def __bool__(self):
        # NO_MINOs are falsy, everything else is truthy
        return self.value != 0
