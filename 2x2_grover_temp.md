# How the 2×2 Demonstration Works: A Gate-by-Gate Walkthrough

This note follows the default 2×2 example in the repository from its initial board to the end of menu option 7. It explains which values are classical, which qubits and gates are created, how those gates act on the example state, and what the final measurement means.

> **Important accuracy note:** The menu calls option 7 “2×2 Grover Search,” but the default board has exactly one legal move. The current `GroverSearch.search` returns that move before constructing a Grover circuit. The following 23-qubit circuit is then built and measured, but it does not determine or apply a new board state. The circuit's direction logic also fails to recognize this forward move. This is a useful circuit-construction example, not a completed quantum chess move engine.

## 1. The example and its route through the program

The board is 2 rows by 2 columns. Positions are written `(row, col)`, with row increasing downward:

```text
             col 0       col 1
row 0        (0,0)       (0,1)
row 1        (1,0)       (1,1)
```

The default configuration contains one piece:

| Square | Classical contents |
|---|---|
| `(0,0)` | Black Pawn |
| `(0,1)` | Empty |
| `(1,0)` | Empty |
| `(1,1)` | Empty |

The intended demonstration move is the Black Pawn stepping forward from `(0,0)` to `(1,0)`. The move generator and board are ordinary Python objects. The quantum circuit receives the already known source, target, and board; it is not given a quantum superposition of complete chess positions.

Menu option 7 in `main.py` performs these operations:

1. Set the configured board size to 2 and construct the classical board and `GameState`.
2. Call `GroverSearch.search(state)`.
3. Pass the returned `Move` to `PureQuantumCircuitBuilder.build_full_chess_circuit`.
4. Simulate that 23-qubit circuit for one shot and print the measured bit string.
5. Save a circuit diagram and print a completion message.

Option 7 does **not** call the game's `make_move` method or keep a post-move board. The interactive option 6 is a different route: a user selects a legal move, the diagnostic circuit is run, and then the classical game applies the supplied move.

## 2. First, the classical move list

The Black Pawn is at row 0. In this project, Black advances toward increasing row numbers. The next square `(1,0)` is on the board and empty, so the move generator returns:

```text
candidates = [ Move((0,0) -> (1,0)) ]
candidate count = 1
```

There is no second legal destination: moving diagonally would require an enemy piece to capture, but both diagonal destinations are empty. The two-square opening step is outside this 2-row board.

`GroverSearch.search` asks `MoveOracle` for candidates and legal candidate indices. Here there is one candidate and its index is 0, so every candidate is marked. The search method contains an early-return case for that situation:

```python
if len(target_indices) == n_candidates:
    return candidates[target_indices[0]]
```

Therefore, the current default run builds **no Grover circuit**. It applies no Grover Hadamard gates, no phase oracle, no diffuser, and no measurement of a move-index register. The method simply returns the one `Move` already produced by the classical move generator.

This is a key distinction: the following 23-qubit circuit is not the Grover search. It is a separate coordinate/status circuit built after the move has been supplied.

## 3. The 23-qubit circuit registers

For board size 2, `PureQuantumRegisters` allocates four coordinate qubits per square coordinate. Two bits per axis are enough to represent 0 or 1; the implementation keeps a minimum of four coordinate qubits even on this small board. It then allocates direction, source status, destination status, and scratch registers:

| Register | Qubits | Intended role in the prototype |
|---|---:|---|
| `cur[0..3]` | 4 | Current/source coordinate |
| `tgt[0..3]` | 4 | Target coordinate |
| `dir[0..3]` | 4 | Direction-result workspace |
| `src[0..2]` | 3 | Compact source-square status |
| `dst[0..2]` | 3 | Compact target-square status |
| `anc[0..4]` | 5 | Temporary work qubits |
| **Total** | **23** | Each qubit is measured into a classical bit |

The code uses 23 qubits and a 23-bit classical readout register. Register names describe the design intent; they do not guarantee that every intended predicate is correctly computed.

### 3.1 Coordinate bit order

`BoardEncoder.encode_position` forms a logical string from the column bits followed by the row bits. With two bits allocated per axis:

| Position `(row, col)` | Column bits + row bits | Logical coordinate string |
|---|---|---|
| `(0,0)` | `00` + `00` | `0000` |
| `(0,1)` | `01` + `00` | `0100` |
| `(1,0)` | `00` + `01` | `0001` |
| `(1,1)` | `01` + `01` | `0101` |

Qiskit numbers a register's qubits from least significant (`q[0]`) upward. The initializer walks the logical string in reverse when deciding which qubit index to flip. Thus `0001` is prepared by applying X to `tgt[0]`; a logical `0100` would instead flip `tgt[2]`.

