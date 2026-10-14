# 2×2 Pure-Quantum Demonstration, Grover Search, and the 3×3 Handoff

This is the detailed circuit and architecture note for the small-board demonstrations. It explains what the current code builds, what each register/gate is intended to do, how Grover is used in the hybrid search path, and where the two quantum paths meet in software. This is an implementation explanation, not a claim that the prototype is a complete quantum chess engine.

## 1. The main distinction: two circuits with different jobs

The project has two different quantum-circuit ideas:

| Path | Quantum input | Quantum operation | Meaning of measurement |
|---|---|---|---|
| Small-board pure-circuit prototype (`pure_quantum_engine/`) | A classically known `GameState` and a supplied source-to-target `Move` | Encodes coordinates, obtains square-status bits from a classical lookup encoded as gates, and runs limited direction/status logic | Diagnostic bit string for the constructed circuit; it does not update a chess board |
| Hybrid Grover search (`quantum/`, used by `ai/`) | Integer indices of classically ranked candidate moves | Creates a uniform index superposition, phase-marks heuristic-best indices, and applies the diffuser | Sampled move index, decoded by classical software into the existing `Move` object |

The small-board coordinate qubits do **not** feed into Grover's index qubits. The classical program can pass a selected `Move` from one component to another, but no circuit composition currently wires the measured pure-circuit bits into the Grover search. Grover's candidate list and target indices are constructed by Python before the index circuit runs.

There is also a route distinction in the menu. The normal 3×3 game (menu option 2) uses classical depth-3 minimax to choose the AI move, and the pure circuit processes the chosen move for diagnostics. The 3×3 hybrid evaluation branch uses classical candidate scoring plus Grover. These are separate implementations. The 8×8 GUI hybrid engine also uses the Grover search path.

## 2. Small-board pure circuit: data path and register sizes

`PureQuantumCircuitBuilder.build_full_chess_circuit(state, source, target, color)` receives the classical board and the already selected move. For 2×2 and 3×3, the allocation is:

| Register | Width | Purpose |
|---|---:|---|
| `cur` | 4 | Source square coordinate |
| `tgt` | 4 | Destination square coordinate |
| `dir` | 4 | Direction/result workspace |
| `src` | 3 | Compact encoding for source-square status |
| `dst` | 3 | Compact encoding for destination-square status |
| `anc` | 5 | Temporary workspace for comparisons and controlled operations |
| **Total** | **23 qubits** | All are measured into a 23-bit classical register |

For board widths that need more than two bits per axis, the coordinate width can grow; the 8×8 circuit uses 6 bits per coordinate register and 6 status bits per square, for 33 qubits with this allocation. The prototype small-board status code is compact, while larger boards use a sparse six-bit code.

### Coordinate convention

The encoder stores the column (x) bits first, then the row (y) bits. For the 3×3 board, each axis is two bits:

- `(row=0, col=0)` → `00 00` → `0000`
- `(row=2, col=1)` → `01 10` → `0110`
- `(row=0, col=2)` → `10 00` → `1000`

The same four-bit coordinate allocation is used on the 2×2 board, leaving some coordinate patterns unused. The register initialization helper applies an X gate for every encoded `1`; the all-zero coordinate begins in `|0000⟩` without X gates. Qiskit displays bit strings using its classical-bit ordering conventions, so distinguish the encoder's logical bit string from the left-to-right order printed by a full measured circuit.

### Compact square-status code

`BoardEncoder.encode_status` returns a three-character logical code: one color bit followed by two piece-type bits. In the current compact map:

- Empty square → `000`
- Black pawn → `001`
- White pawn → `101`
- Black knight → `010`
- White knight → `110`

This is not a unique encoding for all chess pieces: pawn/rook, knight/queen, and bishop/king share type codes. The mapping is therefore useful only as a compact prototype encoding; it cannot identify every piece type unambiguously. The module header still describes an older two-bit status convention, so the actual three-bit implementation above is the source of truth.

## 3. What the pure-circuit gates do

### `X` gate: bit flip / pattern preparation

