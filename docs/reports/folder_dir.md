# Project Folder and File Guide

This document maps the repository after organization. It describes what each tracked project file and folder is responsible for, and where generated/reference artifacts belong.

## Repository layout

```text
quantum_chess_engine/
├── ai/                         AI selection and search
├── docs/                       Design documents and project artifacts
│   ├── assets/diagrams/        Architecture and circuit images
│   ├── circuits/               Saved ASCII circuit diagrams
│   ├── flowcharts/              Python-generated system flowcharts and sources
│   │   └── generated/           Python-rendered PNG and SVG flowcharts
│   └── reports/                Faculty reports and this file map
├── engine/                     Classical chess domain and rules
├── evaluation/                 3×3 runtime and circuit-resource comparison
├── pure_quantum_engine/        Coordinate/status circuit prototype
├── quantum/                    Encoding, Grover search, and simulation
├── tests/                      Automated checks for core behavior
├── tools/                      Standalone circuit-inspection scripts
├── ui/                         Pygame interface and rendering
├── config.py                   Shared board and simulation settings
├── main.py                     Interactive application entry point
├── requirements.txt            Python dependency list
├── README.md                   Project overview and usage
├── ARCHITECTURE.md             Detailed architecture notes
├── JOURNAL.md                  Development notes and project history
└── LICENSE                     Project license
```

## Root-level files

| File | Responsibility |
|---|---|
| `.gitignore` | Excludes local environments, Python bytecode, test caches, and selected local files from Git. |
| `.python-version` | Declares the Python version expected by version managers. |
| `README.md` | Project overview, architecture summary, installation, run modes, and test commands. |
| `ARCHITECTURE.md` | Expanded architecture and data-flow notes retained as a top-level project reference. |
| `JOURNAL.md` | Development journal documenting design decisions and project progress. |
| `LICENSE` | Terms under which the project may be used and distributed. |
| `config.py` | Default board size, demo piece layouts, shot count, Aer backend/noise settings, and UI dimensions/colors. |
| `main.py` | Interactive menu and orchestration for 8×8 hybrid play, 3×3 and 2×2 demonstrations, and architecture diagram generation. Generated architecture images are written to `docs/assets/diagrams/`. |
| `requirements.txt` | Pinned and minimum Python package requirements for Qiskit, Aer, numerical work, graphics, tests, and code quality. |

## Application packages

### `engine/` — classical chess model and rules

| File | Responsibility |
|---|---|
| `engine/__init__.py` | Package initialization and public engine exports. |
| `engine/constants.py` | Enumerations and shared constants for color, piece type, and direction. |
| `engine/position.py` | Immutable board coordinate value object. |
| `engine/piece.py` | Chess piece value object containing color and piece type. |
| `engine/pieces.py` | Factory/helper functions for creating the initial piece arrangement. |
| `engine/move.py` | Move value object, source/destination representation, and direction helpers. |
| `engine/board.py` | Board storage, occupancy queries, bounds checks, and piece placement/removal. |
| `engine/state.py` | Game state containing the board, current side, and state transitions/history. |
| `engine/rules.py` | Stateless move validation helpers. |
| `engine/move_generator.py` | Piece-specific pseudo-legal move generation and filtering for legal moves. |
| `engine/evaluator.py` | Position evaluation, terminal-state, winner, and draw-related logic. |
| `engine/game.py` | Game orchestration and public move-application interface. |

### `ai/` — move scoring and selection

| File | Responsibility |
|---|---|
| `ai/__init__.py` | AI package initialization. |
| `ai/classical_3x3.py` | 3×3 classical selector used by the system comparison. |
| `ai/heuristic.py` | Classical position and per-move heuristic scoring. |
| `ai/minimax.py` | Classical minimax search with alpha-beta pruning and move ordering. |
| `ai/quantum_search.py` | Prepares heuristic-best legal-move indices and invokes Grover search; provides a classical fallback. |
| `ai/hybrid_engine.py` | Coordinates legal move generation, quantum-assisted selection, and minimax fallback. |

### `quantum/` — shared quantum search and simulation

| File | Responsibility |
|---|---|
| `quantum/__init__.py` | Quantum package initialization. |
| `quantum/registers.py` | Register allocation for the general/paper-inspired circuit path. |
| `quantum/encoder.py` | Converts classical positions, statuses, and boards to encoded bit strings/register initialization. |
| `quantum/decoder.py` | Converts measured bit strings and indices back to classical data. |
| `quantum/circuit_builder.py` | Builds reusable comparator, direction, and status subcircuits. |
| `quantum/oracle.py` | Builds the reversible index-marking oracle used by Grover search. |
| `quantum/diffuser.py` | Builds the inversion-about-the-mean operator. |
| `quantum/grover.py` | Creates and executes the Grover search circuit and decodes the measured candidate. |
| `quantum/measurement.py` | Processes shot counts and selects likely measurement results. |
| `quantum/simulator.py` | Qiskit Aer wrapper, transpilation, shots, optional noise model, and GPU/CPU fallback. |

