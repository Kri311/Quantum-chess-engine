"""
Circuit Inspection Script for Pure Quantum Engine.

Builds and displays a board-size-dependent pure circuit, then saves its
ASCII representation and image under the documentation artifact folders.
"""

from pathlib import Path
import sys

# Make package imports work when this utility is launched from any directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from engine.board import Board
from engine.constants import Color, PieceType
from engine.piece import Piece
from engine.position import Position
from engine.state import GameState
from pure_quantum_engine.circuit import PureQuantumCircuitBuilder

def main() -> None:
    # 1. Create a basic game state
    board = Board(size=8)
    source = Position(4, 4)
    target = Position(6, 5) # Knight L-shape
    board.place_piece(source, Piece(Color.WHITE, PieceType.KNIGHT))
    state = GameState(board=board, current_turn=Color.WHITE)

    # 2. Build the pure quantum circuit for a move
    print("Building pure quantum circuit for the 8x8 knight example...")
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
    circuit_dir = PROJECT_ROOT / "docs" / "circuits"
    diagram_dir = PROJECT_ROOT / "docs" / "assets" / "diagrams"
    circuit_dir.mkdir(parents=True, exist_ok=True)
    diagram_dir.mkdir(parents=True, exist_ok=True)

    text_path = circuit_dir / "pure_circuit.txt"
    with text_path.open("w") as f:
        f.write(str(circuit.draw(fold=-1)))
    print(f"Saved full ASCII circuit diagram to '{text_path}'.")
    
    # 5. Optionally try to save as an image if matplotlib is installed
    try:
        image_path = diagram_dir / "with_knight.png"
        circuit.draw(output="mpl", filename=str(image_path), style="iqp", fold=-1)
        print(f"Saved graphical circuit diagram to '{image_path}'.")
    except Exception as e:
        print(f"Could not save graphical diagram (matplotlib may not be installed): {e}")

if __name__ == "__main__":
    main()
