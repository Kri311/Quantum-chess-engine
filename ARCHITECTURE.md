# Quantum Chess Engine: Architecture & Implementation

**Presented to the Quantum Computing Faculty**

Respected Faculty,

The project I am presenting is a hybrid classical-quantum chess engine. Drawing inspiration from the foundational paper *"Design of Quantum Circuits to Play Chess in a Quantum Computer"*, this engine scales the theoretical 3x3 pawn-chess prototype into a playable 8x8 board featuring Pawns and Knights. 

Our core innovation is twofold:
1. **Move Selection via Grover's Search**: Utilizing amplitude amplification to achieve a quadratic speedup when searching the game tree for optimal moves.
2. **Pure Quantum Circuit Execution**: Constructing massive multi-qubit reversible circuits to extract piece status, verify move directions, and update board states completely within a quantum simulation.

---

## 1. Directory Structure (Lecture Breakdown)

To ensure the engine is modular and maintainable, the codebase is strictly separated into classical, quantum, and hybrid domains:

### `engine/` (Classical Game Mechanics)
*Why we need it:* Before we can run quantum algorithms, we need a classical oracle to define what a chess board is. This module handles the fundamental physics of the board, tracking the `GameState`, the 8x8 grid bounds, and piece collision rules (`rules.py`, `move_generator.py`). It prevents the quantum engine from searching physically impossible states.

### `quantum/` (The Quantum Subsystem)
*Why we need it:* This is where the classical rules are translated into quantum operations.
*   **`encoder.py` & `decoder.py`**: Maps classical board positions and piece types into quantum bitstrings.
*   **`oracle.py` & `grover.py`**: Implements Grover's algorithm. Instead of O(N) classical search, we prepare a superposition of all candidate moves, apply phase kickback via the oracle to mark the legal/optimal moves, and amplify their probability amplitudes using the `diffuser.py`.
*   **`simulator.py`**: Wraps Qiskit's `AerSimulator`. Crucially, this is where we inject **Depolarizing Noise** into the gates to simulate the decoherence inherent in physical NISQ (Noisy Intermediate-Scale Quantum) devices.

### `pure_quantum_engine/` (The Paper Implementation)
*Why we need it:* While the `quantum/` folder uses Grover to *search* for moves, this module attempts to execute the state transition itself using pure quantum gates (mapping Figures 4-7 from the research paper).
*   **`circuit.py`**: Uses multi-controlled X gates (MCX) and CNOTs to build a massive circuit containing Status Extractors, Subtractor/Comparators for direction detection, and Status Operators for board state updates.
*   **`registers.py`**: Dynamically allocates the required quantum registers (coordinates, statuses, direction, and ancilla workspace qubits).

### `ai/` (The Hybrid Bridge)
*Why we need it:* Real quantum hardware is noisy and limited by circuit depth. `hybrid_engine.py` merges classical Minimax (Alpha-Beta pruning) with our Quantum Grover search. If the quantum circuit decoheres or the search space is too massive, it can safely fall back to the classical engine.

### `ui/` & `main.py` (Interactivity)
*Why we need it:* To allow us to actually play against the quantum engine! `gui.py` provides a Pygame visualizer where a human can play the White pieces, triggering the quantum backend to compute the Black pieces' moves in real-time.

---

## 2. Quantum State Encoding

Scaling the paper from 3x3 to 8x8 required expanding the qubit registers significantly.

### Coordinate Encoding (6 Qubits)
Each square is identified by a binary representation of its (X, Y) coordinates. An 8x8 grid requires 3 bits per axis (`ceil(log2(8)) = 3`).
*   Example: Square (Row 4, Col 4) maps to `|x2 x1 x0 y2 y1 y0>` $\rightarrow$ `|100100>`.

### Status Encoding (3 Qubits)
To support multiple piece types (Empty, Pawns, Knights) and their colours, we require 3 qubits per square:
*   `|000>`: Empty Square
*   `|001>`: Black Pawn
*   `|101>`: White Pawn
*   `|010>`: Black Knight
*   `|110>`: White Knight
*(The Most Significant Bit denotes colour, the lower 2 bits denote piece type).*

---

## 3. Pure Quantum Circuitry & Knights Scaling

In the `pure_quantum_engine/circuit.py`, the quantum state transition relies on Reversible Computing principles:

1. **Status Extractor**: We use X gates to conditionally flip coordinate qubits, allowing us to use MCX gates to extract the 3-qubit status of a square onto an output register without collapsing the board state.
2. **Direction Detection**: For pawns, subtracting the target coordinates from the current coordinates yields a specific signature (e.g., Forward, Diagonal). For Knights, the logic is highly complex: it requires a full quantum subtractor and absolute value circuit to verify `|Δx| == 2` and `|Δy| == 1` (or vice versa). We have expanded the direction register to 4 qubits to accommodate these new vectors.
3. **Status Operator**: The operator conditionally swaps the 3-qubit statuses between the source and target registers based on the validated direction, successfully executing a quantum move.

## 4. Hardware Realities & Simulation

Because this 8x8 architecture generates circuits with hundreds of gates and massive depth, we implemented realistic noise modeling in `config.py` (`QUANTUM_NOISE_ENABLED`). 
By applying depolarizing errors (with two-qubit entangling gates suffering 10x the error rate of single-qubit gates), the Qiskit simulator demonstrates how this engine would perform on actual, noisy IBM Quantum processors today, highlighting the balance between theoretical algorithms and physical hardware limitations.
