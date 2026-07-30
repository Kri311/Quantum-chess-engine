"""
Legal-move generator.

``MoveGenerator`` produces every legal ``Move`` for the current player
in a given ``GameState``.  It is designed around a *strategy* approach:
piece-specific logic is encapsulated in private methods so that adding
new piece types later only requires extending this class — no changes
to ``Rules`` or ``Board``.
"""

from __future__ import annotations

from engine.board import Board
from engine.constants import Color, PieceType
from engine.move import Move
from engine.piece import Piece
from engine.position import Position
from engine.rules import Rules
from engine.state import GameState


class MoveGenerator:
    """Generates all legal moves for the active player."""

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @staticmethod
    def generate_legal_moves(state: GameState) -> list[Move]:
        """Return every legal move for the player whose turn it is.

        Args:
            state: Current game snapshot.

        Returns:
            List of legal ``Move`` objects (may be empty if no moves
            are available).
        """
        moves: list[Move] = []
        color: Color = state.current_turn

        for position, piece in state.board.pieces_by_color(color):
            moves.extend(
                MoveGenerator._generate_moves_for_piece(
                    state, position, piece
                )
            )

        return moves

    @staticmethod
    def generate_moves_for_position(
        state: GameState,
        position: Position,
    ) -> list[Move]:
        """Return legal moves for the piece at *position*.

        Args:
            state: Current game snapshot.
            position: Square to query.

        Returns:
            List of legal ``Move`` objects originating from *position*.
        """
        piece: Piece | None = state.board.get_piece(position)
        if piece is None:
            return []
        if piece.color is not state.current_turn:
            return []
        return MoveGenerator._generate_moves_for_piece(state, position, piece)

    # ------------------------------------------------------------------
    # Piece-specific generators (strategy methods)
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_moves_for_piece(
        state: GameState,
        position: Position,
        piece: Piece,
    ) -> list[Move]:
        """Dispatch to the piece-type–specific generator.

        Args:
            state: Current game snapshot.
            position: Square the piece sits on.
            piece: The piece to generate moves for.

        Returns:
            List of candidate ``Move`` objects that pass validation.
        """
        if piece.piece_type is PieceType.PAWN:
            return MoveGenerator._pawn_moves(state, position, piece.color)

        # Future piece types would be dispatched here.
        return []

    @staticmethod
    def _pawn_moves(
        state: GameState,
        position: Position,
        color: Color,
    ) -> list[Move]:
        """Generate all legal pawn moves from *position*.

        A pawn may:
        * Move one square forward if the target is empty.
        * Capture diagonally if the target holds an enemy piece.

        Args:
            state: Current game snapshot.
            position: Source square.
            color: Colour of the pawn.

        Returns:
            List of legal ``Move`` objects.
        """
        board: Board = state.board
        forward_row = position.row + (-1 if color is Color.WHITE else 1)
        candidates: list[Move] = []

        # Forward move.
        if 0 <= forward_row < board.size:
            forward_pos = Position(forward_row, position.col)
            forward_move = Move(start=position, end=forward_pos, capture=False)
            if Rules.is_valid_move(state, forward_move):
                candidates.append(forward_move)

        # Diagonal captures.
        for col_offset in (-1, 1):
            new_col = position.col + col_offset
            if 0 <= forward_row < board.size and 0 <= new_col < board.size:
                diag_pos = Position(forward_row, new_col)
                diag_move = Move(start=position, end=diag_pos, capture=True)
                if Rules.is_valid_move(state, diag_move):
                    candidates.append(diag_move)

        return candidates
