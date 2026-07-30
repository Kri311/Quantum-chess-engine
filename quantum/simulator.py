"""
Quantum circuit simulator wrapper.

Provides a clean interface to Qiskit Aer for running quantum circuits
and retrieving measurement results.
"""

from __future__ import annotations

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

import config

# Basis gates natively supported by Qiskit Aer's simulator.
# We pass these explicitly to transpile() so that:
#   1) No coupling-map width limit is enforced (no backend target).
#   2) MCX gates decompose into cx/ccx/x/h — NOT rccx which Aer rejects.
_AER_BASIS_GATES: list[str] = [
    "cx", "ccx", "x", "h", "s", "sdg", "t", "tdg",
    "rz", "ry", "rx", "sx", "sxdg", "u1", "u2", "u3",
    "id", "swap", "cz",
]


class QuantumSimulator:
    """Wrapper around Qiskit Aer for executing quantum circuits.

    Attributes:
        shots: Number of measurement shots per execution.
    """

    def __init__(
        self,
        backend_name: str | None = None,
        shots: int | None = None,
    ) -> None:
        """Initialise the simulator.

        Args:
            backend_name: Aer backend identifier. Defaults to
                config.QUANTUM_BACKEND.
            shots: Number of shots. Defaults to config.QUANTUM_SHOTS.
        """
        name = backend_name if backend_name is not None else config.QUANTUM_BACKEND
        self.shots: int = shots if shots is not None else config.QUANTUM_SHOTS
        self._backend = AerSimulator()

    def run(self, circuit: QuantumCircuit) -> dict[str, int]:
        """Execute a circuit and return measurement counts.

        Args:
            circuit: The quantum circuit to execute.

        Returns:
            Dictionary mapping bitstrings to their measurement counts.
        """
        transpiled = transpile(
            circuit, basis_gates=_AER_BASIS_GATES, optimization_level=1,
        )
        job = self._backend.run(transpiled, shots=self.shots)
        result = job.result()
        return result.get_counts(transpiled)

    def run_statevector(self, circuit: QuantumCircuit) -> dict[str, complex]:
        """Execute a circuit using statevector simulation.

        Removes all measurements from the circuit and returns the
        full statevector as a dictionary of amplitudes.

        Args:
            circuit: The quantum circuit to simulate.

        Returns:
            Dictionary mapping basis states to complex amplitudes.
        """
        try:
            sv_backend = AerSimulator(method="statevector", device="GPU")
        except Exception:
            sv_backend = AerSimulator(method="statevector")

        # Create a copy without measurements for statevector sim.
        sv_circuit = circuit.remove_final_measurements(inplace=False)
        sv_circuit.save_statevector()
        transpiled = transpile(
            sv_circuit, basis_gates=_AER_BASIS_GATES, optimization_level=1,
        )
        job = sv_backend.run(transpiled)
        result = job.result()
        statevector = result.get_statevector(transpiled)
        return {
            format(i, f"0{circuit.num_qubits}b"): amp
            for i, amp in enumerate(statevector)
            if abs(amp) > 1e-10
        }
