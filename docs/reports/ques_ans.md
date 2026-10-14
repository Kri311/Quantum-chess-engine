# Faculty Q&A: Quantum Chess Engine

This question bank is based on the current source implementation. The answers intentionally distinguish implemented behavior from design goals and future work.

## Project purpose and architecture

### 1. What is the goal of this project?

It is an educational hybrid chess engine that connects classical chess logic with Qiskit circuit simulation. The 8×8 mode uses classical legal-move generation and heuristic scoring, then applies Grover-style amplitude amplification to indices of the best moves. The 2×2 and 3×3 modes provide small circuit demonstrations for coordinate/status encoding and reversible gate patterns.

### 2. Why use a hybrid architecture?

The classical engine already has a direct representation of pieces, board occupancy, and legal moves. The hybrid design can reuse that reliable structure and reserve quantum simulation for a clearly bounded search component. It also avoids simulating a 33-qubit board circuit for routine 8×8 move selection, which would require a statevector with `2^33` complex amplitudes.

### 3. What are the main architectural layers?

`engine/` models the board and rules; `ai/` generates candidate moves, scores them, and chooses one; `quantum/` builds and simulates the Grover index-search circuit; `pure_quantum_engine/` builds the small-board coordinate/status demonstration; `ui/` provides interaction and rendering; `config.py` centralizes settings; and `main.py` connects the modes.

### 4. Is the 8×8 board represented entirely by qubits?

No. In normal 8×8 hybrid play the board is a classical `GameState`. The quantum circuit represents an integer index into a classical legal-move list. A separate pure-circuit register allocator would use 33 qubits on 8×8, but the current gameplay selector does not use that full board circuit.

### 5. What does “pure quantum” mean in this project?

It labels the small-board gate-level demonstration that encodes source and target coordinates and statuses into quantum registers and applies a circuit. It does not mean the entire running chess game or board state is quantum. The game wrappers update their authoritative board through the classical `Game.make_move` method after running the circuit.

### 6. What is the role of the 2×2 board?

It minimizes the number of meaningful squares and pieces, making it easier to trace how a black pawn’s coordinate and status are initialized and how gates are wired. It is an explanatory circuit scenario, not a demonstration of complete chess or of a general move-selection advantage.

### 7. Why retain the 3×3 prototype?

It follows the small-board research-inspired setup and shows that coordinate/status circuits can be generated for a board with more than one movement option and more than one piece. The current configured pieces are a White Knight at `(2,1)` and a Black Pawn at `(0,0)`.

### 8. Which standard chess features are implemented?

The classical move generator has pawn, knight, sliding-piece, and king move generation and filters moves based on king safety. Before claiming complete FIDE-standard chess, inspect and verify special rules such as castling, en passant, promotion, repetition, and check/stalemate handling. The quantum circuits do not implement all those rules.

## Quantum representation and gates

### 9. How many qubits encode a square on a 3×3 board?

Four: two bits for the column and two for the row. Two bits are needed per axis because `ceil(log2(3)) = 2`. The four-bit encoding can represent 16 coordinates, though only nine are valid board squares.

### 10. How many coordinate qubits does an 8×8 source/destination pair need?

Each axis needs `ceil(log2(8)) = 3` bits, so a square uses six coordinate bits and a source/target pair uses twelve.

### 11. What is the 2×2 coordinate for `(row=1, col=0)`?

The encoder concatenates two-bit column then two-bit row: column `00`, row `01`, resulting in `0001`.

### 12. How does the compact status encoding work?

On small boards, status is three bits. The first bit represents color (`0` black, `1` white), and the final two bits represent a compact type code. Empty is `000`, and a Black Pawn is `001`. Some types share compact codes, so it is not a unique six-piece encoding.

### 13. How does the sparse status encoding work?

For board sizes of at least five, the pure register allocator uses six bits: one color bit plus a five-bit sparse piece field. The mapping in `BoardEncoder.encode_status` assigns one field bit for pawn, knight, bishop, rook, or queen; the king maps to all zero in that field. Since empty also maps to all zero, the full six-bit code cannot distinguish an empty square from a black king by itself. This is a limitation to correct before relying on the encoding as a complete representation.

### 14. What is a qubit?

A qubit has state `α|0⟩ + β|1⟩`, where `α` and `β` are complex amplitudes and `|α|²+|β|²=1`. Measurement returns 0 or 1 with the corresponding squared-amplitude probability.

### 15. What does the X gate do?

It swaps computational basis states: `X|0⟩=|1⟩` and `X|1⟩=|0⟩`. Here it initializes 1-bits, temporarily inverts zero-valued controls for equality checks, and participates in flag and diffuser preparation.

### 16. What does the Hadamard gate do?

It maps `|0⟩` to `( |0⟩+|1⟩ )/√2` and `|1⟩` to `( |0⟩−|1⟩ )/√2`. Applying H to all move-index bits creates a uniform superposition over all binary indices. H on the flag after X prepares `|−⟩` for phase kickback.

