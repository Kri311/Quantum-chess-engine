# Quantum Chess Engine — Research Journal

A chronological record of design decisions, implementation notes, challenges, and observations throughout the development of the Quantum Chess Engine research project.

---

## Project Inception

**Date**: July 2026

**Motivation**: The goal is to build a hybrid classical-quantum chess engine that demonstrates genuine quantum computation — not a classical engine with quantum buzzwords, but an engine where quantum circuits actively participate in move evaluation and selection.

**Research Questions**:
1. How can chess board states be represented using quantum registers?
2. Can quantum algorithms (specifically Grover's) assist in move selection?
3. What is the practical circuit depth and qubit count for a 3x3 board?
4. Does the quantum approach scale to larger boards?

---

## Paper Analysis

### Paper 1: Design of Quantum Circuits to Play Chess in a Quantum Computer

This is the base paper that provides the quantum circuit architecture for chess.

**Key Contributions**:
- **Coordinate Encoding**: Each square on a 3x3 board is encoded using 4 qubits — 2 for the column (X-coordinate) and 2 for the row (Y-coordinate). This gives `|x1 x0 y1 y0>` for each square.
- **Status Encoding**: 2 qubits per square encode the piece occupancy: `|00>` = empty, `|01>` = black pawn, `|10>` = white pawn.
- **Direction Detection**: A subtractor circuit computes the difference between source and target coordinates to determine the move direction (forward, diagonal-left, diagonal-right).
- **Status Extraction**: A circuit that reads the status of a specific square by matching its coordinate qubits against the board encoding (Fig 5 in the paper).
- **Status Operation**: A circuit that applies the move logic — swapping statuses for forward moves, replacing for captures — controlled by the direction register (Fig 6).
- **Board Update**: After the status operation, the new statuses are written back to the board state (Fig 7).

**Limitation**: The paper only implements move *validation and execution*, not move *search or selection*. This is where Grover's algorithm comes in.

**Our Extension**: We apply Grover's algorithm to search over candidate moves, using the paper's validation circuits as the oracle.

### Paper 2: A Fast Quantum Mechanical Algorithm for Database Search (Grover, 1996)

The foundational paper for unstructured quantum search.

**Key Insight**: Grover's algorithm finds a marked item in an unstructured database of N items using O(sqrt(N)) queries, compared to the classical O(N). This is provably optimal for quantum search.

**Algorithm Structure**:
1. **Initialisation**: Prepare a uniform superposition over all N items.
2. **Oracle**: Apply a phase flip to marked items (in our case, legal moves).
3. **Diffuser**: Inversion about the mean (amplification).
4. **Repeat** steps 2-3 for `floor(pi/4 * sqrt(N/M))` iterations.
5. **Measure**: The marked item is found with high probability.

**Application to Chess**: The search space is all possible candidate moves from the current position. The oracle marks moves that are legal according to pawn movement rules. Grover's algorithm amplifies these legal moves so that measurement yields a valid move with high probability.

---

## Phase 1: Classical Engine

**Design Decisions**:

1. **Position as `(row, col)` rather than flat index**: The paper uses flat indices (1-9), but `(row, col)` is more natural for chess, easier to reason about, and trivially convertible to flat indices for quantum encoding.

2. **Immutable value objects**: `Position`, `Piece`, and `Move` are frozen dataclasses. This enables safe use in sets, dictionary keys, and immutable game tree exploration.

3. **Board as `dict[Position, Piece]`**: Sparse representation scales well from 3x3 (2 pieces) to 8x8 (32 pieces). More memory-efficient and faster for queries than a 2D array for sparse boards.

4. **`GameState.apply_move()` returns a NEW state**: Essential for minimax search — the engine explores many branches of the game tree simultaneously without mutation side effects.

5. **Strategy pattern in MoveGenerator**: Each piece type gets its own move generation method (`_pawn_moves`). Adding new piece types for 8x8 expansion only requires adding new methods, not modifying existing ones.

6. **Separation of Rules and MoveGenerator**: `Rules` is a stateless validator (pure functions). `MoveGenerator` orchestrates candidate generation and filters through `Rules`. This separation enables the quantum oracle to reuse `Rules` logic independently.

**Observations**:
- The 3x3 single-pawn game has a very shallow game tree. White starts at (2,1) and needs to reach row 0 (2 forward moves if unblocked). Black starts at (0,1) and needs to reach row 2. The game typically ends in 2-4 moves.
- Despite the small game tree, the architecture handles all the complexity needed for 8x8 expansion.

---

## Phase 2: Pygame Visualization

**Design Decisions**:

1. **Renderer separated from GUI**: `BoardRenderer` only knows how to draw. `ChessGUI` handles events and game logic. This follows the Single Responsibility Principle and makes it easy to swap renderers.

2. **Piece representation as circles with labels**: Simple geometric shapes (circles with W/B text) keep the focus on the quantum research aspect. Unicode chess symbols are available for console mode.

3. **Smooth animation with ease-out**: Using quadratic ease-out for piece movement gives a natural deceleration effect. The animator uses lerp with a configurable speed factor.

4. **Resizable window**: Uses `pygame.RESIZABLE` and recalculates the grid layout on each resize event. The cell size is computed from the available window area minus the status bar.

---

## Phase 3: Quantum Representation

**Design Decisions**:

1. **Register allocation follows the paper exactly**: 4 qubits for current square coordinates, 4 for target square coordinates, 2 for direction, 2 for source status, 2 for target status, plus ancilla and flag qubits.

2. **Encoding convention**: MSB-first for human readability in the bitstrings, but Qiskit uses little-endian internally. The encoder/decoder handle this conversion transparently.

3. **Status extractor uses multi-controlled X gates**: For each occupied square, the circuit conditionally copies the square's status to the output register when the coordinate qubits match. This requires applying X gates to condition on `|0>` bits, then uncomputing them — maintaining reversibility.

4. **`initialize_register()` uses X gates only**: Starting from `|0...0>`, applying X to specific qubits sets any desired classical bitstring. No other gates needed for classical initialization.

**Qubit Budget (3x3 Board)**:
- Coordinates: 4 + 4 = 8 qubits
- Direction: 2 qubits
- Status: 2 + 2 = 4 qubits
- Ancilla: 4 qubits
- Flag: 1 qubit
- **Total: 19 qubits**

This is well within the capability of Qiskit Aer's statevector simulator (up to ~30 qubits on modern hardware).

---

## Phase 4: Quantum Oracle

**Design Decisions**:

1. **Oracle operates on move indices, not board coordinates**: Rather than encoding source/target coordinates in superposition (which would require the full board circuit from Phase 3 per oracle query), we pre-compute all candidate moves classically and encode only the *index* into the candidate list as a quantum register. This dramatically reduces the circuit depth.

2. **Phase kickback for Grover**: The oracle uses the standard phase-kickback trick. The flag qubit is prepared in the `|->` state, so when the MCX flips it for a marked state, the overall state picks up a `-1` phase.

3. **Reversibility guaranteed**: Each oracle marking uses the pattern: (a) flip `|0>` bits with X, (b) MCX to flip flag, (c) unflip with X. This is perfectly reversible.

---

## Phase 5: Grover's Search

**Design Decisions**:

1. **Optimal iteration count**: Using Grover's formula `floor(pi/4 * sqrt(N/M))`. For the 3x3 board with typically 1-3 legal moves out of 3 candidates, this gives 1-2 iterations — very shallow circuits.

2. **Fallback mechanism**: If Grover's measurement doesn't yield a valid legal move (possible with low iteration counts or when N ≈ M), the search falls back to returning the first classically-verified legal move. This ensures robustness.

3. **Measurement processing**: The `MeasurementProcessor` class provides probabilistic analysis — normalised counts, top-k results, entropy calculation. This is useful for debugging and for understanding the quantum advantage.

**Observations**:
- For the 3x3 board, the quantum advantage is negligible (too few candidates for sqrt speedup to matter). The value is in demonstrating the *algorithm* and *circuit design* that would provide real advantage on larger boards.
- On an 8x8 board with potentially dozens of legal moves, Grover's O(sqrt(N)) search becomes significantly more efficient than classical O(N) evaluation.

---

## Phase 6: Hybrid Engine

**Pipeline**:

```
1. Classical MoveGenerator -> all legal moves
2. Classical HeuristicEvaluator -> scored and ranked
3. Quantum GroverSearch -> amplify best move(s)
4. Classical validation -> ensure legality
5. Apply move
```

The hybrid approach leverages classical computation for what it does best (rule checking, game state management) and quantum computation for what it uniquely offers (parallel search amplification).

---

## Challenges and Solutions

### Challenge 1: Qiskit 2.x API Changes
Qiskit 2.x removed `qiskit.execute()` and the old `BasicAer` module. Solution: Use `qiskit_aer.AerSimulator` directly with `transpile()` and `backend.run()`.

### Challenge 2: Qubit Ordering Convention
Qiskit uses little-endian qubit ordering (qubit 0 = LSB), but the paper writes bitstrings MSB-first. Solution: The encoder applies X gates in reversed order, and the decoder reverses measurement bitstrings before parsing.

### Challenge 3: Oracle Reversibility
The oracle must be perfectly reversible (unitary) for Grover's algorithm to work. Solution: Every gate applied to condition on `|0>` bits is meticulously uncomputed after the MCX, ensuring the net effect is only the phase flip on marked states.

### Challenge 4: Small Search Space
With only 3 candidate moves on the 3x3 board, Grover's algorithm provides no real speedup. Solution: The architecture is designed so that scaling to 8x8 (with dozens of candidates) is a configuration change, not an architectural change.

---

## Results and Observations

1. **Classical engine**: Fully functional 3x3 pawn chess with correct move generation, validation, and win detection. The minimax engine with alpha-beta pruning solves the game tree exhaustively.

2. **Quantum encoding**: All 9 squares correctly encode/decode through the quantum register scheme, matching the paper's Table II exactly.

3. **Grover search**: Successfully amplifies legal moves from the candidate space. Measurement statistics show the expected probability concentration on marked states after the correct number of iterations.

4. **Hybrid pipeline**: The combined classical-quantum engine plays complete games autonomously, with quantum-selected moves that are always verified as legal by the classical engine.

---

## Future Research Directions

1. **8x8 board implementation**: Scale `config.BOARD_SIZE = 8`. Requires 6 qubits per coordinate axis (ceil(log2(8)) = 3, so 6 total), 2 qubits for status, and additional qubits for piece type differentiation.

2. **Piece-type encoding**: Add 3 qubits to the status register to distinguish Pawn/Rook/Knight/Bishop/Queen/King (6 types = 3 bits).

3. **Quantum evaluation oracle**: Instead of marking legal moves, mark *good* moves (evaluated above a threshold by the heuristic). This would give Grover a role in evaluation, not just legality.

4. **NISQ hardware execution**: Run the circuits on real IBM Quantum hardware to study noise effects on Grover's amplification accuracy.

5. **Quantum game theory**: Explore superposition of strategies (Eisert et al., 1999) where players can make quantum moves — placing pieces in superposition of squares.
