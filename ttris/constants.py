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

LOCK_DELAY = 30  # 30 frames = .5 seconds

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

SRS_TESTS = [  # Super Rotation System
    [  # spin 0
        [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],  # 0 -cw-> 1
        [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],  # 0 -ccw-> 3
    ],
    [  # spin 1
        [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],  # 1 -cw-> 2
        [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],  # 1 -ccw-> 0
    ],
    [  # spin 2
        [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],  # 2 -cw-> 3
        [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],  # 2 -ccw-> 1
    ],
    [  # spin 3
        [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],  # 3 -cw-> 0
        [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],  # 3 -ccw-> 2
    ],
]

SRS_TESTS_I = [  # separate tests for I piece
    [  # spin 0
        [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],  # 0 -cw-> 1
        [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],  # 0 -ccw-> 3
    ],
    [  # spin 1
        [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],  # 1 -cw-> 2
        [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],  # 1 -ccw-> 0
    ],
    [  # spin 2
        [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],  # 2 -cw-> 3
        [(0, 0), (1, 0), (-2, 0), (-1, 2), (-2, 1)],  # 2 -ccw-> 1
    ],
    [  # spin 3
        [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],  # 3 -cw-> 0
        [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],  # 3 -ccw-> 2
    ],
]
