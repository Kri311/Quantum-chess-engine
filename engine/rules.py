"""
Move-legality rules.

``Rules`` is a stateless validator.  Every public method is a
``@staticmethod`` that receives the data it needs explicitly, making the
class easy to test and to call from both the classical engine and the
quantum oracle.
"""

from __future__ import annotations

import config
from engine.board import Board
from engine.constants import Color, Direction
from engine.move import Move
from engine.piece import Piece
from engine.position import Position
from engine.state import GameState


class Rules:
    """Pure-function rule checker for pawn chess."""

    # ------------------------------------------------------------------
    # Top-level validation
    # ------------------------------------------------------------------

    @staticmethod
    def is_valid_move(state: GameState, move: Move) -> bool:
        """Determine whether *move* is legal in *state*.

        Validates:
        1. Source square contains a piece of the current player's colour.
        2. Destination is within board bounds.
        3. Movement direction is legal for a pawn.
        4. Target square occupancy is compatible (empty for forward,
           enemy for diagonal).

        Args:
            state: Current game snapshot.
            move: Candidate move.

        Returns:
            ``True`` if the move is legal.
        """
        board: Board = state.board
        color: Color = state.current_turn

        # 1. Source must hold our piece.
        piece: Piece | None = board.get_piece(move.start)
        if piece is None or piece.color is not color:
            return False

        # 2. Destination in bounds.
        if not board.is_within_bounds(move.end):
            return False

        # 3. Direction.
        try:
            direction = move.direction(color)
        except ValueError:
            return False

        # 4. Target compatibility.
        target_piece: Piece | None = board.get_piece(move.end)

        if direction is Direction.FORWARD:
            return target_piece is None  # must be empty

        # Diagonal: must capture an enemy.
        if direction in (Direction.DIAGONAL_LEFT, Direction.DIAGONAL_RIGHT):
            return target_piece is not None and target_piece.color is not color

        return False

    # ------------------------------------------------------------------
    # Direction helpers
    # ------------------------------------------------------------------

    @staticmethod
    def is_forward_move(
        move: Move,
        color: Color,
        board_size: int | None = None,
    ) -> bool:
        """Check whether *move* represents a single-square forward step.

        Args:
            move: Candidate move.
            color: Side making the move.
            board_size: Board side length (unused for pawns but kept for
                future piece-type expansion).

        Returns:
            ``True`` if the displacement is exactly one row forward with
            no column change.
        """
        try:
            return move.direction(color) is Direction.FORWARD
        except ValueError:
            return False

    @staticmethod
    def is_diagonal_capture(
        move: Move,
        color: Color,
        board_size: int | None = None,
    ) -> bool:
        """Check whether *move* is a valid diagonal capture direction.

        Args:
            move: Candidate move.
            color: Side making the move.
            board_size: Board side length (reserved for expansion).

        Returns:
            ``True`` if the displacement is one row forward and one
            column to either side.
        """
        try:
            d = move.direction(color)
            return d in (Direction.DIAGONAL_LEFT, Direction.DIAGONAL_RIGHT)
        except ValueError:
            return False

    @staticmethod
    def check_bounds(
        position: Position,
        board_size: int | None = None,
    ) -> bool:
        """Return ``True`` if *position* is inside the board.

        Args:
            position: Coordinate to test.
            board_size: Side length.  Defaults to ``config.BOARD_SIZE``.

        Returns:
            ``True`` if both coordinates are in range.
        """
        size = board_size if board_size is not None else config.BOARD_SIZE
        return 0 <= position.row < size and 0 <= position.col < size
