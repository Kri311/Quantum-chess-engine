"""
Pure Quantum 3x3 Chess Circuit Generator (Base Paper Architecture).

Generates the exact 19-qubit quantum circuit described in the base paper
"Design of Quantum Circuits to Play Chess in a Quantum Computer".
Simulates a 3x3 grid with two pawns (White at 2,1 and Black at 0,1) and
a pure quantum move execution.
"""

from qiskit import transpile

from engine.board import Board
from engine.constants import Color, PieceType
from engine.piece import Piece
from engine.position import Position
from engine.state import GameState
from pure_quantum_engine.circuit import PureQuantumCircuitBuilder


def main() -> None:
    print("Initializing 3x3 Pure Quantum Chess Board...")
    
    # 1. Setup 3x3 Board with 2 Pawns
    board = Board(size=3)
    white_pawn = Piece(color=Color.WHITE, piece_type=PieceType.PAWN)
    black_pawn = Piece(color=Color.BLACK, piece_type=PieceType.PAWN)
    
    # Paper layout: White pawn bottom-center, Black pawn top-center
    board.place_piece(Position(2, 1), white_pawn)
    board.place_piece(Position(0, 1), black_pawn)
    state = GameState(board=board, current_turn=Color.WHITE)

    # 2. Define a move (White Pawn moves forward)
    source = Position(2, 1)
    target = Position(1, 1)

    print(f"Building Pure Quantum Circuit for move {source} -> {target}...")
    
    # 3. Build the 19-qubit pure circuit
    circuit, regs = PureQuantumCircuitBuilder.build_full_chess_circuit(
        state=state,
        source=source,
        target=target,
        color=Color.WHITE
    )

    print("=" * 60)
    print("  PURE QUANTUM 3x3 ARCHITECTURE (Paper Spec Extended)")
    print("=" * 60)
    print(f"  Total Qubits:      {circuit.num_qubits} (Extended from paper 19 for full piece set)")
    print(f"  Classical Bits:    {circuit.num_clbits}")
    print(f"  Circuit Depth:     {circuit.depth()}")
    print(f"  Gate Breakdown:    {dict(circuit.count_ops())}")
    print("-" * 60)

    print("\n  Register Allocation:")
    print("  ┌──────────────────────┬────────┬─────────────────────────┐")
    print("  │ Register             │ Qubits │ Purpose                 │")
    print("  ├──────────────────────┼────────┼─────────────────────────┤")
    print("  │ cur_sq               │   4    │ Source coordinate       │")
    print("  │ tgt_sq               │   4    │ Target coordinate       │")
    print("  │ src_status           │   3    │ Source piece encoding   │")
    print("  │ dst_status           │   3    │ Target piece encoding   │")
    print("  │ direction            │   4    │ Move direction flags    │")
    print("  │ ancilla              │   5    │ Scratch workspace       │")
    print("  ├──────────────────────┼────────┼─────────────────────────┤")
    print(f"  │ TOTAL                │  {circuit.num_qubits:2d}    │                         │")
    print("  └──────────────────────┴────────┴─────────────────────────┘")

    # 4. Save the circuit
    print("\n  Saving circuit diagrams...")
    
    with open("pure_3x3_circuit.txt", "w") as f:
        f.write(str(circuit.draw(fold=-1)))
    print("  ✓ Saved ASCII diagram -> pure_3x3_circuit.txt")
    
    try:
        fig = circuit.draw(output="mpl", style="iqp", fold=40, scale=0.7)
        fig.savefig("pure_3x3_qiskit_circuit.png", dpi=200, bbox_inches="tight")
        print("  ✓ Saved graphical diagram -> pure_3x3_qiskit_circuit.png")
    except Exception as e:
        print(f"  ✗ Could not save graphical diagram: {e}")

    # 5. Execute on Qiskit Aer Statevector
    print(f"\n  Simulating Pure Quantum Execution ({circuit.num_qubits} Qubits)...")
    try:
        from qiskit_aer import AerSimulator
        import time
        
        sim = AerSimulator(method="statevector")
        transpiled = transpile(circuit, sim, optimization_level=1)
        
        t0 = time.time()
        result = sim.run(transpiled, shots=1024).result()
        t1 = time.time()
        
        print(f"  ✓ Simulation complete in {(t1-t0)*1000:.1f}ms")
        counts = result.get_counts()
        print(f"  ✓ Measured {len(counts)} unique outcomes.")
    except Exception as e:
        print(f"  ✗ Simulation failed: {e}")

if __name__ == "__main__":
    main()
