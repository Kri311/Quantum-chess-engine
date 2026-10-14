"""
ai — Artificial intelligence and hybrid engine package.

Provides classical (minimax with alpha-beta pruning), quantum (Grover
search), and hybrid (classical + quantum) move selection strategies.
"""

from ai.heuristic import HeuristicEvaluator
from ai.minimax import MinimaxEngine
from ai.classical_3x3 import Classical3x3Engine
from ai.quantum_search import QuantumMoveSearcher
from ai.hybrid_engine import HybridEngine

__all__: list[str] = [
    "HeuristicEvaluator",
    "MinimaxEngine",
    "Classical3x3Engine",
    "QuantumMoveSearcher",
    "HybridEngine",
]
