import pyxel


class SoundBoard:
    def __init__(self):
        pass

    def playHardDrop(self) -> None:
        pyxel.play(2, 4)

    def playHold(self) -> None:
        pyxel.play(2, 1)

    def playMovement(self) -> None:
        pyxel.play(1, 3)

    def playRotation(self) -> None:
        pyxel.play(1, 2)

    def playLineClear(self) -> None:
        pyxel.play(0, 0)
