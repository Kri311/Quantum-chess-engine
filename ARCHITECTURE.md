# Architecture & Implementation Document

## Overview

The Quantum Chess Engine is a hybrid classical-quantum chess engine implemented in Python, applying genuine quantum computation to the game of chess using Qiskit. The project features a 3x3 pawn-chess board and is structured to demonstrate how quantum search algorithms can be applied to game trees. The core innovation is the use of Grover's Search Algorithm to evaluate and select valid chess moves, integrating this seamlessly with a classical chess engine and heuristic evaluator.

## Project Structure & Modules

The repository is modularized into several domains, separating classical game logic, quantum circuit building, AI evaluation, and user interface.

```
quantum-chess-engine/
├── ai/                      # AI logic (Heuristics, Minimax, Hybrid pipeline)
├── docs/                    # Technical documentation
├── engine/                  # Classical chess engine rules, state, and move generation
├── pure_quantum_engine/     # Pure quantum approach utilities
├── quantum/                 # Qiskit quantum circuits, Grover search, oracle, and encoding
├── tests/                   # Pytest testing suite
├── ui/                      # Pygame graphical user interface
├── config.py                # Global configurations
└── main.py                  # CLI entry point for console, GUI, or quantum modes
```

## Core Components and Pipelines

### 1. Classical Engine (`engine/`)
The classical engine maintains the state of the game and enforces the rules of pawn chess.
*   **State & Board (`board.py`, `state.py`)**: The board is represented as a dictionary mapping a coordinate `Position(row, col)` to a `Piece`. `GameState` is an immutable snapshot containing the board, current turn, and move history.
*   **Rules & Move Generation (`rules.py`, `move_generator.py`)**: Generates legal moves (forward push, diagonal captures) and validates moves. It uses a Strategy Pattern to handle different piece types (currently Pawns).
*   **Evaluation (`evaluator.py`)**: Provides heuristic scoring for board states to detect wins (reaching the opposite end or capturing all pieces) and draws.

### 2. Quantum Engine (`quantum/`)
This module handles translating the chess game into quantum circuits and running them on a simulator.
*   **Encoder / Decoder (`encoder.py`, `decoder.py`)**: Translates classical board positions into qubit bitstrings. A 3x3 board position uses 4 qubits (2 for X, 2 for Y). Piece status is encoded in 2 qubits (`00`: Empty, `01`: Black, `10`: White).
*   **Oracle (`oracle.py`)**: A reversible quantum circuit that acts as a move-legality checker. It marks legal moves with a phase flip (`-1`).
*   **Grover's Search (`grover.py`, `diffuser.py`)**: Implements Grover's Search Algorithm. It prepares a uniform superposition of all candidate moves, applies the oracle and diffuser iteratively, and amplifies the probability of measuring a valid, optimal move.
*   **Simulator (`simulator.py`)**: Wraps the Qiskit Aer simulator to execute circuits and aggregate measurement shots.

### 3. AI & Hybrid Engine (`ai/`)
Combines classical and quantum strategies into a single pipeline.
*   **Pipeline (`hybrid_engine.py`)**:
    1.  **Classical Generation**: The classical `MoveGenerator` produces all candidate moves.
    2.  **Heuristic Evaluation**: The classical `HeuristicEvaluator` scores and ranks moves.
    3.  **Quantum Search**: `QuantumMoveSearcher` encodes the candidates and uses Grover's algorithm to search for the best move by amplifying its probability amplitude.
    4.  **Fallback**: If quantum search is disabled or yields no result, it falls back to a classical `MinimaxEngine` with alpha-beta pruning.

### 4. User Interface (`ui/`)
*   **Renderer (`renderer.py`)**: Uses Pygame to draw the board, pieces, highlights, and text.
*   **GUI (`gui.py`)**: Handles the Pygame event loop, user clicks, and connects UI interactions to the `Game` orchestrator.

## Algorithms and Approach

### Quantum State Encoding
Based on the foundational paper *Design of Quantum Circuits to Play Chess in a Quantum Computer*:
*   **Position**: Each coordinate on the 3x3 board is represented as `|x1 x0 y1 y0>`, requiring 4 qubits. E.g., `(2, 1)` -> `|0110>`.
*   **Status**: 2 qubits per square. `|00>` (Empty), `|01>` (Black Pawn), `|10>` (White Pawn).

### Grover's Algorithm for Move Selection
Instead of iterating through moves sequentially (O(N)), Grover's algorithm offers a quadratic speedup O(sqrt(N)) for unstructured search.
1.  **Superposition**: All candidate moves are encoded into a quantum register in equal superposition.
2.  **Iterations**: The engine calculates the optimal number of Grover iterations: `floor((pi/4) * sqrt(N/M))`, where N is the total search space and M is the number of legal solutions.
3.  **Phase Kickback**: The `MoveOracle` applies a phase shift to legal moves.
4.  **Diffuser**: The `GroverDiffuser` performs inversion about the mean, amplifying the amplitude of the marked legal moves while diminishing illegal ones.
5.  **Measurement**: The circuit is measured, collapsing into a bitstring representing a legal move with high probability.

### Quantum Noise Modeling & Simulation
To approximate the behavior on physical Noisy Intermediate-Scale Quantum (NISQ) hardware, the simulation environment now incorporates realistic errors:
*   **Depolarizing Errors**: Qubits suffer from depolarizing noise, mimicking decoherence. The simulator injects a baseline error probability into single-qubit gates, and a higher probability (typically 10x) for multi-qubit entangling gates.
*   **Performance Impact**: Introducing noise forces the `AerSimulator` to move away from pure statevector evaluations towards density matrices or Kraus operators, increasing computation time (e.g. going from ~100ms to over 60 seconds on complex 19-qubit pure-quantum circuits) but accurately profiling real hardware viability.

## Data Flow Pipeline

1.  **Input**: User makes a move or AI is prompted to move via `Game.make_move()`.
2.  **State Encoding**: Classical `GameState` is transformed by `BoardEncoder` into qubit representations.
3.  **Circuit Building**: `CircuitBuilder` constructs the necessary registers, oracle, and diffuser based on the current state and candidate moves.
4.  **Quantum Execution**: The circuit is sent to the `QuantumSimulator` (Qiskit Aer) for `QUANTUM_SHOTS` executions.
5.  **Measurement & Decoding**: Measurement counts are analyzed by `MeasurementProcessor`. The highest frequency bitstring is decoded via `BoardDecoder` back into a classical `Move` object.
6.  **Update**: The classical `GameState` applies the move and updates the UI.

## Global Configurations (`config.py`)

The engine's tunable parameters are centralized in `config.py`:
*   **Board Configuration**: `BOARD_SIZE = 3` (3x3 grid). `TOTAL_SQUARES = 9`.
*   **Quantum Simulation**: 
    *   `QUANTUM_SHOTS = 1024`: The number of times the quantum circuit is measured to gather probability distributions.
    *   `QUANTUM_BACKEND = "aer_simulator"`: The local Qiskit simulator backend used.
    *   `QUANTUM_NOISE_ENABLED = True`: Whether the depolarizing noise model is applied.
    *   `QUANTUM_NOISE_PROB = 0.01`: The base probability rate of single-qubit gate errors.
*   **UI Settings**: `FPS = 60`, Window dimensions (`600x680`), animation speeds (`8.0`), and RGB color constants for the board (light/dark squares), highlights, and text.
