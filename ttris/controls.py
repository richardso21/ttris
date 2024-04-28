import pyxel

from ttris.tetriminos import RotationDirection


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
            res |= self.board.curr_piece.rotateMino(
                RotationDirection.CLOCKWISE, self.board.board_arr
            )

        if pyxel.btnp(pyxel.KEY_Z):
            res |= self.board.curr_piece.rotateMino(
                RotationDirection.COUNTERCLOCKWISE, self.board.board_arr
            )

        if pyxel.btnp(pyxel.KEY_A):  # 180 rotation
            res |= self.board.curr_piece.rotateMino(
                RotationDirection.FLIP180, self.board.board_arr
            )

        if res:
            self.board.sound_board.playRotation()

            tspin = self.board.curr_piece.checkTSpin(self.board.board_arr)
            if tspin:
                self.board.sound_board.playLCSpecial()
                self.board.previous_tspin = tspin

    def _checkMovementKeys(self) -> None:
        res = False
        if pyxel.btnp(pyxel.KEY_LEFT, hold=self.das, repeat=self.arr):
            res |= self.board.curr_piece.moveX(-1, self.board.board_arr)

        if pyxel.btnp(pyxel.KEY_RIGHT, hold=self.das, repeat=self.arr):
            res |= self.board.curr_piece.moveX(1, self.board.board_arr)

        if pyxel.btnp(pyxel.KEY_DOWN, repeat=self.arr):
            res |= self.board.curr_piece.softDrop(self.board.board_arr)

        if res:
            self.board.sound_board.playMovement()

    def checkControls(self) -> None:
        self._checkHoldKey()
        self._checkHardDropKey()
        self._checkRotationKeys()
        self._checkMovementKeys()
