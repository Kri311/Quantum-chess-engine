"""
Quantum register allocation.

``ChessQuantumRegisters`` bundles all the quantum and classical registers
required by the chess circuits into one dataclass.  Register sizes are
derived from the board size so that the same code works for both the
3×3 prototype and a future 8×8 board.

Register layout (3×3 board, following the base paper):

    current_square : 4 qubits  — coordinate of the source square
    target_square  : 4 qubits  — coordinate of the destination square
    direction      : 2 qubits  — computed move direction (d1, d0)
    source_status  : 2 qubits  — piece status of the source square
    target_status  : 2 qubits  — piece status of the target square
    ancilla        : 4 qubits  — scratch workspace for reversible logic
    flag           : 1 qubit   — oracle output (1 = legal move)
    classical      : 15 bits   — measurement readout
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from qiskit import QuantumRegister, ClassicalRegister

import config


@dataclass
class ChessQuantumRegisters:
    """Container for every quantum and classical register used by the
    chess quantum circuits.

    Attributes:
        board_size: Side length of the chess board.
        coord_bits: Number of qubits per coordinate axis.
        current_square: Source-square coordinate register.
        target_square: Target-square coordinate register.
        direction: Computed direction register.
        source_status: Status of the source square.
        target_status: Status of the target square.
        ancilla: Scratch qubits for reversible arithmetic.
        flag: Single-qubit oracle output.
        classical: Classical measurement register.
    """

    board_size: int = field(default_factory=lambda: config.BOARD_SIZE)
    coord_bits: int = field(init=False)
    current_square: QuantumRegister = field(init=False)
    target_square: QuantumRegister = field(init=False)
    direction: QuantumRegister = field(init=False)
    source_status: QuantumRegister = field(init=False)
    target_status: QuantumRegister = field(init=False)
    ancilla: QuantumRegister = field(init=False)
    flag: QuantumRegister = field(init=False)
    classical: ClassicalRegister = field(init=False)

    def __post_init__(self) -> None:
        """Compute register sizes and create Qiskit register objects."""
        # Each axis needs ceil(log2(board_size)) qubits; a coordinate
        # is (x_bits + y_bits).  For the 3×3 board this gives 2+2 = 4.
        self.coord_bits = math.ceil(math.log2(self.board_size)) * 2
        if self.coord_bits < 4:
            self.coord_bits = 4  # minimum for 3×3 per the paper

        self.current_square = QuantumRegister(self.coord_bits, "cur")
        self.target_square = QuantumRegister(self.coord_bits, "tgt")
        self.direction = QuantumRegister(2, "dir")
        self.source_status = QuantumRegister(2, "src")
        self.target_status = QuantumRegister(2, "dst")
        self.ancilla = QuantumRegister(4, "anc")
        self.flag = QuantumRegister(1, "flag")

        total_qubits = (
            self.coord_bits * 2  # current + target
            + 2  # direction
            + 2  # source status
            + 2  # target status
            + 1  # flag
        )
        self.classical = ClassicalRegister(total_qubits, "meas")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def all_quantum_registers(self) -> list[QuantumRegister]:
        """Return a list of every ``QuantumRegister`` in allocation order.

        Returns:
            Ordered list suitable for ``QuantumCircuit`` construction.
        """
        return [
            self.current_square,
            self.target_square,
            self.direction,
            self.source_status,
            self.target_status,
            self.ancilla,
            self.flag,
        ]

    @property
    def total_qubits(self) -> int:
        """Return the total number of qubits across all registers.

        Returns:
            Non-negative integer.
        """
        return sum(reg.size for reg in self.all_quantum_registers())

    def __repr__(self) -> str:
        return (
            f"ChessQuantumRegisters(board_size={self.board_size}, "
            f"total_qubits={self.total_qubits})"
        )
