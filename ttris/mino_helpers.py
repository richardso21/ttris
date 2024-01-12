from collections import deque
from enum import Enum
from itertools import islice
from random import Random
from typing import List

from ttris.tetriminos import Tetrimino


class MinoType(Enum):
    NO_MINO = 0
    MINO_I = 1
    MINO_O = 2
    MINO_T = 3
    MINO_S = 4
    MINO_Z = 5
    MINO_J = 6
    MINO_L = 7


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
            self._generateMinos()
        return Tetrimino(mino)

    def _generateMinos(self) -> List[MinoType]:
        minoBag = [MinoType(i) for i in range(1, 8)]
        self.r.shuffle(minoBag)
        return minoBag