`X|0⟩ = |1⟩` and `X|1⟩ = |0⟩`. The builder uses X gates to initialize coordinate ones. It also uses X gates around controlled gates to turn a control-on-zero condition into a control-on-one condition. For example, to match coordinate `0100`, it temporarily flips the coordinate qubits whose expected bits are zero, performs the multi-controlled operation, then flips those qubits back.

### `CX` gate: controlled bit flip

`CX` flips its target only if its one control is `1`. It is used in the direction logic and to copy/toggle intermediate results. The target can be in superposition in a genuinely coherent computation; this builder starts coordinates in basis states, so these particular values are mostly classical bit patterns represented by qubits.

### `CCX` gate: Toffoli / two-control `X`

`CCX(a,b,t)` flips target `t` only when both controls are `1`. Here it contributes to limited diagonal-direction pattern detection. Like the other controlled gates, it is reversible: the input information is not simply erased.

### `MCX` gate: multi-controlled `X`

`MCX` flips its target only when every control is `1`. The status extractor uses it as a coordinate-controlled lookup: for each square with a nonzero status code, it prepares the coordinate controls for that square and toggles the appropriate status output bits. The direction/status stages also use MCX with ancilla controls.

### Measurement

The builder measures every qubit into classical memory. A measurement samples a basis value and collapses the simulated state. The printed string records the measured circuit registers; it is not a serialized chess board and is not passed back to `GameState` as a new position. The game applies the supplied classical `Move` after the diagnostic run.

## 4. How the pure-circuit builder is assembled

The implementation in `pure_quantum_engine/circuit.py` follows these stages:

1. **Allocate registers.** `PureQuantumRegisters` creates the coordinate, direction, status, ancilla, and measurement registers.
2. **Encode the given move.** `BoardEncoder.encode_position` converts source and target coordinates to bit strings. X gates prepare each coordinate register.
3. **Extract square status.** The builder loops over every square in the Python board. For each occupied square, it appends coordinate-controlled MCX gates that write its compact status into the source or destination status register. This is a gate-level lookup generated from classical board data, not a quantum scan over a superposition of all board locations.
4. **Compute a direction pattern.** CX, X, and CCX gates compare coordinate components and attempt to set direction/ancilla bits.
5. **Apply a status transformation pattern.** The circuit temporarily complements destination status bits and applies controlled toggles using direction and status controls.
6. **Measure.** All register qubits are measured. `PureQuantumGame.make_move` runs a single-shot Aer simulation, reports the circuit metrics/output, and then calls the classical parent `Game.make_move` with the original `Move`.

### Prototype limits to state clearly

The direction logic in `_add_direction_detection` is a limited pattern implementation, not a complete reversible subtractor/comparator for every displacement. The source comments themselves note that full knight scaling needs more logic. The status operator is an experimental transformation pattern; it does not implement a complete, validated chess transition in quantum memory. Compact status codes also conflate piece types. So the academically accurate claim is that this is a small-board **circuit construction and measurement prototype**, while classical rules decide and apply the move.

## 5. Grover circuit: a separate search over move indices

The Grover path operates on indices, not on the coordinate/status registers above. In `QuantumMoveSearcher.search`:

1. Python calls `MoveGenerator.generate_legal_moves(state)` and creates an ordered list of legal `Move` objects.
2. Python calls `HeuristicEvaluator.score_move` on each candidate and collects every index whose score equals the maximum.
3. The candidate count determines the index width: `n = ceil(log₂(candidate_count))` (with at least one qubit). The full circuit search space is `2ⁿ`, which may include unused padded indices if the candidate count is not a power of two.
4. `GroverSearch` receives the candidates and target indices. If every candidate is marked, it takes a shortcut and returns the first target without constructing a circuit.
5. Otherwise, it prepares the index superposition, marks the target indices with its oracle, applies a diffuser for the configured number of Grover iterations, and measures the index register using the simulator.
6. Python converts the measured binary index back to the candidate `Move`, checks that it is in range and marked, and falls back to the first target move if sampling gives an unusable index.
7. The game applies the returned `Move` through the classical engine.

### Grover-specific gates

