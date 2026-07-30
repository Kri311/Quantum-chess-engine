"""
Minimax search with alpha-beta pruning.

Provides a classical game-tree search engine that explores all
possible move sequences up to a given depth and selects the move
that maximises (or minimises) the heuristic evaluation.
"""

from __future__ import annotations

import math

from ai.heuristic import HeuristicEvaluator
from engine.constants import Color
from engine.evaluator import Evaluator
from engine.move import Move
from engine.move_generator import MoveGenerator
from engine.state import GameState


class MinimaxEngine:
    """Classical minimax search with alpha-beta pruning.

    Attributes:
        max_depth: Maximum search depth.
    """

    def __init__(self, max_depth: int = 6) -> None:
        """Initialise the minimax engine.

        Args:
            max_depth: Maximum plies to search. Defaults to 6
                (sufficient for the 3x3 board's shallow game tree).
        """
        self.max_depth: int = max_depth

    def search(self, state: GameState) -> Move | None:
        """Find the best move for the current player.

        Args:
            state: Current game snapshot.

        Returns:
            The best Move, or None if no legal moves exist.
        """
        moves = MoveGenerator.generate_legal_moves(state)
        if not moves:
            return None

        # Sort moves by heuristic score for better pruning.
        moves.sort(
            key=lambda m: HeuristicEvaluator.score_move(state, m),
            reverse=True,
        )

        maximizing = state.current_turn is Color.WHITE
        best_move: Move | None = None
        best_score = -math.inf if maximizing else math.inf

        for move in moves:
            new_state = state.apply_move(move)
            score = self._minimax(
                new_state,
                depth=self.max_depth - 1,
                alpha=-math.inf,
                beta=math.inf,
                maximizing=not maximizing,
            )

            if maximizing and score > best_score:
                best_score = score
                best_move = move
            elif not maximizing and score < best_score:
                best_score = score
                best_move = move

        return best_move

    def _minimax(
        self,
        state: GameState,
        depth: int,
        alpha: float,
        beta: float,
        maximizing: bool,
    ) -> float:
        """Recursive minimax with alpha-beta pruning.

        Args:
            state: Current position in the game tree.
            depth: Remaining search depth.
            alpha: Best score achievable by the maximizer.
            beta: Best score achievable by the minimizer.
            maximizing: True if the current player is the maximizer.

        Returns:
            Heuristic evaluation of the best reachable position.
        """
        # Terminal conditions.
        winner = Evaluator.winner(state)
        if winner is not None:
            return 100.0 if winner is Color.WHITE else -100.0

        if depth == 0:
            return HeuristicEvaluator.evaluate(state)

        moves = MoveGenerator.generate_legal_moves(state)
        if not moves:
            return 0.0  # Draw.

        # Move ordering for better pruning.
        moves.sort(
            key=lambda m: HeuristicEvaluator.score_move(state, m),
            reverse=maximizing,
        )

        if maximizing:
            max_eval = -math.inf
            for move in moves:
                new_state = state.apply_move(move)
                eval_score = self._minimax(
                    new_state, depth - 1, alpha, beta, False
                )
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff.
            return max_eval
        else:
            min_eval = math.inf
            for move in moves:
                new_state = state.apply_move(move)
                eval_score = self._minimax(
                    new_state, depth - 1, alpha, beta, True
                )
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff.
            return min_eval
