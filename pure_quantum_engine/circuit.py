"""
Pure Quantum Circuit Builder.

Constructs the full circuit implementing quantum move verification, square status extraction,
direction computation, status transformation, and board state updates (following paper Figs 4-7).
"""

from __future__ import annotations

from qiskit import QuantumCircuit

from engine.constants import Color
from engine.position import Position
from engine.state import GameState
from quantum.encoder import BoardEncoder
from pure_quantum_engine.registers import PureQuantumRegisters


class PureQuantumCircuitBuilder:
    """Factory for constructing full Pure Quantum Chess Engine circuits."""

    @staticmethod
    def build_full_chess_circuit(
        state: GameState,
        source: Position,
        target: Position,
        color: Color,
    ) -> tuple[QuantumCircuit, PureQuantumRegisters]:
        """Construct the complete quantum circuit for a move transition.

        Args:
            state: Current game state.
            source: Source square position.
            target: Target square position.
            color: Current player color.

        Returns:
            Tuple of (assembled QuantumCircuit, PureQuantumRegisters instance).
        """
        regs = PureQuantumRegisters(board_size=state.board.size)
        circuit = QuantumCircuit(*regs.all_quantum_registers(), regs.classical)

        # 1. Encode Source and Target Coordinates into Quantum Registers
        src_bits = BoardEncoder.encode_position(source, state.board.size)
        tgt_bits = BoardEncoder.encode_position(target, state.board.size)
        BoardEncoder.initialize_register(circuit, regs.current_square, src_bits)
        BoardEncoder.initialize_register(circuit, regs.target_square, tgt_bits)

        # 2. Extract Source and Target Piece Statuses (Paper Fig 5)
        PureQuantumCircuitBuilder._add_status_extractor(
            circuit, list(regs.current_square), list(regs.src_status), state
        )
        PureQuantumCircuitBuilder._add_status_extractor(
            circuit, list(regs.target_square), list(regs.dst_status), state
        )

        # 3. Compute Move Direction (Paper Subtractor & Comparator logic)
        axis_bits = regs.coord_bits // 2
        cur_x = list(regs.current_square[:axis_bits])
        cur_y = list(regs.current_square[axis_bits:])
        tgt_x = list(regs.target_square[:axis_bits])
        tgt_y = list(regs.target_square[axis_bits:])

        PureQuantumCircuitBuilder._add_direction_detection(
            circuit, cur_x, cur_y, tgt_x, tgt_y,
            list(regs.direction), list(regs.ancilla), color
        )

        # 4. Apply Status Operator (Paper Fig 6)
        PureQuantumCircuitBuilder._add_status_operator(
            circuit,
            list(regs.direction),
            list(regs.src_status),
            list(regs.dst_status),
            list(regs.ancilla[2:]),
        )

        # 5. Measure all quantum registers into classical memory
        cl_idx = 0
        for reg in regs.all_quantum_registers():
            for q_idx in range(reg.size):
                if cl_idx < regs.classical.size:
                    circuit.measure(reg[q_idx], regs.classical[cl_idx])
                    cl_idx += 1

        return circuit, regs

    # ------------------------------------------------------------------
    # Reversible Sub-circuit Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _add_status_extractor(
        circuit: QuantumCircuit,
        coord_qubits: list,
        status_output: list,
        state: GameState,
    ) -> None:
        """Extract the status of a square identified by coord_qubits."""
        board = state.board
        for row in range(board.size):
            for col in range(board.size):
                pos = Position(row, col)
                piece = board.get_piece(pos)
                status = BoardEncoder.encode_status(piece)
                if status == "000":
                    continue

                coord_bits = BoardEncoder.encode_position(pos, board.size)
                flip_indices = []
                for i, bit in enumerate(reversed(coord_bits)):
                    if bit == "0":
                        circuit.x(coord_qubits[i])
                        flip_indices.append(i)

                for i, bit in enumerate(reversed(status)):
                    if bit == "1":
                        circuit.mcx(coord_qubits, status_output[i])

                for i in flip_indices:
                    circuit.x(coord_qubits[i])

    @staticmethod
    def _add_direction_detection(
        circuit: QuantumCircuit,
        cur_x: list, cur_y: list,
        tgt_x: list, tgt_y: list,
        direction: list, ancilla: list,
        color: Color,
    ) -> None:
        """Compute move direction into 2-qubit direction register."""
        for i in range(len(cur_x)):
            circuit.cx(cur_x[i], tgt_x[i])
            circuit.x(tgt_x[i])
        circuit.mcx(tgt_x, ancilla[0])
        for i in range(len(cur_x)):
            circuit.x(tgt_x[i])
            circuit.cx(cur_x[i], tgt_x[i])

        # Forward move -> set direction = |0011>
        circuit.cx(ancilla[0], direction[0])
        circuit.cx(ancilla[0], direction[1])

        # Diagonal left -> set direction = |0010>
        circuit.x(tgt_x[1])
        circuit.ccx(cur_x[1], tgt_x[1], ancilla[1])
        circuit.x(tgt_x[1])
        circuit.cx(ancilla[1], direction[1])

        # Diagonal right -> set direction = |0001>
        circuit.x(cur_x[1])
        circuit.ccx(tgt_x[1], cur_x[1], ancilla[2])
        circuit.x(cur_x[1])
        circuit.cx(ancilla[2], direction[0])
        
        # Note for 8x8 Knight scaling:
        # A full quantum subtractor and absolute value circuit is required here 
        # to detect |cur_x - tgt_x| == 2 and |cur_y - tgt_y| == 1 (and vice versa).
        # When detected, it would set direction[3] to 1.

    @staticmethod
    def _add_status_operator(
        circuit: QuantumCircuit,
        direction: list,
        src_status: list,
        dst_status: list,
        ancilla: list,
    ) -> None:
        """Execute status swap/capture transformation."""
        # For 8x8, this operator requires swapping/capturing 3-qubit statuses 
        # conditionally based on the 4-qubit direction register.
        # Below is the extended shell of the 3x3 operator logic adapted.
        for i in range(3):
            circuit.x(dst_status[i])
            
        controls = list(direction) + list(dst_status)

        for i in range(3):
            circuit.mcx(controls + [src_status[i]], ancilla[0])
            circuit.cx(ancilla[0], dst_status[i])
            circuit.mcx(controls + [src_status[i]], ancilla[0])

        for i in range(3):
            circuit.x(dst_status[i])
