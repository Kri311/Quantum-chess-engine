"""
Board position representation.

A ``Position`` is an immutable (row, col) coordinate on the chess board.
It supports conversion to / from a flat index so that the quantum encoder
can map positions to qubit bitstrings.
"""

from __future__ import annotations

from dataclasses import dataclass

import config


@dataclass(frozen=True, slots=True)
class Position:
    """Immutable board coordinate.

    Attributes:
        row: Zero-indexed row (0 = top / Black's home row in 3×3).
        col: Zero-indexed column (0 = left).
    """

    row: int
    col: int

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:
        """Validate that the position lies within the configured board."""
        if not (0 <= self.row < config.BOARD_SIZE):
            raise ValueError(
                f"Row {self.row} out of range [0, {config.BOARD_SIZE})"
            )
        if not (0 <= self.col < config.BOARD_SIZE):
            raise ValueError(
                f"Col {self.col} out of range [0, {config.BOARD_SIZE})"
            )

    # ------------------------------------------------------------------
    # Flat-index conversions
    # ------------------------------------------------------------------

    def to_index(self, board_size: int | None = None) -> int:
        """Convert to a flat index in row-major order.

        Args:
            board_size: Side length of the board.  Defaults to
                ``config.BOARD_SIZE``.

        Returns:
            Integer index in ``[0, board_size² - 1]``.
        """
        size = board_size if board_size is not None else config.BOARD_SIZE
        return self.row * size + self.col

    @classmethod
    def from_index(cls, index: int, board_size: int | None = None) -> Position:
        """Create a ``Position`` from a flat row-major index.

        Args:
            index: Integer index in ``[0, board_size² - 1]``.
            board_size: Side length of the board.  Defaults to
                ``config.BOARD_SIZE``.

        Returns:
            Corresponding ``Position``.
        """
        size = board_size if board_size is not None else config.BOARD_SIZE
        return cls(row=index // size, col=index % size)

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return f"({self.row},{self.col})"

    def __repr__(self) -> str:
        return f"Position(row={self.row}, col={self.col})"
