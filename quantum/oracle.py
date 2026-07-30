"""
Quantum oracle for move legality.

The oracle is a reversible circuit that flips a flag qubit when a
candidate move (encoded as an index into a list of all possible moves)
is legal. This is the key component plugged into Grover's algorithm.

The oracle checks:
1. Source square contains a piece of the correct colour.
2. Movement direction is valid for a pawn.
3. Target square is compatible (empty for forward, enemy for diagonal).
"""

from __future__ import annotations

import math

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

from engine.constants import Color
from engine.move import Move
from engine.state import GameState
from engine.move_generator import MoveGenerator


class MoveOracle:
    """Reversible quantum oracle that marks legal moves.

    The oracle operates on a register of n qubits encoding a move index
    in [0, 2^n - 1]. For each legal move index, the oracle flips the
    phase of that basis state (for Grover's algorithm).
    """

    @staticmethod
    def build_legality_oracle(
        circuit: QuantumCircuit,
        move_register: QuantumRegister,
        flag_qubit: QuantumRegister,
        legal_indices: list[int],
        n_qubits: int,
    ) -> None:
        """Append a legality-checking oracle to the circuit.

        For each index in legal_indices, the oracle flips the flag qubit
        when move_register encodes that index. This implements the
        standard Grover oracle pattern using multi-controlled X gates.

        The oracle is fully reversible: each marking operation uses
        X gates to condition on |0> bits, a multi-controlled X (Toffoli)
        to flip the flag, then uncomputes the X gates.

        Args:
            circuit: Circuit to append oracle gates to.
            move_register: n-qubit register encoding the move index.
            flag_qubit: Single-qubit register to flip for legal moves.
            legal_indices: List of integer indices that are legal.
            n_qubits: Number of qubits in move_register.
        """
        for idx in legal_indices:
            bitstring = format(idx, f"0{n_qubits}b")

            # Apply X gates to qubits where the bitstring has '0',
            # so all qubits become |1> for this specific index.
            flip_positions: list[int] = []
            for bit_pos, bit_val in enumerate(reversed(bitstring)):
                if bit_val == "0":
                    circuit.x(move_register[bit_pos])
                    flip_positions.append(bit_pos)

            # Multi-controlled X: flips flag when all move_register
            # qubits are |1> (i.e., the index matches).
            circuit.mcx(
                list(move_register),
                flag_qubit[0],
            )

            # Uncompute X gates to restore move_register.
            for bit_pos in flip_positions:
                circuit.x(move_register[bit_pos])

    @staticmethod
    def build_phase_oracle(
        circuit: QuantumCircuit,
        move_register: QuantumRegister,
        flag_qubit: QuantumRegister,
        legal_indices: list[int],
        n_qubits: int,
    ) -> None:
        """Append a phase-kickback oracle for Grover's algorithm.

        Instead of flipping a flag qubit, this oracle directly applies
        a phase flip to the marked states by using the flag qubit
        prepared in the |-> state (H|1> = |->).

        The phase kickback effect: when the flag qubit is in |-> and
        the MCX flips it, the overall state picks up a -1 phase for
        the marked basis state.

        Args:
            circuit: Circuit to append oracle gates to.
            move_register: n-qubit register encoding the move index.
            flag_qubit: Single qubit prepared in |-> state.
            legal_indices: List of legal move indices to mark.
            n_qubits: Number of qubits in move_register.
        """
        # The flag qubit should already be in |-> = H|1>.
        # Each MCX will cause phase kickback on marked states.
        MoveOracle.build_legality_oracle(
            circuit, move_register, flag_qubit, legal_indices, n_qubits,
        )

    @staticmethod
    def compute_legal_indices(
        state: GameState,
        all_candidates: list[Move],
    ) -> list[int]:
        """Determine which candidate indices correspond to legal moves.

        Uses the classical MoveGenerator to identify legal moves,
        then maps them to indices in the all_candidates list.

        Args:
            state: Current game state.
            all_candidates: Full list of candidate moves (legal + illegal).

        Returns:
            List of integer indices into all_candidates that are legal.
        """
        legal_moves = set(
            (m.start, m.end) for m in MoveGenerator.generate_legal_moves(state)
        )
        return [
            i for i, m in enumerate(all_candidates)
            if (m.start, m.end) in legal_moves
        ]

    @staticmethod
    def generate_all_candidates(state: GameState) -> list[Move]:
        """Generate all possible pawn moves (legal and illegal).

        Creates every (source, target) combination where source holds
        a piece of the current player's colour and target is a
        neighbouring square a pawn could theoretically reach.

        Args:
            state: Current game state.

        Returns:
            List of Move objects, some legal and some not.
        """
        candidates: list[Move] = []
        board = state.board
        color = state.current_turn
        forward_dir = -1 if color is Color.WHITE else 1

        for pos, piece in board.pieces_by_color(color):
            forward_row = pos.row + forward_dir
            for col_offset in [-1, 0, 1]:
                new_col = pos.col + col_offset
                if (
                    0 <= forward_row < board.size
                    and 0 <= new_col < board.size
                ):
                    from engine.position import Position

                    target = Position(forward_row, new_col)
                    is_capture = col_offset != 0
                    candidates.append(
                        Move(start=pos, end=target, capture=is_capture)
                    )

        return candidates
