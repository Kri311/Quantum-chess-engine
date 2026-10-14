# 2×2 black-pawn demonstrations

The project has two separate 2×2 routes. Both use one Black Pawn at `(0,0)`, but they connect to the circuit in different ways.

## Menu option 6: interactive pawn demo

```mermaid
flowchart TD
    A([main.py option 6]) --> B[Set BOARD_SIZE to 2]
    B --> C[Create Game and configured one-pawn board]
    C --> D[Set current turn to Black]
    D --> E[Create ChessGUI with no AI engine]
    E --> F[Human selects a legal pawn move]
    F --> G[PureQuantumGame2x2.make_move]
    G --> H[Build circuit for selected source and target]
    H --> I[Transpile and run Aer statevector for one shot]
    I --> J[Print circuit metrics and measurement]
    J --> K[Parent Game validates and applies move classically]
    K --> L{Continue?}
    L -->|yes| E
    L -->|no or terminal| M([End demo])
```

## Menu option 7: Grover-labelled autonomous demo

```mermaid
flowchart TD
    A([main.py option 7]) --> B[Create 2x2 board with Black Pawn at 0,0]
    B --> C[Set side to move to Black]
    C --> D[Call GroverSearch.search with default arguments]
    D --> E[MoveOracle.generate_all_candidates returns legal moves]
    E --> F{Any legal candidates?}
    F -->|no| G[Return no move and show no-valid-moves message]
    F -->|yes| H[compute_legal_indices marks every candidate as legal]
    H --> I{Are all candidates marked?}
    I -->|yes in current path| J[Return first candidate immediately]
    I -->|no in a different configured path| K[Build and simulate Grover circuit]
    J --> L[Build pure-circuit registers for returned move]
    K --> L
    L --> M[Run pure circuit with Aer statevector, one shot]
    M --> N[Print measurement and metrics]
    N --> O[Save circuit diagram under docs/assets/diagrams]
    O --> P([Demo complete])
    G --> P
```

## Important current behavior

Menu option 7 is labelled as a Grover search demo, but the current call path does **not** execute a Grover circuit for its default candidates. `generate_all_candidates` returns only legal moves, and `compute_legal_indices` marks all of those as targets. `GroverSearch.search` returns the first candidate when every candidate is a target, before circuit construction. The following pure-circuit simulation does run. This behavior is shown explicitly so the diagram matches the code.

The destination `(1,0)` is the illustrative forward square for the black pawn. The pure circuit's measured result is diagnostic; the option 7 wrapper prints it and saves the circuit diagram but does not call `Game.make_move` to update the board.
