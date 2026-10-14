"""Simple project-level 3×3 classical and quantum system comparison.

Run from any directory with:
    python evaluation/compare_3x3_systems.py

The benchmark compares the 3×3 classical selector, the 3×3 pure quantum
move-execution circuit, and the project's hybrid quantum-classical selector.
It reports average runtime and simple circuit resources. Results are a
simulator study, not evidence of quantum speedup.
"""

from __future__ import annotations

import csv
import os
import random
import sys
import tempfile
import threading
import time
from pathlib import Path

import psutil

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(tempfile.gettempdir()) / "quantum_chess_engine_matplotlib"),
)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from qiskit import transpile
from qiskit_aer import AerSimulator

from ai.classical_3x3 import Classical3x3Engine
from ai.heuristic import HeuristicEvaluator
from engine.board import Board
from engine.constants import Color, PieceType
from engine.move_generator import MoveGenerator
from engine.piece import Piece
from engine.position import Position
from engine.state import GameState
from quantum.grover import GroverSearch
from quantum.simulator import QuantumSimulator
from pure_quantum_engine.circuit import PureQuantumCircuitBuilder


BOARD_SIZE = 3
POSITION_COUNT = 4
BASE_SEED = 20261013
SHOT_COUNT = 2048
MINIMAX_DEPTH = 3
RESULTS_DIR = PROJECT_ROOT / "evaluation" / "results"

SYSTEM_ORDER = (
    "3×3 Classical",
    "3×3 Pure Quantum",
    "3×3 Hybrid Quantum-Classical",
)


def _state_from_layout(
    layout: list[tuple[int, int, Color, PieceType]],
    turn: Color,
) -> GameState:
    board = Board(size=BOARD_SIZE)
    for row, col, color, piece_type in layout:
        board.place_piece(Position(row, col), Piece(color, piece_type))
    return GameState(board=board, current_turn=turn)


def build_positions(
    count: int = POSITION_COUNT,
    seed: int = BASE_SEED,
) -> list[GameState]:
    """Create unique benchmark positions using seeded legal random walks."""
    if count < 1:
        raise ValueError("count must be at least one")

    layouts = [
        [
            (2, 1, Color.WHITE, PieceType.KNIGHT),
            (0, 0, Color.BLACK, PieceType.PAWN),
        ],
        [
            (2, 1, Color.WHITE, PieceType.PAWN),
            (1, 0, Color.BLACK, PieceType.PAWN),
            (0, 2, Color.BLACK, PieceType.KNIGHT),
        ],
        [
            (2, 0, Color.WHITE, PieceType.PAWN),
            (2, 2, Color.WHITE, PieceType.KNIGHT),
            (0, 0, Color.BLACK, PieceType.PAWN),
            (0, 2, Color.BLACK, PieceType.KNIGHT),
        ],
        [
            (2, 1, Color.WHITE, PieceType.KNIGHT),
            (1, 0, Color.WHITE, PieceType.PAWN),
            (0, 1, Color.BLACK, PieceType.KNIGHT),
            (0, 2, Color.BLACK, PieceType.PAWN),
        ],
    ]
    rng = random.Random(seed)
    positions: list[GameState] = []
    seen: set[tuple] = set()
    max_steps_per_layout = count * 8

    for layout in layouts:
        state = _state_from_layout(layout, Color.WHITE)
        for _ in range(max_steps_per_layout):
            key = _state_key(state)
            legal_moves = MoveGenerator.generate_legal_moves(state)
            if len(legal_moves) >= 2 and key not in seen:
                positions.append(state)
                seen.add(key)
                if len(positions) >= count:
                    return positions

            # End this walk if either side has no remaining pieces or moves.
            if not legal_moves or state.is_terminal():
                break
            state = state.apply_move(rng.choice(legal_moves))

    # Fill any remaining slots by continuing seeded random walks from the
    # layouts. This fallback is bounded and fails clearly if the rules/data
    # cannot provide enough distinct decision positions.
    for restart in range(count * 4):
        state = _state_from_layout(layouts[restart % len(layouts)], Color.WHITE)
        for _ in range(max_steps_per_layout):
            key = _state_key(state)
            legal_moves = MoveGenerator.generate_legal_moves(state)
            if len(legal_moves) >= 2 and key not in seen:
                positions.append(state)
                seen.add(key)
                if len(positions) >= count:
                    return positions
            if not legal_moves or state.is_terminal():
                break
            state = state.apply_move(rng.choice(legal_moves))

    raise RuntimeError(
        f"Only generated {len(positions)} unique 3x3 positions with at least "
        f"two legal moves; requested {count}."
    )


def _state_key(state: GameState) -> tuple:
    pieces = tuple(
        sorted(
            (
                position.row,
                position.col,
                piece.color.name,
                piece.piece_type.name,
            )
            for position, piece in state.board.all_pieces.items()
        )
    )
    return state.current_turn.name, pieces


