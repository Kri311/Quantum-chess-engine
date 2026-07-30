# Circuit Design

Detailed documentation of every quantum circuit used in the Quantum Chess Engine, following the base paper's design.

## Register Allocation

| Register       | Qubits | Name  | Purpose                                    |
|----------------|--------|-------|--------------------------------------------|
| Current Square | 4      | `cur` | Coordinate of source square (x1 x0 y1 y0) |
| Target Square  | 4      | `tgt` | Coordinate of destination square           |
| Direction      | 2      | `dir` | Computed move direction (d1 d0)            |
| Source Status   | 2      | `src` | Piece status of source square              |
| Target Status   | 2      | `dst` | Piece status of target square              |
| Ancilla        | 4      | `anc` | Scratch workspace for reversible logic     |
| Flag           | 1      | `flag`| Oracle output (1 = legal move)             |
| **Total**      | **19** |       |                                            |

## Circuit 1: Comparator (Paper Fig 4c)

**Purpose**: Check if two n-qubit registers hold the same value.

**Algorithm**:
1. XOR register A into register B: `CNOT(a[i], b[i])` for each qubit.
2. If A == B, all B qubits become |0>. Apply X to each B qubit (now all |1> if equal).
3. Multi-controlled X: set output to |1> if all B qubits are |1>.
4. Uncompute steps 1-2 to restore B.

**Gate Count**: 2n CNOT + 2n X + 1 MCX(n)

```
a[0] ──●──────────────────●── a[0]
       │                  │
b[0] ──⊕── X ──■──── X ──⊕── b[0]
                │
a[1] ──●──────────────────●── a[1]
       │       │          │
b[1] ──⊕── X ──■──── X ──⊕── b[1]
                │
out  ──────────⊕────────────── out (1 if a==b)
```

## Circuit 2: Direction Detector

**Purpose**: Determine the direction of a pawn move from coordinate differences.

**Direction Encoding**:

| Direction       | d1 | d0 | Condition                              |
|-----------------|----|----|----------------------------------------|
| Forward         | 1  | 1  | Same column, row differs by 1          |
| Diagonal Left   | 1  | 0  | Column decreases by 1, row differs by 1|
| Diagonal Right  | 0  | 1  | Column increases by 1, row differs by 1|
| Invalid         | 0  | 0  | None of the above                      |

**Algorithm**:
1. Compare source and target columns using the Comparator.
2. If columns match, set direction = |11> (forward).
3. If target column < source column, set direction = |10> (left diagonal).
4. If target column > source column, set direction = |01> (right diagonal).

## Circuit 3: Status Extractor (Paper Fig 5)

**Purpose**: Look up the piece status of a square given its coordinates.

**Algorithm**: For each square on the board:
1. Apply X gates to coordinate qubits where the square's encoding has |0>.
2. Multi-controlled X: if all coordinate qubits are |1> (matching this square), copy the square's status to the output register.
3. Uncompute the X gates.

This creates a quantum lookup table — the output register receives the status corresponding to the coordinate in the input register.

**Gate Count per square**: Up to 4 X gates + 1 MCX(4) for status bit 0 + 1 MCX(4) for status bit 1 + 4 X gates to uncompute.

## Circuit 4: Status Operator (Paper Fig 6)

**Purpose**: Apply the move by updating source and target square statuses.

**Forward Move** (dir = |11>, target must be empty):
1. Check dst_status == |00> (apply X to both, check both are |1>).
2. If dir == |11> AND dst == |00>:
   - Copy src_status to dst_status (src piece moves to target).
   - Clear src_status to |00> (source square becomes empty).
3. Uncompute condition checks.

**Diagonal Capture** (dir = |10> or |01>, target must have enemy):
1. Check dst_status has enemy piece.
2. If conditions met:
   - Replace dst_status with src_status (capture).
   - Clear src_status to |00>.
3. Uncompute.

## Circuit 5: Grover Oracle

**Purpose**: Mark legal moves with a phase flip for Grover's algorithm.

**Algorithm**: For each legal move index `i` in the candidate list:
1. Apply X to move_register qubits where bit `i` has |0>.
2. MCX: flip flag_qubit when all move_register qubits are |1>.
3. Uncompute X gates.

When flag_qubit is in |-> state, the MCX causes phase kickback: the basis state |i> picks up a -1 phase.

## Circuit 6: Grover Diffuser

**Purpose**: Amplify the amplitude of marked states (inversion about the mean).

**Algorithm**:
```
H^n  -->  X^n  -->  MCZ  -->  X^n  -->  H^n
```

Where MCZ = H on last qubit, MCX on all-but-last controlling last, H on last qubit.

This implements the operator `2|s><s| - I` where `|s>` is the uniform superposition.

## Complexity Analysis

| Circuit            | Qubits | Gates (approx)        | Depth   |
|--------------------|--------|-----------------------|---------|
| Comparator (2-bit) | 5      | 8 CNOT + 4 X + 1 MCX | O(n)    |
| Direction Detector | 10     | ~20 gates             | O(1)    |
| Status Extractor   | 6+     | 9 * (8+2 MCX)        | O(S)    |
| Status Operator    | 8      | ~15 controlled gates  | O(1)    |
| Grover Oracle      | n+1    | M * (n X + 1 MCX)    | O(M*n)  |
| Grover Diffuser    | n      | 2n H + 2n X + 1 MCZ  | O(n)    |

Where S = number of squares, M = number of legal moves, n = move index qubits.
