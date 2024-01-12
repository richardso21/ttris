import pyxel

from ttris.tetriminos import MinoType, Tetrimino


class Controller:
    def __init__(self, das, arr):
        self.das = das
        self.arr = arr

        self._left = False
        self._right = False
        self._ccw = False
        self._cw = False
        self._sdrop = False
        self._hdrop = False

    def checkControls(self):
        if pyxel.btnp(pyxel.KEY_LEFT, hold=self.das, repeat=self.arr):
            self._left = True
        pass

    @property
    def left(self):
        res = self.keyp
        self.keyp = [False, False, False, False]
        return res
