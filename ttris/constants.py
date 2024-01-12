WINDOW_HEIGHT = 200
WINDOW_WIDTH = 180
DISPLAY_SCALE = 8
FPS = 60

OVERFLOW_HEIGHT = 5
BOARD_HEIGHT = 25
BOARD_WIDTH = 10

BLOCK_SIZE = 8

BOARD_X = 50
BOARD_Y = -10

LOCK_DELAY = 60  # 60 frames = 1 second

MINO_ARRS = [
    [  # I
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
    [  # O
        [0, 1, 1, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0],
    ],
    [[0, 1, 0], [1, 1, 1], [0, 0, 0]],  # T
    [[0, 1, 1], [1, 1, 0], [0, 0, 0]],  # S
    [[1, 1, 0], [0, 1, 1], [0, 0, 0]],  # Z
    [[1, 0, 0], [1, 1, 1], [0, 0, 0]],  # J
    [[0, 0, 1], [1, 1, 1], [0, 0, 0]],  # L
]