### `pure_quantum_engine/` — board-transition circuit prototype

| File | Responsibility |
|---|---|
| `pure_quantum_engine/__init__.py` | Pure-circuit package initialization. |
| `pure_quantum_engine/registers.py` | Allocates coordinate, direction, status, ancilla, and classical-readout registers. |
| `pure_quantum_engine/circuit.py` | Assembles the paper-inspired status extraction, direction, and status-operation circuit. |
| `pure_quantum_engine/engine.py` | Runs a built pure circuit and returns measurement counts and structural/runtime metrics. |
| `pure_quantum_engine/benchmark.py` | Runs a comparative circuit/engine benchmark and prints metrics. |

### `ui/` — graphical interface

| File | Responsibility |
|---|---|
| `ui/__init__.py` | UI package initialization. |
| `ui/gui.py` | Pygame event loop, user interaction, game flow, and AI turn integration. |
| `ui/renderer.py` | Board, pieces, labels, move hints, and status rendering. |
| `ui/animations.py` | Piece movement animation helpers. |

## Documentation and artifacts

### `docs/` — design references

| File | Responsibility |
|---|---|
| `docs/architecture.md` | Layered software architecture, module relationships, and data flow. |
| `docs/quantum_design.md` | Quantum design intent, encoding, oracle, and Grover discussion. |
| `docs/circuit_design.md` | Register and gate-level design reference for the circuit prototype. |
| `docs/2x2_qc_architecture.md` | Focused architectural explanation for the minimal 2×2 circuit scenario. |
| `docs/2x2_pure_quantum_grover.md` | Detailed 2×2/3×3 gate and register walkthrough, separate Grover-index path, worked move-selection example, and classical/quantum responsibility split. |

### `docs/assets/diagrams/` — image artifacts

These are saved architecture and Qiskit circuit images for reports, presentations, and visual inspection. The 2×2 architecture circuit has one canonical image; the two byte-identical duplicate copies were removed.

| File | Responsibility |
|---|---|
| `architecture_2x2.png` | Canonical 2×2 pure-circuit diagram, also produced by menu diagram generation and the 2×2 Grover demo. |
| `architecture_3x3.png` | Saved 3×3 circuit/architecture diagram. |
| `architecture_8x8.png` | Saved 8×8 pure-circuit architecture diagram. |
| `chess_archi.png` | Project-level chess architecture visual. |
| `complete_qiskit_circuit.png` | Full circuit visualization artifact. |
| `pure_3x3_qiskit_circuit.png` | 3×3 pure-circuit visualization. |
| `pure_circuit.png` | Additional saved pure-circuit visualization. |
| `pure_quantum_3x3_circuit.png` | 3×3 pure quantum circuit visualization. |
| `with_knight.png` | Circuit visualization for the knight example generated by `tools/inspect_pure_circuit.py`. |

### `docs/circuits/` — text circuit artifacts

| File | Responsibility |
|---|---|
| `2x2_circuit.txt` | Saved ASCII circuit dump for the 2×2 demonstration. |
| `pure_circuit.txt` | Full ASCII output produced by `tools/inspect_pure_circuit.py`. |
| `pure_quantum_3x3_circuit.txt` | Saved ASCII dump for the 3×3 pure circuit. |

### `docs/flowcharts/` — implementation flowcharts

| File | Responsibility |
|---|---|
| `README.md` | Reading order, diagram scope, important behavior notes, and source-code locations. |
| `00_project_overview.md` | Connects the application menu, shared chess core, AI, circuit paths, and benchmark outputs. |
| `01_8x8_hybrid_game.md` | Shows human/AI turns, classical move preparation, Grover selection, fallback, and board update. |
| `02_3x3_pure_game.md` | Shows the selected-move circuit path and classical minimax opponent/state update. |
| `03_2x2_demonstrations.md` | Separately explains the interactive pawn route and the Grover-labelled autonomous route. |
| `04_pure_circuit_builder.md` | Details register allocation, coordinate initialization, status lookup, gate stages, and readout. |
| `05_3x3_benchmark.md` | Traces the classical, pure-circuit, and hybrid measurement branches to their result files. |
| `06_circuit_diagram_generation.md` | Shows menu circuit-generation inputs, simulation choices, and saved image outputs. |
| `generate_flowcharts.py` | Python/Matplotlib renderer for the six connected PNG and SVG flowcharts. |
| `generated/01_complete_project_map.png` and `.svg` | Unified overview linking menu routes to the implementation lanes and outputs. |
| `generated/02_gameplay_implementation_routes.png` and `.svg` | Rendered comparison of the 8×8, 3×3, and 2×2 play/demo routes. |
| `generated/03_quantum_circuit_paths.png` and `.svg` | Rendered pure-circuit and hybrid Grover circuit workflows. |
| `generated/04_3x3_benchmark_flow.png` and `.svg` | Rendered comparison pipeline from positions through metrics and result files. |
| `generated/05_3x3_piece_to_best_move.png` and `.svg` | One connected 3×3 walkthrough from classical board and move indices through Grover sampling, the software Move handoff, and separate pure-circuit measurement. |
| `generated/06_2x2_black_pawn_pure_quantum.png` and `.svg` | Interactive 2×2 Black Pawn example from board setup and move encoding through pure-circuit readout and classical state update. |

