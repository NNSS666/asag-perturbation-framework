"""Generate Figure 1: framework overview + headline finding.

Two-panel layout:
  (a) Linear pipeline making the self-comparison explicit:
      Student answer -> three perturbation families ->
      Original + Perturbed answers -> Grader (same model on both) ->
      Score delta -> IVR / SSR / ASR.
  (b) Per-type miss rates with 95% bootstrap CI under L0 (no reference)
      and L1 (with reference). Delta annotations on each pair show the
      direction and magnitude of the L1 effect (green = improvement,
      red = the L1 deletion paradox).

Output: paper/figures/figure_1_overview.png (300 dpi).
"""

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "paper/figures/figure_1_overview.png"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})

INVARIANCE = "#4C72B0"
SENSITIVITY = "#DD8452"
GAMING = "#C44E52"
GREEN = "#2E8B57"
NEUTRAL = "#333333"


fig = plt.figure(figsize=(11, 7.0))
gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.0], hspace=0.45)

# ============== Panel (a): linear pipeline =================================
ax_top = fig.add_subplot(gs[0])
ax_top.set_xlim(0, 11)
ax_top.set_ylim(0, 4.6)
ax_top.set_axis_off()
ax_top.text(0.05, 4.45, "(a) Framework overview",
            fontsize=11, fontweight="bold", ha="left", va="top")


def box(ax, x, y, w, h, label, color, fontcolor="white", fontsize=9, fw="bold"):
    rect = mpatches.FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.08",
        linewidth=0, facecolor=color,
    )
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h / 2, label,
            ha="center", va="center", color=fontcolor, fontsize=fontsize, fontweight=fw)


def arrow(ax, x1, y1, x2, y2, color=NEUTRAL, lw=1.5):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=color, lw=lw))


yc = 2.3

# 1) Student answer
sa_x, sa_w = 0.2, 1.4
box(ax_top, sa_x, yc - 0.45, sa_w, 0.9, "Student\nanswer", NEUTRAL, fontsize=9)

# 2) Three perturbation family boxes (stacked, name only)
fam_x, fam_w, fam_h = 2.2, 1.7, 0.7
fam_gap = 0.12
for i, (label, color) in enumerate([
    ("INVARIANCE", INVARIANCE),
    ("SENSITIVITY", SENSITIVITY),
    ("GAMING", GAMING),
]):
    fy = (yc + 0.95) - i * (fam_h + fam_gap)
    box(ax_top, fam_x, fy, fam_w, fam_h, label, color, fontsize=9)

# Direct diagonal arrows from student to each family
for i in range(3):
    fy = (yc + 0.95) - i * (fam_h + fam_gap) + fam_h / 2
    arrow(ax_top, sa_x + sa_w + 0.05, yc, fam_x - 0.05, fy)

# 3) Pair: Original + Perturbed
pair_x = 4.55
pair_w = 1.7
box(ax_top, pair_x, yc + 0.10, pair_w, 0.65, "Original answer", "#888", fontsize=8.5)
box(ax_top, pair_x, yc - 0.75, pair_w, 0.65, "Perturbed answer", "#888", fontsize=8.5)

# 3 arrows from families converging into the pair
for i in range(3):
    fy = (yc + 0.95) - i * (fam_h + fam_gap) + fam_h / 2
    arrow(ax_top, fam_x + fam_w + 0.05, fy, pair_x - 0.05, yc)

# 4) Grader (single model applied to BOTH inputs)
gr_x = 6.65
gr_w = 1.7
box(ax_top, gr_x, yc - 0.45, gr_w, 0.9, "Grader\n(ML  |  LLM)", NEUTRAL, fontsize=9)
ax_top.text(gr_x + gr_w / 2, yc - 0.65, "same model on both",
            ha="center", va="top", fontsize=7.5, style="italic", color="#555")
arrow(ax_top, pair_x + pair_w + 0.05, yc + 0.42, gr_x - 0.05, yc + 0.10)
arrow(ax_top, pair_x + pair_w + 0.05, yc - 0.42, gr_x - 0.05, yc - 0.10)

# 5) Score delta
delta_x = 8.65
delta_w = 0.85
box(ax_top, delta_x, yc - 0.35, delta_w, 0.7, "Δ score", "#555", fontsize=9)
arrow(ax_top, gr_x + gr_w + 0.05, yc, delta_x - 0.05, yc)

