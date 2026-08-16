"""
Move representation.

A ``Move`` encapsulates the transition of a piece from one square to
another, optionally flagging a capture.  The ``direction`` property maps
the displacement to a ``Direction`` enum value used by the quantum oracle.
"""

from __future__ import annotations

from dataclasses import dataclass

from engine.constants import Color, Direction
from engine.position import Position


@dataclass(frozen=True, slots=True)
class Move:
    """Immutable chess move.

    Attributes:
        start: Origin square.
        end: Destination square.
        capture: Whether this move captures an opponent piece.
    """

    start: Position
    end: Position
    capture: bool = False

    # ------------------------------------------------------------------
    # Direction detection
    # ------------------------------------------------------------------

    def direction(self, color: Color) -> Direction:
        """Determine the direction of this move relative to *color*.

        White moves toward decreasing rows (upward on screen);
        Black moves toward increasing rows (downward on screen).

        Args:
            color: The side making the move.

        Returns:
            A ``Direction`` enum member.

        Raises:
            ValueError: If the displacement does not correspond to any
                recognised pawn direction.
        """
        row_delta = self.end.row - self.start.row
        col_delta = self.end.col - self.start.col

        # Normalise so that "forward" is always +1 row_delta.
        forward_step = -1 if color is Color.WHITE else 1

        if row_delta == forward_step and col_delta == 0:
            return Direction.FORWARD
        if row_delta == forward_step and col_delta == -1:
            return Direction.DIAGONAL_LEFT
        if row_delta == forward_step and col_delta == 1:
            return Direction.DIAGONAL_RIGHT
            
        if (abs(row_delta) == 2 and abs(col_delta) == 1) or (abs(row_delta) == 1 and abs(col_delta) == 2):
            return Direction.KNIGHT_MOVE

        raise ValueError(
            f"Unrecognised pawn direction: Δrow={row_delta}, Δcol={col_delta}"
        )

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        tag = " ×" if self.capture else ""
        return f"{self.start} → {self.end}{tag}"

    def __repr__(self) -> str:
        return (
            f"Move(start={self.start!r}, end={self.end!r}, "
            f"capture={self.capture})"
        )
