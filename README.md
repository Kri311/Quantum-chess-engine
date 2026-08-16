# Quantum Chess Engine

A hybrid classical-quantum chess engine that demonstrates genuine quantum computation applied to chess using Qiskit. 
Originally built as a 3x3 pawn-chess prototype, it has now been fully scaled to an **8x8 Standard Board** supporting all traditional pieces (Pawns, Knights, Bishops, Rooks, Queens, Kings) using a GPU-accelerated Hybrid CPU-GPU architecture.

This project is a research project for Quantum Computing and Algorithms, grounded in two foundational papers and implemented as production-quality Python suitable for academic publication and public GitHub release.

---

## Architecture

```
quantum-chess-engine/
|
|-- main.py                  Entry point (console / gui / quantum modes)
|-- config.py                Global configuration (board size, quantum params)
|
|-- engine/                  Classical chess engine
|   |-- constants.py         Enums: Color, PieceType, Direction
|   |-- position.py          Immutable (row, col) coordinate
|   |-- piece.py             Chess piece with colour and type
|   |-- pieces.py            Initial piece layout factory
|   |-- move.py              Move with direction detection
|   |-- board.py             Board state (dict[Position, Piece])
|   |-- state.py             GameState (board + turn + history)
|   |-- rules.py             Move legality validation
|   |-- move_generator.py    Legal move generation (strategy pattern)
|   |-- evaluator.py         Heuristic scoring and win detection
|   |-- game.py              Game orchestrator (console + programmatic API)
|
|-- quantum/                 Quantum computation
|   |-- registers.py         Qiskit register allocation
|   |-- encoder.py           Classical -> Quantum (position + status encoding)
|   |-- decoder.py           Quantum -> Classical (measurement decoding)
|   |-- circuit_builder.py   Sub-circuits (comparator, direction, status ops)
|   |-- simulator.py         Qiskit Aer wrapper
|   |-- oracle.py            Reversible move-legality oracle
|   |-- diffuser.py          Grover diffusion operator
|   |-- grover.py            Grover's search algorithm
|   |-- measurement.py       Measurement post-processing
|
|-- ai/                      AI and hybrid engine
|   |-- heuristic.py         Classical heuristic evaluator
|   |-- minimax.py           Minimax with alpha-beta pruning
|   |-- quantum_search.py    Quantum move searcher (Grover wrapper)
|   |-- hybrid_engine.py     Combined classical + quantum pipeline
|
|-- ui/                      Pygame graphical interface
|   |-- renderer.py          Board and piece drawing
|   |-- animations.py        Smooth piece movement animation
|   |-- gui.py               Event loop and interaction handling
|
|-- tests/                   Pytest test suite
|-- docs/                    Technical documentation
```

### Data Flow

```
Classical Board State
        |
        v
  [BoardEncoder] -- Position -> 4-qubit coordinate (|x1 x0 y1 y0>)
        |           -- Status  -> 2-qubit status (|00>, |01>, |10>)
        v
  [CircuitBuilder] -- Direction detection (subtractor/comparator)
        |            -- Status extraction (multi-controlled lookup)
        |            -- Status operation (move application)
        v
  [MoveOracle] -- Reversible legality check (MCX gates)
        |
        v
  [GroverSearch] -- Superposition of candidates
        |          -- Oracle + Diffuser iterations
        |          -- Measurement
        v
  [BoardDecoder] -- Bitstring -> Position, Piece, Move
        |
        v
  Classical Move Selection
```

---

## Quantum Design

### Board Encoding (Base Paper)

Each square on the 3x3 board is encoded using 4 qubits (2 for column X, 2 for row Y):

| Square | Position | Coordinate Qubits |
|--------|----------|-------------------|
| 1      | (0,0)    | `\|0000>`           |
| 2      | (0,1)    | `\|0100>`           |
| 3      | (0,2)    | `\|1000>`           |
| 4      | (1,0)    | `\|0001>`           |
| 5      | (1,1)    | `\|0101>`           |
| 6      | (1,2)    | `\|1001>`           |
| 7      | (2,0)    | `\|0010>`           |
| 8      | (2,1)    | `\|0110>`           |
| 9      | (2,2)    | `\|1010>`           |

Piece status uses 2 qubits per square:

