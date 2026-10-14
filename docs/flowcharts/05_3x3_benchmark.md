# 3×3 system-comparison benchmark

```mermaid
flowchart TD
    A([Run evaluation/compare_3x3_systems.py]) --> B[Build four reproducible 3x3 positions with seed 20261013]
    B --> C[For each position generate legal moves and record legal-move count]
    C --> D1[Classical branch]
    C --> D2[Pure-circuit branch]
    C --> D3[Hybrid Grover branch]

    subgraph Classical[3x3 classical selector]
        D1 --> E1[Depth-3 minimax selects move]
        E1 --> F1[Record elapsed time and sampled extra peak RAM]
        F1 --> G1[Qubits, gates, and depth are N/A]
    end

    subgraph Pure[3x3 pure-circuit operation]
        D2 --> E2[Choose first legal move as fixed circuit input]
        E2 --> F2[Build 23-qubit pure circuit]
        F2 --> G2[Transpile and run Aer CPU matrix-product-state; one shot]
        G2 --> H2[Record time, RAM, qubits, gate count, and depth]
    end

    subgraph Hybrid[3x3 hybrid move-index operation]
        D3 --> E3[Score legal moves classically]
        E3 --> F3[Mark every index tied for best heuristic score]
        F3 --> G3{All moves are tied best?}
        G3 -->|yes| H3[Skip Grover circuit; circuit metrics remain N/A]
        G3 -->|no| I3[Build move-index Grover circuit]
        I3 --> J3[Transpile and run Aer CPU matrix-product-state; 2048 shots]
        J3 --> K3[Record time, RAM, qubits, gate count, and depth]
    end

    G1 --> M[Aggregate metrics across four positions]
    H2 --> M
    H3 --> M
    K3 --> M
    M --> N[Write summary and per-position CSV files]
    M --> O[Plot systems on x-axis; time, RAM, qubits, gates in metric panels]
    M --> P[Write docs/reports/3x3_system_comparison.md]
```

## How to interpret the branches

- **Classical:** measures depth-3 minimax move selection. There is no quantum circuit, so circuit metrics are N/A.
- **Pure circuit:** processes a fixed legal move; it does not autonomously select that move.
- **Hybrid:** legality and heuristic target selection happen classically, then Grover samples the compact index circuit. It is not a coherent search over all chess rules.
- All branches use the same four seeded positions. Simulator setup is excluded from the measured operation time; memory is an approximate sampled increase in process RSS.
- The result is a local simulator resource comparison. It does not measure move quality, hardware execution, or quantum advantage.

