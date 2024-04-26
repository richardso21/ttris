from collections import deque
from enum import Enum
from itertools import islice
from random import Random
from typing import List

import pyxel

from ttris.constants import (
    BLOCK_SIZE,
    BOARD_HEIGHT,
    BOARD_WIDTH,
    BOARD_X,
    BOARD_Y,
    LOCK_DELAY,
    MINO_ARRS,
    SRS_TESTS,
    SRS_TESTS_I,
)


class RotationDirection(Enum):
    CLOCKWISE = 1
    COUNTERCLOCKWISE = -1
    FLIP180 = 2


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


class Tetrimino:
    def __init__(self, minoType: MinoType, x=3, y=2, minoArr=None) -> None:
        if minoType == MinoType.NO_MINO:
            raise Exception("Mino cannot be created with MinoType == 0 (NO_MINO)")
        self.minoType: MinoType = minoType
        self.minoArr: List[List[int]] = (
            minoArr if minoArr else MINO_ARRS[self.minoType.value - 1]
        )
        # set the position of the mino at the center of board/well by default
        self.x: int = x
        self.y: int = y
        self._spin: int = 0
        self.lockDelayStart: int = -1

    @property
    def spin(self) -> int:
        return self._spin % 4

    def resetPiece(self) -> None:
        # resets all mino properties to default when first initialized
        self.x = 3
        self.y = 2
        self.minoArr = MINO_ARRS[self.minoType.value - 1]
        self._spin = 0
        self.lockDelayStart = -1

    def lockDelayExpired(self, board: List[List[MinoType]]) -> bool:
        # returns boolean if the lock for the current piece has expired
        new_mino = Tetrimino(
            self.minoType, x=self.x, y=self.y + 1, minoArr=self.minoArr
        )
        if not new_mino.isValidPosition(board):
            if self.lockDelayStart == -1:
                self.lockDelayStart = pyxel.frame_count
        else:
            self.lockDelayStart = -1

        return (
            self.lockDelayStart != -1
            and pyxel.frame_count - self.lockDelayStart > LOCK_DELAY
        )

    def draw(self, x: int, y: int) -> None:
        minoTypeVal = self.minoType.value - 1
        for i, row in enumerate(self.minoArr):
            for j, block in enumerate(row):
                if not block:
                    continue
                draw_x = (self.x + j) * BLOCK_SIZE + x
                draw_y = (self.y + i) * BLOCK_SIZE + y
                u = (minoTypeVal) * BLOCK_SIZE
                pyxel.blt(draw_x, draw_y, 1, u, 0, BLOCK_SIZE, BLOCK_SIZE)

    def drawOnBoard(self, hint=False) -> None:
        # draw the floating mino on top of the board
        # if hint, then draw outline of piece instead with the hintY value
        minoTypeVal = self.minoType.value - 1 if not hint else 7
        minoY = self.y if not hint else self.hintY
        if hint:
            pyxel.dither(0.5)
        for i, row in enumerate(self.minoArr):
            for j, block in enumerate(row):
                if not block:
                    continue
                x = (self.x + j) * BLOCK_SIZE + BOARD_X
                y = (minoY + i) * BLOCK_SIZE + BOARD_Y
                u = (minoTypeVal) * BLOCK_SIZE
                pyxel.blt(x, y, 1, u, 0, BLOCK_SIZE, BLOCK_SIZE)
        pyxel.dither(1)

    def rotateMino(
        self, direction: RotationDirection, board: List[List[MinoType]]
    ) -> bool:
        if self.minoType == MinoType.MINO_O:  # O-pieces can't rotate
            return True

        new_minoArr = self._getRotatedMinoArr(direction.value)

        # check if rotation works with the SRS tests
        tests = (SRS_TESTS if self.minoType != MinoType.MINO_I else SRS_TESTS_I)[
            self.spin
        ][direction.value]
        for test_x, test_y in tests:
            new_mino = Tetrimino(
                self.minoType, x=self.x + test_x, y=self.y - test_y, minoArr=new_minoArr
            )
            if new_mino.isValidPosition(board):
                # save rotation if successful
                self._spin += direction.value
                self.minoArr = new_minoArr
                self.x += test_x
                self.y -= test_y
                self.lockDelayStart = -1
                self.updateHint(board)
                return True
        return False

    def _getRotatedMinoArr(self, direction: int) -> List[List[int]]:
        new_minoArr = self.minoArr
        while direction != 0:
            # perform the rotation
            # https://stackoverflow.com/questions/8421337/rotating-a-two-dimensional-array-in-python
            new_minoArr = (
                list(zip(*new_minoArr[::-1]))
                if direction > 0
                else list(zip(*new_minoArr))[::-1]
            )
            direction -= 1 if direction > 0 else -1
        return new_minoArr

    def moveX(self, direction: int, board: List[List[MinoType]]) -> bool:
        new_x = self.x + direction
        new_mino = Tetrimino(self.minoType, x=new_x, y=self.y, minoArr=self.minoArr)

        # check if move is valid
        if not new_mino.isValidPosition(board):
            return False

        # save x translation
        self.x = new_x
        self.lockDelayStart = -1
        self.updateHint(board)
        return True

    def softDrop(self, board: List[List[MinoType]]) -> bool:
        new_mino = Tetrimino(
            self.minoType, x=self.x, y=self.y + 1, minoArr=self.minoArr
        )
        # move piece down only if it's okay to do so
        if not new_mino.isValidPosition(board):
            return False

        self.y += 1
        return True

    def hardDrop(self, board: List[List[MinoType]]) -> None:
        new_mino = Tetrimino(
            self.minoType, x=self.x, y=self.y + 1, minoArr=self.minoArr
        )
        # pretend we are soft dropping until we can't go any further
        while new_mino.isValidPosition(board):
            new_mino.y += 1
            self.y += 1

    def updateHint(self, board: List[List[MinoType]]) -> None:
        # make a copy of the current mino, see how far it hard drops to,
        # that is where the hint should be drawn
        hint_mino = Tetrimino(self.minoType, x=self.x, y=self.y, minoArr=self.minoArr)
        hint_mino.hardDrop(board)
        self.hintY = hint_mino.y

    def isValidPosition(self, board: List[List[MinoType]]) -> bool:
        # check collision with other minos and out of bounds
        return not (self._isOutOfBounds() or self._isColliding(board))

    def _isOutOfBounds(self) -> bool:
        # for each block, check if it exceeds the bounds of the board
        for i, row in enumerate(self.minoArr):
            for j, el in enumerate(row):
                if not el:
                    continue
                block_x = j + self.x
                block_y = i + self.y
                if (not 0 <= block_x < BOARD_WIDTH) or (
                    not 0 <= block_y < BOARD_HEIGHT
                ):
                    return True
        return False

    def _isColliding(self, board: List[List[MinoType]]) -> bool:
        # for each block, check if it is already occupied by a mino block
        for i, row in enumerate(self.minoArr):
            for j, el in enumerate(row):
                if el and board[self.y + i][self.x + j] is not MinoType.NO_MINO:
                    return True
        return False


