"""
Professional 2D Site-Plan Visualizer â€” Premium v3
Homestead Architect Pro 2026 â€” Global Edition

Inspired by: top-down aerial renders showing curved gravel paths,
wooden raised beds, perimeter tree border, proper house roof plan.

Rules:
  - Curved bezier paths between every feature
  - Raised beds with visible wooden frames
  - Perimeter border of dense shrubs/trees
  - Proper architectural house plan (roof ridge + rooms)
  - ALL features preserved, nothing removed
  - Overlap prevention via bounding box registry
  - English-only code comments
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


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  Bounding-box registry (same logic as 3D collision system)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
class _Reg2D:
    GAP = 4.0
    def __init__(self):
        self.rects: List[Tuple] = []
        self.circles: List[Tuple] = []

    def add_rect(self, x,y,w,h):
        self.rects.append((x,y,w,h))

    def add_circle(self, cx,cy,r):
        self.circles.append((cx,cy,r))

    def rect_ok(self,x,y,w,h) -> bool:
        g=self.GAP
        for (rx,ry,rw,rh) in self.rects:
            if (x-g < rx+rw and x+w+g > rx and
                y-g < ry+rh and y+h+g > ry):
                return False
        for (cx,cy,r) in self.circles:
            nx=max(x-g,min(cx,x+w+g)); ny=max(y-g,min(cy,y+h+g))
            if (cx-nx)**2+(cy-ny)**2 < (r+g)**2:
                return False
        return True

    def circle_ok(self,cx,cy,r) -> bool:
        g=self.GAP
        for (rx,ry,rw,rh) in self.rects:
            nx=max(rx,min(cx,rx+rw)); ny=max(ry,min(cy,ry+rh))
            if (cx-nx)**2+(cy-ny)**2 < (r+g)**2:
                return False
        for (ocx,ocy,or_) in self.circles:
            if (cx-ocx)**2+(cy-ocy)**2 < (r+or_+g)**2:
                return False
        return True

    def point_free(self,px,py) -> bool:
        for (rx,ry,rw,rh) in self.rects:
            if rx<=px<=rx+rw and ry<=py<=ry+rh: return False
        for (cx,cy,r) in self.circles:
            if (px-cx)**2+(py-cy)**2<=r**2: return False
        return True


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  Curved bezier path helper
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _bezier_path(ax, points, width=10, color='#E8DCC8', alpha=0.92, zorder=4):
    """
    Draw a smooth curved gravel path through a list of (x,y) waypoints.
    Uses cubic bezier splines between consecutive points.
    Width is in data-units (feet).
    """
    if len(points) < 2:
        return
    pts = np.array(points, dtype=float)
    n   = len(pts)

    # Build smooth curve via catmull-rom â†’ bezier
    t_vals = np.linspace(0, 1, max(40, n*20))
    xs_all, ys_all = [], []

    for i in range(n - 1):
        p0 = pts[max(0, i-1)]
        p1 = pts[i]
        p2 = pts[i+1]
        p3 = pts[min(n-1, i+2)]
        # Catmull-Rom tangents
        t1 = (p2 - p0) * 0.5
        t2 = (p3 - p1) * 0.5
        seg_t = np.linspace(0, 1, max(20, int(np.hypot(*(p2-p1))/8)+1))
        for s in seg_t:
            h00 =  2*s**3 - 3*s**2 + 1
            h10 =    s**3 - 2*s**2 + s
            h01 = -2*s**3 + 3*s**2
            h11 =    s**3 -   s**2
            pt  = h00*p1 + h10*t1 + h01*p2 + h11*t2
            xs_all.append(pt[0]); ys_all.append(pt[1])

    xs_all = np.array(xs_all); ys_all = np.array(ys_all)

    # Compute perpendicular offsets for road width
    dx = np.gradient(xs_all); dy = np.gradient(ys_all)
    length = np.hypot(dx, dy) + 1e-9
    nx, ny = -dy/length, dx/length

    hw = width/2
    # Upper and lower edges
    x_up = xs_all + nx*hw;  y_up = ys_all + ny*hw
    x_dn = xs_all - nx*hw;  y_dn = ys_all - ny*hw

    # Fill path polygon
    x_poly = np.concatenate([x_up, x_dn[::-1]])
    y_poly = np.concatenate([y_up, y_dn[::-1]])

    ax.fill(x_poly, y_poly, color=color, alpha=alpha, zorder=zorder)
    # Edge lines
    ax.plot(x_up, y_up, color='#C8B89A', lw=0.8, alpha=0.7, zorder=zorder+1)
    ax.plot(x_dn, y_dn, color='#C8B89A', lw=0.8, alpha=0.7, zorder=zorder+1)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  Raised garden bed (wooden frame look)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _raised_bed(ax, x, y, w, h, soil_color='#3E2723', frame_color='#8D6E63',
                plant_color='#2E7D32', zorder=6):
    """Draw a single raised bed: wooden frame + soil + plant dots."""
    frame_t = min(w,h)*0.12   # frame thickness

    # Outer wooden frame
    ax.add_patch(FancyBboxPatch((x,y), w, h,
                                boxstyle='round,pad=0',
                                facecolor=frame_color,
                                edgecolor='#5D4037', linewidth=2.0,
                                zorder=zorder))
    # Soil interior
    ax.add_patch(Rectangle((x+frame_t, y+frame_t),
                            w-2*frame_t, h-2*frame_t,
                            facecolor=soil_color,
                            edgecolor='none', zorder=zorder+1))
    # Plant dots in rows
    inner_w = w - 2*frame_t - 4
    inner_h = h - 2*frame_t - 4
    if inner_w < 4 or inner_h < 4:
        return
    n_cols = max(1, int(inner_w / 12))
    n_rows = max(1, int(inner_h / 10))
    p_colors = ['#4CAF50','#66BB6A','#81C784','#A5D6A7']
    for ri in range(n_rows):
        for ci in range(n_cols):
            px = x + frame_t + 2 + ci * (inner_w/(max(n_cols-1,1))) if n_cols>1 else x+w/2
            py = y + frame_t + 2 + ri * (inner_h/(max(n_rows-1,1))) if n_rows>1 else y+h/2
            ax.add_patch(Circle((px,py), min(3.5, inner_w/n_cols*0.35),
                                facecolor=p_colors[(ri+ci)%len(p_colors)],
                                edgecolor='#1B5E20', linewidth=0.4,
                                zorder=zorder+2))


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  Single tree (top-down aerial view â€” blob canopy)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
TREE_COLORS = {
    'Mango':    ('#2E7D32','#388E3C'), 'Jackfruit':('#1B5E20','#2E7D32'),
    'Coconut':  ('#33691E','#558B2F'), 'Banana':   ('#558B2F','#7CB342'),
    'Guava':    ('#33691E','#43A047'), 'Papaya':   ('#558B2F','#8BC34A'),
    'Avocado':  ('#2E7D32','#1B5E20'), 'Moringa':  ('#66BB6A','#4CAF50'),
    'Citrus':   ('#43A047','#66BB6A'), 'Neem':     ('#388E3C','#2E7D32'),
    'Teak':     ('#1B5E20','#2E7D32'), 'Bamboo':   ('#4CAF50','#8BC34A'),
    'default':  ('#2E7D32','#388E3C'),
}

def _draw_tree(ax, tx, ty, r, species='default', zorder=7):
    """Aerial top-down tree: shadow + canopy blob + highlight."""
    c1,c2 = TREE_COLORS.get(species, TREE_COLORS['default'])
    # Drop shadow
    ax.add_patch(Circle((tx+r*0.25, ty-r*0.25), r*1.0,
                         facecolor='#1B5E20', edgecolor='none',
                         alpha=0.18, zorder=zorder-1))
    # Main canopy
    np.random.seed(hash(species+str(round(tx)))%9999)
    # Irregular blob via polygon
    n = 12
    angles = np.linspace(0, 2*np.pi, n, endpoint=False)
    radii  = r * (0.82 + 0.18*np.random.rand(n))
    bx = tx + radii * np.cos(angles)
    by = ty + radii * np.sin(angles)
    ax.add_patch(Polygon(list(zip(bx,by)),
                          facecolor=c1, edgecolor=c2,
                          linewidth=1.0, alpha=0.92, zorder=zorder))
    # Inner highlight
    ax.add_patch(Circle((tx-r*0.22, ty+r*0.22), r*0.32,
                         facecolor='white', edgecolor='none',
                         alpha=0.14, zorder=zorder+1))


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  Main class
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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

    # â”€â”€ Public API â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def create(self, layout: dict, answers: dict) -> BytesIO:
        L = layout['dimensions']['L']
        W = layout['dimensions']['W']
        self._reg = _Reg2D()
        self._L = L; self._W = W

        fig, ax = plt.subplots(figsize=(18,14), dpi=150)
        fig.patch.set_facecolor('#F9F6F0')
        ax.set_facecolor('#5A8F3C')   # rich grass green base

        # â”€â”€ Back â†’ Front draw order â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self._grass_texture(ax, L, W)
        self._zones(ax, layout, L, W)
        self._perimeter_border(ax, L, W)
        self._contour_lines(ax, layout, L, W)
        self._curved_paths(ax, layout, L, W)   # curved gravel paths
        self._water_features(ax, layout, L, W)
        self._utilities(ax, layout, L, W)
        self._livestock_housing(ax, layout, L, W)
        self._kitchen_garden_beds(ax, layout, L, W)
        self._vegetation(ax, layout, L, W)
        self._house_plan(ax, layout, L, W)
        self._zone_labels(ax, layout, L, W)

        # â”€â”€ Cartographic â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self._north_arrow(ax, L, W)
        self._scale_bar(ax, L, W)
        self._legend(ax, L, W)
        self._dimensions(ax, L, W)
        self._title(ax, layout, L, W)

        margin = max(L,W)*0.18
        ax.set_xlim(-margin, L+margin*1.9)
        ax.set_ylim(-margin*1.1, W+margin)
        ax.set_aspect('equal')
        ax.axis('off')
        plt.tight_layout(pad=0.4)

        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=200, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        buf.seek(0)
        plt.close(fig)
        return buf

    # â”€â”€ Grass texture â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _grass_texture(self, ax, L, W):
        """Subtle grass texture via small semi-random strokes."""
        np.random.seed(1)
        # Base green fill
        ax.add_patch(Rectangle((0,0),L,W,
                                facecolor='#5A8F3C',edgecolor='none',zorder=0))
        # Fine noise overlay (very subtle)
        for _ in range(400):
            gx=np.random.uniform(2,L-2); gy=np.random.uniform(2,W-2)
            gl=np.random.uniform(3,12); ga=np.random.uniform(20,80)
            gc=['#4CAF50','#66BB6A','#388E3C','#2E7D32'][_ % 4]
            ax.plot([gx,gx+np.random.uniform(-2,2)],[gy,gy+gl],
                    color=gc, lw=0.4, alpha=0.12, zorder=0)

    # â”€â”€ Zones (semi-transparent overlays) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _zones(self, ax, layout, L, W):
        for zid,pos in layout.get('zone_positions',{}).items():
            ax.add_patch(Rectangle((pos['x'],pos['y']),pos['width'],pos['height'],
                                   facecolor=self.ZONE_COLORS.get(zid,'#CCC'),
                                   edgecolor='#546E7A', linewidth=1.5,
                                   alpha=0.40, zorder=2))

    # â”€â”€ Perimeter border (dense shrubs like in reference) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _perimeter_border(self, ax, L, W):
        """Ring of dense green shrubs/trees around property boundary."""
        border_w = min(L,W)*0.04
        np.random.seed(7)
        # Draw dense circular blobs along all 4 edges
        for edge in range(4):
            if edge==0:   xs=np.linspace(0,L,int(L/14)); ys=[border_w/2]*len(xs)
            elif edge==1: xs=np.linspace(0,L,int(L/14)); ys=[W-border_w/2]*len(xs)
            elif edge==2: ys=np.linspace(border_w,W-border_w,int(W/14)); xs=[border_w/2]*len(ys)
            else:         ys=np.linspace(border_w,W-border_w,int(W/14)); xs=[L-border_w/2]*len(ys)
            for bx,by in zip(xs,ys):
                r = np.random.uniform(border_w*0.55, border_w*0.90)
                c = ['#1B5E20','#2E7D32','#388E3C','#33691E'][int(bx+by)%4]
                ax.add_patch(Circle((bx+np.random.uniform(-3,3),
                                     by+np.random.uniform(-3,3)),
                                    r, facecolor=c, edgecolor='#1B5E20',
                                    linewidth=0.5, alpha=0.88, zorder=3))

    # â”€â”€ Contour lines â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _contour_lines(self, ax, layout, L, W):
        slope = layout.get('slope','Flat')
        if slope=='Flat': return
        for idx in range(1,5):
            frac=idx/5
            if slope in('South','North'):
                y=W*frac if slope=='South' else W*(1-frac)
                ax.plot([0,L],[y,y],color='#A5D6A7',linestyle='--',
                        lw=0.6,alpha=0.5,zorder=1)
            else:
                x=L*frac if slope=='East' else L*(1-frac)
                ax.plot([x,x],[0,W],color='#A5D6A7',linestyle='--',
                        lw=0.6,alpha=0.5,zorder=1)

    # â”€â”€ Paths: logical network only â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _curved_paths(self, ax, layout, L, W):
        """
        CLEAN path network:
          1. Main entrance: boundary to front door
          2. Garden path inside Z1
          3. Service path: house to greenhouse
          4. Farm road: house to livestock/Z3
        NO random spurs to every feature.
        """
        hx, hy, hw, hh = self._house_bbox(layout, L, W)
        door_cx = hx + hw / 2
        gravel  = '#E8DCC8'
        gravel2 = '#D7CCC8'
        main_w  = max(10, min(L,W) * 0.026)
        sec_w   = max(7,  min(L,W) * 0.016)

        # 1. Main entrance: south boundary to front door
        self._reg.add_rect(door_cx - main_w/2, 0, main_w, hy)
        _bezier_path(ax, [
            (door_cx,               0),
            (door_cx + L*0.025,     hy*0.35),
            (door_cx - L*0.018,     hy*0.70),
            (door_cx,               hy),
        ], width=main_w, color=gravel, zorder=4)

        # 2. Garden path inside Z1 (between raised beds)
        features = layout.get('features', {})
        z1 = layout.get('zone_positions', {}).get('z1', {})
        if z1:
            z1_cy = z1['y'] + z1['height'] * 0.5
            _bezier_path(ax, [
                (z1['x'] + z1['width'] * 0.05,  z1_cy),
                (z1['x'] + z1['width'] * 0.35,  z1_cy + W * 0.008),
                (z1['x'] + z1['width'] * 0.65,  z1_cy - W * 0.006),
                (z1['x'] + z1['width'] * 0.95,  z1_cy),
            ], width=sec_w * 0.80, color=gravel2, alpha=0.72, zorder=4)

        # 3. Service path: house right edge to greenhouse
        if 'greenhouse' in features:
            gh = features['greenhouse']
            gh_cx = gh['x']
            gh_cy = gh['y'] + gh['height'] / 2
            house_r = hx + hw
            _bezier_path(ax, [
                (house_r,              hy + hh * 0.55),
                (house_r + (gh_cx - house_r) * 0.45,  gh_cy + W*0.01),
                (gh_cx,                gh_cy),
            ], width=sec_w * 0.85, color=gravel2, alpha=0.80, zorder=4)

        # 4. Farm road: house top toward Z3 livestock area
        z3 = layout.get('zone_positions', {}).get('z3', {})
        if z3:
            farm_x = hx + hw * 0.75
            z3_top = z3['y']
            z3_dest = z3['x'] + z3['width'] * 0.72
            _bezier_path(ax, [
                (farm_x,           hy + hh),
                (farm_x + L*0.02,  hy + hh + (z3_top - hy - hh) * 0.5),
                (z3_dest,          z3_top),
            ], width=sec_w, color=gravel, alpha=0.85, zorder=4)

    # â”€â”€ House (proper aerial plan view) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _house_bbox(self, layout, L, W):
        pos = layout.get('house_position','Center')
        p = {
            'North':        (L*0.30,W*0.82,L*0.38,W*0.12),
            'South':        (L*0.30,W*0.06,L*0.38,W*0.12),
            'East':         (L*0.74,W*0.36,L*0.20,W*0.28),
            'West':         (L*0.06,W*0.36,L*0.20,W*0.28),
            'Center':       (L*0.35,W*0.42,L*0.30,W*0.20),
            'Not built yet':(L*0.35,W*0.42,L*0.30,W*0.20),
        }
        return p.get(pos,p['Center'])

    def _house_plan(self, ax, layout, L, W):
        hx,hy,hw,hh = self._house_bbox(layout,L,W)
        self._reg.add_rect(hx,hy,hw,hh)
        z = 10
        wall = min(hw,hh)*0.06

        # Shadow
        ax.add_patch(Rectangle((hx+4,hy-4),hw,hh,
                                facecolor='#795548',edgecolor='none',
                                alpha=0.22,zorder=z-1))
        # Roof (light grey wood like reference image)
        ax.add_patch(Rectangle((hx,hy),hw,hh,
                                facecolor='#ECEFF1',
                                edgecolor='#546E7A',linewidth=3.5,zorder=z))
        # Roof shingles â€” fill with grey gradient lines
        for ry in np.arange(hy+wall,hy+hh,8):
            ax.plot([hx+wall,hx+hw-wall],[ry,ry],
                    color='#B0BEC5',lw=0.7,alpha=0.55,zorder=z)
        # Ridge lines (like reference)
        ridge_x = hx+hw/2
        ax.plot([ridge_x,ridge_x],[hy+wall,hy+hh-wall],
                color='#607D8B',lw=2.5,linestyle='-.',zorder=z+1)
        # Diagonal hip lines
        for corner in [(hx,hy),(hx+hw,hy),(hx,hy+hh),(hx+hw,hy+hh)]:
            ax.plot([corner[0],ridge_x],[corner[1],hy+hh/2],
                    color='#546E7A',lw=1.2,alpha=0.65,zorder=z+1)

        # Walls (thick border = wall thickness in plan)
        for wx0,wy0,wx1,wy1 in [
            (hx,   hy,         hx+hw, hy+wall),
            (hx,   hy+hh-wall, hx+hw, hy+hh),
            (hx,   hy,         hx+wall,   hy+hh),
            (hx+hw-wall,hy,    hx+hw,     hy+hh),
        ]:
            ax.add_patch(Rectangle((wx0,wy0),wx1-wx0,wy1-wy0,
                                   facecolor='#8D6E63',edgecolor='none',zorder=z+1))

        # Interior room lines
        div_y = hy+hh*0.52; gap=(hx+hw*0.43,hx+hw*0.57)
        ax.plot([hx+wall,gap[0]],[div_y,div_y],color='#5D4037',lw=2.8,zorder=z+2)
        ax.plot([gap[1],hx+hw-wall],[div_y,div_y],color='#5D4037',lw=2.8,zorder=z+2)
        # Door arc
        dw=hw*0.12; dx=hx+hw/2-dw/2
        ax.add_patch(Arc((dx,div_y),(dw*2.2),(dw*2.2),angle=0,
                          theta1=270,theta2=360,color='#4E342E',lw=1.2,zorder=z+3))
        ax.plot([dx,dx+dw],[div_y,div_y],color='#4E342E',lw=2.0,zorder=z+3)
        # Vert room dividers
        for vf in [0.36,0.72]:
            ax.plot([hx+hw*vf,hx+hw*vf],[div_y,hy+hh-wall],
                    color='#5D4037',lw=2.2,zorder=z+2)
        # Room labels
        rl = dict(fontsize=6,color='#5D4037',ha='center',va='center',
                  zorder=z+3,fontstyle='italic')
        ax.text(hx+hw*.50,hy+hh*.27,'LIVING / KITCHEN',**rl)
        ax.text(hx+hw*.18,hy+hh*.74,'BED 1',**rl)
        ax.text(hx+hw*.54,hy+hh*.74,'MASTER',**rl)
        ax.text(hx+hw*.86,hy+hh*.74,'BATH',**rl)
        # Windows
        ww=hw*0.13; wz_h=wall*0.85
        ws=dict(facecolor='#B3E5FC',edgecolor='#1565C0',lw=1.5,zorder=z+2)
        for wx in [hx+hw*0.18,hx+hw*0.62]:
            ax.add_patch(Rectangle((wx,hy),ww,wz_h,**ws))
            ax.add_patch(Rectangle((wx,hy+hh-wz_h),ww,wz_h,**ws))
        ax.add_patch(Rectangle((hx,hy+hh*.54),wz_h,ww,**ws))
        ax.add_patch(Rectangle((hx+hw-wz_h,hy+hh*.54),wz_h,ww,**ws))
        # Front door
        fdw=hw*0.13; fdx=hx+hw/2-fdw/2
        ax.add_patch(Rectangle((fdx,hy),fdw,wall*1.3,
                                facecolor='#3E2723',edgecolor='black',lw=1.2,zorder=z+2))
        ax.add_patch(Arc((fdx,hy+wall*.6),(fdw*2),(fdw*2),
                          angle=0,theta1=0,theta2=90,
                          color='#4E342E',lw=1.4,zorder=z+3))
        # Steps
        for si,ss in enumerate([10,17,24]):
            ax.add_patch(FancyBboxPatch(
                (fdx-ss*.4,hy-ss*.55-si*2.5),fdw+ss*.8,ss*.5,
                boxstyle='round,pad=1.5',facecolor='#EFEBE9',
                edgecolor='#8D6E63',lw=0.9,zorder=z-1))
        # Porch/deck (like reference image â€” wooden deck)
        pw=hw*.52; pd=hh*.14; px2=hx+(hw-pw)/2; py2=hy-pd
        ax.add_patch(FancyBboxPatch((px2,py2),pw,pd,
                                    boxstyle='round,pad=2',
                                    facecolor='#D7CCC8',edgecolor='#8D6E63',
                                    lw=1.8,alpha=0.88,zorder=z-1))
        # Deck boards (horizontal lines)
        for dy_deck in np.arange(py2+3,py2+pd,5):
            ax.plot([px2+3,px2+pw-3],[dy_deck,dy_deck],
                    color='#A1887F',lw=0.6,alpha=0.55,zorder=z)
        # Deck railing posts
        for px3 in np.linspace(px2+5,px2+pw-5,6):
            ax.plot([px3,px3],[py2,py2+pd],color='#795548',lw=1.0,zorder=z)
        ax.text(px2+pw/2,py2+pd/2,'DECK',ha='center',va='center',
                fontsize=6,color='#6D4C41',zorder=z+1)
        # Chimney
        cx2=hx+hw*.72; cy2=hy+hh*.40; cw2=hw*.08; cd2=hh*.08
        ax.add_patch(Rectangle((cx2,cy2),cw2,cd2,
                                facecolor='#6D4C41',edgecolor='#3E2723',
                                lw=1.8,zorder=z+2))
        for si,(sox,soy,sr,sa) in enumerate([(2,9,3.5,.28),(5,17,5,.18),(8,27,7,.10)]):
            ax.add_patch(Circle((cx2+cw2/2+sox,cy2+cd2+soy),sr,
                                facecolor='#90A4AE',edgecolor='none',
                                alpha=sa,zorder=z+2))
        # Label
        ax.text(hx+hw/2,hy+hh+cd2+22,'RESIDENCE',
                ha='center',fontsize=10,fontweight='bold',color='#BF360C',
                zorder=z+4,
                path_effects=[pe.withStroke(linewidth=2.8,foreground='white')])

    # â”€â”€ Kitchen Garden raised beds â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _kitchen_garden_beds(self, ax, layout, L, W):
        zones = layout.get('zone_positions',{})
        if 'z1' not in zones: return
        pos=zones['z1']
        x0,y0=pos['x'],pos['y']; w,h=pos['width'],pos['height']
        hx,hy,hw,hh=self._house_bbox(layout,L,W)
        pad=8

        # Keep beds away from house
        safe_y0=y0+pad; safe_y1=y0+h-pad
        h_margin=10
        if not (hx+hw+h_margin<x0+pad or hx-h_margin>x0+w-pad or
                hy+hh+h_margin<safe_y0 or hy-h_margin>safe_y1):
            if hy>safe_y0: safe_y1=min(safe_y1,hy-h_margin)
            else:          safe_y0=max(safe_y0,hy+hh+h_margin)

        if safe_y1-safe_y0<15: return

        # Two groups of beds (left and right of garden path)
        bed_w=max(10,min(w*0.14,18)); bed_h=max(20,min(h*0.55,(safe_y1-safe_y0)*0.90))
        gap  =max(5, min(w*0.025,8))
        n_beds=max(1,int((w-2*pad-gap)/(bed_w+gap)))

        for i in range(n_beds):
            bx=x0+pad+i*(bed_w+gap)
            if bx+bed_w>x0+w-pad: break
            by=safe_y0
            if self._reg.rect_ok(bx,by,bed_w,bed_h):
                self._reg.add_rect(bx,by,bed_w,bed_h)
                _raised_bed(ax,bx,by,bed_w,bed_h,zorder=6)

    # â”€â”€ Water features â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _water_features(self, ax, layout, L, W):
        features=layout.get('features',{})
        z=7

        for key in ('borewell','well'):
            if key in features:
                f=features[key]; r=f.get('radius',min(L,W)*.022)
                if self._reg.circle_ok(f['x'],f['y'],r):
                    self._reg.add_circle(f['x'],f['y'],r)
                    ax.add_patch(Circle((f['x'],f['y']),r,
                                        facecolor='#4FC3F7',edgecolor='#0288D1',
                                        lw=2.5,zorder=z))
                    ax.add_patch(Circle((f['x'],f['y']),r*.75,
                                        facecolor='#81D4FA',edgecolor='none',zorder=z))
                    ax.text(f['x'],f['y'],'W',ha='center',va='center',
                            fontsize=9,fontweight='bold',color='white',zorder=z+1)
                    ax.text(f['x'],f['y']-r-9,'WELL',ha='center',
                            fontsize=7,color='#0288D1',zorder=z+1)
                break

        if 'pond' in features:
            f=features['pond']; r=f['radius']
            if self._reg.circle_ok(f['x'],f['y'],r):
                self._reg.add_circle(f['x'],f['y'],r)
                theta=np.linspace(0,2*np.pi,40)
                rip=1+0.12*np.sin(3*theta)+0.08*np.cos(5*theta)
                ax.add_patch(Polygon(list(zip(f['x']+r*rip*np.cos(theta),
                                              f['y']+r*rip*np.sin(theta))),
                                     facecolor='#4FC3F7',edgecolor='#0288D1',
                                     lw=2.0,alpha=0.88,zorder=z))
                ax.add_patch(Polygon(list(zip(f['x']+r*.45*np.cos(theta),
                                              f['y']+r*.45*np.sin(theta))),
                                     facecolor='#29B6F6',edgecolor='none',
                                     alpha=0.55,zorder=z))
                np.random.seed(42)
                for _ in range(5):
                    ang=np.random.uniform(0,2*np.pi); d=np.random.uniform(0,r*.5)
                    ax.add_patch(Circle((f['x']+d*np.cos(ang),f['y']+d*np.sin(ang)),
                                        2.8,facecolor='#4CAF50',edgecolor='none',
                                        alpha=0.72,zorder=z+1))
                ax.text(f['x'],f['y'],'POND',ha='center',va='center',
                        fontsize=7.5,color='#01579B',fontweight='bold',zorder=z+1)

        if 'rain_tank' in features:
            f=features['rain_tank']
            if self._reg.rect_ok(f['x'],f['y'],f['width'],f['height']):
                self._reg.add_rect(f['x'],f['y'],f['width'],f['height'])
                ax.add_patch(FancyBboxPatch((f['x'],f['y']),f['width'],f['height'],
                                            boxstyle='round,pad=2',
                                            facecolor='#B3E5FC',edgecolor='#0288D1',
                                            lw=2.0,zorder=z))
                for by in np.linspace(f['y']+f['height']*.2,f['y']+f['height']*.85,3):
                    ax.plot([f['x']+3,f['x']+f['width']-3],[by,by],
                            color='#0288D1',lw=0.8,zorder=z+1)
                ax.text(f['x']+f['width']/2,f['y']+f['height']/2,
                        'RAIN\nTANK',ha='center',va='center',
                        fontsize=7,color='#01579B',fontweight='bold',zorder=z+1)

    # â”€â”€ Utilities (solar, greenhouse) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _utilities(self, ax, layout, L, W):
        features=layout.get('features',{})
        z=6
        if 'solar' in features:
            f=features['solar']
            if self._reg.rect_ok(f['x'],f['y'],f['width'],f['height']):
                self._reg.add_rect(f['x'],f['y'],f['width'],f['height'])
                ax.add_patch(Rectangle((f['x'],f['y']),f['width'],f['height'],
                                       facecolor='#90A4AE',edgecolor='#37474F',
                                       lw=1.5,zorder=z))
                rows,cols,g=2,3,1.5
                cw=(f['width']-g*(cols+1))/cols; ch=(f['height']-g*(rows+1))/rows
                for row in range(rows):
                    for col in range(cols):
                        px=f['x']+g+col*(cw+g); py=f['y']+g+row*(ch+g)
                        ax.add_patch(Rectangle((px,py),cw,ch,
                                               facecolor='#1565C0',edgecolor='#0D47A1',
                                               lw=0.8,zorder=z+1))
                        for gi in range(1,3):
                            ax.plot([px+gi*cw/3,px+gi*cw/3],[py,py+ch],
                                    color='#1976D2',lw=0.4,zorder=z+2)
                        ax.plot([px,px+cw],[py+ch/2,py+ch/2],
                                color='#1976D2',lw=0.4,zorder=z+2)
                ax.text(f['x']+f['width']/2,f['y']+f['height']+9,
                        'SOLAR ARRAY',ha='center',fontsize=7.5,
                        fontweight='bold',color='#0D47A1',zorder=z+2)

        if 'greenhouse' in features:
            f=features['greenhouse']
            if self._reg.rect_ok(f['x'],f['y'],f['width'],f['height']):
                self._reg.add_rect(f['x'],f['y'],f['width'],f['height'])
                ax.add_patch(Rectangle((f['x'],f['y']),f['width'],f['height'],
                                       facecolor='#E0F2F1',edgecolor='#00695C',
                                       lw=2.0,linestyle='--',alpha=0.80,zorder=z))
                ax.add_patch(Arc((f['x']+f['width']/2,f['y']+f['height']),
                                 f['width'],f['height']*.32,
                                 angle=0,theta1=0,theta2=180,
                                 color='#00695C',lw=2.0,zorder=z+1))
                for by in [f['y']+8,f['y']+f['height']-18]:
                    ax.add_patch(Rectangle((f['x']+4,by),f['width']-8,9,
                                           facecolor='#5D4037',edgecolor='black',
                                           lw=0.6,zorder=z+1))
                ax.text(f['x']+f['width']/2,f['y']-11,'GREENHOUSE',
                        ha='center',fontsize=7.5,color='#004D40',zorder=z+2)

    # â”€â”€ All livestock â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _livestock_housing(self, ax, layout, L, W):
        features=layout.get('features',{})
        if 'goat_shed'     in features: f=features['goat_shed'];     self._goat_shed(ax,f['x'],f['y'],f['width'],f['height'])
        if 'chicken_coop'  in features: f=features['chicken_coop'];  self._chicken_coop(ax,f['x'],f['y'],f['width'],f['height'])
        if 'piggery'       in features: f=features['piggery'];       self._piggery(ax,f['x'],f['y'],f['width'],f['height'])
        if 'cow_shed'      in features: f=features['cow_shed'];      self._cow_shed(ax,f['x'],f['y'],f['width'],f['height'])
        if 'fish_tanks'    in features: f=features['fish_tanks'];    self._fish_tanks(ax,f['x'],f['y'],f['width'],f['height'])
        if 'bee_hives'     in features: f=features['bee_hives'];     self._bee_hives(ax,f['x'],f['y'],f['width'],f['height'])

    def _shed_base(self,ax,x,y,w,h,fc,ec,label,z=6):
        if not self._reg.rect_ok(x,y,w,h): return False
        self._reg.add_rect(x,y,w,h)
        ax.add_patch(Rectangle((x-2,y-2),w+4,h+4,facecolor='#8D6E63',edgecolor='none',zorder=z-1))
        ax.add_patch(Rectangle((x,y),w,h,facecolor=fc,edgecolor=ec,lw=2.5,zorder=z))
        ax.add_patch(Polygon([[x-4,y+h],[x+w/2,y+h+min(h*.25,16)],[x+w+4,y+h]],
                              facecolor='#A1887F',edgecolor=ec,lw=1.5,zorder=z+1))
        ax.text(x+w/2,y+h+min(h*.25,16)+8,label,ha='center',fontsize=8,
                fontweight='bold',color=ec,zorder=z+2)
        return True

    def _goat_shed(self,ax,x,y,w,h):
        if not self._shed_base(ax,x,y,w,h,'#FFCCBC','#5D4037','GOAT SHED'): return
        for vx in [x+w*.2,x+w*.5,x+w*.8]:
            ax.add_patch(Rectangle((vx-7,y+h-9),14,8,facecolor='#B3E5FC',edgecolor='black',lw=0.8,zorder=7))
        ax.add_patch(Rectangle((x+10,y-8),w-20,8,facecolor='#4E342E',edgecolor='black',zorder=7))
        ax.add_patch(Rectangle((x+w/2-11,y),22,32,facecolor='#3E2723',edgecolor='black',zorder=7))
        for fx in range(int(x),int(x+w),13):
            ax.plot([fx,fx],[y-22,y-8],color='#8D6E63',lw=1.8,zorder=7)
        ax.plot([x,x+w],[y-8,y-8],color='#8D6E63',lw=1.8,zorder=7)
        ax.plot([x,x+w],[y-16,y-16],color='#8D6E63',lw=0.9,zorder=7)

    def _chicken_coop(self,ax,x,y,w,h):
        if not self._shed_base(ax,x,y,w,h,'#FFF8E1','#F57F17','CHICKEN COOP'): return
        ax.add_patch(Rectangle((x+w,y+h*.28),w*.28,h*.42,facecolor='#FFE0B2',edgecolor='#E65100',lw=1.8,zorder=7))
        ax.add_patch(Polygon([[x+w*.30,y],[x+w*.50,y-18],[x+w*.70,y]],facecolor='#D7CCC8',edgecolor='#5D4037',zorder=7))
        ax.add_patch(Rectangle((x-18,y-36),w+54,36,facecolor='#F1F8E9',edgecolor='#33691E',linestyle='--',alpha=0.45,zorder=5))

    def _piggery(self,ax,x,y,w,h):
        if not self._shed_base(ax,x,y,w,h,'#FFCCBC','#BF360C','PIGGERY'): return
        sw=w/3
        for i,s in enumerate(['FAR','NUR','GRW']):
            sx=x+i*sw
            if i>0: ax.plot([sx,sx],[y,y+h],'k-',lw=1.8,zorder=7)
            ax.text(sx+sw/2,y+h/2,s,ha='center',va='center',fontsize=7,fontweight='bold',color='#BF360C',zorder=7)
        for fx in [x+w*.15,x+w*.85]:
            ax.add_patch(Circle((fx,y+h-13),7,facecolor='#EEE',edgecolor='black',lw=0.8,zorder=8))
            for ang in [0,45,90,135]:
                r=np.radians(ang); ax.plot([fx,fx+5.5*np.cos(r)],[y+h-13,y+h-13+5.5*np.sin(r)],'k-',lw=0.8,zorder=8)

    def _cow_shed(self,ax,x,y,w,h):
        if not self._shed_base(ax,x,y,w,h,'#D7CCC8','#5D4037','COW SHED'): return
        n=max(2,int(w/38)); sw=w/n
        for i in range(1,n):
            ax.plot([x+i*sw,x+i*sw],[y+h*.28,y+h],color='#795548',lw=1.8,zorder=7)
        ax.add_patch(Rectangle((x,y),w,h*.28,facecolor='#EFEBE9',edgecolor='#5D4037',lw=1.2,zorder=7))
        ax.text(x+w/2,y+h*.14,'FEED ALLEY',ha='center',va='center',fontsize=6,color='#5D4037',zorder=8)
        ax.add_patch(Rectangle((x+w*.3,y-13),w*.4,10,facecolor='#B3E5FC',edgecolor='#0288D1',lw=1.2,zorder=7))

    def _fish_tanks(self,ax,x,y,w,h):
        if not self._shed_base(ax,x,y,w,h,'#B3E5FC','#0288D1','FISH TANKS'): return
        tw=(w-12)/2; th=(h-12)/2
        for tx,ty in [(x+4,y+4),(x+4+tw+4,y+4),(x+4,y+4+th+4),(x+4+tw+4,y+4+th+4)]:
            ax.add_patch(Rectangle((tx,ty),tw,th,facecolor='#4FC3F7',edgecolor='#0288D1',lw=1.5,zorder=7))
            ax.add_patch(Circle((tx+tw/2,ty+th/2),min(tw,th)*.22,facecolor='#B3E5FC',edgecolor='none',alpha=0.6,zorder=8))

    def _bee_hives(self,ax,x,y,w,h):
        if not self._shed_base(ax,x,y,w,h,'#FFF176','#F9A825','BEE HIVES'): return
        n=max(1,int(w/14)); hw_e=(w-4)/n-1.5
        for hi in range(n):
            hxe=x+2+hi*(hw_e+1.5)
            ax.add_patch(FancyBboxPatch((hxe,y+2),hw_e,h*.5,boxstyle='round,pad=1',
                                        facecolor=['#FFF176','#FFD54F','#FFCA28'][hi%3],
                                        edgecolor='#F57F17',lw=1.5,zorder=7))
            ax.add_patch(Rectangle((hxe-0.5,y+2+h*.5+2),hw_e+1,h*.28,facecolor='#FFF9C4',edgecolor='#F9A825',lw=1.2,zorder=7))
            ax.add_patch(Rectangle((hxe-1,y+h*.8+4),hw_e+2,4,facecolor='#795548',edgecolor='#4E342E',lw=1.2,zorder=7))
        np.random.seed(55)
        for _ in range(7):
            bx=x+np.random.uniform(0,w+35); by=y+h+np.random.uniform(2,18)
            ax.add_patch(Circle((bx,by),1.4,facecolor='#FDD835',edgecolor='#F57F17',lw=0.4,alpha=0.65,zorder=8))

    # â”€â”€ Vegetation (aerial top-down trees) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _vegetation(self, ax, layout, L, W):
        zones=layout.get('zone_positions',{})
        features=layout.get('features',{})
        placements=layout.get('tree_placements',[])

        # Auto from z2
        if not placements and 'z2' in zones:
            z=zones['z2']
            np.random.seed(42)
            sp_list=['Mango','Jackfruit','Coconut','Banana','Guava','Papaya',
                     'Avocado','Moringa','Citrus','Neem','Teak','Bamboo']
            for idx in range(25):
                rx=np.random.uniform(.06,.94); ry=np.random.uniform(.06,.94)
                placements.append({'x':z['x']+rx*z['width'],
                                   'y':z['y']+ry*z['height'],
                                   'species':sp_list[idx%len(sp_list)]})

        # Buffer zone sparse trees
        if 'z4' in zones:
            z4=zones['z4']
            np.random.seed(77)
            for idx in range(14):
                rx=np.random.uniform(.03,.97); ry=np.random.uniform(.08,.92)
                sp=['Neem','Teak','Bamboo'][idx%3]
                placements.append({'x':z4['x']+rx*z4['width'],
                                   'y':z4['y']+ry*z4['height'],
                                   'species':sp})

        # Extra user trees
        for t in layout.get('extra_trees',[]):
            placements.append(t)

        sp_sizes={'Mango':13,'Jackfruit':15,'Coconut':8,'Banana':7,'Guava':9,
                  'Papaya':6,'Avocado':11,'Moringa':7,'Citrus':9,'Neem':14,
                  'Teak':12,'Bamboo':5,'default':10}

        first_label=set()
        for t in placements:
            sp=t.get('species','Mango')
            r=sp_sizes.get(sp,10)
            tx=t['x']; ty=t['y']

            # Clamp inside zone if specified
            for zid in ('z2','z4'):
                if zid in zones and t.get('zone',zid)==zid:
                    z=zones[zid]
                    tx=max(z['x']+r+2, min(tx, z['x']+z['width']-r-2))
                    ty=max(z['y']+r+2, min(ty, z['y']+z['height']-r-2))

            tx=max(r+3,min(tx,L-r-3)); ty=max(r+3,min(ty,W-r-3))
            if not self._reg.circle_ok(tx,ty,r): continue
            self._reg.add_circle(tx,ty,r)
            _draw_tree(ax,tx,ty,r,sp,zorder=7)
            if sp not in first_label:
                ax.text(tx,ty+r+5,sp,ha='center',fontsize=6,color='#1B5E20',
                        zorder=8,path_effects=[pe.withStroke(linewidth=1.4,foreground='white')])
                first_label.add(sp)

    # â”€â”€ Zone labels â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _zone_labels(self, ax, layout, L, W):
        house_bbox=self._house_bbox(layout,L,W)
        for zid,pos in layout.get('zone_positions',{}).items():
            cx=pos['x']+pos['width']/2; cy=pos['y']+pos['height']/2
            area=int(pos['width']*pos['height'])
            hx,hy,hw,hh=house_bbox
            if hx<=cx<=hx+hw and hy<=cy<=hy+hh:
                cx=pos['x']+pos['width']*.82; cy=pos['y']+pos['height']*.5
            ax.text(cx,cy+8,self.ZONE_NAMES.get(zid,zid),
                    ha='center',va='center',fontsize=8,fontweight='bold',
                    color='#1B5E20',zorder=13,
                    bbox=dict(boxstyle='round,pad=0.3',facecolor='white',
                              edgecolor='#A5D6A7',alpha=0.88,lw=0.9))
            ax.text(cx,cy-10,f'{area:,} sq.ft.',ha='center',va='center',
                    fontsize=7,color='#33691E',zorder=13)

    # â”€â”€ Cartographic elements â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _north_arrow(self,ax,L,W):
        nx,ny=L*.93,W*.07; r=min(L,W)*.034
        ax.add_patch(Circle((nx,ny),r,facecolor='white',edgecolor='#1A237E',lw=2.5,zorder=15))
        ax.annotate('',xy=(nx,ny+r*.74),xytext=(nx,ny-r*.38),
                    arrowprops=dict(arrowstyle='->',color='red',lw=2.5),zorder=16)
        ax.text(nx,ny+r+5,'N',ha='center',fontsize=12,fontweight='bold',color='red',zorder=16)

    def _scale_bar(self,ax,L,W):
        sx,sy=L*.04,W*.04; sc=min(50,int(L*.18/10)*10); half=sc/2
        ax.add_patch(Rectangle((sx,sy-3),half,7,facecolor='black',edgecolor='none',zorder=15))
        ax.add_patch(Rectangle((sx+half,sy-3),half,7,facecolor='white',edgecolor='black',lw=0.8,zorder=15))
        ax.plot([sx,sx+sc],[sy+4,sy+4],'k-',lw=0.5,zorder=15)
        ax.text(sx+sc/2,sy-12,f'{sc} ft',ha='center',fontsize=8.5,fontweight='bold',zorder=15)
        ax.text(sx+sc/2,sy+12,'SCALE',ha='center',fontsize=7.5,zorder=15)

    def _legend(self,ax,L,W):
        lx=L+min(L,W)*.06; ly=W*.97
        items=[
            ('#ECEFF1','Residence (Roof)'),('#FFCCBC','Livestock Shed'),
            ('#4FC3F7','Water / Pond'),('#1565C0','Solar Array'),
            ('#E0F2F1','Greenhouse'),('#2E7D32','Food Forest Trees'),
            ('#3E2723','Raised Garden Beds'),('#E8DCC8','Gravel Paths'),
            (self.ZONE_COLORS['z0'],'Zone 0 â€“ Residential'),
            (self.ZONE_COLORS['z1'],'Zone 1 â€“ Kitchen Garden'),
            (self.ZONE_COLORS['z2'],'Zone 2 â€“ Food Forest'),
            (self.ZONE_COLORS['z3'],'Zone 3 â€“ Pasture / Crops'),
            (self.ZONE_COLORS['z4'],'Zone 4 â€“ Buffer Zone'),
        ]
        bh=19; total_h=len(items)*bh+36
        ax.add_patch(FancyBboxPatch((lx-10,ly-total_h),148,total_h+8,
                                    boxstyle='round,pad=5',facecolor='white',
                                    edgecolor='#546E7A',lw=2,alpha=0.97,zorder=14))
        ax.text(lx+64,ly+2,'LEGEND',ha='center',fontsize=10,fontweight='bold',
                color='#1A237E',zorder=15)
        for i,(c,label) in enumerate(items):
            yp=ly-(i+1)*bh+6
            ax.add_patch(Rectangle((lx,yp),15,12,facecolor=c,edgecolor='#546E7A',lw=0.8,zorder=15))
            ax.text(lx+22,yp+6,label,fontsize=7.8,va='center',zorder=15)

    def _dimensions(self,ax,L,W):
        off=min(L,W)*.055
        ax.annotate('',xy=(0,-off),xytext=(L,-off),
                    arrowprops=dict(arrowstyle='<->',color='#1A237E',lw=1.8),zorder=13)
        ax.text(L/2,-off-14,f'{int(L)} ft',ha='center',fontsize=10,fontweight='bold',color='#1A237E')
        ax.annotate('',xy=(-off,0),xytext=(-off,W),
                    arrowprops=dict(arrowstyle='<->',color='#1A237E',lw=1.8),zorder=13)
        ax.text(-off-16,W/2,f'{int(W)} ft',ha='center',fontsize=10,fontweight='bold',
                color='#1A237E',rotation=90)

    def _title(self,ax,layout,L,W):
        acres=layout.get('acres',layout.get('total_sqft',0)/43560)
        total=layout.get('total_sqft',0); cat=layout.get('category','').upper()
        title=f"{acres:.2f} ACRE HOMESTEAD\n{int(total):,} SQ.FT.  Â·  {cat} SCALE"
        ax.text(L/2,W+min(L,W)*.075,title,ha='center',va='bottom',
                fontsize=14,fontweight='bold',color='#1B5E20',
                bbox=dict(boxstyle='round,pad=0.6',facecolor='#E8F5E9',
                          edgecolor='#2E7D32',lw=2.5),zorder=16)
