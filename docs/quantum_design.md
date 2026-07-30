# Quantum Design

## Overview

The quantum component of the Quantum Chess Engine serves two purposes:

1. **Board State Encoding**: Represent the classical chess board state as quantum register states, enabling quantum operations on the game state.

2. **Move Selection via Grover's Algorithm**: Use quantum search to amplify legal (or best) moves from a candidate pool, providing a quadratic speedup over classical exhaustive search.

## Encoding Scheme

### Position Encoding

Following the base paper, each square on the board is identified by 4 qubits encoding its (column, row) position:

```
|x1 x0 y1 y0>

x1 x0 = column (0 to 2 for 3x3)
y1 y0 = row    (0 to 2 for 3x3)
```

This encoding is chosen because:
- It maps naturally to the 2D grid structure.
- Arithmetic operations (comparison, subtraction) on coordinates are straightforward in binary.
- It scales to 8x8 by increasing axis bits: `ceil(log2(8)) = 3` bits per axis, so 6 qubits per coordinate.

### Status Encoding

Each square's occupancy is encoded with 2 qubits:

```
|00> = Empty (no piece)
|01> = Black Pawn
|10> = White Pawn
```

For 8x8 expansion with multiple piece types, additional qubits would distinguish piece types (3 qubits for 6 types: Pawn, Rook, Knight, Bishop, Queen, King), giving 5 qubits per square status.

### Board State

The complete board state is the tensor product of all square statuses:

```
|Board> = |s1> ⊗ |s2> ⊗ ... ⊗ |s9>
```

where each `|si>` is a 2-qubit status register. Total: 18 qubits for the full board state (3x3).

## Oracle Design

### Purpose

The oracle is a unitary operator U_f that identifies legal moves:

```
U_f |x>|flag> = |x>|flag ⊕ f(x)>
```

where `f(x) = 1` if move x is legal, `f(x) = 0` otherwise.

### Implementation

Rather than encoding the full board in superposition (which would require ~20 qubits just for the board state), we use a more practical approach:

1. **Classical pre-computation**: Generate all N candidate moves classically.
2. **Index encoding**: Encode the move index (0 to N-1) in `ceil(log2(N))` qubits.
3. **Oracle marking**: For each legal index, apply the standard Grover oracle pattern (X gates to condition on |0> bits + MCX + uncompute).

This approach is equivalent to the theoretical full-board oracle but uses far fewer qubits.

### Legality Conditions

A pawn move from square A to square B is legal if:

1. **Piece exists at A**: `status(A) != |00>`.
2. **Correct colour**: `status(A)` matches the current turn.
3. **Valid direction**: The coordinate difference between A and B corresponds to a legal pawn direction.
4. **Target compatibility**:
   - Forward: `status(B) == |00>` (target must be empty).
   - Diagonal: `status(B)` has an enemy piece.

Each condition is checked by the sub-circuits (comparator, direction detector, status extractor) and combined using multi-controlled gates.

## Grover's Algorithm Application

### Search Space

For a given board position, the search space consists of all candidate moves. For the 3x3 board with one pawn per side, this is at most 3 candidates per turn (forward + 2 diagonals).

### Circuit Structure

```
|0>^n --[H^n]-- |s> --[Oracle]--[Diffuser]-- ... --[Measure]
                       |__________________________|
                              Repeat k times

k = floor(pi/4 * sqrt(N/M))
N = total candidates (2^n)
M = number of legal moves
```

### Optimal Iterations

| N (search space) | M (solutions) | k (iterations) |
|-------------------|---------------|----------------|
| 4                 | 1             | 1              |
| 4                 | 2             | 1              |
| 8                 | 1             | 2              |
| 8                 | 2             | 1              |
| 16                | 1             | 3              |
| 64                | 1             | 6              |
| 64                | 4             | 3              |

### Measurement and Decoding

After k Grover iterations, measuring the move-index register yields a legal move index with probability approaching 1. The `MeasurementProcessor` extracts the most likely result from the shot statistics.

If the measurement yields an invalid or illegal index (possible with low iteration counts or measurement noise), the system falls back to classical move selection.

## Scaling Analysis

### 3x3 Board (Current)

| Parameter          | Value  |
|--------------------|--------|
| Coordinate qubits  | 4      |
| Status qubits      | 2      |
| Move index qubits  | 2      |
| Oracle gate depth  | ~10    |
| Grover iterations  | 1      |
| Total circuit depth | ~30    |

### 8x8 Board (Future)

| Parameter          | Value  |
|--------------------|--------|
| Coordinate qubits  | 6      |
| Status qubits      | 5      |
| Move index qubits  | 6-7    |
| Oracle gate depth  | ~100   |
| Grover iterations  | 3-6    |
| Total circuit depth | ~600   |

The 8x8 board is within reach of modern NISQ devices (~100 qubits) but would require error mitigation techniques for reliable results.

## Connection to the Papers

### Base Paper Circuits Used

| Paper Circuit         | Our Module                    | Purpose                    |
|-----------------------|-------------------------------|----------------------------|
| Subtractor (Fig 4a)   | `circuit_builder.py`          | Coordinate difference      |
| Adder (Fig 4b)        | `circuit_builder.py`          | Coordinate computation     |
| Comparator (Fig 4c)   | `circuit_builder.build_comparator()` | Equality checking   |
| Status Extractor (Fig 5) | `circuit_builder.build_status_extractor()` | Square lookup |
| Status Operator (Fig 6)  | `circuit_builder.build_status_operator()` | Move execution |
| Board Update (Fig 7)  | `circuit_builder.build_move_circuit()` | State update      |

### Grover's Algorithm Components

| Grover Component     | Our Module                    | Purpose                    |
|----------------------|-------------------------------|----------------------------|
| Initialisation (H^n) | `grover.py`                   | Uniform superposition      |
| Oracle (U_f)         | `oracle.py`                   | Mark legal moves           |
| Diffuser (2|s><s|-I) | `diffuser.py`                 | Amplitude amplification    |
| Measurement          | `measurement.py`              | Result extraction          |