class MinoQueue:
    def __init__(self) -> None:
        self.q = deque()

    def pop(self) -> MinoType:
        return self.q.popleft()

    def topk(self, k: int) -> List[MinoType]:
        return list(islice(self.q, k))

    def push(self, mino: MinoType):
        self.q.append(mino)

    def extend(self, minos: List[MinoType]):
        self.q.extend(minos)

    def __len__(self):
        return len(self.q)


class MinoProvider:  # 7-bag
    def __init__(self, numPreviews) -> None:
        self.numPreviews = numPreviews
        self.minoQueue = MinoQueue()
        self.r = Random()
        # generate the first few batches of tetraminos
        while len(self.minoQueue) < self.numPreviews:
            self.minoQueue.extend(self._generateMinos())

    @property
    def minoPreview(self) -> List[MinoType]:
        return self.minoQueue.topk(self.numPreviews)

    def fetchMino(self) -> Tetrimino:
        mino = self.minoQueue.pop()
        if len(self.minoQueue) <= self.numPreviews:
            self.minoQueue.extend(self._generateMinos())
        return Tetrimino(mino)

    def _generateMinos(self) -> List[MinoType]:
        minoBag = [MinoType(i) for i in range(1, 8)]
        self.r.shuffle(minoBag)
        return minoBag
