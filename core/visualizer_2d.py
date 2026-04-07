"""
Professional 2D Site-Plan Visualizer — Premium v4
Homestead Architect Pro 2026

Fixes in v4:
  ✅ House size = realistic (max 15-20% of plot, not zone-sized)
  ✅ Kitchen garden beds SCALE with plot size (visible on all sizes)
  ✅ Pond ALWAYS draws (no registry collision blocking it)
  ✅ Paths REMOVED (were not rendering cleanly)
  ✅ All elements scale proportionally from 0.25 to 62 acres
  ✅ Premium aerial-view look throughout
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import (
    FancyBboxPatch, Circle, Rectangle, Polygon, Arc, PathPatch
)
from matplotlib.path import Path
import matplotlib.patheffects as pe
import numpy as np
from io import BytesIO
from typing import List, Tuple, Optional


# ─────────────────────────────────────────────────────────────────────────────
#  Scale helper: convert "design units" to current plot size
# ─────────────────────────────────────────────────────────────────────────────
def _s(val: float, ref: float, current: float) -> float:
    """Scale val from reference plot size (ref) to current plot size."""
    return val * (current / ref)


# ─────────────────────────────────────────────────────────────────────────────
#  Bounding-box registry (collision detection)
# ─────────────────────────────────────────────────────────────────────────────
class _Reg2D:
    GAP = 2.0

    def __init__(self):
        self.rects: List[Tuple]   = []
        self.circles: List[Tuple] = []

    def add_rect(self, x, y, w, h):
        self.rects.append((x, y, w, h))

    def add_circle(self, cx, cy, r):
        self.circles.append((cx, cy, r))

    def rect_ok(self, x, y, w, h) -> bool:
        g = self.GAP
        for (rx, ry, rw, rh) in self.rects:
            if (x - g < rx + rw and x + w + g > rx and
                    y - g < ry + rh and y + h + g > ry):
                return False
        return True

    def circle_ok(self, cx, cy, r) -> bool:
        g = self.GAP
        for (rx, ry, rw, rh) in self.rects:
            nx = max(rx, min(cx, rx + rw))
            ny = max(ry, min(cy, ry + rh))
            if (cx - nx) ** 2 + (cy - ny) ** 2 < (r + g) ** 2:
                return False
        for (ocx, ocy, or_) in self.circles:
            if (cx - ocx) ** 2 + (cy - ocy) ** 2 < (r + or_ + g) ** 2:
                return False
        return True

    def force_add_circle(self, cx, cy, r):
        """Add circle without collision check (for pond/water)."""
        self.circles.append((cx, cy, r))

    def force_add_rect(self, x, y, w, h):
        """Add rect without collision check."""
        self.rects.append((x, y, w, h))


# ─────────────────────────────────────────────────────────────────────────────
#  Tree canopy (top-down aerial blob)
# ─────────────────────────────────────────────────────────────────────────────
TREE_COLORS = {
    'Mango':    ('#2E7D32', '#388E3C'), 'Jackfruit': ('#1B5E20', '#2E7D32'),
    'Coconut':  ('#33691E', '#558B2F'), 'Banana':    ('#558B2F', '#7CB342'),
    'Guava':    ('#33691E', '#43A047'), 'Papaya':    ('#558B2F', '#8BC34A'),
    'Avocado':  ('#2E7D32', '#1B5E20'), 'Moringa':   ('#66BB6A', '#4CAF50'),
    'Citrus':   ('#43A047', '#66BB6A'), 'Neem':      ('#388E3C', '#2E7D32'),
    'Teak':     ('#1B5E20', '#2E7D32'), 'Bamboo':    ('#4CAF50', '#8BC34A'),
    'default':  ('#2E7D32', '#388E3C'),
}


def _draw_tree(ax, tx, ty, r, species='default', zorder=7):
    """Aerial top-down tree: shadow + canopy blob + highlight."""
    c1, c2 = TREE_COLORS.get(species, TREE_COLORS['default'])
    ax.add_patch(Circle((tx + r * 0.25, ty - r * 0.25), r * 1.0,
                         facecolor='#1B5E20', edgecolor='none', alpha=0.16, zorder=zorder - 1))
    np.random.seed(hash(species + str(round(tx))) % 9999)
    n = 12
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    radii  = r * (0.82 + 0.18 * np.random.rand(n))
    bx = tx + radii * np.cos(angles)
    by = ty + radii * np.sin(angles)
    ax.add_patch(Polygon(list(zip(bx, by)),
                          facecolor=c1, edgecolor=c2, linewidth=0.8,
                          alpha=0.92, zorder=zorder))
    ax.add_patch(Circle((tx - r * 0.22, ty + r * 0.22), r * 0.30,
                         facecolor='white', edgecolor='none', alpha=0.13, zorder=zorder + 1))


# ─────────────────────────────────────────────────────────────────────────────
#  Raised garden bed (wooden frame look)
# ─────────────────────────────────────────────────────────────────────────────
def _raised_bed(ax, x, y, w, h, soil_color='#3E2723', frame_color='#8D6E63',
                plant_color='#2E7D32', zorder=6):
    frame_t = min(w, h) * 0.12
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                 boxstyle='round,pad=0',
                                 facecolor=frame_color, edgecolor='#5D4037',
                                 linewidth=max(1.5, w * 0.04), zorder=zorder))
    ax.add_patch(Rectangle((x + frame_t, y + frame_t),
                             w - 2 * frame_t, h - 2 * frame_t,
                             facecolor=soil_color, edgecolor='none', zorder=zorder + 1))
    inner_w = w - 2 * frame_t - 4
    inner_h = h - 2 * frame_t - 4
    if inner_w < 4 or inner_h < 4:
        return
    n_cols = max(1, int(inner_w / max(8, w * 0.15)))
    n_rows = max(1, int(inner_h / max(7, h * 0.15)))
    p_colors = ['#4CAF50', '#66BB6A', '#81C784', '#A5D6A7']
    pr = min(inner_w / n_cols, inner_h / n_rows) * 0.28
    for ri in range(n_rows):
        for ci in range(n_cols):
            px = x + frame_t + 2 + (ci + 0.5) * inner_w / n_cols
            py = y + frame_t + 2 + (ri + 0.5) * inner_h / n_rows
            ax.add_patch(Circle((px, py), pr,
                                  facecolor=p_colors[(ri + ci) % len(p_colors)],
                                  edgecolor='#1B5E20', linewidth=0.3, zorder=zorder + 2))


# ─────────────────────────────────────────────────────────────────────────────
#  Main Visualizer class
# ─────────────────────────────────────────────────────────────────────────────
class Visualizer2D:

    ZONE_COLORS = {
        'z0': '#F0EAD6', 'z1': '#C5E1A5', 'z2': '#388E3C',
        'z3': '#FFF9C4', 'z4': '#A5D6A7',
    }
    ZONE_NAMES = {
        'z0': 'ZONE 0\nRESIDENTIAL', 'z1': 'ZONE 1\nKITCHEN GARDEN',
        'z2': 'ZONE 2\nFOOD FOREST',  'z3': 'ZONE 3\nPASTURE / CROPS',
        'z4': 'ZONE 4\nBUFFER',
    }

    def __init__(self):
        self._reg: Optional[_Reg2D] = None
        self._L = 300.0
        self._W = 300.0

    # ── Public API ───────────────────────────────────────────────────────────
    def create(self, layout: dict, answers: dict) -> BytesIO:
        L = float(layout['dimensions']['L'])
        W = float(layout['dimensions']['W'])
        self._reg = _Reg2D()
        self._L = L
        self._W = W

        # DPI and figure size scale with plot
        base = max(L, W)
        dpi = 150
        fig_w = 18
        fig_h = max(10, fig_w * (W / L) * 0.72)

        fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)
        fig.patch.set_facecolor('#F9F6F0')
        ax.set_facecolor('#5A8F3C')

        # Draw order: back → front
        self._grass_texture(ax, L, W)
        self._zones(ax, layout, L, W)
        self._contour_lines(ax, layout, L, W)
        self._perimeter_border(ax, L, W)
        self._water_features(ax, layout, L, W)        # water before house
        self._utilities(ax, layout, L, W)
        self._livestock_housing(ax, layout, L, W)
        self._kitchen_garden_beds(ax, layout, L, W)
        self._vegetation(ax, layout, L, W)
        self._house_plan(ax, layout, L, W)             # house on top
        self._zone_labels(ax, layout, L, W)
        self._north_arrow(ax, L, W)
        self._scale_bar(ax, L, W)
        self._legend(ax, L, W)
        self._dimensions(ax, L, W)
        self._title(ax, layout, L, W)

        margin = max(L, W) * 0.18
        ax.set_xlim(-margin, L + margin * 1.9)
        ax.set_ylim(-margin * 1.1, W + margin)
        ax.set_aspect('equal')
        ax.axis('off')
        plt.tight_layout(pad=0.4)

        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=200, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        buf.seek(0)
        plt.close(fig)
        return buf

    # ── Grass texture ─────────────────────────────────────────────────────────
    def _grass_texture(self, ax, L, W):
        ax.add_patch(Rectangle((0, 0), L, W, facecolor='#5A8F3C',
                                edgecolor='none', zorder=0))
        np.random.seed(1)
        density = max(200, min(600, int(L * W / 200)))
        for _ in range(density):
            gx = np.random.uniform(2, L - 2)
            gy = np.random.uniform(2, W - 2)
            gl = np.random.uniform(max(2, L * 0.008), max(6, L * 0.025))
            gc = ['#4CAF50', '#66BB6A', '#388E3C', '#2E7D32'][_ % 4]
            ax.plot([gx, gx + np.random.uniform(-1, 1)], [gy, gy + gl],
                    color=gc, lw=0.3, alpha=0.10, zorder=0)

    # ── Zones ─────────────────────────────────────────────────────────────────
    def _zones(self, ax, layout, L, W):
        for zid, pos in layout.get('zone_positions', {}).items():
            ax.add_patch(Rectangle((pos['x'], pos['y']), pos['width'], pos['height'],
                                    facecolor=self.ZONE_COLORS.get(zid, '#CCC'),
                                    edgecolor='#546E7A', linewidth=1.5,
                                    alpha=0.40, zorder=2))

    # ── Contour lines ─────────────────────────────────────────────────────────
    def _contour_lines(self, ax, layout, L, W):
        slope = layout.get('slope', 'Flat')
        if slope == 'Flat':
            return
        for idx in range(1, 5):
            frac = idx / 5
            if slope in ('South', 'North'):
                y = W * frac if slope == 'South' else W * (1 - frac)
                ax.plot([0, L], [y, y], color='#A5D6A7', linestyle='--',
                        lw=0.6, alpha=0.5, zorder=1)
            else:
                x = L * frac if slope == 'East' else L * (1 - frac)
                ax.plot([x, x], [0, W], color='#A5D6A7', linestyle='--',
                        lw=0.6, alpha=0.5, zorder=1)

    # ── Perimeter fence & gate ────────────────────────────────────────────────
    def _perimeter_border(self, ax, L, W):
        # Scale fence proportionally
        unit = min(L, W)
        post_gap = max(unit * 0.04, 10.0)
        post_w   = max(post_gap * 0.10, 2.0)
        post_h   = post_w * 2.0
        z = 3

        def _fence_edge(x0, y0, x1, y1):
            dx = x1 - x0; dy = y1 - y0
            length = np.hypot(dx, dy)
            if length < 2:
                return
            n_posts = max(2, int(length / post_gap))
            for i in range(n_posts + 1):
                t = i / n_posts
                px = x0 + t * dx - post_w / 2
                py = y0 + t * dy - post_h / 2
                ax.add_patch(FancyBboxPatch((px, py), post_w, post_h,
                                             boxstyle='round,pad=0.3',
                                             facecolor='#5D4037', edgecolor='#3E2723',
                                             linewidth=0.6, zorder=z + 1))
            ux, uy = dx / length, dy / length
            nx_v, ny_v = -uy, ux
            for rail_t in [0.30, 0.70]:
                off = post_h * (rail_t - 0.5) * 0.8
                ax.plot([x0 + nx_v * off, x1 + nx_v * off],
                        [y0 + ny_v * off, y1 + ny_v * off],
                        color='#A1887F', lw=max(2.0, post_w * 0.8),
                        solid_capstyle='round', zorder=z)

        gate_cx = L / 2
        gate_hw = max(unit * 0.04, 15.0)

        _fence_edge(0, 0, gate_cx - gate_hw, 0)
        _fence_edge(gate_cx + gate_hw, 0, L, 0)
        _fence_edge(0, W, L, W)
        _fence_edge(0, 0, 0, W)
        _fence_edge(L, 0, L, W)

        gp_w = post_w * 1.6
        gp_h = post_h * 1.4
        for gx in [gate_cx - gate_hw - gp_w, gate_cx + gate_hw]:
            ax.add_patch(FancyBboxPatch((gx, -gp_h / 2), gp_w, gp_h,
                                         boxstyle='round,pad=0.3',
                                         facecolor='#4E342E', edgecolor='#1A237E',
                                         linewidth=1.8, zorder=z + 3))
        ax.text(gate_cx, -gp_h - max(6, unit * 0.018), 'MAIN GATE',
                ha='center', va='top', fontsize=max(7, unit * 0.022),
                fontweight='bold', color='#1A237E', zorder=z + 4,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor='#1A237E', alpha=0.85, linewidth=1.0))

    # ── House (FIXED SIZE: proportional to plot, NOT to zone) ─────────────────
    def _house_bbox(self, layout, L, W):
        """
        House size: realistic 3-5 bedroom home.
        Max 15% of plot width, min ~40ft.
        Position follows house_position within Z0 zone.
        """
        pos = layout.get('house_position', 'Center')
        zone_positions = layout.get('zone_positions', {})
        z0 = zone_positions.get('z0', {'x': 0, 'y': 0, 'width': L, 'height': W})

        # FIXED: house is 12-18% of min(L,W) — realistic size
        unit = min(L, W)
        hw = max(40.0, min(unit * 0.16, 120.0))   # width 40–120 ft
        hh = max(30.0, min(unit * 0.12, 90.0))    # depth 30–90 ft

        # Center in Z0 zone
        z0_cx = z0['x'] + z0['width'] / 2
        z0_cy = z0['y'] + z0['height'] / 2

        hx = z0_cx - hw / 2
        hy = z0_cy - hh / 2

        # Clamp inside Z0
        hx = max(z0['x'] + 4, min(hx, z0['x'] + z0['width'] - hw - 4))
        hy = max(z0['y'] + 4, min(hy, z0['y'] + z0['height'] - hh - 4))

        return hx, hy, hw, hh

    def _house_plan(self, ax, layout, L, W):
        hx, hy, hw, hh = self._house_bbox(layout, L, W)
        self._reg.force_add_rect(hx, hy, hw, hh)
        z = 10
        wall = min(hw, hh) * 0.07
        unit = min(L, W)
        fsize_room = max(5, min(8, unit * 0.018))
        fsize_lbl  = max(8, min(12, unit * 0.030))

        # Drop shadow
        ax.add_patch(Rectangle((hx + 3, hy - 3), hw, hh,
                                 facecolor='#795548', edgecolor='none',
                                 alpha=0.20, zorder=z - 1))

        # Roof base (light grey shingles)
        ax.add_patch(Rectangle((hx, hy), hw, hh,
                                 facecolor='#ECEFF1', edgecolor='#546E7A',
                                 linewidth=max(2.0, wall * 0.4), zorder=z))

        # Shingle lines
        shingle_gap = max(5, hh * 0.06)
        for ry in np.arange(hy + wall, hy + hh, shingle_gap):
            ax.plot([hx + wall, hx + hw - wall], [ry, ry],
                    color='#B0BEC5', lw=0.6, alpha=0.55, zorder=z)

        # Ridge + hip lines
        ridge_x = hx + hw / 2
        ax.plot([ridge_x, ridge_x], [hy + wall, hy + hh - wall],
                color='#607D8B', lw=max(1.5, wall * 0.3), linestyle='-.', zorder=z + 1)
        for corner in [(hx, hy), (hx + hw, hy), (hx, hy + hh), (hx + hw, hy + hh)]:
            ax.plot([corner[0], ridge_x], [corner[1], hy + hh / 2],
                    color='#546E7A', lw=max(0.8, wall * 0.2), alpha=0.60, zorder=z + 1)

        # Thick walls (plan view)
        for wx0, wy0, wx1, wy1 in [
            (hx, hy, hx + hw, hy + wall),
            (hx, hy + hh - wall, hx + hw, hy + hh),
            (hx, hy, hx + wall, hy + hh),
            (hx + hw - wall, hy, hx + hw, hy + hh),
        ]:
            ax.add_patch(Rectangle((wx0, wy0), wx1 - wx0, wy1 - wy0,
                                    facecolor='#8D6E63', edgecolor='none', zorder=z + 1))

        # Interior dividers
        div_y = hy + hh * 0.52
        gap = (hx + hw * 0.43, hx + hw * 0.57)
        ax.plot([hx + wall, gap[0]], [div_y, div_y], color='#5D4037',
                lw=max(1.5, wall * 0.3), zorder=z + 2)
        ax.plot([gap[1], hx + hw - wall], [div_y, div_y], color='#5D4037',
                lw=max(1.5, wall * 0.3), zorder=z + 2)
        for vf in [0.36, 0.72]:
            ax.plot([hx + hw * vf, hx + hw * vf], [div_y, hy + hh - wall],
                    color='#5D4037', lw=max(1.2, wall * 0.25), zorder=z + 2)

        # Room labels
        rl = dict(fontsize=fsize_room, color='#5D4037', ha='center', va='center',
                  zorder=z + 3, fontstyle='italic')
        ax.text(hx + hw * .50, hy + hh * .27, 'LIVING / KITCHEN', **rl)
        ax.text(hx + hw * .18, hy + hh * .74, 'BED 1', **rl)
        ax.text(hx + hw * .54, hy + hh * .74, 'MASTER', **rl)
        ax.text(hx + hw * .86, hy + hh * .74, 'BATH', **rl)

        # Windows
        ww = hw * 0.13
        wz_h = wall * 0.85
        ws = dict(facecolor='#B3E5FC', edgecolor='#1565C0',
                  lw=max(1.0, wall * 0.2), zorder=z + 2)
        for wx in [hx + hw * 0.18, hx + hw * 0.62]:
            ax.add_patch(Rectangle((wx, hy), ww, wz_h, **ws))
            ax.add_patch(Rectangle((wx, hy + hh - wz_h), ww, wz_h, **ws))
        ax.add_patch(Rectangle((hx, hy + hh * .54), wz_h, ww, **ws))
        ax.add_patch(Rectangle((hx + hw - wz_h, hy + hh * .54), wz_h, ww, **ws))

        # Front door
        fdw = hw * 0.13
        fdx = hx + hw / 2 - fdw / 2
        ax.add_patch(Rectangle((fdx, hy), fdw, wall * 1.3,
                                 facecolor='#3E2723', edgecolor='black',
                                 lw=max(1.0, wall * 0.2), zorder=z + 2))
        ax.add_patch(Arc((fdx, hy + wall * .6), (fdw * 2), (fdw * 2),
                          angle=0, theta1=0, theta2=90,
                          color='#4E342E', lw=max(1.0, wall * 0.2), zorder=z + 3))

        # Steps
        for si, ss in enumerate([hh * 0.06, hh * 0.10, hh * 0.14]):
            ax.add_patch(FancyBboxPatch(
                (fdx - ss * .4, hy - ss * .55 - si * hh * 0.015),
                fdw + ss * .8, ss * .5,
                boxstyle='round,pad=1.0',
                facecolor='#EFEBE9', edgecolor='#8D6E63',
                lw=max(0.6, wall * 0.12), zorder=z - 1))

        # Porch/deck
        pw = hw * .52
        pd = hh * .14
        px2 = hx + (hw - pw) / 2
        py2 = hy - pd
        ax.add_patch(FancyBboxPatch((px2, py2), pw, pd,
                                     boxstyle='round,pad=2',
                                     facecolor='#D7CCC8', edgecolor='#8D6E63',
                                     lw=max(1.2, wall * 0.25), alpha=0.88, zorder=z - 1))
        for dy_deck in np.arange(py2 + 3, py2 + pd, max(4, pd * 0.18)):
            ax.plot([px2 + 3, px2 + pw - 3], [dy_deck, dy_deck],
                    color='#A1887F', lw=0.5, alpha=0.55, zorder=z)

        # Chimney
        cw2 = hw * .07
        cd2 = hh * .07
        cx2 = hx + hw * .72
        cy2 = hy + hh * .40
        ax.add_patch(Rectangle((cx2, cy2), cw2, cd2,
                                 facecolor='#6D4C41', edgecolor='#3E2723',
                                 lw=max(1.2, wall * 0.25), zorder=z + 2))
        for sox, soy, sr, sa in [(2, 9, 3.5, .28), (5, 17, 5, .18), (8, 27, 7, .10)]:
            ax.add_patch(Circle((cx2 + cw2 / 2 + sox * (unit / 300),
                                  cy2 + cd2 + soy * (unit / 300)),
                                 sr * (unit / 300),
                                 facecolor='#90A4AE', edgecolor='none',
                                 alpha=sa, zorder=z + 2))

        # Label
        ax.text(hx + hw / 2, hy + hh + max(12, unit * 0.035), 'RESIDENCE',
                ha='center', fontsize=fsize_lbl, fontweight='bold', color='#BF360C',
                zorder=z + 4,
                path_effects=[pe.withStroke(linewidth=2.5, foreground='white')])

    # ── Kitchen Garden (SCALED beds) ──────────────────────────────────────────
    def _kitchen_garden_beds(self, ax, layout, L, W):
        zones = layout.get('zone_positions', {})
        if 'z1' not in zones:
            return
        pos = zones['z1']
        x0, y0 = pos['x'], pos['y']
        w, h = pos['width'], pos['height']

        unit = min(L, W)
        pad  = max(6.0, w * 0.05)

        # Bed dimensions scale with zone size
        bed_w = max(14.0, min(w * 0.12, 35.0))
        bed_h = max(25.0, min(h * 0.45, 80.0))
        gap   = max(8.0, min(w * 0.04, 20.0))

        avail_w = w - 2 * pad
        n_beds = max(1, int((avail_w + gap) / (bed_w + gap)))
        n_beds = min(n_beds, 6)

        # Total beds width
        total_bw = n_beds * bed_w + (n_beds - 1) * gap
        start_x  = x0 + pad + max(0, (avail_w - total_bw) / 2)

        # Two rows of beds if zone is tall enough
        rows = 1
        if h > bed_h * 2.5 + gap + 2 * pad:
            rows = 2
        row_gap = max(8.0, h * 0.06)

        for row in range(rows):
            by = y0 + pad + row * (bed_h + row_gap)
            if by + bed_h > y0 + h - pad:
                break
            for i in range(n_beds):
                bx = start_x + i * (bed_w + gap)
                if bx + bed_w > x0 + w - pad:
                    break
                # Don't check registry — garden beds are planned to be here
                self._reg.force_add_rect(bx, by, bed_w, bed_h)
                _raised_bed(ax, bx, by, bed_w, bed_h, zorder=6)

        # Central garden path between rows
        if rows == 2:
            path_y = y0 + pad + bed_h + row_gap * 0.1
            path_h = row_gap * 0.8
            ax.add_patch(Rectangle((x0 + pad, path_y),
                                    total_bw, path_h,
                                    facecolor='#D2B48C', edgecolor='#BCAAA4',
                                    lw=1.0, alpha=0.70, zorder=5))

        # Compost corner
        comp_sz = max(10.0, min(w * 0.08, 22.0))
        cx_c = x0 + w - pad - comp_sz
        cy_c = y0 + h - pad - comp_sz
        ax.add_patch(FancyBboxPatch((cx_c, cy_c), comp_sz, comp_sz,
                                     boxstyle='round,pad=1.5',
                                     facecolor='#5D4037', edgecolor='#3E2723',
                                     lw=1.5, zorder=6))
        ax.text(cx_c + comp_sz / 2, cy_c + comp_sz / 2, 'COMPOST',
                ha='center', va='center',
                fontsize=max(5, comp_sz * 0.22), color='white',
                fontweight='bold', zorder=7)

    # ── Water features (pond ALWAYS draws) ───────────────────────────────────
    def _water_features(self, ax, layout, L, W):
        features = layout.get('features', {})
        unit = min(L, W)
        z = 7

        # Borewell / Well
        for key in ('borewell', 'well'):
            if key in features:
                f = features[key]
                r = max(unit * 0.015, f.get('radius', unit * 0.022))
                r = min(r, unit * 0.04)
                # Force draw (no collision block)
                self._reg.force_add_circle(f['x'], f['y'], r)
                ax.add_patch(Circle((f['x'], f['y']), r,
                                     facecolor='#4FC3F7', edgecolor='#0288D1',
                                     lw=max(2.0, r * 0.15), zorder=z))
                ax.add_patch(Circle((f['x'], f['y']), r * .70,
                                     facecolor='#81D4FA', edgecolor='none', zorder=z))
                ax.text(f['x'], f['y'], 'W', ha='center', va='center',
                        fontsize=max(8, r * 0.35), fontweight='bold',
                        color='white', zorder=z + 1)
                ax.text(f['x'], f['y'] - r - max(6, r * 0.4), 'WELL',
                        ha='center', fontsize=max(6, r * 0.25),
                        color='#0288D1', zorder=z + 1)
                break

        # Pond — ALWAYS draw regardless of registry
        if 'pond' in features:
            f = features['pond']
            r = max(unit * 0.04, f['radius'])   # minimum visible size
            r = min(r, unit * 0.12)              # max size

            # Remove old circle entries that might block it
            self._reg.force_add_circle(f['x'], f['y'], r)

            theta = np.linspace(0, 2 * np.pi, 50)
            rip = 1 + 0.10 * np.sin(3 * theta) + 0.06 * np.cos(5 * theta)

            # Outer shadow
            ax.add_patch(Circle((f['x'] + r * 0.08, f['y'] - r * 0.08), r * 1.05,
                                  facecolor='#1A237E', edgecolor='none',
                                  alpha=0.12, zorder=z - 1))
            # Main water body
            ax.add_patch(Polygon(
                list(zip(f['x'] + r * rip * np.cos(theta),
                          f['y'] + r * rip * np.sin(theta))),
                facecolor='#29B6F6', edgecolor='#0288D1',
                lw=max(2.0, r * 0.06), alpha=0.90, zorder=z))
            # Inner shimmer
            ax.add_patch(Polygon(
                list(zip(f['x'] + r * .48 * np.cos(theta),
                          f['y'] + r * .48 * np.sin(theta))),
                facecolor='#81D4FA', edgecolor='none', alpha=0.55, zorder=z))
            # Ripple lines
            for rf in [0.25, 0.65]:
                ax.add_patch(Circle((f['x'], f['y']), r * rf,
                                     facecolor='none', edgecolor='#4FC3F7',
                                     lw=max(0.5, r * 0.02), alpha=0.45, zorder=z + 1))
            # Lily pads
            np.random.seed(42)
            for _ in range(max(3, int(r * 0.4))):
                ang = np.random.uniform(0, 2 * np.pi)
                d = np.random.uniform(0, r * 0.45)
                ax.add_patch(Circle(
                    (f['x'] + d * np.cos(ang), f['y'] + d * np.sin(ang)),
                    max(2.0, r * 0.06),
                    facecolor='#4CAF50', edgecolor='none', alpha=0.72, zorder=z + 1))
            # Label
            ax.text(f['x'], f['y'], 'POND',
                    ha='center', va='center',
                    fontsize=max(7, r * 0.20), color='#01579B',
                    fontweight='bold', zorder=z + 2,
                    path_effects=[pe.withStroke(linewidth=1.5, foreground='white')])

        # Rain tank
        if 'rain_tank' in features:
            f = features['rain_tank']
            if self._reg.rect_ok(f['x'], f['y'], f['width'], f['height']):
                self._reg.force_add_rect(f['x'], f['y'], f['width'], f['height'])
                ax.add_patch(FancyBboxPatch((f['x'], f['y']), f['width'], f['height'],
                                             boxstyle='round,pad=2',
                                             facecolor='#B3E5FC', edgecolor='#0288D1',
                                             lw=2.0, zorder=z))
                for by in np.linspace(f['y'] + f['height'] * .2,
                                       f['y'] + f['height'] * .85, 3):
                    ax.plot([f['x'] + 3, f['x'] + f['width'] - 3], [by, by],
                            color='#0288D1', lw=0.8, zorder=z + 1)
                ax.text(f['x'] + f['width'] / 2, f['y'] + f['height'] / 2,
                        'RAIN\nTANK', ha='center', va='center',
                        fontsize=max(6, f['width'] * 0.10),
                        color='#01579B', fontweight='bold', zorder=z + 1)

    # ── Utilities (solar, greenhouse) ─────────────────────────────────────────
    def _utilities(self, ax, layout, L, W):
        features = layout.get('features', {})
        z = 6

        if 'solar' in features:
            f = features['solar']
            if self._reg.rect_ok(f['x'], f['y'], f['width'], f['height']):
                self._reg.force_add_rect(f['x'], f['y'], f['width'], f['height'])
                ax.add_patch(Rectangle((f['x'], f['y']), f['width'], f['height'],
                                        facecolor='#90A4AE', edgecolor='#37474F',
                                        lw=1.5, zorder=z))
                rows, cols, g = 2, 3, 1.5
                cw = (f['width'] - g * (cols + 1)) / cols
                ch = (f['height'] - g * (rows + 1)) / rows
                for row in range(rows):
                    for col in range(cols):
                        px = f['x'] + g + col * (cw + g)
                        py = f['y'] + g + row * (ch + g)
                        ax.add_patch(Rectangle((px, py), cw, ch,
                                                facecolor='#1565C0', edgecolor='#0D47A1',
                                                lw=0.8, zorder=z + 1))
                        for gi in range(1, 3):
                            ax.plot([px + gi * cw / 3, px + gi * cw / 3], [py, py + ch],
                                    color='#1976D2', lw=0.4, zorder=z + 2)
                        ax.plot([px, px + cw], [py + ch / 2, py + ch / 2],
                                color='#1976D2', lw=0.4, zorder=z + 2)
                ax.text(f['x'] + f['width'] / 2, f['y'] + f['height'] + 8,
                        'SOLAR ARRAY', ha='center',
                        fontsize=max(6, f['width'] * 0.07),
                        fontweight='bold', color='#0D47A1', zorder=z + 2)

        if 'greenhouse' in features:
            f = features['greenhouse']
            if self._reg.rect_ok(f['x'], f['y'], f['width'], f['height']):
                self._reg.force_add_rect(f['x'], f['y'], f['width'], f['height'])
                ax.add_patch(Rectangle((f['x'], f['y']), f['width'], f['height'],
                                        facecolor='#E0F2F1', edgecolor='#00695C',
                                        lw=2.0, linestyle='--', alpha=0.80, zorder=z))
                ax.add_patch(Arc((f['x'] + f['width'] / 2, f['y'] + f['height']),
                                  f['width'], f['height'] * .32,
                                  angle=0, theta1=0, theta2=180,
                                  color='#00695C', lw=2.0, zorder=z + 1))
                ax.text(f['x'] + f['width'] / 2, f['y'] - 10, 'GREENHOUSE',
                        ha='center', fontsize=max(7, f['width'] * 0.07),
                        color='#004D40', zorder=z + 2)

    # ── Livestock housing ─────────────────────────────────────────────────────
    def _livestock_housing(self, ax, layout, L, W):
        features = layout.get('features', {})
        unit = min(L, W)

        if 'goat_shed'    in features:
            f = features['goat_shed']
            self._goat_shed(ax, f['x'], f['y'], f['width'], f['height'], unit)
        if 'chicken_coop' in features:
            f = features['chicken_coop']
            self._chicken_coop(ax, f['x'], f['y'], f['width'], f['height'], unit)
        if 'piggery'      in features:
            f = features['piggery']
            self._piggery(ax, f['x'], f['y'], f['width'], f['height'], unit)
        if 'cow_shed'     in features:
            f = features['cow_shed']
            self._cow_shed(ax, f['x'], f['y'], f['width'], f['height'], unit)
        if 'fish_tanks'   in features:
            f = features['fish_tanks']
            self._fish_tanks(ax, f['x'], f['y'], f['width'], f['height'], unit)
        if 'bee_hives'    in features:
            f = features['bee_hives']
            self._bee_hives(ax, f['x'], f['y'], f['width'], f['height'], unit)

    def _shed_base(self, ax, x, y, w, h, fc, ec, label, unit, z=6):
        if not self._reg.rect_ok(x, y, w, h):
            # Force draw anyway — shed positions from layout_engine are valid
            pass
        self._reg.force_add_rect(x, y, w, h)
        lw = max(1.5, w * 0.04)
        # Shadow
        ax.add_patch(Rectangle((x - 2, y - 2), w + 4, h + 4,
                                 facecolor='#8D6E63', edgecolor='none', zorder=z - 1))
        # Main body
        ax.add_patch(Rectangle((x, y), w, h,
                                 facecolor=fc, edgecolor=ec, lw=lw, zorder=z))
        # Roof triangle
        roof_h = min(h * 0.25, max(12, unit * 0.03))
        ax.add_patch(Polygon([[x - 3, y + h], [x + w / 2, y + h + roof_h], [x + w + 3, y + h]],
                               facecolor='#A1887F', edgecolor=ec, lw=lw * 0.6, zorder=z + 1))
        ax.text(x + w / 2, y + h + roof_h + max(6, unit * 0.015), label,
                ha='center', fontsize=max(6, unit * 0.020),
                fontweight='bold', color=ec, zorder=z + 2,
                path_effects=[pe.withStroke(linewidth=1.5, foreground='white')])
        return True

    def _goat_shed(self, ax, x, y, w, h, unit):
        self._shed_base(ax, x, y, w, h, '#FFCCBC', '#5D4037', 'GOAT SHED', unit)
        for vx in [x + w * .2, x + w * .5, x + w * .8]:
            ww = max(8, w * 0.10)
            wh = max(6, h * 0.12)
            ax.add_patch(Rectangle((vx - ww / 2, y + h - wh - 2), ww, wh,
                                    facecolor='#B3E5FC', edgecolor='black', lw=0.8, zorder=7))
        # Door
        dw = max(14, w * 0.14)
        ax.add_patch(Rectangle((x + w / 2 - dw / 2, y), dw, h * 0.35,
                                 facecolor='#3E2723', edgecolor='black', zorder=7))
        # Fence run
        fence_ext = max(20, w * 0.4)
        for fy in [y - fence_ext, y - fence_ext * 0.5, y]:
            ax.plot([x - 3, x + w + 3], [fy, fy], color='#8D6E63', lw=1.5, zorder=5)
        for fx in np.linspace(x - 3, x + w + 3, max(4, int(w / 15))):
            ax.plot([fx, fx], [y - fence_ext, y], color='#8D6E63', lw=1.2, zorder=5)

    def _chicken_coop(self, ax, x, y, w, h, unit):
        self._shed_base(ax, x, y, w, h, '#FFF8E1', '#F57F17', 'CHICKEN COOP', unit)
        run_ext = max(20, h * 0.5)
        ax.add_patch(Rectangle((x - run_ext, y), run_ext, h,
                                 facecolor='#F1F8E9', edgecolor='#33691E',
                                 linestyle='--', alpha=0.45, lw=1.2, zorder=5))
        ax.text(x - run_ext / 2, y + h / 2, 'RUN',
                ha='center', va='center',
                fontsize=max(5, run_ext * 0.12), color='#33691E', zorder=6)

    def _piggery(self, ax, x, y, w, h, unit):
        self._shed_base(ax, x, y, w, h, '#FFCCBC', '#BF360C', 'PIGGERY', unit)
        sw = w / 3
        for i, s in enumerate(['FAR', 'NUR', 'GRW']):
            sx = x + i * sw
            if i > 0:
                ax.plot([sx, sx], [y, y + h], 'k-', lw=1.5, zorder=7)
            ax.text(sx + sw / 2, y + h / 2, s, ha='center', va='center',
                    fontsize=max(5, sw * 0.14), fontweight='bold',
                    color='#BF360C', zorder=7)

    def _cow_shed(self, ax, x, y, w, h, unit):
        self._shed_base(ax, x, y, w, h, '#D7CCC8', '#5D4037', 'COW SHED', unit)
        n = max(2, int(w / 40))
        sw = w / n
        for i in range(1, n):
            ax.plot([x + i * sw, x + i * sw], [y + h * .28, y + h],
                    color='#795548', lw=1.8, zorder=7)
        ax.add_patch(Rectangle((x, y), w, h * .28,
                                 facecolor='#EFEBE9', edgecolor='#5D4037',
                                 lw=1.2, zorder=7))
        ax.text(x + w / 2, y + h * .14, 'FEED ALLEY',
                ha='center', va='center',
                fontsize=max(5, w * 0.07), color='#5D4037', zorder=8)

    def _fish_tanks(self, ax, x, y, w, h, unit):
        self._shed_base(ax, x, y, w, h, '#B3E5FC', '#0288D1', 'FISH TANKS', unit)
        tw = (w - 12) / 2
        th = (h - 12) / 2
        for tx, ty in [(x + 4, y + 4), (x + 4 + tw + 4, y + 4),
                        (x + 4, y + 4 + th + 4), (x + 4 + tw + 4, y + 4 + th + 4)]:
            ax.add_patch(Rectangle((tx, ty), tw, th,
                                    facecolor='#4FC3F7', edgecolor='#0288D1',
                                    lw=1.5, zorder=7))
            ax.add_patch(Circle((tx + tw / 2, ty + th / 2),
                                  min(tw, th) * .22,
                                  facecolor='#B3E5FC', edgecolor='none',
                                  alpha=0.6, zorder=8))

    def _bee_hives(self, ax, x, y, w, h, unit):
        self._shed_base(ax, x, y, w, h, '#FFF176', '#F9A825', 'BEE HIVES', unit)
        n = max(1, int(w / max(14, w * 0.25)))
        hw_e = (w - 4) / n - 1.5
        for hi in range(n):
            hxe = x + 2 + hi * (hw_e + 1.5)
            ax.add_patch(FancyBboxPatch((hxe, y + 2), hw_e, h * .5,
                                         boxstyle='round,pad=1',
                                         facecolor=['#FFF176', '#FFD54F', '#FFCA28'][hi % 3],
                                         edgecolor='#F57F17', lw=1.5, zorder=7))
        np.random.seed(55)
        for _ in range(6):
            bx = x + np.random.uniform(0, w + 25)
            by = y + h + np.random.uniform(2, max(15, h * 0.3))
            ax.add_patch(Circle((bx, by), max(1.2, unit * 0.004),
                                  facecolor='#FDD835', edgecolor='#F57F17',
                                  lw=0.4, alpha=0.65, zorder=8))

    # ── Vegetation (food forest + buffer trees) ───────────────────────────────
    def _vegetation(self, ax, layout, L, W):
        zones    = layout.get('zone_positions', {})
        features = layout.get('features', {})
        unit     = min(L, W)

        sp_list = ['Mango', 'Jackfruit', 'Coconut', 'Banana', 'Guava',
                   'Papaya', 'Avocado', 'Moringa', 'Citrus', 'Neem', 'Teak', 'Bamboo']
        sp_sizes = {
            'Mango': 13, 'Jackfruit': 15, 'Coconut': 8, 'Banana': 7,
            'Guava': 9, 'Papaya': 6, 'Avocado': 11, 'Moringa': 7,
            'Citrus': 9, 'Neem': 14, 'Teak': 12, 'Bamboo': 5, 'default': 10
        }

        # Scale tree radius to plot
        r_scale = max(0.5, min(2.0, unit / 300.0))

        placements = list(layout.get('tree_placements', []))
        tree_count = layout.get('tree_count', 15)

        # Food Forest zone (z2)
        if 'z2' in zones:
            z = zones['z2']
            np.random.seed(42)
            needed = max(tree_count, 12)
            for idx in range(needed):
                rx = np.random.uniform(.05, .95)
                ry = np.random.uniform(.05, .95)
                placements.append({
                    'x': z['x'] + rx * z['width'],
                    'y': z['y'] + ry * z['height'],
                    'species': sp_list[idx % len(sp_list)],
                    'zone': 'z2',
                })

        # Buffer zone (z4) — sparse trees
        if 'z4' in zones:
            z4 = zones['z4']
            np.random.seed(77)
            n_buf = max(6, int(z4['width'] * z4['height'] / 2500))
            for idx in range(n_buf):
                rx = np.random.uniform(.04, .96)
                ry = np.random.uniform(.08, .92)
                placements.append({
                    'x': z4['x'] + rx * z4['width'],
                    'y': z4['y'] + ry * z4['height'],
                    'species': ['Neem', 'Teak', 'Bamboo'][idx % 3],
                    'zone': 'z4',
                })

        first_label = set()
        for t in placements:
            sp = t.get('species', 'Mango')
            r  = sp_sizes.get(sp, 10) * r_scale
            tx = t['x']
            ty = t['y']

            # Clamp inside relevant zone
            for zid in ('z2', 'z4'):
                if zid in zones and t.get('zone', '') == zid:
                    z_pos = zones[zid]
                    tx = max(z_pos['x'] + r + 2, min(tx, z_pos['x'] + z_pos['width'] - r - 2))
                    ty = max(z_pos['y'] + r + 2, min(ty, z_pos['y'] + z_pos['height'] - r - 2))

            tx = max(r + 3, min(tx, L - r - 3))
            ty = max(r + 3, min(ty, W - r - 3))

            # Skip if in pond area
            pond_ok = True
            if 'pond' in features and features['pond']:
                pf = features['pond']
                if np.hypot(tx - pf['x'], ty - pf['y']) < pf['radius'] * 1.2:
                    pond_ok = False
            if not pond_ok:
                continue

            if not self._reg.circle_ok(tx, ty, r):
                continue
            self._reg.add_circle(tx, ty, r)
            _draw_tree(ax, tx, ty, r, sp, zorder=7)

            if sp not in first_label:
                ax.text(tx, ty + r + max(4, r * 0.4), sp,
                        ha='center', fontsize=max(5, r * 0.45), color='#1B5E20',
                        zorder=8, path_effects=[pe.withStroke(linewidth=1.2, foreground='white')])
                first_label.add(sp)

    # ── Zone labels ───────────────────────────────────────────────────────────
    def _zone_labels(self, ax, layout, L, W):
        unit = min(L, W)
        hx, hy, hw, hh = self._house_bbox(layout, L, W)
        for zid, pos in layout.get('zone_positions', {}).items():
            cx = pos['x'] + pos['width'] / 2
            cy = pos['y'] + pos['height'] / 2
            area = int(pos['width'] * pos['height'])
            # Avoid label on house
            if hx <= cx <= hx + hw and hy <= cy <= hy + hh:
                cx = pos['x'] + pos['width'] * .82
            ax.text(cx, cy + max(6, unit * 0.018),
                    self.ZONE_NAMES.get(zid, zid),
                    ha='center', va='center',
                    fontsize=max(7, min(11, unit * 0.026)),
                    fontweight='bold', color='#1B5E20', zorder=13,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor='#A5D6A7', alpha=0.88, lw=0.9))
            ax.text(cx, cy - max(8, unit * 0.022), f'{area:,} sq.ft.',
                    ha='center', va='center',
                    fontsize=max(6, min(9, unit * 0.020)),
                    color='#33691E', zorder=13)

    # ── Cartographic elements ─────────────────────────────────────────────────
    def _north_arrow(self, ax, L, W):
        unit = min(L, W)
        nx, ny = L * .93, W * .07
        r = unit * 0.034
        ax.add_patch(Circle((nx, ny), r, facecolor='white',
                             edgecolor='#1A237E', lw=2.5, zorder=15))
        ax.annotate('', xy=(nx, ny + r * .74), xytext=(nx, ny - r * .38),
                    arrowprops=dict(arrowstyle='->', color='red', lw=2.5), zorder=16)
        ax.text(nx, ny + r + max(3, r * 0.4), 'N', ha='center',
                fontsize=max(10, r * 0.45), fontweight='bold', color='red', zorder=16)

    def _scale_bar(self, ax, L, W):
        unit = min(L, W)
        sx, sy = L * .04, W * .04
        sc = min(100, int(L * .18 / 10) * 10)
        half = sc / 2
        ax.add_patch(Rectangle((sx, sy - 3), half, 7,
                                 facecolor='black', edgecolor='none', zorder=15))
        ax.add_patch(Rectangle((sx + half, sy - 3), half, 7,
                                 facecolor='white', edgecolor='black', lw=0.8, zorder=15))
        ax.plot([sx, sx + sc], [sy + 4, sy + 4], 'k-', lw=0.5, zorder=15)
        ax.text(sx + sc / 2, sy - max(10, unit * 0.03), f'{sc} ft',
                ha='center', fontsize=max(7, unit * 0.022),
                fontweight='bold', zorder=15)
        ax.text(sx + sc / 2, sy + max(10, unit * 0.025), 'SCALE',
                ha='center', fontsize=max(6, unit * 0.019), zorder=15)

    def _legend(self, ax, L, W):
        unit = min(L, W)
        lx = L + unit * .06
        ly = W * .97
        fsize = max(7, min(10, unit * 0.026))
        items = [
            ('#ECEFF1',  'Residence (Roof Plan)'),
            ('#FFCCBC',  'Livestock Shed'),
            ('#29B6F6',  'Water / Pond'),
            ('#1565C0',  'Solar Array'),
            ('#E0F2F1',  'Greenhouse'),
            ('#2E7D32',  'Food Forest Trees'),
            ('#3E2723',  'Raised Garden Beds'),
            (self.ZONE_COLORS['z0'], 'Zone 0 – Residential'),
            (self.ZONE_COLORS['z1'], 'Zone 1 – Kitchen Garden'),
            (self.ZONE_COLORS['z2'], 'Zone 2 – Food Forest'),
            (self.ZONE_COLORS['z3'], 'Zone 3 – Pasture / Crops'),
            (self.ZONE_COLORS['z4'], 'Zone 4 – Buffer Zone'),
        ]
        bh = fsize * 2.4
        total_h = len(items) * bh + 36
        box_w = max(140, unit * 0.42)
        ax.add_patch(FancyBboxPatch((lx - 10, ly - total_h), box_w, total_h + 8,
                                     boxstyle='round,pad=5', facecolor='white',
                                     edgecolor='#546E7A', lw=2, alpha=0.97, zorder=14))
        ax.text(lx + box_w / 2 - 10, ly + 2, 'LEGEND',
                ha='center', fontsize=fsize + 2, fontweight='bold',
                color='#1A237E', zorder=15)
        for i, (c, label) in enumerate(items):
            yp = ly - (i + 1) * bh + 6
            ax.add_patch(Rectangle((lx, yp), max(12, unit * 0.035),
                                    max(10, fsize * 1.3),
                                    facecolor=c, edgecolor='#546E7A',
                                    lw=0.8, zorder=15))
            ax.text(lx + max(16, unit * 0.042), yp + max(5, fsize * 0.65),
                    label, fontsize=fsize, va='center', zorder=15)

    def _dimensions(self, ax, L, W):
        unit = min(L, W)
        off = unit * .055
        ax.annotate('', xy=(0, -off), xytext=(L, -off),
                    arrowprops=dict(arrowstyle='<->', color='#1A237E', lw=1.8), zorder=13)
        ax.text(L / 2, -off - max(12, unit * 0.032),
                f'{int(L)} ft', ha='center',
                fontsize=max(9, unit * 0.028), fontweight='bold', color='#1A237E')
        ax.annotate('', xy=(-off, 0), xytext=(-off, W),
                    arrowprops=dict(arrowstyle='<->', color='#1A237E', lw=1.8), zorder=13)
        ax.text(-off - max(14, unit * 0.038), W / 2,
                f'{int(W)} ft', ha='center',
                fontsize=max(9, unit * 0.028), fontweight='bold',
                color='#1A237E', rotation=90)

    def _title(self, ax, layout, L, W):
        unit = min(L, W)
        acres = layout.get('acres', layout.get('total_sqft', 0) / 43560)
        total = layout.get('total_sqft', 0)
        cat   = layout.get('category', '').upper()
        loc   = layout.get('location', '')
        loc_str = f' · {loc}' if loc else ''
        title = f"{acres:.2f} ACRE HOMESTEAD{loc_str}\n{int(total):,} SQ.FT.  ·  {cat} SCALE"
        ax.text(L / 2, W + unit * .075, title,
                ha='center', va='bottom',
                fontsize=max(11, min(16, unit * 0.040)),
                fontweight='bold', color='#1B5E20',
                bbox=dict(boxstyle='round,pad=0.6', facecolor='#E8F5E9',
                          edgecolor='#2E7D32', lw=2.5),
                zorder=16)
