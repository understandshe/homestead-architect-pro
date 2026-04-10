"""
Professional 2D Site-Plan Visualizer — v6
Homestead Architect Pro 2026
Rules: zero overlaps, smart roads, dynamic animals, all sizes
"""

import matplotlib
matplotlib.use('Agg')
from core.shared_geometry import HomesteadGeometry
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon, Arc
import matplotlib.patheffects as pe
import numpy as np
from io import BytesIO
from typing import List, Tuple, Optional, Dict

# ─────────────────────────────────────────────────
#  TREE PALETTE
# ─────────────────────────────────────────────────
TREE_COLORS = {
    'Mango':   ('#2E7D32','#388E3C'), 'Jackfruit':('#1B5E20','#2E7D32'),
    'Coconut': ('#33691E','#558B2F'), 'Banana':   ('#558B2F','#7CB342'),
    'Guava':   ('#33691E','#43A047'), 'Papaya':   ('#558B2F','#8BC34A'),
    'Avocado': ('#2E7D32','#1B5E20'), 'Moringa':  ('#66BB6A','#4CAF50'),
    'Citrus':  ('#43A047','#66BB6A'), 'Neem':     ('#388E3C','#2E7D32'),
    'Teak':    ('#1B5E20','#2E7D32'), 'Bamboo':   ('#4CAF50','#8BC34A'),
    'default': ('#2E7D32','#388E3C'),
}
SP_SIZES = {
    'Mango':0.90,'Jackfruit':1.0,'Coconut':0.65,'Banana':0.55,
    'Guava':0.70,'Papaya':0.50,'Avocado':0.80,'Moringa':0.55,
    'Citrus':0.65,'Neem':0.90,'Teak':0.85,'Bamboo':0.40,'default':0.70,
}
SP_LIST = ['Mango','Jackfruit','Coconut','Banana','Guava',
           'Papaya','Avocado','Moringa','Citrus','Neem','Teak','Bamboo']


# ─────────────────────────────────────────────────
#  REGISTRY — strict collision detection
# ─────────────────────────────────────────────────
class _Reg2D:
    GAP = 2.5

    def __init__(self, L: float, W: float):
        self.L = L
        self.W = W
        self.rects:   List[Tuple] = []
        self.circles: List[Tuple] = []

    def _in_bounds_rect(self, x, y, w, h) -> bool:
        return x >= 0 and y >= 0 and x + w <= self.L and y + h <= self.W

    def _in_bounds_circle(self, cx, cy, r) -> bool:
        return cx - r >= 0 and cy - r >= 0 and cx + r <= self.L and cy + r <= self.W

    def rect_ok(self, x, y, w, h, gap=None) -> bool:
        g = gap if gap is not None else self.GAP
        x, y, w, h = float(x), float(y), float(w), float(h)
        if not self._in_bounds_rect(x, y, w, h):
            return False
        for (rx, ry, rw, rh) in self.rects:
            if x - g < rx + rw and x + w + g > rx and y - g < ry + rh and y + h + g > ry:
                return False
        for (cx, cy, cr) in self.circles:
            nx = max(x, min(cx, x + w))
            ny = max(y, min(cy, y + h))
            if (cx - nx)**2 + (cy - ny)**2 < (cr + g)**2:
                return False
        return True

    def circle_ok(self, cx, cy, r, gap=None) -> bool:
        g = gap if gap is not None else self.GAP
        cx, cy, r = float(cx), float(cy), float(r)
        if not self._in_bounds_circle(cx, cy, r):
            return False
        for (rx, ry, rw, rh) in self.rects:
            nx = max(rx, min(cx, rx + rw))
            ny = max(ry, min(cy, ry + rh))
            if (cx - nx)**2 + (cy - ny)**2 < (r + g)**2:
                return False
        for (ocx, ocy, or_) in self.circles:
            if (cx - ocx)**2 + (cy - ocy)**2 < (r + or_ + g)**2:
                return False
        return True

    def reg_rect(self, x, y, w, h):
        self.rects.append((float(x), float(y), float(w), float(h)))

    def reg_circle(self, cx, cy, r):
        self.circles.append((float(cx), float(cy), float(r)))

    def force_reg_circle(self, cx, cy, r):
        """Only for pond — forced registration without check."""
        self.circles.append((float(cx), float(cy), float(r)))


# ─────────────────────────────────────────────────
#  DRAWING HELPERS
# ─────────────────────────────────────────────────
def _draw_tree(ax, tx, ty, r, species='default', zorder=7):
    c1, c2 = TREE_COLORS.get(species, TREE_COLORS['default'])
    ax.add_patch(Circle((tx + r*0.20, ty - r*0.20), r,
                         facecolor='#1A3A1A', edgecolor='none', alpha=0.13, zorder=zorder-1))
    np.random.seed(abs(hash(species + str(int(tx*7)))) % 9999)
    n = 14
    angles = np.linspace(0, 2*np.pi, n, endpoint=False)
    radii  = r * (0.78 + 0.22 * np.random.rand(n))
    ax.add_patch(Polygon(list(zip(tx + radii*np.cos(angles),
                                   ty + radii*np.sin(angles))),
                          facecolor=c1, edgecolor=c2, linewidth=0.7,
                          alpha=0.93, zorder=zorder))
    ax.add_patch(Circle((tx - r*0.18, ty + r*0.18), r*0.26,
                         facecolor='white', edgecolor='none', alpha=0.11, zorder=zorder+1))


def _raised_bed(ax, x, y, w, h, zorder=6):
    ft = min(w, h) * 0.13
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0',
                                 facecolor='#8D6E63', edgecolor='#5D4037',
                                 linewidth=max(1.2, min(w,h)*0.05), zorder=zorder))
    ax.add_patch(Rectangle((x+ft, y+ft), w-2*ft, h-2*ft,
                             facecolor='#3E2723', edgecolor='none', zorder=zorder+1))
    iw = w - 2*ft - 2; ih = h - 2*ft - 2
    if iw < 3 or ih < 3:
        return
    nc = max(1, int(iw / max(6, w*0.14)))
    nr = max(1, int(ih / max(6, h*0.14)))
    pr = min(iw/nc, ih/nr) * 0.25
    pc = ['#4CAF50','#66BB6A','#81C784','#A5D6A7','#2E7D32']
    for ri in range(nr):
        for ci in range(nc):
            ax.add_patch(Circle((x+ft+1+(ci+0.5)*iw/nc, y+ft+1+(ri+0.5)*ih/nr),
                                  pr, facecolor=pc[(ri+ci)%len(pc)],
                                  edgecolor='#1B5E20', linewidth=0.2, zorder=zorder+2))


