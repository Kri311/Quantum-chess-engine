"""
Piece factory functions.

Provides helpers that create the initial piece layout for a given board
size.  The 3×3 prototype places one white pawn on the bottom-centre
square and one black pawn on the top-centre square.
"""

from __future__ import annotations

from engine.constants import Color, PieceType
from engine.piece import Piece
from engine.position import Position

import config


def create_initial_pieces(
    board_size: int | None = None,
) -> dict[Position, Piece]:
    """Create the starting piece layout.

    For the 3×3 board:
        * White pawn at ``(2, 1)`` — bottom-centre.
        * Black pawn at ``(0, 1)`` — top-centre.

    Args:
        board_size: Side length.  Defaults to ``config.BOARD_SIZE``.

    Returns:
        Dictionary mapping each occupied ``Position`` to its ``Piece``.
    """
    size = board_size if board_size is not None else config.BOARD_SIZE

    white_pawn = Piece(color=Color.WHITE, piece_type=PieceType.PAWN)
    black_pawn = Piece(color=Color.BLACK, piece_type=PieceType.PAWN)

    pieces: dict[Position, Piece] = {}

    if size == 3:
        # Single pawn per side — research prototype layout.
        pieces[Position(row=size - 1, col=1)] = white_pawn
        pieces[Position(row=0, col=1)] = black_pawn
    else:
        # Generic layout: full row of pawns for each side.
        for col in range(size):
            pieces[Position(row=size - 2, col=col)] = white_pawn
            pieces[Position(row=1, col=col)] = black_pawn
            
        # Place remaining pieces
        piece_order = [
            PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
            PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK
        ]
        
        for col, p_type in enumerate(piece_order):
            if col < size:
                pieces[Position(row=size - 1, col=col)] = Piece(Color.WHITE, p_type)
                pieces[Position(row=0, col=col)] = Piece(Color.BLACK, p_type)

    return pieces
