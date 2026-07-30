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

        # Attempt quantum search.
        result = self.grover.search(state)
        if result is not None:
            return result

        # Fallback: return a random legal move.
        return random.choice(legal_moves)
