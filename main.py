#!/usr/bin/env python3
"""
Quantum Chess Engine — entry point.

Usage:
    python main.py                  # default: console mode
    python main.py --mode console   # interactive terminal game
    python main.py --mode gui       # pygame graphical interface
    python main.py --mode quantum   # hybrid quantum-classical game
"""

from __future__ import annotations

import argparse
import sys


def _parse_args() -> argparse.Namespace:
    """Build and parse command-line arguments.

    Returns:
        Parsed ``Namespace`` with a ``mode`` attribute.
    """
    parser = argparse.ArgumentParser(
        prog="quantum-chess-engine",
        description="Hybrid classical-quantum chess engine (3×3 pawn chess)",
    )
    parser.add_argument(
        "--mode",
        choices=["console", "gui", "quantum", "quantum_gui"],
        default="console",
        help="Game mode: console (default), gui, quantum (AI vs AI), or quantum_gui (Human vs Quantum AI).",
    )
    return parser.parse_args()


def main() -> None:
    """Dispatch to the selected game mode."""
    args = _parse_args()

    if args.mode == "console":
        from engine.game import Game

        game = Game()
        game.play()

    elif args.mode == "gui":
        from ui.gui import ChessGUI

        gui = ChessGUI()
        gui.run()

    elif args.mode == "quantum":
        from ai.hybrid_engine import HybridEngine
        from engine.game import Game

        game = Game()
        engine = HybridEngine(use_quantum=True) # Enabled for Qiskit Aer GPU offloading
        engine.play_game(game)
        
    elif args.mode == "quantum_gui":
        from ai.hybrid_engine import HybridEngine
        from ui.gui import ChessGUI
        from engine.constants import Color
        
        engine = HybridEngine(use_quantum=True) # Enabled for Qiskit Aer GPU offloading
        gui = ChessGUI(engine=engine, ai_color=Color.BLACK)
        gui.run()

    else:
        print(f"Unknown mode: {args.mode}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
