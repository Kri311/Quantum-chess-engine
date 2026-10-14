# 3×3 Classical, Pure Quantum, and Hybrid System Comparison

## What is compared

The same 4 fixed 3×3 chess positions were used for each system. The benchmark seed is `20261013`. The classical system selects a move with depth-3 minimax. The pure quantum system builds and simulates the 23-qubit pure-circuit path for a fixed legal move, using one shot per position. The hybrid system prepares and ranks legal moves classically, then runs the project's Grover move-index circuit with 2048 shots per position. Both quantum circuits use the Qiskit Aer CPU matrix-product-state simulator with noise disabled.

The pure-circuit path demonstrates quantum move processing; it does not choose its move autonomously. In the hybrid path, the legal list and heuristic-best indices are classically prepared before Grover runs. This is a small educational simulator comparison, not evidence of quantum speedup.

## Metrics

- **Average execution time (ms):** average time for each system's measured operation. Classical timing covers move selection; pure quantum timing covers circuit construction and simulation; hybrid timing covers candidate scoring, Grover circuit construction, transpilation, and simulation. Simulator setup is excluded.
- **Extra peak RAM (MB):** average increase in process resident memory above the amount used immediately before each selection step, sampled every 2 ms. This estimates the extra working memory during a step; it is approximate because the sampler can miss very brief peaks.
- **Average legal moves:** average number of legal candidate moves in the tested positions. This gives context for the size of each selection task.
- **Qubits:** number of qubits in the circuit. Classical selection has no quantum circuit, so the result is N/A.
- **Gates and circuit depth:** gate count is the number of operations in the circuit; depth is the number of sequential gate layers. These are reported for the pure and hybrid quantum circuits.

Execution times depend on the computer and simulator and should be read as measurements from this run. They are not directly comparable to execution on a real quantum processor.

## Results

![3×3 classical, pure quantum, and hybrid systems compared by execution time, RAM, and circuit resources](../../evaluation/results/3x3_comparison.png)

| System | Avg. time (ms) | Extra peak RAM (MB) | Avg. legal moves | Qubits | Gates | Circuit depth |
|---|---:|---:|---:|---:|---:|---:|
| 3×3 Classical | 1.19 | 0.01 | 2.25 | N/A | N/A | N/A |
| 3×3 Pure Quantum | 95.81 | 5.19 | 2.25 | 23.00 | 102.00 | 32.25 |
| 3×3 Hybrid Quantum-Classical | 71.74 | 0.04 | 2.25 | 2.25 | 13.75 | 10.25 |

## How to explain the comparison

The classical system reports the time and extra RAM needed to select a move. The pure quantum system reports the circuit resources and simulation cost for processing a specified legal move. The hybrid system reports its end-to-end candidate-scoring and Grover simulation cost. Classical selection has no quantum circuit, so its qubit, gate, and depth entries are N/A. The number of legal moves describes the typical input size.

The pure-circuit demo does not autonomously choose a move, and the hybrid Grover path uses classical preprocessing. The evaluation shows basic runtime and circuit resource measurements; it does not prove quantum speedup or compare move quality.

## Generated files

- `3x3_comparison.png`: four panels compare execution time, extra peak RAM, qubits, and circuit gate count. The systems are on the x-axis and each panel's metric is on the y-axis.
- `3x3_comparison_summary.csv`: one row per system with average metrics.
- `3x3_comparison_positions.csv`: simple measurements for each position.
