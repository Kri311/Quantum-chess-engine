"""
Position evaluator and win-condition detector.

``Evaluator`` provides both a numeric heuristic (used by minimax and
the quantum evaluation oracle) and concrete win / draw detection.
"""

from __future__ import annotations

from engine.board import Board
from engine.constants import Color, PieceType
from engine.move_generator import MoveGenerator
from engine.position import Position
from engine.state import GameState


class Evaluator:
    """Heuristic evaluator and terminal-state detector."""

    # ------------------------------------------------------------------
    # Win / draw
    # ------------------------------------------------------------------

    @staticmethod
    def winner(state: GameState) -> Color | None:
        """Return the winning colour, or ``None`` if the game is ongoing.

        Checkmate: The current player is in check and has no legal moves.
        In this case, the opponent wins.

        Args:
            state: Current game snapshot.

        Returns:
            ``Color.WHITE``, ``Color.BLACK``, or ``None``.
        """
        # Checkmate condition
        legal_moves = MoveGenerator.generate_legal_moves(state)
        if len(legal_moves) == 0:
            if MoveGenerator.is_in_check(state, state.current_turn):
                # The player whose turn it is got checkmated
                return Color.BLACK if state.current_turn is Color.WHITE else Color.WHITE

        # Fallback: Capture King condition (for legacy 3x3 or testing)
        board: Board = state.board
        white_king_alive = False
        black_king_alive = False

        for pos, piece in board.pieces_by_color(Color.WHITE):
            if piece.piece_type == PieceType.KING:
                white_king_alive = True

        for pos, piece in board.pieces_by_color(Color.BLACK):
            if piece.piece_type == PieceType.KING:
                black_king_alive = True

        if not white_king_alive and black_king_alive:
            return Color.BLACK
        if not black_king_alive and white_king_alive:
            return Color.WHITE

        return None

    @staticmethod
    def is_draw(state: GameState) -> bool:
        """Return ``True`` if the game is a draw.

        Stalemate: The current player has no legal moves but is NOT in check.

        Args:
            state: Current game snapshot.

        Returns:
            ``True`` if the position is a stalemate.
        """
        if Evaluator.winner(state) is not None:
            return False
            
        legal_moves = MoveGenerator.generate_legal_moves(state)
        if len(legal_moves) == 0:
            if not MoveGenerator.is_in_check(state, state.current_turn):
                return True
                
        return False

    # ------------------------------------------------------------------
    # Heuristic scoring
    # ------------------------------------------------------------------

    @staticmethod
    def evaluate(state: GameState) -> float:
        """Return a heuristic score for *state* from White's perspective.

        Positive values favour White; negative values favour Black.
        The score considers:

        * **Checkmate** — ±10000.0 points.
        * **Material** — each piece is scored by its standard chess value.
        * **Advancement/Position** — centre control and pawn advancement.

        Args:
            state: Current game snapshot.

        Returns:
            Floating-point evaluation.
        """
        # Terminal bonuses (Checkmate is infinite priority)
        winner = Evaluator.winner(state)
        if winner is Color.WHITE:
            return 10000.0
        elif winner is Color.BLACK:
            return -10000.0
            
        if Evaluator.is_draw(state):
            return 0.0

        board: Board = state.board
        score: float = 0.0
        max_distance: float = float(board.size - 1)

        def piece_value(pt: PieceType) -> float:
            if pt == PieceType.PAWN: return 1.0
            if pt == PieceType.KNIGHT: return 3.0
            if pt == PieceType.BISHOP: return 3.0
            if pt == PieceType.ROOK: return 5.0
            if pt == PieceType.QUEEN: return 9.0
            if pt == PieceType.KING: return 0.0 # King has no trading value
            return 1.0

        for pos, piece in board.pieces_by_color(Color.WHITE):
            val = piece_value(piece.piece_type)
            score += val  # material
            
            # Advancement bonus for pawns
            if piece.piece_type == PieceType.PAWN:
                advancement = (board.size - 1 - pos.row) / max_distance
                score += advancement * 0.5
                
            # Center control
            center_dist = abs(pos.col - board.size / 2.0) + abs(pos.row - board.size / 2.0)
            score += (board.size - center_dist) * 0.1

        for pos, piece in board.pieces_by_color(Color.BLACK):
            val = piece_value(piece.piece_type)
            score -= val  # material
            
            if piece.piece_type == PieceType.PAWN:
                advancement = pos.row / max_distance
                score -= advancement * 0.5
                
            center_dist = abs(pos.col - board.size / 2.0) + abs(pos.row - board.size / 2.0)
            score -= (board.size - center_dist) * 0.1

        return score