def _road(ax, pts, width, color='#D2B48C', alpha=0.88, zorder=4):
    """PREMIUM Catmull-Rom road with shadow + dashed center line."""
    if len(pts) < 2:
        return
    arr = np.array(pts, dtype=float)
    n = len(arr)
    xs, ys = [], []
    for i in range(n - 1):
        p0 = arr[max(0, i-1)]; p1 = arr[i]
        p2 = arr[i+1]; p3 = arr[min(n-1, i+2)]
        t1 = (p2 - p0) * 0.5; t2 = (p3 - p1) * 0.5
        steps = max(16, int(np.hypot(*(p2-p1)) / 4) + 1)
        for s in np.linspace(0, 1, steps):
            h00 = 2*s**3 - 3*s**2 + 1
            h10 = s**3 - 2*s**2 + s
            h01 = -2*s**3 + 3*s**2
            h11 = s**3 - s**2
            pt = h00*p1 + h10*t1 + h01*p2 + h11*t2
            xs.append(pt[0]); ys.append(pt[1])

    xs = np.array(xs); ys = np.array(ys)
    dx = np.gradient(xs); dy = np.gradient(ys)
    ln = np.hypot(dx, dy) + 1e-9
    nx_, ny_ = -dy/ln, dx/ln
    hw = width / 2

    # Shadow
    xu_s = xs + nx_*(hw+1.5); yu_s = ys + ny_*(hw+1.5)
    xd_s = xs - nx_*(hw+1.5); yd_s = ys - ny_*(hw+1.5)
    ax.fill(np.concatenate([xu_s, xd_s[::-1]]),
            np.concatenate([yu_s, yd_s[::-1]]),
            color='#5D4037', alpha=0.12, zorder=zorder-1)

    # Road body
    xu = xs + nx_*hw; yu = ys + ny_*hw
    xd = xs - nx_*hw; yd = ys - ny_*hw
    ax.fill(np.concatenate([xu, xd[::-1]]),
            np.concatenate([yu, yd[::-1]]),
            color=color, alpha=alpha, zorder=zorder)

    # Edge lines
    ax.plot(xu, yu, color='#8D6E63', lw=0.8, alpha=0.65, zorder=zorder+1)
    ax.plot(xd, yd, color='#8D6E63', lw=0.8, alpha=0.65, zorder=zorder+1)

    # Center dashed line (PREMIUM)
    ax.plot(xs, ys, color='white', lw=max(0.8, width*0.06),
            alpha=0.45, zorder=zorder+2, linestyle=(0, (8, 6)))