### `docs/reports/` — faculty reports and repository guide

| File | Responsibility |
|---|---|
| `chess_engine_quantum.md` | Detailed architecture, encoding, gate, Grover, configuration, and limitation explanation for faculty. |
| `ques_ans.md` | Faculty-style oral-exam question bank with answers and challenging prompts. |
| `3x3_system_comparison.md` | Generated comparison of the classical, pure quantum, and hybrid 3×3 systems, with metric explanations and aggregate results. |
| `project_implementation_report.md` | Combined faculty/team report covering architecture, configurations, gates, phases, results, run steps, and the Markdown documentation set. |
| `folder_dir.md` | This file: a map of folder and file responsibilities. |

## Evaluation, tests, and utilities

### `evaluation/`

| File | Responsibility |
|---|---|
| `evaluation/compare_3x3_systems.py` | Builds a deterministic 3×3 position set, measures classical, pure quantum, and hybrid systems, and writes CSV, PNG, and Markdown results. |
| `evaluation/best_move.py` | Backward-compatible command that runs `compare_3x3_systems.py`. |
| `evaluation/results/3x3_comparison.png` | Four metric panels with the three 3×3 systems on the x-axis and execution time, extra peak RAM, qubits, and gate count as separate y-axis metrics. |
| `evaluation/results/3x3_comparison_summary.csv` | Aggregate metrics by 3×3 system. |
| `evaluation/results/3x3_comparison_positions.csv` | Per-position legal-move count, execution time, extra peak RAM, and circuit resource measurements. |

### `tests/`

| File | Responsibility |
|---|---|
| `tests/__init__.py` | Test package initialization. |
| `tests/test_board.py` | Board storage and occupancy behavior checks. |
| `tests/test_state.py` | Game-state transition checks. |
| `tests/test_moves.py` | Move representation and movement behavior checks. |
| `tests/test_rules.py` | Rule validation checks. |
| `tests/test_knights.py` | Knight movement checks. |
| `tests/test_encoder.py` | Encoding/decoding checks. |
| `tests/test_oracle.py` | Oracle behavior checks. |
| `tests/test_grover.py` | Grover circuit/search behavior checks. |
| `tests/test_pure_quantum.py` | Pure-circuit construction/execution checks. |
| `tests/integration_test.py` | Cross-module integration checks. |

### `tools/`

| File | Responsibility |
|---|---|
| `tools/inspect_circuit.py` | Builds and prints a small Grover circuit summary and ASCII drawing. |
| `tools/inspect_pure_circuit.py` | Builds a pure-circuit example and saves its text and image outputs to `docs/circuits/` and `docs/assets/diagrams/`. |

## Presentation and report outputs

| Path | Responsibility |
|---|---|
| `outputs/Quantum_Chess_Project/Quantum_Chess_Project_Presentation.pptx` | Faculty presentation adapted to the supplied visual reference. |
| `outputs/Quantum_Chess_Project/Quantum_Chess_Project_Report.docx` | Editable implementation report. |
| `outputs/Quantum_Chess_Project/Quantum_Chess_Project_Report.pdf` | PDF reading/printing copy of the implementation report. |

## Local-only folders

These can appear in a developer checkout but are not part of the source layout described above:

| Folder | Responsibility / handling |
|---|---|
| `venv1/` | Ignored local Python virtual environment. Keep local; recreate from `requirements.txt` if needed. |
| `.pytest_cache/`, `__pycache__/` | Disposable test and Python runtime caches; safe to remove and ignored by Git. |
| `.agents/`, `.aws/`, `.codex/` | Workspace/tool metadata when present. These are not application packages and should be left to their owning tools. |

## Output locations and run commands

- `python main.py` runs the interactive menu. Architecture diagrams are saved under `docs/assets/diagrams/`.
- `python tools/inspect_circuit.py` prints a Grover circuit summary and diagram without creating an output file.
- `python tools/inspect_pure_circuit.py` writes `docs/circuits/pure_circuit.txt` and `docs/assets/diagrams/with_knight.png`.
- The 2×2 and 3×3 circuits can also be inspected in the saved artifacts under `docs/circuits/` and `docs/assets/diagrams/`.
- `python evaluation/compare_3x3_systems.py` runs the fixed 3×3 comparison and writes the plot and CSV tables to `evaluation/results/`, plus the faculty report to `docs/reports/3x3_system_comparison.md`.
- `python evaluation/best_move.py` is a compatibility alias for the same comparison.
