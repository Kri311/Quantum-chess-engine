#!/usr/bin/env python3
"""Generate the 2x2 Grover/circuit flow in the report's three-lane style."""

from __future__ import annotations

import os
from pathlib import Path
import tempfile

os.environ.setdefault(
    "MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "qce_2x2_grover_mplcache")
)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


OUT = Path(__file__).resolve().parent / "generated"
COLORS = {
    "navy": "#18324B",
    "ink": "#263746",
    "muted": "#526777",
    "line": "#5D7182",
    "white": "#FFFFFF",
    "green": "#328767",
    "green_bg": "#F4F9F5",
    "green_box": "#E8F3EA",
    "green_border": "#CFE3D5",
    "purple": "#8057AD",
    "purple_bg": "#F9F6FC",
    "purple_box": "#EEE9F8",
    "purple_border": "#DED4EA",
    "orange": "#B47819",
    "orange_bg": "#FFFAF1",
    "orange_box": "#FFF0D1",
    "orange_border": "#E9D9B7",
    "blue_box": "#E8F1FA",
    "teal_box": "#E3F3F2",
    "gray": "#F1F3F5",
    "gray_border": "#D4DCE2",
}


def panel(ax, x: float, y: float, width: float, height: float,
          fill: str, border: str) -> None:
    ax.add_patch(FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        facecolor=fill, edgecolor=border, linewidth=0.9, zorder=0,
    ))


def phase(ax, x: float, y: float, width: float, height: float,
          label: str, color: str) -> None:
    ax.add_patch(FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        facecolor="none", edgecolor=color, linewidth=1.15,
        linestyle=(0, (1.2, 2.2)), zorder=1,
    ))
    ax.text(x + width / 2, y + height - 0.09, label,
            ha="center", va="top", fontsize=9.3, weight="bold",
            color=color, zorder=4,
            bbox={"boxstyle": "round,pad=0.12", "fc": "white", "ec": "none"})


def box(ax, cx: float, cy: float, width: float, height: float,
        title: str, body: str, fill: str, edge: str,
        *, title_size: float = 11.0, body_size: float = 9.3) -> None:
    ax.add_patch(FancyBboxPatch(
        (cx - width / 2, cy - height / 2), width, height,
        boxstyle="round,pad=0.025,rounding_size=0.075",
        linewidth=1.1, edgecolor=edge, facecolor=fill, zorder=3,
    ))
    ax.text(cx, cy + height * 0.23, title, ha="center", va="center",
            fontsize=title_size, weight="bold", color=COLORS["navy"], zorder=4)
    ax.text(cx, cy - height * 0.14, body, ha="center", va="center",
            fontsize=body_size, color=COLORS["ink"], linespacing=1.16, zorder=4)


def arrow(ax, start: tuple[float, float], end: tuple[float, float],
          color: str, *, dashed: bool = False) -> None:
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=11, linewidth=1.25,
        color=color, linestyle="--" if dashed else "-", zorder=2,
    ))