def _measurement_row(
    *,
    state_id: int,
    system: str,
    legal_count: int,
    elapsed_ms: float,
    peak_ram_mb: float,
    qubits: int | None = None,
    gates: int | None = None,
    depth: int | None = None,
) -> dict[str, object]:
    return {
        "position": state_id,
        "system": system,
        "legal_moves": legal_count,
        "execution_time_ms": elapsed_ms,
        "peak_ram_mb": peak_ram_mb,
        "qubits": qubits if qubits is not None else "",
        "gates": gates if gates is not None else "",
        "circuit_depth": depth if depth is not None else "",
    }


def _measure(action) -> tuple[float, float]:
    """Return elapsed milliseconds and sampled extra peak process RSS in MB."""
    process = psutil.Process()
    baseline_rss = process.memory_info().rss
    peak_rss = [baseline_rss]
    stop_sampling = threading.Event()

    def sample_memory() -> None:
        while not stop_sampling.wait(0.002):
            try:
                peak_rss[0] = max(peak_rss[0], process.memory_info().rss)
            except psutil.Error:
                return

    sampler = threading.Thread(target=sample_memory, daemon=True)
    sampler.start()
    start = time.perf_counter()
    try:
        action()
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        try:
            peak_rss[0] = max(peak_rss[0], process.memory_info().rss)
        except psutil.Error:
            pass
        stop_sampling.set()
        sampler.join()
    additional_peak_rss = max(0, peak_rss[0] - baseline_rss)
    return elapsed_ms, additional_peak_rss / (1024 * 1024)


def evaluate_positions(
    positions: list[GameState],
    *,
    shots: int = SHOT_COUNT,
    seed: int = BASE_SEED,
) -> list[dict[str, object]]:
    """Measure simple runtime and resource counts for each 3×3 system."""
    if shots < 1:
        raise ValueError("shots must be at least one")

    classical = Classical3x3Engine(max_depth=MINIMAX_DEPTH)
    pure_simulator = AerSimulator(method="matrix_product_state")
    hybrid_simulator = QuantumSimulator(shots=shots, noise_enabled=False, use_gpu=False)
    hybrid_backend = AerSimulator(method="matrix_product_state")
    grover = GroverSearch(simulator=hybrid_simulator)
    rows: list[dict[str, object]] = []

    for state_id, state in enumerate(positions, start=1):
        legal_moves = MoveGenerator.generate_legal_moves(state)
        if len(legal_moves) < 2:
            raise ValueError(f"Position {state_id} has fewer than two legal moves")

        classical_ms, classical_ram = _measure(lambda: classical.select_move(state))
        rows.append(
            _measurement_row(
                state_id=state_id,
                system=SYSTEM_ORDER[0],
                legal_count=len(legal_moves),
                elapsed_ms=classical_ms,
                peak_ram_mb=classical_ram,
            )
        )

        # The pure 3×3 circuit executes one given legal move transition. The
        # first legal move makes that input deterministic across benchmark runs.
        pure_move = legal_moves[0]
        pure_circuit = None

        def run_pure_circuit() -> None:
            nonlocal pure_circuit
            pure_circuit, _ = PureQuantumCircuitBuilder.build_full_chess_circuit(
                state=state,
                source=pure_move.start,
                target=pure_move.end,
                color=state.current_turn,
            )
            compiled = transpile(pure_circuit, pure_simulator, optimization_level=1)
            pure_simulator.run(
                compiled,
                shots=1,
                seed_simulator=seed + state_id,
            ).result()

        pure_ms, pure_ram = _measure(run_pure_circuit)
        rows.append(
            _measurement_row(
                state_id=state_id,
                system=SYSTEM_ORDER[1],
                legal_count=len(legal_moves),
                elapsed_ms=pure_ms,
                peak_ram_mb=pure_ram,
                qubits=pure_circuit.num_qubits,
                gates=pure_circuit.size(),
                depth=pure_circuit.depth(),
            )
        )

        hybrid_moves = []
        circuit_qubits = circuit_gates = circuit_depth = None
        def run_hybrid_circuit() -> None:
            nonlocal hybrid_moves, circuit_qubits, circuit_gates, circuit_depth
            hybrid_moves = MoveGenerator.generate_legal_moves(state)
            hybrid_scores = [
                HeuristicEvaluator.score_move(state, move) for move in hybrid_moves
            ]
            hybrid_best = max(hybrid_scores)
            hybrid_targets = [
                i for i, score in enumerate(hybrid_scores) if score == hybrid_best
            ]
            if len(hybrid_targets) == len(hybrid_moves):
                # Equal scores require no Grover circuit.
                return
            n_move_qubits = max(1, (len(hybrid_moves) - 1).bit_length())
            search_space = 1 << n_move_qubits
            iterations = grover.calculate_iterations(search_space, len(hybrid_targets))
            circuit = grover._build_grover_circuit(
                n_move_qubits,
                hybrid_targets,
                iterations,
            )
            compiled = transpile(circuit, hybrid_backend, optimization_level=1)
            hybrid_backend.run(
                compiled,
                shots=shots,
                seed_simulator=seed + state_id,
            ).result()
            circuit_qubits = circuit.num_qubits
            circuit_gates = circuit.size()
            circuit_depth = circuit.depth()
        hybrid_ms, hybrid_ram = _measure(run_hybrid_circuit)
        rows.append(
            _measurement_row(
                state_id=state_id,
                system=SYSTEM_ORDER[2],
                legal_count=len(hybrid_moves),
                elapsed_ms=hybrid_ms,
                peak_ram_mb=hybrid_ram,
                qubits=circuit_qubits,
                gates=circuit_gates,
                depth=circuit_depth,
            )
        )

    return rows


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    summaries: list[dict[str, object]] = []
    for system in SYSTEM_ORDER:
        group = [row for row in rows if row["system"] == system]
        if not group:
            continue
        summaries.append(
            {
                "system": system,
                "positions": len(group),
                "average_legal_moves": sum(
                    float(row["legal_moves"]) for row in group
                ) / len(group),
                "average_execution_time_ms": sum(
                    float(row["execution_time_ms"]) for row in group
                )
                / len(group),
                "average_peak_ram_mb": sum(
                    float(row["peak_ram_mb"]) for row in group
                ) / len(group),
                "average_qubits": _mean_optional(group, "qubits"),
                "average_gates": _mean_optional(group, "gates"),
                "average_circuit_depth": _mean_optional(group, "circuit_depth"),
            }
        )
    return summaries