### 3.2 Piece-status bit order

For the compact three-bit status code, a Black Pawn is `001` and an empty square is `000`. Like the coordinate initializer, the status extractor maps the rightmost logical character to output qubit 0. Therefore the Black Pawn sets `src[0]` to 1; `src[1]` and `src[2]` remain 0. The target's three status qubits remain 0 because `(1,0)` is empty.

These compact codes are not unique for every chess piece. They are an educational encoding for a small prototype, not a full chess-piece data format.

## 4. Building the circuit, one stage at a time

All 23 qubits start in `|0⟩`. The circuit builder then appends gates in this order: coordinate initialization, source and destination status lookup, direction logic, status-operator logic, and measurement.

### Stage A: prepare the source coordinate

The source `(0,0)` encodes as `0000`. It contains no 1-bits, so the initializer applies no X gates to `cur`. Its state stays:

```text
cur = |0000⟩
```

### Stage B: prepare the target coordinate

The target `(1,0)` encodes as `0001`. The initializer applies `X(tgt[0])`:

```text
tgt[0]: |0⟩ --X--> |1⟩
tgt[1], tgt[2], tgt[3]: remain |0⟩
tgt = |0001⟩    (logical string)
```

The X gate is the NOT operation: `X|0⟩=|1⟩` and `X|1⟩=|0⟩`. It prepares a basis value here; it does not create a superposition.

At this point the coordinate portion is the product state `|0000⟩cur |0001⟩tgt`. There is no quantum uncertainty over which move was chosen: the move has already been selected as classical data.

### Stage C: extract the source-square status

`_add_status_extractor` loops over all four board squares using the classical Python board. It skips empty squares. The only occupied square is `(0,0)`, with coordinate `0000` and status `001`.

The lookup must activate only when the coordinate register matches `0000`. The MCX gate is controlled on 1s, so the builder converts each expected zero control into a one temporarily:

1. Apply X to all four `cur` qubits: `0000 → 1111`.
2. Apply the four-controlled X from the coordinate qubits to `src[0]`, because the last status bit of `001` is 1. Since all four controls are 1, `src[0]` flips: `0 → 1`.
3. Apply X to all four `cur` qubits again: `1111 → 0000`.

The two sets of X gates restore the coordinate register. This is called uncomputing the temporary control pattern. The status result remains:

```text
cur = |0000⟩
src = |001⟩    (logical string; src[0] is 1)
```

The lookup is encoded in gates, but its contents came from the classical board. The circuit did not search through a quantum-encoded board.

### Stage D: extract the target-square status

The destination lookup again considers the occupied source square `(0,0)` with coordinate `0000`. It temporarily applies X to all four target qubits, using the `tgt` register as the MCX controls. Since `tgt` is `0001`, this makes the temporary control pattern `1110`, not `1111`. At least one control is zero, so the four-controlled X does not fire. The X gates are undone and `tgt` returns to `0001`.

There are no other occupied squares. Consequently, the destination status stays:

```text
tgt = |0001⟩
dst = |000⟩    (empty square)
```

### Stage E: attempt to compute the move direction

The code divides each four-qubit coordinate register into two two-qubit slices:

```python
cur_x = cur[0:2]
cur_y = cur[2:4]
tgt_x = tgt[0:2]
tgt_y = tgt[2:4]
```

Because Qiskit's low-index qubits hold the rightmost logical bits, `cur[0:2]` and `tgt[0:2]` contain the **row** bits in this encoding; `cur[2:4]` and `tgt[2:4]` contain the **column** bits. The variable names `x` and `y` can therefore be confusing when read alongside the logical strings.

The first block attempts an equality check on the first slices. For each bit it applies CX from `cur_x[i]` to `tgt_x[i]`, then X to `tgt_x[i]`. Algebraically, the target bit becomes `NOT(cur_x[i] XOR tgt_x[i])`, which equals 1 when the input bits matched. The MCX into `anc[0]` fires only if both bits matched.

For this move, the first slices are the row values:

```text
cur_x (row 0) = 00
tgt_x (row 1) = 01
```

They do not match. In qubit-index order the row bits are `cur_x=[0,0]` and `tgt_x=[1,0]`; after the CX/X pattern the temporary target controls are `[0,1]`. The MCX therefore does not fire, and `anc[0]` stays 0. The following gates restore the target bits.

The code then copies `anc[0]` into `dir[0]` and `dir[1]` using CX gates. Since `anc[0]=0`, neither direction bit changes. The subsequent two CCX patterns attempt limited diagonal detection; with this input their controls are not both 1, so `anc[1]`, `anc[2]`, and the direction bits remain 0. No direction flag is set for the forward move.