def main() -> None:
    fig, ax = plt.subplots(figsize=(18, 11), facecolor=COLORS["white"])
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 11)
    ax.axis("off")
    ax.set_facecolor(COLORS["white"])

    lane_y, lane_h, lane_w = 1.18, 9.55, 5.65
    lane_x = (0.22, 6.17, 12.12)
    centers = tuple(x + lane_w / 2 for x in lane_x)
    lane_defs = (
        ("2×2 MOVE-INDEX SEARCH", COLORS["green_bg"], COLORS["green_border"], COLORS["green"]),
        ("2×2 MOVE SELECTION", COLORS["purple_bg"], COLORS["purple_border"], COLORS["purple"]),
        ("23-QUBIT CIRCUIT TRACE", COLORS["orange_bg"], COLORS["orange_border"], COLORS["orange"]),
    )
    for x, (heading, fill, border, accent) in zip(lane_x, lane_defs):
        panel(ax, x, lane_y, lane_w, lane_h, fill, border)
        ax.text(x + lane_w / 2, 10.48, heading, ha="center", va="center",
                fontsize=13.2, weight="bold", color=accent, zorder=4)

    # Left lane: candidate preparation and the optional Grover search.
    left_x = centers[0]
    step_y = (9.38, 7.58, 5.78, 3.98, 2.18)
    step_w, step_h = 5.0, 1.25
    phase(ax, lane_x[0] + 0.18, 8.65, lane_w - 0.36, 1.48,
          "CLASSICAL INPUT", COLORS["green"])
    phase(ax, lane_x[0] + 0.18, 1.38, lane_w - 0.36, 6.98,
          "GROVER CIRCUIT + AER", COLORS["purple"])
    left_steps = [
        ("1  Candidate encoding",
         "CPU lists L legal moves; classical code marks M targets.\nq=max(1,⌈log₂L⌉); N=2^q index states.",
         COLORS["green_box"], COLORS["green"]),
        ("2  Uniform superposition",
         "H^⊗q|0^q⟩=|s⟩; |s⟩=(1/√N)Σₓ|x⟩.\nInitial P(index)=1/N.",
         COLORS["purple_box"], COLORS["purple"]),
        ("3  Oracle phase mark",
         "f(x)=1 marks a target; O_f|x⟩=(−1)^f(x)|x⟩.\nAncilla |−⟩ enables phase kickback.",
         COLORS["purple_box"], COLORS["purple"]),
        ("4  Diffuser / amplify",
         "H–X–MCZ–X–H; D=2|s⟩⟨s|−I.\nk≈⌊(π/4)√(N/M)⌋ rounds.",
         COLORS["purple_box"], COLORS["purple"]),
        ("5  Measure + decode",
         "Measure q index bits and decode candidates[x].\nUse first-target fallback if invalid or unmarked.",
         COLORS["teal_box"], COLORS["green"]),
    ]
    for y, (title, body, fill, edge) in zip(step_y, left_steps):
        box(ax, left_x, y, step_w, step_h, title, body, fill, edge,
            title_size=10.9, body_size=9.0)
    for y0, y1 in zip(step_y, step_y[1:]):
        arrow(ax, (left_x, y0 - step_h / 2 - 0.04),
              (left_x, y1 + step_h / 2 + 0.04), COLORS["green"])

    # Middle lane: the all-target shortcut and the converged selected move.
    middle_x = centers[1]
    phase(ax, lane_x[1] + 0.18, 7.35, lane_w - 0.36, 1.5,
          "TARGET-SET CHECK", COLORS["purple"])
    box(ax, middle_x, 8.1, 5.0, 1.25, "Check marked targets",
        "Option 7 marks every legal candidate;\nM=L in the 2×2 route.",
        COLORS["purple_box"], COLORS["purple"], title_size=11.0, body_size=9.2)
    phase(ax, lane_x[1] + 0.18, 4.15, lane_w - 0.36, 1.98,
          "OPTION 7 SHORTCUT", COLORS["purple"])
    box(ax, middle_x, 5.14, 5.0, 1.45, "Short-circuit return",
        "Return the first legal Move without\nconstructing Grover's circuit.",
        COLORS["orange_box"], COLORS["orange"], title_size=11.0, body_size=9.2)
    phase(ax, lane_x[1] + 0.18, 1.38, lane_w - 0.36, 1.62,
          "MOVE SELECTION", COLORS["purple"])
    box(ax, middle_x, 2.18, 5.0, 1.2, "Selected move",
        "Measured Grover index or direct 2×2 return",
        COLORS["green_box"], COLORS["green"], title_size=11.2, body_size=9.5)
    arrow(ax, (middle_x, 7.45), (middle_x, 5.89), COLORS["purple"])
    arrow(ax, (middle_x, 4.39), (middle_x, 2.83), COLORS["purple"], dashed=True)
    # Option 7 branches from candidate generation; the measured Grover result
    # joins the same selected-move node from step 5.
    arrow(ax, (left_x + step_w / 2 + 0.04, step_y[0]),
          (middle_x - 2.5 - 0.04, 8.1), COLORS["green"], dashed=True)
    arrow(ax, (left_x + step_w / 2 + 0.04, step_y[4]),
          (middle_x - 2.5 - 0.04, 2.18), COLORS["purple"])

    # Right lane: the selected move feeds the diagnostic 23-qubit trace.
    right_x = centers[2]
    circuit_y = (2.18, 3.98, 5.78, 7.58, 9.38)
    circuit_steps = [
        ("6  Encode move",
         "23 qubits = 4+4+4+3+3+5; cur=0000; tgt=0001.\nBits encode column, then row.",
         COLORS["blue_box"], COLORS["orange"]),
        ("7  Look up status",
         "X complements zero address bits; MCX fires on exact match.\nsrc=001 (Pawn); dst=000 (empty).",
         COLORS["blue_box"], COLORS["orange"]),
        ("8  Detect direction",
         "CX computes XOR; CCX sets its flag when both controls are 1.\nCurrent comparator output: dir=0000.",
         COLORS["orange_box"], COLORS["orange"]),
        ("9  Conditional status operator",
         "Controls include direction, target, and source status.\nWith dir=0000, controls fail; no transfer or source clear.",
         COLORS["orange_box"], COLORS["orange"]),
        ("10  Aer measurement",
         "Statevector simulator; 1 shot; measure all registers.\nReadout is diagnostic, not a board state.",
         COLORS["teal_box"], COLORS["orange"]),
    ]
    phase(ax, lane_x[2] + 0.18, 1.38, lane_w - 0.36, 6.98,
          "MOVE-STATE GATES", COLORS["orange"])
    phase(ax, lane_x[2] + 0.18, 8.65, lane_w - 0.36, 1.48,
          "AER READOUT", COLORS["orange"])
    for y, (title, body, fill, edge) in zip(circuit_y, circuit_steps):
        box(ax, right_x, y, step_w, step_h, title, body, fill, edge,
            title_size=10.7, body_size=8.9)
    for y0, y1 in zip(circuit_y, circuit_y[1:]):
        arrow(ax, (right_x, y0 + step_h / 2 + 0.04),
              (right_x, y1 - step_h / 2 - 0.04), COLORS["orange"])
    arrow(ax, (middle_x + 2.5 + 0.04, 2.18),
          (right_x - step_w / 2 - 0.04, 2.18), COLORS["purple"])

    # Compact diagnostic strip retained from the original flowchart.
    ax.add_patch(FancyBboxPatch(
        (0.35, 0.18), 17.3, 0.82,
        boxstyle="round,pad=0.02,rounding_size=0.055",
        facecolor=COLORS["gray"], edgecolor=COLORS["gray_border"],
        linewidth=0.8, zorder=1,
    ))
    ax.text(0.55, 0.76,
            "READOUT  cur=0000 | tgt=0001 | src=001 | dst=000 | dir=0000 | anc=00000",
            fontsize=9.0, weight="bold", color=COLORS["ink"], va="center", zorder=2)
    ax.text(0.55, 0.49,
            "The forward-move comparator currently fails; H gates are Grover-only, and move-state gates are X/CX/CCX/MCX.",
            fontsize=8.0, color=COLORS["muted"], va="center", zorder=2)
    ax.text(0.55, 0.27,
            "Option 6 applies the Move through classical Game.make_move; option 7 saves measurement and does not update GameState.",
            fontsize=8.0, color=COLORS["muted"], va="center", zorder=2)

    OUT.mkdir(parents=True, exist_ok=True)
    stem = "12_2x2_grover_circuit_flow"
    fig.savefig(OUT / f"{stem}.png", dpi=240, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(OUT / f"{stem}.svg", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Wrote {OUT / (stem + '.png')}")
    print(f"Wrote {OUT / (stem + '.svg')}")


if __name__ == "__main__":
    main()
