import pyxel

from ttris.constants import MAX_LEVEL


class Score:
    def __init__(self):
        pass

    @staticmethod
    def draw(board):
        pyxel.text(2, 60, f"Total Lines\n{board.lines_cleared}", 7)
        pyxel.text(
            2,
            80,
            f"Level {board.level if board.level != MAX_LEVEL else 'MAX'}\n{board.lines_cleared_level}/{board.curr_lc_goal_level} Lines",
            7,
        )
