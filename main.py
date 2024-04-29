import pyxel

from ttris.main import TtrisGame

# constants for pyxel.init
WINDOW_HEIGHT = 200
WINDOW_WIDTH = 180
DISPLAY_SCALE = 8
FPS = 60


class TtrisMenu:
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
        self.runGame()

    def update(self) -> None:
        pass

    def draw(self) -> None:
        pass

    def runGame(self) -> None:
        self.game = TtrisGame()
        self.game.run()
        pyxel.run(self.update, self.draw)


TtrisMenu()