### 17. What are CX and CCX gates used for?

CX conditionally flips one target based on one control; CCX (Toffoli) uses two controls. They are reversible Boolean building blocks. The circuit uses them in direction logic and in constructions that compare coordinates or control status changes.

### 18. What does MCX do in the move oracle?

The oracle temporarily applies X gates to index bits that should be zero, so a selected target index is represented by all-one controls. An MCX then flips the flag exactly for that basis state. The temporary X gates are undone to restore the index register.

### 19. What is phase kickback?

The flag is prepared in `|−⟩`. Since `X|−⟩=−|−⟩`, an MCX that flips the flag for a matching index changes the sign of that index’s amplitude. The flag returns to the same state, while the move-index state receives the phase mark.

### 20. Why does the oracle phase flip not immediately change measurement probability?

Probability is the squared magnitude of amplitude, and `|−a|²=|a|²`. The diffuser uses interference to turn relative phase differences into changed amplitudes, making the marked indices more likely to be measured.

### 21. What does the diffuser do?

It implements the reflection `D=2|s⟩⟨s|−I`, called inversion about the mean. In this code it is built from H gates, X gates, a multi-controlled Z constructed with H–MCX–H, then X and H gates again.

### 22. What does measurement do?

It samples classical bits from the quantum state according to measurement probabilities and collapses the measured qubits. In Grover search those bits are converted into a candidate index. In the pure circuit the registers are all measured for diagnostics; the measurement does not itself rewrite the classical chess board.

## Grover and move selection

### 23. What exactly is the search space in 8×8 mode?

It is the legal move list already produced by the classical `MoveGenerator`, with the index register padded to the next power of two. It is not the set of all possible board states or all moves in the game tree.

### 24. What does the quantum oracle mark in the hybrid mode?

`QuantumMoveSearcher` computes a heuristic score for each legal move classically, finds the maximum, and passes the indices tied at that maximum to Grover. Thus the Grover oracle marks heuristic-best move indices. It is not doing the legal-move validation in this call path.

### 25. What is the Grover iteration formula?

For a search space of size `N` with `M` marked items, the approximate count is `floor((π/4)√(N/M))`, with implementation-specific edge handling. The code uses at least one iteration when not all candidates are targets and computes `N` from the padded power-of-two index width.

### 26. Why are there padded indices?

An `n`-qubit register has `2^n` values. If the number of legal moves is not a power of two, some encoded values exceed the list length. Those values have no corresponding move and are not marked. The code checks the measured result and falls back to a marked candidate if it is padding or otherwise not a target.

### 27. What does measurement probability mean in the console output?

The printed percentage is the fraction of simulator shots that produced the most frequent measured bitstring. It is an empirical frequency for the most likely outcome; it is not an “amplitude percentage.” Amplitudes are complex numbers, while probabilities are squared magnitudes.

### 28. Does the implementation prove a quadratic speedup for chess?

No. Grover’s ideal query complexity is quadratic in an unstructured search size when the oracle is available at an appropriate cost. Here, legal moves and heuristic-best indices are precomputed classically, and the oracle is built from that list. The project demonstrates the Grover circuit mechanics, not an end-to-end chess speedup.

### 29. What happens if Grover returns a non-target index?

The searcher returns the first marked target index as a fallback. The hybrid engine can also fall back to minimax if the quantum search returns no move. A single legal move is returned without constructing a Grover circuit.

### 30. Is minimax combined with Grover in every move?

No. If `use_quantum=True`, the hybrid engine first tries the quantum move search and returns that move when available. Minimax is a fallback path. The `HybridEngine` creates minimax with depth 3; `MinimaxEngine` itself defaults to depth 6 when separately instantiated.

## Pure circuit and limitations

### 31. What does the status extractor do?

At circuit-construction time, Python loops over occupied classical squares, compares each known coordinate to the coordinate register using X-normalized controls, and uses MCX gates to toggle the corresponding status-output bits. It is a gate-encoded lookup based on the classical board supplied to the builder.

### 32. Is the direction circuit a complete subtractor?

No. The current `_add_direction_detection` contains partial CX/X/CCX patterns and is not a general reversible coordinate subtractor/comparator. The source explicitly notes that a full subtractor/absolute-value circuit is required for knight displacement detection on 8×8. Present it as a prototype subcircuit, not complete movement verification.

### 33. Does the pure circuit update every square on the board?

No. The circuit has source and target coordinate and status registers plus direction and ancilla registers; it does not allocate a quantum status register for every board square. The classical game applies the move to its board state.

### 34. What does the status operator currently represent?

It is an attempt to conditionally transform destination status using direction, source status, destination status, and ancilla controls. It is not a complete encoding of a chess transition, and it does not perform all required state updates such as source clearing and special-move rules.

### 35. Is reversible computation important here?

Yes. Quantum gates must be unitary and therefore reversible. A predicate can be computed into ancilla/work bits, used to control an operation, and then uncomputed to clean workspace without erasing information. Classical overwrite operations cannot be inserted directly as quantum gates.