# ─────────────────────────────────────────────────
#  MAIN CLASS
# ─────────────────────────────────────────────────
class Visualizer2D:

    ZONE_COLORS = {
        'z0':'#F0EAD6','z1':'#C5E1A5','z2':'#388E3C',
        'z3':'#FFF9C4','z4':'#A5D6A7',
    }
    ZONE_NAMES = {
        'z0':'ZONE 0\nRESIDENTIAL','z1':'ZONE 1\nKITCHEN GARDEN',
        'z2':'ZONE 2\nFOOD FOREST', 'z3':'ZONE 3\nPASTURE / CROPS',
        'z4':'ZONE 4\nBUFFER',
    }

    def __init__(self):
        self._reg: Optional[_Reg2D] = None
        self._geo: Optional[HomesteadGeometry] = None
        self._L = 300.0
        self._W = 300.0

    # ─────────────────────────────────────────────
    #  PUBLIC API
    # ─────────────────────────────────────────────
    def create(self, layout: dict, answers: dict) -> BytesIO:
        # ── USE SHARED GEOMETRY ──
        self._geo = HomesteadGeometry(layout)
        L, W = self._geo.L, self._geo.W
        unit = self._geo.unit
        small = unit < 150
        self._L = L; self._W = W

        self._reg = _Reg2D(L, W)

        fig, ax = plt.subplots(figsize=(18, max(10, 18*(W/L)*0.72)), dpi=150)
        fig.patch.set_facecolor('#F9F6F0')
        ax.set_facecolor('#5A8F3C')

        # ── Layer order ───────────────────────────
        self._grass(ax, L, W, unit)
        self._draw_zones(ax, layout)
        self._contours(ax, layout, L, W)
        self._fence_and_gate(ax, L, W, unit)

        # House bbox — FROM SHARED GEOMETRY (same as 3D!)
        hx, hy, hw, hh = self._geo.house_bbox()
        self._reg.reg_rect(hx, hy, hw, hh)

        # Water BEFORE roads/sheds (so roads avoid pond)
        self._water(ax, layout, L, W, unit)

        # Roads — FROM SHARED GEOMETRY ENGINE
        self._roads_from_geometry(ax, small)

        # Utilities
        self._utilities(ax, layout, L, W, unit, small)

        # Livestock — dynamic per user selection
        self._livestock(ax, layout, L, W, unit, small)

        # Kitchen garden
        self._kitchen_garden(ax, layout, L, W, unit, small)

        # Food forest trees
        self._trees(ax, layout, L, W, unit, small)

        # House on top
        self._house(ax, layout, L, W, unit, hx, hy, hw, hh)

        # Labels + cartographic
        self._zone_labels(ax, layout, L, W, unit, hx, hy, hw, hh)
        self._north_arrow(ax, L, W, unit)
        self._scale_bar(ax, L, W, unit)
        self._legend(ax, L, W, unit)
        self._dims(ax, L, W, unit)
        self._title(ax, layout, L, W, unit)

        margin = max(L, W) * 0.18
        ax.set_xlim(-margin, L + margin*1.9)
        ax.set_ylim(-margin*1.1, W + margin)
        ax.set_aspect('equal'); ax.axis('off')
        plt.tight_layout(pad=0.3)

        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=180, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        buf.seek(0); plt.close(fig)
        return buf

    # ─────────────────────────────────────────────
    #  GRASS
    # ─────────────────────────────────────────────
    def _grass(self, ax, L, W, unit):
        ax.add_patch(Rectangle((0,0), L, W, facecolor='#5A8F3C', edgecolor='none', zorder=0))
        np.random.seed(1)
        n = max(150, min(500, int(L*W/250)))
        gl = max(4, unit*0.018)
        for _ in range(n):
            gx = np.random.uniform(1, L-1); gy = np.random.uniform(1, W-1)
            gc = ['#4CAF50','#66BB6A','#388E3C','#2E7D32'][_ % 4]
            ax.plot([gx, gx+np.random.uniform(-0.8,0.8)],
                    [gy, gy+np.random.uniform(2, gl)],
                    color=gc, lw=0.22, alpha=0.09, zorder=0)

    # ─────────────────────────────────────────────
    #  ZONES
    # ─────────────────────────────────────────────
    def _draw_zones(self, ax, layout):
        for zid, pos in layout.get('zone_positions', {}).items():
            ax.add_patch(Rectangle((pos['x'], pos['y']), pos['width'], pos['height'],
                                    facecolor=self.ZONE_COLORS.get(zid,'#CCC'),
                                    edgecolor='#546E7A', linewidth=1.1,
                                    alpha=0.38, zorder=2))

    # ─────────────────────────────────────────────
    #  CONTOURS
    # ─────────────────────────────────────────────
    def _contours(self, ax, layout, L, W):
        slope = layout.get('slope','Flat')
        if slope == 'Flat': return
        for idx in range(1, 6):
            f = idx / 6
            if slope in ('South','North'):
                y = W*f if slope=='South' else W*(1-f)
                ax.plot([0,L],[y,y], color='#A5D6A7', linestyle='--', lw=0.5, alpha=0.4, zorder=1)
            elif slope in ('East','West'):
                x = L*f if slope=='East' else L*(1-f)
                ax.plot([x,x],[0,W], color='#A5D6A7', linestyle='--', lw=0.5, alpha=0.4, zorder=1)
            else:
                ax.plot([0,L],[W*f, W*(1-f)], color='#A5D6A7', linestyle='--', lw=0.4, alpha=0.3, zorder=1)

    # ─────────────────────────────────────────────
    #  FENCE + GATE
    # ─────────────────────────────────────────────
    def _fence_and_gate(self, ax, L, W, unit):
        pg = max(unit*0.038, 8.0)
        pw = max(pg*0.09, 1.8)
        ph = pw * 2.0
        z = 3

        def seg(x0, y0, x1, y1):
            dx=x1-x0; dy=y1-y0; ln=np.hypot(dx,dy)
            if ln < 1: return
            ux=dx/ln; uy=dy/ln; nx=-uy; ny=ux
            for rt in [0.28, 0.68]:
                off = ph*(rt-0.5)*0.72
                ax.plot([x0+nx*off, x1+nx*off],[y0+ny*off, y1+ny*off],
                        color='#A1887F', lw=max(1.4,pw*0.65),
                        solid_capstyle='round', zorder=z)
            np_ = max(2, int(ln/pg))
            for i in range(np_+1):
                t=i/np_
                ax.add_patch(FancyBboxPatch((x0+t*dx-pw/2, y0+t*dy-ph/2), pw, ph,
                                             boxstyle='round,pad=0.2',
                                             facecolor='#5D4037', edgecolor='#3E2723',
                                             linewidth=0.5, zorder=z+1))

        gcx = L/2
        ghw = max(unit*0.038, 14.0)
        seg(0, 0, gcx-ghw, 0)
        seg(gcx+ghw, 0, L, 0)
        seg(0, W, L, W)
        seg(0, 0, 0, W)
        seg(L, 0, L, W)

        gpw=pw*1.5; gph=ph*1.35
        for gx in [gcx-ghw-gpw, gcx+ghw]:
            ax.add_patch(FancyBboxPatch((gx,-gph/2), gpw, gph,
                                         boxstyle='round,pad=0.2',
                                         facecolor='#4E342E', edgecolor='#1A237E',
                                         linewidth=1.5, zorder=z+3))
        ax.text(gcx, -gph-max(4,unit*0.015), 'MAIN GATE',
                ha='center', va='top', fontsize=max(7,unit*0.020),
                fontweight='bold', color='#1A237E', zorder=z+4,
                bbox=dict(boxstyle='round,pad=0.22', facecolor='white',
                          edgecolor='#1A237E', alpha=0.85, lw=0.8))
        self._gcx = gcx; self._ghw = ghw

    # ─────────────────────────────────────────────
    #  ROADS — from shared geometry engine
    # ─────────────────────────────────────────────
    def _roads_from_geometry(self, ax, small):
        """Draw ALL roads from shared geometry engine."""
        roads = self._geo.road_network()
        for road in roads:
            _road(ax, road['points'], road['width'],
                  road['color'], road['alpha'], road['zorder'])

        # Register main road corridor for collision avoidance
        if roads:
            r0 = roads[0]
            pts = r0['points']
            rw = r0['width']
            min_x = min(p[0] for p in pts) - rw * 1.5
            min_y = min(p[1] for p in pts)
            max_x = max(p[0] for p in pts) + rw * 1.5
            self._reg.reg_rect(min_x, 0, max_x - min_x, min_y)

    # ─────────────────────────────────────────────
    #  WATER FEATURES
    # ─────────────────────────────────────────────
    def _water(self, ax, layout, L, W, unit):
        feats = layout.get('features', {})
        z = 7

        # Well / Borewell
        for key in ('borewell','well'):
            if key not in feats or not feats[key]: continue
            f = feats[key]
            r = max(unit*0.013, min(float(f.get('radius', unit*0.020)), unit*0.036))
            wx = max(r+2, min(float(f['x']), L-r-2))
            wy = max(r+2, min(float(f['y']), W-r-2))
            if not self._reg.circle_ok(wx, wy, r, gap=1):
                # Try nearby spot
                for dx, dy in [(r*2,0),(-r*2,0),(0,r*2),(0,-r*2)]:
                    nx2, ny2 = wx+dx, wy+dy
                    if self._reg.circle_ok(nx2, ny2, r, gap=1):
                        wx, wy = nx2, ny2; break
            self._reg.reg_circle(wx, wy, r)
            ax.add_patch(Circle((wx,wy), r, facecolor='#4FC3F7',
                                  edgecolor='#0288D1', lw=max(1.8,r*0.12), zorder=z))
            ax.add_patch(Circle((wx,wy), r*0.68, facecolor='#81D4FA',
                                  edgecolor='none', zorder=z))
            ax.text(wx, wy, 'W', ha='center', va='center',
                    fontsize=max(6,r*0.28), fontweight='bold', color='white', zorder=z+1)
            ax.text(wx, wy-r-max(5,r*0.32), 'WELL/BOREWELL',
                    ha='center', fontsize=max(4.5,r*0.20), color='#0288D1', zorder=z+1)
            break

        # Pond — ONLY forced registration (per rules)
        if 'pond' in feats and feats['pond']:
            f = feats['pond']
            r = max(unit*0.042, min(float(f.get('radius', unit*0.07)), unit*0.13))
            px = max(r+2, min(float(f['x']), L-r-2))
            py = max(r+2, min(float(f['y']), W-r-2))
            self._reg.force_reg_circle(px, py, r*1.12)

            theta = np.linspace(0, 2*np.pi, 60)
            rip = 1 + 0.09*np.sin(3*theta) + 0.05*np.cos(5*theta)
            ax.add_patch(Circle((px+r*0.06,py-r*0.06), r*1.06,
                                  facecolor='#1A237E', alpha=0.09, edgecolor='none', zorder=z-1))
            ax.add_patch(Polygon(list(zip(px+r*rip*np.cos(theta), py+r*rip*np.sin(theta))),
                                  facecolor='#29B6F6', edgecolor='#0288D1',
                                  lw=max(1.8,r*0.055), alpha=0.91, zorder=z))
            ax.add_patch(Polygon(list(zip(px+r*0.44*np.cos(theta), py+r*0.44*np.sin(theta))),
                                  facecolor='#81D4FA', edgecolor='none', alpha=0.48, zorder=z))
            for rf in [0.28, 0.66]:
                ax.add_patch(Circle((px,py), r*rf, facecolor='none', edgecolor='#4FC3F7',
                                     lw=max(0.4,r*0.016), alpha=0.38, zorder=z+1))
            np.random.seed(77)
            for _ in range(max(3, int(r*0.33))):
                ang=np.random.uniform(0,2*np.pi); d=np.random.uniform(0,r*0.40)
                ax.add_patch(Circle((px+d*np.cos(ang),py+d*np.sin(ang)),
                                     max(1.5,r*0.052), facecolor='#4CAF50',
                                     edgecolor='none', alpha=0.68, zorder=z+1))
            ax.text(px, py, 'POND', ha='center', va='center',
                    fontsize=max(7,r*0.18), color='#01579B', fontweight='bold', zorder=z+2,
                    path_effects=[pe.withStroke(linewidth=1.3, foreground='white')])

        # Rain tank
        if 'rain_tank' in feats and feats['rain_tank']:
            f = feats['rain_tank']
            rx,ry,rw,rh = float(f['x']),float(f['y']),float(f['width']),float(f['height'])
            if self._reg.rect_ok(rx,ry,rw,rh):
                self._reg.reg_rect(rx,ry,rw,rh)
                ax.add_patch(FancyBboxPatch((rx,ry), rw, rh, boxstyle='round,pad=2',
                                             facecolor='#B3E5FC', edgecolor='#0288D1',
                                             lw=1.8, zorder=z))
                for by in np.linspace(ry+rh*0.2, ry+rh*0.8, 3):
                    ax.plot([rx+3,rx+rw-3],[by,by], color='#0288D1', lw=0.7, zorder=z+1)
                ax.text(rx+rw/2, ry+rh/2, 'RAIN\nTANK', ha='center', va='center',
                        fontsize=max(5,rw*0.09), color='#01579B',
                        fontweight='bold', zorder=z+1)

    # ─────────────────────────────────────────────
    #  UTILITIES
    # ─────────────────────────────────────────────
    def _utilities(self, ax, layout, L, W, unit, small):
        feats = layout.get('features', {}); z = 6
        if 'solar' in feats and feats['solar']:
            f = feats['solar']
            sx,sy,sw,sh = float(f['x']),float(f['y']),float(f['width']),float(f['height'])
            if self._reg.rect_ok(sx,sy,sw,sh):
                self._reg.reg_rect(sx,sy,sw,sh)
                ax.add_patch(Rectangle((sx,sy),sw,sh, facecolor='#90A4AE',
                                        edgecolor='#37474F', lw=1.3, zorder=z))
                if sw>4 and sh>4:
                    r2,c2,g2=2,3,1.0
                    cw2=max(1,(sw-g2*(c2+1))/c2); ch2=max(1,(sh-g2*(r2+1))/r2)
                    for row in range(r2):
                        for col in range(c2):
                            ax.add_patch(Rectangle(
                                (sx+g2+col*(cw2+g2), sy+g2+row*(ch2+g2)), cw2, ch2,
                                facecolor='#1565C0', edgecolor='#0D47A1', lw=0.7, zorder=z+1))
                ax.text(sx+sw/2, sy+sh+max(6,unit*0.013), 'SOLAR ARRAY',
                        ha='center', fontsize=max(5,sw*0.06), fontweight='bold',
                        color='#0D47A1', zorder=z+2)

        if 'greenhouse' in feats and feats['greenhouse']:
            f = feats['greenhouse']
            gx,gy,gw,gh = float(f['x']),float(f['y']),float(f['width']),float(f['height'])
            if self._reg.rect_ok(gx,gy,gw,gh):
                self._reg.reg_rect(gx,gy,gw,gh)
                ax.add_patch(Rectangle((gx,gy),gw,gh, facecolor='#E0F2F1',
                                        edgecolor='#00695C', lw=1.8, linestyle='--',
                                        alpha=0.80, zorder=z))
                ax.add_patch(Arc((gx+gw/2,gy+gh), gw, gh*0.28,
                                  angle=0, theta1=0, theta2=180,
                                  color='#00695C', lw=1.8, zorder=z+1))
                ax.text(gx+gw/2, gy-max(8,unit*0.017), 'GREENHOUSE',
                        ha='center', fontsize=max(5,gw*0.06), color='#004D40', zorder=z+2)

    # ─────────────────────────────────────────────
    #  LIVESTOCK — dynamic, only selected animals
    # ─────────────────────────────────────────────
    def _livestock(self, ax, layout, L, W, unit, small):
        feats = layout.get('features', {})
        z = 6
        draw_map = {
            'goat_shed':    self._goat_shed,
            'chicken_coop': self._chicken_coop,
            'piggery':      self._piggery,
            'cow_shed':     self._cow_shed,
            'fish_tanks':   self._fish_tanks,
            'bee_hives':    self._bee_hives,
        }
        for key, fn in draw_map.items():
            if key not in feats or not feats[key]: continue
            f = feats[key]
            if not isinstance(f, dict): continue
            sx = max(1.0, min(float(f.get('x',0)), L-float(f.get('width',30))-1))
            sy = max(1.0, min(float(f.get('y',0)), W-float(f.get('height',25))-1))
            sw = float(f.get('width',30)); sh = float(f.get('height',25))
            # Only check for overlap — if layout engine placed it, register and draw
            if not self._reg.rect_ok(sx, sy, sw, sh, gap=1):
                # Try minimal shift
                found = False
                for dx, dy in [(0,sh+4),(0,-(sh+4)),(sw+4,0),(-(sw+4),0)]:
                    nx2 = max(1, min(sx+dx, L-sw-1))
                    ny2 = max(1, min(sy+dy, W-sh-1))
                    if self._reg.rect_ok(nx2, ny2, sw, sh, gap=1):
                        sx, sy = nx2, ny2; found = True; break
                if not found:
                    continue  # Skip if no room
            self._reg.reg_rect(sx, sy, sw, sh)
            fn(ax, sx, sy, sw, sh, unit, z)

    def _shed_base(self, ax, x, y, w, h, fc, ec, label, unit, z):
        lw = max(1.3, min(w,h)*0.038)
        ax.add_patch(Rectangle((x+2,y-2), w, h, facecolor='#5D4037',
                                edgecolor='none', alpha=0.16, zorder=z-1))
        ax.add_patch(Rectangle((x,y), w, h, facecolor=fc, edgecolor=ec,
                                lw=lw, zorder=z))
        rh_ = min(h*0.20, max(9,unit*0.026))
        ax.add_patch(Polygon([[x-2,y+h],[x+w/2,y+h+rh_],[x+w+2,y+h]],
                               facecolor='#A1887F', edgecolor=ec, lw=lw*0.55, zorder=z+1))
        ax.text(x+w/2, y+h+rh_+max(5,unit*0.011), label,
                ha='center', fontsize=max(6,unit*0.018), fontweight='bold',
                color=ec, zorder=z+2,
                path_effects=[pe.withStroke(linewidth=1.3, foreground='white')])

    def _goat_shed(self, ax, x, y, w, h, unit, z):
        self._shed_base(ax, x, y, w, h, '#FFCCBC','#5D4037','GOAT SHED', unit, z)
        for vx in [x+w*0.2, x+w*0.5, x+w*0.8]:
            ww=max(5,w*0.09); wh=max(4,h*0.10)
            ax.add_patch(Rectangle((vx-ww/2,y+h-wh-2), ww, wh,
                                    facecolor='#B3E5FC', edgecolor='#555', lw=0.6, zorder=z+1))
        dw=max(9,w*0.15)
        ax.add_patch(Rectangle((x+w/2-dw/2,y), dw, h*0.35,
                                 facecolor='#3E2723', edgecolor='#111', lw=0.6, zorder=z+1))
        fe=max(16,h*0.48)
        for fy in [y-fe, y-fe*0.5, y]:
            ax.plot([x-2,x+w+2],[fy,fy], color='#8D6E63', lw=1.2, zorder=z-1)
        for fx in np.linspace(x-2, x+w+2, max(4,int(w/13))):
            ax.plot([fx,fx],[y-fe,y], color='#8D6E63', lw=0.9, zorder=z-1)

    def _chicken_coop(self, ax, x, y, w, h, unit, z):
        self._shed_base(ax, x, y, w, h, '#FFF8E1','#F57F17','CHICKEN COOP', unit, z)
        re=max(16,h*0.44)
        ax.add_patch(Rectangle((x-re,y), re, h, facecolor='#F1F8E9',
                                 edgecolor='#33691E', linestyle='--', alpha=0.38, lw=1.0, zorder=z-1))
        ax.text(x-re/2, y+h/2, 'RUN', ha='center', va='center',
                fontsize=max(5,re*0.10), color='#33691E', zorder=z)
        cdw=max(6,w*0.13)
        ax.add_patch(Polygon([[x+w*0.35,y],[x+w*0.50,y-cdw*0.7],[x+w*0.65,y]],
                               facecolor='#D7CCC8', edgecolor='#5D4037', zorder=z+1))

    def _piggery(self, ax, x, y, w, h, unit, z):
        self._shed_base(ax, x, y, w, h, '#FFCCBC','#BF360C','PIGGERY', unit, z)
        sw_=w/3
        for i, s in enumerate(['FAR','NUR','GRW']):
            sx_=x+i*sw_
            if i>0: ax.plot([sx_,sx_],[y,y+h], color='#BF360C', lw=1.3, zorder=z+1)
            ax.text(sx_+sw_/2, y+h/2, s, ha='center', va='center',
                    fontsize=max(5,sw_*0.12), fontweight='bold', color='#BF360C', zorder=z+2)
        ax.add_patch(Circle((x+w/2, y+h*0.24), max(4,w*0.07),
                              facecolor='#8D6E63', edgecolor='none', alpha=0.52, zorder=z+1))

    def _cow_shed(self, ax, x, y, w, h, unit, z):
        self._shed_base(ax, x, y, w, h, '#D7CCC8','#5D4037','COW SHED', unit, z)
        n_=max(2,int(w/38)); sw_=w/n_
        for i in range(1,n_):
            ax.plot([x+i*sw_,x+i*sw_],[y+h*0.27,y+h], color='#795548', lw=1.5, zorder=z+1)
        ax.add_patch(Rectangle((x,y),w,h*0.27, facecolor='#EFEBE9',
                                 edgecolor='#5D4037', lw=1.0, zorder=z+1))
        ax.text(x+w/2, y+h*0.135, 'FEED ALLEY', ha='center', va='center',
                fontsize=max(5,w*0.063), color='#5D4037', zorder=z+2)
        tw_=max(9,w*0.28); th_=max(3.5,h*0.065)
        ax.add_patch(Rectangle((x+w*0.36,y-th_-3), tw_, th_,
                                 facecolor='#B3E5FC', edgecolor='#0288D1', lw=0.9, zorder=z+1))

    def _fish_tanks(self, ax, x, y, w, h, unit, z):
        self._shed_base(ax, x, y, w, h, '#B3E5FC','#0288D1','FISH TANKS', unit, z)
        pad_=max(3,w*0.04); tw_=(w-3*pad_)/2; th_=(h-3*pad_)/2
        if tw_<2 or th_<2: return
        for tx_,ty_ in [(x+pad_,y+pad_),(x+pad_+tw_+pad_,y+pad_),
                         (x+pad_,y+pad_+th_+pad_),(x+pad_+tw_+pad_,y+pad_+th_+pad_)]:
            ax.add_patch(Rectangle((tx_,ty_),tw_,th_,
                                    facecolor='#4FC3F7', edgecolor='#0288D1', lw=1.1, zorder=z+1))
            ax.add_patch(Circle((tx_+tw_/2,ty_+th_/2), min(tw_,th_)*0.19,
                                  facecolor='#B3E5FC', edgecolor='none', alpha=0.52, zorder=z+2))

    def _bee_hives(self, ax, x, y, w, h, unit, z):
        self._shed_base(ax, x, y, w, h, '#FFF176','#F9A825','BEE HIVES', unit, z)
        n_=max(1,min(5,int(w/max(10,w*0.22))))
        hwe=(w-3)/n_-1.5
        if hwe<2: return
        for hi in range(n_):
            hxe=x+1.5+hi*(hwe+1.5)
            ax.add_patch(FancyBboxPatch((hxe,y+2), hwe, h*0.46,
                                         boxstyle='round,pad=0.7',
                                         facecolor=['#FFF176','#FFD54F','#FFCA28'][hi%3],
                                         edgecolor='#F57F17', lw=1.2, zorder=z+1))
        np.random.seed(55)
        for _ in range(max(4,int(w*0.11))):
            bx_=x+np.random.uniform(0,w+20); by_=y+h+np.random.uniform(2,max(11,h*0.26))
            ax.add_patch(Circle((bx_,by_), max(1.0,unit*0.0033),
                                  facecolor='#FDD835', edgecolor='#F57F17',
                                  lw=0.3, alpha=0.60, zorder=z+2))

    # ─────────────────────────────────────────────
    #  KITCHEN GARDEN — beds, path between rows,
    #  roads stay OUTSIDE this zone
    # ─────────────────────────────────────────────
    def _kitchen_garden(self, ax, layout, L, W, unit, small):
        zp = layout.get('zone_positions', {})
        if 'z1' not in zp: return
        pos = zp['z1']
        x0,y0,zw,zh = pos['x'],pos['y'],pos['width'],pos['height']

        pad   = max(5.0, zw*0.055)
        bed_w = max(12.0, min(zw*0.13, 32.0))
        bed_h = max(18.0, min(zh*0.42, 70.0))
        gx_   = max(7.0, min(zw*0.038, 18.0))
        gy_   = max(8.0, min(zh*0.055, 16.0))

        avail = zw - 2*pad
        nb    = min(6, max(1, int((avail+gx_)/(bed_w+gx_))))
        total_bw = nb*bed_w + (nb-1)*gx_
        sx_   = x0 + pad + max(0.0, (avail-total_bw)/2)

        rows = 1
        if not small and zh > (bed_h*2+gy_+2*pad+5): rows = 2

        placed_beds = []
        for row in range(rows):
            by_ = y0 + pad + row*(bed_h+gy_)
            if by_+bed_h > y0+zh-pad: break
            for i in range(nb):
                bx_ = sx_ + i*(bed_w+gx_)
                if bx_+bed_w > x0+zw-pad: break
                if not self._reg.rect_ok(bx_, by_, bed_w, bed_h, gap=2):
                    continue
                self._reg.reg_rect(bx_, by_, bed_w, bed_h)
                _raised_bed(ax, bx_, by_, bed_w, bed_h, zorder=6)
                placed_beds.append((bx_, by_, bed_w, bed_h))

        # Inner garden path between rows (inside z1 only)
        if rows == 2 and placed_beds:
            py_ = y0 + pad + bed_h + gy_*0.08
            ph_ = gy_*0.84
            ax.add_patch(Rectangle((x0+pad, py_), total_bw, ph_,
                                    facecolor='#D2B48C', edgecolor='#BCAAA4',
                                    lw=0.7, alpha=0.66, zorder=5))

        # Compost corner
        cs = max(9.0, min(zw*0.072, 20.0))
        cx_c = x0+zw-pad-cs; cy_c = y0+zh-pad-cs
        if self._reg.rect_ok(cx_c, cy_c, cs, cs, gap=2):
            self._reg.reg_rect(cx_c, cy_c, cs, cs)
            ax.add_patch(FancyBboxPatch((cx_c,cy_c), cs, cs,
                                         boxstyle='round,pad=1.1',
                                         facecolor='#5D4037', edgecolor='#3E2723',
                                         lw=1.2, zorder=6))
            ax.text(cx_c+cs/2, cy_c+cs/2, 'COMPOST', ha='center', va='center',
                    fontsize=max(4,cs*0.19), color='white', fontweight='bold', zorder=7)

    # ─────────────────────────────────────────────
    #  FOOD FOREST TREES — strict non-overlap
    # ─────────────────────────────────────────────
    def _trees(self, ax, layout, L, W, unit, small):
        zp    = layout.get('zone_positions', {})
        feats = layout.get('features', {})
        tc    = int(layout.get('tree_count', 15))
        base_r = max(3.5, min(unit*0.026, 13.0))

        pond_x = pond_y = pond_rb = -9999.0
        if 'pond' in feats and feats['pond']:
            pf = feats['pond']
            pond_x = float(pf.get('x',-9999)); pond_y = float(pf.get('y',-9999))
            pond_rb = float(pf.get('radius',10)) * 1.28

        # Z2 — Food Forest
        if 'z2' in zp:
            z2 = zp['z2']
            np.random.seed(42)
            n_ff = max(tc, 6)
            placed = 0; attempts = 0
            while placed < n_ff and attempts < n_ff*35:
                attempts += 1
                sp = SP_LIST[placed % len(SP_LIST)]
                r  = SP_SIZES.get(sp,0.70) * base_r
                tx = z2['x'] + np.random.uniform(0.04,0.96)*z2['width']
                ty = z2['y'] + np.random.uniform(0.04,0.96)*z2['height']
                tx = max(z2['x']+r+1, min(tx, z2['x']+z2['width']-r-1))
                ty = max(z2['y']+r+1, min(ty, z2['y']+z2['height']-r-1))
                if np.hypot(tx-pond_x, ty-pond_y) < pond_rb+r: continue
                if not self._reg.circle_ok(tx, ty, r): continue
                self._reg.reg_circle(tx, ty, r)
                _draw_tree(ax, tx, ty, r, sp, zorder=7)
                placed += 1

        # Z4 — Buffer trees
        if 'z4' in zp:
            z4 = zp['z4']
            area4 = z4['width']*z4['height']
            n_b4  = max(4, min(int(area4/2800), 28))
            np.random.seed(99)
            placed4 = 0
            for idx in range(n_b4*25):
                if placed4 >= n_b4: break
                sp = ['Neem','Teak','Bamboo'][placed4%3]
                r  = SP_SIZES.get(sp,0.70)*base_r*0.85
                tx = z4['x'] + np.random.uniform(0.03,0.97)*z4['width']
                ty = z4['y'] + np.random.uniform(0.06,0.94)*z4['height']
                tx = max(z4['x']+r+1, min(tx, z4['x']+z4['width']-r-1))
                ty = max(z4['y']+r+1, min(ty, z4['y']+z4['height']-r-1))
                if not self._reg.circle_ok(tx, ty, r): continue
                self._reg.reg_circle(tx, ty, r)
                _draw_tree(ax, tx, ty, r, sp, zorder=7)
                placed4 += 1

    # ─────────────────────────────────────────────
    #  HOUSE (drawn on top)
    # ─────────────────────────────────────────────
    def _house(self, ax, layout, L, W, unit, hx, hy, hw, hh):
        z = 10; wall = min(hw,hh)*0.07
        fsr = max(5, min(8, unit*0.016)); fsl = max(8, min(13, unit*0.028))

        ax.add_patch(Rectangle((hx+3,hy-3), hw, hh, facecolor='#795548',
                                edgecolor='none', alpha=0.17, zorder=z-1))
        ax.add_patch(Rectangle((hx,hy), hw, hh, facecolor='#ECEFF1',
                                edgecolor='#546E7A', linewidth=max(1.8,wall*0.37), zorder=z))
        sg = max(4, hh*0.058)
        for ry in np.arange(hy+wall, hy+hh, sg):
            ax.plot([hx+wall,hx+hw-wall],[ry,ry], color='#B0BEC5', lw=0.5, alpha=0.50, zorder=z)
        rdx = hx+hw/2
        ax.plot([rdx,rdx],[hy+wall,hy+hh-wall], color='#607D8B',
                lw=max(1.3,wall*0.27), linestyle='-.', zorder=z+1)
        for corner in [(hx,hy),(hx+hw,hy),(hx,hy+hh),(hx+hw,hy+hh)]:
            ax.plot([corner[0],rdx],[corner[1],hy+hh/2],
                    color='#546E7A', lw=max(0.65,wall*0.17), alpha=0.55, zorder=z+1)
        for wx0,wy0,wx1,wy1 in [
            (hx,hy,hx+hw,hy+wall),(hx,hy+hh-wall,hx+hw,hy+hh),
            (hx,hy,hx+wall,hy+hh),(hx+hw-wall,hy,hx+hw,hy+hh)]:
            ax.add_patch(Rectangle((wx0,wy0),wx1-wx0,wy1-wy0,
                                    facecolor='#8D6E63', edgecolor='none', zorder=z+1))
        dy_ = hy+hh*0.52; g_=(hx+hw*0.43,hx+hw*0.57)
        ax.plot([hx+wall,g_[0]],[dy_,dy_], color='#5D4037', lw=max(1.2,wall*0.26), zorder=z+2)
        ax.plot([g_[1],hx+hw-wall],[dy_,dy_], color='#5D4037', lw=max(1.2,wall*0.26), zorder=z+2)
        for vf in [0.36,0.72]:
            ax.plot([hx+hw*vf,hx+hw*vf],[dy_,hy+hh-wall],
                    color='#5D4037', lw=max(1.0,wall*0.22), zorder=z+2)
        rl=dict(fontsize=fsr, color='#5D4037', ha='center', va='center', zorder=z+3, fontstyle='italic')
        ax.text(hx+hw*.50,hy+hh*.27,'LIVING / KITCHEN',**rl)
        ax.text(hx+hw*.18,hy+hh*.75,'BED 1',**rl)
        ax.text(hx+hw*.54,hy+hh*.75,'MASTER',**rl)
        ax.text(hx+hw*.86,hy+hh*.75,'BATH',**rl)
        ww_=hw*0.13; wzh=wall*0.82
        ws=dict(facecolor='#B3E5FC',edgecolor='#1565C0',lw=max(0.8,wall*0.17),zorder=z+2)
        for wx in [hx+hw*0.18,hx+hw*0.62]:
            ax.add_patch(Rectangle((wx,hy),ww_,wzh,**ws))
            ax.add_patch(Rectangle((wx,hy+hh-wzh),ww_,wzh,**ws))
        ax.add_patch(Rectangle((hx,hy+hh*.54),wzh,ww_,**ws))
        ax.add_patch(Rectangle((hx+hw-wzh,hy+hh*.54),wzh,ww_,**ws))
        fdw=hw*0.13; fdx=hx+hw/2-fdw/2
        ax.add_patch(Rectangle((fdx,hy),fdw,wall*1.3, facecolor='#3E2723',
                                 edgecolor='black', lw=max(0.8,wall*0.17), zorder=z+2))
        ax.add_patch(Arc((fdx,hy+wall*.6),fdw*2,fdw*2, angle=0, theta1=0, theta2=90,
                          color='#4E342E', lw=max(0.8,wall*0.17), zorder=z+3))
        for si,ss in enumerate([hh*0.053,hh*0.092,hh*0.130]):
            ax.add_patch(FancyBboxPatch((fdx-ss*.4,hy-ss*.50-si*hh*0.013),fdw+ss*.8,ss*.46,
                                         boxstyle='round,pad=0.7', facecolor='#EFEBE9',
                                         edgecolor='#8D6E63', lw=max(0.45,wall*0.10), zorder=z-1))
        pw_=hw*.50; pd_=hh*.13; px2_=hx+(hw-pw_)/2; py2_=hy-pd_
        ax.add_patch(FancyBboxPatch((px2_,py2_),pw_,pd_, boxstyle='round,pad=1.4',
                                     facecolor='#D7CCC8', edgecolor='#8D6E63',
                                     lw=max(0.9,wall*0.20), alpha=0.87, zorder=z-1))
        for dd in np.arange(py2_+2,py2_+pd_,max(3.2,pd_*0.16)):
            ax.plot([px2_+2,px2_+pw_-2],[dd,dd], color='#A1887F', lw=0.42, alpha=0.50, zorder=z)
        cw2=hw*.07; cd2=hh*.07; cx2=hx+hw*.72; cy2=hy+hh*.40
        ax.add_patch(Rectangle((cx2,cy2),cw2,cd2, facecolor='#6D4C41',
                                 edgecolor='#3E2723', lw=max(0.9,wall*0.20), zorder=z+2))
        sc_=unit/300.0
        for sox,soy,sr,sa in [(2,8,3,.25),(4,15,4.4,.15),(7,23,6.4,.08)]:
            ax.add_patch(Circle((cx2+cw2/2+sox*sc_,cy2+cd2+soy*sc_), sr*sc_,
                                  facecolor='#90A4AE', edgecolor='none', alpha=sa, zorder=z+2))
        ax.text(hx+hw/2, hy+hh+max(10,unit*0.032), 'RESIDENCE',
                ha='center', fontsize=fsl, fontweight='bold', color='#BF360C', zorder=z+4,
                path_effects=[pe.withStroke(linewidth=2.2, foreground='white')])

    # ─────────────────────────────────────────────
    #  ZONE LABELS
    # ─────────────────────────────────────────────
    def _zone_labels(self, ax, layout, L, W, unit, hx, hy, hw, hh):
        for zid, pos in layout.get('zone_positions',{}).items():
            cx = pos['x']+pos['width']/2; cy = pos['y']+pos['height']/2
            area = int(pos['width']*pos['height'])
            if hx<=cx<=hx+hw and hy<=cy<=hy+hh:
                cx = pos['x']+pos['width']*0.82
            ax.text(cx, cy+max(5,unit*0.015), self.ZONE_NAMES.get(zid,zid),
                    ha='center', va='center',
                    fontsize=max(6.5,min(10.5,unit*0.024)), fontweight='bold',
                    color='#1B5E20', zorder=13,
                    bbox=dict(boxstyle='round,pad=0.26', facecolor='white',
                              edgecolor='#A5D6A7', alpha=0.87, lw=0.80))
            ax.text(cx, cy-max(7,unit*0.019), f'{area:,} sq.ft.',
                    ha='center', va='center',
                    fontsize=max(5.5,min(8.5,unit*0.018)), color='#33691E', zorder=13)

    # ─────────────────────────────────────────────
    #  CARTOGRAPHIC
    # ─────────────────────────────────────────────
    def _north_arrow(self, ax, L, W, unit):
        nx_,ny_=L*.93,W*.07; r=unit*0.031
        ax.add_patch(Circle((nx_,ny_),r, facecolor='white',
                             edgecolor='#1A237E', lw=2.2, zorder=15))
        ax.annotate('',xy=(nx_,ny_+r*.70),xytext=(nx_,ny_-r*.34),
                    arrowprops=dict(arrowstyle='->',color='red',lw=2.2),zorder=16)
        ax.text(nx_,ny_+r+max(2.5,r*0.36),'N', ha='center',
                fontsize=max(9,r*0.41), fontweight='bold', color='red', zorder=16)

    def _scale_bar(self, ax, L, W, unit):
        sx_,sy_=L*.04,W*.04
        sc_=max(10,min(200,int(L*.16/10)*10)); half=sc_/2
        ax.add_patch(Rectangle((sx_,sy_-3),half,6, facecolor='black',edgecolor='none',zorder=15))
        ax.add_patch(Rectangle((sx_+half,sy_-3),half,6, facecolor='white',
                                edgecolor='black',lw=0.7,zorder=15))
        ax.plot([sx_,sx_+sc_],[sy_+3.5,sy_+3.5],'k-',lw=0.4,zorder=15)
        ax.text(sx_+sc_/2,sy_-max(9,unit*0.027),f'{sc_} ft',
                ha='center', fontsize=max(6.5,unit*0.020), fontweight='bold', zorder=15)
        ax.text(sx_+sc_/2,sy_+max(9,unit*0.022),'SCALE',
                ha='center', fontsize=max(5.5,unit*0.017), zorder=15)

    def _legend(self, ax, L, W, unit):
        lx_=L+unit*0.053; ly_=W*0.97
        fs_=max(6.5,min(9.5,unit*0.024)); bsz=max(11,unit*0.031)
        items=[
            ('#ECEFF1','Residence (Roof Plan)'),('#FFCCBC','Livestock Shed'),
            ('#29B6F6','Water / Pond'),('#1565C0','Solar Array'),
            ('#E0F2F1','Greenhouse'),('#2E7D32','Food Forest Trees'),
            ('#3E2723','Raised Garden Beds'),('#D2B48C','Roads / Paths'),
            (self.ZONE_COLORS['z0'],'Zone 0 – Residential'),
            (self.ZONE_COLORS['z1'],'Zone 1 – Kitchen Garden'),
            (self.ZONE_COLORS['z2'],'Zone 2 – Food Forest'),
            (self.ZONE_COLORS['z3'],'Zone 3 – Pasture / Crops'),
            (self.ZONE_COLORS['z4'],'Zone 4 – Buffer Zone'),
        ]
        bh_=fs_*2.32; tot_h=len(items)*bh_+32; bw_=max(133,unit*0.39)
        ax.add_patch(FancyBboxPatch((lx_-8,ly_-tot_h),bw_,tot_h+6,
                                     boxstyle='round,pad=4', facecolor='white',
                                     edgecolor='#546E7A', lw=1.7, alpha=0.97, zorder=14))
        ax.text(lx_+bw_/2-8,ly_+1,'LEGEND', ha='center',
                fontsize=fs_+1.7, fontweight='bold', color='#1A237E', zorder=15)
        for i,(c,lbl) in enumerate(items):
            yp=ly_-(i+1)*bh_+5
            ax.add_patch(Rectangle((lx_,yp),bsz,max(9,fs_*1.22),
                                    facecolor=c,edgecolor='#546E7A',lw=0.65,zorder=15))
            ax.text(lx_+bsz+4,yp+max(4.5,fs_*0.60),lbl, fontsize=fs_,va='center',zorder=15)

    def _dims(self, ax, L, W, unit):
        off=unit*0.050
        ax.annotate('',xy=(0,-off),xytext=(L,-off),
                    arrowprops=dict(arrowstyle='<->',color='#1A237E',lw=1.6),zorder=13)
        ax.text(L/2,-off-max(11,unit*0.029),f'{int(L)} ft',
                ha='center', fontsize=max(8.5,unit*0.025), fontweight='bold', color='#1A237E')
        ax.annotate('',xy=(-off,0),xytext=(-off,W),
                    arrowprops=dict(arrowstyle='<->',color='#1A237E',lw=1.6),zorder=13)
        ax.text(-off-max(13,unit*0.034),W/2,f'{int(W)} ft',
                ha='center', fontsize=max(8.5,unit*0.025), fontweight='bold',
                color='#1A237E', rotation=90)

    def _title(self, ax, layout, L, W, unit):
        acres=layout.get('acres',layout.get('total_sqft',0)/43560)
        total=layout.get('total_sqft',0); cat=layout.get('category','').upper()
        loc=layout.get('location',''); ls=f' · {loc}' if loc else ''
        title=f"{acres:.2f} ACRE HOMESTEAD{ls}\n{int(total):,} SQ.FT.  ·  {cat} SCALE"
        ax.text(L/2,W+unit*0.070,title, ha='center', va='bottom',
                fontsize=max(10,min(15,unit*0.037)), fontweight='bold', color='#1B5E20',
                bbox=dict(boxstyle='round,pad=0.52', facecolor='#E8F5E9',
                          edgecolor='#2E7D32', lw=2.2), zorder=16)
