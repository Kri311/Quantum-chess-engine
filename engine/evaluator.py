"""
Position evaluator and win-condition detector.

``Evaluator`` provides both a numeric heuristic (used by minimax and
the quantum evaluation oracle) and concrete win / draw detection.
"""

from __future__ import annotations

from engine.board import Board
from engine.constants import Color
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

        A player wins by:
        * Capturing the opponent's last pawn.
        * Reaching the promotion row (row 0 for White, last row for Black).

        Args:
            state: Current game snapshot.

        Returns:
            ``Color.WHITE``, ``Color.BLACK``, or ``None``.
        """
        board: Board = state.board

        white_alive = False
        black_alive = False

        for pos, piece in board.pieces_by_color(Color.WHITE):
            white_alive = True
            if pos.row == 0:
                return Color.WHITE

        for pos, piece in board.pieces_by_color(Color.BLACK):
            black_alive = True
            if pos.row == board.size - 1:
                return Color.BLACK

        if not white_alive:
            return Color.BLACK
        if not black_alive:
            return Color.WHITE

        return None

    @staticmethod
    def is_draw(state: GameState) -> bool:
        """Return ``True`` if the game is a draw.

        The game is drawn when the current player has no legal moves and
        neither side has won.

        Args:
            state: Current game snapshot.

        Returns:
            ``True`` if the position is a stalemate.
        """
        if Evaluator.winner(state) is not None:
            return False
        return len(MoveGenerator.generate_legal_moves(state)) == 0

    # ------------------------------------------------------------------
    # Heuristic scoring
    # ------------------------------------------------------------------

    @staticmethod
    def evaluate(state: GameState) -> float:
        """Return a heuristic score for *state* from White's perspective.

        Positive values favour White; negative values favour Black.
        The score considers:

        * **Material** — each surviving pawn is worth 1.0 point.
        * **Advancement** — pawns closer to the promotion row receive a
          bonus proportional to (distance covered / total distance).

        Args:
            state: Current game snapshot.

        Returns:
            Floating-point evaluation.
        """
        board: Board = state.board
        score: float = 0.0
        max_distance: float = float(board.size - 1)

        for pos, piece in board.pieces_by_color(Color.WHITE):
            score += 1.0  # material
            # White moves upward: advancement = (start_row - current_row).
            advancement = (board.size - 1 - pos.row) / max_distance
            score += advancement * 0.5

        for pos, piece in board.pieces_by_color(Color.BLACK):
            score -= 1.0  # material
            advancement = pos.row / max_distance
            score -= advancement * 0.5

        # Terminal bonuses.
        winner = Evaluator.winner(state)
        if winner is Color.WHITE:
            score += 100.0
        elif winner is Color.BLACK:
            score -= 100.0

        return score
