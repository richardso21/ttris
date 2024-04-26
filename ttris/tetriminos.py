from collections import deque
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
    MAX_LOCKS,
    MINO_ARRS,
    SRS_TESTS,
    SRS_TESTS_I,
)
from ttris.enums import MinoType, RotationDirection, TSpinType


class Tetrimino:
    def __init__(self, minoType: MinoType, x=3, y=2, minoArr=None) -> None:
        if minoType == MinoType.NO_MINO:
            raise Exception("Mino cannot be created with MinoType == 0 (NO_MINO)")
        self.minoType: MinoType = minoType
        self.mino_arr: List[List[int]] = (
            minoArr if minoArr else MINO_ARRS[self.minoType.value - 1]
        )
        # set the position of the mino at the center of board/well by default
        self.x: int = x
        self.y: int = y
        self._spin: int = 0
        self.prev_kick = None
        self.lock_delay_start: int = -1
        self.lock_resets: int = 0

    @property
    def spin(self) -> int:
        # spin "condition" of the mino (0: 0°, 1: 90°, 2: 180°, 3: 270°)
        return self._spin % 4

    def resetPiece(self) -> None:
        # resets all mino properties to default when first initialized
        self.x = 3
        self.y = 2
        self.mino_arr = MINO_ARRS[self.minoType.value - 1]
        self._spin = 0
        self.lock_delay_start = -1

    def lockDelayExpired(self, board: List[List[MinoType]]) -> bool:
        # returns boolean if the lock for the current piece has expired
        new_mino = Tetrimino(
            self.minoType, x=self.x, y=self.y + 1, minoArr=self.mino_arr
        )
        if self.lock_resets < MAX_LOCKS:
            if not new_mino.isValidPosition(board):
                if self.lock_delay_start == -1:
                    self.lock_delay_start = pyxel.frame_count
            else:
                self.lock_delay_start = -1

        return (
            self.lock_delay_start != -1
            and pyxel.frame_count - self.lock_delay_start > LOCK_DELAY
        )

    def draw(self, x: int, y: int) -> None:
        # draws the mino at a specified x, y position on the screen
        minoTypeVal = self.minoType.value - 1
        for i, row in enumerate(self.mino_arr):
            for j, block in enumerate(row):
                if not block:
                    continue
                draw_x = (self.x + j) * BLOCK_SIZE + x
                draw_y = (self.y + i) * BLOCK_SIZE + y
                u = (minoTypeVal) * BLOCK_SIZE
                pyxel.blt(draw_x, draw_y, 1, u, 0, BLOCK_SIZE, BLOCK_SIZE)

    def drawOnBoard(self, hint=False) -> None:
        # draw the floating mino on top of the board
        # if hint is true, draw outline of piece instead with the hintY value
        minoTypeVal = self.minoType.value - 1 if not hint else 7
        minoY = self.y if not hint else self.hintY
        for i, row in enumerate(self.mino_arr):
            for j, block in enumerate(row):
                if not block:
                    continue
                x = (self.x + j) * BLOCK_SIZE + BOARD_X
                y = (minoY + i) * BLOCK_SIZE + BOARD_Y
                u = (minoTypeVal) * BLOCK_SIZE
                pyxel.blt(x, y, 1, u, 0, BLOCK_SIZE, BLOCK_SIZE)

    def drawLockDelayMeter(
        self,
        x: int,
        y: int,
        max_length: int,
        thickness=1,
        horizontal=True,
        color=8,
        last_lock_color=2,
    ) -> None:
        # draw a meter that shows how long until the piece locks
        if self.lock_delay_start == -1:
            return
        time_elapsed = pyxel.frame_count - self.lock_delay_start
        # get fraction of max_length to draw based on time elapsed
        length = int(max_length * (1 - time_elapsed / LOCK_DELAY))

        color = color if self.lock_resets < MAX_LOCKS - 1 else last_lock_color

        if horizontal:
            pyxel.rect(x, y, length, thickness, color)
        else:
            pyxel.rect(x, y, thickness, length, color)

    def rotateMino(
        self, direction: RotationDirection, board: List[List[MinoType]]
    ) -> bool:
        # rotates a mino in a specified direction with the given board state
        # returns boolean if the rotation was successful
        if self.minoType == MinoType.MINO_O:  # O-pieces can't rotate
            return False

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
                self.mino_arr = new_minoArr
                self.x += test_x
                self.y -= test_y
                self.updateHint(board)
                self.prev_kick = (test_x, test_y)

                # update lock reset
                if self.lock_delay_start != -1:
                    self.lock_resets += 1
                if self.lock_resets < MAX_LOCKS:
                    self.lock_delay_start = -1

                return True

        return False

    def _getRotatedMinoArr(self, direction: int) -> List[List[int]]:
        # returns a rotated copy of minoArr based on the direction value
        # e.g. direction = 1 -> rotate clockwise, direction = -1 -> rotate counterclockwise, direction = 2 -> rotate 180°
        new_minoArr = self.mino_arr
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

    def checkTSpin(self, board: List[List[MinoType]]) -> TSpinType:
        # check if the current T piece is in a position only possible after a T-spin
        if self.minoType != MinoType.MINO_T:
            return TSpinType.NONE

        # if a TST kick was used most recently, it is definitely a T-spin
        # (kick that pushes tetrimino two blocks down and one to either side)
        if self.prev_kick and abs(self.prev_kick[0]) == 1 and self.prev_kick[1] == -2:
            return TSpinType.TSPIN

        # check how many corners around the T piece have another block
        corner_count = {}
        for corner in [(0, 0), (2, 0), (0, 2), (2, 2)]:
            corner_count[corner] = 0
            x, y = corner
            if (
                (not 0 <= self.x + x < BOARD_WIDTH)  # out of bounds counts as filled
                or (not 0 <= self.y + y < BOARD_HEIGHT)
                or board[self.y + y][self.x + x] is not MinoType.NO_MINO
            ):
                corner_count[corner] = 1

        if sum(corner_count.values()) < 3:
            return TSpinType.NONE

        # check if two of the filled corners are along the forward face of the T piece
        forward_corners = [(0, 0), (2, 0), (2, 2), (0, 2), (0, 0)][
            self.spin : self.spin + 2
        ]
        if sum(corner_count[corner] for corner in forward_corners) < 2:
            return TSpinType.MINI
        return TSpinType.TSPIN

    def moveX(self, direction: int, board: List[List[MinoType]]) -> bool:
        # move the mino in the x direction by the specified amount
        new_x = self.x + direction
        new_mino = Tetrimino(self.minoType, x=new_x, y=self.y, minoArr=self.mino_arr)

        # check if move is valid
        if not new_mino.isValidPosition(board):
            return False

        # save x translation
        self.x = new_x
        self.updateHint(board)

        # update lock reset
        if self.lock_delay_start != -1:
            self.lock_resets += 1
        if self.lock_resets < MAX_LOCKS:
            self.lock_delay_start = -1

        return True

    def softDrop(self, board: List[List[MinoType]]) -> bool:
        # drop the mino down by 1 block position
        new_mino = Tetrimino(
            self.minoType, x=self.x, y=self.y + 1, minoArr=self.mino_arr
        )
        # move piece down only if it's okay to do so
        if not new_mino.isValidPosition(board):
            return False

        self.y += 1
        return True

    def hardDrop(self, board: List[List[MinoType]]) -> None:
        # drop the mino down until it can't go any further
        new_mino = Tetrimino(
            self.minoType, x=self.x, y=self.y + 1, minoArr=self.mino_arr
        )
        # pretend we are soft dropping until we can't go any further
        while new_mino.isValidPosition(board):
            new_mino.y += 1
            self.y += 1

    def updateHint(self, board: List[List[MinoType]]) -> None:
        # make a copy of the current mino, see how far it hard drops to,
        # that is where the hint should be drawn
        hint_mino = Tetrimino(self.minoType, x=self.x, y=self.y, minoArr=self.mino_arr)
        hint_mino.hardDrop(board)
        self.hintY = hint_mino.y

    def isValidPosition(self, board: List[List[MinoType]]) -> bool:
        # check collision with other minos and out of bounds
        return not (self._isOutOfBounds() or self._isColliding(board))

    def _isOutOfBounds(self) -> bool:
        # for each block, check if it exceeds the bounds of the board
        for i, row in enumerate(self.mino_arr):
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
        for i, row in enumerate(self.mino_arr):
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