| Status | Encoding | Meaning    |
|--------|----------|------------|
| Empty  | `\|00>`    | No piece   |
| Black  | `\|01>`    | Black Pawn |
| White  | `\|10>`    | White Pawn |

### Grover's Algorithm

Applied to amplify legal moves from the search space:

1. Encode all candidate moves into uniform superposition.
2. Apply the legality oracle (marks legal moves with phase flip).
3. Apply the Grover diffuser (inversion about the mean).
4. Repeat for `floor(pi/4 * sqrt(N/M))` iterations.
5. Measure to collapse to a legal move with high probability.

---

## The Hybrid CPU-GPU Advantage (Scaling to 8x8)

Simulating a full 8x8 board purely on a quantum computer using the architecture described in the base papers requires **33 Qubits** (12 for coordinates, 6 for status, 4 for direction, 11 for ancillas/Grover). 
Simulating 33 qubits classically requires tracking $2^{33}$ complex amplitudes simultaneously, which demands roughly **128 Terabytes of RAM**—impossible for modern hardware.

To achieve real-time, playable performance on an RTX 4050 Laptop GPU, we decoupled the **Physics of Chess** from the **Decision Making** using a **Hybrid Architecture**:

1. **CPU (Classical Mechanics)**: 
   The classical engine scans the board and computes a strict list of legal moves (e.g., 30 possible moves). It mathematically handles the physics of sliding pieces and captures, passing this $N$-sized array to the quantum pipeline.

2. **CPU (Heuristics & MVV-LVA)**: 
   The CPU scores these 30 moves using material values and positional advantages, tagging the mathematically "best" moves as optimal.

3. **GPU (Quantum Compression)**: 
   Instead of encoding the entire $8 \times 8$ board state into 33 qubits, we only need to encode the **Search Array Index**. Since there are 30 moves, we only need **5 Qubits** to represent the entire decision space ($2^5 = 32$).

4. **GPU (Grover Amplification)**: 
   The `qiskit-aer-gpu` simulator executes a fast 6-qubit (5 index + 1 flag) Grover Search Oracle directly on the RTX 4050. The oracle flips the phase of the optimal move indices, and the Diffuser amplifies them. 
   
By compressing the problem from an $O(N^2)$ spatial board representation to an $O(\log_2 M)$ search array representation, the quantum simulation finishes in **~140 milliseconds** instead of crashing due to out-of-memory errors.

---

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/Quantum-chess-engine.git
cd Quantum-chess-engine

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Requirements

- Python 3.12+
- Qiskit 2.5.0
- Qiskit Aer 0.17.2
- Pygame (for GUI mode)
- Pytest (for testing)
- Matplotlib (for circuit visualisation)

---

## Running

### Console Mode (Default)

```bash
python main.py
# or
python main.py --mode console
```

Interactive terminal game with text-based board display.

### GUI Mode

```bash
python main.py --mode gui
```

Pygame graphical interface with:
- Mouse-click piece selection
- Legal move highlighting
- Smooth piece movement animation
- FPS display
- Resizable window
- Restart (R) and Quit (ESC) keys

### Quantum Mode

```bash
python main.py --mode quantum
```

Hybrid engine plays both sides automatically using:
1. Classical move generation
2. Quantum Grover search for move selection
3. Classical validation and execution

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test modules
pytest tests/test_board.py -v
pytest tests/test_encoder.py -v
pytest tests/test_grover.py -v

# Run integration tests
pytest tests/integration_test.py -v
```

---

## References

1. **Design of Quantum Circuits to Play Chess in a Quantum Computer** - The base paper implementing 3x3 chess on quantum circuits using coordinate/status qubit encoding, direction detection, status extraction, and board state update circuits.

2. **A Fast Quantum Mechanical Algorithm for Database Search** (Grover, 1996) - The original Grover's algorithm paper providing O(sqrt(N)) unstructured search, applied here to amplify legal chess moves from the candidate space.

---

## Future Work

## Future Work

The architecture is currently complete for 8x8 play, but is designed for further expansion:

- **Advanced rules**: Castling, en passant, promotion, full check/checkmate verification trees.
- **Circuit Transpilation Optimization**: Mapping the multi-controlled gates more efficiently to specific hardware topologies.
- **NISQ hardware**: Replace Aer simulator with IBM Quantum hardware backends to run the hybrid engine on a physical quantum processing unit (QPU).

---

## License

This project is intended for academic research and educational purposes.
