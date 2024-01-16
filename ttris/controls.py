import pyxel


class Controller:
    def __init__(self, das, arr, board):
        self.das: int = das
        self.arr: int = arr
        self.board = board

    def _checkHardDropKey(self) -> None:
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.board.hardDropCurrPiece()

    def _checkHoldKey(self) -> None:
        if pyxel.btnp(pyxel.KEY_SHIFT):
            self.board.holdCurrPiece()

    def _checkRotationKeys(self) -> None:
        res = False
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_X):
            res |= self.board.currPiece.rotateMino(1, self.board.boardArr)

        if pyxel.btnp(pyxel.KEY_Z):
            res |= self.board.currPiece.rotateMino(-1, self.board.boardArr)

        if res:
            self.board.soundBoard.playRotation()

    def _checkMovementKeys(self) -> None:
        res = False
        if pyxel.btnp(pyxel.KEY_LEFT, hold=self.das, repeat=self.arr):
            res |= self.board.currPiece.moveX(-1, self.board.boardArr)

        if pyxel.btnp(pyxel.KEY_RIGHT, hold=self.das, repeat=self.arr):
            res |= self.board.currPiece.moveX(1, self.board.boardArr)

        if pyxel.btnp(pyxel.KEY_DOWN, repeat=self.arr):
            res |= self.board.currPiece.softDrop(self.board.boardArr)

        if res:
            self.board.soundBoard.playMovement()

    def checkControls(self) -> None:
        self._checkHoldKey()
        self._checkHardDropKey()
        self._checkRotationKeys()
        self._checkMovementKeys()
