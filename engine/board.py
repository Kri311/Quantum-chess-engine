"""
Board state container.

``Board`` owns a ``dict[Position, Piece]`` mapping and provides all
queries / mutations needed by the rule engine and quantum encoder.
It deliberately stores *only* piece placement — turn, history, and
game-over logic belong to ``GameState``.
"""

from __future__ import annotations

import copy
from typing import Iterator

import config
from engine.constants import Color
from engine.piece import Piece
from engine.position import Position


class Board:
    """Mutable board that tracks which pieces sit on which squares.

    Attributes:
        size: Side length of the square board.
    """

    def __init__(self, size: int | None = None) -> None:
        """Initialise an empty board.

        Args:
            size: Side length.  Defaults to ``config.BOARD_SIZE``.
        """
        self.size: int = size if size is not None else config.BOARD_SIZE
        self._pieces: dict[Position, Piece] = {}

    # ------------------------------------------------------------------
    # Piece access
    # ------------------------------------------------------------------

    def place_piece(self, position: Position, piece: Piece) -> None:
        """Place *piece* on *position*, overwriting any existing occupant.

        Args:
            position: Target square.
            piece: Piece to place.

        Raises:
            ValueError: If *position* is out of bounds.
        """
        self._check_bounds(position)
        self._pieces[position] = piece

    def remove_piece(self, position: Position) -> Piece | None:
        """Remove and return the piece at *position*, or ``None``.

        Args:
            position: Square to clear.

        Returns:
            The removed ``Piece``, or ``None`` if the square was empty.
        """
        return self._pieces.pop(position, None)

    def get_piece(self, position: Position) -> Piece | None:
        """Return the piece at *position* without removing it.

        Args:
            position: Square to query.

        Returns:
            The ``Piece`` occupying the square, or ``None``.
        """
        return self._pieces.get(position)

    def is_occupied(self, position: Position) -> bool:
        """Check whether *position* contains a piece.

        Args:
            position: Square to query.

        Returns:
            ``True`` if a piece is present.
        """
        return position in self._pieces

    def is_within_bounds(self, position: Position) -> bool:
        """Check whether *position* falls inside the board.

        Args:
            position: Coordinate to test.

        Returns:
            ``True`` if both row and col are in ``[0, size)``.
        """
        return 0 <= position.row < self.size and 0 <= position.col < self.size

    # ------------------------------------------------------------------
    # Iteration & querying
    # ------------------------------------------------------------------

    def pieces_by_color(self, color: Color) -> Iterator[tuple[Position, Piece]]:
        """Yield ``(position, piece)`` pairs for every piece of *color*.

        Args:
            color: The side to filter on.

        Yields:
            Tuples of position and piece.
        """
        for pos, piece in self._pieces.items():
            if piece.color is color:
                yield pos, piece

    @property
    def all_pieces(self) -> dict[Position, Piece]:
        """Return a shallow copy of the internal piece map.

        Returns:
            ``dict[Position, Piece]`` snapshot.
        """
        return dict(self._pieces)

    @property
    def piece_count(self) -> int:
        """Return the total number of pieces on the board.

        Returns:
            Non-negative integer.
        """
        return len(self._pieces)

    # ------------------------------------------------------------------
    # Copying
    # ------------------------------------------------------------------

    def copy(self) -> Board:
        """Return a deep copy of this board.

        Returns:
            Independent ``Board`` instance with the same piece layout.
        """
        new_board = Board(size=self.size)
        new_board._pieces = copy.copy(self._pieces)
        return new_board

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def to_grid(self) -> list[list[str]]:
        """Convert the board to a 2-D list of single-character strings.

        Empty squares are represented by ``'.'``.

        Returns:
            ``size × size`` grid of characters.
        """
        grid: list[list[str]] = []
        for row in range(self.size):
            row_chars: list[str] = []
            for col in range(self.size):
                piece = self._pieces.get(Position(row, col))
                row_chars.append(piece.ascii_label if piece else ".")
            grid.append(row_chars)
        return grid

    def __str__(self) -> str:
        lines: list[str] = []
        grid = self.to_grid()
        col_header = "    " + "   ".join(str(c) for c in range(self.size))
        lines.append(col_header)
        lines.append("  +" + "---+" * self.size)
        for row_idx, row in enumerate(grid):
            row_str = f"{row_idx} | " + " | ".join(row) + " |"
            lines.append(row_str)
            lines.append("  +" + "---+" * self.size)
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"Board(size={self.size}, pieces={len(self._pieces)})"

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _check_bounds(self, position: Position) -> None:
        """Raise ``ValueError`` if *position* is outside the board."""
        if not self.is_within_bounds(position):
            raise ValueError(
                f"Position {position} is outside the "
                f"{self.size}×{self.size} board"
            )
