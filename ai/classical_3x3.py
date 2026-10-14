"""Classical 3×3 move selector used as a comparison baseline."""

from __future__ import annotations

import math

from engine.constants import Color
from ai.heuristic import HeuristicEvaluator
from ai.minimax import MinimaxEngine
from engine.move import Move
from engine.move_generator import MoveGenerator
from engine.state import GameState


class Classical3x3Engine:
    """A size-checked classical selector for the 3×3 chess variant.

    The engine uses the existing rules and evaluation code. ``select_move``
    performs depth-limited minimax with alpha-beta pruning; ``select_greedy``
    is a one-ply heuristic baseline useful for comparing against Grover over
    the same per-move heuristic scores.
    """

    def __init__(self, max_depth: int = 3) -> None:
        if max_depth < 1:
            raise ValueError("max_depth must be at least 1")
        self.max_depth = max_depth
        self._minimax = MinimaxEngine(max_depth=max_depth)

    @staticmethod
    def _check_board(state: GameState) -> None:
        if state.board.size != 3:
            raise ValueError(
                f"Classical3x3Engine requires a 3x3 board, got {state.board.size}x{state.board.size}"
            )

    def select_move(self, state: GameState) -> Move | None:
        """Select a move with depth-limited classical minimax."""
        self._check_board(state)
        return self._minimax.search(state)

    def select_greedy(self, state: GameState) -> Move | None:
        """Select the legal move with the highest one-ply move score."""
        self._check_board(state)
        moves = MoveGenerator.generate_legal_moves(state)
        if not moves:
            return None
        return max(moves, key=lambda move: HeuristicEvaluator.score_move(state, move))

    def action_values(self, state: GameState) -> dict[Move, float]:
        """Return each legal move's minimax value from the mover's perspective.

        This evaluates every root action to the configured search depth. It is
        used as an independent tactical reference in the comparison report;
        values are oriented so that larger is always better for the side to
        move, regardless of color.
        """
        self._check_board(state)
        moves = MoveGenerator.generate_legal_moves(state)
        maximizing_white = state.current_turn is Color.WHITE
        values: dict[Move, float] = {}
        for move in moves:
            child = state.apply_move(move)
            white_value = self._minimax._minimax(
                child,
                depth=self.max_depth - 1,
                alpha=-math.inf,
                beta=math.inf,
                maximizing=not maximizing_white,
            )
            values[move] = white_value if maximizing_white else -white_value
        return values
