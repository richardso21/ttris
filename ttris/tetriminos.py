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
    MINO_SHADOW,
)


class MinoType(Enum):
    NO_MINO = 0
    MINO_I = 1
    MINO_O = 2
    MINO_T = 3
    MINO_S = 4
    MINO_Z = 5
    MINO_J = 6
    MINO_L = 7


class Tetrimino:
    def __init__(self, minoType: MinoType, x=3, y=2, minoArr=None) -> None:
        if minoType == MinoType.NO_MINO:
            raise Exception("Mino cannot be created with MinoType == 0 (NO_MINO)")
        self.minoType = minoType
        self.minoArr = minoArr if minoArr else MINO_ARRS[self.minoType.value - 1]
        # set the position of the mino at the center of board/well by default
        self.x = x
        self.y = y
        self._spin = 0
        self.lockDelayStart = -1

    @property
    def spin(self):
        return self._spin % 4

    def draw(self, hint=False) -> None:
        minoTypeVal = self.minoType.value - 1 if not hint else 7
        minoY = self.y if not hint else self.hintY
        for i, row in enumerate(self.minoArr):
            for j, block in enumerate(row):
                if not block:
                    continue
                x = (self.x + j) * BLOCK_SIZE + BOARD_X
                y = (minoY + i) * BLOCK_SIZE + BOARD_Y
                u = (minoTypeVal) * BLOCK_SIZE
                pyxel.blt(x, y, 1, u, 0, BLOCK_SIZE, BLOCK_SIZE)

    def rotateMino(self, direction: int, board: List[List[MinoType]]) -> None:
        if self.minoType == MinoType.MINO_O:  # O-pieces can't rotate
            return

        # perform the rotation
        # https://stackoverflow.com/questions/8421337/rotating-a-two-dimensional-array-in-python
        new_minoArr = (
            list(zip(*self.minoArr[::-1]))
            if direction > 0
            else list(zip(*self.minoArr))[::-1]
        )
        new_mino = Tetrimino(self.minoType, x=self.x, y=self.y, minoArr=new_minoArr)

        # check if rotation works
        if not new_mino.isValidPosition(board):
            return

        # save rotation if successful
        self._spin += direction
        self.minoArr = new_minoArr
        self.lockDelayStart = -1
        self.updateHint(board)

    def moveX(self, direction: int, board: List[List[MinoType]]) -> None:
        new_x = self.x + direction
        new_mino = Tetrimino(self.minoType, x=new_x, y=self.y, minoArr=self.minoArr)

        # check if move is valid
        if not new_mino.isValidPosition(board):
            return

        # save x translation
        self.x = new_x
        self.updateHint(board)

    def softDrop(self, board: List[List[MinoType]]) -> bool:
        # returns boolean if piece is still falling (including lock delay)
        new_mino = Tetrimino(
            self.minoType, x=self.x, y=self.y + 1, minoArr=self.minoArr
        )

        if not new_mino.isValidPosition(board):
            # if something's blocking below, start lock delay, return false
            # once delay expires
            if self.lockDelayStart == -1:
                self.lockDelayStart = pyxel.frame_count
            return pyxel.frame_count - self.lockDelayStart <= LOCK_DELAY

        # reset lock delay
        self.lockDelayStart = -1
        self.y += 1
        return True

    def hardDrop(self, board: List[List[MinoType]]) -> None:
        # pretend we are soft dropping until we can't go any further
        new_mino = Tetrimino(
            self.minoType, x=self.x, y=self.y + 1, minoArr=self.minoArr
        )
        while new_mino.isValidPosition(board):
            new_mino.y += 1
            self.y += 1

    def updateHint(self, board: List[List[MinoType]]) -> None:
        # make a copy of the current mino, see how far it hard drops to,
        # then take the y-value of that mino after the drop
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