def _mean_optional(rows: list[dict[str, object]], key: str) -> float | str:
    values = [float(row[key]) for row in rows if row[key] != ""]
    return sum(values) / len(values) if values else "N/A"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Cannot write an empty results table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_summary(summaries: list[dict[str, object]], path: Path) -> None:
    label_map = {
        SYSTEM_ORDER[0]: "Classical",
        SYSTEM_ORDER[1]: "Pure quantum",
        SYSTEM_ORDER[2]: "Hybrid\nquantum-classical",
    }
    labels = [label_map[str(row["system"])] for row in summaries]
    colors = ["#36688D", "#5AAE8A", "#9467BD"]
    x = list(range(len(labels)))
    fig, axes = plt.subplots(1, 4, figsize=(18, 6.5))
    fig.suptitle(
        "3×3 System Comparison by Runtime and Resources",
        fontsize=13,
        fontweight="bold",
    )

    metrics = [
        ("average_execution_time_ms", "Execution time (ms)"),
        ("average_peak_ram_mb", "Extra peak RAM (MB)"),
        ("average_qubits", "Qubits"),
        ("average_gates", "Circuit gates"),
    ]
    for axis, (key, title) in zip(axes, metrics):
        raw_values = [row[key] for row in summaries]
        values = [float(value) if value != "N/A" else 0 for value in raw_values]
        bars = axis.bar(x, values, color=colors[: len(values)], width=0.68)
        axis.set_title(title)
        axis.set_xticks(x, labels)
        axis.set_ylim(bottom=0)
        axis.grid(axis="y", alpha=0.25)
        axis.set_axisbelow(True)
        max_value = max(values, default=0)
        for bar, value, raw_value in zip(bars, values, raw_values):
            label = f"{value:.2f}" if raw_value != "N/A" else "N/A"
            axis.annotate(
                label,
                (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )
        axis.set_ylim(top=max_value * 1.25 if max_value else 1)
        axis.set_ylabel(title)
    fig.text(
        0.5,
        0.025,
        "Systems are on the x-axis. RAM is extra peak RSS above the run's starting process memory. N/A means that system has no quantum circuit.",
        ha="center",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.91))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def write_summary_report(
    path: Path,
    summaries: list[dict[str, object]],
    position_count: int,
    seed: int,
    shots: int,
) -> None:
    lines = [
        "# 3×3 Classical, Pure Quantum, and Hybrid System Comparison",
        "",
        "## What is compared",
        "",
        f"The same {position_count} fixed 3×3 chess positions were used for each system. The benchmark seed is `{seed}`. The classical system selects a move with depth-{MINIMAX_DEPTH} minimax. The pure quantum system builds and simulates the 23-qubit pure-circuit path for a fixed legal move, using one shot per position. The hybrid system prepares and ranks legal moves classically, then runs the project's Grover move-index circuit with {shots} shots per position. Both quantum circuits use the Qiskit Aer CPU matrix-product-state simulator with noise disabled.",
        "",
        "The pure-circuit path demonstrates quantum move processing; it does not choose its move autonomously. In the hybrid path, the legal list and heuristic-best indices are classically prepared before Grover runs. This is a small educational simulator comparison, not evidence of quantum speedup.",
        "",
        "## Metrics",
        "",
        "- **Average execution time (ms):** average time for each system's measured operation. Classical timing covers move selection; pure quantum timing covers circuit construction and simulation; hybrid timing covers candidate scoring, Grover circuit construction, transpilation, and simulation. Simulator setup is excluded.",
        "- **Extra peak RAM (MB):** average increase in process resident memory above the amount used immediately before each selection step, sampled every 2 ms. This estimates the extra working memory during a step; it is approximate because the sampler can miss very brief peaks.",
        "- **Average legal moves:** average number of legal candidate moves in the tested positions. This gives context for the size of each selection task.",
        "- **Qubits:** number of qubits in the circuit. Classical selection has no quantum circuit, so the result is N/A.",
        "- **Gates and circuit depth:** gate count is the number of operations in the circuit; depth is the number of sequential gate layers. These are reported for the pure and hybrid quantum circuits.",
        "",
        "Execution times depend on the computer and simulator and should be read as measurements from this run. They are not directly comparable to execution on a real quantum processor.",
        "",
        "## Results",
        "",
        "![3×3 classical, pure quantum, and hybrid systems compared by execution time, RAM, and circuit resources](../../evaluation/results/3x3_comparison.png)",
        "",
        "| System | Avg. time (ms) | Extra peak RAM (MB) | Avg. legal moves | Qubits | Gates | Circuit depth |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summaries:
        fmt = lambda key: (
            f"{float(row[key]):.2f}" if row[key] != "N/A" else "N/A"
        )
        lines.append(
            "| {system} | {time} | {ram} | {moves} | {qubits} | {gates} | {depth} |".format(
                system=row["system"],
                time=fmt("average_execution_time_ms"),
                ram=fmt("average_peak_ram_mb"),
                moves=fmt("average_legal_moves"),
                qubits=fmt("average_qubits"),
                gates=fmt("average_gates"),
                depth=fmt("average_circuit_depth"),
            )
        )
    lines.extend(
        [
            "",
            "## How to explain the comparison",
            "",
            "The classical system reports the time and extra RAM needed to select a move. The pure quantum system reports the circuit resources and simulation cost for processing a specified legal move. The hybrid system reports its end-to-end candidate-scoring and Grover simulation cost. Classical selection has no quantum circuit, so its qubit, gate, and depth entries are N/A. The number of legal moves describes the typical input size.",
            "",
            "The pure-circuit demo does not autonomously choose a move, and the hybrid Grover path uses classical preprocessing. The evaluation shows basic runtime and circuit resource measurements; it does not prove quantum speedup or compare move quality.",
            "",
            "## Generated files",
            "",
            "- `3x3_comparison.png`: four panels compare execution time, extra peak RAM, qubits, and circuit gate count. The systems are on the x-axis and each panel's metric is on the y-axis.",
            "- `3x3_comparison_summary.csv`: one row per system with average metrics.",
            "- `3x3_comparison_positions.csv`: simple measurements for each position.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_comparison(
    *,
    position_count: int = POSITION_COUNT,
    shots: int = SHOT_COUNT,
    seed: int = BASE_SEED,
) -> list[dict[str, object]]:
    positions = build_positions(position_count, seed)
    rows = evaluate_positions(positions, shots=shots, seed=seed)
    summaries = summarize(rows)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(RESULTS_DIR / "3x3_comparison_positions.csv", rows)
    write_csv(RESULTS_DIR / "3x3_comparison_summary.csv", summaries)
    plot_summary(summaries, RESULTS_DIR / "3x3_comparison.png")
    write_summary_report(
        PROJECT_ROOT / "docs" / "reports" / "3x3_system_comparison.md",
        summaries,
        len(positions),
        seed,
        shots,
    )
    return summaries


def main() -> None:
    summaries = run_comparison()
    position_count = int(summaries[0]["positions"]) if summaries else 0
    print(f"3x3 comparison complete: {position_count} fixed positions")
    for row in summaries:
        print(
            "{system}: time={time:.3f} ms, peak_ram={ram:.1f} MB, "
            "legal_moves={moves:.1f}, qubits={qubits}, gates={gates}, depth={depth}".format(
                system=row["system"],
                time=float(row["average_execution_time_ms"]),
                ram=float(row["average_peak_ram_mb"]),
                moves=float(row["average_legal_moves"]),
                qubits=row["average_qubits"],
                gates=row["average_gates"],
                depth=row["average_circuit_depth"],
            )
        )
    print(f"Artifacts written to {RESULTS_DIR}")


if __name__ == "__main__":
    main()
