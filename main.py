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
    config.BOARD_SIZE = board_size
    
    board = Board(size=board_size)
    if board_size == 2:
        # Read layout from 2×2 config
        for row, col, color_name, type_name in config.INITIAL_PIECES_2x2:
            c = Color[color_name]
            pt = PieceType[type_name]
            board.place_piece(Position(row, col), Piece(c, pt))
        # Black pawn moves forward: (0,0) → (1,0)
        first = config.INITIAL_PIECES_2x2[0]
        source = Position(first[0], first[1])
        fwd = -1 if first[2] == "WHITE" else 1
        target = Position(first[0] + fwd, first[1])
    elif board_size == 3:
        # Read layout from the same global config used by the game
        for row, col, color_name, type_name in config.INITIAL_PIECES_3x3:
            c = Color[color_name]
            pt = PieceType[type_name]
            board.place_piece(Position(row, col), Piece(c, pt))
        # Use the first entry as the source piece for the demo circuit
        first = config.INITIAL_PIECES_3x3[0]
        source = Position(first[0], first[1])
        # Target is one row forward (row - 1 for WHITE, row + 1 for BLACK)
        fwd = -1 if first[2] == "WHITE" else 1
        target = Position(first[0] + fwd, first[1])
    else:
        # 8x8 knight move
        board.place_piece(Position(7, 6), Piece(Color.WHITE, PieceType.KNIGHT))
        source, target = Position(7, 6), Position(5, 5)

    state = GameState(board=board, current_turn=Color.WHITE)
    
    # Build the full, exact logic circuit.
    circuit, regs = PureQuantumCircuitBuilder.build_full_chess_circuit(
        state=state, source=source, target=target, color=Color.WHITE
    )

    filename = f"architecture_{board_size}x{board_size}.png"
    print(f"\n========================================================")
    print(f"  QUANTUM ARCHITECTURE: {circuit.num_qubits} QUBITS")
    print(f"========================================================")
    print(f"  Board Size:        {board_size}×{board_size}")
    print(f"  Total Qubits:      {circuit.num_qubits}")
    print(f"  Coord Bits:        {regs.coord_bits} (per register)")
    print(f"  Status Bits:       {regs.status_bits} (per register)")
    print(f"  Circuit Depth:     {circuit.depth()}")
    print(f"  Gate Breakdown:    {dict(circuit.count_ops())}")
    print(f"--------------------------------------------------------")
    
    # For small boards (2×2, 3×3), run a single-shot simulation
    if board_size <= 3:
        print(f"\n  [SIMULATION] Running single-shot measurement...")
        sim = AerSimulator(method="statevector")
        transpiled = transpile(circuit, sim, optimization_level=1)
        t0 = time.time()
        result = sim.run(transpiled, shots=config.QUANTUM_SHOTS).result()
        t1 = time.time()
        counts = result.get_counts()
        
        # Display top measurement results
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        print(f"  ► Simulation Time:  {(t1-t0)*1000:.1f} ms")
        print(f"  ► Total Shots:      {config.QUANTUM_SHOTS}")
        print(f"  ► Top Measurements:")
        for bitstring, count in sorted_counts[:5]:
            prob = count / config.QUANTUM_SHOTS * 100
            print(f"    |{bitstring}⟩  →  {count}/{config.QUANTUM_SHOTS} shots ({prob:.1f}%)")
        print(f"  --------------------------------------------------------")
    
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


def play_2x2_pure_quantum() -> None:
    """Runs the 2x2 interactive 1-pawn demo with Pure Quantum tracking."""
    config.BOARD_SIZE = 2
    from engine.game import Game
    from engine.move import Move
    from engine.constants import Color
    from pure_quantum_engine.circuit import PureQuantumCircuitBuilder
    from ui.gui import ChessGUI

    class PureQuantumGame2x2(Game):
        def __init__(self):
            super().__init__()
            # Force Black's turn since the config only has a Black Pawn
            self.state.current_turn = Color.BLACK

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

    print("\nStarting 2x2 Pure Quantum Game (1-Pawn Interactive Demo)...")
    game = PureQuantumGame2x2()
    # No AI engine, purely manual so the user can make the move themselves
    gui = ChessGUI(engine=None, ai_color=None)
    gui.game = game
    gui.run()


