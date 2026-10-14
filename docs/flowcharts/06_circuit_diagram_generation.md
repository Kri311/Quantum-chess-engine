# Menu circuit-diagram generation

Menu options 3, 4, and 5 use `generate_circuit_diagram` in `main.py`. Option 7 also saves the 2×2 circuit image after running its autonomous demo.

```mermaid
flowchart TD
    A([Select menu option]) --> B{Board size}
    B -->|3| C[Option 3: configure 8x8 board]
    B -->|4| D[Option 4: configure 3x3 board]
    B -->|5| E[Option 5: configure 2x2 board]
    C --> F[Place configured pieces]
    D --> F
    E --> F
    F --> G{Choose source and target}
    G -->|8x8| H[White Knight 7,6 to 5,5]
    G -->|3x3| I[First configured piece to one row forward]
    G -->|2x2| J[First configured piece to one row forward]
    H --> K[Build PureQuantumCircuitBuilder circuit]
    I --> K
    J --> K
    K --> L[Print qubit count, depth, and gate breakdown]
    L --> M{Board size at most 3?}
    M -->|yes| N[Transpile for Aer statevector]
    N --> O[Run QUANTUM_SHOTS and print counts]
    M -->|no| P[Skip simulation in diagram option]
    O --> Q[Draw circuit with Qiskit mpl renderer]
    P --> Q
    Q --> R[Save docs/assets/diagrams/architecture_SIZE.png]
    R --> S([Return to menu])
```

## Example inputs and caveats

- **8×8 option 3:** places a White Knight at `(7,6)` and supplies target `(5,5)`. It constructs the 33-qubit circuit and prints its structure; this menu route does not run the simulation branch because the board size exceeds 3.
- **3×3 option 4:** uses the configured first piece (currently a White Knight at `(2,1)`) and chooses `(1,1)` as the “one row forward” circuit input. That is not a legal Knight move. The diagram generator constructs the circuit directly; it does not ask `MoveGenerator` to validate this source/target pair.
- **2×2 option 5:** uses the Black Pawn at `(0,0)` and target `(1,0)`, then runs the configured number of shots for the circuit display.
- These options inspect circuit structure. They are not gameplay transitions and do not update a `GameState`.
- Option 7 separately saves the same canonical 2×2 image after its 2×2 pure-circuit simulation.

