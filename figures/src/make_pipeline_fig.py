"""Render the conceptual pipeline/defect figure for the manuscript.

Editable source of record for this CONCEPTUAL diagram:
figures/src/pipeline_defect.drawio. This script renders the vector PDF/PNG the
manuscript includes. Numerical figures are produced by
experiments/v2/analyze_main.py from raw data, never by hand.
"""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import pathlib

BLUE, GREEN, ORANGE, RED, GREY = "#2a78d6", "#1baf7a", "#eb6834", "#e34948", "#52514e"
FIG = pathlib.Path(__file__).resolve().parents[1]

def box(ax, x, y, w, h, text, ec, fc, fs=6.6, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.015",
                                lw=1.0, edgecolor=ec, facecolor=fc, zorder=2))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fs, zorder=3,
            color="#0b0b0b", fontweight="bold" if bold else "normal", linespacing=1.4)

def arrow(ax, p, q, color=GREY, ls="-"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=8, lw=0.9,
                                 color=color, linestyle=ls, zorder=1,
                                 connectionstyle="arc3,rad=0"))

fig, ax = plt.subplots(figsize=(7.1, 4.15))
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

W, H, Y = 0.169, 0.142, 0.772           # top row geometry
GAP = 0.027
xs = [0.013 + i * (W + GAP) for i in range(5)]
tops = ["QAOA circuit\n(virtual qubits)",
        "transpile to device\ncoupling map, basis\nlayout $\\pi$",
        "global folding\nscales $(1,3,5)$",
        "re-transpile\n$\\mathtt{opt\\_level}\\!=\\!0$",
        "execute\n(noisy simulator)"]
for x, t in zip(xs, tops):
    box(ax, x, Y, W, H, t, BLUE, "#e8f0fb")
for i in range(4):
    arrow(ax, (xs[i] + W, Y + H/2), (xs[i+1], Y + H/2))

BY, BH = 0.345, 0.125                   # bottom row
bxs = [0.055, 0.30, 0.545, 0.788]
bots = [("readout calibration\n$2k$ circuits", GREEN, "#e6f7f0"),
        ("invert $A$,\nclip + renormalise", GREEN, "#e6f7f0"),
        ("Richardson\nextrapolation", ORANGE, "#fff3ec"),
        ("estimate vs\nexact value", GREY, "#f2f2f0")]
for x, (t, ec, fc) in zip(bxs, bots):
    box(ax, x, BY, 0.157, BH, t, ec, fc)
for i in range(3):
    arrow(ax, (bxs[i] + 0.157, BY + BH/2), (bxs[i+1], BY + BH/2))

# vertical links
arrow(ax, (xs[1] + W/2, Y), (0.1335, BY + BH))                     # transpile -> calibration
arrow(ax, (xs[4] + W/2, Y), (xs[4] + W/2, BY + BH + 0.005))        # execute -> down
arrow(ax, (xs[4] + W/2, BY + BH + 0.005), (0.457, BY + BH + 0.005))# -> invert A (elbow)
arrow(ax, (0.457, BY + BH + 0.005), (0.3785, BY + BH))

# defect callouts
box(ax, 0.318, 0.575, 0.272, 0.155,
    "DEFECT 1 (folding)\nmeasurements rebuilt generically:\nclbit $c\\!\\leftarrow\\!q_c$, discarding $\\pi$",
    RED, "#fdecea", fs=6.2, bold=True)
arrow(ax, (0.454, 0.730), (0.454, Y), RED, ls="--")

box(ax, 0.012, 0.112, 0.244, 0.150,
    "DEFECT 2 (calibration)\nindexed by virtual $i$, but\nclbit $i$ reads physical $q_{\\pi(i)}$\n$\\Rightarrow A$ inverted on wrong qubits",
    RED, "#fdecea", fs=6.0, bold=True)
arrow(ax, (0.134, 0.262), (0.134, BY), RED, ls="--")
ax.text(0.134, 0.070, "M3 solves this via $\\mathtt{final\\_measurement\\_mapping}$",
        fontsize=5.4, color=GREY, ha="center", va="center", style="italic")

box(ax, 0.465, 0.105, 0.508, 0.180,
    "TWO independent oracles are required:\n"
    "(a) folding: $U U^{\\dagger} U = U$, so the ideal\n"
    "distribution must be unchanged;\n"
    "(b) REM: unequal response matrices, because\n"
    "at $p=0$ oracle (a) is blind to Defect 2.",
    BLUE, "#eef6ff", fs=6.1)

ax.text(0.5, 0.958, "Budget-matched ZNE / REM pipeline: two integration defect sites",
        ha="center", fontsize=9.0, fontweight="bold")
ax.text(0.5, 0.022,
        "Budget rule: every method spends the same total shots $B$  "
        "(unmitigated $B$; ZNE $B/3$ per scale; REM $0.8B$ circuits $+\\,0.2B$ calibration)",
        ha="center", fontsize=6.6, color=GREY)

for ext in ("pdf", "png"):
    fig.savefig(FIG/f"fig0_pipeline.{ext}", dpi=300, bbox_inches="tight", facecolor="white")
print("wrote figures/fig0_pipeline.pdf and .png")
