# Whole-project architecture

```mermaid
flowchart TD
    Start([Run project]) --> Menu[main.py interactive menu]
    Config[config.py board layouts and simulator defaults] -. settings .-> Menu

    Menu -->|1| HybridUI[8x8 hybrid GUI]
    Menu -->|2| Pure3UI[3x3 pure-circuit GUI]
    Menu -->|3 to 5| DiagramMode[Circuit diagram generator]
    Menu -->|6| Pawn2UI[2x2 interactive pawn GUI]
    Menu -->|7| Grover2[2x2 Grover-labelled demo]
    Menu -->|comparison command| Benchmark[3x3 benchmark script]

    subgraph SharedChess[Shared classical chess foundation]
        GUI[ui ChessGUI] --> Game[engine Game and GameState]
        Game --> Board[engine Board and pieces]
        Game --> Rules[MoveGenerator and rules]
        Rules --> Legal[Legal Move list]
        Game --> Apply[Game.make_move validates and applies move]
    end

    HybridUI --> GUI
    Pure3UI --> GUI
    Pawn2UI --> GUI
    GUI -->|human input and display| Game
    Legal -->|AI turn| HybridAI[HybridEngine]
    HybridAI -->|8x8 quantum enabled| Search[QuantumMoveSearcher]
    Search -->|classical heuristic marks best indices| Grover[GroverSearch and oracle/diffuser]
    Grover --> Sim[quantum Simulator using Qiskit Aer]
    Sim --> Decode[Measurement and index decode]
    Decode -->|candidate move| HybridAI
    HybridAI -->|invalid or unavailable result| Minimax[Depth-3 Minimax fallback]
    Minimax --> HybridAI
    HybridAI -->|selected move| GUI

    Pure3UI -->|use_quantum=False| Minimax
    Pawn2UI -->|manual legal move| PureWrap[PureQuantumGame wrapper]
    PureWrap --> PureBuilder[PureQuantumCircuitBuilder]
    Grover2 -->|first legal candidate in current implementation| PureBuilder
    DiagramMode --> PureBuilder
    PureBuilder --> PureSim[Aer statevector circuit simulation]
    PureSim -->|measured string is diagnostic| PureWrap
    PureSim --> Diagram[PNG circuit artifact under docs/assets/diagrams]
    PureWrap -->|actual selected Move| Apply
    GUI -->|render board, input, animation| View[ui renderer and animator]

    Benchmark --> Positions[Four seeded 3x3 positions]
    Positions --> Classical[3x3 depth-3 minimax baseline]
    Positions --> PureBranch[Pure-circuit run for first legal move]
    Positions --> HybridBranch[Classical heuristic targets plus Grover index circuit]
    Classical --> Metrics[Time, extra peak RAM, legal moves, qubits, gates, depth]
    PureBranch --> Metrics
    HybridBranch --> Metrics
    Metrics --> Outputs[CSV tables, comparison PNG, Markdown report]
```

## What is shared and what is separate

- `engine/` owns the actual board and move rules in every playable route.
- `ui/` is shared by the 8×8, 3×3, and interactive 2×2 game modes.
- `ai/` supplies the hybrid 8×8 selector, minimax fallback, and 3×3 classical benchmark selector.
- `quantum/` builds and runs the move-index Grover circuit.
- `pure_quantum_engine/` constructs a different circuit: coordinates and statuses for one supplied move.
- The benchmark is a separate command-line experiment, not an additional GUI mode.

