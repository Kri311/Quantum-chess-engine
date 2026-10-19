# Quantum Chess Engine Flowcharts

This folder contains Python-generated flowcharts for the complete system and its implementations. PNG files are ready to view or place in a presentation; SVG files are scalable. Mermaid sources remain alongside them as readable references.

## Main connected flowchart

![Connected Quantum Chess Engine implementation flowchart](generated/01_complete_project_map.png)

Regenerate every image with:

```bash
python docs/flowcharts/generate_flowcharts.py
```

The script writes PNG and SVG copies under `docs/flowcharts/generated/`.

## Generated diagrams

- [Complete connected implementation flowchart (PNG)](generated/01_complete_project_map.png) · [SVG](generated/01_complete_project_map.svg)
- [Gameplay implementation routes (PNG)](generated/02_gameplay_implementation_routes.png) · [SVG](generated/02_gameplay_implementation_routes.svg)
- [Quantum circuit paths (PNG)](generated/03_quantum_circuit_paths.png) · [SVG](generated/03_quantum_circuit_paths.svg)
- [3×3 evaluation flow (PNG)](generated/04_3x3_benchmark_flow.png) · [SVG](generated/04_3x3_benchmark_flow.svg)
- [3×3 piece-to-index-to-circuit walkthrough (PNG)](generated/05_3x3_piece_to_best_move.png) · [SVG](generated/05_3x3_piece_to_best_move.svg)
- [2×2 Black Pawn pure-circuit walkthrough (PNG)](generated/06_2x2_black_pawn_pure_quantum.png) · [SVG](generated/06_2x2_black_pawn_pure_quantum.svg)
- [Classical, quantum, and hybrid implementation flow (PNG)](generated/07_approach_implementation_flow.png) · [SVG](generated/07_approach_implementation_flow.svg)
- [Detailed 2×2, 3×3, and 8×8 implementation flows with configuration (PNG)](generated/08_detailed_system_implementation_flows.png) · [SVG](generated/08_detailed_system_implementation_flows.svg)
- [2×2 quantum implementation and configuration (PNG)](generated/09_2x2_system_implementation.png) · [SVG](generated/09_2x2_system_implementation.svg)
- [3×3 Minimax and circuit-trace implementation (PNG)](generated/10_3x3_system_implementation.png) · [SVG](generated/10_3x3_system_implementation.svg)
- [8×8 hybrid Grover implementation and configuration (PNG)](generated/11_8x8_hybrid_system_implementation.png) · [SVG](generated/11_8x8_hybrid_system_implementation.svg)
- [2×2 Grover search and move-circuit flow (PNG)](generated/12_2x2_grover_circuit_flow.png) · [SVG](generated/12_2x2_grover_circuit_flow.svg)

The detailed 2×2 Grover/circuit flow is generated separately with:

```bash
python docs/flowcharts/generate_2x2_grover_circuit_flow.py
```

## Reading order

1. [Whole-project map](00_project_overview.md) — where the menu, UI, chess model, AI, and circuit modules connect.
2. [8×8 hybrid game](01_8x8_hybrid_game.md) — human move, classical legality and scoring, Grover index circuit, fallback, and state update.
3. [3×3 pure-circuit game](02_3x3_pure_game.md) — classical minimax opponent, per-move circuit, measurement, and classical state update.
4. [2×2 demonstrations](03_2x2_demonstrations.md) — interactive pawn mode and the menu's Grover-labelled autonomous route.
5. [Pure-circuit builder](04_pure_circuit_builder.md) — register allocation, initialization, status lookup, direction logic, status operation, and measurement.
6. [3×3 benchmark](05_3x3_benchmark.md) — fixed-position generation, three system branches, metrics, and output files.
7. [Circuit-diagram generation](06_circuit_diagram_generation.md) — menu options 3–5 and the diagram output path.

## Important interpretation

“Pure quantum” is the project name for a small-board circuit demonstration. The chess `GameState`, legal move generation, UI, and final board update are classical. The pure circuit receives a selected move and reports a measured circuit string; it does not maintain or update a complete chessboard in qubits.

The charts distinguish implemented behavior from intended labels. In particular, menu option 7 calls `GroverSearch.search(state)` without supplied candidates or target indices. The current oracle helper produces only legal candidates; all are then marked as targets, so `GroverSearch` returns the first candidate before constructing or running a Grover circuit. The pure-circuit simulation still runs afterward.

## Project locations

- Entry menu and demo wrappers: `main.py`
- Defaults and example layouts: `config.py`
- Board, state, move rules, and transitions: `engine/`
- Classical and hybrid AI: `ai/`
- Grover components and simulator wrapper: `quantum/`
- Small-board reversible-circuit prototype: `pure_quantum_engine/`
- Graphical UI: `ui/`
- Three-system measurement script: `evaluation/compare_3x3_systems.py`
