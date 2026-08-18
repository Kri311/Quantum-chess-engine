"""
Grover diffusion operator.

The diffuser (also called the "inversion about the mean") is the second
component of each Grover iteration.  After the oracle marks target
states with a phase flip, the diffuser amplifies their amplitude.

The standard diffuser for n qubits is:
    H^n  ·  X^n  ·  MCZ  ·  X^n  ·  H^n

where MCZ is a multi-controlled Z gate (Z on the last qubit, controlled
by all others).
"""

from __future__ import annotations

from qiskit import QuantumCircuit, QuantumRegister


class GroverDiffuser:
    """Builds the Grover diffusion operator."""

    @staticmethod
    def build_diffuser(
        circuit: QuantumCircuit,
        qubits: QuantumRegister,
    ) -> None:
        """Append the Grover diffusion operator to the circuit.

        Implements inversion about the mean (2|s><s| - I) where
        |s> = H^n|0^n> is the uniform superposition.

        Args:
            circuit: Circuit to append the diffuser to.
            qubits: The register over which to apply diffusion.
        """
        n = qubits.size

        # Step 1: Apply Hadamard to all qubits.
        for i in range(n):
            circuit.h(qubits[i])

        # Step 2: Apply X to all qubits.
        for i in range(n):
            circuit.x(qubits[i])

        # Step 3: Multi-controlled Z gate.
        # MCZ = H on last qubit, MCX, H on last qubit (or just Z for n=1).
        if n == 1:
            circuit.z(qubits[0])
        else:
            circuit.h(qubits[n - 1])
            circuit.mcx(list(qubits[: n - 1]), qubits[n - 1])
            circuit.h(qubits[n - 1])

        # Step 4: Apply X to all qubits.
        for i in range(n):
            circuit.x(qubits[i])

        # Step 5: Apply Hadamard to all qubits.
        for i in range(n):
            circuit.h(qubits[i])

    @staticmethod
    def build_diffuser_circuit(n_qubits: int) -> QuantumCircuit:
        """Create a standalone diffuser circuit.

        Useful for testing or composing circuits.

        Args:
            n_qubits: Number of qubits for the diffuser.

        Returns:
            A QuantumCircuit implementing the diffusion operator.
        """
        qr = QuantumRegister(n_qubits, "diff")
        circuit = QuantumCircuit(qr)
        GroverDiffuser.build_diffuser(circuit, qr)
        return circuit
