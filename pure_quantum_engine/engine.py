"""
Pure Quantum Engine Execution Subsystem.

Executes board state transformations purely through Qiskit Aer simulation
of the full 150+ gate paper circuit, measuring runtime and gate metrics.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from engine.constants import Color
from engine.position import Position
from engine.state import GameState
from quantum.simulator import QuantumSimulator
from pure_quantum_engine.circuit import PureQuantumCircuitBuilder


@dataclass
class PureQuantumExecutionMetrics:
    """Performance and structural metrics for a Pure Quantum circuit run.

    Attributes:
        num_qubits: Total number of allocated quantum registers.
        circuit_depth: Depth of the compiled quantum gate sequence.
        total_gates: Total number of fundamental logic operations.
        cx_mcx_gates: Count of multi-controlled 2+ qubit entangling gates.
        execution_time_ms: Wall-clock simulation runtime in milliseconds.
    """

    num_qubits: int
    circuit_depth: int
    total_gates: int
    cx_mcx_gates: int
    execution_time_ms: float


class PureQuantumEngine:
    """Executes state transitions using the pure quantum gate architecture."""

    def __init__(self, simulator: QuantumSimulator | None = None) -> None:
        self.simulator = simulator if simulator is not None else QuantumSimulator()

    def execute_move(
        self,
        state: GameState,
        source: Position,
        target: Position,
        color: Color,
    ) -> tuple[dict[str, int], PureQuantumExecutionMetrics]:
        """Execute a move through the complete Pure Quantum Circuit.

        Args:
            state: Current game state.
            source: Source square position.
            target: Target square position.
            color: Side making the move.

        Returns:
            Tuple of (measurement counts dict, PureQuantumExecutionMetrics).
        """
        start_time = time.perf_counter()

        # Build full paper circuit
        circuit, regs = PureQuantumCircuitBuilder.build_full_chess_circuit(
            state, source, target, color
        )

        # Run simulation
        counts = self.simulator.run(circuit)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        # Extract gate metrics
        ops = circuit.count_ops()
        total_gates = sum(ops.values())
        cx_mcx_count = ops.get("cx", 0) + ops.get("mcx", 0) + ops.get("ccx", 0)

        metrics = PureQuantumExecutionMetrics(
            num_qubits=circuit.num_qubits,
            circuit_depth=circuit.depth(),
            total_gates=total_gates,
            cx_mcx_gates=cx_mcx_count,
            execution_time_ms=elapsed_ms,
        )

        return counts, metrics