- **Hadamard (`H`) on each index qubit:** `H|0⟩=(|0⟩+|1⟩)/√2`. Applying H to all `n` index qubits prepares an equal superposition of all `2ⁿ` binary indices.
- **Flag preparation (`X` then `H`):** starting from `|0⟩`, X produces `|1⟩`; H then produces `|−⟩=(|0⟩−|1⟩)/√2`.
- **Oracle (`X` controls + MCX):** for each marked integer index, X gates invert the zero-valued index bits so the MCX matches the entire pattern. The MCX flips the flag. Since the flag is `|−⟩`, that flip leaves the flag's observable state the same but multiplies the corresponding index amplitude by `−1` (phase kickback). The temporary X gates are undone.
- **Diffuser:** the implementation applies H to all index qubits, X to all, a multi-controlled Z pattern (made from H–MCX–H on the final qubit when there are at least two index qubits), then X and H again. This is the reflection about the uniform-superposition state, often described as inversion about the mean.
- **Measurement:** the index register collapses to one integer. Classical code uses that integer as an array position in the `candidates` list.

The oracle does **not** calculate piece rules in superposition in this implementation. It receives target indices already chosen by classical move generation and scoring, then marks those exact indices reversibly.

## 6. Worked 3×3 example: from piece data to a sampled best move

This example uses the default 3×3 layout in `config.py`: White Knight at `(2,1)`, Black Pawn at `(0,0)`, White to move. The coordinate and status bit strings below are the logical encoder values.

### A. Classical piece and move preparation

The White Knight at `(2,1)` encodes as `0110`; the Black Pawn at `(0,0)` encodes as `0000`. Their compact status codes are Knight `110` and Pawn `001`, respectively. These board objects and encodings are still classical Python data at this point.

The classical `MoveGenerator` returns the following legal candidates in order; the actual scores below come from the project's `HeuristicEvaluator`:

| Index | Candidate | Score | Reason in brief |
|---:|---|---:|---|
| 0 | `(2,1) → (0,0)` capture | 13.3 | Capture bonus plus center-position terms |
| 1 | `(2,1) → (0,2)` | 4.4 | Knight and general center-position terms |

So classical code sets `candidate_count=2`, `n=ceil(log₂2)=1`, and `optimal_indices=[0]`. The heuristic determines which index is marked; Grover does not calculate these scores.

### B. Grover amplitude manipulation (illustrative ideal state)

For this example the index register has one qubit, so the search basis is `|0⟩, |1⟩`. After H, the index state is:

`(|0⟩ + |1⟩) / √2`

Index 0 is the only best-scoring target. With the flag in `|−⟩`, the oracle's MCX causes phase kickback, giving:

`(−|0⟩ + |1⟩) / √2`

One Grover iteration is selected by the code's iteration formula for `N=2`, `M=1`. The diffuser reflects the amplitudes about their mean and produces `−|0⟩` (global phase is physically unobservable). An ideal noiseless measurement therefore returns index 0 with probability 1. The simulator can differ because of circuit transpilation, sampling, or backend/noise choices; regardless, the code validates the result and has a classical target fallback.

The measured index `0` decodes through `candidates[0]` to `(2,1) → (0,0)`, the Knight capture. This is the best move **under the current one-ply heuristic ranking of this candidate list**, not a proof of globally optimal play. Minimax or deeper lookahead is a different classical algorithm.

### C. Passing that move to the small-board circuit

If the selected move is passed to `PureQuantumCircuitBuilder`, the source register is initialized with Knight coordinate `0110` and the target register with Pawn coordinate `0000`. The builder also generates status-lookup controls for the board. With the 23-qubit small-board allocation:

`cur(4) + tgt(4) + dir(4) + src(3) + dst(3) + anc(5) = 23`

The circuit then runs its limited direction/status gate sequence and reports a measured 23-bit diagnostic. The classical game layer validates/applies the original Knight capture to the board. No measured coordinate/status bit is interpreted as the selected candidate index; the move selection already happened through the separate Grover index path.

For the default 3×3 capture move, a direct build of the current source reports 23 qubits and 23 classical readout bits, logical depth 29, and operations `{x: 40, mcx: 12, cx: 11, ccx: 3, measure: 23}`. These are pre-transpilation circuit-construction counts for this exact board/move; different occupancy and moves can change the count.

