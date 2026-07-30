# Architecture

## Module Dependency Diagram

```
main.py
  |
  |-- engine.Game
  |     |-- engine.Board
  |     |-- engine.GameState
  |     |-- engine.MoveGenerator -> engine.Rules
  |     |-- engine.Evaluator
  |     |-- engine.pieces (factory)
  |
  |-- ui.ChessGUI
  |     |-- ui.BoardRenderer
  |     |-- ui.MoveAnimator
  |     |-- engine.Game
  |
  |-- ai.HybridEngine
        |-- ai.MinimaxEngine -> ai.HeuristicEvaluator
        |-- ai.QuantumMoveSearcher
              |-- quantum.GroverSearch
                    |-- quantum.MoveOracle
                    |-- quantum.GroverDiffuser
                    |-- quantum.QuantumSimulator
                    |-- quantum.MeasurementProcessor
```

## Layered Architecture

```
+--------------------------------------------------+
|                    Presentation                   |
|   main.py  |  ui/gui.py  |  ui/renderer.py       |
+--------------------------------------------------+
|                  Application Logic                |
|   engine/game.py  |  ai/hybrid_engine.py          |
+--------------------------------------------------+
|                   Domain Model                    |
|   engine/board.py  |  engine/state.py              |
|   engine/piece.py  |  engine/position.py           |
|   engine/move.py   |  engine/constants.py          |
+--------------------------------------------------+
|                  Business Rules                   |
|   engine/rules.py  |  engine/move_generator.py     |
|   engine/evaluator.py                              |
+--------------------------------------------------+
|                Quantum Computation                |
|   quantum/encoder.py    |  quantum/decoder.py      |
|   quantum/registers.py  |  quantum/circuit_builder  |
|   quantum/oracle.py     |  quantum/diffuser.py      |
|   quantum/grover.py     |  quantum/measurement.py   |
|   quantum/simulator.py                              |
+--------------------------------------------------+
|                   AI / Search                     |
|   ai/heuristic.py  |  ai/minimax.py               |
|   ai/quantum_search.py                             |
+--------------------------------------------------+
```

## Data Flow

### Console Mode
```
User Input -> Game.play() -> MoveGenerator -> Rules -> User selects move -> GameState.apply_move()
```

### GUI Mode
```
Mouse Click -> ChessGUI._handle_click() -> MoveGenerator -> Highlight legal targets
Mouse Click on target -> MoveAnimator.start() -> Game.make_move() -> Render new state
```

### Quantum Mode
```
GameState -> HybridEngine.select_move()
  |-> MoveGenerator.generate_legal_moves()  [classical]
  |-> HeuristicEvaluator.score_move()       [classical ranking]
  |-> GroverSearch.search()                 [quantum amplification]
  |     |-> MoveOracle.generate_all_candidates()
  |     |-> MoveOracle.compute_legal_indices()
  |     |-> Build Grover circuit (superposition + oracle + diffuser)
  |     |-> QuantumSimulator.run()
  |     |-> MeasurementProcessor.get_most_likely()
  |     |-> Decode move index
  |-> Validate and return selected move     [classical verification]
```

## SOLID Principles

- **Single Responsibility**: Each class has one reason to change. `Board` manages piece storage. `Rules` validates legality. `MoveGenerator` produces moves. `Evaluator` scores positions.
- **Open/Closed**: New piece types are added by extending `PieceType` enum and adding methods to `MoveGenerator`, without modifying existing code.
- **Liskov Substitution**: All positions, pieces, and moves are interchangeable through their interfaces.
- **Interface Segregation**: Classical engine knows nothing about quantum. Quantum oracle imports only the minimal classical interfaces it needs.
- **Dependency Inversion**: `HybridEngine` depends on abstractions (MoveGenerator, Evaluator) not concrete implementations.
