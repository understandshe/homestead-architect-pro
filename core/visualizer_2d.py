# core/visualizer_2d.py

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from io import BytesIO


class Visualizer2D:
    def create(self, layout: dict, answers: dict) -> BytesIO:

        L = layout["dimensions"]["L"]
        W = layout["dimensions"]["W"]

        fig, ax = plt.subplots(figsize=(24, 18), dpi=200)
        ax.set_facecolor("#f2f5f2")

        # ---- ZONES ----
        for zid, pos in layout.get("zone_positions", {}).items():
            ax.add_patch(Rectangle(
                (pos["x"], pos["y"]),
                pos["width"],
                pos["height"],
                edgecolor="#333",
                facecolor="#cfe8c6",
                alpha=0.5
            ))

        # ---- HOUSE ----
        hx, hy = L * 0.4, W * 0.45
        ax.add_patch(Rectangle((hx, hy), L*0.2, W*0.15,
                               facecolor="#ddd", edgecolor="black", linewidth=2))

        # ---- TREES ----
        for t in layout.get("tree_placements", []):
            ax.add_patch(Circle((t["x"], t["y"]), 5,
                                facecolor="green", edgecolor="darkgreen"))

        # ---- SIMPLE ROAD ----
        ax.plot([hx + L*0.1, hx + L*0.1], [0, hy],
                linewidth=10, color="#c2a57a")

        # ---- FINAL ----
        ax.set_xlim(0, L)
        ax.set_ylim(0, W)
        ax.set_aspect("equal")
        ax.axis("off")

        buf = BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        buf.seek(0)
        plt.close()

        return buf
