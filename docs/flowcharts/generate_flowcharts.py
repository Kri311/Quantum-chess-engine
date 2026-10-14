#!/usr/bin/env python3
"""Generate connected Quantum Chess Engine flowcharts as PNG and SVG.

Run from any directory:
    python docs/flowcharts/generate_flowcharts.py

The diagrams use Matplotlib only. They are explanatory architecture drawings,
not runtime-generated traces; keep labels synchronized with the implementation.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
import tempfile
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = Path(__file__).resolve().parent / "generated"
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "quantum_chess_flowchart_mplcache"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle


COLORS = {
    "navy": "#18324B",
    "blue": "#E8F1FA",
    "green": "#E8F4EC",
    "gold": "#FFF2D7",
    "purple": "#EEE9F8",
    "gray": "#F1F3F5",
    "red": "#FBE9E7",
    "teal": "#E3F3F2",
    "ink": "#23313D",
    "muted": "#52616F",
    "line": "#526B80",
    "white": "#FFFFFF",
}


@dataclass
class Box:
    key: str
    x: float
    y: float
    w: float
    h: float
    title: str
    body: str
    color: str = "blue"
    title_color: str = "navy"
    patch: FancyBboxPatch | None = None


def make_box(key: str, x: float, y: float, w: float, h: float, title: str,
             body: str = "", color: str = "blue") -> Box:
    return Box(key, x, y, w, h, title, body, color)


def render_chart(
    filename: str,
    title: str,
    subtitle: str,
    boxes: Iterable[Box],
    edges: list[tuple[str, str, str | None]],
    *,
    width: float = 18,
    height: float = 12,
    footnote: str = "",
    section_bands: list[tuple[float, float, float, float, str, str]] | None = None,
) -> None:
    """Draw a diagram with boxes and automatically clipped connecting arrows."""
    fig, ax = plt.subplots(figsize=(width, height), facecolor=COLORS["white"])
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 14)
    ax.axis("off")
    ax.set_facecolor(COLORS["white"])

    if section_bands:
        for x, y, w, h, label, color in section_bands:
            band = Rectangle((x, y), w, h, facecolor=color, edgecolor="none", zorder=0)
            ax.add_patch(band)
            ax.text(x + 0.25, y + h - 0.28, label.upper(), fontsize=9,
                    color=COLORS["muted"], weight="bold", va="top", zorder=1)

    ax.text(0.55, 13.52, title, fontsize=20, weight="bold", color=COLORS["navy"], va="top")
    ax.text(0.57, 13.08, subtitle, fontsize=10.5, color=COLORS["muted"], va="top")

    box_map = {box.key: box for box in boxes}
    for source, target, label in edges:
        a, b = box_map[source], box_map[target]
        arrow = FancyArrowPatch(
            (a.x, a.y), (b.x, b.y),
            patchA=a.patch, patchB=b.patch,
            arrowstyle="-|>", mutation_scale=13,
            linewidth=1.45, color=COLORS["line"],
            connectionstyle="arc3,rad=0.0", zorder=2,
        )
        ax.add_patch(arrow)
        if label:
            mx, my = (a.x + b.x) / 2, (a.y + b.y) / 2
            ax.text(mx, my + 0.12, label, fontsize=7.2, color=COLORS["muted"],
                    ha="center", va="center",
                    bbox={"boxstyle": "round,pad=0.16", "facecolor": "white",
                          "edgecolor": "none", "alpha": 0.92}, zorder=4)

    for box in boxes:
        patch = FancyBboxPatch(
            (box.x - box.w / 2, box.y - box.h / 2), box.w, box.h,
            boxstyle="round,pad=0.03,rounding_size=0.13",
            linewidth=1.2, edgecolor=COLORS["navy"],
            facecolor=COLORS[box.color], zorder=3,
        )
        box.patch = patch
        ax.add_patch(patch)
        title_color = COLORS["white"] if box.color == "navy" else box.title_color
        body_color = COLORS["white"] if box.color == "navy" else COLORS["ink"]
        if box.body:
            ax.text(box.x, box.y + box.h * 0.19, box.title, fontsize=9.4,
                    color=title_color, weight="bold", ha="center", va="center", zorder=5)
            ax.text(box.x, box.y - box.h * 0.16, box.body, fontsize=7.8,
                    color=body_color, ha="center", va="center", linespacing=1.2, zorder=5)
        else:
            ax.text(box.x, box.y, box.title, fontsize=9.0, color=title_color,
                    weight="bold", ha="center", va="center", zorder=5, wrap=True)

    if footnote:
        ax.text(0.58, 0.32, footnote, fontsize=8.2, color=COLORS["muted"],
                ha="left", va="bottom", wrap=True)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    png = OUTPUT_DIR / f"{filename}.png"
    svg = OUTPUT_DIR / f"{filename}.svg"
    fig.savefig(png, dpi=190, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(svg, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Wrote {png.relative_to(PROJECT_ROOT)}")
    print(f"Wrote {svg.relative_to(PROJECT_ROOT)}")


def project_map() -> None:
    boxes = [
        make_box("entry", 10, 12.1, 5.0, 0.9, "main.py + config.py",
                 "Menu routes, board layouts, simulator defaults", "navy"),
        make_box("hybrid", 2.65, 9.55, 4.0, 1.0, "8×8 hybrid • option 1",
                 "GUI game with quantum-assisted AI", "navy"),
        make_box("small", 7.55, 9.55, 4.0, 1.0, "3×3 / 2×2 • options 2, 6, 7",
                 "Pure-circuit and pawn demonstrations", "navy"),
        make_box("diagram", 12.45, 9.55, 4.0, 1.0, "Circuit diagrams • options 3–5",
                 "Construct 8×8, 3×3, or 2×2 circuit", "navy"),
        make_box("bench", 17.35, 9.55, 4.0, 1.0, "3×3 comparison • CLI",
                 "Compare three implemented systems", "navy"),

        make_box("h2", 2.65, 7.55, 4.0, 1.0, "Classical engine + AI",
                 "GameState → legal moves → heuristic targets", "green"),
        make_box("h3", 2.65, 5.55, 4.0, 1.0, "Grover index search",
                 "Oracle + diffuser → Aer sample → decode Move", "purple"),
        make_box("h4", 2.65, 3.55, 4.0, 1.0, "Classical move update",
                 "Validate and apply selected Move", "green"),
        make_box("s2", 7.55, 7.55, 4.0, 1.0, "Shared classical game model",
                 "GameState, legal moves, manual input / minimax", "green"),
        make_box("s3", 7.55, 5.55, 4.0, 1.0, "Pure-circuit builder",
                 "Process selected move with coordinate/status gates", "purple"),
        make_box("s4", 7.55, 3.55, 4.0, 1.0, "Aer measurement",
                 "One-shot diagnostic output", "teal"),
        make_box("s5", 7.55, 1.55, 4.0, 1.0, "Classical state update",
                 "Options 2/6 apply Move; option 7 does not", "green"),
        make_box("d2", 12.45, 7.55, 4.0, 1.0, "Build circuit input",
                 "Configured state + selected source/target", "blue"),
        make_box("d3", 12.45, 5.55, 4.0, 1.0, "Shared pure-circuit builder",
                 "Allocate registers; append gates; measure", "purple"),
        make_box("d4", 12.45, 3.55, 4.0, 1.0, "Simulate small boards; draw all",
                 "2×2/3×3 simulate; 8×8 diagram skips simulation", "teal"),
        make_box("d5", 12.45, 1.55, 4.0, 1.0, "Save circuit image",
                 "docs/assets/diagrams/architecture_*.png", "gray"),
        make_box("b2", 17.35, 7.55, 4.0, 1.0, "Build four seeded positions",
                 "Same test inputs for each system", "blue"),
        make_box("b3", 17.35, 5.55, 4.0, 1.0, "Run three branches",
                 "Classical minimax • pure circuit • hybrid Grover", "gold"),
        make_box("b4", 17.35, 3.55, 4.0, 1.0, "Collect simple metrics",
                 "Time • extra RAM • qubits • gates • depth", "teal"),
        make_box("b5", 17.35, 1.55, 4.0, 1.0, "Write outputs",
                 "CSV tables • graph • Markdown report", "gray"),
    ]
    edges = [
        ("entry", "hybrid", None), ("entry", "small", None),
        ("entry", "diagram", None), ("entry", "bench", None),
        ("hybrid", "h2", None), ("h2", "h3", None), ("h3", "h4", None),
        ("small", "s2", None), ("s2", "s3", None), ("s3", "s4", None), ("s4", "s5", None),
        ("diagram", "d2", None), ("d2", "d3", None), ("d3", "d4", None), ("d4", "d5", None),
        ("bench", "b2", None), ("b2", "b3", None), ("b3", "b4", None), ("b4", "b5", None),
    ]
    render_chart(
        "01_complete_project_map",
        "Quantum Chess Engine | Connected implementation flowchart",
        "The main menu branches into four implementations; each lane follows its data to the result.",
        boxes, edges, width=20, height=14,
        section_bands=[
            (0.35, 0.75, 4.6, 9.75, "", "#F7FAFD"),
            (5.25, 0.75, 4.6, 9.75, "", "#FBF9FE"),
            (10.15, 0.75, 4.6, 9.75, "", "#F7FAFD"),
            (15.05, 0.75, 4.6, 9.75, "", "#F7FAFD"),
        ],
        footnote=("Key boundary: the game board and legal moves stay classical. Small-board circuits process supplied moves; "
                  "hybrid Grover samples indices from classical scores. Option 7 currently skips Grover circuit construction; see the detailed route chart."),
    )


def gameplay_routes() -> None:
    boxes = [
        make_box("lane8", 2.5, 12.2, 4.35, 0.75, "8×8 HYBRID · OPTION 1", "", "navy"),
        make_box("h1", 2.5, 10.65, 4.35, 1.0, "GUI + GameState", "Human White; AI Black; classical board", "blue"),
        make_box("h2", 2.5, 9.15, 4.35, 1.0, "Generate and score", "Legal moves → heuristic target indices", "green"),
        make_box("h3", 2.5, 7.65, 4.35, 1.0, "Grover + Aer", "Oracle → diffuser → sample index", "purple"),
        make_box("h4", 2.5, 6.15, 4.35, 1.0, "Decode and validate", "Return target Move; fallback if needed", "gold"),
        make_box("h5", 2.5, 4.65, 4.35, 1.0, "Apply and repeat", "Game.make_move updates classical state", "green"),

        make_box("lane3", 7.5, 12.2, 4.35, 0.75, "3×3 PURE GAME · OPTION 2", "", "navy"),
        make_box("p1", 7.5, 10.65, 4.35, 1.0, "Human + classical AI", "Player move; Black AI uses minimax", "blue"),
        make_box("p2", 7.5, 9.15, 4.35, 1.0, "PureQuantumGame", "Build circuit for each selected Move", "purple"),
        make_box("p3", 7.5, 7.65, 4.35, 1.0, "Aer one-shot run", "Print qubits, depth, time, measurement", "teal"),
        make_box("p4", 7.5, 6.15, 4.35, 1.0, "Classical state update", "Parent Game applies the original Move", "green"),

        make_box("lane6", 12.5, 12.2, 4.35, 0.75, "2×2 INTERACTIVE · OPTION 6", "", "navy"),
        make_box("i1", 12.5, 10.65, 4.35, 1.0, "Manual pawn move", "One Black Pawn; no AI engine", "blue"),
        make_box("i2", 12.5, 9.15, 4.35, 1.0, "Build and simulate", "Pure circuit; Aer; one shot", "purple"),
        make_box("i3", 12.5, 7.65, 4.35, 1.0, "Show measurement", "Circuit metrics and diagnostic string", "teal"),
        make_box("i4", 12.5, 6.15, 4.35, 1.0, "Apply classical Move", "Parent Game validates and updates board", "green"),

        make_box("lane7", 17.5, 12.2, 4.35, 0.75, "2×2 AUTONOMOUS · OPTION 7", "", "navy"),
        make_box("g1", 17.5, 10.65, 4.35, 1.0, "Call GroverSearch", "Default candidate list contains legal moves", "gold"),
        make_box("g2", 17.5, 9.15, 4.35, 1.0, "All-target shortcut", "Returns first candidate; no Grover circuit", "red"),
        make_box("g3", 17.5, 7.65, 4.35, 1.0, "Pure circuit runs", "Aer one-shot; prints and saves diagram", "purple"),
        make_box("g4", 17.5, 6.15, 4.35, 1.0, "No game-state update", "Option 7 does not call Game.make_move", "gray"),
    ]
    edges = [("lane8", "h1", None), ("h1", "h2", None), ("h2", "h3", None),
             ("h3", "h4", None), ("h4", "h5", None),
             ("lane3", "p1", None), ("p1", "p2", None),
             ("p2", "p3", None), ("p3", "p4", "measurement is diagnostic"),
             ("lane6", "i1", None), ("i1", "i2", None), ("i2", "i3", None), ("i3", "i4", None),
             ("lane7", "g1", None), ("g1", "g2", None), ("g2", "g3", None), ("g3", "g4", None)]
    render_chart(
        "02_gameplay_implementation_routes",
        "Gameplay routes | What each mode actually does",
        "Four separate routes; the 3×3 and interactive 2×2 modes apply moves through the classical game model.",
        boxes, edges, width=22, height=14,
        footnote=("3×3 AI uses classical minimax. Option 6 applies moves through Game.make_move after circuit diagnostics. "
                  "Option 7 currently runs the pure circuit after returning the first candidate; it skips Grover circuit execution."),
    )


def circuit_paths() -> None:
    boxes = [
        make_box("input", 10, 12.2, 5.2, 0.9, "Classical input", "GameState + a supplied move, or best move indices", "green"),
        make_box("purein", 4.1, 10.1, 5.4, 1.0, "Small-board pure circuit", "Source/target coordinates + classical square lookup", "purple"),
        make_box("groverin", 15.9, 10.1, 5.4, 1.0, "Hybrid Grover circuit", "Index register + phase-kickback flag", "purple"),
        make_box("preg", 4.1, 7.95, 5.4, 1.0, "Allocate registers", "2×2 / 3×3: 23 qubits; 8×8 diagram: 33", "blue"),
        make_box("gates", 4.1, 5.85, 5.4, 1.0, "Encode and compute", "X initialize; MCX lookup; limited direction/status logic", "gold"),
        make_box("gprep", 15.9, 7.95, 5.4, 1.0, "Prepare search", "H superposition; X+H flag to |−⟩", "blue"),
        make_box("goracle", 15.9, 5.85, 5.4, 1.0, "Oracle + diffuser", "Phase mark targets; reflect amplitudes; repeat", "gold"),
        make_box("simulate", 10, 3.55, 6.2, 1.05, "Aer simulator + measurement", "Pure circuit: diagnostic bit string • Grover: sampled move index", "teal"),
        make_box("decode", 15.2, 1.35, 5.7, 1.0, "Hybrid index decode", "Map sampled integer to candidate Move; fallback if needed", "green"),
        make_box("diag", 4.8, 1.35, 6.0, 1.0, "Pure-circuit diagnostic", "Reports register output; does not update a complete quantum board", "gray"),
    ]
    edges = [("input", "purein", "selected Move"), ("input", "groverin", "classical target indices"),
             ("purein", "preg", None), ("preg", "gates", None), ("gates", "simulate", None),
             ("groverin", "gprep", None), ("gprep", "goracle", None),
             ("goracle", "simulate", None), ("simulate", "diag", "pure route"),
             ("simulate", "decode", "Grover route")]
    render_chart(
        "03_quantum_circuit_paths",
        "Quantum paths | Two different circuit jobs",
        "The board-transition prototype and hybrid move-index search do not encode the same data.",
        boxes, edges, width=20, height=13,
        footnote=("Small-board status values are compact and not fully unique; direction and status transformations are incomplete prototypes. "
                  "All paths run on a simulator in this project."),
    )


def benchmark_flow() -> None:
    boxes = [
        make_box("start", 10, 12.0, 5.3, 0.9, "Run comparison script", "evaluation/compare_3x3_systems.py", "navy"),
        make_box("positions", 10, 10.1, 5.3, 0.9, "Build shared inputs", "Four seeded 3×3 positions; legal move count recorded", "blue"),
        make_box("classical", 3.2, 7.55, 5.6, 1.1, "3×3 Classical", "Depth-3 minimax selects a move\nMeasure time + sampled extra RAM", "green"),
        make_box("pure", 10, 7.55, 5.6, 1.1, "3×3 Pure Quantum", "First legal move is supplied\nBuild 23-qubit circuit; one shot", "purple"),
        make_box("hybrid", 16.8, 7.55, 5.6, 1.1, "3×3 Hybrid", "Score moves classically\nGrover on best indices; 2048 shots", "gold"),
        make_box("mclass", 3.2, 5.2, 5.6, 0.95, "Circuit fields: N/A", "Classical branch constructs no circuit", "gray"),
        make_box("mpure", 10, 5.2, 5.6, 0.95, "Circuit fields measured", "Qubits • gates • depth • time • RAM", "teal"),
        make_box("mhybrid", 16.8, 5.2, 5.6, 0.95, "Circuit fields measured", "Qubits • gates • depth • time • RAM", "teal"),
        make_box("aggregate", 10, 3.0, 6.2, 0.9, "Aggregate over positions", "Average basic system metrics", "blue"),
        make_box("files", 10, 1.2, 7.4, 0.9, "Write results", "PNG graph + summary/per-position CSV + Markdown report", "green"),
    ]
    edges = [("start", "positions", None), ("positions", "classical", None),
             ("positions", "pure", None), ("positions", "hybrid", None),
             ("classical", "mclass", None), ("pure", "mpure", None),
             ("hybrid", "mhybrid", None), ("mclass", "aggregate", None),
             ("mpure", "aggregate", None), ("mhybrid", "aggregate", None),
             ("aggregate", "files", None)]
    render_chart(
        "04_3x3_benchmark_flow",
        "Evaluation flow | Three 3×3 systems, simple metrics",
        "The same four positions feed three distinct measured operations; results are local simulator measurements.",
        boxes, edges, width=19, height=13,
        footnote=("The tasks differ: classical chooses a move, pure quantum processes a supplied move, and hybrid runs classical scoring plus Grover simulation. "
                  "This is a resource comparison, not a move-quality or quantum-speedup evaluation."),
    )


def three_by_three_move_to_circuit() -> None:
    """Show the classical move-index/Grover path and pure-circuit path together.

    The connector between the two quantum paths is intentionally a software
    handoff: current gameplay does not feed pure-circuit measurement bits into
    the Grover indexer (or vice versa).
    """
    boxes = [
        make_box("board", 2.5, 11.5, 4.2, 1.0, "3×3 classical board",
                 "Pieces, side to move, GameState", "green"),
        make_box("moves", 7.3, 11.5, 4.2, 1.0, "Generate legal Moves",
                 "Rules inspect piece and destination squares", "green"),
        make_box("rank", 12.1, 11.5, 4.2, 1.0, "Score each candidate",
                 "HeuristicEvaluator runs classically", "gold"),
        make_box("indices", 17.0, 11.5, 4.4, 1.0, "Build target index list",
                 "Tie best Move(s) to integer indices", "gold"),

        make_box("indexreg", 17.0, 8.9, 4.4, 1.1, "Grover index register",
                 "n = ceil(log₂(candidate count)) qubits + 1 flag", "purple"),
        make_box("superposition", 12.1, 8.9, 4.2, 1.1, "Prepare search state",
                 "H on index; X then H makes flag |−⟩", "blue"),
        make_box("oracle", 7.3, 8.9, 4.2, 1.1, "Oracle phase marking",
                 "MCX matches target indices; kickback adds − phase", "purple"),
        make_box("diffuser", 2.5, 8.9, 4.2, 1.1, "Diffuser + measurement",
                 "Reflect amplitudes; Aer samples an index", "teal"),

        make_box("selected", 2.5, 6.25, 4.2, 1.0, "Decode selected index",
                 "Map integer back to the candidate Move", "green"),
        make_box("handoff", 7.3, 6.25, 4.2, 1.0, "Software handoff",
                 "Selected Move can be supplied to pure circuit\n(separate path; not an automatic circuit link)", "red"),
        make_box("coords", 12.1, 6.25, 4.2, 1.0, "Encode source + target",
                 "4 + 4 coordinate qubits; X sets 1 bits", "blue"),
        make_box("lookup", 17.0, 6.25, 4.4, 1.0, "Look up square statuses",
                 "Classical board lookup controls X/MCX gates", "gold"),

        make_box("logic", 17.0, 3.45, 4.4, 1.1, "Direction + status logic",
                 "CX, CCX, MCX and ancillas; prototype logic", "purple"),
        make_box("readout", 12.1, 3.45, 4.2, 1.1, "Measure 23-qubit circuit",
                 "Aer output is a diagnostic bit string", "teal"),
        make_box("apply", 7.3, 3.45, 4.2, 1.1, "Validate/apply Move",
                 "Classical Game updates the board", "green"),
        make_box("result", 2.5, 3.45, 4.2, 1.1, "Next classical position",
                 "Board state remains in GameState", "green"),
    ]
    edges = [
        ("board", "moves", None), ("moves", "rank", None),
        ("rank", "indices", None), ("indices", "indexreg", None),
        ("indexreg", "superposition", None), ("superposition", "oracle", None),
        ("oracle", "diffuser", None), ("diffuser", "selected", None),
        ("selected", "handoff", "Move object, not qubit measurements"),
        ("handoff", "coords", None), ("coords", "lookup", None),
        ("lookup", "logic", None), ("logic", "readout", None),
        ("readout", "apply", "measurement does not apply the move"),
        ("apply", "result", None),
    ]
    render_chart(
        "05_3x3_piece_to_best_move",
        "3×3 move selection and pure-circuit walkthrough",
        "Classical piece/move data becomes Grover target indices; a selected Move can then be processed by the separate 23-qubit prototype.",
        boxes, edges, width=22, height=14,
        footnote=("Important: the normal 3×3 gameplay uses classical depth-3 minimax. The 3×3 hybrid benchmark exercises Grover separately. "
                  "The Grover index qubits do not come from the pure circuit's coordinate/status qubits; the link shown is a software-level Move handoff. "
                  "Grover amplifies heuristic-best candidates supplied by classical code; it does not evaluate chess rules or guarantee a globally optimal move."),
    )


def two_by_two_black_pawn_circuit() -> None:
    """Trace the interactive 2×2 Black Pawn demonstration end to end."""
    boxes = [
        make_box("setup", 2.5, 11.5, 4.2, 1.0, "2×2 demo configuration",
                 "One Black Pawn at (row 0, col 0)", "green"),
        make_box("turn", 7.5, 11.5, 4.2, 1.0, "Classical GameState",
                 "Black to move; board remains in Python", "green"),
        make_box("move", 12.5, 11.5, 4.2, 1.0, "Choose legal pawn move",
                 "Example: (0,0) → (1,0), forward", "gold"),
        make_box("encode", 17.5, 11.5, 4.2, 1.0, "Encode coordinates",
                 "source 0000; target 0001", "blue"),

        make_box("registers", 17.5, 8.8, 4.2, 1.1, "Allocate 23 qubits",
                 "cur4 + tgt4 + dir4 + src3 + dst3 + anc5", "purple"),
        make_box("init", 12.5, 8.8, 4.2, 1.1, "Initialize coordinate state",
                 "X gates set 1 bits; basis-state coordinates", "blue"),
        make_box("lookup", 7.5, 8.8, 4.2, 1.1, "Encode square statuses",
                 "Pawn 001; empty square 000", "gold"),
        make_box("gates", 2.5, 8.8, 4.2, 1.1, "Build controlled lookup",
                 "Classical board loop adds X + MCX gates", "purple"),

        make_box("direction", 2.5, 6.0, 4.2, 1.1, "Direction pattern logic",
                 "CX / X / CCX; limited prototype", "purple"),
        make_box("status", 7.5, 6.0, 4.2, 1.1, "Status operation",
                 "Controlled toggles use direction/status bits", "purple"),
        make_box("simulate", 12.5, 6.0, 4.2, 1.1, "Aer one-shot simulation",
                 "Measure all 23 qubits", "teal"),
        make_box("readout", 17.5, 6.0, 4.2, 1.1, "Diagnostic bit string",
                 "Shows measured registers; not a new board", "teal"),

        make_box("validate", 17.5, 3.2, 4.2, 1.1, "Classical move validation",
                 "Parent Game receives original Move", "green"),
        make_box("apply", 12.5, 3.2, 4.2, 1.1, "Apply pawn move classically",
                 "Move piece to (1,0); switch turn", "green"),
        make_box("next", 7.5, 3.2, 4.2, 1.1, "Updated classical state",
                 "GameState owns the resulting board", "green"),
        make_box("repeat", 2.5, 3.2, 4.2, 1.1, "Continue the game",
                 "Next turn uses the updated GameState", "blue"),
    ]
    edges = [
        ("setup", "turn", None), ("turn", "move", None),
        ("move", "encode", None), ("encode", "registers", None),
        ("registers", "init", None), ("init", "lookup", None),
        ("lookup", "gates", None), ("gates", "direction", None),
        ("direction", "status", None), ("status", "simulate", None),
        ("simulate", "readout", "measurement is diagnostic"),
        ("readout", "validate", "original Move continues classically"),
        ("validate", "apply", None), ("apply", "next", None),
        ("next", "repeat", None),
    ]
    render_chart(
        "06_2x2_black_pawn_pure_quantum",
        "2×2 Black Pawn | Pure-circuit demonstration",
        "From the configured pawn and selected move to coordinate/status gates, Aer readout, and the classical board update.",
        boxes, edges, width=22, height=14,
        footnote=("This is the interactive option 6 route. The circuit uses 23 qubits and its measurement does not select or apply the move. "
                  "The board update is classical. The Grover-labelled option 7 is separate and currently returns the first legal candidate before constructing a Grover circuit."),
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    project_map()
    gameplay_routes()
    circuit_paths()
    benchmark_flow()
    three_by_three_move_to_circuit()
    two_by_two_black_pawn_circuit()
    print(f"\nGenerated 6 connected flowcharts in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
