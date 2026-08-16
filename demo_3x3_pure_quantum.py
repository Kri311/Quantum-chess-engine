"""
Pure Quantum 3x3 Chess Demonstration.

This script demonstrates the exact architecture described in the foundational
paper: 'Design of Quantum Circuits to Play Chess in a Quantum Computer'.

It sets up a 3x3 grid with two pawns, builds the full 19-qubit pure quantum
circuit, simulates a legal move using Qiskit Aer GPU, and saves the circuit
diagram.
"""

import config
# Override configuration for the 3x3 demo
config.BOARD_SIZE = 3

import time
from qiskit import transpile
from qiskit_aer import AerSimulator

from engine.board import Board
from engine.constants import Color, PieceType
from engine.piece import Piece
from engine.position import Position
from engine.state import GameState
from pure_quantum_engine.circuit import PureQuantumCircuitBuilder


def main() -> None:
    print("=" * 60)
    print("  PURE QUANTUM 3x3 CHESS DEMONSTRATION")
    print("=" * 60)

    # 1. Setup the 3x3 Board
    board = Board(size=3)
    white_pawn = Piece(color=Color.WHITE, piece_type=PieceType.PAWN)
    black_pawn = Piece(color=Color.BLACK, piece_type=PieceType.PAWN)
    
    # Place pieces according to the paper's prototype
    board.place_piece(Position(2, 1), white_pawn)
    board.place_piece(Position(0, 1), black_pawn)
    
    state = GameState(board=board, current_turn=Color.WHITE)
    
    print("\n  Initial 3x3 Board State:")
    print("  " + str(board).replace("\n", "\n  "))
    
    # 2. Define the move: White pawn moving forward (2,1) -> (1,1)
    source = Position(2, 1)
    target = Position(1, 1)
    print(f"\n  Demonstrating Pure Quantum Circuit for Move: {source} → {target}")
    
    # 3. Build the 19-Qubit Circuit
    print("  Constructing 19-Qubit Reversible Circuit...")
    circuit, regs = PureQuantumCircuitBuilder.build_full_chess_circuit(
        state=state,
        source=source,
        target=target,
        color=Color.WHITE
    )
    
    print(f"  ✓ Circuit built successfully. Total Qubits: {circuit.num_qubits}")
    
    # 4. Save diagrams
    try:
        fig = circuit.draw(output="mpl", style="iqp", fold=30, scale=0.7)
        fig.savefig("pure_quantum_3x3_circuit.png", dpi=200, bbox_inches="tight")
        print("  ✓ Saved visual diagram to pure_quantum_3x3_circuit.png")
    except Exception as e:
        print(f"  ✗ Could not save visual diagram: {e}")
        
    with open("pure_quantum_3x3_circuit.txt", "w") as f:
        f.write(str(circuit.draw(fold=-1)))
    print("  ✓ Saved ASCII diagram to pure_quantum_3x3_circuit.txt")
    
    # 5. Simulate on GPU
    print("\n  Executing 19-Qubit Simulation on RTX 4050 GPU...")
    try:
        sim = AerSimulator(method="statevector", device="GPU")
        transpiled = transpile(circuit, optimization_level=1)
        
        t0 = time.time()
        result = sim.run(transpiled, shots=1024).result()
        t1 = time.time()
        
        counts = result.get_counts()
        print(f"  ✓ Execution completed in {(t1-t0)*1000:.1f}ms")
        print(f"  ✓ Simulation Status: {result.status}")
        
        # Display the highest probability measurement
        best_outcome = max(counts, key=counts.get)
        print(f"  ✓ Most probable quantum measurement: |{best_outcome}⟩")
        print("  (This bitstring encodes the new board state after the move)")
        
    except Exception as e:
        print(f"  ✗ GPU Simulation Failed: {e}")


if __name__ == "__main__":
    main()