This is a limitation of the current implementation: the first check is testing equality on the row slice, while a forward pawn move requires equal columns and a one-row displacement. The code does not implement the needed complete row-increment/equality predicate. The source code also explicitly leaves full knight displacement logic for future work.

### Stage F: run the status-operator pattern

The method named `_add_status_operator` is not a complete move or board-update circuit. For this example, it behaves as follows:

1. Apply X to all three `dst` bits. The empty destination changes temporarily from `000` to `111`.
2. Use all four `dir` bits and all three `dst` bits as controls. A later MCX also uses one source-status bit as a control.
3. Apply the MCX, a CX from `anc[0]` to a destination bit, and another MCX intended to clear the temporary ancilla result.
4. Apply X to all three destination bits again, undoing the temporary complement.

An MCX flips its target if and only if **every** control qubit is 1. Here every direction bit is 0, so the direction controls are not satisfied. The MCX gates do not fire; `anc[0]` and `dst` do not change during this stage. The final X gates restore `dst` from `111` to `000`.

Thus this example's logical data registers at the end of the unitary-gate portion are:

| Register | Logical value after the implemented gates | Meaning in this example |
|---|---|---|
| `cur` | `0000` | Source `(0,0)` |
| `tgt` | `0001` | Destination `(1,0)` |
| `dir` | `0000` | No direction flag was detected |
| `src` | `001` | Black Pawn status was looked up |
| `dst` | `000` | Destination remains encoded as empty |
| `anc` | `00000` | Scratch qubits end at zero for this input |

This output does **not** encode a completed pawn move: the source is still marked as occupied in `src`, the target still reads empty in `dst`, and there is no board register to update.

## 5. What each gate does, and why this circuit uses it

The exact gate letters and their effect on computational-basis bits are:

| Gate | Basis-state action | Why it appears here |
|---|---|---|
| X | `|0⟩ ↔ |1⟩` on its target | Loads coordinate 1-bits; temporarily converts zero-valued controls to 1s so an MCX can test an exact bit pattern; complements target status bits inside the status-operator attempt. |
| CX | `(control, target) → (control, target XOR control)` | Copies/toggles a bit conditionally in the direction logic. If the control is 0, the target stays the same; if it is 1, the target flips. |
| CCX | `(a,b,target) → (a,b,target XOR (a AND b))` | Toffoli gate used by the limited diagonal-pattern checks. It flips the target only when both controls are 1. |
| MCX | Flips its target iff every control equals 1 | Implements exact coordinate lookup and multi-condition patterns. A four-control example flips `src[0]` only when all four coordinate controls match the prepared pattern. |
| Measurement | Reads a qubit in the computational basis and records 0 or 1 | Produces the printed classical bit string. It does not itself move a piece or update `GameState`. |

All these gates are reversible. X is its own inverse; CX, CCX, and MCX are also their own inverses. That lets the code undo temporary control flips and keep the coordinate inputs intact while writing a status bit. A circuit with only these gates and basis-state inputs produces a basis-state output; that is why the noiseless statevector simulation with one shot gives a deterministic-looking bit string. This does not mean the circuit has found a move by quantum search.

The `PureQuantumCircuitBuilder` code for this example does not append H gates. Hadamard gates are relevant to a nontrivial Grover search, but no such search circuit is built by the current default option 7.

## 6. Measurement and the printed bit string

The builder measures every quantum register in order into classical bits `meas[0]` through `meas[22]`. In that mapping, each register's `q[0]` is sent to the next classical bit. Qiskit displays a measurement key with the highest-index classical bit on the left, so the printed 23-character string is not simply the register list written left-to-right. Read it by accounting for that reversal and the within-register bit ordering.

For this default input, the logical post-gate values are the register table above. The measured string is a readout of those circuit registers (subject to simulator behavior); it is not a new chess position and is not decoded back into a board. Option 7 prints the measurement and saves `architecture_2x2.png`; it does not apply the move to a persistent game.

With the current register-to-classical-bit wiring and noiseless statevector simulator, those values are displayed in Qiskit's reversed classical-bit order as:

```text
00000 000 001 0000 0001 0000
 anc   dst src  dir  tgt  cur
```

Without spaces, the 23-bit measurement key is `00000000001000000010000`. Grouping it by the labels above makes the register values easier to read than treating the full string as a board encoding.

## 7. What Grover would do in a different, nontrivial search

This section describes the Grover gates present in the general implementation, to distinguish them from what happens in the default 2×2 route. Suppose an application supplied at least two candidate moves and marked only some of their integer indices. `GroverSearch` would then construct a separate, small circuit with a move-index register, one flag qubit, and classical measurement bits.

### 7.1 Prepare an equal superposition with H

For one index qubit, H acts as:

