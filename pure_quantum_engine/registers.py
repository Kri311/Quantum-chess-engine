"""
Pure Quantum register allocation.

Defines the 19-qubit quantum register set following the base paper:
'Design of Quantum Circuits to Play Chess in a Quantum Computer'.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from qiskit import QuantumRegister, ClassicalRegister

import config


@dataclass
class PureQuantumRegisters:
    """Allocates all quantum registers required for full quantum move execution.

    Attributes:
        board_size: Side length of the chess board (default 3).
        current_square: 4-qubit source square register.
        target_square: 4-qubit target square register.
        direction: 4-qubit direction output register (supports pawn & knight moves).
        src_status: 3-qubit source status register.
        dst_status: 3-qubit target status register.
        ancilla: Scratch workspace qubits.
        classical: Classical readout register.
    """

    board_size: int = field(default_factory=lambda: config.BOARD_SIZE)
    coord_bits: int = field(init=False)
    current_square: QuantumRegister = field(init=False)
    target_square: QuantumRegister = field(init=False)
    direction: QuantumRegister = field(init=False)
    src_status: QuantumRegister = field(init=False)
    dst_status: QuantumRegister = field(init=False)
    ancilla: QuantumRegister = field(init=False)
    classical: ClassicalRegister = field(init=False)

    def __post_init__(self) -> None:
        """Create Qiskit register objects matching the paper architecture."""
        axis_bits = math.ceil(math.log2(self.board_size)) if self.board_size > 1 else 1
        self.coord_bits = max(4, axis_bits * 2)

        # 8x8 uses 6-bit sparse status encoding from the paper to reach exactly 33 qubits
        self.status_bits = 6 if self.board_size == 8 else 3

        self.current_square = QuantumRegister(self.coord_bits, "cur")
        self.target_square = QuantumRegister(self.coord_bits, "tgt")
        self.direction = QuantumRegister(4, "dir")
        self.src_status = QuantumRegister(self.status_bits, "src")
        self.dst_status = QuantumRegister(self.status_bits, "dst")
        self.ancilla = QuantumRegister(5, "anc")

        total_qubits = self.total_qubits
        self.classical = ClassicalRegister(total_qubits, "meas")

    def all_quantum_registers(self) -> list[QuantumRegister]:
        """Return all quantum registers in ordered sequence."""
        return [
            self.current_square,
            self.target_square,
            self.direction,
            self.src_status,
            self.dst_status,
            self.ancilla,
        ]

    @property
    def total_qubits(self) -> int:
        """Calculate total qubit allocation count."""
        return (
            self.coord_bits * 2  # cur + tgt
            + 4  # dir (4)
            + self.status_bits * 2  # src + dst status
            + 5  # anc (5)
        )
