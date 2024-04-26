import pyxel


class Score:
    def __init__(self):
        pass

    @staticmethod
    def draw(board):
        pyxel.text(15, 60, f"Lines\n{board.linesCleared}", 7)
