"""
Generates Figure 6 for the paper: a three-band heatmap comparing
Band A (structural inclusion % in the effort-framed WordProc subset, n=49),
Band B (aggregated human MoSCoW "Must" %, 12 evaluators, n=42 requirement blocks),
and Band C (divergence signal, Band A - Band B).

Input : band_abc_FINAL_n49.csv
Output: figure6_bands.pdf and figure6_bands.png (300 dpi)

Usage:
    python3 generate_figure6_bands.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# ---------------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------------
df = pd.read_csv("band_abc_FINAL_n49.csv").sort_values("mapped_req_42")

labels = df["official_name"].tolist()
band_a = df["band_a_pct"].to_numpy()
band_b = df["band_b_pct"].to_numpy()
band_c = df["band_c_delta"].to_numpy()

n = len(labels)

# ---------------------------------------------------------------------------
# 2. Build the figure: 3 stacked heatmap rows sharing the x-axis
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(
    3, 1, figsize=(16, 5.2), sharex=True,
    gridspec_kw={"height_ratios": [1, 1, 1], "hspace": 0.15}
)

# --- Band A: structural inclusion % (sequential colormap, 0-100) ---
ax = axes[0]
im_a = ax.imshow(
    band_a.reshape(1, -1), aspect="auto", cmap="viridis",
    vmin=0, vmax=100
)
ax.set_yticks([0]); ax.set_yticklabels(["Band A\n(Structural %)"], fontsize=9)
cbar_a = fig.colorbar(im_a, ax=ax, fraction=0.02, pad=0.01)
cbar_a.ax.tick_params(labelsize=7)

# --- Band B: human MoSCoW "Must" % (sequential colormap, 0-100) ---
ax = axes[1]
im_b = ax.imshow(
    band_b.reshape(1, -1), aspect="auto", cmap="viridis",
    vmin=0, vmax=100
)
ax.set_yticks([0]); ax.set_yticklabels(["Band B\n(Human Must %)"], fontsize=9)
cbar_b = fig.colorbar(im_b, ax=ax, fraction=0.02, pad=0.01)
cbar_b.ax.tick_params(labelsize=7)

# --- Band C: divergence signal (diverging colormap, centered at 0) ---
ax = axes[2]
max_abs = np.max(np.abs(band_c))
im_c = ax.imshow(
    band_c.reshape(1, -1), aspect="auto", cmap="RdBu_r",
    vmin=-max_abs, vmax=max_abs
)
ax.set_yticks([0]); ax.set_yticklabels(["Band C\n(A - B Delta)"], fontsize=9)
cbar_c = fig.colorbar(im_c, ax=ax, fraction=0.02, pad=0.01)
cbar_c.ax.tick_params(labelsize=7)

# ---------------------------------------------------------------------------
# 3. X-axis: requirement names, rotated for legibility
# ---------------------------------------------------------------------------
axes[-1].set_xticks(range(n))
axes[-1].set_xticklabels(labels, rotation=90, fontsize=7, ha="center")

# Remove per-row x tick marks on the top two rows (they share the bottom axis)
for ax in axes[:-1]:
    ax.set_xticks(range(n))
    ax.set_xticklabels([])
    ax.tick_params(axis="x", length=0)

for ax in axes:
    ax.set_xlim(-0.5, n - 0.5)

# fig.suptitle(
#    "Requirement-level comparison: structural inclusion (Band A) vs. "
#    "human MoSCoW priority (Band B) and their divergence (Band C)\n"
#    r"Spearman $\rho$ = 0.157, $p$ = 0.320, $n$ = 42; "
#    r"Fleiss' $\kappa$ (human agreement, binary Must/Not-Must) = 0.265",
#    fontsize=10, y=1.04
#)



plt.tight_layout()
fig.savefig("figure6_bands.pdf", bbox_inches="tight", dpi=300)
fig.savefig("figure6_bands.png", bbox_inches="tight", dpi=300)
print("Saved figure6_bands.pdf and figure6_bands.png")
