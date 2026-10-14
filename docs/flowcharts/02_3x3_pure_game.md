# 3×3 pure-circuit game

```mermaid
flowchart TD
    A([main.py option 2]) --> B[Set BOARD_SIZE to 3]
    B --> C[Create Game with configured 3x3 pieces]
    C --> D[Wrap Game as PureQuantumGame]
    D --> E[Create HybridEngine use_quantum false]
    E --> F[Create ChessGUI human White AI Black]
    F --> G[Human chooses a legal move]
    G --> H[GUI animates selected move]
    H --> I[PureQuantumGame.make_move override]
    I --> J[Build circuit from current state and supplied source/target]
    J --> K[Encode coordinates and read square statuses into registers]
    K --> L[Append limited direction and status-operation gates]
    L --> M[Transpile for Aer statevector simulator]
    M --> N[Run one shot and read measured bit string]
    N --> O[Print qubits, depth, elapsed time, and measurement]
    O --> P[Call parent Game.make_move]
    P --> Q[Validate move and update classical GameState]
    Q --> R{Game over?}
    R -->|no| S[AI turn uses depth-3 classical minimax]
    S --> H
    R -->|yes| T([Display result])
```

## What the 3×3 mode does

- Default example layout: White Knight `(2,1)` and Black Pawn `(0,0)`.
- The player's legal move is used as the circuit input; the circuit is not the move selector.
- The AI is deliberately configured as `HybridEngine(use_quantum=False)`, so its move comes from classical minimax.
- `PureQuantumCircuitBuilder` encodes the chosen move. The measured string is printed for diagnostics.
- The parent `Game.make_move` validates and applies the actual board transition classically.

**Scope note:** The circuit's direction/status operations are a prototype. They do not implement a complete reversible 3×3 chess state update.

