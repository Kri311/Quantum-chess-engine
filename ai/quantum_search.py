"""
Quantum move searcher.

Wraps Grover's search with classical pre- and post-processing.
Falls back to a classical random legal move if the quantum search
fails to produce a valid result.
"""

from __future__ import annotations

import random

from engine.move import Move
from engine.move_generator import MoveGenerator
from engine.state import GameState
from quantum.grover import GroverSearch
from quantum.simulator import QuantumSimulator


class QuantumMoveSearcher:
    """Selects a move using Grover's quantum search algorithm.

    Attributes:
        grover: The underlying Grover search instance.
    """

    def __init__(self, simulator: QuantumSimulator | None = None) -> None:
        """Initialise the quantum searcher.

        Args:
            simulator: Quantum simulator. Creates a default if None.
        """
        self.grover = GroverSearch(simulator)

    def search(self, state: GameState) -> Move | None:
        """Run quantum search to select a legal move.

        The pipeline:
        1. Generate all candidate moves (legal + illegal).
        2. Run Grover's algorithm to amplify legal moves.
        3. Measure and decode the result.
        4. Fall back to classical selection if quantum fails.

        Args:
            state: Current game state.

        Returns:
            A legal Move, or None if no moves exist.
        """
        legal_moves = MoveGenerator.generate_legal_moves(state)
        if not legal_moves:
            return None

        # Classical pre-processing: Score all legal moves using heuristics
        from ai.heuristic import HeuristicEvaluator
        
        best_score = -float('inf')
        optimal_indices = []
        
        for idx, move in enumerate(legal_moves):
            score = HeuristicEvaluator.score_move(state, move)
            if score > best_score:
                best_score = score
                optimal_indices = [idx]
            elif score == best_score:
                optimal_indices.append(idx)

        # Attempt quantum search to amplify only the optimal moves.
        result = self.grover.search(state, candidates=legal_moves, optimal_indices=optimal_indices)
        
        if result is not None:
            return result

        # Fallback: return a random optimal move.
        return legal_moves[optimal_indices[0]]
