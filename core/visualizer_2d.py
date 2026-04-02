import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrow
from matplotlib.lines import Line2D
from io import BytesIO
import numpy as np


class Visualizer2D:

    # -----------------------------
    # ENTRY
    # -----------------------------
    def create(self, layout: dict, answers: dict) -> BytesIO:

        L = layout["dimensions"]["L"]
        W = layout["dimensions"]["W"]

        fig, ax = plt.subplots(figsize=(24, 18), dpi=200)
        ax.set_facecolor("#e9efe9")

        # -----------------------------
        # ZONES (clean + readable)
        # -----------------------------
        zone_colors = {
            "z0": "#dfe7ec",  # residential
            "z1": "#cfe8b4",  # kitchen
            "z2": "#8fbc8f",  # forest
            "z3": "#e6d3a3",  # pasture
            "z4": "#c6e2d9",  # buffer
        }

        for zid, pos in layout.get("zone_positions", {}).items():
            ax.add_patch(Rectangle(
                (pos["x"], pos["y"]),
                pos["width"],
                pos["height"],
                facecolor=zone_colors.get(zid, "#ccc"),
                edgecolor="#4f5b4f",
                linewidth=2,
                zorder=1
            ))

            # label
            ax.text(
                pos["x"] + pos["width"]/2,
                pos["y"] + pos["height"]/2,
                f"{zid.upper()}",
                ha="center",
                va="center",
                fontsize=14,
                weight="bold",
                color="#2f3e2f"
            )

        # -----------------------------
        # HOUSE
        # -----------------------------
        hx, hy, hw, hh = self._house_bbox(layout, L, W)

        ax.add_patch(Rectangle(
            (hx, hy), hw, hh,
            facecolor="#d6dbe0",
            edgecolor="#333",
            linewidth=3,
            zorder=5
        ))

        # -----------------------------
        # STRUCTURES (REAL SHAPES)
        # -----------------------------
        structures = layout.get("structures", [])

        for s in structures:
            self._draw_structure(ax, s)

        # -----------------------------
        # ROADS (AUTO CONNECTION)
        # -----------------------------
        self._draw_roads(ax, structures, hx + hw/2, hy)

        # -----------------------------
        # TREES (cluster)
        # -----------------------------
        self._draw_trees(ax, layout.get("tree_placements", []))

        # -----------------------------
        # COMPASS
        # -----------------------------
        self._draw_compass(ax, L, W)

        # -----------------------------
        # SCALE
        # -----------------------------
        ax.text(L/2, -W*0.08, f"{int(L)} units", ha="center", fontsize=12)

        # -----------------------------
        # LIMITS
        # -----------------------------
        margin = max(L, W) * 0.2
        ax.set_xlim(-margin, L + margin)
        ax.set_ylim(-margin, W + margin)
        ax.set_aspect("equal")
        ax.axis("off")

        # -----------------------------
        # EXPORT
        # -----------------------------
        buf = BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        buf.seek(0)
        plt.close()

        return buf

    # -----------------------------
    # STRUCTURE DRAWER
    # -----------------------------
    def _draw_structure(self, ax, s):

        x, y = s["x"], s["y"]
        t = s["type"]

        if t == "goat_pen":
            ax.add_patch(Rectangle((x, y), 25, 20,
                facecolor="#b58b5b", edgecolor="#5a3e2b", linewidth=2, zorder=6))
            ax.text(x+12, y+10, "Goat", ha="center", fontsize=10)

        elif t == "fish_pond":
            ax.add_patch(Circle((x, y), 12,
                facecolor="#5dade2", edgecolor="#1f618d", linewidth=2, zorder=6))
            ax.text(x, y, "Fish", ha="center", fontsize=10)

        elif t == "greenhouse":
            ax.add_patch(Rectangle((x, y), 28, 18,
                facecolor="#d4efdf", edgecolor="#145a32", linewidth=2, zorder=6))
            ax.text(x+14, y+9, "GH", ha="center", fontsize=10)

        elif t == "solar":
            ax.add_patch(Rectangle((x, y), 20, 20,
                facecolor="#f7dc6f", edgecolor="#b7950b", linewidth=2, zorder=6))
            ax.text(x+10, y+10, "Solar", ha="center", fontsize=9)

        else:
            ax.add_patch(Rectangle((x, y), 15, 15,
                facecolor="#ccc", edgecolor="black", zorder=6))

    # -----------------------------
    # ROAD SYSTEM (SMART)
    # -----------------------------
    def _draw_roads(self, ax, structures, hx, hy):

        road_color = "#d2b48c"

        for s in structures:
            sx, sy = s["x"], s["y"]

            # L-shape connection (clean, realistic)
            ax.plot([hx, sx], [hy, hy],
                    color=road_color, linewidth=8, zorder=3, solid_capstyle="round")

            ax.plot([sx, sx], [hy, sy],
                    color=road_color, linewidth=8, zorder=3, solid_capstyle="round")

    # -----------------------------
    # TREES
    # -----------------------------
    def _draw_trees(self, ax, trees):

        np.random.seed(0)

        for t in trees:
            r = np.random.uniform(4, 7)
            ax.add_patch(Circle(
                (t["x"], t["y"]),
                r,
                facecolor="#2e7d32",
                edgecolor="#1b5e20",
                zorder=4
            ))

    # -----------------------------
    # COMPASS
    # -----------------------------
    def _draw_compass(self, ax, L, W):

        cx, cy = L*0.9, W*0.1

        ax.add_patch(Circle((cx, cy), 15, facecolor="white", edgecolor="black"))
        ax.add_patch(FancyArrow(cx, cy, 0, 10, width=2, color="red"))

        ax.text(cx, cy+18, "N", ha="center", fontsize=12)

    # -----------------------------
    # HOUSE POSITION
    # -----------------------------
    def _house_bbox(self, layout, L, W):

        pos = layout.get("house_position", "Center")

        mapping = {
            "Center": (L*0.35, W*0.45, L*0.3, W*0.18),
            "North": (L*0.3, W*0.8, L*0.35, W*0.15),
            "South": (L*0.3, W*0.05, L*0.35, W*0.15),
            "East": (L*0.75, W*0.35, L*0.2, W*0.25),
            "West": (L*0.05, W*0.35, L*0.2, W*0.25),
        }

        return mapping.get(pos, mapping["Center"])