### 36. Why are some status outputs toggled instead of assigned?

MCX and CNOT are XOR-like reversible operations: they toggle a target under a control condition. The output must be initialized correctly and the predicate must be mutually exclusive or uncomputed as designed. The circuit builder must account for this behavior to avoid accidental cancellation or residual entanglement.

## Simulation, configuration, and validation

### 37. Which simulator is used?

`QuantumSimulator` wraps Qiskit Aer. It tries a statevector backend with GPU support and falls back to Aer without GPU when unavailable or when GPU execution raises a runtime error. The demo code in `main.py` sometimes instantiates Aer directly.

### 38. What does `QUANTUM_SHOTS=1024` mean?

It configures the number of repeated circuit executions for sampling when the `QuantumSimulator` wrapper is used. More shots reduce sampling uncertainty but increase runtime. Some pure-circuit wrappers use one shot or invoke Aer directly with the configured count.

### 39. What does the noise configuration do?

When enabled, `QuantumSimulator` builds a simple depolarizing noise model with configured single-qubit probability `p` and two-qubit probability `10p` for selected gates. This is an illustrative model. Because the circuit is transpiled and some operations are decomposed, the actual error coverage depends on the final basis operations. It is not calibrated hardware noise.

### 40. Why can a 33-qubit statevector be difficult to simulate?

A full statevector has `2^33` complex amplitudes. At 16 bytes per complex double, amplitudes alone require about 128 GiB of memory, before simulator and operating-system overhead. The hybrid index circuit is much smaller because it uses `ceil(log2(number_of_moves))` qubits plus a flag.

### 41. How should the project be validated?

For the quantum portions, compare small circuits against hand-computed basis-state behavior, check oracle phase marks, measure the Grover success rate against the amplitude-amplification formula across shots, verify index/endianness mappings, and test padding cases. For chess, validate move legality and game outcomes against a trusted rules implementation, especially for special moves and king safety. Report simulator and hardware results separately.

### 42. What are the important current limitations to disclose?

The hybrid oracle’s targets are prepared classically; the pure circuit has incomplete direction/status-transition logic; the board state is not wholly quantum; the sparse encoding conflates a black king and empty status; the noise model is simplified; and full standard chess-rule coverage needs verification. These are useful boundaries for a research prototype and also define concrete next steps.

## Challenging oral-exam prompts

### 43. If legality was already determined classically, what is Grover adding?

In the present call path, it adds a demonstration of amplitude amplification over the indices selected as heuristic-best. It does not reduce the classical work already used to generate legal moves and scores. A future quantum-search claim would need a coherent oracle that evaluates the desired predicate on superposed candidates and a careful accounting of oracle cost.

### 44. What would a correct quantum board transition require?

First define an injective board encoding, including empty, every piece type, and color. Then encode source/target coordinates and the board state, compute legality and transition conditions reversibly, apply a controlled update that clears the source and sets/captures the destination, handle special moves, and uncompute all work registers. Finally verify reversibility and compare measured/reconstructed results against classical reference transitions.

### 45. What is the difference between superposition and “checking every move at once”?

Superposition represents amplitudes for many basis states, but it does not expose all answers at measurement. A useful algorithm must use interference—through an oracle and operations such as diffusion—to increase the probability of desired outcomes. The cost of preparing and evaluating the oracle remains part of the algorithm.

### 46. Why can’t we just measure the whole superposition to get every candidate?

Measurement returns one sampled basis state per shot and collapses the measured state. Repeating shots provides samples, not a free readout of all amplitudes or all candidate answers.

### 47. What would count as evidence of a useful quantum advantage?

A well-defined task and oracle cost, a fair classical baseline, a scaling study over increasing candidate sizes, total runtime including candidate and oracle construction, noise-aware success probabilities, and preferably execution on hardware or a defensible simulator model. A Grover circuit alone does not establish practical advantage.

### 48. What is the next most valuable implementation improvement?

Make the problem statement and oracle boundary explicit, then fix the pure circuit’s representation and transition correctness. For the hybrid path, separate “legality search” from “heuristic-best search,” benchmark end-to-end costs, and verify Grover probability behavior over controlled synthetic cases.

## Repository organization after cleanup

This question bank is stored beside the architecture report in `docs/reports/`. Implementation code remains in `engine/`, `ai/`, `quantum/`, `pure_quantum_engine/`, and `ui/`. Circuit diagrams, text dumps, evaluation output, and inspection utilities now have dedicated locations under `docs/assets/diagrams/`, `docs/circuits/`, `evaluation/`, and `tools/`. The byte-identical 2×2 diagram duplicates were consolidated into one canonical image. Utility output paths and documentation references were updated; chess rules and quantum algorithms were left unchanged. Disposable Python/Pytest caches were removed, while the ignored environment and hidden workspace metadata were preserved. See [`folder_dir.md`](folder_dir.md) for the file-by-file map.
