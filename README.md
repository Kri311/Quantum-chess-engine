# Quantum Chess Engine

A hybrid classical-quantum chess engine that demonstrates genuine quantum computation applied to standard 8x8 chess using Qiskit. Implements a fully-featured chess board (Pawns, Knights, Bishops, Rooks, Queens, Kings) accelerated by an NVIDIA RTX 4050 GPU using cuQuantum and cuStateVec.

This project is a research project for Quantum Computing and Algorithms, grounded in foundational academic papers, and implemented as production-quality Python suitable for academic publication and public GitHub release.

---

## ⚡ Hybrid Classical-Quantum Architecture

A major achievement of this project is resolving the "Quantum Memory Explosion" problem. 

### The Theoretical Pure Quantum Model (33 Qubits)
In a purely theoretical quantum computer, the entire physical board state and the rules of chess are encoded directly into quantum gates:
- **Coordinate Encoding:** 12 qubits (6 for source, 6 for target)
- **Status Extraction:** 6 qubits (3 for source piece, 3 for target piece)
- **Quantum Subtractor:** 9 qubits (to calculate move trajectory legality)
- **Status Transformation:** 6 qubits (to apply the move)

**The Problem:** Simulating 33 qubits classically requires tracking $2^{33}$ complex probability amplitudes — consuming **128 Terabytes of RAM**. This makes the theoretical academic model physically impossible to simulate on modern consumer hardware.

### The Real-World Hybrid Model (6 Qubits)
To make this playable in real-time with hardware acceleration, we decouple the *rules of chess* from the *decision making*:
1. **Classical Move Generation (CPU):** The Python CPU engine evaluates the physical rules of chess and generates an array of strictly legal moves (e.g., 25 possible moves).
2. **Heuristic Evaluation (CPU):** The CPU assigns a material/positional score to each legal move and identifies the optimal candidates.
3. **Quantum Compression (GPU):** Instead of encoding the entire physical chessboard (33 qubits), we simply encode the *search space index*. To represent an array of up to 32 legal moves, we only need **5 qubits** ($2^5 = 32$).
4. **Grover's Oracle Amplification (GPU):** We construct a 6-qubit Grover Search circuit on the RTX 4050 GPU. The Oracle flips the quantum phase of the optimal move indices, and the Diffuser amplifies their probability to near 100%.
5. **Measurement:** The quantum circuit is measured, collapsing into the mathematically best move.

By mapping **Move Indices** to qubits instead of mapping **Physical Chess Pieces** to qubits, we compressed the requirement from $O(N^2)$ board qubits down to $O(\log_2 M)$ search qubits. This allows standard laptops to run genuine quantum algorithms natively.

---

## Architecture Map

```
quantum-chess-engine/
|
|-- main.py                  Entry point (quantum_gui / console modes)
|-- generate_complete_circuit.py Generates the full 33-qubit academic architecture PNG
|-- demo_3x3_pure_quantum.py Demonstrates the 19-qubit pure quantum base paper logic
|
|-- engine/                  Classical chess engine (8x8 rules, move gen, heuristics)
|-- quantum/                 Quantum computation (Encoder, Simulator, Oracle, Grover)
|-- pure_quantum_engine/     Implementation of theoretical full-board quantum circuits
|-- ai/                      Hybrid Engine combining CPU Heuristics + GPU Quantum Search
|-- ui/                      Pygame graphical interface (animations, piece rendering)
```

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
- Python 3.10+
- `qiskit==0.46.3`
- `qiskit-aer-gpu==0.14.2`
- `cuquantum-cu12` (for NVIDIA hardware acceleration)
- `pygame` (for GUI)
- `matplotlib` & `pylatexenc` (for circuit visualisation)

---

## Running the Engine

### Quantum GUI Mode (Recommended)

```bash
python main.py --mode quantum_gui
```
Play standard 8x8 chess against the GPU-accelerated Hybrid Quantum Engine. Features smooth piece animation, real-time FPS, and full standard move validation.

### Generate 33-Qubit Academic Circuit
```bash
python generate_complete_circuit.py
```
Outputs `complete_qiskit_circuit.png`, proving that the academic logic scales to an 8x8 board.

### Run 3x3 Pure Quantum Demo
```bash
python demo_3x3_pure_quantum.py
```
Executes the base paper's 3x3 prototype (19 Qubits) entirely via pure quantum statevector simulation.

---

## References

1. **Design of Quantum Circuits to Play Chess in a Quantum Computer** - The base paper implementing 3x3 chess on quantum circuits using coordinate/status qubit encoding, direction detection, status extraction, and board state update circuits.
2. **A Fast Quantum Mechanical Algorithm for Database Search (Grover, 1996)** - The original Grover's algorithm paper providing $O(\sqrt{N})$ unstructured search, applied here to amplify optimal chess moves from the candidate space.

---

## License

This project is intended for academic research and educational purposes.
