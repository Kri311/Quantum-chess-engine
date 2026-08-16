"""
Classical heuristic evaluator.

Provides a static evaluation function for leaf nodes in the minimax
tree and a per-move scoring function for move ordering.
"""

from __future__ import annotations

from engine.constants import Color
from engine.evaluator import Evaluator
from engine.move import Move
from engine.state import GameState


class HeuristicEvaluator:
    """Classical heuristic for position and move evaluation.

    All scores are from White's perspective: positive favours White,
    negative favours Black.
    """

    # ------------------------------------------------------------------
    # Position evaluation
    # ------------------------------------------------------------------

    @staticmethod
    def evaluate(state: GameState) -> float:
        """Return a heuristic score for the current position.

        Delegates to ``engine.Evaluator.evaluate`` and adds
        additional strategic considerations.

        Args:
            state: Current game snapshot.

        Returns:
            Floating-point evaluation from White's perspective.
        """
        base_score = Evaluator.evaluate(state)

        # Bonus for having more legal moves (mobility).
        from engine.move_generator import MoveGenerator

        moves = MoveGenerator.generate_legal_moves(state)
        mobility_bonus = len(moves) * 0.1
        if state.current_turn is Color.WHITE:
            base_score += mobility_bonus
        else:
            base_score -= mobility_bonus

        return base_score

    # ------------------------------------------------------------------
    # Move scoring
    # ------------------------------------------------------------------

    @staticmethod
    def score_move(state: GameState, move: Move) -> float:
        """Score an individual move for move-ordering purposes.

        Higher scores indicate more promising moves, used to improve
        alpha-beta pruning efficiency.

        Args:
            state: Current game snapshot.
            move: The move to score.

        Returns:
            Floating-point move score.
        """
        score = 0.0

        # Captures are generally good.
        if move.capture:
            score += 10.0

        # Advancing toward promotion is good for pawns.
        piece = state.board.get_piece(move.start)
        board_size = state.board.size
        
        if piece and piece.piece_type.name == "PAWN":
            if state.current_turn is Color.WHITE:
                advancement = (board_size - 1 - move.end.row)
                score += advancement * 2.0
            else:
                score += move.end.row * 2.0

        # Centre control preference for all pieces (highly important for knights)
        centre = board_size / 2.0
        distance_to_centre = abs(move.end.col - centre) + abs(move.end.row - centre)
        score += ((board_size * 2) - distance_to_centre) * 0.5

        return score
