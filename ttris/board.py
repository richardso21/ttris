from typing import List

import pyxel

from ttris.constants import (
    BLOCK_SIZE,
    BOARD_HEIGHT,
    BOARD_WIDTH,
    BOARD_X,
    BOARD_Y,
    OVERFLOW_HEIGHT,
)
from ttris.controls import Controller
from ttris.enums import MinoType
from ttris.score import Score
from ttris.sound import SoundBoard
from ttris.tetriminos import MinoProvider, Tetrimino


class Board:
    def __init__(self, das: int, arr: int, lookahead: int):
        # make empty board
        self.board_arr: List[List[MinoType]] = [
            [MinoType.NO_MINO] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)
        ]
        # start a queue of tetraminos
        self.mino_provider = MinoProvider(lookahead)

        self.spawnMino()
        self.hold = None
        self.hold_lock = False

        self.controller = Controller(das, arr, self)
        self.sound_board = SoundBoard()

        self.soft_drop_timer: int = 45
        self.lines_cleared: int = 0
        self.combo_count: int = 0
        self.hard_drop_tick: bool = False

    def update(self) -> None:
        self.hard_drop_tick = False
        # check controls
        self.controller.checkControls()

        # piece gravity
        if pyxel.frame_count % self.soft_drop_timer == 0:
            self.curr_piece.softDrop(self.board_arr)

        # check lock delay of piece, hard drop if lock expires
        if self.curr_piece.lockDelayExpired(self.board_arr):
            self.hardDropCurrPiece()

        # check and clear any lines on the board
        self.clearLines()

    def draw(self) -> None:
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
        for i, row in enumerate(self.board_arr):
            for j, block in enumerate(row):
                if block == MinoType.NO_MINO:
                    continue
                x = j * BLOCK_SIZE + BOARD_X
                y = i * BLOCK_SIZE + BOARD_Y
                u = (block.value - 1) * BLOCK_SIZE
                pyxel.blt(x, y, 1, u, 0, BLOCK_SIZE, BLOCK_SIZE)

        self.curr_piece.drawOnBoard(hint=True)  # draw hint first, then the actual piece
        self.curr_piece.drawOnBoard()

        # draw holding piece
        pyxel.rectb(
            BOARD_X - 48, BOARD_Y + (BLOCK_SIZE * OVERFLOW_HEIGHT) - 10, 48, 32, 13
        )
        pyxel.text(
            BOARD_X - 32, BOARD_Y + (BLOCK_SIZE * OVERFLOW_HEIGHT) - 7, "HOLD", 7
        )
        if self.hold:
            if self.hold_lock:
                pyxel.dither(0.5)
            self.hold.draw(
                (
                    -10
                    if self.hold.minoType not in [MinoType.MINO_I, MinoType.MINO_O]
                    else -14
                ),
                15,
            )
            pyxel.dither(1)

        # draw minos/pieces in queue
        pyxel.rectb(
            BOARD_X + (BLOCK_SIZE * BOARD_WIDTH),
            BOARD_Y + (BLOCK_SIZE * OVERFLOW_HEIGHT) - 10,
            48,
            130,
            13,
        )
        pyxel.text(
            BOARD_X + (BLOCK_SIZE * BOARD_WIDTH) + 16,
            BOARD_Y + (BLOCK_SIZE * OVERFLOW_HEIGHT) - 7,
            "NEXT",
            7,
        )
        for i, minoType in enumerate(self.mino_provider.minoPreview):
            Tetrimino(minoType).draw(
                115 + (4 if minoType not in [MinoType.MINO_I, MinoType.MINO_O] else 0),
                15 + (i * 24) - (4 if minoType is MinoType.MINO_I else 0),
            )

        # update score and other game info besides board
        Score.draw(self)

    def clearLines(self) -> None:
        # check for any line clears and construct new board if necessary
        clear_inds = [i for i, row in enumerate(self.board_arr) if all(row)]
        if len(clear_inds):  # some lines need to be cleared
            new_board_arr = [[MinoType.NO_MINO] * BOARD_WIDTH for _ in clear_inds]
            new_board_arr.extend(
                [row for i, row in enumerate(self.board_arr) if i not in clear_inds]
            )
            self.board_arr = new_board_arr
            # need to re-update hint with new board state
            self.curr_piece.updateHint(self.board_arr)
            self.lines_cleared += len(clear_inds)
            self.combo_count += 1
            self.sound_board.playLineClear(self.combo_count)
            if len(clear_inds) == 4:
                self.sound_board.playLCSpecial()
        elif self.hard_drop_tick:
            self.combo_count = 0

    def holdCurrPiece(self) -> None:
        if self.hold_lock:
            return
        # swap hold and current item
        tmp = self.hold
        self.hold = self.curr_piece
        # or get next item in queue if hold is empty
        self.curr_piece = tmp if tmp else self.mino_provider.fetchMino()
        self.curr_piece.updateHint(self.board_arr)

        # reset x-y and rotation state of the now held piece
        self.hold.resetPiece()

        # prevent infinite holding
        self.hold_lock = True
        self.sound_board.playHold()

    def hardDropCurrPiece(self) -> None:
        self.curr_piece.hardDrop(self.board_arr)

        # copy piece to board
        for i, row in enumerate(self.curr_piece.mino_arr):
            for j, block in enumerate(row):
                if not block:
                    continue
                self.board_arr[self.curr_piece.y + i][
                    self.curr_piece.x + j
                ] = self.curr_piece.minoType

            # play hard drop sound
            self.sound_board.playHardDrop()

        # get new piece
        self.spawnMino()
        self.hold_lock = False
        self.hard_drop_tick = True

    def spawnMino(self) -> None:
        self.curr_piece = self.mino_provider.fetchMino()
        self.curr_piece.updateHint(self.board_arr)
