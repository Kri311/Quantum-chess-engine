"""
pure_quantum_engine package.

Implements a Pure Quantum Chess Engine based directly on the paper:
'Design of Quantum Circuits to Play Chess in a Quantum Computer'.

All state checks, direction calculations, piece status extraction,
and square transformations are performed using pure quantum gates without
intermediate CPU filtering.
"""

from pure_quantum_engine.registers import PureQuantumRegisters
from pure_quantum_engine.circuit import PureQuantumCircuitBuilder
from pure_quantum_engine.engine import PureQuantumEngine

__all__: list[str] = [
    "PureQuantumRegisters",
    "PureQuantumCircuitBuilder",
    "PureQuantumEngine",
]