## 7. 2×2 Black Pawn example and menu routes

For the 2×2 demonstration, the configured Black Pawn starts at `(0,0)` and its forward destination is `(1,0)`. Their coordinate values are `0000` and `0001`. The pawn status is `001`; the empty destination status is `000`. In interactive option 6, a user chooses a legal move, the pure circuit is built and simulated for one shot, and the parent classical `Game` applies the supplied move.

Option 7 is titled “2×2 Grover Search,” but the current default call does not construct a Grover circuit: its candidate helper returns only legal moves, making every candidate a target; `GroverSearch.search` detects that all-candidates-marked case and returns the first candidate before building the circuit. The later pure-circuit simulation does run. Option 7 also does not apply the move to a persistent game board. Do not describe that menu route as an executed Grover amplitude-amplification demo.

## 8. What is classical, what is quantum, and why

| Concern | Current implementation | Why it is classical or quantum here |
|---|---|---|
| Board storage / pieces / turns | Classical `Board` and `GameState` | The application and UI need an explicit, inspectable chess position |
| Legal move generation | Classical `MoveGenerator` | Current rules enumerate legal `Move` objects before either circuit is built |
| Candidate scoring | Classical `HeuristicEvaluator` | It computes the target score and target index set before Grover runs |
| Move-index amplitude amplification | Quantum-style circuit in Qiskit/Aer | H, oracle phase marking, diffuser, and measurement sample among prepared indices |
| Coordinate/status gate experiment | Quantum-style circuit in Qiskit/Aer | Encoded source/target values and limited reversible operations are represented as qubits/gates |
| Result decoding, validation, fallback | Classical Python | A measured integer must be mapped to a `Move`, checked, and safely returned |
| Final board transition | Classical `Game.make_move` / `GameState` | The small-circuit measurement is diagnostic and does not constitute a board-state update |

The hybrid design uses classical code for data structures, rules, and evaluation, and uses a quantum simulator to demonstrate amplitude amplification on an index set. The current project does not establish a quantum speedup or a fully quantum chess implementation.

## 9. Architecture flowchart

The single connected diagram below traces classical piece information through candidate indexing, Grover amplitude manipulation, Move decoding, and the separate pure-circuit processing path. Its red handoff box is important: it marks a software-level connection between two circuit paths, not a circuit-to-circuit quantum connection.

![3×3 classical move ranking, Grover index search, and separate pure-circuit move path](flowcharts/generated/05_3x3_piece_to_best_move.png)

Regenerate it (and the other Python-generated flowcharts) with:

```bash
python docs/flowcharts/generate_flowcharts.py
```

### Interactive 2×2 Black Pawn circuit flow

This companion chart follows menu option 6 only: the configured Black Pawn, its manually supplied legal move, 23-qubit coordinate/status circuit, diagnostic measurement, and classical `GameState` update. Grover is not part of that interactive route.

![2×2 Black Pawn pure-circuit flowchart](flowcharts/generated/06_2x2_black_pawn_pure_quantum.png)

## 10. Relevant implementation files

- `config.py` — board size, 2×2/3×3 piece layouts, and simulator settings.
- `engine/board.py`, `engine/state.py`, `engine/move.py` — classical board, state, and move values.
- `engine/move_generator.py` — classical legal candidate generation.
- `ai/heuristic.py` — current per-move ranking used to prepare target indices.
- `ai/quantum_search.py` — classical best-index preparation and Grover invocation.
- `ai/hybrid_engine.py` — hybrid selector and classical minimax fallback.
- `quantum/encoder.py` — coordinate/status encodings and initialization helpers.
- `quantum/oracle.py` — reversible index-pattern marking and phase kickback.
- `quantum/diffuser.py` — inversion-about-the-mean operator.
- `quantum/grover.py` — index register, oracle/diffuser iterations, measurement, and Move decoding.
- `pure_quantum_engine/registers.py` — 23-qubit 2×2/3×3 allocation (and larger-board sizing).
- `pure_quantum_engine/circuit.py` — coordinate/status/direction circuit construction.
- `main.py` — menu routes and pure-circuit demo wrappers.
