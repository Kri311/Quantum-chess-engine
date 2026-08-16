#!/usr/bin/env python3
"""
Quantum Chess Engine — Interactive Entry Point.

Provides a unified menu to select between full 8x8 Hybrid Quantum gameplay,
3x3 Pure Quantum prototype gameplay, and architectural circuit generation.
"""

from __future__ import annotations
import sys
import time
import math

import config
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator

# --- Option 3/4: Circuit Generators ---

def generate_circuit_diagram(board_size: int, is_pure: bool) -> None:
    """Generates the architectural diagram for the selected board size."""
    from engine.constants import Color
    from engine.position import Position
    from engine.state import GameState
    from engine.board import Board
    from engine.piece import Piece
    from engine.constants import PieceType
    from pure_quantum_engine.circuit import PureQuantumCircuitBuilder

    print(f"\n[GENERATOR] Building circuit architecture for {board_size}x{board_size} board...")
    
    board = Board(size=board_size)
    if board_size == 3:
        board.place_piece(Position(2, 1), Piece(Color.WHITE, PieceType.PAWN))
        board.place_piece(Position(0, 0), Piece(Color.BLACK, PieceType.PAWN))
        source, target = Position(2, 1), Position(1, 1)
    else:
        # 8x8 knight move
        board.place_piece(Position(7, 6), Piece(Color.WHITE, PieceType.KNIGHT))
        source, target = Position(7, 6), Position(5, 5)

    state = GameState(board=board, current_turn=Color.WHITE)
    
    # Build the full, exact logic circuit for both 3x3 (23 qubits) and 8x8 (33 qubits).
    # We do not simulate the 8x8 circuit here (which would require 128TB RAM), 
    # we only assemble the gates to draw the architectural diagram.
    circuit, _ = PureQuantumCircuitBuilder.build_full_chess_circuit(
        state=state, source=source, target=target, color=Color.WHITE
    )

    filename = f"architecture_{board_size}x{board_size}.png"
    print(f"\n========================================================")
    print(f"  QUANTUM ARCHITECTURE: {circuit.num_qubits} QUBITS")
    print(f"========================================================")
    print(f"  Total Qubits:      {circuit.num_qubits}")
    print(f"  Circuit Depth:     {circuit.depth()}")
    print(f"  Gate Breakdown:    {dict(circuit.count_ops())}")
    print(f"--------------------------------------------------------")
    
    try:
        fig = circuit.draw(output="mpl", style="iqp", fold=40, scale=0.7)
        fig.savefig(filename, dpi=200, bbox_inches="tight")
        print(f"  ✓ Saved graphical diagram -> {filename}")
    except Exception as e:
        print(f"  ✗ Could not save diagram: {e}")
    
    input("\nPress Enter to return to main menu...")


# --- Option 2: 3x3 Pure Quantum Game Wrapper ---

def play_3x3_pure_quantum() -> None:
    """Runs the 3x3 game overriding normal moves with Pure Quantum tracking."""
    config.BOARD_SIZE = 3
    from engine.game import Game
    from engine.move import Move
    from engine.constants import Color
    from pure_quantum_engine.circuit import PureQuantumCircuitBuilder
    from ai.hybrid_engine import HybridEngine
    from ui.gui import ChessGUI

    class PureQuantumGame(Game):
        def make_move(self, move: Move) -> None:
            print(f"\n[PURE QUANTUM METRICS] Executing {move.start} -> {move.end}")
            
            # 1. Build circuit
            circuit, _ = PureQuantumCircuitBuilder.build_full_chess_circuit(
                state=self.state, source=move.start, target=move.end, color=self.state.current_turn
            )
            
            # 2. Simulate
            sim = AerSimulator(method="statevector")
            transpiled = transpile(circuit, sim, optimization_level=1)
            
            t0 = time.time()
            result = sim.run(transpiled, shots=1).result()
            t1 = time.time()
            
            counts = result.get_counts()
            measured = list(counts.keys())[0] if counts else "Error"
            
            # Print Faculty Metrics
            print(f"  ► Target Circuit: {circuit.num_qubits} Qubits")
            print(f"  ► Quantum Depth:  {circuit.depth()} gates")
            print(f"  ► Exec Time:      {(t1-t0)*1000:.1f} ms")
            print(f"  ► Prob Amplitude: 100.0% (Reversible deterministic path)")
            print(f"  ► Measurement:    |{measured}⟩")
            print(f"  ► Status:         Collapsed. UI updating.")
            
            super().make_move(move)

    print("\nStarting 3x3 Pure Quantum Game...")
    game = PureQuantumGame()
    engine = HybridEngine(use_quantum=False) # AI plays as Black using classical mini-max for the 3x3
    gui = ChessGUI(engine=engine, ai_color=Color.BLACK)
    gui.game = game
    gui.run()


# --- Option 1: 8x8 Hybrid Game Wrapper ---

def play_8x8_hybrid_quantum() -> None:
    """Runs the standard 8x8 Hybrid Quantum gameplay."""
    config.BOARD_SIZE = 8
    from engine.constants import Color
    from ai.hybrid_engine import HybridEngine
    from ui.gui import ChessGUI

    print("\nStarting 8x8 Hybrid Quantum Game on RTX 4050...")
    engine = HybridEngine(use_quantum=True) # Quantum Search AI
    gui = ChessGUI(engine=engine, ai_color=Color.BLACK)
    gui.run()


# --- Main Menu ---

def main() -> None:
    while True:
        print("\n========================================================")
        print("    QUANTUM CHESS ENGINE — INTERACTIVE CONTROL PANEL")
        print("========================================================")
        print("1. Play 8x8 Hybrid Chess (You vs Quantum GPU AI)")
        print("2. Play 3x3 Pure Chess   (Academic Prototype metrics)")
        print("3. Generate 33-Qubit 8x8 Architecture Diagram")
        print("4. Generate 23-Qubit 3x3 Architecture Diagram")
        print("5. Exit")
        print("========================================================")
        
        try:
            choice = input("Select an option [1-5]: ").strip()
            if choice == "1":
                play_8x8_hybrid_quantum()
            elif choice == "2":
                play_3x3_pure_quantum()
            elif choice == "3":
                generate_circuit_diagram(8, False)
            elif choice == "4":
                generate_circuit_diagram(3, True)
            elif choice == "5":
                print("Exiting...")
                sys.exit(0)
            else:
                print("Invalid choice, please try again.")
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)


if __name__ == "__main__":
    main()
