"""
Professional 2D Architectural Visualizer
Homestead Architect Pro 2026 — Global Edition
Fixes: solar panels → blue, house/zone label overlap, livestock housing
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import (
    FancyBboxPatch, Circle, Rectangle, Polygon, Arc, PathPatch
)
from matplotlib.path import Path
import matplotlib.patheffects as pe
import numpy as np
from io import BytesIO


class Visualizer2D:
    """Professional architectural site-plan renderer."""

    def __init__(self):
        self.colors = {
            'residential': '#F5F5DC',
            'kitchen':     '#C8E6C9',
            'forest':      '#81C784',
            'pasture':     '#FFF9C4',
            'buffer':      '#E1BEE7',
            'water':       '#4FC3F7',
            'water_dark':  '#0288D1',
            'building':    '#8D6E63',
            'roof':        '#5D4037',
            'solar_panel': '#1565C0',   # ← FIXED: dark blue, not yellow
            'solar_frame': '#0D47A1',
            'solar_cell':  '#1976D2',
            'greenhouse':  '#E0F2F1',
            'livestock':   '#FFCCBC',
            'path':        '#D7CCC8',
            'fence':       '#795548',
        }
        self.zone_colors = {
            'z0': '#F5F5DC',
            'z1': '#C8E6C9',
            'z2': '#81C784',
            'z3': '#FFF9C4',
            'z4': '#E1BEE7',
        }
        self.zone_names = {
            'z0': 'ZONE 0\nRESIDENTIAL',
            'z1': 'ZONE 1\nKITCHEN GARDEN',
            'z2': 'ZONE 2\nFOOD FOREST',
            'z3': 'ZONE 3\nPASTURE / CROPS',
            'z4': 'ZONE 4\nBUFFER',
        }

    # ── Public API ─────────────────────────────────────────────────────────────
    def create(self, layout: dict, answers: dict) -> BytesIO:
        """Render professional site plan. Returns PNG bytes."""
        L = layout['dimensions']['L']
        W = layout['dimensions']['W']

        fig, ax = plt.subplots(figsize=(18, 14), dpi=150)
        fig.patch.set_facecolor('#FAFAFA')
        ax.set_facecolor('#EAF4FB')   # light sky – property background

        # ── Draw order (bottom → top) ─────────────────────────────────────
        self._draw_property_boundary(ax, L, W)

        if layout.get('slope', 'Flat') != 'Flat':
            self._draw_contour_lines(ax, L, W, layout['slope'])

        self._draw_zones(ax, layout, L, W)           # filled zone slabs
        self._draw_paths(ax, layout, L, W)            # footpaths
        self._draw_water_features(ax, layout, L, W)
        self._draw_utilities(ax, layout, L, W)        # solar, greenhouse
        self._draw_livestock_housing(ax, layout, L, W)
        self._draw_vegetation(ax, layout, L, W)       # trees
        self._draw_house(ax, layout, L, W)            # house on top
        self._draw_zone_labels(ax, layout, L, W)      # labels last (not behind house)

        # ── Cartographic elements ─────────────────────────────────────────
        self._add_north_arrow(ax, L, W)
        self._add_scale_bar(ax, L, W)
        self._add_legend(ax, L, W)
        self._add_dimensions(ax, L, W)
        self._add_title_block(ax, layout, L, W)

        margin = max(L, W) * 0.18
        ax.set_xlim(-margin, L + margin * 1.6)    # extra right for legend
        ax.set_ylim(-margin * 1.1, W + margin)
        ax.set_aspect('equal')
        ax.axis('off')

        plt.tight_layout(pad=0.5)

        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=200, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        buf.seek(0)
        plt.close(fig)
        return buf

    # ── Property boundary ──────────────────────────────────────────────────────
    def _draw_property_boundary(self, ax, L, W):
        # Outer boundary
        ax.add_patch(Rectangle(
            (0, 0), L, W,
            linewidth=3.5, edgecolor='#1A237E',
            facecolor='none', linestyle='-', zorder=2,
        ))
        # Corner monuments
        for i, (x, y) in enumerate([(0,0),(L,0),(L,W),(0,W)], 1):
            ax.add_patch(Circle(
                (x, y), min(L, W) * 0.012,
                facecolor='white', edgecolor='#1A237E',
                linewidth=2, zorder=10,
            ))
            ax.text(x, y, str(i), ha='center', va='center',
                    fontsize=7, fontweight='bold', zorder=11)

    # ── Contour lines ──────────────────────────────────────────────────────────
    def _draw_contour_lines(self, ax, L, W, slope):
        n = 5
        for i in range(1, n + 1):
            frac = i / (n + 1)
            if slope in ('South', 'North'):
                y = W * frac if slope == 'South' else W * (1 - frac)
                ax.plot([0, L], [y, y], color='#A5D6A7',
                        linestyle='--', linewidth=0.6, alpha=0.7, zorder=1)
                ax.text(L * 0.98, y, f'+{i}m', fontsize=6,
                        color='#388E3C', ha='right', va='bottom')
            else:
                x = L * frac if slope == 'East' else L * (1 - frac)
                ax.plot([x, x], [0, W], color='#A5D6A7',
                        linestyle='--', linewidth=0.6, alpha=0.7, zorder=1)

    # ── Zone fills (no labels here) ────────────────────────────────────────────
    def _draw_zones(self, ax, layout, L, W):
        for zone_id, pos in layout.get('zone_positions', {}).items():
            ax.add_patch(Rectangle(
                (pos['x'], pos['y']), pos['width'], pos['height'],
                facecolor=self.zone_colors.get(zone_id, '#CCCCCC'),
                edgecolor='#546E7A', linewidth=1.8,
                alpha=0.70, zorder=3,
            ))

    # ── Zone labels — placed AFTER house so they don't overlap ───────────────
    def _draw_zone_labels(self, ax, layout, L, W):
        """Smart label placement: avoids house footprint."""
        house_bbox = self._get_house_bbox(layout, L, W)

        for zone_id, pos in layout.get('zone_positions', {}).items():
            cx = pos['x'] + pos['width'] / 2
            cy = pos['y'] + pos['height'] / 2
            area = int(pos['width'] * pos['height'])

            # Check if centre is inside house; shift label if so
            if house_bbox and self._pt_in_rect(cx, cy, house_bbox):
                # Push label to right third of zone
                cx = pos['x'] + pos['width'] * 0.80
                cy = pos['y'] + pos['height'] * 0.50

            label = self.zone_names.get(zone_id, zone_id.upper())
            ax.text(
                cx, cy + 8, label,
                ha='center', va='center',
                fontsize=8.5, fontweight='bold',
                color='#1B5E20', zorder=12,
                bbox=dict(boxstyle='round,pad=0.3',
                          facecolor='white', edgecolor='#A5D6A7',
                          alpha=0.88, linewidth=1),
            )
            ax.text(
                cx, cy - 10, f'{area:,} sq.ft.',
                ha='center', va='center',
                fontsize=7.5, color='#33691E', zorder=12,
            )

    # ── House ──────────────────────────────────────────────────────────────────
    def _get_house_bbox(self, layout, L, W):
        pos = layout.get('house_position', 'Center')
        positions = {
            'North':  (L*0.30, W*0.82, L*0.40, W*0.12),
            'South':  (L*0.30, W*0.06, L*0.40, W*0.12),
            'East':   (L*0.75, W*0.35, L*0.20, W*0.30),
            'West':   (L*0.05, W*0.35, L*0.20, W*0.30),
            'Center': (L*0.35, W*0.40, L*0.30, W*0.20),
        }
        hx, hy, hw, hh = positions.get(pos, positions['Center'])
        return (hx, hy, hw, hh)

    @staticmethod
    def _pt_in_rect(px, py, bbox):
        x, y, w, h = bbox
        return (x <= px <= x + w) and (y <= py <= y + h)

    def _draw_house(self, ax, layout, L, W):
        hx, hy, hw, hh = self._get_house_bbox(layout, L, W)

        # Shadow
        ax.add_patch(Rectangle(
            (hx + 3, hy - 3), hw, hh,
            facecolor='#9E9E9E', edgecolor='none',
            alpha=0.25, zorder=8,
        ))
        # Walls
        ax.add_patch(Rectangle(
            (hx, hy), hw, hh,
            facecolor=self.colors['building'],
            edgecolor='#3E2723', linewidth=2.5, zorder=9,
        ))
        # Gable roof
        roof_h = hh * 0.35
        ax.add_patch(Polygon(
            [[hx - hw*0.05, hy + hh],
             [hx + hw/2,     hy + hh + roof_h],
             [hx + hw*1.05,  hy + hh]],
            facecolor=self.colors['roof'],
            edgecolor='#3E2723', linewidth=2, zorder=10,
        ))
        # Ridge line
        ax.plot([hx + hw*0.2, hx + hw*0.8], [hy + hh + roof_h*0.95, hy + hh + roof_h*0.95],
                color='#3E2723', linewidth=1, zorder=11)

        # Door
        dw, dh = hw * 0.13, hh * 0.38
        ax.add_patch(Rectangle(
            (hx + hw/2 - dw/2, hy), dw, dh,
            facecolor='#3E2723', edgecolor='black',
            linewidth=1.5, zorder=10,
        ))
        ax.add_patch(Circle(
            (hx + hw/2 + dw*0.3, hy + dh*0.5),
            min(hw, hh)*0.013,
            facecolor='#FFD700', edgecolor='black', zorder=11,
        ))

        # Windows ×2
        ww, wh = hw * 0.18, hh * 0.20
        for wx in [hx + hw*0.12, hx + hw*0.70]:
            wy = hy + hh * 0.55
            ax.add_patch(FancyBboxPatch(
                (wx, wy), ww, wh,
                boxstyle='round,pad=1',
                facecolor='#B3E5FC', edgecolor='#3E2723', linewidth=1.5, zorder=10,
            ))
            # Cross bars
            ax.plot([wx, wx + ww], [wy + wh/2, wy + wh/2],
                    color='#3E2723', linewidth=0.8, zorder=11)
            ax.plot([wx + ww/2, wx + ww/2], [wy, wy + wh],
                    color='#3E2723', linewidth=0.8, zorder=11)

        # Label
        ax.text(hx + hw/2, hy + hh + roof_h + 8,
                'RESIDENCE',
                ha='center', fontsize=9, fontweight='bold',
                color='#BF360C', zorder=12,
                path_effects=[pe.withStroke(linewidth=2, foreground='white')])

    # ── Paths ──────────────────────────────────────────────────────────────────
    def _draw_paths(self, ax, layout, L, W):
        """Simple gravel path from house to property edge."""
        hx, hy, hw, hh = self._get_house_bbox(layout, L, W)
        path_w = min(L, W) * 0.025

        # Front door path going south
        door_x = hx + hw / 2
        ax.add_patch(Rectangle(
            (door_x - path_w/2, 0), path_w, hy,
            facecolor=self.colors['path'],
            edgecolor='#BCAAA4', linewidth=0.5,
            alpha=0.85, zorder=4,
        ))

    # ── Water features ─────────────────────────────────────────────────────────
    def _draw_water_features(self, ax, layout, L, W):
        features = layout.get('features', {})

        if 'well' in features:
            f = features['well']
            r = f.get('radius', min(L,W)*0.025)
            ax.add_patch(Circle(
                (f['x'], f['y']), r,
                facecolor=self.colors['water'], edgecolor=self.colors['water_dark'],
                linewidth=2.5, zorder=6,
            ))
            ax.add_patch(Circle(
                (f['x'], f['y']), r * 0.75,
                facecolor='#81D4FA', edgecolor='none', zorder=6,
            ))
            ax.text(f['x'], f['y'], 'W', ha='center', va='center',
                    fontsize=9, fontweight='bold', color='white', zorder=7)
            ax.text(f['x'], f['y'] - r - 8, 'BOREWELL\n(150 ft)',
                    ha='center', fontsize=7, color=self.colors['water_dark'])

        if 'pond' in features:
            f = features['pond']
            r = f['radius']
            theta = np.linspace(0, 2*np.pi, 40)
            ripple = 1 + 0.12 * np.sin(3*theta)
            xp = f['x'] + r * ripple * np.cos(theta)
            yp = f['y'] + r * ripple * np.sin(theta)
            ax.add_patch(Polygon(
                list(zip(xp, yp)),
                facecolor='#B3E5FC', edgecolor=self.colors['water_dark'],
                linewidth=2, alpha=0.85, zorder=5,
            ))
            # Inner reflection
            ax.add_patch(Polygon(
                list(zip(f['x'] + r*0.5*np.cos(theta),
                         f['y'] + r*0.5*np.sin(theta))),
                facecolor='#4FC3F7', edgecolor='none', alpha=0.5, zorder=5,
            ))
            # Lily pads
            for _ in range(4):
                px = f['x'] + np.random.uniform(-r*0.5, r*0.5)
                py = f['y'] + np.random.uniform(-r*0.5, r*0.5)
                ax.add_patch(Circle((px, py), 3, facecolor='#4CAF50',
                                     edgecolor='none', alpha=0.7, zorder=6))
            ax.text(f['x'], f['y'], 'POND\n(Aquaculture)',
                    ha='center', va='center', fontsize=7.5,
                    color=self.colors['water_dark'], zorder=7)

    # ── Utilities: SOLAR (blue panels) + GREENHOUSE ───────────────────────────
    def _draw_utilities(self, ax, layout, L, W):
        features = layout.get('features', {})

        # ── Solar Panels — proper blue photovoltaic look ──────────────────
        if 'solar' in features:
            f = features['solar']
            rows, cols = 2, 3
            gap = 2
            cell_w = (f['width']  - gap * (cols + 1)) / cols
            cell_h = (f['height'] - gap * (rows + 1)) / rows

            # Panel frame background
            ax.add_patch(Rectangle(
                (f['x'], f['y']), f['width'], f['height'],
                facecolor='#90A4AE', edgecolor='#37474F',
                linewidth=1.5, zorder=5,
            ))

            for row in range(rows):
                for col in range(cols):
                    px = f['x'] + gap + col * (cell_w + gap)
                    py = f['y'] + gap + row * (cell_h + gap)

                    # Main panel cell (dark blue)
                    ax.add_patch(Rectangle(
                        (px, py), cell_w, cell_h,
                        facecolor=self.colors['solar_panel'],
                        edgecolor=self.colors['solar_frame'],
                        linewidth=1, zorder=6,
                    ))
                    # Cell grid lines (inner blue)
                    for gi in range(1, 3):
                        ax.plot([px + gi*cell_w/3, px + gi*cell_w/3],
                                [py, py + cell_h],
                                color=self.colors['solar_cell'],
                                linewidth=0.5, zorder=7)
                    for gj in range(1, 2):
                        ax.plot([px, px + cell_w],
                                [py + gj*cell_h/2, py + gj*cell_h/2],
                                color=self.colors['solar_cell'],
                                linewidth=0.5, zorder=7)

            ax.text(f['x'] + f['width']/2, f['y'] + f['height'] + 9,
                    'SOLAR ARRAY (5 kW)',
                    ha='center', fontsize=7.5,
                    fontweight='bold', color='#0D47A1', zorder=8)

        # ── Greenhouse ────────────────────────────────────────────────────
        if 'greenhouse' in features:
            f = features['greenhouse']
            ax.add_patch(Rectangle(
                (f['x'], f['y']), f['width'], f['height'],
                facecolor=self.colors['greenhouse'],
                edgecolor='#00695C', linewidth=2,
                linestyle='--', alpha=0.75, zorder=5,
            ))
            # Arched roof suggestion
            ax.add_patch(Arc(
                (f['x'] + f['width']/2, f['y'] + f['height']),
                f['width'], f['height']*0.35,
                angle=0, theta1=0, theta2=180,
                color='#00695C', linewidth=2, zorder=6,
            ))
            # Benches
            for by in [f['y'] + 8, f['y'] + f['height'] - 18]:
                ax.add_patch(Rectangle(
                    (f['x'] + 5, by), f['width'] - 10, 10,
                    facecolor='#8D6E63', edgecolor='black',
                    linewidth=0.8, zorder=6,
                ))
            ax.text(f['x'] + f['width']/2, f['y'] - 10,
                    'GREENHOUSE\n(Seasonal crops)',
                    ha='center', fontsize=7.5, color='#004D40', zorder=7)

    # ── Livestock housing ──────────────────────────────────────────────────────
    def _draw_livestock_housing(self, ax, layout, L, W):
        features = layout.get('features', {})
        if 'livestock' not in features:
            return
        f = features['livestock']
        # Main shed
        ax.add_patch(Rectangle(
            (f['x'], f['y']), f['width'], f['height'],
            facecolor=self.colors['livestock'],
            edgecolor='#4E342E', linewidth=2, zorder=5,
        ))
        # Roof ridge line
        ax.plot([f['x'], f['x'] + f['width']],
                [f['y'] + f['height']] * 2,
                color='#4E342E', linewidth=1.5, zorder=6)
        # Paddock fence (dashed)
        pad = f['width'] * 1.6
        ax.add_patch(Rectangle(
            (f['x'] - pad*0.1, f['y'] - pad*0.5),
            f['width'] + pad*0.2, pad*0.5,
            facecolor='none',
            edgecolor=self.colors['fence'],
            linewidth=1.5, linestyle=':', zorder=5,
        ))
        ax.text(f['x'] + f['width']/2, f['y'] + f['height'] + 8,
                'LIVESTOCK SHED',
                ha='center', fontsize=7.5,
                fontweight='bold', color='#4E342E', zorder=7)

    # ── Vegetation ─────────────────────────────────────────────────────────────
    def _draw_vegetation(self, ax, layout, L, W):
        zones = layout.get('zone_positions', {})
        if 'z2' not in zones:
            return
        z = zones['z2']

        placements = [
            (0.18, 0.32, 'Mango',    '#2E7D32', 11),
            (0.50, 0.60, 'Coconut',  '#388E3C',  9),
            (0.82, 0.42, 'Jackfruit','#1B5E20', 13),
            (0.32, 0.75, 'Banana',   '#558B2F', 10),
            (0.68, 0.22, 'Guava',    '#33691E',  8),
        ]

        for rx, ry, label, color, crown_r in placements:
            tx = z['x'] + rx * z['width']
            ty = z['y'] + ry * z['height']

            # Trunk
            ax.add_patch(Rectangle(
                (tx - 2, ty - crown_r), 4, crown_r,
                facecolor='#795548', edgecolor='none', zorder=6,
            ))
            # Crown
            ax.add_patch(Circle(
                (tx, ty), crown_r,
                facecolor=color, edgecolor='#1B5E20',
                linewidth=1, alpha=0.85, zorder=7,
            ))
            # Shadow
            ax.add_patch(Polygon(
                [[tx - crown_r*0.7, ty - crown_r],
                 [tx + crown_r*0.7, ty - crown_r],
                 [tx + crown_r*0.5, ty - crown_r - 6],
                 [tx - crown_r*0.5, ty - crown_r - 6]],
                facecolor='#33691E', edgecolor='none',
                alpha=0.25, zorder=6,
            ))
            ax.text(tx, ty + crown_r + 5, label,
                    ha='center', fontsize=6.5, color='#1B5E20', zorder=8)

        # Scattered shrubs in Z4
        if 'z4' in zones:
            z4 = zones['z4']
            for _ in range(6):
                sx = z4['x'] + np.random.uniform(0.1, 0.9) * z4['width']
                sy = z4['y'] + np.random.uniform(0.2, 0.8) * z4['height']
                ax.add_patch(Circle((sx, sy), 5,
                                    facecolor='#7B1FA2', edgecolor='none',
                                    alpha=0.25, zorder=5))

    # ── Cartographic elements ──────────────────────────────────────────────────
    def _add_north_arrow(self, ax, L, W):
        nx, ny = L * 0.93, W * 0.07
        r = min(L, W) * 0.035
        # Circle
        ax.add_patch(Circle((nx, ny), r, facecolor='white',
                             edgecolor='#1A237E', linewidth=2, zorder=15))
        # Arrow
        ax.annotate('', xy=(nx, ny + r*0.75), xytext=(nx, ny - r*0.4),
                    arrowprops=dict(arrowstyle='->', color='red', lw=2.5),
                    zorder=16)
        ax.text(nx, ny + r + 5, 'N', ha='center', fontsize=12,
                fontweight='bold', color='red', zorder=16)

    def _add_scale_bar(self, ax, L, W):
        sx, sy = L * 0.04, W * 0.04
        scale = min(50, int(L * 0.18 / 10) * 10)

        # Alternating black/white bar
        half = scale / 2
        ax.add_patch(Rectangle((sx, sy - 3), half, 7,
                                facecolor='black', edgecolor='none', zorder=15))
        ax.add_patch(Rectangle((sx + half, sy - 3), half, 7,
                                facecolor='white', edgecolor='black',
                                linewidth=0.8, zorder=15))
        ax.plot([sx, sx + scale], [sy + 4, sy + 4], 'k-', linewidth=0.5, zorder=15)

        ax.text(sx + scale / 2, sy - 10, f'{scale} ft',
                ha='center', fontsize=8.5, fontweight='bold', zorder=15)
        ax.text(sx + scale / 2, sy + 12, 'SCALE',
                ha='center', fontsize=7.5, zorder=15)

    def _add_legend(self, ax, L, W):
        lx = L + min(L, W) * 0.06
        ly = W * 0.95
        box_h = 18
        items = [
            (self.colors['building'],    'Residence'),
            (self.colors['livestock'],   'Livestock Shed'),
            (self.colors['water'],       'Water / Pond'),
            (self.colors['solar_panel'], 'Solar Array'),
            (self.colors['greenhouse'],  'Greenhouse'),
            ('#2E7D32',                  'Trees'),
            (self.zone_colors['z0'],     'Zone 0 – Residential'),
            (self.zone_colors['z1'],     'Zone 1 – Kitchen Garden'),
            (self.zone_colors['z2'],     'Zone 2 – Food Forest'),
            (self.zone_colors['z3'],     'Zone 3 – Pasture/Crops'),
            (self.zone_colors['z4'],     'Zone 4 – Buffer'),
        ]
        total_h = len(items) * box_h + 30
        # Background
        ax.add_patch(FancyBboxPatch(
            (lx - 8, ly - total_h), 130, total_h + 6,
            boxstyle='round,pad=4',
            facecolor='white', edgecolor='#546E7A',
            linewidth=1.5, zorder=14,
        ))
        ax.text(lx + 55, ly + 2, 'LEGEND', ha='center',
                fontsize=9.5, fontweight='bold', color='#1A237E', zorder=15)

        for i, (color, label) in enumerate(items):
            yp = ly - (i + 1) * box_h + 4
            ax.add_patch(Rectangle(
                (lx, yp), 14, 11,
                facecolor=color,
                edgecolor='#546E7A', linewidth=0.8, zorder=15,
            ))
            ax.text(lx + 20, yp + 5.5, label,
                    fontsize=7.5, va='center', zorder=15)

    def _add_dimensions(self, ax, L, W):
        offset = min(L, W) * 0.05
        # Width
        ax.annotate('', xy=(0, -offset), xytext=(L, -offset),
                    arrowprops=dict(arrowstyle='<->', color='#1A237E', lw=1.5),
                    zorder=13)
        ax.text(L/2, -offset - 12, f'{int(L)} ft',
                ha='center', fontsize=10, fontweight='bold', color='#1A237E')
        # Height
        ax.annotate('', xy=(-offset, 0), xytext=(-offset, W),
                    arrowprops=dict(arrowstyle='<->', color='#1A237E', lw=1.5),
                    zorder=13)
        ax.text(-offset - 14, W/2, f'{int(W)} ft',
                ha='center', fontsize=10, fontweight='bold',
                color='#1A237E', rotation=90)

    def _add_title_block(self, ax, layout, L, W):
        acres  = layout.get('acres', layout.get('total_sqft', 0) / 43560)
        total  = layout.get('total_sqft', 0)
        cat    = layout.get('category', '').upper()
        title  = f"{acres:.2f} ACRE HOMESTEAD\n{int(total):,} SQ.FT.  ·  {cat} SCALE"

        ax.text(L/2, W + min(L,W)*0.07, title,
                ha='center', va='bottom',
                fontsize=13, fontweight='bold', color='#1B5E20',
                bbox=dict(boxstyle='round,pad=0.6',
                          facecolor='#E8F5E9',
                          edgecolor='#2E7D32', linewidth=2),
                zorder=16)
