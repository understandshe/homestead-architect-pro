"""
Professional 2D Site-Plan Visualizer — v5 FINAL
Homestead Architect Pro 2026

Rules:
- Zero overlaps (strict registry, no force bypass except water/house)
- Proportional scaling: 100ft x 100ft to 3000ft+ plots
- Smart placement: Gate → Road → House → Garden → Livestock → Forest
- Dynamic animal handling: any combo, any count
- Water placed by slope logic
- Professional aerial-view output
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import (
    FancyBboxPatch, Circle, Rectangle, Polygon, Arc
)
import matplotlib.patheffects as pe
import numpy as np
from io import BytesIO
from typing import List, Tuple, Optional, Dict, Any


# ── Tree color palette ────────────────────────────────────────────────────────
TREE_COLORS = {
    'Mango':   ('#2E7D32', '#388E3C'), 'Jackfruit': ('#1B5E20', '#2E7D32'),
    'Coconut': ('#33691E', '#558B2F'), 'Banana':    ('#558B2F', '#7CB342'),
    'Guava':   ('#33691E', '#43A047'), 'Papaya':    ('#558B2F', '#8BC34A'),
    'Avocado': ('#2E7D32', '#1B5E20'), 'Moringa':   ('#66BB6A', '#4CAF50'),
    'Citrus':  ('#43A047', '#66BB6A'), 'Neem':      ('#388E3C', '#2E7D32'),
    'Teak':    ('#1B5E20', '#2E7D32'), 'Bamboo':    ('#4CAF50', '#8BC34A'),
    'default': ('#2E7D32', '#388E3C'),
}

SP_SIZES = {
    'Mango': 0.90, 'Jackfruit': 1.0, 'Coconut': 0.65, 'Banana': 0.55,
    'Guava': 0.70, 'Papaya': 0.50, 'Avocado': 0.80, 'Moringa': 0.55,
    'Citrus': 0.65, 'Neem': 0.90, 'Teak': 0.85, 'Bamboo': 0.40,
    'default': 0.70,
}

SP_LIST = ['Mango', 'Jackfruit', 'Coconut', 'Banana', 'Guava',
           'Papaya', 'Avocado', 'Moringa', 'Citrus', 'Neem', 'Teak', 'Bamboo']


# ── Bounding-box registry ─────────────────────────────────────────────────────
class _Reg2D:
    GAP = 3.0

    def __init__(self, L: float, W: float):
        self.L = L
        self.W = W
        self.rects: List[Tuple]   = []
        self.circles: List[Tuple] = []

    def add_rect(self, x, y, w, h):
        self.rects.append((float(x), float(y), float(w), float(h)))

    def add_circle(self, cx, cy, r):
        self.circles.append((float(cx), float(cy), float(r)))

    def rect_ok(self, x, y, w, h) -> bool:
        g = self.GAP
        x, y, w, h = float(x), float(y), float(w), float(h)
        # Plot boundary check
        if x < 0 or y < 0 or x + w > self.L or y + h > self.W:
            return False
        for (rx, ry, rw, rh) in self.rects:
            if (x - g < rx + rw and x + w + g > rx and
                    y - g < ry + rh and y + h + g > ry):
                return False
        for (cx, cy, cr) in self.circles:
            nx = max(x, min(cx, x + w))
            ny = max(y, min(cy, y + h))
            if (cx - nx) ** 2 + (cy - ny) ** 2 < (cr + g) ** 2:
                return False
        return True

    def circle_ok(self, cx, cy, r) -> bool:
        g = self.GAP
        cx, cy, r = float(cx), float(cy), float(r)
        if cx - r < 0 or cy - r < 0 or cx + r > self.L or cy + r > self.W:
            return False
        for (rx, ry, rw, rh) in self.rects:
            nx = max(rx, min(cx, rx + rw))
            ny = max(ry, min(cy, ry + rh))
            if (cx - nx) ** 2 + (cy - ny) ** 2 < (r + g) ** 2:
                return False
        for (ocx, ocy, or_) in self.circles:
            if (cx - ocx) ** 2 + (cy - ocy) ** 2 < (r + or_ + g) ** 2:
                return False
        return True

    def register_rect(self, x, y, w, h):
        self.rects.append((float(x), float(y), float(w), float(h)))

    def register_circle(self, cx, cy, r):
        self.circles.append((float(cx), float(cy), float(r)))


# ── Drawing helpers ───────────────────────────────────────────────────────────
def _draw_tree(ax, tx, ty, r, species='default', zorder=7):
    c1, c2 = TREE_COLORS.get(species, TREE_COLORS['default'])
    ax.add_patch(Circle((tx + r * 0.22, ty - r * 0.22), r,
                         facecolor='#1A3A1A', edgecolor='none', alpha=0.14, zorder=zorder - 1))
    np.random.seed(abs(hash(species + str(int(tx * 10)))) % 9999)
    n = 14
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    radii  = r * (0.80 + 0.20 * np.random.rand(n))
    bx = tx + radii * np.cos(angles)
    by = ty + radii * np.sin(angles)
    ax.add_patch(Polygon(list(zip(bx, by)),
                          facecolor=c1, edgecolor=c2, linewidth=0.7,
                          alpha=0.93, zorder=zorder))
    ax.add_patch(Circle((tx - r * 0.20, ty + r * 0.20), r * 0.28,
                         facecolor='white', edgecolor='none', alpha=0.12, zorder=zorder + 1))


def _raised_bed(ax, x, y, w, h, zorder=6):
    frame_t = min(w, h) * 0.13
    # Outer frame
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0',
                                 facecolor='#8D6E63', edgecolor='#5D4037',
                                 linewidth=max(1.2, min(w, h) * 0.05), zorder=zorder))
    # Soil
    ax.add_patch(Rectangle((x + frame_t, y + frame_t),
                             w - 2 * frame_t, h - 2 * frame_t,
                             facecolor='#3E2723', edgecolor='none', zorder=zorder + 1))
    # Plant dots
    iw = w - 2 * frame_t - 2
    ih = h - 2 * frame_t - 2
    if iw < 3 or ih < 3:
        return
    nc = max(1, int(iw / max(6, w * 0.14)))
    nr = max(1, int(ih / max(6, h * 0.14)))
    pr = min(iw / nc, ih / nr) * 0.26
    pc = ['#4CAF50', '#66BB6A', '#81C784', '#A5D6A7', '#2E7D32']
    for ri in range(nr):
        for ci in range(nc):
            px = x + frame_t + 1 + (ci + 0.5) * iw / nc
            py = y + frame_t + 1 + (ri + 0.5) * ih / nr
            ax.add_patch(Circle((px, py), pr,
                                  facecolor=pc[(ri + ci) % len(pc)],
                                  edgecolor='#1B5E20', linewidth=0.2, zorder=zorder + 2))


def _draw_road(ax, points, width, color='#D2B48C', alpha=0.88, zorder=4):
    """Draw a smooth road through waypoints using catmull-rom spline."""
    if len(points) < 2:
        return
    pts = np.array(points, dtype=float)
    n = len(pts)
    xs, ys = [], []
    for i in range(n - 1):
        p0 = pts[max(0, i - 1)]
        p1 = pts[i]
        p2 = pts[i + 1]
        p3 = pts[min(n - 1, i + 2)]
        t1 = (p2 - p0) * 0.5
        t2 = (p3 - p1) * 0.5
        steps = max(15, int(np.hypot(*(p2 - p1)) / 6) + 1)
        for s in np.linspace(0, 1, steps):
            h00 = 2*s**3 - 3*s**2 + 1
            h10 = s**3 - 2*s**2 + s
            h01 = -2*s**3 + 3*s**2
            h11 = s**3 - s**2
            pt  = h00*p1 + h10*t1 + h01*p2 + h11*t2
            xs.append(pt[0]); ys.append(pt[1])

    xs = np.array(xs); ys = np.array(ys)
    dx = np.gradient(xs); dy = np.gradient(ys)
    ln = np.hypot(dx, dy) + 1e-9
    nx_, ny_ = -dy / ln, dx / ln
    hw = width / 2
    x_up = xs + nx_ * hw; y_up = ys + ny_ * hw
    x_dn = xs - nx_ * hw; y_dn = ys - ny_ * hw
    xp = np.concatenate([x_up, x_dn[::-1]])
    yp = np.concatenate([y_up, y_dn[::-1]])
    ax.fill(xp, yp, color=color, alpha=alpha, zorder=zorder)
    ax.plot(x_up, y_up, color='#BCAAA4', lw=0.7, alpha=0.6, zorder=zorder + 1)
    ax.plot(x_dn, y_dn, color='#BCAAA4', lw=0.7, alpha=0.6, zorder=zorder + 1)


# ── Main class ────────────────────────────────────────────────────────────────
class Visualizer2D:

    ZONE_COLORS = {
        'z0': '#F0EAD6', 'z1': '#C5E1A5', 'z2': '#388E3C',
        'z3': '#FFF9C4', 'z4': '#A5D6A7',
    }
    ZONE_NAMES = {
        'z0': 'ZONE 0\nRESIDENTIAL',    'z1': 'ZONE 1\nKITCHEN GARDEN',
        'z2': 'ZONE 2\nFOOD FOREST',     'z3': 'ZONE 3\nPASTURE / CROPS',
        'z4': 'ZONE 4\nBUFFER',
    }

    def __init__(self):
        self._reg: Optional[_Reg2D] = None
        self._L = 300.0
        self._W = 300.0

    # ─────────────────────────────────────────────────────────────────────────
    #  PUBLIC API
    # ─────────────────────────────────────────────────────────────────────────
    def create(self, layout: dict, answers: dict) -> BytesIO:
        dims = layout.get('dimensions', {})
        L = float(dims.get('L', dims.get('length', 300)))
        W = float(dims.get('W', dims.get('width', 300)))
        L = max(50.0, L); W = max(50.0, W)

        self._reg = _Reg2D(L, W)
        self._L = L
        self._W = W

        unit  = min(L, W)           # reference dimension for scaling
        small = unit < 150          # small plot flag

        fig_w = 18
        fig_h = max(10, fig_w * (W / L) * 0.72)
        fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=150)
        fig.patch.set_facecolor('#F9F6F0')
        ax.set_facecolor('#5A8F3C')

        # ── Draw order: back → front ──────────────────────────────────────────
        self._grass_texture(ax, L, W, unit)
        self._zones(ax, layout, L, W)
        self._contour_lines(ax, layout, L, W)
        self._perimeter_and_gate(ax, L, W, unit)

        # Register house FIRST so all others avoid it
        hx, hy, hw, hh = self._house_bbox(layout, L, W, unit)
        self._reg.register_rect(hx, hy, hw, hh)

        # Road system (gate → house → zones), before structures
        self._road_system(ax, layout, L, W, unit, hx, hy, hw, hh, small)

        # Water (before trees/sheds so they avoid pond)
        self._water_features(ax, layout, L, W, unit)

        # Utilities
        self._utilities(ax, layout, L, W, unit, small)

        # Livestock sheds (dynamic, all user-selected animals)
        self._livestock_housing(ax, layout, L, W, unit, small)

        # Kitchen garden beds
        self._kitchen_garden_beds(ax, layout, L, W, unit, small)

        # Food forest trees
        self._vegetation(ax, layout, L, W, unit, small)

        # House drawn last (on top)
        self._house_plan(ax, layout, L, W, unit, hx, hy, hw, hh)

        # Labels + cartographic
        self._zone_labels(ax, layout, L, W, unit, hx, hy, hw, hh)
        self._north_arrow(ax, L, W, unit)
        self._scale_bar(ax, L, W, unit)
        self._legend(ax, L, W, unit)
        self._dimensions(ax, L, W, unit)
        self._title(ax, layout, L, W, unit)

        margin = max(L, W) * 0.18
        ax.set_xlim(-margin, L + margin * 1.9)
        ax.set_ylim(-margin * 1.1, W + margin)
        ax.set_aspect('equal')
        ax.axis('off')
        plt.tight_layout(pad=0.3)

        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=180, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        buf.seek(0)
        plt.close(fig)
        return buf

    # ─────────────────────────────────────────────────────────────────────────
    #  GRASS TEXTURE
    # ─────────────────────────────────────────────────────────────────────────
    def _grass_texture(self, ax, L, W, unit):
        ax.add_patch(Rectangle((0, 0), L, W, facecolor='#5A8F3C',
                                edgecolor='none', zorder=0))
        np.random.seed(1)
        density = max(150, min(500, int(L * W / 250)))
        gl_max = max(4, unit * 0.020)
        for _ in range(density):
            gx = np.random.uniform(1, L - 1)
            gy = np.random.uniform(1, W - 1)
            gl = np.random.uniform(2, gl_max)
            gc = ['#4CAF50', '#66BB6A', '#388E3C', '#2E7D32'][_ % 4]
            ax.plot([gx, gx + np.random.uniform(-1, 1)], [gy, gy + gl],
                    color=gc, lw=0.25, alpha=0.09, zorder=0)

    # ─────────────────────────────────────────────────────────────────────────
    #  ZONES
    # ─────────────────────────────────────────────────────────────────────────
    def _zones(self, ax, layout, L, W):
        for zid, pos in layout.get('zone_positions', {}).items():
            ax.add_patch(Rectangle(
                (pos['x'], pos['y']), pos['width'], pos['height'],
                facecolor=self.ZONE_COLORS.get(zid, '#CCC'),
                edgecolor='#546E7A', linewidth=1.2, alpha=0.38, zorder=2))

    # ─────────────────────────────────────────────────────────────────────────
    #  CONTOUR LINES
    # ─────────────────────────────────────────────────────────────────────────
    def _contour_lines(self, ax, layout, L, W):
        slope = layout.get('slope', 'Flat')
        if slope == 'Flat':
            return
        for idx in range(1, 6):
            frac = idx / 6
            if slope in ('South', 'North'):
                y = W * frac if slope == 'South' else W * (1 - frac)
                ax.plot([0, L], [y, y], color='#A5D6A7',
                        linestyle='--', lw=0.55, alpha=0.45, zorder=1)
            elif slope in ('East', 'West'):
                x = L * frac if slope == 'East' else L * (1 - frac)
                ax.plot([x, x], [0, W], color='#A5D6A7',
                        linestyle='--', lw=0.55, alpha=0.45, zorder=1)
            else:  # Mixed
                y = W * frac
                ax.plot([0, L], [y, W - y], color='#A5D6A7',
                        linestyle='--', lw=0.45, alpha=0.35, zorder=1)

    # ─────────────────────────────────────────────────────────────────────────
    #  PERIMETER FENCE + GATE
    # ─────────────────────────────────────────────────────────────────────────
    def _perimeter_and_gate(self, ax, L, W, unit):
        post_gap = max(unit * 0.038, 8.0)
        post_w   = max(post_gap * 0.09, 1.8)
        post_h   = post_w * 2.0
        z = 3

        def _fence_seg(x0, y0, x1, y1):
            dx = x1 - x0; dy = y1 - y0
            length = np.hypot(dx, dy)
            if length < 1:
                return
            ux, uy = dx / length, dy / length
            nx_v, ny_v = -uy, ux
            # Rails
            for rt in [0.28, 0.68]:
                off = post_h * (rt - 0.5) * 0.75
                ax.plot([x0 + nx_v*off, x1 + nx_v*off],
                        [y0 + ny_v*off, y1 + ny_v*off],
                        color='#A1887F', lw=max(1.5, post_w * 0.7),
                        solid_capstyle='round', zorder=z)
            # Posts
            n_posts = max(2, int(length / post_gap))
            for i in range(n_posts + 1):
                t = i / n_posts
                ax.add_patch(FancyBboxPatch(
                    (x0 + t*dx - post_w/2, y0 + t*dy - post_h/2),
                    post_w, post_h, boxstyle='round,pad=0.2',
                    facecolor='#5D4037', edgecolor='#3E2723',
                    linewidth=0.5, zorder=z + 1))

        gate_cx = L / 2
        gate_hw = max(unit * 0.038, 14.0)
        _fence_seg(0, 0, gate_cx - gate_hw, 0)
        _fence_seg(gate_cx + gate_hw, 0, L, 0)
        _fence_seg(0, W, L, W)
        _fence_seg(0, 0, 0, W)
        _fence_seg(L, 0, L, W)

        # Gate posts
        gp_w = post_w * 1.5; gp_h = post_h * 1.35
        for gx in [gate_cx - gate_hw - gp_w, gate_cx + gate_hw]:
            ax.add_patch(FancyBboxPatch(
                (gx, -gp_h/2), gp_w, gp_h, boxstyle='round,pad=0.2',
                facecolor='#4E342E', edgecolor='#1A237E',
                linewidth=1.6, zorder=z + 3))
        ax.text(gate_cx, -gp_h - max(5, unit*0.016), 'MAIN GATE',
                ha='center', va='top',
                fontsize=max(7, unit*0.021), fontweight='bold', color='#1A237E',
                zorder=z+4, bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
                                      edgecolor='#1A237E', alpha=0.85, lw=0.9))
        # Store gate position
        self._gate_cx = gate_cx
        self._gate_hw = gate_hw

    # ─────────────────────────────────────────────────────────────────────────
    #  HOUSE BBOX — fixed realistic size
    # ─────────────────────────────────────────────────────────────────────────
    def _house_bbox(self, layout, L, W, unit) -> Tuple[float, float, float, float]:
        """
        House: realistic size = 12-16% of min(L,W), clamped 40–110ft wide.
        Centered in Z0 zone, respecting house_position.
        """
        zone_positions = layout.get('zone_positions', {})
        z0 = zone_positions.get('z0', {'x': 0, 'y': 0, 'width': L, 'height': W})

        hw = max(40.0, min(unit * 0.15, 110.0))
        hh = max(28.0, min(unit * 0.11, 80.0))

        z0_cx = z0['x'] + z0['width']  / 2
        z0_cy = z0['y'] + z0['height'] / 2

        hx = max(z0['x'] + 3, min(z0_cx - hw/2, z0['x'] + z0['width']  - hw - 3))
        hy = max(z0['y'] + 3, min(z0_cy - hh/2, z0['y'] + z0['height'] - hh - 3))

        return hx, hy, hw, hh

    # ─────────────────────────────────────────────────────────────────────────
    #  ROAD SYSTEM: Gate → House → Garden → Livestock
    # ─────────────────────────────────────────────────────────────────────────
    def _road_system(self, ax, layout, L, W, unit, hx, hy, hw, hh, small):
        if small:
            # Small plot: simple straight path only
            road_w = max(4, unit * 0.028)
            door_cx = hx + hw / 2
            _draw_road(ax, [(door_cx, 0), (door_cx, hy)],
                       road_w, '#D2B48C', zorder=4)
            self._reg.register_rect(door_cx - road_w/2, 0, road_w, hy)
            return

        road_w_main = max(8, unit * 0.032)
        road_w_sec  = max(5, unit * 0.020)
        gate_cx = getattr(self, '_gate_cx', L / 2)
        door_cx = hx + hw / 2

        # 1) Main road: gate → house front door (slight curve)
        mid_y = hy * 0.45
        mid_x = door_cx + (gate_cx - door_cx) * 0.18
        pts_main = [
            (gate_cx,  0),
            (mid_x,    mid_y),
            (door_cx,  hy),
        ]
        _draw_road(ax, pts_main, road_w_main, '#D2B48C', alpha=0.90, zorder=4)
        self._reg.register_rect(
            min(gate_cx, door_cx) - road_w_main,
            0, abs(gate_cx - door_cx) + road_w_main * 2, hy)

        zones = layout.get('zone_positions', {})

        # 2) Garden path: house → Z1 (kitchen garden)
        if 'z1' in zones:
            z1 = zones['z1']
            z1_cx = z1['x'] + z1['width'] * 0.5
            z1_cy = z1['y']
            _draw_road(ax, [
                (hx + hw * 0.5, hy + hh),
                (hx + hw * 0.5 + (z1_cx - hx - hw*0.5)*0.5, (hy+hh+z1_cy)*0.5),
                (z1_cx, z1_cy),
            ], road_w_sec, '#D7CCC8', alpha=0.78, zorder=4)

        # 3) Farm road: house → Z3 (livestock)
        if 'z3' in zones:
            z3 = zones['z3']
            z3_dest_x = z3['x'] + z3['width'] * 0.35
            z3_dest_y = z3['y']
            _draw_road(ax, [
                (hx + hw * 0.8, hy + hh),
                (hx + hw * 0.8 + L*0.02, (hy+hh + z3_dest_y)*0.5),
                (z3_dest_x, z3_dest_y),
            ], road_w_sec, '#D7CCC8', alpha=0.72, zorder=4)

    # ─────────────────────────────────────────────────────────────────────────
    #  WATER FEATURES
    # ─────────────────────────────────────────────────────────────────────────
    def _water_features(self, ax, layout, L, W, unit):
        features = layout.get('features', {})
        z = 7
        slope = layout.get('slope', 'Flat')

        # Well / Borewell
        for key in ('borewell', 'well'):
            if key not in features:
                continue
            f = features[key]
            r = float(f.get('radius', unit * 0.020))
            r = max(unit * 0.012, min(r, unit * 0.038))
            wx, wy = float(f['x']), float(f['y'])
            # Clamp inside plot
            wx = max(r+2, min(wx, L-r-2))
            wy = max(r+2, min(wy, W-r-2))
            # Force register & draw
            self._reg.register_circle(wx, wy, r)
            ax.add_patch(Circle((wx, wy), r, facecolor='#4FC3F7',
                                 edgecolor='#0288D1', lw=max(1.8, r*0.12), zorder=z))
            ax.add_patch(Circle((wx, wy), r*0.68, facecolor='#81D4FA',
                                 edgecolor='none', zorder=z))
            fs = max(6, r * 0.30)
            ax.text(wx, wy, 'W', ha='center', va='center',
                    fontsize=fs, fontweight='bold', color='white', zorder=z+1)
            ax.text(wx, wy - r - max(5, r*0.35), 'WELL/BOREWELL',
                    ha='center', fontsize=max(5, r*0.22), color='#0288D1', zorder=z+1)
            break

        # Pond — ALWAYS drawn, forced
        if 'pond' in features and features['pond']:
            f = features['pond']
            r = float(f.get('radius', unit * 0.06))
            r = max(unit * 0.04, min(r, unit * 0.12))
            px, py = float(f['x']), float(f['y'])
            px = max(r+2, min(px, L-r-2))
            py = max(r+2, min(py, W-r-2))

            self._reg.register_circle(px, py, r * 1.15)

            # Outer glow / shadow
            ax.add_patch(Circle((px + r*0.07, py - r*0.07), r*1.08,
                                  facecolor='#1A237E', alpha=0.10,
                                  edgecolor='none', zorder=z-1))
            # Main body — organic shape
            theta = np.linspace(0, 2*np.pi, 60)
            rip   = 1 + 0.09*np.sin(3*theta) + 0.05*np.cos(5*theta)
            ax.add_patch(Polygon(
                list(zip(px + r*rip*np.cos(theta), py + r*rip*np.sin(theta))),
                facecolor='#29B6F6', edgecolor='#0288D1',
                lw=max(1.8, r*0.06), alpha=0.92, zorder=z))
            # Inner shimmer
            ax.add_patch(Polygon(
                list(zip(px + r*0.45*np.cos(theta), py + r*0.45*np.sin(theta))),
                facecolor='#81D4FA', edgecolor='none', alpha=0.50, zorder=z))
            # Ripple rings
            for rf in [0.30, 0.68]:
                ax.add_patch(Circle((px, py), r*rf, facecolor='none',
                                     edgecolor='#4FC3F7',
                                     lw=max(0.4, r*0.018), alpha=0.40, zorder=z+1))
            # Lily pads
            np.random.seed(77)
            n_lily = max(3, int(r * 0.35))
            for _ in range(n_lily):
                ang = np.random.uniform(0, 2*np.pi)
                d   = np.random.uniform(0, r*0.42)
                ax.add_patch(Circle(
                    (px + d*np.cos(ang), py + d*np.sin(ang)),
                    max(1.5, r*0.055),
                    facecolor='#4CAF50', edgecolor='none', alpha=0.70, zorder=z+1))
            # Label
            ax.text(px, py, 'POND', ha='center', va='center',
                    fontsize=max(7, r*0.19), color='#01579B',
                    fontweight='bold', zorder=z+2,
                    path_effects=[pe.withStroke(linewidth=1.4, foreground='white')])

        # Rain tank
        if 'rain_tank' in features and features['rain_tank']:
            f = features['rain_tank']
            rx, ry = float(f['x']), float(f['y'])
            rw, rh = float(f['width']), float(f['height'])
            if self._reg.rect_ok(rx, ry, rw, rh):
                self._reg.register_rect(rx, ry, rw, rh)
                ax.add_patch(FancyBboxPatch((rx, ry), rw, rh,
                                             boxstyle='round,pad=2',
                                             facecolor='#B3E5FC', edgecolor='#0288D1',
                                             lw=1.8, zorder=z))
                for by in np.linspace(ry+rh*0.2, ry+rh*0.8, 3):
                    ax.plot([rx+3, rx+rw-3], [by, by], color='#0288D1', lw=0.7, zorder=z+1)
                ax.text(rx+rw/2, ry+rh/2, 'RAIN\nTANK',
                        ha='center', va='center',
                        fontsize=max(5, rw*0.09), color='#01579B',
                        fontweight='bold', zorder=z+1)

    # ─────────────────────────────────────────────────────────────────────────
    #  UTILITIES: Solar, Greenhouse
    # ─────────────────────────────────────────────────────────────────────────
    def _utilities(self, ax, layout, L, W, unit, small):
        features = layout.get('features', {})
        z = 6

        if 'solar' in features and features['solar']:
            f = features['solar']
            sx, sy = float(f['x']), float(f['y'])
            sw, sh = float(f['width']), float(f['height'])
            if self._reg.rect_ok(sx, sy, sw, sh):
                self._reg.register_rect(sx, sy, sw, sh)
                ax.add_patch(Rectangle((sx, sy), sw, sh,
                                        facecolor='#90A4AE', edgecolor='#37474F',
                                        lw=1.4, zorder=z))
                rows, cols, g = 2, 3, 1.2
                if sw > 4 and sh > 4:
                    cw = max(1, (sw - g*(cols+1)) / cols)
                    ch = max(1, (sh - g*(rows+1)) / rows)
                    for row in range(rows):
                        for col in range(cols):
                            px = sx + g + col*(cw+g)
                            py = sy + g + row*(ch+g)
                            ax.add_patch(Rectangle((px, py), cw, ch,
                                                    facecolor='#1565C0', edgecolor='#0D47A1',
                                                    lw=0.7, zorder=z+1))
                ax.text(sx+sw/2, sy+sh+max(6,unit*0.014), 'SOLAR ARRAY',
                        ha='center', fontsize=max(5, sw*0.065),
                        fontweight='bold', color='#0D47A1', zorder=z+2)

        if 'greenhouse' in features and features['greenhouse']:
            f = features['greenhouse']
            gx, gy = float(f['x']), float(f['y'])
            gw, gh = float(f['width']), float(f['height'])
            if self._reg.rect_ok(gx, gy, gw, gh):
                self._reg.register_rect(gx, gy, gw, gh)
                ax.add_patch(Rectangle((gx, gy), gw, gh,
                                        facecolor='#E0F2F1', edgecolor='#00695C',
                                        lw=1.8, linestyle='--', alpha=0.80, zorder=z))
                ax.add_patch(Arc((gx+gw/2, gy+gh), gw, gh*0.30,
                                  angle=0, theta1=0, theta2=180,
                                  color='#00695C', lw=1.8, zorder=z+1))
                ax.text(gx+gw/2, gy-max(8,unit*0.018), 'GREENHOUSE',
                        ha='center', fontsize=max(5, gw*0.065),
                        color='#004D40', zorder=z+2)

    # ─────────────────────────────────────────────────────────────────────────
    #  LIVESTOCK HOUSING — dynamic, ALL user-selected animals
    # ─────────────────────────────────────────────────────────────────────────
    def _livestock_housing(self, ax, layout, L, W, unit, small):
        features = layout.get('features', {})
        z = 6

        SHED_DRAW = {
            'goat_shed':    self._goat_shed,
            'chicken_coop': self._chicken_coop,
            'piggery':      self._piggery,
            'cow_shed':     self._cow_shed,
            'fish_tanks':   self._fish_tanks,
            'bee_hives':    self._bee_hives,
        }

        for key, draw_fn in SHED_DRAW.items():
            if key not in features or not features[key]:
                continue
            f = features[key]
            if not isinstance(f, dict):
                continue
            sx = float(f.get('x', 0)); sy = float(f.get('y', 0))
            sw = float(f.get('width', 30)); sh = float(f.get('height', 25))
            # Clamp inside plot
            sx = max(1, min(sx, L - sw - 1))
            sy = max(1, min(sy, W - sh - 1))
            # Register & draw (force — layout engine placed them)
            self._reg.register_rect(sx, sy, sw, sh)
            draw_fn(ax, sx, sy, sw, sh, unit, z)

    def _shed_base(self, ax, x, y, w, h, fc, ec, label, unit, z):
        lw = max(1.4, min(w, h) * 0.040)
        # Shadow
        ax.add_patch(Rectangle((x+2, y-2), w, h,
                                 facecolor='#5D4037', edgecolor='none',
                                 alpha=0.18, zorder=z-1))
        # Body
        ax.add_patch(Rectangle((x, y), w, h,
                                 facecolor=fc, edgecolor=ec, lw=lw, zorder=z))
        # Roof triangle
        roof_h = min(h * 0.22, max(10, unit * 0.028))
        ax.add_patch(Polygon(
            [[x-2, y+h], [x+w/2, y+h+roof_h], [x+w+2, y+h]],
            facecolor='#A1887F', edgecolor=ec, lw=lw*0.6, zorder=z+1))
        ax.text(x+w/2, y+h+roof_h+max(5,unit*0.012), label,
                ha='center', fontsize=max(6, unit*0.019),
                fontweight='bold', color=ec, zorder=z+2,
                path_effects=[pe.withStroke(linewidth=1.4, foreground='white')])

    def _goat_shed(self, ax, x, y, w, h, unit, z):
        self._shed_base(ax, x, y, w, h, '#FFCCBC', '#5D4037', 'GOAT SHED', unit, z)
        # Windows
        for vx in [x+w*0.2, x+w*0.5, x+w*0.8]:
            ww = max(6, w*0.09); wh = max(5, h*0.11)
            ax.add_patch(Rectangle((vx-ww/2, y+h-wh-2), ww, wh,
                                    facecolor='#B3E5FC', edgecolor='#555', lw=0.7, zorder=z+1))
        # Door
        dw = max(10, w*0.16)
        ax.add_patch(Rectangle((x+w/2-dw/2, y), dw, h*0.36,
                                 facecolor='#3E2723', edgecolor='#111', lw=0.7, zorder=z+1))
        # Fence run in front
        fe = max(18, h*0.5)
        for fy in [y-fe, y-fe*0.5, y]:
            ax.plot([x-2, x+w+2], [fy, fy], color='#8D6E63', lw=1.3, zorder=z-1)
        for fx in np.linspace(x-2, x+w+2, max(4, int(w/14))):
            ax.plot([fx, fx], [y-fe, y], color='#8D6E63', lw=1.0, zorder=z-1)

    def _chicken_coop(self, ax, x, y, w, h, unit, z):
        self._shed_base(ax, x, y, w, h, '#FFF8E1', '#F57F17', 'CHICKEN COOP', unit, z)
        # Run area
        run_ext = max(18, h*0.45)
        ax.add_patch(Rectangle((x-run_ext, y), run_ext, h,
                                 facecolor='#F1F8E9', edgecolor='#33691E',
                                 linestyle='--', alpha=0.40, lw=1.1, zorder=z-1))
        ax.text(x-run_ext/2, y+h/2, 'RUN',
                ha='center', va='center',
                fontsize=max(5, run_ext*0.11), color='#33691E', zorder=z)
        # Chicken door
        cdw = max(7, w*0.14)
        ax.add_patch(Polygon([[x+w*0.35,y],[x+w*0.50,y-cdw*0.8],[x+w*0.65,y]],
                               facecolor='#D7CCC8', edgecolor='#5D4037', zorder=z+1))

    def _piggery(self, ax, x, y, w, h, unit, z):
        self._shed_base(ax, x, y, w, h, '#FFCCBC', '#BF360C', 'PIGGERY', unit, z)
        sw = w / 3
        for i, s in enumerate(['FAR', 'NUR', 'GRW']):
            sx = x + i * sw
            if i > 0:
                ax.plot([sx, sx], [y, y+h], color='#BF360C', lw=1.4, zorder=z+1)
            ax.text(sx+sw/2, y+h/2, s, ha='center', va='center',
                    fontsize=max(5, sw*0.13), fontweight='bold',
                    color='#BF360C', zorder=z+2)
        # Mud pit
        ax.add_patch(Circle((x+w/2, y+h*0.25), max(5, w*0.08),
                              facecolor='#8D6E63', edgecolor='none', alpha=0.55, zorder=z+1))

    def _cow_shed(self, ax, x, y, w, h, unit, z):
        self._shed_base(ax, x, y, w, h, '#D7CCC8', '#5D4037', 'COW SHED', unit, z)
        n = max(2, int(w / 38))
        sw = w / n
        for i in range(1, n):
            ax.plot([x+i*sw, x+i*sw], [y+h*0.28, y+h],
                    color='#795548', lw=1.6, zorder=z+1)
        ax.add_patch(Rectangle((x, y), w, h*0.28,
                                 facecolor='#EFEBE9', edgecolor='#5D4037',
                                 lw=1.1, zorder=z+1))
        ax.text(x+w/2, y+h*0.14, 'FEED ALLEY',
                ha='center', va='center',
                fontsize=max(5, w*0.065), color='#5D4037', zorder=z+2)
        # Water trough
        tw = max(10, w*0.30); th = max(4, h*0.07)
        ax.add_patch(Rectangle((x+w*0.35, y-th-3), tw, th,
                                 facecolor='#B3E5FC', edgecolor='#0288D1',
                                 lw=1.0, zorder=z+1))

    def _fish_tanks(self, ax, x, y, w, h, unit, z):
        self._shed_base(ax, x, y, w, h, '#B3E5FC', '#0288D1', 'FISH TANKS', unit, z)
        pad = max(3, w*0.04)
        tw = (w - 3*pad) / 2; th = (h - 3*pad) / 2
        if tw < 2 or th < 2:
            return
        for ti, (tx, ty) in enumerate([
            (x+pad, y+pad), (x+pad+tw+pad, y+pad),
            (x+pad, y+pad+th+pad), (x+pad+tw+pad, y+pad+th+pad)
        ]):
            ax.add_patch(Rectangle((tx, ty), tw, th,
                                    facecolor='#4FC3F7', edgecolor='#0288D1',
                                    lw=1.2, zorder=z+1))
            ax.add_patch(Circle((tx+tw/2, ty+th/2), min(tw,th)*0.20,
                                  facecolor='#B3E5FC', edgecolor='none',
                                  alpha=0.55, zorder=z+2))

    def _bee_hives(self, ax, x, y, w, h, unit, z):
        self._shed_base(ax, x, y, w, h, '#FFF176', '#F9A825', 'BEE HIVES', unit, z)
        n = max(1, min(5, int(w / max(10, w*0.22))))
        hw_e = (w - 3) / n - 1.5
        if hw_e < 2:
            return
        for hi in range(n):
            hxe = x + 1.5 + hi * (hw_e + 1.5)
            ax.add_patch(FancyBboxPatch((hxe, y+2), hw_e, h*0.48,
                                         boxstyle='round,pad=0.8',
                                         facecolor=['#FFF176','#FFD54F','#FFCA28'][hi%3],
                                         edgecolor='#F57F17', lw=1.3, zorder=z+1))
        np.random.seed(55)
        for _ in range(max(4, int(w*0.12))):
            bx = x + np.random.uniform(0, w+22)
            by = y + h + np.random.uniform(2, max(12, h*0.28))
            ax.add_patch(Circle((bx, by), max(1.0, unit*0.0035),
                                  facecolor='#FDD835', edgecolor='#F57F17',
                                  lw=0.3, alpha=0.62, zorder=z+2))

    # ─────────────────────────────────────────────────────────────────────────
    #  KITCHEN GARDEN BEDS — scaled, no overlaps
    # ─────────────────────────────────────────────────────────────────────────
    def _kitchen_garden_beds(self, ax, layout, L, W, unit, small):
        zones = layout.get('zone_positions', {})
        if 'z1' not in zones:
            return
        pos = zones['z1']
        x0, y0 = pos['x'], pos['y']
        zw, zh = pos['width'], pos['height']

        pad     = max(5.0, zw * 0.055)
        bed_w   = max(12.0, min(zw * 0.13, 32.0))
        bed_h   = max(20.0, min(zh * 0.42, 72.0))
        gap_x   = max(7.0, min(zw * 0.038, 18.0))
        gap_y   = max(8.0, min(zh * 0.055, 16.0))

        avail_w = zw - 2*pad
        n_beds  = min(6, max(1, int((avail_w + gap_x) / (bed_w + gap_x))))
        total_w = n_beds*bed_w + (n_beds-1)*gap_x
        sx      = x0 + pad + max(0.0, (avail_w - total_w) / 2)

        rows = 1
        if not small and zh > (bed_h*2 + gap_y + 2*pad + 5):
            rows = 2

        for row in range(rows):
            by = y0 + pad + row*(bed_h + gap_y)
            if by + bed_h > y0 + zh - pad:
                break
            for i in range(n_beds):
                bx = sx + i*(bed_w + gap_x)
                if bx + bed_w > x0 + zw - pad:
                    break
                if not self._reg.rect_ok(bx, by, bed_w, bed_h):
                    continue
                self._reg.register_rect(bx, by, bed_w, bed_h)
                _raised_bed(ax, bx, by, bed_w, bed_h, zorder=6)

        # Garden path between rows
        if rows == 2:
            path_y = y0 + pad + bed_h + gap_y*0.08
            path_h = gap_y * 0.84
            ax.add_patch(Rectangle((x0+pad, path_y), total_w, path_h,
                                    facecolor='#D2B48C', edgecolor='#BCAAA4',
                                    lw=0.8, alpha=0.68, zorder=5))

        # Compost bin — placed in empty corner
        comp_sz = max(9.0, min(zw*0.075, 20.0))
        cx_c = x0 + zw - pad - comp_sz
        cy_c = y0 + zh - pad - comp_sz
        if self._reg.rect_ok(cx_c, cy_c, comp_sz, comp_sz):
            self._reg.register_rect(cx_c, cy_c, comp_sz, comp_sz)
            ax.add_patch(FancyBboxPatch((cx_c, cy_c), comp_sz, comp_sz,
                                         boxstyle='round,pad=1.2',
                                         facecolor='#5D4037', edgecolor='#3E2723',
                                         lw=1.3, zorder=6))
            ax.text(cx_c+comp_sz/2, cy_c+comp_sz/2, 'COMPOST',
                    ha='center', va='center',
                    fontsize=max(4, comp_sz*0.20), color='white',
                    fontweight='bold', zorder=7)

    # ─────────────────────────────────────────────────────────────────────────
    #  VEGETATION: Food forest + buffer trees, STRICT non-overlap
    # ─────────────────────────────────────────────────────────────────────────
    def _vegetation(self, ax, layout, L, W, unit, small):
        zones    = layout.get('zone_positions', {})
        features = layout.get('features', {})
        tree_count = int(layout.get('tree_count', 15))

        # Base tree radius for this plot
        base_r = max(3.5, min(unit * 0.028, 14.0))
        r_scale = base_r / 10.0

        pond_x = pond_y = pond_r_block = -9999.0
        if 'pond' in features and features['pond']:
            pf = features['pond']
            pond_x = float(pf.get('x', -9999))
            pond_y = float(pf.get('y', -9999))
            pond_r_block = float(pf.get('radius', 10)) * 1.25

        placements: List[Dict] = []

        # Food Forest zone z2
        if 'z2' in zones:
            z2 = zones['z2']
            np.random.seed(42)
            n_ff = max(tree_count, 8)
            attempts = 0
            placed   = 0
            while placed < n_ff and attempts < n_ff * 30:
                attempts += 1
                sp = SP_LIST[placed % len(SP_LIST)]
                r  = SP_SIZES.get(sp, 0.70) * base_r
                rx = np.random.uniform(0.04, 0.96)
                ry = np.random.uniform(0.04, 0.96)
                tx = z2['x'] + rx * z2['width']
                ty = z2['y'] + ry * z2['height']
                tx = max(z2['x']+r+1, min(tx, z2['x']+z2['width']-r-1))
                ty = max(z2['y']+r+1, min(ty, z2['y']+z2['height']-r-1))
                # Avoid pond
                if np.hypot(tx-pond_x, ty-pond_y) < pond_r_block + r:
                    continue
                if not self._reg.circle_ok(tx, ty, r):
                    continue
                self._reg.register_circle(tx, ty, r)
                placements.append({'x': tx, 'y': ty, 'r': r, 'sp': sp, 'z': 'z2'})
                placed += 1

        # Buffer zone z4
        if 'z4' in zones:
            z4 = zones['z4']
            area4 = z4['width'] * z4['height']
            n_buf = max(4, min(int(area4 / 2800), 30))
            np.random.seed(99)
            for idx in range(n_buf):
                sp = ['Neem', 'Teak', 'Bamboo'][idx % 3]
                r  = SP_SIZES.get(sp, 0.70) * base_r * 0.88
                for _ in range(20):
                    rx = np.random.uniform(0.03, 0.97)
                    ry = np.random.uniform(0.06, 0.94)
                    tx = z4['x'] + rx * z4['width']
                    ty = z4['y'] + ry * z4['height']
                    tx = max(z4['x']+r+1, min(tx, z4['x']+z4['width']-r-1))
                    ty = max(z4['y']+r+1, min(ty, z4['y']+z4['height']-r-1))
                    if self._reg.circle_ok(tx, ty, r):
                        self._reg.register_circle(tx, ty, r)
                        placements.append({'x': tx, 'y': ty, 'r': r, 'sp': sp, 'z': 'z4'})
                        break

        # Draw all
        first_label: set = set()
        for t in placements:
            _draw_tree(ax, t['x'], t['y'], t['r'], t['sp'], zorder=7)
            if t['sp'] not in first_label:
                ax.text(t['x'], t['y'] + t['r'] + max(3, t['r']*0.35), t['sp'],
                        ha='center', fontsize=max(4.5, t['r']*0.42), color='#1B5E20',
                        zorder=8,
                        path_effects=[pe.withStroke(linewidth=1.1, foreground='white')])
                first_label.add(t['sp'])

    # ─────────────────────────────────────────────────────────────────────────
    #  HOUSE PLAN — drawn last (on top)
    # ─────────────────────────────────────────────────────────────────────────
    def _house_plan(self, ax, layout, L, W, unit, hx, hy, hw, hh):
        z    = 10
        wall = min(hw, hh) * 0.07
        fsr  = max(5, min(8,  unit * 0.017))
        fsl  = max(8, min(13, unit * 0.029))

        # Shadow
        ax.add_patch(Rectangle((hx+3, hy-3), hw, hh,
                                 facecolor='#795548', edgecolor='none',
                                 alpha=0.18, zorder=z-1))
        # Roof (shingles)
        ax.add_patch(Rectangle((hx, hy), hw, hh,
                                 facecolor='#ECEFF1', edgecolor='#546E7A',
                                 linewidth=max(1.8, wall*0.38), zorder=z))
        sg = max(4, hh*0.060)
        for ry in np.arange(hy+wall, hy+hh, sg):
            ax.plot([hx+wall, hx+hw-wall], [ry, ry],
                    color='#B0BEC5', lw=0.55, alpha=0.52, zorder=z)
        # Ridge + hip
        ridge_x = hx + hw/2
        ax.plot([ridge_x, ridge_x], [hy+wall, hy+hh-wall],
                color='#607D8B', lw=max(1.4, wall*0.28), linestyle='-.', zorder=z+1)
        for corner in [(hx,hy),(hx+hw,hy),(hx,hy+hh),(hx+hw,hy+hh)]:
            ax.plot([corner[0], ridge_x], [corner[1], hy+hh/2],
                    color='#546E7A', lw=max(0.7, wall*0.18), alpha=0.58, zorder=z+1)
        # Walls
        for wx0,wy0,wx1,wy1 in [
            (hx,    hy,          hx+hw, hy+wall),
            (hx,    hy+hh-wall,  hx+hw, hy+hh),
            (hx,    hy,          hx+wall,      hy+hh),
            (hx+hw-wall, hy,     hx+hw,        hy+hh),
        ]:
            ax.add_patch(Rectangle((wx0,wy0), wx1-wx0, wy1-wy0,
                                    facecolor='#8D6E63', edgecolor='none', zorder=z+1))
        # Interior dividers
        div_y = hy + hh*0.52
        g = (hx+hw*0.43, hx+hw*0.57)
        ax.plot([hx+wall, g[0]], [div_y, div_y], color='#5D4037',
                lw=max(1.3, wall*0.28), zorder=z+2)
        ax.plot([g[1], hx+hw-wall], [div_y, div_y], color='#5D4037',
                lw=max(1.3, wall*0.28), zorder=z+2)
        for vf in [0.36, 0.72]:
            ax.plot([hx+hw*vf, hx+hw*vf], [div_y, hy+hh-wall],
                    color='#5D4037', lw=max(1.1, wall*0.23), zorder=z+2)
        # Room labels
        rl = dict(fontsize=fsr, color='#5D4037', ha='center', va='center',
                  zorder=z+3, fontstyle='italic')
        ax.text(hx+hw*.50, hy+hh*.27, 'LIVING / KITCHEN', **rl)
        ax.text(hx+hw*.18, hy+hh*.75, 'BED 1', **rl)
        ax.text(hx+hw*.54, hy+hh*.75, 'MASTER', **rl)
        ax.text(hx+hw*.86, hy+hh*.75, 'BATH', **rl)
        # Windows
        ww = hw*0.13; wz_h = wall*0.83
        ws = dict(facecolor='#B3E5FC', edgecolor='#1565C0',
                  lw=max(0.9, wall*0.18), zorder=z+2)
        for wx in [hx+hw*0.18, hx+hw*0.62]:
            ax.add_patch(Rectangle((wx, hy), ww, wz_h, **ws))
            ax.add_patch(Rectangle((wx, hy+hh-wz_h), ww, wz_h, **ws))
        ax.add_patch(Rectangle((hx, hy+hh*.54), wz_h, ww, **ws))
        ax.add_patch(Rectangle((hx+hw-wz_h, hy+hh*.54), wz_h, ww, **ws))
        # Front door
        fdw = hw*0.13; fdx = hx+hw/2-fdw/2
        ax.add_patch(Rectangle((fdx, hy), fdw, wall*1.3,
                                 facecolor='#3E2723', edgecolor='black',
                                 lw=max(0.9, wall*0.18), zorder=z+2))
        ax.add_patch(Arc((fdx, hy+wall*.6), fdw*2, fdw*2,
                          angle=0, theta1=0, theta2=90,
                          color='#4E342E', lw=max(0.9, wall*0.18), zorder=z+3))
        # Steps
        for si, ss in enumerate([hh*0.055, hh*0.095, hh*0.135]):
            ax.add_patch(FancyBboxPatch(
                (fdx-ss*.4, hy-ss*.52-si*hh*0.014), fdw+ss*.8, ss*.48,
                boxstyle='round,pad=0.8', facecolor='#EFEBE9', edgecolor='#8D6E63',
                lw=max(0.5, wall*0.11), zorder=z-1))
        # Porch
        pw = hw*.50; pd = hh*.13
        px2 = hx+(hw-pw)/2; py2 = hy-pd
        ax.add_patch(FancyBboxPatch((px2, py2), pw, pd,
                                     boxstyle='round,pad=1.5',
                                     facecolor='#D7CCC8', edgecolor='#8D6E63',
                                     lw=max(1.0, wall*0.22), alpha=0.88, zorder=z-1))
        for dy_d in np.arange(py2+2, py2+pd, max(3.5, pd*0.17)):
            ax.plot([px2+2, px2+pw-2], [dy_d, dy_d],
                    color='#A1887F', lw=0.45, alpha=0.52, zorder=z)
        # Chimney
        cw2 = hw*.07; cd2 = hh*.07
        cx2 = hx+hw*.72; cy2 = hy+hh*.40
        ax.add_patch(Rectangle((cx2, cy2), cw2, cd2,
                                 facecolor='#6D4C41', edgecolor='#3E2723',
                                 lw=max(1.0, wall*0.22), zorder=z+2))
        sc = unit / 300.0
        for sox, soy, sr, sa in [(2,8,3,.26),(4,15,4.5,.16),(7,24,6.5,.09)]:
            ax.add_patch(Circle((cx2+cw2/2+sox*sc, cy2+cd2+soy*sc), sr*sc,
                                  facecolor='#90A4AE', edgecolor='none',
                                  alpha=sa, zorder=z+2))
        # Label
        ax.text(hx+hw/2, hy+hh+max(10, unit*0.033), 'RESIDENCE',
                ha='center', fontsize=fsl, fontweight='bold', color='#BF360C',
                zorder=z+4,
                path_effects=[pe.withStroke(linewidth=2.3, foreground='white')])

    # ─────────────────────────────────────────────────────────────────────────
    #  ZONE LABELS
    # ─────────────────────────────────────────────────────────────────────────
    def _zone_labels(self, ax, layout, L, W, unit, hx, hy, hw, hh):
        for zid, pos in layout.get('zone_positions', {}).items():
            cx = pos['x'] + pos['width'] / 2
            cy = pos['y'] + pos['height'] / 2
            area = int(pos['width'] * pos['height'])
            # Nudge if on house
            if hx <= cx <= hx+hw and hy <= cy <= hy+hh:
                cx = pos['x'] + pos['width'] * 0.82
            ax.text(cx, cy + max(5, unit*0.016),
                    self.ZONE_NAMES.get(zid, zid),
                    ha='center', va='center',
                    fontsize=max(6.5, min(10.5, unit*0.025)),
                    fontweight='bold', color='#1B5E20', zorder=13,
                    bbox=dict(boxstyle='round,pad=0.28', facecolor='white',
                              edgecolor='#A5D6A7', alpha=0.88, lw=0.85))
            ax.text(cx, cy - max(7, unit*0.020), f'{area:,} sq.ft.',
                    ha='center', va='center',
                    fontsize=max(5.5, min(8.5, unit*0.019)),
                    color='#33691E', zorder=13)

    # ─────────────────────────────────────────────────────────────────────────
    #  CARTOGRAPHIC ELEMENTS
    # ─────────────────────────────────────────────────────────────────────────
    def _north_arrow(self, ax, L, W, unit):
        nx, ny = L*.93, W*.07
        r = unit * 0.032
        ax.add_patch(Circle((nx, ny), r, facecolor='white',
                             edgecolor='#1A237E', lw=2.3, zorder=15))
        ax.annotate('', xy=(nx, ny+r*.72), xytext=(nx, ny-r*.36),
                    arrowprops=dict(arrowstyle='->', color='red', lw=2.3), zorder=16)
        ax.text(nx, ny+r+max(2.5, r*0.38), 'N', ha='center',
                fontsize=max(9, r*0.43), fontweight='bold', color='red', zorder=16)

    def _scale_bar(self, ax, L, W, unit):
        sx, sy = L*.04, W*.04
        sc = max(10, min(200, int(L*.16 / 10) * 10))
        half = sc / 2
        ax.add_patch(Rectangle((sx, sy-3), half, 6,
                                 facecolor='black', edgecolor='none', zorder=15))
        ax.add_patch(Rectangle((sx+half, sy-3), half, 6,
                                 facecolor='white', edgecolor='black', lw=0.7, zorder=15))
        ax.plot([sx, sx+sc], [sy+3.5, sy+3.5], 'k-', lw=0.4, zorder=15)
        ax.text(sx+sc/2, sy-max(9, unit*0.028), f'{sc} ft',
                ha='center', fontsize=max(6.5, unit*0.021), fontweight='bold', zorder=15)
        ax.text(sx+sc/2, sy+max(9, unit*0.023), 'SCALE',
                ha='center', fontsize=max(5.5, unit*0.018), zorder=15)

    def _legend(self, ax, L, W, unit):
        lx   = L + unit*0.055
        ly   = W*0.97
        fs   = max(6.5, min(9.5, unit*0.025))
        bsz  = max(11, unit*0.033)
        items = [
            ('#ECEFF1',  'Residence (Roof Plan)'),
            ('#FFCCBC',  'Livestock Shed'),
            ('#29B6F6',  'Water / Pond'),
            ('#1565C0',  'Solar Array'),
            ('#E0F2F1',  'Greenhouse'),
            ('#2E7D32',  'Food Forest Trees'),
            ('#3E2723',  'Raised Garden Beds'),
            ('#D2B48C',  'Roads / Paths'),
            (self.ZONE_COLORS['z0'], 'Zone 0 – Residential'),
            (self.ZONE_COLORS['z1'], 'Zone 1 – Kitchen Garden'),
            (self.ZONE_COLORS['z2'], 'Zone 2 – Food Forest'),
            (self.ZONE_COLORS['z3'], 'Zone 3 – Pasture / Crops'),
            (self.ZONE_COLORS['z4'], 'Zone 4 – Buffer Zone'),
        ]
        bh      = fs * 2.35
        total_h = len(items) * bh + 34
        box_w   = max(135, unit * 0.40)
        ax.add_patch(FancyBboxPatch((lx-8, ly-total_h), box_w, total_h+7,
                                     boxstyle='round,pad=4', facecolor='white',
                                     edgecolor='#546E7A', lw=1.8, alpha=0.97, zorder=14))
        ax.text(lx+box_w/2-8, ly+1, 'LEGEND',
                ha='center', fontsize=fs+1.8, fontweight='bold',
                color='#1A237E', zorder=15)
        for i, (c, label) in enumerate(items):
            yp = ly - (i+1)*bh + 5
            ax.add_patch(Rectangle((lx, yp), bsz, max(9, fs*1.25),
                                    facecolor=c, edgecolor='#546E7A', lw=0.7, zorder=15))
            ax.text(lx+bsz+4, yp+max(4.5, fs*0.62), label,
                    fontsize=fs, va='center', zorder=15)

    def _dimensions(self, ax, L, W, unit):
        off = unit * 0.052
        ax.annotate('', xy=(0,-off), xytext=(L,-off),
                    arrowprops=dict(arrowstyle='<->', color='#1A237E', lw=1.7), zorder=13)
        ax.text(L/2, -off-max(11, unit*0.030), f'{int(L)} ft',
                ha='center', fontsize=max(8.5, unit*0.026),
                fontweight='bold', color='#1A237E')
        ax.annotate('', xy=(-off,0), xytext=(-off,W),
                    arrowprops=dict(arrowstyle='<->', color='#1A237E', lw=1.7), zorder=13)
        ax.text(-off-max(13, unit*0.036), W/2, f'{int(W)} ft',
                ha='center', fontsize=max(8.5, unit*0.026),
                fontweight='bold', color='#1A237E', rotation=90)

    def _title(self, ax, layout, L, W, unit):
        acres   = layout.get('acres', layout.get('total_sqft', 0) / 43560)
        total   = layout.get('total_sqft', 0)
        cat     = layout.get('category', '').upper()
        loc     = layout.get('location', '')
        loc_str = f' · {loc}' if loc else ''
        title   = f"{acres:.2f} ACRE HOMESTEAD{loc_str}\n{int(total):,} SQ.FT.  ·  {cat} SCALE"
        ax.text(L/2, W + unit*0.072, title,
                ha='center', va='bottom',
                fontsize=max(10, min(15, unit*0.038)),
                fontweight='bold', color='#1B5E20',
                bbox=dict(boxstyle='round,pad=0.55', facecolor='#E8F5E9',
                          edgecolor='#2E7D32', lw=2.3), zorder=16)