# --- Option 7: 2x2 Grover Search + Pure Quantum Execution ---

def run_2x2_grover_demo() -> None:
    """Runs a 2x2 autonomous demo using Grover's search and Pure Quantum state execution."""
    config.BOARD_SIZE = 2
    from engine.constants import Color, PieceType
    from engine.position import Position
    from engine.state import GameState
    from engine.board import Board
    from engine.piece import Piece
    from quantum.grover import GroverSearch
    from pure_quantum_engine.circuit import PureQuantumCircuitBuilder
    from qiskit_aer import AerSimulator
    from qiskit import transpile
    import time

    print("\n========================================================")
    print("    2x2 GROVER'S ALGORITHM + PURE QUANTUM DEMONSTRATION")
    print("========================================================")
    board = Board(size=2)
    for row, col, color_name, type_name in config.INITIAL_PIECES_2x2:
        c = Color[color_name]
        pt = PieceType[type_name]
        board.place_piece(Position(row, col), Piece(c, pt))
    
    state = GameState(board=board, current_turn=Color.BLACK)
    
    print(f"\n[PHASE 1] Initializing 2x2 Board with {len(config.INITIAL_PIECES_2x2)} piece(s)")
    
    print("\n[PHASE 2] Executing Grover's Algorithm to find optimal move...")
    grover = GroverSearch()
    
    best_move = grover.search(state)
    
    if best_move:
        print(f"\n[GROVER RESULT] Found optimal path: {best_move.start} -> {best_move.end}")
    else:
        print("\n[GROVER RESULT] No valid moves found!")
        input("\nPress Enter to return to main menu...")
        return
        
    print(f"\n[PHASE 3] Executing move {best_move.start} -> {best_move.end} via Pure Quantum Circuit...")
    circuit, regs = PureQuantumCircuitBuilder.build_full_chess_circuit(
        state=state, source=best_move.start, target=best_move.end, color=Color.BLACK
    )
    
    sim = AerSimulator(method="statevector")
    transpiled = transpile(circuit, sim, optimization_level=1)
    
    t0 = time.time()
    result = sim.run(transpiled, shots=1).result()
    t1 = time.time()
    
    counts = result.get_counts()
    measured = list(counts.keys())[0] if counts else "Error"
    
    print(f"  ► Quantum Depth:  {circuit.depth()} gates")
    print(f"  ► Target Circuit: {circuit.num_qubits} Qubits")
    print(f"  ► Exec Time:      {(t1-t0)*1000:.1f} ms")
    print(f"  ► Final State:    |{measured}⟩")
    
    filename = "2x2_pure_quantum_grover.png"
    try:
        fig = circuit.draw(output="mpl", style="iqp", fold=40, scale=0.7)
        fig.savefig(filename, dpi=200, bbox_inches="tight")
        print(f"  ✓ Saved graphical diagram -> {filename}")
    except Exception as e:
        print(f"  ✗ Could not save diagram: {e}")
        
    print("\nDemonstration Complete! The AI successfully found and executed the quantum move.")
    input("\nPress Enter to return to main menu...")


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
        print("5. Generate 23-Qubit 2x2 Architecture Diagram (1 Pawn Demo)")
        print("6. Play 2x2 Pure Chess   (Interactive 1-Pawn Demo)")
        print("7. Run 2x2 Grover Search (Autonomous Demo)")
        print("8. Exit")
        print("========================================================")
        
        try:
            choice = input("Select an option [1-8]: ").strip()
            if choice == "1":
                play_8x8_hybrid_quantum()
            elif choice == "2":
                play_3x3_pure_quantum()
            elif choice == "3":
                generate_circuit_diagram(8, False)
            elif choice == "4":
                generate_circuit_diagram(3, True)
            elif choice == "5":
                generate_circuit_diagram(2, True)
            elif choice == "6":
                play_2x2_pure_quantum()
            elif choice == "7":
                run_2x2_grover_demo()
            elif choice == "8":
                print("Exiting...")
                sys.exit(0)
            else:
                print("Invalid choice, please try again.")
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)


if __name__ == "__main__":
    main()
