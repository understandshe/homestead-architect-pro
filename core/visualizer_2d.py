import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrow, Polygon
from matplotlib.lines import Line2D
from io import BytesIO
import numpy as np


class Visualizer2DPremium:
    """
    Rule-based premium site plan renderer
    - stable layout
    - feature-based drawing
    - road hierarchy
    - water + slope logic
    - print ready
    """

    # --------------------------
    # PUBLIC ENTRY
    # --------------------------
    def create(self, layout: dict, answers: dict) -> BytesIO:

        L = layout["dimensions"]["L"]
        W = layout["dimensions"]["W"]

        fig, ax = plt.subplots(figsize=(24, 18), dpi=200)
        ax.set_facecolor("#f4f7f4")

        # ---------------------------------
        # 1. DRAW ZONES
        # ---------------------------------
        self._draw_zones(ax, layout)

        # ---------------------------------
        # 2. HOUSE
        # ---------------------------------
        hx, hy, hw, hh = self._house_bbox(layout, L, W)
        self._draw_house(ax, hx, hy, hw, hh)

        # ---------------------------------
        # 3. STRUCTURES (FROM USER INPUT)
        # ---------------------------------
        structures = self._generate_structures(layout, answers)
        self._draw_structures(ax, structures)

        # ---------------------------------
        # 4. ROADS (SMART SYSTEM)
        # ---------------------------------
        self._draw_roads(ax, structures, hx + hw/2, hy)

        # ---------------------------------
        # 5. WATER + SLOPE
        # ---------------------------------
        self._draw_water_and_slope(ax, layout, answers)

        # ---------------------------------
        # 6. TREES (CLUSTERS)
        # ---------------------------------
        self._draw_tree_clusters(ax, layout, answers)

        # ---------------------------------
        # 7. LABELS
        # ---------------------------------
        self._draw_labels(ax, layout)

        # ---------------------------------
        # 8. COMPASS + SCALE
        # ---------------------------------
        self._draw_compass(ax, L, W)
        ax.text(L/2, -W*0.08, f"{int(L)} ft", ha="center", fontsize=12)

        # ---------------------------------
        # LIMITS
        # ---------------------------------
        margin = max(L, W) * 0.2
        ax.set_xlim(-margin, L + margin)
        ax.set_ylim(-margin, W + margin)
        ax.set_aspect("equal")
        ax.axis("off")

        # ---------------------------------
        # EXPORT
        # ---------------------------------
        buf = BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        buf.seek(0)
        plt.close()

        return buf

    # --------------------------
    # ZONES
    # --------------------------
    def _draw_zones(self, ax, layout):

        colors = {
            "z0": "#e1e8ed",
            "z1": "#d4edc9",
            "z2": "#8fbc8f",
            "z3": "#e9d8a6",
            "z4": "#cde3e3"
        }

        for zid, pos in layout.get("zone_positions", {}).items():
            ax.add_patch(Rectangle(
                (pos["x"], pos["y"]),
                pos["width"],
                pos["height"],
                facecolor=colors.get(zid, "#ccc"),
                edgecolor="#4f5b4f",
                linewidth=2,
                zorder=1
            ))

    # --------------------------
    # HOUSE
    # --------------------------
    def _draw_house(self, ax, x, y, w, h):

        # shadow
        ax.add_patch(Rectangle((x+3, y-3), w, h,
            color="black", alpha=0.1, zorder=2))

        # main
        ax.add_patch(Rectangle((x, y), w, h,
            facecolor="#d0d7de", edgecolor="#333", linewidth=3, zorder=5))

        # roof line
        ax.plot([x, x+w/2, x+w], [y+h, y+h+8, y+h], color="#555", linewidth=2)

    # --------------------------
    # STRUCTURES FROM INPUT
    # --------------------------
    def _generate_structures(self, layout, answers):

        structures = []
        zones = layout.get("zone_positions", {})

        # goat paddock
        if "Goats" in answers.get("livestock", []):
            z = zones.get("z3")
            if z:
                structures.append({
                    "type": "goat",
                    "x": z["x"] + z["width"]*0.3,
                    "y": z["y"] + z["height"]*0.5
                })

        # fish pond
        if "Fish" in answers.get("livestock", []):
            z = zones.get("z2")
            if z:
                structures.append({
                    "type": "fish",
                    "x": z["x"] + z["width"]*0.5,
                    "y": z["y"] + z["height"]*0.3
                })

        return structures

    # --------------------------
    # DRAW STRUCTURES
    # --------------------------
    def _draw_structures(self, ax, structures):

        for s in structures:

            x, y = s["x"], s["y"]

            if s["type"] == "goat":
                ax.add_patch(Rectangle((x, y), 30, 25,
                    facecolor="#b58b5b", edgecolor="#5a3e2b", linewidth=2, zorder=6))
                ax.text(x+15, y+12, "Goat", ha="center")

            elif s["type"] == "fish":
                pts = [(x, y), (x+10, y+6), (x+6, y+16), (x-5, y+12)]
                ax.add_patch(Polygon(pts,
                    facecolor="#5dade2", edgecolor="#1f618d", linewidth=2, zorder=6))
                ax.text(x, y, "Pond", ha="center")

    # --------------------------
    # ROADS
    # --------------------------
    def _draw_roads(self, ax, structures, hx, hy):

        for s in structures:
            sx, sy = s["x"], s["y"]

            ax.plot([hx, sx], [hy, hy],
                color="#d2b48c", linewidth=10, zorder=3, solid_capstyle="round")

            ax.plot([sx, sx], [hy, sy],
                color="#d2b48c", linewidth=6, zorder=3, solid_capstyle="round")

    # --------------------------
    # WATER + SLOPE
    # --------------------------
    def _draw_water_and_slope(self, ax, layout, answers):

        slope = answers.get("slope")

        if slope and slope != "Flat":
            ax.add_patch(FancyArrow(
                20, 20, 40, 20,
                width=2, color="blue", alpha=0.5
            ))

    # --------------------------
    # TREES
    # --------------------------
    def _draw_tree_clusters(self, ax, layout, answers):

        np.random.seed(42)

        for t in layout.get("tree_placements", []):
            r = np.random.uniform(4, 7)
            ax.add_patch(Circle(
                (t["x"], t["y"]),
                r,
                facecolor="#2e7d32",
                edgecolor="#1b5e20",
                zorder=4
            ))

    # --------------------------
    # LABELS
    # --------------------------
    def _draw_labels(self, ax, layout):

        for zid, pos in layout.get("zone_positions", {}).items():
            ax.text(
                pos["x"] + pos["width"]/2,
                pos["y"] + pos["height"]/2,
                zid.upper(),
                ha="center",
                fontsize=12,
                weight="bold"
            )

    # --------------------------
    # COMPASS
    # --------------------------
    def _draw_compass(self, ax, L, W):

        cx, cy = L*0.9, W*0.1
        ax.add_patch(Circle((cx, cy), 15, facecolor="white", edgecolor="black"))
        ax.add_patch(FancyArrow(cx, cy, 0, 10, width=2, color="red"))
        ax.text(cx, cy+18, "N", ha="center")

    # --------------------------
    # HOUSE POSITION
    # --------------------------
    def _house_bbox(self, layout, L, W):

        return (L*0.35, W*0.45, L*0.3, W*0.18)
