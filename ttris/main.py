import pyxel

from ttris.board import Board


class TtrisGame:
    def __init__(self) -> None:
        self.board = Board(10, 1, 5)

    def update(self) -> None:
        self.board.update()
        pass

    def draw(self) -> None:
        pyxel.cls(0)
        self.board.draw()

    def run(self) -> None:
        pyxel.run(self.update, self.draw)
