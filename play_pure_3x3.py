#!/usr/bin/env python3
"""
Interactive Pure Quantum 3x3 GUI.

Plays a game of 3x3 Pawn Chess where every move is executed by building
and simulating the complete 23-qubit pure quantum architecture (from the
base paper, extended for all piece types) before the classical board is
updated.
"""

import time
import config

# Force 3x3 configuration
config.BOARD_SIZE = 3

from qiskit import transpile
from qiskit_aer import AerSimulator

from engine.game import Game
from engine.move import Move
from pure_quantum_engine.circuit import PureQuantumCircuitBuilder
from ui.gui import ChessGUI

class PureQuantumGame(Game):
    """A Game subclass that intercepts moves to execute them quantumly."""

    def make_move(self, move: Move) -> None:
        """Execute the move on a pure quantum circuit before updating board."""
        print(f"\n[PURE QUANTUM] User requested move: {move}")
        print("[PURE QUANTUM] Building 23-qubit physical simulation circuit...")
        
        # Build the exact physical simulation circuit
        circuit, regs = PureQuantumCircuitBuilder.build_full_chess_circuit(
            state=self.state,
            source=move.start,
            target=move.end,
            color=self.state.current_turn
        )
        
        print("[PURE QUANTUM] Executing move via Statevector Simulation...")
        sim = AerSimulator(method="statevector")
        transpiled = transpile(circuit, sim, optimization_level=1)
        
        t0 = time.time()
        result = sim.run(transpiled, shots=1).result()
        t1 = time.time()
        
        counts = result.get_counts()
        measured_string = list(counts.keys())[0]
        
        print(f"[PURE QUANTUM] Move executed in {(t1-t0)*1000:.1f}ms")
        print(f"[PURE QUANTUM] Measured bitstring (cur|tgt|src|dst|dir|anc): {measured_string}")
        print("[PURE QUANTUM] State collapsed. Updating classical UI...")
        
        # Call the actual classical move to advance the state for the GUI
        super().make_move(move)


def main() -> None:
    print("======================================================")
    print("   PURE QUANTUM CHESS — 3x3 ACADEMIC PROTOTYPE")
    print("======================================================")
    print("Every move you make will generate a full 23-qubit circuit")
    print("simulating the exact physical move via quantum gates.")
    print("Check your terminal to see the execution details!\n")
    
    # Initialize our custom Pure Quantum Game
    game = PureQuantumGame()
    
    # Pass it into the PyGame GUI (no AI engine, human vs human)
    gui = ChessGUI(engine=None, ai_color=None)
    gui.game = game  # Inject our custom game
    
    # Run the GUI
    gui.run()


if __name__ == "__main__":
    main()
