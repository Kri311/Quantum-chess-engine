"""
Domain constants and enumerations for the chess engine.

Every symbolic constant referenced across the engine lives here so that
no module contains magic numbers or hard-coded strings.
"""

from enum import Enum, auto


class Color(Enum):
    """Side / player colour."""

    WHITE = auto()
    BLACK = auto()

    def opponent(self) -> "Color":
        """Return the opposing colour.

        Returns:
            The other ``Color`` member.
        """
        return Color.BLACK if self is Color.WHITE else Color.WHITE

    def __str__(self) -> str:
        return self.name


class PieceType(Enum):
    """Chess piece type.

    Only ``PAWN`` is used in the 3×3 prototype.  Additional piece types
    are declared here so that future 8×8 expansion requires only adding
    movement strategies — no enum changes.
    """

    PAWN = auto()
    ROOK = auto()
    KNIGHT = auto()
    BISHOP = auto()
    QUEEN = auto()
    KING = auto()

    def __str__(self) -> str:
        return self.name


class Direction(Enum):
    """Pawn movement direction relative to the player's forward axis.

    The quantum oracle uses this to validate move legality.  In the base
    paper the direction register ``|d1 d0⟩`` encodes these three cases.
    """

    FORWARD = auto()
    DIAGONAL_LEFT = auto()
    DIAGONAL_RIGHT = auto()
    KNIGHT_MOVE = auto()

    def __str__(self) -> str:
        return self.name
