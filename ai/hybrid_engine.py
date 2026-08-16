"""
Hybrid classical-quantum engine.

Combines the classical minimax engine with the quantum Grover search
into a single decision pipeline:

1. Classical MoveGenerator produces all legal moves.
2. Classical HeuristicEvaluator scores and ranks them.
3. Quantum GroverSearch amplifies the best candidate(s).
4. Classical engine validates and returns the selected move.
"""

from __future__ import annotations

from ai.heuristic import HeuristicEvaluator
from ai.minimax import MinimaxEngine
from ai.quantum_search import QuantumMoveSearcher
from engine.constants import Color
from engine.evaluator import Evaluator
from engine.game import Game
from engine.move import Move
from engine.move_generator import MoveGenerator
from engine.state import GameState


class HybridEngine:
    """Hybrid classical-quantum move selection engine.

    Attributes:
        use_quantum: Whether to use quantum search.
        minimax: Classical minimax engine.
        quantum_searcher: Quantum Grover-based searcher.
    """

    def __init__(self, use_quantum: bool = True) -> None:
        """Initialise the hybrid engine.

        Args:
            use_quantum: If True, use quantum-assisted search.
                If False, fall back to pure minimax.
        """
        self.use_quantum: bool = use_quantum
        self.minimax = MinimaxEngine(max_depth=3)
        self.quantum_searcher = QuantumMoveSearcher()

    def select_move(self, state: GameState) -> Move | None:
        """Select the best move using the hybrid pipeline.

        Pipeline:
        1. Generate all legal moves classically.
        2. Score and rank using the heuristic evaluator.
        3. If quantum is enabled, run Grover search on candidates.
        4. Otherwise, use minimax.
        5. Validate the selected move.

        Args:
            state: Current game state.

        Returns:
            The selected Move, or None if no legal moves exist.
        """
        legal_moves = MoveGenerator.generate_legal_moves(state)
        if not legal_moves:
            return None

        if len(legal_moves) == 1:
            return legal_moves[0]

        if self.use_quantum:
            # Quantum-assisted selection.
            quantum_move = self.quantum_searcher.search(state)
            if quantum_move is not None:
                return quantum_move

        # Classical fallback.
        return self.minimax.search(state)

    def play_game(self, game: Game) -> None:
        """Play a complete game using the hybrid engine for both sides.

        Prints the board state and selected moves to the console.

        Args:
            game: The Game instance to play.
        """
        print("=" * 50)
        print("  QUANTUM CHESS ENGINE — Hybrid Mode")
        print("=" * 50)

        mode = "Quantum-Assisted" if self.use_quantum else "Classical"
        print(f"  Engine: {mode}")
        print()

        move_count = 0
        while not game.is_over():
            print(game.state)
            print()

            move = self.select_move(game.state)
            if move is None:
                print("  No legal moves available.")
                break

            player = game.state.current_turn
            print(f"  {player} plays: {move}")
            game.make_move(move)
            move_count += 1
            print()

        # Final state.
        print(game.state)
        print()

        winner = game.winner()
        if winner is not None:
            print(f"  >>> {winner} WINS in {move_count} moves! <<<")
        elif Evaluator.is_draw(game.state):
            print(f"  >>> DRAW after {move_count} moves <<<")

        print("\nGame complete.")
