"""
Circuit Inspection Script for Pure Quantum Engine.

Builds and displays the ASCII representation and saves an image of the
19-qubit pure quantum circuit generated for move verification and state update.
"""

from engine.board import Board
from engine.constants import Color, PieceType
from engine.piece import Piece
from engine.position import Position
from engine.state import GameState
from pure_quantum_engine.circuit import PureQuantumCircuitBuilder

def main() -> None:
    # 1. Create a basic game state
    board = Board(size=3)
    source = Position(2, 1)
    target = Position(1, 1)
    board.place_piece(source, Piece(Color.WHITE, PieceType.PAWN))
    state = GameState(board=board, current_turn=Color.WHITE)

    # 2. Build the pure quantum circuit for a move
    print("Building 19-qubit pure quantum circuit...")
    circuit, regs = PureQuantumCircuitBuilder.build_full_chess_circuit(
        state, source, target, Color.WHITE
    )

    # 3. Print quantum circuit summary
    print("=" * 60)
    print("  PURE QUANTUM ENGINE — Qiskit Full Circuit Inspection")
    print("=" * 60)
    print(f"Total Qubits:      {circuit.num_qubits}")
    print(f"Classical Bits:    {circuit.num_clbits}")
    print(f"Circuit Depth:     {circuit.depth()}")
    print(f"Gate Breakdown:    {circuit.count_ops()}")
    print("-" * 60)

    # 4. Save the circuit as a text file for easier viewing (since it's very large)
    with open("pure_circuit.txt", "w") as f:
        f.write(str(circuit.draw(fold=-1)))
    print("Saved full ASCII circuit diagram to 'pure_circuit.txt'.")
    
    # 5. Optionally try to save as an image if matplotlib is installed
    try:
        circuit.draw(output="mpl", filename="pure_circuit.png", style="iqp")
        print("Saved graphical circuit diagram to 'pure_circuit.png'.")
    except Exception as e:
        print(f"Could not save graphical diagram (matplotlib may not be installed): {e}")

if __name__ == "__main__":
    main()
