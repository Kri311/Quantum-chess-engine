"""
quantum — Quantum computation package for the Quantum Chess Engine.

Implements board-state encoding into quantum registers, reversible
oracles for move-legality checking, Grover's search algorithm, and
measurement post-processing.  All circuits use real Qiskit gates —
nothing is faked.
"""

from quantum.registers import ChessQuantumRegisters
from quantum.encoder import BoardEncoder
from quantum.decoder import BoardDecoder
from quantum.circuit_builder import CircuitBuilder
from quantum.simulator import QuantumSimulator
from quantum.oracle import MoveOracle
from quantum.diffuser import GroverDiffuser
from quantum.grover import GroverSearch
from quantum.measurement import MeasurementProcessor

__all__: list[str] = [
    "ChessQuantumRegisters",
    "BoardEncoder",
    "BoardDecoder",
    "CircuitBuilder",
    "QuantumSimulator",
    "MoveOracle",
    "GroverDiffuser",
    "GroverSearch",
    "MeasurementProcessor",
]
