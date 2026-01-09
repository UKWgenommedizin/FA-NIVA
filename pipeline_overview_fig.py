#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 09:29:11 2024

@author: jiangyanyu
"""

import matplotlib.pyplot as plt

# Define nodes and their positions
nodes = {
    "fast5": (1, 4),
    "pod5": (0.3, 3.5),
    "bam": (2, 3.5),
    "dorado": (1, 3),
    "pycoQC": (1, 2),
    "pbmm2": (2, 2),
    "sawfish": (3, 3),
    "AnnotSV": (4, 2),
    "WhatsHap": (5.5, 2),
    "DeepVariant": (3, 1),
}

# Define edges (connections)
edges = [
    ("fast5", "dorado"),
    ("pod5", "dorado"),
    ("bam", "pbmm2"),
    ("dorado", "pycoQC"),
    ("pycoQC", "pbmm2"),
    ("pbmm2", "sawfish"),
    ("pbmm2", "DeepVariant"),
    ("sawfish", "AnnotSV"),
    ("DeepVariant", "AnnotSV"),
]

# Define special edges (square stepwise connections)
square_edges = [
    
    ("sawfish", "WhatsHap"),
    ("DeepVariant", "WhatsHap"),
]

# Nodes with background color
filled_nodes = {"fast5": "lightgrey", "pod5": "lightgrey", "bam": "lightgrey"}

# Initialize the plot
fig, ax = plt.subplots(figsize=(9, 5))

# Plot straight-line edges
for start, end in edges:
    x1, y1 = nodes[start]
    x2, y2 = nodes[end]
    ax.plot([x1, x2], [y1, y2], color="green", linewidth=1)

# Plot stepwise square edges
for start, end in square_edges:
    x1, y1 = nodes[start]
    x2, y2 = nodes[end]
    mid_x = (x2 + x2) / 2  # Midpoint for stepwise effect
    ax.plot([x1, mid_x, mid_x, x2], [y1, y1, y2, y2], color="green", linewidth=1)

# Plot nodes
for label, (x, y) in nodes.items():
    if label in filled_nodes:
        ax.scatter(x, y, s=100, color="red", zorder=3)  # Node with background
        ax.text(
            x, y, label, fontsize=15, ha="center", va="center", color="black", zorder=4,
            bbox=dict(boxstyle="circle", facecolor=filled_nodes[label], edgecolor="green")
        )
    else:
        ax.text(
            x, y, label, fontsize=15, ha="center", va="center", color="black", zorder=2,
            bbox=dict(boxstyle="square", facecolor="white", edgecolor="green", linewidth=1)
        )

# Add "FA-NIVA" text at coordinates (3, 5)
ax.text(3.5, 4.5, "FA-NIVA", fontsize=25, ha="center", va="center", color="green", zorder=4)
ax.text(3.5, 4.2, "Fanconi anemia – Nanopore Indel and Variant Analysis", fontsize=11, ha="center", va="center", color="green", zorder=4)

# Customize plot appearance
ax.set_xlim(0, 7)
ax.set_ylim(0, 5)
ax.axis("off")  # Hide axes

# Save and show the figure
plt.savefig("workflow_complete_graph.png", dpi=300)
plt.show()
