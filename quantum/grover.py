"""
Grover's search algorithm for move selection.

Implements the full Grover search pipeline:
1. Encode candidate moves into a superposition over n qubits.
2. Calculate the optimal number of Grover iterations.
3. Apply oracle + diffuser for each iteration.
4. Measure to obtain the selected move index.
5. Decode the result back to a Move.

The number of iterations is floor((pi/4) * sqrt(N/M)) where
N = total candidates and M = number of legal moves (solutions).
"""

from __future__ import annotations

import math

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

from engine.move import Move
from engine.state import GameState
from quantum.oracle import MoveOracle
from quantum.diffuser import GroverDiffuser
from quantum.measurement import MeasurementProcessor
from quantum.simulator import QuantumSimulator


class GroverSearch:
    """Grover's algorithm applied to chess move selection.

    Attributes:
        simulator: The quantum simulator instance.
    """

    def __init__(self, simulator: QuantumSimulator | None = None) -> None:
        """Initialise the Grover search engine.

        Args:
            simulator: Quantum simulator. Creates a default one if None.
        """
        self.simulator = simulator if simulator is not None else QuantumSimulator()

    def search(
        self,
        state: GameState,
        candidates: list[Move] | None = None,
        optimal_indices: list[int] | None = None,
    ) -> Move | None:
        """Run Grover's algorithm to select an optimal move.

        Args:
            state: Current game state.
            candidates: Optional list of candidate moves. If None,
                all possible moves are generated.
            optimal_indices: Optional list of indices corresponding to
                heuristically optimal moves to amplify. If None,
                amplifies all legal moves.

        Returns:
            The selected Move, or None if no moves exist.
        """
        if candidates is None:
            candidates = MoveOracle.generate_all_candidates(state)

        if not candidates:
            return None

        # Determine which candidates to amplify.
        if optimal_indices is not None:
            target_indices = optimal_indices
        else:
            target_indices = MoveOracle.compute_legal_indices(state, candidates)

        if not target_indices:
            return None

        n_candidates = len(candidates)
        n_qubits = math.ceil(math.log2(n_candidates)) if n_candidates > 1 else 1
        search_space = 2 ** n_qubits

        # If all candidates are targets, just return the first one.
        if len(target_indices) == n_candidates:
            return candidates[target_indices[0]]

        # Calculate optimal number of Grover iterations.
        n_iterations = self.calculate_iterations(search_space, len(target_indices))

        # Build the Grover circuit.
        circuit = self._build_grover_circuit(
            n_qubits, target_indices, n_iterations
        )

        # Execute and measure.
        counts = self.simulator.run(circuit)

        # Decode the most likely result.
        processor = MeasurementProcessor()
        best_bitstring = processor.get_most_likely(counts)

        # Convert bitstring to move index.
        move_index = int(best_bitstring[::-1], 2)  # Qiskit little-endian.

        if move_index < len(candidates) and move_index in target_indices:
            return candidates[move_index]

        # Fallback: if Grover didn't amplify a target move (can happen
        # with low iteration counts), return the first target move.
        return candidates[target_indices[0]]

    @staticmethod
    def calculate_iterations(n_total: int, n_solutions: int) -> int:
        """Calculate the optimal number of Grover iterations.

        Uses the formula: floor((pi/4) * sqrt(N/M)) where N is the
        total search space size and M is the number of solutions.

        Args:
            n_total: Total number of items in the search space (2^n).
            n_solutions: Number of marked (solution) items.

        Returns:
            Optimal number of iterations (at least 1).
        """
        if n_solutions <= 0 or n_solutions >= n_total:
            return 1
        return max(1, int(math.floor((math.pi / 4) * math.sqrt(n_total / n_solutions))))

    def _build_grover_circuit(
        self,
        n_qubits: int,
        legal_indices: list[int],
        n_iterations: int,
    ) -> QuantumCircuit:
        """Construct the complete Grover search circuit.

        Args:
            n_qubits: Number of qubits for the move-index register.
            legal_indices: Indices to mark as solutions.
            n_iterations: Number of Grover iterations.

        Returns:
            The assembled QuantumCircuit.
        """
        move_reg = QuantumRegister(n_qubits, "move")
        flag_reg = QuantumRegister(1, "flag")
        classical = ClassicalRegister(n_qubits, "result")
        circuit = QuantumCircuit(move_reg, flag_reg, classical)

        # Step 1: Create uniform superposition.
        for i in range(n_qubits):
            circuit.h(move_reg[i])

        # Prepare flag qubit in |-> state for phase kickback.
        circuit.x(flag_reg[0])
        circuit.h(flag_reg[0])

        # Step 2: Grover iterations.
        for _ in range(n_iterations):
            # Oracle: marks legal moves with phase flip.
            MoveOracle.build_phase_oracle(
                circuit, move_reg, flag_reg, legal_indices, n_qubits,
            )
            # Diffuser: amplifies marked states.
            GroverDiffuser.build_diffuser(circuit, move_reg)

        # Step 3: Measure the move register.
        circuit.measure(move_reg, classical)

        return circuit
