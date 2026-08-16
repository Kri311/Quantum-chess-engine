"""
Global configuration for the Quantum Chess Engine.

All tunable parameters are centralized here to avoid magic numbers
and provide a single source of truth across all modules.
"""

# ---------------------------------------------------------------------------
# Board configuration
# ---------------------------------------------------------------------------

BOARD_SIZE: int = 8
"""Side length of the square board (3 for the research prototype, 8 for standard)."""

TOTAL_SQUARES: int = BOARD_SIZE * BOARD_SIZE
"""Total number of squares on the board."""

# ---------------------------------------------------------------------------
# Quantum simulation
# ---------------------------------------------------------------------------

QUANTUM_SHOTS: int = 1024
"""Number of measurement shots per quantum circuit execution."""

QUANTUM_BACKEND: str = "aer_simulator"
"""Qiskit Aer backend identifier used for local simulation."""

QUANTUM_NOISE_ENABLED: bool = False
"""Whether to enable realistic quantum noise simulation."""

QUANTUM_NOISE_PROB: float = 0.001
"""Probability of depolarizing error for single-qubit gates (two-qubit gets 10x this)."""

# ---------------------------------------------------------------------------
# Pygame / UI
# ---------------------------------------------------------------------------

FPS: int = 60
"""Target frames per second for the graphical interface."""

WINDOW_WIDTH: int = 600
"""Default window width in pixels."""

WINDOW_HEIGHT: int = 680
"""Default window height in pixels (extra space for status bar)."""

ANIMATION_SPEED: float = 8.0
"""Piece movement animation speed (pixels per frame factor)."""

# ---------------------------------------------------------------------------
# Colours (RGB tuples used by the renderer)
# ---------------------------------------------------------------------------

COLOR_LIGHT_SQUARE: tuple[int, int, int] = (240, 217, 181)
COLOR_DARK_SQUARE: tuple[int, int, int] = (181, 136, 99)
COLOR_HIGHLIGHT: tuple[int, int, int] = (130, 170, 100)
COLOR_SELECTED: tuple[int, int, int] = (186, 202, 68)
COLOR_BACKGROUND: tuple[int, int, int] = (48, 46, 43)
COLOR_TEXT: tuple[int, int, int] = (255, 255, 255)
COLOR_WHITE_PIECE: tuple[int, int, int] = (255, 255, 255)
COLOR_BLACK_PIECE: tuple[int, int, int] = (0, 0, 0)
