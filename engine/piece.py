"""
Chess piece representation.

A ``Piece`` is an immutable value object carrying a colour and a type.
The ``symbol`` property returns a single character for console rendering,
while the quantum encoder maps ``Piece`` → status bitstring via the
``Color`` attribute.
"""

from __future__ import annotations

from dataclasses import dataclass

from engine.constants import Color, PieceType


# Unicode symbols keyed by (Color, PieceType).
_SYMBOLS: dict[tuple[Color, PieceType], str] = {
    (Color.WHITE, PieceType.PAWN): "♙",
    (Color.BLACK, PieceType.PAWN): "♟",
    (Color.WHITE, PieceType.ROOK): "♖",
    (Color.BLACK, PieceType.ROOK): "♜",
    (Color.WHITE, PieceType.KNIGHT): "♘",
    (Color.BLACK, PieceType.KNIGHT): "♞",
    (Color.WHITE, PieceType.BISHOP): "♗",
    (Color.BLACK, PieceType.BISHOP): "♝",
    (Color.WHITE, PieceType.QUEEN): "♕",
    (Color.BLACK, PieceType.QUEEN): "♛",
    (Color.WHITE, PieceType.KING): "♔",
    (Color.BLACK, PieceType.KING): "♚",
}

# Fallback ASCII labels when Unicode isn't available.
_ASCII_LABELS: dict[Color, str] = {
    Color.WHITE: "W",
    Color.BLACK: "B",
}


@dataclass(frozen=True, slots=True)
class Piece:
    """Immutable chess piece.

    Attributes:
        color: The side this piece belongs to.
        piece_type: The kind of piece (``PAWN`` in the 3×3 prototype).
    """

    color: Color
    piece_type: PieceType

    @property
    def symbol(self) -> str:
        """Return a single Unicode character representing this piece.

        Returns:
            A Unicode chess symbol (e.g. ``♙``).
        """
        return _SYMBOLS.get(
            (self.color, self.piece_type),
            _ASCII_LABELS[self.color],
        )

    @property
    def ascii_label(self) -> str:
        """Return a plain ASCII label (``'W'`` or ``'B'``).

        Returns:
            Single-character colour label.
        """
        return _ASCII_LABELS[self.color]

    def __str__(self) -> str:
        return self.symbol

    def __repr__(self) -> str:
        return f"Piece({self.color.name}, {self.piece_type.name})"
