# Shared pure-circuit builder

This is the common path used when a game wrapper or circuit-diagram option asks `PureQuantumCircuitBuilder` to construct a circuit for one supplied source/target pair.

```mermaid
flowchart TD
    A[Caller supplies GameState, source, target, color] --> B[PureQuantumRegisters reads board size]
    B --> C{Board size}
    C -->|2x2 or 3x3| D[4 coordinate qubits per square; 3 status qubits per square]
    C -->|8x8| E[6 coordinate qubits per square; 6 status qubits per square]
    D --> F[Allocate direction register and 5 ancillas]
    E --> F
    F --> G[Create matching classical measurement register]
    G --> H[BoardEncoder encodes source and target positions]
    H --> I[Initialize coordinate registers with X gates for one bits]
    I --> J[Status extractor loops over the classical board at build time]
    J --> K[Coordinate-control MCX gates write source and target status bits]
    K --> L[Direction helper appends limited coordinate-comparison gates]
    L --> M[Status operator appends controlled status transformation attempt]
    M --> N[Measure every quantum register into classical bits]
    N --> O[Return QuantumCircuit and register handles]
    O --> P[Caller transpiles and runs simulator or draws circuit]
    P --> Q[Counts / measured string / metrics / diagram]
```

## Register totals

| Board | Coordinate bits per square | Status bits per square | Direction | Ancillas | Total |
|---|---:|---:|---:|---:|---:|
| 2×2 | 4 | 3 | 4 | 5 | 23 qubits |
| 3×3 | 4 | 3 | 4 | 5 | 23 qubits |
| 8×8 diagram allocation | 6 | 6 | 4 | 5 | 33 qubits |

There is no complete board register in this builder. The status extractor compiles a lookup from the **classical** board into gates. The circuit measures its working registers; game wrappers use the original `Move` object for the real board update. The movement comparator is limited and should not be presented as a general reversible chess legality checker.