# 6) Metrics (stacked, with direct diagonal arrows from delta)
m_x, m_w, m_h = 9.85, 1.05, 0.55
for i, (label, color) in enumerate([
    ("IVR", INVARIANCE),
    ("SSR", SENSITIVITY),
    ("ASR", GAMING),
]):
    my = yc + 0.7 - i * 0.7
    box(ax_top, m_x, my - m_h / 2, m_w, m_h, label, color, fontsize=10)
    arrow(ax_top, delta_x + delta_w + 0.05, yc, m_x - 0.05, my)

ax_top.text(6.0, 0.50,
            "Invariance: synonym, typo. Sensitivity: negation, deletion, contradiction. "
            "Gaming: keyword echoing, wrong extension.",
            ha="center", va="bottom", fontsize=8, color="#555")
ax_top.text(6.0, 0.10,
            "The same grader scores both inputs; metrics read the score difference.",
            ha="center", va="bottom", fontsize=8, style="italic", color="#555")


# ============== Panel (b): gradient with delta annotations =================
ax_bot = fig.add_subplot(gs[1])

types = ["Contradiction", "Negation", "Deletion"]
miss_l0 = [43.0, 52.2, 68.7]
miss_l1 = [39.6, 41.8, 74.8]
ci_l0 = [(41.7, 44.3), (50.8, 53.5), (67.4, 70.0)]
ci_l1 = [(38.3, 40.9), (40.5, 43.2), (73.6, 76.0)]
deltas = [m1 - m0 for m0, m1 in zip(miss_l0, miss_l1)]

err_l0 = ([m - lo for m, (lo, _) in zip(miss_l0, ci_l0)],
          [hi - m for m, (_, hi) in zip(miss_l0, ci_l0)])
err_l1 = ([m - lo for m, (lo, _) in zip(miss_l1, ci_l1)],
          [hi - m for m, (_, hi) in zip(miss_l1, ci_l1)])

x = np.arange(len(types))
w = 0.36
ax_bot.bar(x - w / 2, miss_l0, w, label="L0  (no reference)",
           color=SENSITIVITY, alpha=0.55, edgecolor="white",
           yerr=err_l0, capsize=3, ecolor=NEUTRAL)
ax_bot.bar(x + w / 2, miss_l1, w, label="L1  (with reference)",
           color=SENSITIVITY, alpha=1.0, edgecolor="white",
           yerr=err_l1, capsize=3, ecolor=NEUTRAL)

for xi, (m0, m1) in enumerate(zip(miss_l0, miss_l1)):
    ax_bot.text(xi - w / 2, m0 + 1.7, f"{m0:.1f}", ha="center", va="bottom", fontsize=8.5)
    ax_bot.text(xi + w / 2, m1 + 1.7, f"{m1:.1f}", ha="center", va="bottom", fontsize=8.5)

for xi, d in enumerate(deltas):
    sign = "+" if d > 0 else "−"
    color = GAMING if d > 0 else GREEN
    label = f"L1 {sign}{abs(d):.0f} pp"
    top = max(miss_l0[xi], miss_l1[xi]) + 9
    ax_bot.annotate(
        label,
        xy=(xi, top),
        ha="center", va="bottom",
        fontsize=8.5, fontweight="bold", color=color,
    )
    y0 = miss_l0[xi] + 0.5
    y1 = miss_l1[xi] + 0.5
    ax_bot.annotate(
        "",
        xy=(xi + w / 2, y1),
        xytext=(xi - w / 2, y0),
        arrowprops=dict(arrowstyle="->", color=color, lw=1.2, alpha=0.85),
    )

ax_bot.set_xticks(x)
ax_bot.set_xticklabels(types)
ax_bot.set_ylabel("Miss rate  (% same-score pairs)")
ax_bot.set_ylim(0, 95)
ax_bot.set_title(
    "(b) Sensitivity-blindness gradient — adding the reference answer (L1) "
    "helps on contradiction and negation but hurts on deletion",
    loc="left", fontsize=9.5, pad=8,
)
ax_bot.legend(loc="upper left", frameon=False, fontsize=8.5)
ax_bot.grid(axis="y", alpha=0.25, linestyle=":")
ax_bot.set_axisbelow(True)

fig.savefig(OUT)
print(f"Saved: {OUT}")
