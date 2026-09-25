#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 09:29:11 2024

@author: jiangyanyu
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import numpy as np

def get_edge_point(start, end, box_width=0.65, box_height=0.22):
    """Return points just outside the rectangular node boxes."""

    x1, y1 = nodes[start]
    x2, y2 = nodes[end]

    dx = x2 - x1
    dy = y2 - y1

    # Normalize direction
    length = np.sqrt(dx**2 + dy**2)
    dx /= length
    dy /= length

    # Find intersection with rectangular boundary
    scale_x = (box_width / 2) / abs(dx) if dx != 0 else np.inf
    scale_y = (box_height / 2) / abs(dy) if dy != 0 else np.inf

    scale = min(scale_x, scale_y) 

    start_point = (
        x1 + dx * scale ,
        y1 + dy * scale*2 
    )

    end_point = (
        x2 - dx * scale*2,
        y2 - dy * scale*2
    )

    return start_point, end_point

# Define nodes and their positions
nodes = {
    ".fast5": (1, 4),
    ".pod5": (0.2, 3.5),
    ".bam": (2.4, 3.5),
    "dorado": (0.8, 2.9),

    "pycoQC": (0.8, 2),
    "pbmm2": (2.4, 2),

    "sawfish": (3.5, 3),
    "DeepVariant": (3.5, 1),
    "AnnotSV": (4.8, 2),
    "WhatsHap": (6.2, 2),
}

# Define edges (connections)
edges = [
    (".fast5", "dorado"),
    (".pod5", "dorado"),
    (".bam", "pbmm2"),
    ("dorado", "pycoQC"),
    ("pycoQC", "pbmm2"),
    ("pbmm2", "sawfish"),
    ("pbmm2", "DeepVariant"),
    ("sawfish", "AnnotSV"),
    ("DeepVariant", "AnnotSV")
]

# Define special edges (square stepwise connections)
square_edges = [
    
    ("sawfish", "WhatsHap"),
    ("DeepVariant", "WhatsHap"),
]

# Nodes with background color
filled_nodes = {".fast5": "lightgrey", ".pod5": "lightgrey", ".bam": "lightgrey"}

# Initialize the plot
fig, ax = plt.subplots(figsize=(9, 5))

# Plot normal arrowed edges
for start, end in edges:

    if start == "pycoQC" and end == "pbmm2":
        continue

    (x1, y1), (x2, y2) = get_edge_point(
        start,
        end,
        box_width=0.65,
        box_height=0.22
    )

    arrow = FancyArrowPatch(
        (x1, y1),
        (x2, y2),
        arrowstyle="->",
        mutation_scale=12,
        linewidth=1,
        color="green",
        zorder=5
    )

    ax.add_patch(arrow)


# Custom pycoQC -> pbmm2 arrow
x1, y1 = nodes["pycoQC"]
x2, y2 = nodes["pbmm2"]

arrow = FancyArrowPatch(
    (x1 + 0.50, y1),   # start at right edge of pycoQC
    (x2 - 0.40, y2),   # stop at left edge of pbmm2
    arrowstyle="->",
    mutation_scale=12,
    linewidth=1,
    color="green",
    zorder=5
)

ax.add_patch(arrow)

# Plot stepwise square edges
for start, end in square_edges:
    x1, y1 = nodes[start]
    x2, y2 = nodes[end]
    mid_x = x2  # Midpoint for stepwise effect
    ax.plot([x1, mid_x, mid_x, x2], [y1, y1, y2, y2], color="green", linewidth=1)

    # Manually add arrowhead: sawfish -> WhatsHap
ax.annotate(
    "",
    xy=(6.2, 2.2),
    xytext=(6.2, 2.5),
    arrowprops=dict(
        arrowstyle="->",
        color="green",
        linewidth=1,
        mutation_scale=12
    )
)


# Manually add arrowhead: DeepVariant -> WhatsHap
ax.annotate(
    "",
    xy=(6.2, 1.8),
    xytext=(6.2, 1.3),
    arrowprops=dict(
        arrowstyle="->",
        color="green",
        linewidth=1,
        mutation_scale=12
    )
)
    

# Plot nodes
for label, (x, y) in nodes.items():
    if label in filled_nodes:
        #ax.scatter(x, y, s=100, color="red", zorder=3)  # Node with background
        ax.text(
            x, y, label, fontsize=15, ha="center", va="center", color="black", zorder=4,
            bbox=dict(boxstyle="circle", facecolor="none", edgecolor="none")
        )
    else:
        ax.text(
            x, y, label, fontsize=15, ha="center", va="center", color="black", zorder=2,
            bbox=dict(boxstyle="square", facecolor="white", edgecolor="green", linewidth=1)
        )

# Add "FA-NIVA" text at coordinates (3, 5)
ax.text(3.5, 4.9, "FA-NIVA", fontsize=25, ha="center", va="center", color="green", zorder=4)
ax.text(3.5, 4.6, "Flexible and  Automated – Nextflow-based Integrated Variant Analysis", fontsize=11, ha="center", va="center", color="green", zorder=4)

# Customize plot appearance
ax.set_xlim(0, 7)
ax.set_ylim(0, 5)
ax.axis("off")  # Hide axes

# Save and show the figure
plt.savefig("workflow_complete_graph.png", dpi=300)
plt.show()