```text
H|0⟩ = (|0⟩ + |1⟩)/√2
H|1⟩ = (|0⟩ - |1⟩)/√2
```

Starting at `|0⟩`, H creates equal amplitudes for candidate indices 0 and 1. With more index qubits, H on each creates equal amplitudes over all `2^n` bit strings. This is useful only if there are multiple alternatives to search; one candidate needs no amplitude amplification.

### 7.2 Prepare the phase-kickback flag

The Grover builder also starts a flag at `|0⟩`, then applies X followed by H:

```text
|0⟩ --X--> |1⟩ --H--> |−⟩ = (|0⟩ - |1⟩)/√2
```

If an oracle-controlled X flips this flag, `X|−⟩ = -|−⟩`. The flag returns to the same observable state, while the associated move-index amplitude acquires a minus sign. This is phase kickback.

### 7.3 Mark an index with the oracle

For each marked integer index, the oracle converts zero-valued index bits to 1 temporarily using X gates, applies an MCX controlled by the full index register to the flag, then undoes the X gates. That MCX fires only for the selected index. Because the flag is `|−⟩`, the selected index's amplitude changes sign:

```text
unmarked index amplitude: +a
marked index amplitude:   -a
```

The oracle in this repository does not calculate chess rules on a superposition. Python supplies the target indices to it before the circuit is built.

### 7.4 Amplify with the diffuser

The diffuser performs the reflection-about-the-mean operation. In `quantum/diffuser.py`, its gate sequence is H on every index qubit, X on every index qubit, a multi-controlled Z construction, then X and H again. With exactly one index qubit, the code uses a Z gate for the central step. With more qubits, it constructs the controlled-Z operation using H–MCX–H on the final qubit.

The phase oracle alone does not change measurement probabilities because `|a|² = |-a|²`. The diffuser lets amplitudes interfere so marked states can grow in probability. An appropriate number of oracle/diffuser rounds is important; too many rounds can reduce the success probability again.

### 7.5 Measure and decode

Measurement returns an index bit string. Classical Python parses it as an integer and uses that integer to select an element of the original `candidates` list. It checks that the index is in range and among the marked targets, with a fallback to the first target if needed.

Again, none of these Grover steps occur in the present 2×2 default path because that path has one candidate and returns early.

## 8. Why the present result is not a quantum board transition

The 23-qubit circuit has registers for one source coordinate, one target coordinate, a direction workspace, two compact status values, and scratch space. It has no register holding all four squares as a mutable board. It also has no implemented reversible operation that clears the source square, writes a piece into the destination, updates turn/history, or applies all chess rules.

The actual game transition belongs to classical code. In interactive option 6, after the circuit is measured, `PureQuantumGame2x2.make_move` calls its parent `Game.make_move(move)`. Option 7 does not make that call; it reports a selected move and a circuit measurement, then exits the demonstration.

The measured output should therefore be described as a **diagnostic measurement of a coordinate/status gate prototype**. The move list and move selection in option 7 are classical in this default example, and the board is not changed by the 23-qubit circuit.

## 9. Summary: actual default 2×2 execution

```text
Classical board setup
    Black Pawn at (0,0); other three squares empty
        ↓
Classical legal move generation
    One candidate: (0,0) → (1,0)
        ↓
GroverSearch early return
    Returns the only candidate; no Grover circuit or index measurement
        ↓
23-qubit coordinate/status circuit
    cur=0000, tgt=0001; lookup src=001 and dst=000
    limited direction logic leaves dir=0000 for this move
    status operator does not change the empty dst encoding
        ↓
One-shot measurement and circuit diagram
    Diagnostic bit string; no board update in option 7
```

That description matches the current code. To turn this into an actual Grover example, the program would need multiple candidates and a proper target-selection rule that marks a strict subset. To turn the small circuit into a move executor, it would need corrected reversible direction predicates, a complete board-state encoding, a validated reversible state transition, and code that decodes/uses the circuit result. Those are separate engineering tasks; the current demo should not claim they are already implemented.

## 10. Source files to follow along

- `config.py` — default 2×2 Black Pawn layout.
- `main.py` — option 6 and option 7 control flow.
- `engine/move_generator.py` — classical pawn move generation.
- `engine/move.py` — coordinate displacement and direction labels.
- `quantum/grover.py` — Grover early-return condition, general circuit, measurement, and index decoding.
- `quantum/oracle.py` — candidate generation and index-pattern oracle.
- `quantum/diffuser.py` — general Grover diffuser gates.
- `quantum/encoder.py` — coordinate/status bit encodings and register initialization.
- `pure_quantum_engine/registers.py` — the 23-qubit small-board register allocation.
- `pure_quantum_engine/circuit.py` — status lookup, direction pattern, status operator, and measurement wiring.
