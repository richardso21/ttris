import pyxel

from ttris.board import Board
from ttris.constants import DISPLAY_SCALE, FPS, WINDOW_HEIGHT, WINDOW_WIDTH


class TtrisGame:
    def __init__(self) -> None:
        pyxel.init(
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
            title="ttris",
            display_scale=DISPLAY_SCALE,
            fps=FPS,
        )
        pyxel.screen_mode(2)
        pyxel.load("assets/ttris.pyxres")
        self.board = Board(10, 1, 5)
        pyxel.run(self.update, self.draw)

    def update(self) -> None:
        self.board.update()
        pass

    def draw(self) -> None:
        pyxel.cls(0)
        self.board.draw()


TtrisGame()
