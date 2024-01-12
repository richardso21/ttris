import pyxel

from ttris.constants import (
    BLOCK_SIZE,
    BOARD_HEIGHT,
    BOARD_WIDTH,
    BOARD_X,
    BOARD_Y,
    OVERFLOW_HEIGHT,
)
from ttris.tetriminos import MinoProvider, MinoType


class Board:
    def __init__(self, das, arr, lookahead):
        # make empty board
        self.boardArr = [[MinoType.NO_MINO] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        # start a queue of tetraminos
        self.minoProvider = MinoProvider(lookahead)
        self.das = das
        self.arr = arr
        self.spawnMino()
        self.hold = None
        self.holdLock = False

    def update(self) -> None:
        # check controls
        if pyxel.btnp(pyxel.KEY_SHIFT):
            self.holdCurrPiece()
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.hardDropCurrPiece()
        if pyxel.btnp(pyxel.KEY_DOWN, repeat=self.arr):
            if not self.currPiece.softDrop(self.boardArr):
                self.hardDropCurrPiece()
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_X):
            self.currPiece.rotateMino(1, self.boardArr)
        if pyxel.btnp(pyxel.KEY_Z):
            self.currPiece.rotateMino(-1, self.boardArr)
        if pyxel.btnp(pyxel.KEY_LEFT, hold=self.das, repeat=self.arr):
            self.currPiece.moveX(-1, self.boardArr)
        if pyxel.btnp(pyxel.KEY_RIGHT, hold=self.das, repeat=self.arr):
            self.currPiece.moveX(1, self.boardArr)

        # check for any line clears and construct new board if necessary
        clear_inds = [i for i, row in enumerate(self.boardArr) if all(row)]
        if len(clear_inds):  # some lines need to be cleared
            new_board_arr = [[MinoType.NO_MINO] * BOARD_WIDTH for _ in clear_inds]
            new_board_arr.extend(
                [row for i, row in enumerate(self.boardArr) if i not in clear_inds]
            )
            self.boardArr = new_board_arr

    def draw(self) -> None:
        # background (DEBUGGING)
        pyxel.rect(
            BOARD_X, BOARD_Y, BOARD_WIDTH * BLOCK_SIZE, BOARD_HEIGHT * BLOCK_SIZE, 1
        )

        # draw the bounding box up to the 20th block
        pyxel.rectb(
            BOARD_X - 1,
            BOARD_Y + (BLOCK_SIZE * OVERFLOW_HEIGHT) - 1,
            (BOARD_WIDTH * BLOCK_SIZE) + 2,
            ((BOARD_HEIGHT - OVERFLOW_HEIGHT) * BLOCK_SIZE) + 2,
            13,
        )
        # "undraw" the top edge of the board border
        pyxel.rect(
            BOARD_X,
            BOARD_Y + (BLOCK_SIZE * OVERFLOW_HEIGHT) - 1,
            (BOARD_WIDTH * BLOCK_SIZE),
            1,
            0,
        )

        # draw existing pieces on the board if a piece has dropped
        for i, row in enumerate(self.boardArr):
            for j, block in enumerate(row):
                if block == MinoType.NO_MINO:
                    continue
                x = j * BLOCK_SIZE + BOARD_X
                y = i * BLOCK_SIZE + BOARD_Y
                u = (block.value - 1) * BLOCK_SIZE
                pyxel.blt(x, y, 1, u, 0, BLOCK_SIZE, BLOCK_SIZE)

        self.currPiece.draw(hint=True)  # draw hint first, then the actual piece
        self.currPiece.draw()

    def holdCurrPiece(self) -> None:
        if self.holdLock:
            return
        # swap hold and current item
        tmp = self.hold
        self.hold = self.currPiece
        # or get next item in queue if hold is empty
        self.currPiece = tmp if tmp else self.minoProvider.fetchMino()
        self.currPiece.updateHint(self.boardArr)

        # reset x-y and rotation state of the now held piece
        self.hold.resetPiece()

        # prevent infinite holding
        self.holdLock = True

    def hardDropCurrPiece(self) -> None:
        self.currPiece.hardDrop(self.boardArr)

        # copy piece to board
        for i, row in enumerate(self.currPiece.minoArr):
            for j, block in enumerate(row):
                if not block:
                    continue
                self.boardArr[self.currPiece.y + i][
                    self.currPiece.x + j
                ] = self.currPiece.minoType

        # get new piece
        self.spawnMino()
        self.holdLock = False

    def spawnMino(self) -> None:
        self.currPiece = self.minoProvider.fetchMino()
        self.currPiece.updateHint(self.boardArr)
