# 8×8 hybrid gameplay

```mermaid
flowchart TD
    A([main.py option 1]) --> B[Set BOARD_SIZE to 8]
    B --> C[Create HybridEngine use_quantum true]
    C --> D[Create ChessGUI human White AI Black]
    D --> E[Render current classical GameState]
    E --> F{Human turn?}
    F -->|yes| G[Select piece and destination in GUI]
    G --> H[GUI displays legal targets from MoveGenerator]
    H --> I[Animate move]
    I --> J[Game.make_move validates and updates GameState]
    J --> K{Game over?}
    K -->|no| E
    F -->|AI turn| L[HybridEngine.select_move]
    L --> M[MoveGenerator builds legal candidates]
    M --> N{No moves or only one?}
    N -->|no moves| End([Stop or show game result])
    N -->|one move| Q[Return the only legal move]
    N -->|multiple| O[QuantumMoveSearcher scores legal moves classically]
    O --> P[Collect every index tied for highest heuristic score]
    P --> R{Are all legal moves tied for best score?}
    R -->|yes| Q
    R -->|no| S[GroverSearch encodes candidate indices]
    S --> T[H layer creates index superposition; flag prepared in minus state]
    T --> U[Oracle phase-marks target indices by controlled gates]
    U --> V[Diffuser reflects amplitudes about their mean]
    V --> W[Repeat oracle and diffuser for chosen iteration count]
    W --> X[Qiskit Aer samples the move-index register]
    X --> Y[Decode measured bit string to integer index]
    Y --> Z{Index is a target candidate?}
    Z -->|yes| Q
    Z -->|no or unmarked index| AA[Use first best-scoring index fallback]
    AA --> Q
    Q --> AB[HybridEngine returns selected Move]
    AB --> AC[GUI animates AI move]
    AC --> J
    K -->|yes| End
```

## Connection details

1. `ui/gui.py` asks `Game`/`MoveGenerator` for legal targets and calls `HybridEngine.select_move` on the AI turn.
2. `HybridEngine` returns the sole legal move immediately when there is only one. Otherwise it calls `QuantumMoveSearcher` when quantum mode is enabled.
3. `ai/quantum_search.py` uses `HeuristicEvaluator.score_move` to choose target indices before Grover runs. Grover amplifies these already selected indices; it does not discover chess legality.
   If every legal move is tied for best, `GroverSearch` returns the first target directly and skips circuit construction.
4. `quantum/grover.py` creates a compact index register of `ceil(log2(candidate count))` qubits (minimum one) plus a phase-kickback flag. The index space is padded to a power of two when needed.
5. Measurement is decoded to a legal move-list index. If it does not map to a marked index, the implementation returns the first best index. If the quantum search path returns no move, `HybridEngine` uses depth-3 minimax.
6. `Game.make_move` remains authoritative: it validates and applies the selected move to the classical `GameState`.

**Important:** Grover does not search a coherent 8×8 board or game tree. Legal moves and heuristic targets are built by Python before the circuit is constructed.
