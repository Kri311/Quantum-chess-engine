"""
Piece factory functions.

Provides helpers that create the initial piece layout for a given board
size.  The 3×3 prototype reads its layout from ``config.INITIAL_PIECES_3x3``
so that positions and piece types can be changed without editing source code.
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

    For the 3×3 board the layout is read from ``config.INITIAL_PIECES_3x3``.
    Edit that list to change positions, add or remove pieces.

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
        # Read layout from the global config — edit config.INITIAL_PIECES_3x3
        # to change positions, add pieces, or remove pieces.
        for row, col, color_name, type_name in config.INITIAL_PIECES_3x3:
            color = Color[color_name]
            ptype = PieceType[type_name]
            pieces[Position(row=row, col=col)] = Piece(color=color, piece_type=ptype)
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
