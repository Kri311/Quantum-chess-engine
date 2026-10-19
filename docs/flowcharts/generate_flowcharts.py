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
import textwrap
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
        make_box("p1", 7.5, 10.65, 4.35, 1.0, "Human White + Minimax Black", "Black selects moves with depth-3 classical Minimax", "blue"),
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
        footnote=("3×3 Black uses depth-3 classical Minimax. Option 6 applies moves through Game.make_move after circuit diagnostics. "
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


def approach_implementation_flow() -> None:
    """Compare the classical, small-circuit, and hybrid implementation paths."""
    fig, ax = plt.subplots(figsize=(20, 11.25), facecolor=COLORS["white"])
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 11.25)
    ax.axis("off")
    ax.set_facecolor(COLORS["white"])

    classical = "#3F805C"
    quantum = "#7653A3"
    class_fill = COLORS["green"]
    quantum_fill = COLORS["purple"]
    center_x = {"classical": 3.3, "quantum": 10.0, "hybrid": 16.7}
    node_width = 4.85
    node_height = 0.72

    ax.text(10, 10.95, "Approach Implementation | Classical, Quantum & Hybrid",
            fontsize=20, weight="bold", color=COLORS["navy"], ha="center", va="center")
    ax.text(10, 10.57, "Dotted boundaries identify classical and quantum processing",
            fontsize=10.5, color=COLORS["muted"], ha="center", va="center")

    headings = [
        ("classical", "CLASSICAL SYSTEM", classical),
        ("quantum", "QUANTUM CIRCUITS", quantum),
        ("hybrid", "HYBRID SYSTEM", COLORS["navy"]),
    ]
    for key, label, color in headings:
        ax.text(center_x[key], 10.05, label, fontsize=12, weight="bold",
                color=color, ha="center", va="center")

    for x in (6.65, 13.35):
        ax.plot([x, x], [0.6, 9.68], color="#D9E0E6", linewidth=0.8, zorder=0)

    def group(x: float, y: float, width: float, height: float,
              label: str, color: str) -> None:
        frame = FancyBboxPatch(
            (x, y), width, height,
            boxstyle="round,pad=0.025,rounding_size=0.12",
            linewidth=1.6, linestyle=(0, (1.2, 2.3)),
            edgecolor=color, facecolor=COLORS["white"], zorder=0,
        )
        ax.add_patch(frame)
        ax.text(x + width / 2, y + height - 0.2, label,
                fontsize=9, weight="bold", color=color,
                ha="center", va="center", zorder=2,
                bbox={"facecolor": COLORS["white"], "edgecolor": "none", "pad": 1.4})

    # The classical baseline is entirely inside a classical-use boundary.
    group(0.4, 0.72, 5.8, 8.96, "CLASSICAL USAGE", classical)

    # Both circuit types are shown in the quantum section. Grover is labeled
    # as a subroutine used by the hybrid path, with its classical handoffs
    # shown between the middle and right columns.
    group(7.15, 0.72, 5.7, 8.96, "QUANTUM-CIRCUIT USAGE", quantum)
    ax.text(center_x["quantum"], 9.08, "SMALL-BOARD COORDINATE / STATUS DEMO",
            fontsize=8.7, weight="bold", color=quantum, ha="center", va="center")
    ax.plot([7.7, 12.3], [5.6, 5.6], color="#D9D1E5", linewidth=0.9, zorder=1)
    ax.text(center_x["quantum"], 5.35, "GROVER INDEX SEARCH · HYBRID USE",
            fontsize=8.7, weight="bold", color=quantum, ha="center", va="center")

    # The hybrid path prepares targets classically, searches their indices,
    # and returns to classical move decoding and board updates.
    group(13.85, 7.12, 5.7, 2.56, "CLASSICAL USAGE", classical)
    group(13.85, 0.48, 5.7, 2.32, "CLASSICAL USAGE", classical)

    nodes: list[tuple[float, float, str, str, str]] = []
    # Classical Minimax baseline.
    classical_y = [8.55, 7.02, 5.49, 3.96, 2.43]
    classical_labels = [
        "3×3 board position",
        "Legal move generation",
        "Depth-3 Minimax + α–β",
        "Best move selection",
        "Classical board update",
    ]
    nodes.extend((center_x["classical"], y, label, class_fill, classical)
                 for y, label in zip(classical_y, classical_labels))

    # Small-board coordinate/status circuit and the separate Grover circuit.
    pure_circuit_y = [
        (8.45, "Encode supplied move", quantum_fill, quantum),
        (7.45, "Coordinate/status gates", quantum_fill, quantum),
        (6.45, "Aer diagnostic measurement", quantum_fill, quantum),
    ]
    nodes.extend((center_x["quantum"], y, label, fill, edge)
                 for y, label, fill, edge in pure_circuit_y)

    grover_y = [
        (4.85, "H: index superposition", quantum_fill, quantum),
        (3.95, "Grover phase oracle", quantum_fill, quantum),
        (3.05, "Diffuser", quantum_fill, quantum),
        (2.15, "Aer shots / measured index", quantum_fill, quantum),
    ]
    nodes.extend((center_x["quantum"], y, label, fill, edge)
                 for y, label, fill, edge in grover_y)

    # Hybrid classical preparation and result handling.
    hybrid_input_y = [
        (8.58, "Board + legal move list", class_fill, classical),
        (7.62, "Heuristic target indices", class_fill, classical),
    ]
    hybrid_output_y = [
        (1.88, "Decode + validate index", class_fill, classical),
        (0.93, "Move update / Minimax fallback", class_fill, classical),
    ]
    nodes.extend((center_x["hybrid"], y, label, fill, edge)
                 for y, label, fill, edge in hybrid_input_y + hybrid_output_y)

    # Draw the arrows behind the nodes.  The dotted frames group each stage
    # by the kind of processing it uses.
    flows = [
        (center_x["classical"], classical_y),
        (center_x["quantum"], [y for y, *_ in pure_circuit_y]),
        (center_x["quantum"], [y for y, *_ in grover_y]),
        (center_x["hybrid"], [y for y, *_ in hybrid_input_y]),
        (center_x["hybrid"], [y for y, *_ in hybrid_output_y]),
    ]
    for x, ys in flows:
        for upper, lower in zip(ys, ys[1:]):
            arrow = FancyArrowPatch(
                (x, upper - node_height / 2),
                (x, lower + node_height / 2),
                arrowstyle="-|>", mutation_scale=12,
                linewidth=1.2, color=COLORS["line"], zorder=1,
            )
            ax.add_patch(arrow)

    # Classical best-index preparation feeds Grover; its sampled index returns
    # to the hybrid path for decoding and validation.
    grover_handoff = FancyArrowPatch(
        (center_x["hybrid"] - node_width / 2, hybrid_input_y[-1][0]),
        (center_x["quantum"] + node_width / 2, grover_y[0][0]),
        arrowstyle="-|>", mutation_scale=12,
        linewidth=1.35, color=COLORS["line"], zorder=1,
    )
    ax.add_patch(grover_handoff)
    decode_handoff = FancyArrowPatch(
        (center_x["quantum"] + node_width / 2, grover_y[-1][0]),
        (center_x["hybrid"] - node_width / 2, hybrid_output_y[0][0]),
        arrowstyle="-|>", mutation_scale=12,
        linewidth=1.35, color=COLORS["line"], zorder=1,
    )
    ax.add_patch(decode_handoff)

    for x, y, label, fill, edge in nodes:
        patch = FancyBboxPatch(
            (x - node_width / 2, y - node_height / 2),
            node_width, node_height,
            boxstyle="round,pad=0.035,rounding_size=0.1",
            linewidth=0.9, edgecolor=edge, facecolor=fill, zorder=3,
        )
        ax.add_patch(patch)
        ax.text(x, y, label, fontsize=10, color=COLORS["ink"],
                ha="center", va="center", zorder=4)

    ax.text(10, 0.28,
            "Chess rules, move legality, and final board updates remain classical.",
            fontsize=8.6, color=COLORS["muted"], ha="center", va="center")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    png = OUTPUT_DIR / "07_approach_implementation_flow.png"
    svg = OUTPUT_DIR / "07_approach_implementation_flow.svg"
    fig.savefig(png, dpi=190, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(svg, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Wrote {png.relative_to(PROJECT_ROOT)}")
    print(f"Wrote {svg.relative_to(PROJECT_ROOT)}")


def detailed_system_flows() -> None:
    """Compare the configured 2×2, 3×3, and 8×8 implementation pipelines."""
    fig, ax = plt.subplots(figsize=(20, 13), facecolor=COLORS["white"])
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 13)
    ax.axis("off")
    ax.set_facecolor(COLORS["white"])

    lane_lefts = [0.28, 6.92, 13.56]
    lane_width = 6.16
    centers = [x + lane_width / 2 for x in lane_lefts]
    node_width = 5.12
    node_height = 0.82
    ys = [10.62, 9.48, 8.34, 7.20, 6.06, 4.92, 3.78]
    edge_colors = ["#39805A", "#7552A4", "#B17B23"]
    fills = [COLORS["green"], COLORS["purple"], COLORS["gold"]]

    ax.text(10, 12.68, "Three System Implementations | Flow and Configuration",
            fontsize=19, weight="bold", color=COLORS["navy"], ha="center", va="center")
    ax.text(10, 12.28,
            "Follow each lane from its configured input to its output; dotted frames show where classical and quantum work occurs.",
            fontsize=9.5, color=COLORS["muted"], ha="center", va="center")

    # Soft lane backgrounds and separators make the three systems easy to scan.
    for i, left in enumerate(lane_lefts):
        ax.add_patch(Rectangle((left, 0.67), lane_width, 11.26,
                               facecolor=["#F7FAFD", "#FBF9FE", "#FFFCF5"][i],
                               edgecolor="none", zorder=0))
    for x in (6.67, 13.31):
        ax.plot([x, x], [0.75, 11.92], color="#D8E0E7", linewidth=0.9, zorder=0)

    headings = [
        ("2×2 PURE-CIRCUIT DEMO", "#39805A", "One pawn · move encoding and circuit readout"),
        ("3×3 CLASSICAL + CIRCUIT TRACE", "#7552A4", "Depth-3 Minimax move selection · circuit is diagnostic"),
        ("8×8 HYBRID QUANTUM SEARCH", "#9A6B1F", "Classical move scoring · Grover index search"),
    ]
    for x, (label, color, sublabel) in zip(centers, headings):
        ax.text(x, 11.72, label, fontsize=10.3, weight="bold", color=color,
                ha="center", va="center")
        ax.text(x, 11.43, sublabel, fontsize=7.9, color=COLORS["muted"],
                ha="center", va="center")

    def draw_group(lane: int, first: int, last: int, label: str, color: str) -> None:
        x = lane_lefts[lane] + 0.19
        y_top = ys[first] + node_height / 2 + 0.17
        y_bottom = ys[last] - node_height / 2 - 0.17
        frame = FancyBboxPatch(
            (x, y_bottom), lane_width - 0.38, y_top - y_bottom,
            boxstyle="round,pad=0.025,rounding_size=0.12",
            linewidth=1.35, linestyle=(0, (1.3, 2.3)),
            edgecolor=color, facecolor="none", zorder=1,
        )
        ax.add_patch(frame)
        ax.text(centers[lane], y_top - 0.02, label, fontsize=7.4, weight="bold",
                color=color, ha="center", va="center", zorder=4,
                bbox={"facecolor": ["#F7FAFD", "#FBF9FE", "#FFFCF5"][lane],
                      "edgecolor": "none", "pad": 1.2})

    groups = [
        [(0, 1, "CLASSICAL INPUT", edge_colors[0]),
         (2, 4, "QUANTUM CIRCUIT + AER", edge_colors[1]),
         (5, 5, "CLASSICAL GAME UPDATE", edge_colors[0])],
        [(0, 3, "CLASSICAL RULES + MINIMAX", edge_colors[0]),
         (4, 5, "PURE-CIRCUIT DIAGNOSTIC", edge_colors[1]),
         (6, 6, "CLASSICAL GAME UPDATE", edge_colors[0])],
        [(0, 1, "CLASSICAL PRE-PROCESSING", edge_colors[0]),
         (2, 4, "GROVER CIRCUIT + AER", edge_colors[1]),
         (5, 6, "CLASSICAL OUTPUT", edge_colors[0])],
    ]
    for lane, lane_groups in enumerate(groups):
        for first, last, label, color in lane_groups:
            draw_group(lane, first, last, label, color)

    lane_nodes: list[list[tuple[str, str]]] = [
        [
            ("1  Start board + legal move", "Black Pawn at (0,0); example (0,0) → (1,0)"),
            ("2  Encode source and target", "cur = 0000; tgt = 0001; X gates load 1-bits"),
            ("3  Allocate and prepare registers", "cur4 · tgt4 · dir4 · src3 · dst3 · anc5 = 23 qubits"),
            ("4  Look up status and move direction", "X/MCX: square status; CX/CCX: direction; MCX: status operation"),
            ("5  Measure with Aer", "Statevector simulator · 1 shot · readout is diagnostic"),
            ("6  Apply the original Move", "Classical Game updates its board and switches the turn"),
        ],
        [
            ("1  Load 3×3 GameState", "White Knight (2,1); Black Pawn (0,0); White starts"),
            ("2  Generate legal moves", "MoveGenerator applies the current chess-variant rules"),
            ("3  Run Minimax search", "Black's move is selected by depth-3 Minimax; White is human"),
            ("4  Rank outcomes and prune", "α–β pruning; leaf score: material, mobility, pawn advance, center"),
            ("5  Build the 23-qubit trace circuit", "Each selected move is encoded; status and direction gates are added"),
            ("6  Run one Aer shot", "Measurement returns a bitstring; it does not choose the chess move"),
            ("7  Update board classically", "The original legal Move is validated and applied by Game.make_move"),
        ],
        [
            ("1  Read 8×8 GameState", "Board and current turn are held in the classical GameState"),
            ("2  Generate and rank legal moves", "score_move targets tied top moves; one legal move skips Grover"),
            ("3  Encode search space", "n = max(1, ⌈log₂ C⌉) index qubits; N = 2ⁿ; add one flag qubit"),
            ("4  Prepare uniform superposition", "H on each index qubit; X then H prepares the flag in |−⟩"),
            ("5  Oracle + Grover diffuser", "Oracle flips best-index phase; diffuser reflects about mean and amplifies.\nRepeat k≈⌊(π/4)√(N/M)⌋; k=0 if M>N/2."),
            ("6  Measure, decode, and validate", "Aer shots return an index; invalid result falls back to first best target"),
            ("7  Apply move and continue", "Classical Game updates the board; depth-3 Minimax is the no-result fallback"),
        ],
    ]

    for lane, nodes in enumerate(lane_nodes):
        x = centers[lane]
        accent = edge_colors[lane]
        fill = fills[lane]
        # Draw the arrows first so each box remains crisp and legible.
        for upper_idx in range(len(nodes) - 1):
            y1, y2 = ys[upper_idx], ys[upper_idx + 1]
            arrow = FancyArrowPatch(
                (x, y1 - node_height / 2 - 0.02),
                (x, y2 + node_height / 2 + 0.02),
                arrowstyle="-|>", mutation_scale=11, linewidth=1.15,
                color=COLORS["line"], zorder=2,
            )
            ax.add_patch(arrow)

        for idx, (title, body) in enumerate(nodes):
            y = ys[idx]
            patch = FancyBboxPatch(
                (x - node_width / 2, y - node_height / 2), node_width, node_height,
                boxstyle="round,pad=0.03,rounding_size=0.10",
                linewidth=1.0, edgecolor=accent, facecolor=fill, zorder=3,
            )
            ax.add_patch(patch)
            ax.text(x, y + 0.15, title, fontsize=8.15, weight="bold",
                    color=COLORS["navy"], ha="center", va="center", zorder=4)
            ax.text(x, y - 0.15, body, fontsize=6.75, color=COLORS["ink"],
                    ha="center", va="center", zorder=4)

    config_cards = [
        ("2×2 CONFIGURATION",
         "BOARD_SIZE=2 · one Black Pawn at (0,0) · Black to move\n"
         "23-qubit prototype · direct Aer statevector · 1 shot\n"
         "This interactive path does not use the shared noisy wrapper."),
        ("3×3 CONFIGURATION",
         "BOARD_SIZE=3 · Knight (2,1) + Pawn (0,0) · Minimax depth=3\n"
         "HybridEngine(use_quantum=False) for move selection; pure circuit runs per move\n"
         "Direct Aer statevector · 1 shot · no noise model in this route."),
        ("8×8 HYBRID DEFAULTS",
         "HybridEngine(use_quantum=True) · shared QuantumSimulator wrapper\n"
         "1,024 shots · noise on: 1% single-qubit / 10% two-qubit\n"
         "Aer statevector tries GPU, falls back to CPU; local simulation."),
    ]

    for lane, (title, body) in enumerate(config_cards):
        x = centers[lane]
        card = FancyBboxPatch(
            (x - 2.82, 0.75), 5.64, 1.72,
            boxstyle="round,pad=0.05,rounding_size=0.12",
            linewidth=1.0, edgecolor=edge_colors[lane],
            facecolor=["#EFF7F1", "#F3EFF9", "#FFF6E6"][lane], zorder=2,
        )
        ax.add_patch(card)
        ax.text(x, 2.20, title, fontsize=7.7, weight="bold", color=edge_colors[lane],
                ha="center", va="center", zorder=3)
        ax.text(x, 1.52, body, fontsize=6.55, color=COLORS["ink"],
                ha="center", va="center", linespacing=1.3, zorder=3)

    ax.text(10, 0.35,
            "Grover amplifies classically pre-scored best move indices; chess rules, final move validation, and board updates stay classical.",
            fontsize=7.5, color=COLORS["muted"], ha="center", va="center")
    ax.text(10, 0.15,
            "2×2 option 7 caveat: all legal moves are currently marked, so it returns the first move before building a Grover circuit.",
            fontsize=6.9, color=COLORS["muted"], ha="center", va="center")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    png = OUTPUT_DIR / "08_detailed_system_implementation_flows.png"
    svg = OUTPUT_DIR / "08_detailed_system_implementation_flows.svg"
    fig.savefig(png, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(svg, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Wrote {png.relative_to(PROJECT_ROOT)}")
    print(f"Wrote {svg.relative_to(PROJECT_ROOT)}")


def separate_system_charts() -> None:
    """Render one slide-ready, configuration-aware flowchart per system."""
    def draw_one(
        filename: str,
        title: str,
        subtitle: str,
        left_heading: str,
        right_heading: str,
        left_steps: list[tuple[str, str]],
        right_steps: list[tuple[str, str]],
        execution: str,
        configuration: str,
        footnote: str = "",
    ) -> None:
        fig, ax = plt.subplots(figsize=(16, 9), facecolor="#FFFEFC")
        ax.set_xlim(0, 16)
        ax.set_ylim(0, 9)
        ax.axis("off")
        ax.set_facecolor("#FFFEFC")

        classical = "#42815E"
        quantum = "#7654A1"
        output = "#366B84"
        ink = "#26333D"
        muted = "#596774"

        ax.text(0.45, 8.62, title, fontsize=20, weight="bold", color="#1B344A",
                ha="left", va="center")
        ax.text(0.47, 8.18, subtitle, fontsize=11, color=muted,
                ha="left", va="center")

        def dotted_group(x: float, y: float, w: float, h: float,
                         label: str, color: str, fill: str) -> None:
            frame = FancyBboxPatch(
                (x, y), w, h,
                boxstyle="round,pad=0.025,rounding_size=0.11",
                linewidth=1.45, linestyle=(0, (1.25, 2.15)),
                edgecolor=color, facecolor=fill, zorder=0,
            )
            ax.add_patch(frame)
            ax.text(x + w / 2, y + h - 0.18, label,
                    fontsize=10.5, weight="bold", color=color,
                    ha="center", va="center", zorder=3,
                    bbox={"facecolor": fill, "edgecolor": "none", "pad": 1.6})

        dotted_group(0.42, 3.48, 7.18, 4.17,
                     left_heading, classical, "#F6FAF7")
        dotted_group(8.40, 3.48, 7.18, 4.17,
                     right_heading, quantum, "#F9F6FC")
        # Handoff between CPU preparation and the circuit stage.
        ax.add_patch(FancyArrowPatch(
            (7.58, 7.47), (8.38, 7.47), arrowstyle="-|>", mutation_scale=14,
            linewidth=1.5, color="#526B80", zorder=2,
        ))

        step_ys = [6.68, 5.34, 4.00]
        for x, steps, color in ((0.78, left_steps, classical),
                                (8.77, right_steps, quantum)):
            for i, (step_title, body) in enumerate(steps):
                y = step_ys[i]
                node = FancyBboxPatch(
                    (x - 0.10, y - 0.49), 6.66, 0.98,
                    boxstyle="round,pad=0.025,rounding_size=0.09",
                    linewidth=0.95, edgecolor=color,
                    facecolor="#EAF3ED" if color == classical else "#F0EBF7",
                    zorder=1,
                )
                ax.add_patch(node)
                ax.text(x + 0.12, y + 0.22, step_title, fontsize=11.4, weight="bold",
                        color=color, ha="left", va="center", zorder=3)
                wrapped_body = "\n".join(
                    textwrap.fill(line, width=67, break_long_words=False)
                    for line in body.splitlines()
                )
                ax.text(x + 0.15, y - 0.19, wrapped_body, fontsize=9.25,
                        color=ink, ha="left", va="center", linespacing=1.08, zorder=3)
                if i < len(steps) - 1:
                    ax.add_patch(FancyArrowPatch(
                        (x + 3.23, y - 0.51),
                        (x + 3.23, step_ys[i + 1] + 0.51),
                        arrowstyle="-|>", mutation_scale=9,
                        linewidth=1.05, color="#6F8290", zorder=2,
                    ))

        # The measured/selected result returns to classical game execution.
        ax.add_patch(FancyArrowPatch(
            (11.98, 3.46), (11.98, 3.04), arrowstyle="-|>",
            mutation_scale=12, linewidth=1.25, color="#526B80", zorder=2,
        ))
        dotted_group(0.42, 2.03, 15.16, 1.02,
                     "EXECUTION (CPU)", output, "#F4F8FA")
        ax.text(8.0, 2.48, execution, fontsize=9.8, color=ink,
                ha="center", va="center")

        config_card = FancyBboxPatch(
            (0.42, 0.47), 15.16, 1.25,
            boxstyle="round,pad=0.04,rounding_size=0.10",
            linewidth=1.0, edgecolor="#B58A43", facecolor="#FFF8E9", zorder=1,
        )
        ax.add_patch(config_card)
        ax.text(0.72, 1.47, "SYSTEM CONFIGURATION", fontsize=9.5,
                weight="bold", color="#8A651F", ha="left", va="center", zorder=3)
        config_lines = "\n".join(
            textwrap.fill(line, width=150, break_long_words=False)
            for line in configuration.splitlines()
        )
        ax.text(0.74, 1.00, config_lines, fontsize=8.9,
                color=ink, ha="left", va="center", linespacing=1.22, zorder=3)
        if footnote:
            ax.text(0.48, 0.20, footnote, fontsize=7.8, color=muted,
                    ha="left", va="center")

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        png = OUTPUT_DIR / f"{filename}.png"
        svg = OUTPUT_DIR / f"{filename}.svg"
        fig.savefig(png, dpi=210, bbox_inches="tight", facecolor=fig.get_facecolor())
        fig.savefig(svg, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        print(f"Wrote {png.relative_to(PROJECT_ROOT)}")
        print(f"Wrote {svg.relative_to(PROJECT_ROOT)}")

    draw_one(
        "09_2x2_system_implementation",
        "2×2 Quantum Demonstration | Move-to-circuit flow",
        "A supplied pawn move is encoded and traced by a small circuit; the game state remains classical.",
        "CLASSICAL PRE-PROCESSING (CPU)",
        "PURE-CIRCUIT SIMULATION (Aer)",
        [
            ("1. Configure board and choose move", "Black Pawn at (0,0); example legal move is (0,0) → (1,0)."),
            ("2. Encode source and target", "cur=0000, tgt=0001; X gates set the coordinate bits to 1."),
            ("3. Pass classical data to circuit", "Board layout and encoded source/target are circuit inputs."),
        ],
        [
            ("4. Allocate 23 qubits", "cur4 + tgt4 + dir4 + src3 + dst3 + anc5."),
            ("5. Apply status and direction logic", "X/MCX: status lookup; CX/CCX: direction; MCX: status update."),
            ("6. Measure circuit registers", "Aer statevector, 1 shot → diagnostic bitstring, not a move choice."),
        ],
        "Validate and apply the original Move in GameState; move the pawn to (1,0) and switch the turn.",
        "BOARD_SIZE=2; one Black Pawn; direct Aer statevector simulator; 1 shot; this interactive path does not use the shared noisy wrapper.",
        "Option 7 caveat: its current all-target shortcut returns the first legal candidate before building a Grover circuit.",
    )

    draw_one(
        "10_3x3_system_implementation",
        "3×3 System | Minimax decision + circuit trace",
        "Classical Minimax selects a move; the pure-circuit prototype measures that supplied move as a diagnostic.",
        "CLASSICAL GAME + MINIMAX (CPU)",
        "PURE-CIRCUIT DIAGNOSTIC (Aer)",
        [
            ("1. Load the 3×3 position", "White Knight at (2,1), Black Pawn at (0,0); White is the human player."),
            ("2. Generate legal moves", "MoveGenerator applies the game rules for the current player."),
            ("3. Minimax selects Black's move", "Depth 3 with α–β pruning; leaves score material, mobility, pawn advance, and center."),
        ],
        [
            ("4. Encode the selected Move", "Allocate 23 qubits for coordinates, direction, square status, and ancillas."),
            ("5. Build coordinate/status gates", "X + MCX lookup; CX/CCX direction logic; MCX status operation."),
            ("6. Run one Aer shot", "Measure a diagnostic bitstring; the circuit readout does not choose the chess move."),
        ],
        "The original legal Move—not the measured bitstring—is validated and applied to the classical board.",
        "BOARD_SIZE=3; Knight (2,1) + Pawn (0,0); HybridEngine(use_quantum=False), Minimax depth=3.\n"
        "Each move runs direct Aer statevector for 1 shot; no shared noise model in this route.",
    )

    draw_one(
        "11_8x8_hybrid_system_implementation",
        "8×8 Hybrid System | Classical scoring + Grover search",
        "Classical code prepares legal moves and best-score targets; Grover samples their move indices.",
        "CLASSICAL PRE-PROCESSING (CPU)",
        "GROVER CIRCUIT + AER",
        [
            ("1. Read board and legal moves", "GameState holds the 8×8 board; MoveGenerator filters the legal candidates."),
            ("2. Score candidates classically", "HeuristicEvaluator.score_move ranks moves; all tied top indices become targets."),
            ("3. Prepare the search input", "C candidates → n=max(1,⌈log₂C⌉) index qubits; N=2ⁿ; one extra phase flag."),
        ],
        [
            ("4. Prepare uniform superposition", "H on index qubits; X then H puts the flag in |−⟩ for phase kickback."),
            ("5. Oracle + diffuser amplify targets", "Oracle flips target phase; diffuser reflects about the mean.\nRepeat k≈⌊(π/4)√(N/M)⌋ (k=0 if M>N/2)."),
            ("6. Measure and decode index", "Aer samples an index; decode and validate it, falling back to the first best target if needed."),
        ],
        "Return the selected Move and update the classical board/UI; depth-3 Minimax is the no-result fallback.",
        "BOARD_SIZE=8; HybridEngine(use_quantum=True); shared QuantumSimulator.\n"
        "Defaults: 1,024 shots; depolarizing noise 1% single-qubit / 10% two-qubit.\n"
        "Aer statevector tries GPU then CPU fallback; local simulation, not quantum hardware.",
        "Grover amplifies classically pre-scored indices; it does not generate legal moves or evaluate the chess position in superposition.",
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    project_map()
    gameplay_routes()
    circuit_paths()
    benchmark_flow()
    three_by_three_move_to_circuit()
    two_by_two_black_pawn_circuit()
    approach_implementation_flow()
    detailed_system_flows()
    separate_system_charts()
    print(f"\nGenerated 11 connected flowcharts in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
