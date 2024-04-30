import pyxel

from ttris.constants import LC_NAMES, MAX_LEVEL
from ttris.enums import TSpinType


class Score:
    def __init__(self):
        pass

    @staticmethod
    def draw(board):
        pyxel.text(2, 60, f"TOTAL LINES\n{board.lines_cleared}", 7)
        pyxel.text(
            2,
            80,
            f"LEVEL {board.level if board.level != MAX_LEVEL else 'MAX'}\n{board.lines_cleared_level}/{board.curr_lc_goal_level} LINES",
            7,
        )

        # pyxel.text(2, 100, f"SCORE\n{board.score}", 7)

        if board.previous_lc > 0:
            pyxel.text(
                2,
                120,
                f"{LC_NAMES[board.previous_lc - 1].upper()}",
                7 if board.previous_lc != 4 else 9,
            )

        if board.combo_count > 0:
            pyxel.text(
                2,
                130,
                f"{board.combo_count} COMBO",
                3 if board.combo_count < 5 else 8,
            )

        if board.previous_tspin:
            pyxel.text(
                2,
                140,
                "T-SPIN" if board.previous_tspin == TSpinType.TSPIN else "T-SPIN MINI",
                2,
            )
