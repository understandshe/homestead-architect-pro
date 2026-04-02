import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from io import BytesIO
import numpy as np


class Visualizer2D:

    def create(self, layout: dict, answers: dict) -> BytesIO:

        L = layout['dimensions']['L']
        W = layout['dimensions']['W']

        fig, ax = plt.subplots(figsize=(24, 18), dpi=200)
        ax.set_facecolor('#6FAF73')

        # --------------------------
        # ZONES
        # --------------------------
        zone_colors = {
            'z0': '#F0EAD6',
            'z1': '#C5E1A5',
            'z2': '#388E3C',
            'z3': '#FFF9C4',
            'z4': '#A5D6A7',
        }

        for zid, pos in layout.get('zone_positions', {}).items():
            ax.add_patch(Rectangle(
                (pos['x'], pos['y']),
                pos['width'],
                pos['height'],
                facecolor=zone_colors.get(zid, '#ccc'),
                edgecolor='#444',
                linewidth=1.5,
                alpha=0.4
            ))

        # --------------------------
        # HOUSE
        # --------------------------
        hx, hy, hw, hh = self._house_bbox(layout, L, W)

        ax.add_patch(Rectangle(
            (hx, hy), hw, hh,
            facecolor='#ECEFF1',
            edgecolor='#444',
            linewidth=3,
            zorder=5
        ))

        # --------------------------
        # CLEAN PATH SYSTEM
        # --------------------------
        center_x = hx + hw / 2
        cross_y = hy + hh * 0.5

        main_w = max(10, min(L, W) * 0.025)
        sec_w = main_w * 0.7

        path_color = '#DCC8A8'

        # Entry path
        ax.plot(
            [center_x, center_x],
            [0, hy],
            color=path_color,
            linewidth=main_w,
            solid_capstyle='round',
            zorder=3
        )

        # Cross path
        ax.plot(
            [L * 0.2, L * 0.8],
            [cross_y, cross_y],
            color=path_color,
            linewidth=sec_w,
            solid_capstyle='round',
            zorder=3
        )

        # --------------------------
        # TREES
        # --------------------------
        np.random.seed(42)

        for t in layout.get('tree_placements', []):
            ax.add_patch(Circle(
                (t['x'], t['y']),
                6,
                facecolor='#2E7D32',
                edgecolor='#1B5E20',
                alpha=0.9,
                zorder=4
            ))

        # --------------------------
        # KITCHEN BEDS (LIMITED)
        # --------------------------
        if 'z1' in layout.get('zone_positions', {}):
            z = layout['zone_positions']['z1']

            pad = 10
            bed_w = 15
            bed_h = 30

            n_beds = min(8, int((z['width'] - 2 * pad) / (bed_w + 5)))

            for i in range(n_beds):
                bx = z['x'] + pad + i * (bed_w + 5)
                by = z['y'] + pad

                ax.add_patch(Rectangle(
                    (bx, by),
                    bed_w,
                    bed_h,
                    facecolor='#5A3E2B',
                    edgecolor='black',
                    zorder=5
                ))

        # --------------------------
        # LIMITS + MARGIN
        # --------------------------
        margin = max(L, W) * 0.25

        ax.set_xlim(-margin, L + margin)
        ax.set_ylim(-margin, W + margin)

        ax.set_aspect('equal')
        ax.axis('off')

        # --------------------------
        # SAVE HIGH QUALITY
        # --------------------------
        buf = BytesIO()

        plt.savefig(
            buf,
            format='png',
            dpi=300,
            bbox_inches='tight'
        )

        buf.seek(0)
        plt.close()

        return buf

    # --------------------------
    # HOUSE POSITION
    # --------------------------
    def _house_bbox(self, layout, L, W):

        pos = layout.get('house_position', 'Center')

        mapping = {
            'Center': (L * 0.35, W * 0.42, L * 0.30, W * 0.20),
            'North': (L * 0.30, W * 0.80, L * 0.35, W * 0.15),
            'South': (L * 0.30, W * 0.05, L * 0.35, W * 0.15),
            'East': (L * 0.75, W * 0.35, L * 0.20, W * 0.25),
            'West': (L * 0.05, W * 0.35, L * 0.20, W * 0.25),
        }

        return mapping.get(pos, mapping['Center'])
