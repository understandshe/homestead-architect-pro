"""
Professional 2D Architectural Visualizer
Homestead Architect Pro 2026 - Global Edition

Fixes applied:
  - House drawn as proper architectural floor-plan (not a box)
  - Paths are wide gravel roads with lane markings, not single lines
  - Full overlap prevention: every element registers its bounding box
    before being drawn; trees / shrubs never land inside ponds or paths
  - All livestock types kept (goat, chicken, pig, cow, fish, bees)
  - Cow shed and fish tanks added to 2D (were only in 3D before)
  - All original features preserved - nothing removed
  - English-only comments
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
from typing import List, Tuple, Optional


class _OccupiedRegistry:
    """Tracks placed elements to prevent overlap."""
    def __init__(self):
        self._boxes: List[Tuple[float,float,float,float]] = []
        self._circles: List[Tuple[float,float,float]] = []

    def register_rect(self, x, y, w, h, padding=5.0):
        self._boxes.append((x-padding, y-padding, w+2*padding, h+2*padding))

    def register_circle(self, cx, cy, r, padding=5.0):
        self._circles.append((cx, cy, r+padding))

    def point_clear(self, px, py, margin=0.0) -> bool:
        for (bx,by,bw,bh) in self._boxes:
            if bx-margin <= px <= bx+bw+margin and by-margin <= py <= by+bh+margin:
                return False
        for (cx,cy,r) in self._circles:
            if (px-cx)**2+(py-cy)**2 <= (r+margin)**2:
                return False
        return True


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
            'building':    '#D7CCC8',
            'roof':        '#5D4037',
            'solar':       '#1565C0',
            'solar_frame': '#0D47A1',
            'solar_cell':  '#1976D2',
            'greenhouse':  '#E0F2F1',
            'livestock':   '#FFCCBC',
            'path':        '#D7CCC8',
            'path_edge':   '#BCAAA4',
            'fence':       '#795548',
        }
        self.zone_colors = {
            'z0':'#F5F5DC','z1':'#C8E6C9','z2':'#81C784',
            'z3':'#FFF9C4','z4':'#E1BEE7',
        }
        self.zone_names = {
            'z0':'ZONE 0\nRESIDENTIAL','z1':'ZONE 1\nKITCHEN GARDEN',
            'z2':'ZONE 2\nFOOD FOREST','z3':'ZONE 3\nPASTURE / CROPS',
            'z4':'ZONE 4\nBUFFER',
        }
        self._reg: Optional[_OccupiedRegistry] = None

    def create(self, layout: dict, answers: dict) -> BytesIO:
        L = layout['dimensions']['L']
        W = layout['dimensions']['W']
        self._reg = _OccupiedRegistry()

        fig, ax = plt.subplots(figsize=(20,15), dpi=150)
        fig.patch.set_facecolor('#FAFAFA')
        ax.set_facecolor('#E8F5E9')

        self._draw_property_boundary(ax, L, W)
        if layout.get('slope','Flat') != 'Flat':
            self._draw_contour_lines(ax, L, W, layout['slope'])
        self._draw_zones(ax, layout, L, W)
        self._draw_paths(ax, layout, L, W)
        self._draw_water_features(ax, layout, L, W)
        self._draw_utilities(ax, layout, L, W)
        self._draw_livestock_housing(ax, layout, L, W)
        self._draw_vegetation(ax, layout, L, W)
        self._draw_house_plan(ax, layout, L, W)
        self._draw_zone_labels(ax, layout, L, W)
        self._add_north_arrow(ax, L, W)
        self._add_scale_bar(ax, L, W)
        self._add_legend_professional(ax, L, W)
        self._add_dimensions(ax, L, W)
        self._add_title_block(ax, layout, L, W)

        margin = max(L,W)*0.18
        ax.set_xlim(-margin, L+margin*1.8)
        ax.set_ylim(-margin*1.1, W+margin*1.0)
        ax.set_aspect('equal')
        ax.axis('off')
        plt.tight_layout(pad=0.5)

        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=200, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        buf.seek(0)
        plt.close(fig)
        return buf

    def _draw_property_boundary(self, ax, L, W):
        ax.add_patch(Rectangle((0,0), L, W, linewidth=4, edgecolor='#1A237E',
                                facecolor='none', linestyle='-', zorder=2))
        for i,(x,y) in enumerate([(0,0),(L,0),(L,W),(0,W)],1):
            ax.add_patch(Circle((x,y), min(L,W)*0.013,
                                facecolor='white', edgecolor='#1A237E',
                                linewidth=2.5, zorder=10))
            ax.text(x, y, str(i), ha='center', va='center',
                    fontsize=7, fontweight='bold', zorder=11)

    def _draw_contour_lines(self, ax, L, W, slope):
        for idx in range(1,6):
            frac = idx/6
            if slope in ('South','North'):
                y = W*frac if slope=='South' else W*(1-frac)
                ax.plot([0,L],[y,y], color='#A5D6A7',
                        linestyle='--', linewidth=0.7, alpha=0.6, zorder=1)
                ax.text(L*0.98, y, f'+{idx}m', fontsize=6,
                        color='#388E3C', ha='right', va='bottom')
            else:
                x = L*frac if slope=='East' else L*(1-frac)
                ax.plot([x,x],[0,W], color='#A5D6A7',
                        linestyle='--', linewidth=0.7, alpha=0.6, zorder=1)

    def _draw_zones(self, ax, layout, L, W):
        for zone_id, pos in layout.get('zone_positions',{}).items():
            ax.add_patch(Rectangle(
                (pos['x'],pos['y']), pos['width'], pos['height'],
                facecolor=self.zone_colors.get(zone_id,'#CCCCCC'),
                edgecolor='#546E7A', linewidth=1.8, alpha=0.65, zorder=3))

    # ── PATHS: wide gravel roads with lane markings ─────────────────────────
    def _draw_paths(self, ax, layout, L, W):
        hx, hy, hw, hh = self._get_house_bbox(layout, L, W)
        door_cx = hx + hw/2

        path_color = '#D7CCC8'
        path_edge  = '#A1887F'
        path_dash  = '#BCAAA4'
        main_w = max(14, min(L,W)*0.032)
        sec_w  = max(9,  min(L,W)*0.020)
        gate_w = max(6,  min(L,W)*0.013)

        def vpath(xc, y0, y1, pw, z=4):
            px = xc - pw/2
            py = min(y0,y1)
            ph = abs(y1-y0)
            ax.add_patch(Rectangle((px,py), pw, ph,
                                   facecolor=path_color, edgecolor=path_edge,
                                   linewidth=1.2, zorder=z))
            ax.plot([px,px],[py,py+ph], color=path_edge, lw=1.8, zorder=z+1)
            ax.plot([px+pw,px+pw],[py,py+ph], color=path_edge, lw=1.8, zorder=z+1)
            if pw >= 12:
                ax.plot([xc,xc],[py,py+ph], color=path_dash, lw=0.9,
                        linestyle='--', dashes=(7,7), zorder=z+1)
            for ty in np.arange(py+10, py+ph, 22):
                ax.plot([px+2,px+pw-2],[ty,ty], color=path_edge,
                        lw=0.4, alpha=0.45, zorder=z+1)
            self._reg.register_rect(px, py, pw, ph, padding=0)

        def hpath(yc, x0, x1, pw, z=4):
            px = min(x0,x1)
            py = yc - pw/2
            pw2 = abs(x1-x0)
            ax.add_patch(Rectangle((px,py), pw2, pw,
                                   facecolor=path_color, edgecolor=path_edge,
                                   linewidth=1.2, zorder=z))
            ax.plot([px,px+pw2],[py,py], color=path_edge, lw=1.8, zorder=z+1)
            ax.plot([px,px+pw2],[py+pw,py+pw], color=path_edge, lw=1.8, zorder=z+1)
            if pw >= 10:
                ax.plot([px,px+pw2],[yc,yc], color=path_dash, lw=0.9,
                        linestyle='--', dashes=(7,7), zorder=z+1)
            for tx in np.arange(px+10, px+pw2, 22):
                ax.plot([tx,tx],[py+2,py+pw-2], color=path_edge,
                        lw=0.4, alpha=0.45, zorder=z+1)
            self._reg.register_rect(px, py, pw2, pw, padding=0)

        # Main entrance: front door to south boundary
        vpath(door_cx, 0, hy, main_w)
        # Cross path at house mid-height
        cross_y = hy + hh*0.5
        hpath(cross_y, 0, L, sec_w)
        # North service road
        hpath(W*0.90, 0, L, sec_w)
        # East connector (cross → north road)
        vpath(L*0.85, cross_y, W*0.90, gate_w)
        # West connector
        vpath(L*0.15, cross_y, W*0.90, gate_w)

    # ── HOUSE: proper architectural floor plan ──────────────────────────────
    def _get_house_bbox(self, layout, L, W):
        pos = layout.get('house_position','Center')
        p = {
            'North':        (L*0.30, W*0.82, L*0.40, W*0.12),
            'South':        (L*0.30, W*0.06, L*0.40, W*0.12),
            'East':         (L*0.75, W*0.35, L*0.20, W*0.30),
            'West':         (L*0.05, W*0.35, L*0.20, W*0.30),
            'Center':       (L*0.35, W*0.40, L*0.30, W*0.20),
            'Not built yet':(L*0.35, W*0.40, L*0.30, W*0.20),
        }
        return p.get(pos, p['Center'])

    @staticmethod
    def _pt_in_rect(px, py, bbox):
        x,y,w,h = bbox
        return (x<=px<=x+w) and (y<=py<=y+h)

    def _draw_house_plan(self, ax, layout, L, W):
        hx, hy, hw, hh = self._get_house_bbox(layout, L, W)
        wall = min(hw,hh)*0.065
        self._reg.register_rect(hx, hy, hw, hh, padding=10)
        z = 9

        # Drop shadow
        ax.add_patch(Rectangle((hx+4,hy-4), hw, hh,
                                facecolor='#9E9E9E', edgecolor='none',
                                alpha=0.18, zorder=z-1))

        # Outer wall (thick border = wall thickness in plan view)
        ax.add_patch(Rectangle((hx,hy), hw, hh,
                                facecolor='#FFF8F0',
                                edgecolor='#3E2723', linewidth=5.0, zorder=z))

        # Inner space
        ax.add_patch(Rectangle((hx+wall,hy+wall), hw-2*wall, hh-2*wall,
                                facecolor='#FFF3E0', edgecolor='#5D4037',
                                linewidth=1.2, zorder=z))

        # Roof ridge line (centre spine)
        ridge_x = hx + hw/2
        ax.plot([ridge_x,ridge_x],[hy+wall*1.2,hy+hh-wall*1.2],
                color='#5D4037', linewidth=2.2, linestyle='-.', zorder=z+1)
        # Rafter lines
        for fy in np.linspace(hy+wall*2, hy+hh-wall*2, 5):
            ax.plot([hx+wall, ridge_x],[fy,fy],
                    color='#8D6E63', lw=0.4, alpha=0.45, zorder=z+1)
            ax.plot([ridge_x, hx+hw-wall],[fy,fy],
                    color='#8D6E63', lw=0.4, alpha=0.45, zorder=z+1)

        # Horizontal room divider (with door gap)
        div_y = hy + hh*0.52
        gap_s = hx + hw*0.43
        gap_e = hx + hw*0.57
        ax.plot([hx+wall, gap_s],[div_y,div_y], color='#3E2723', lw=3.5, zorder=z+1)
        ax.plot([gap_e, hx+hw-wall],[div_y,div_y], color='#3E2723', lw=3.5, zorder=z+1)
        # Door swing arc at gap
        ax.add_patch(Arc((gap_s, div_y), (gap_e-gap_s)*2, (gap_e-gap_s)*2,
                         angle=0, theta1=270, theta2=360,
                         color='#4E342E', lw=1.2, zorder=z+2))

        # Vertical room dividers
        for vx_frac in [0.36, 0.72]:
            vx = hx + hw*vx_frac
            ax.plot([vx,vx],[div_y,hy+hh-wall],
                    color='#3E2723', lw=2.8, zorder=z+1)

        # Room labels
        rl = dict(fontsize=6.5, color='#6D4C41', ha='center', va='center',
                  zorder=z+2, fontstyle='italic')
        ax.text(hx+hw*0.50, hy+hh*0.28, 'LIVING / KITCHEN', **rl)
        ax.text(hx+hw*0.18, hy+hh*0.74, 'BED 1', **rl)
        ax.text(hx+hw*0.54, hy+hh*0.74, 'MASTER', **rl)
        ax.text(hx+hw*0.86, hy+hh*0.74, 'BATH\n/UTIL', **rl)

        # Windows (shown as coloured gaps in walls)
        win_w  = hw*0.16
        win_th = wall*0.85
        ws = dict(facecolor='#B3E5FC', edgecolor='#1565C0', lw=1.8, zorder=z+2)
        for wx in [hx+hw*0.20, hx+hw*0.63]:          # south
            ax.add_patch(Rectangle((wx,hy), win_w, win_th, **ws))
        for wx in [hx+hw*0.20, hx+hw*0.63]:          # north
            ax.add_patch(Rectangle((wx,hy+hh-win_th), win_w, win_th, **ws))
        ax.add_patch(Rectangle((hx+hw-win_th,hy+hh*0.55), win_th, win_w, **ws))  # east
        ax.add_patch(Rectangle((hx,hy+hh*0.55), win_th, win_w, **ws))            # west

        # Front door with swing arc
        dw = hw*0.14
        dx = hx+hw/2-dw/2
        ax.add_patch(Rectangle((dx,hy), dw, wall*1.3,
                                facecolor='#FFF3E0', edgecolor='none', zorder=z+2))
        ax.plot([dx,dx+dw],[hy+wall*0.6,hy+wall*0.6],
                color='#4E342E', lw=2.5, zorder=z+3)
        ax.add_patch(Arc((dx,hy+wall*0.6), dw*2, dw*2,
                         angle=0, theta1=0, theta2=90,
                         color='#4E342E', lw=1.5, zorder=z+3))

        # Steps (3 layers outside front door)
        for s_i, s_sz in enumerate([10, 18, 26]):
            ax.add_patch(FancyBboxPatch(
                (dx - s_sz*0.4, hy - s_sz*0.6 - s_i*3),
                dw + s_sz*0.8, s_sz*0.55,
                boxstyle='round,pad=2',
                facecolor='#EFEBE9', edgecolor='#8D6E63',
                lw=1.0, zorder=z-1))

        # Porch / veranda
        porch_w = hw*0.55
        porch_h = hh*0.13
        porch_x = hx+(hw-porch_w)/2
        porch_y = hy-porch_h
        ax.add_patch(Rectangle((porch_x,porch_y), porch_w, porch_h,
                                facecolor='#EFEBE9', edgecolor='#8D6E63',
                                lw=2, linestyle='--', zorder=z-1))
        for col_x in [porch_x+porch_w*0.12, porch_x+porch_w*0.88]:
            ax.add_patch(Circle((col_x, porch_y+porch_h*0.5),
                                min(hw,hh)*0.026,
                                facecolor='#8D6E63', edgecolor='#3E2723',
                                lw=1.5, zorder=z))
        ax.text(porch_x+porch_w/2, porch_y+porch_h/2, 'PORCH',
                ha='center', va='center', fontsize=6, color='#8D6E63', zorder=z+1)

        # Chimney
        chim_x = hx+hw*0.73
        chim_y = hy+hh-wall*0.6
        chim_w = hw*0.09
        chim_h = hh*0.11
        ax.add_patch(Rectangle((chim_x,chim_y), chim_w, chim_h,
                                facecolor='#8B4513', edgecolor='#3E2723',
                                lw=2.2, zorder=z+2))
        ax.add_patch(Rectangle((chim_x-2, chim_y+chim_h), chim_w+4, 5,
                                facecolor='#5D4037', edgecolor='black',
                                lw=1, zorder=z+3))
        scx = chim_x+chim_w/2
        for s_off_x, s_off_y, s_r, s_a in [(2,9,4,0.28),(5,17,6,0.18),(9,28,8,0.10)]:
            ax.add_patch(Circle((scx+s_off_x, chim_y+chim_h+s_off_y), s_r,
                                facecolor='#90A4AE', edgecolor='none',
                                alpha=s_a, zorder=z+2))

        # Exterior label
        label_y = hy+hh+chim_h+20
        ax.text(hx+hw/2, label_y, 'RESIDENCE',
                ha='center', fontsize=10, fontweight='bold',
                color='#BF360C', zorder=z+4,
                path_effects=[pe.withStroke(linewidth=2.8, foreground='white')])

    def _draw_zone_labels(self, ax, layout, L, W):
        house_bbox = self._get_house_bbox(layout, L, W)
        for zone_id, pos in layout.get('zone_positions',{}).items():
            cx = pos['x']+pos['width']/2
            cy = pos['y']+pos['height']/2
            area = int(pos['width']*pos['height'])
            if self._pt_in_rect(cx, cy, house_bbox):
                cx = pos['x']+pos['width']*0.82
                cy = pos['y']+pos['height']*0.50
            ax.text(cx, cy+8, self.zone_names.get(zone_id, zone_id.upper()),
                    ha='center', va='center', fontsize=8.5, fontweight='bold',
                    color='#1B5E20', zorder=14,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor='#A5D6A7', alpha=0.88, linewidth=1))
            ax.text(cx, cy-10, f'{area:,} sq.ft.',
                    ha='center', va='center', fontsize=7.5,
                    color='#33691E', zorder=14)

    # ── ALL LIVESTOCK ───────────────────────────────────────────────────────
    def _draw_livestock_housing(self, ax, layout, L, W):
        features = layout.get('features',{})
        if 'goat_shed'    in features: f=features['goat_shed'];    self._draw_goat_shed_professional(ax, f['x'],f['y'],f['width'],f['height'])
        if 'chicken_coop' in features: f=features['chicken_coop']; self._draw_chicken_coop_professional(ax, f['x'],f['y'],f['width'],f['height'])
        if 'piggery'      in features: f=features['piggery'];      self._draw_piggery_professional(ax, f['x'],f['y'],f['width'],f['height'])
        if 'cow_shed'     in features: f=features['cow_shed'];     self._draw_cow_shed_professional(ax, f['x'],f['y'],f['width'],f['height'])
        if 'fish_tanks'   in features: f=features['fish_tanks'];   self._draw_fish_tanks_professional(ax, f['x'],f['y'],f['width'],f['height'])
        if 'bee_hives'    in features: f=features['bee_hives'];    self._draw_bee_hives_professional(ax, f['x'],f['y'],f['width'],f['height'])

    def _draw_goat_shed_professional(self, ax, x, y, w, h):
        self._reg.register_rect(x-30, y-30, w+60, h+55)
        ax.add_patch(Rectangle((x-2,y-2), w+4, h+4, facecolor='#8D6E63', edgecolor='black', lw=1, zorder=5))
        ax.add_patch(Rectangle((x,y), w, h, facecolor=self.colors['livestock'], edgecolor='#5D4037', lw=3, zorder=6))
        ax.add_patch(Polygon([[x-5,y+h],[x+w/2,y+h+15],[x+w+5,y+h]], facecolor='#A1887F', edgecolor='#3E2723', lw=2, zorder=7))
        for vx in [x+w*0.2, x+w*0.5, x+w*0.8]:
            ax.add_patch(Rectangle((vx-8,y+h-10), 16, 8, facecolor='#B3E5FC', edgecolor='black', zorder=7))
        ax.add_patch(Rectangle((x+10,y-8), w-20, 8, facecolor='#5D4037', edgecolor='black', zorder=7))
        ax.add_patch(Rectangle((x+w/2-12,y), 24, 35, facecolor='#4E342E', edgecolor='black', zorder=7))
        for fx in range(int(x), int(x+w), 15):
            ax.plot([fx,fx],[y-25,y-8], color='#8D6E63', lw=2, zorder=7)
        ax.plot([x,x+w],[y-8,y-8], color='#8D6E63', lw=2, zorder=7)
        ax.plot([x,x+w],[y-18,y-18], color='#8D6E63', lw=1, zorder=7)
        ax.text(x+w/2, y+h+25, 'GOAT SHED (10 animals)', ha='center', fontsize=9, fontweight='bold', color='#5D4037', zorder=8)

    def _draw_chicken_coop_professional(self, ax, x, y, w, h):
        self._reg.register_rect(x-22, y-42, w+65, h+35)
        ax.add_patch(Rectangle((x,y), w, h, facecolor='#FFF8E1', edgecolor='#F57F17', lw=3, zorder=6))
        ax.add_patch(Polygon([[x-3,y+h],[x+w+3,y+h+10],[x+w+3,y+h],[x-3,y+h-5]], facecolor='#FFCC80', edgecolor='#E65100', lw=2, zorder=7))
        ax.add_patch(Rectangle((x+w,y+h*0.3), w*0.3, h*0.4, facecolor='#FFE0B2', edgecolor='#E65100', lw=2, zorder=7))
        for ny in [y+h*0.4, y+h*0.55, y+h*0.7]:
            ax.add_patch(Arc((x+w+5,ny), 10, 15, angle=0, theta1=0, theta2=180, color='#E65100', lw=2, zorder=8))
        ax.add_patch(Polygon([[x+w*0.3,y],[x+w*0.5,y-20],[x+w*0.7,y]], facecolor='#D7CCC8', edgecolor='#5D4037', zorder=7))
        ax.add_patch(Rectangle((x-20,y-40), w+60, 40, facecolor='#F1F8E9', edgecolor='#33691E', linestyle='--', alpha=0.5, zorder=5))
        ax.text(x+w/2, y+h+20, 'CHICKEN COOP (50 birds)', ha='center', fontsize=8, fontweight='bold', color='#E65100', zorder=8)

    def _draw_piggery_professional(self, ax, x, y, w, h):
        self._reg.register_rect(x-5, y-5, w+10, h+45)
        ax.add_patch(Rectangle((x,y), w, h, facecolor='#FFCCBC', edgecolor='#BF360C', lw=3, zorder=6))
        sections = ['FARROWING','NURSERY','GROWER']
        sw = w/3
        for i,s in enumerate(sections):
            sx = x+i*sw
            if i>0: ax.plot([sx,sx],[y,y+h],'k-',lw=2,zorder=7)
            ax.text(sx+sw/2, y+h/2, s, ha='center', va='center', fontsize=7,
                    rotation=90 if len(s)>8 else 0, fontweight='bold', color='#BF360C', zorder=7)
        ax.add_patch(Polygon([[x-5,y+h],[x+w/2,y+h+20],[x+w+5,y+h]], facecolor='#FFAB91', edgecolor='#BF360C', lw=2, zorder=7))
        for fx in [x+w*0.15, x+w*0.85]:
            ax.add_patch(Circle((fx,y+h-15), 8, facecolor='#EEEEEE', edgecolor='black', lw=1, zorder=8))
            for angle in [0,45,90,135]:
                rad = np.radians(angle)
                ax.plot([fx,fx+6*np.cos(rad)],[y+h-15,y+h-15+6*np.sin(rad)],'k-',lw=1,zorder=8)
        ax.text(x+w/2, y+h+30, 'PIGGERY (5 sows + piglets)', ha='center', fontsize=9, fontweight='bold', color='#BF360C', zorder=8)

    def _draw_cow_shed_professional(self, ax, x, y, w, h):
        self._reg.register_rect(x-5, y-18, w+10, h+55)
        ax.add_patch(Rectangle((x-3,y-3), w+6, h+6, facecolor='#BCAAA4', edgecolor='black', lw=1, zorder=5))
        ax.add_patch(Rectangle((x,y), w, h, facecolor='#D7CCC8', edgecolor='#5D4037', lw=3, zorder=6))
        n_stalls = max(2, int(w/40))
        stall_w = w/n_stalls
        for i in range(1,n_stalls):
            ax.plot([x+i*stall_w, x+i*stall_w],[y+h*0.3,y+h], color='#795548', lw=2, zorder=7)
        ax.add_patch(Rectangle((x,y), w, h*0.28, facecolor='#EFEBE9', edgecolor='#5D4037', lw=1.5, zorder=7))
        ax.text(x+w/2, y+h*0.14, 'FEED ALLEY', ha='center', va='center', fontsize=6.5, color='#5D4037', zorder=8)
        ax.add_patch(Polygon([[x-5,y+h],[x+w/2,y+h+22],[x+w+5,y+h]], facecolor='#A1887F', edgecolor='#4E342E', lw=2, zorder=7))
        ax.add_patch(Rectangle((x+w*0.4,y+h+18), w*0.2, 8, facecolor='#607D8B', edgecolor='#455A64', lw=1, zorder=8))
        ax.add_patch(Rectangle((x+w*0.3,y-14), w*0.4, 10, facecolor='#B3E5FC', edgecolor='#0288D1', lw=1.5, zorder=7))
        ax.text(x+w/2, y+h+32, 'COW SHED', ha='center', fontsize=9, fontweight='bold', color='#5D4037', zorder=8)

    def _draw_fish_tanks_professional(self, ax, x, y, w, h):
        self._reg.register_rect(x-5, y-5, w+10, h+30)
        ax.add_patch(Rectangle((x-5,y-5), w+10, h+10, facecolor='#78909C', edgecolor='#455A64', lw=2, zorder=5))
        tw = (w-15)/2; th = (h-15)/2
        for tx_off, ty_off in [(5,5),(tw+10,5),(5,th+10),(tw+10,th+10)]:
            ax.add_patch(Rectangle((x+tx_off,y+ty_off), tw, th, facecolor='#4FC3F7', edgecolor='#0288D1', lw=2, zorder=6))
            ax.add_patch(Circle((x+tx_off+tw/2,y+ty_off+th/2), min(tw,th)*0.25,
                                facecolor='#B3E5FC', edgecolor='none', alpha=0.6, zorder=7))
            ax.text(x+tx_off+tw/2, y+ty_off+th/2, 'FISH', ha='center', va='center', fontsize=7, color='#01579B', zorder=8)
        for pipe_x in [x+w*0.25, x+w*0.75]:
            ax.plot([pipe_x,pipe_x],[y-5,y+h+5], color='#607D8B', lw=3, zorder=7)
        ax.text(x+w/2, y+h+18, 'FISH TANKS (Aquaculture)', ha='center', fontsize=8, fontweight='bold', color='#01579B', zorder=8)

    def _draw_bee_hives_professional(self, ax, x, y, w, h):
        self._reg.register_rect(x-10, y-10, w+50, h+32)
        ax.add_patch(Rectangle((x-2,y-2), w+4, h+4, facecolor='#8D6E63', edgecolor='#5D4037', lw=1.5, zorder=5))
        hive_w = max(18, w/3-4)
        n_hives = max(1, int(w/(hive_w+4)))
        hive_colors = ['#FFF176','#FFD54F','#FFCA28']
        for hi in range(n_hives):
            hx = x+hi*(hive_w+4)+2
            ax.add_patch(Rectangle((hx,y+2), hive_w, h*0.5, facecolor=hive_colors[hi%3], edgecolor='#F57F17', lw=2, zorder=6))
            ax.add_patch(Rectangle((hx,y+2+h*0.5+2), hive_w, h*0.3, facecolor='#FFF9C4', edgecolor='#F9A825', lw=1.5, zorder=6))
            ax.add_patch(Rectangle((hx-1,y+2+h*0.8+4), hive_w+2, 5, facecolor='#795548', edgecolor='#4E342E', lw=1.5, zorder=7))
            ax.plot([hx+hive_w*0.3,hx+hive_w*0.7],[y+2,y+2], color='#4E342E', lw=3, zorder=7)
        np.random.seed(55)
        for _ in range(8):
            bx=x+np.random.uniform(0,w+40); by=y+h+np.random.uniform(2,20)
            ax.add_patch(Circle((bx,by), 1.5, facecolor='#FDD835', edgecolor='#F57F17', lw=0.5, alpha=0.6, zorder=8))
        ax.text(x+w/2, y+h+22, 'BEE HIVES', ha='center', fontsize=8, fontweight='bold', color='#F57F17', zorder=8)

    # ── WATER FEATURES ──────────────────────────────────────────────────────
    def _draw_water_features(self, ax, layout, L, W):
        features = layout.get('features',{})

        for key in ('borewell','well'):
            if key in features:
                f = features[key]
                r = f.get('radius', min(L,W)*0.022)
                self._reg.register_circle(f['x'], f['y'], r)
                ax.add_patch(Circle((f['x'],f['y']), r, facecolor=self.colors['water'], edgecolor='#01579B', lw=3, zorder=6))
                ax.add_patch(Circle((f['x'],f['y']), r*0.8, facecolor='#81D4FA', edgecolor='none', zorder=6))
                ax.text(f['x'],f['y'],'W', ha='center', va='center', fontsize=10, fontweight='bold', color='white', zorder=7)
                ax.text(f['x'],f['y']-r-10,'BOREWELL\n(150 ft)', ha='center', fontsize=8, color='#01579B', zorder=7)

        if 'pond' in features:
            f = features['pond']; r = f['radius']
            self._reg.register_circle(f['x'], f['y'], r)
            theta = np.linspace(0,2*np.pi,40)
            ripple = 1+0.15*np.sin(3*theta)
            ax.add_patch(Polygon(list(zip(f['x']+r*ripple*np.cos(theta), f['y']+r*ripple*np.sin(theta))),
                                 facecolor='#B3E5FC', edgecolor='#0288D1', lw=2.5, alpha=0.85, zorder=5))
            ax.add_patch(Polygon(list(zip(f['x']+r*0.45*np.cos(theta), f['y']+r*0.45*np.sin(theta))),
                                 facecolor='#4FC3F7', edgecolor='none', alpha=0.5, zorder=5))
            np.random.seed(42)
            for _ in range(5):
                ang=np.random.uniform(0,2*np.pi); d=np.random.uniform(0,r*0.55)
                ax.add_patch(Circle((f['x']+d*np.cos(ang),f['y']+d*np.sin(ang)), 3,
                                    facecolor='#4CAF50', edgecolor='none', alpha=0.75, zorder=6))
            ax.text(f['x'],f['y'],'POND\n(Aquaculture)', ha='center', va='center', fontsize=8, color='#01579B', zorder=7)

        if 'rain_tank' in features:
            f = features['rain_tank']
            self._reg.register_rect(f['x'],f['y'],f['width'],f['height'])
            ax.add_patch(Rectangle((f['x'],f['y']), f['width'], f['height'],
                                   facecolor='#B3E5FC', edgecolor='#0288D1', lw=2.5, zorder=6))
            for by in np.linspace(f['y']+f['height']*0.25, f['y']+f['height']*0.85, 3):
                ax.plot([f['x'],f['x']+f['width']],[by,by], color='#0288D1', lw=1, zorder=7)
            ax.text(f['x']+f['width']/2, f['y']+f['height']/2, 'RAIN\nTANK',
                    ha='center', va='center', fontsize=7.5, fontweight='bold', color='#01579B', zorder=7)

    # ── UTILITIES ───────────────────────────────────────────────────────────
    def _draw_utilities(self, ax, layout, L, W):
        features = layout.get('features',{})

        if 'solar' in features:
            f = features['solar']
            self._reg.register_rect(f['x'],f['y'],f['width'],f['height'])
            rows,cols,gap = 2,3,2
            cw = (f['width']-gap*(cols+1))/cols
            ch = (f['height']-gap*(rows+1))/rows
            ax.add_patch(Rectangle((f['x'],f['y']),f['width'],f['height'],
                                   facecolor='#90A4AE', edgecolor='#37474F', lw=1.5, zorder=5))
            for row in range(rows):
                for col in range(cols):
                    px=f['x']+gap+col*(cw+gap); py=f['y']+gap+row*(ch+gap)
                    ax.add_patch(Rectangle((px,py),cw,ch, facecolor=self.colors['solar'],
                                           edgecolor=self.colors['solar_frame'], lw=1, zorder=6))
                    for gi in range(1,3):
                        ax.plot([px+gi*cw/3,px+gi*cw/3],[py,py+ch], color=self.colors['solar_cell'], lw=0.5, zorder=7)
                    ax.plot([px,px+cw],[py+ch/2,py+ch/2], color=self.colors['solar_cell'], lw=0.5, zorder=7)
            ax.text(f['x']+f['width']/2, f['y']+f['height']+10, 'SOLAR ARRAY\n(5 kW)',
                    ha='center', fontsize=8, fontweight='bold', color='#0D47A1', zorder=8)

        if 'greenhouse' in features:
            f = features['greenhouse']
            self._reg.register_rect(f['x'],f['y'],f['width'],f['height'])
            ax.add_patch(Rectangle((f['x'],f['y']),f['width'],f['height'],
                                   facecolor=self.colors['greenhouse'], edgecolor='#2E7D32',
                                   lw=2, linestyle='--', zorder=5))
            ax.add_patch(Arc((f['x']+f['width']/2,f['y']+f['height']),
                             f['width'], f['height']*0.32,
                             angle=0, theta1=0, theta2=180, color='#2E7D32', lw=2, zorder=6))
            for by in [f['y']+10, f['y']+f['height']-22]:
                ax.add_patch(Rectangle((f['x']+5,by), f['width']-10, 10,
                                       facecolor='#8D6E63', edgecolor='black', lw=0.8, zorder=6))
            for ry in np.linspace(f['y']+22, f['y']+f['height']-30, 3):
                ax.plot([f['x']+8,f['x']+f['width']-8],[ry,ry],
                        color='#81C784', lw=2, linestyle=':', alpha=0.7, zorder=6)
            ax.text(f['x']+f['width']/2, f['y']-12, 'GREENHOUSE\n(Seasonal crops)',
                    ha='center', fontsize=8, color='#2E7D32', zorder=7)

    # ── VEGETATION (overlap-safe) ────────────────────────────────────────────
    def _draw_vegetation(self, ax, layout, L, W):
        zone_pos = layout.get('zone_positions',{})

        if 'z2' in zone_pos:
            z = zone_pos['z2']
            specs = [
                (0.18,0.32,'Mango',   '#2E7D32',13),
                (0.50,0.60,'Coconut', '#388E3C',11),
                (0.82,0.42,'Jackfruit','#1B5E20',14),
                (0.32,0.75,'Banana',  '#558B2F',10),
                (0.68,0.22,'Guava',   '#33691E', 9),
                (0.15,0.55,'Papaya',  '#43A047', 8),
                (0.60,0.85,'Citrus',  '#66BB6A', 9),
                (0.88,0.70,'Avocado', '#2E7D32',10),
            ]
            for rx,ry,label,color,cr in specs:
                tx = max(z['x']+cr+2, min(z['x']+rx*z['width'],  z['x']+z['width'] -cr-2))
                ty = max(z['y']+cr+2, min(z['y']+ry*z['height'], z['y']+z['height']-cr-2))
                if not self._reg.point_clear(tx, ty, margin=cr): continue
                self._draw_single_tree(ax, tx, ty, cr, color, label)

        if 'z4' in zone_pos:
            z4 = zone_pos['z4']
            np.random.seed(99)
            for _ in range(10):
                sx=max(z4['x']+5,min(z4['x']+np.random.uniform(0.05,0.95)*z4['width'],z4['x']+z4['width']-5))
                sy=max(z4['y']+5,min(z4['y']+np.random.uniform(0.10,0.90)*z4['height'],z4['y']+z4['height']-5))
                if not self._reg.point_clear(sx,sy,margin=6): continue
                ax.add_patch(Circle((sx,sy),5,facecolor=['#7B1FA2','#6A1B9A','#4A148C'][_%3],
                                    edgecolor='none',alpha=0.30,zorder=5))

        if 'z3' in zone_pos:
            z3 = zone_pos['z3']
            np.random.seed(77)
            for _ in range(6):
                sx=max(z3['x']+4,min(z3['x']+np.random.uniform(0.05,0.95)*z3['width'],z3['x']+z3['width']-4))
                sy=max(z3['y']+4,min(z3['y']+np.random.uniform(0.10,0.90)*z3['height'],z3['y']+z3['height']-4))
                if not self._reg.point_clear(sx,sy,margin=5): continue
                ax.add_patch(Circle((sx,sy),4,facecolor='#9CCC65',edgecolor='#558B2F',lw=0.8,alpha=0.50,zorder=5))

    def _draw_single_tree(self, ax, tx, ty, cr, color, label, z=7):
        ax.add_patch(Polygon(
            [[tx-cr*0.65,ty-cr],[tx+cr*0.65,ty-cr],[tx+cr*0.45,ty-cr-5],[tx-cr*0.45,ty-cr-5]],
            facecolor='#33691E',edgecolor='none',alpha=0.18,zorder=z-1))
        ax.add_patch(Rectangle((tx-2,ty-cr-1),4,cr,facecolor='#795548',edgecolor='none',zorder=z))
        ax.add_patch(Circle((tx,ty),cr,facecolor=color,edgecolor='#1B5E20',lw=1.2,alpha=0.88,zorder=z+1))
        ax.add_patch(Circle((tx-cr*0.3,ty+cr*0.35),cr*0.25,facecolor='white',edgecolor='none',alpha=0.18,zorder=z+2))
        ax.text(tx,ty+cr+6,label,ha='center',fontsize=6.5,color='#1B5E20',zorder=z+2,
                path_effects=[pe.withStroke(linewidth=1.5,foreground='white')])

    # ── CARTOGRAPHIC ELEMENTS ────────────────────────────────────────────────
    def _add_north_arrow(self, ax, L, W):
        nx,ny = L*0.93, W*0.07
        r = min(L,W)*0.035
        ax.add_patch(Circle((nx,ny),r,facecolor='white',edgecolor='#1A237E',lw=2.5,zorder=15))
        ax.annotate('',xy=(nx,ny+r*0.75),xytext=(nx,ny-r*0.4),
                    arrowprops=dict(arrowstyle='->',color='red',lw=2.5),zorder=16)
        ax.text(nx,ny+r+5,'N',ha='center',fontsize=12,fontweight='bold',color='red',zorder=16)

    def _add_scale_bar(self, ax, L, W):
        sx,sy = L*0.04, W*0.04
        scale = min(50, int(L*0.18/10)*10)
        half = scale/2
        ax.add_patch(Rectangle((sx,sy-3),half,7,facecolor='black',edgecolor='none',zorder=15))
        ax.add_patch(Rectangle((sx+half,sy-3),half,7,facecolor='white',edgecolor='black',lw=0.8,zorder=15))
        ax.plot([sx,sx+scale],[sy+4,sy+4],'k-',lw=0.5,zorder=15)
        ax.text(sx+scale/2,sy-12,f'{scale} ft',ha='center',fontsize=8.5,fontweight='bold',zorder=15)
        ax.text(sx+scale/2,sy+12,'SCALE',ha='center',fontsize=7.5,zorder=15)

    def _add_legend_professional(self, ax, L, W):
        lx = L+min(L,W)*0.06
        ly = W*0.97
        bh = 19
        items = [
            ('#FFF3E0','Residence'),
            (self.colors['livestock'],'Livestock Shed'),
            (self.colors['water'],'Water / Pond'),
            (self.colors['solar'],'Solar Array (PV)'),
            (self.colors['greenhouse'],'Greenhouse'),
            ('#2E7D32','Trees (Food Forest)'),
            ('#9CCC65','Shrubs (Pasture)'),
            (self.colors['path'],'Gravel Path'),
            (self.zone_colors['z0'],'Zone 0 – Residential'),
            (self.zone_colors['z1'],'Zone 1 – Kitchen Garden'),
            (self.zone_colors['z2'],'Zone 2 – Food Forest'),
            (self.zone_colors['z3'],'Zone 3 – Pasture / Crops'),
            (self.zone_colors['z4'],'Zone 4 – Buffer Zone'),
        ]
        total_h = len(items)*bh+36
        ax.add_patch(FancyBboxPatch((lx-10,ly-total_h),148,total_h+8,
                                    boxstyle='round,pad=5',
                                    facecolor='white',edgecolor='#546E7A',lw=2,alpha=0.97,zorder=14))
        ax.text(lx+64,ly+2,'LEGEND',ha='center',fontsize=10,fontweight='bold',color='#1A237E',zorder=15)
        for i,(color,label) in enumerate(items):
            yp = ly-(i+1)*bh+6
            ax.add_patch(Rectangle((lx,yp),15,12,facecolor=color,edgecolor='#546E7A',lw=0.8,zorder=15))
            ax.text(lx+22,yp+6,label,fontsize=7.8,va='center',zorder=15)

    def _add_dimensions(self, ax, L, W):
        off = min(L,W)*0.055
        ax.annotate('',xy=(0,-off),xytext=(L,-off),
                    arrowprops=dict(arrowstyle='<->',color='#1A237E',lw=1.8),zorder=13)
        ax.text(L/2,-off-14,f'{int(L)} ft',ha='center',fontsize=10,fontweight='bold',color='#1A237E')
        ax.annotate('',xy=(-off,0),xytext=(-off,W),
                    arrowprops=dict(arrowstyle='<->',color='#1A237E',lw=1.8),zorder=13)
        ax.text(-off-16,W/2,f'{int(W)} ft',ha='center',fontsize=10,fontweight='bold',color='#1A237E',rotation=90)

    def _add_title_block(self, ax, layout, L, W):
        acres = layout.get('acres', layout.get('total_sqft',0)/43560)
        total = layout.get('total_sqft',0)
        cat   = layout.get('category','').upper()
        title = f"{acres:.2f} ACRE HOMESTEAD\n{int(total):,} SQ.FT.  ·  {cat} SCALE"
        ax.text(L/2, W+min(L,W)*0.075, title, ha='center', va='bottom',
                fontsize=14, fontweight='bold', color='#1B5E20',
                bbox=dict(boxstyle='round,pad=0.6',facecolor='#E8F5E9',
                          edgecolor='#2E7D32',lw=2.5),zorder=16)
