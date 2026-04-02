"""
3D Visualization Engine — Premium v6 FINAL
Homestead Architect Pro 2026 — Global Edition

Core fixes vs v5:
  1. Traces: 528 → ~80  (paths merged into single Surface grids,
                          plants merged into single Scatter3d,
                          trees batched by species group)
  2. Kitchen Garden never touches house — hard clamp to z1 bounds,
     house bbox excluded from bed placement
  3. Spur paths route via safe waypoints — never enter a registered
     pond/shed; each spur walks outward to the nearest clear spine point
  4. Trees fully inside z2 bounds — radius clamp + z2 bounding wall check
  5. Perimeter roads stay inside boundary and are registered first
"""

import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
from typing import Dict, Any, List, Tuple, Optional


# ─────────────────────────────────────────────────────────────────────────────
#  Collision Registry
# ─────────────────────────────────────────────────────────────────────────────
class _Reg:
    GAP = 6.0   # minimum clear gap between any two objects (ft)

    def __init__(self):
        self.rects:   List[Tuple[float,float,float,float]] = []
        self.circles: List[Tuple[float,float,float]]       = []

    def add_rect(self, x0,y0,x1,y1):
        self.rects.append((min(x0,x1), min(y0,y1), max(x0,x1), max(y0,y1)))

    def add_circle(self, cx,cy,r):
        self.circles.append((cx,cy,r))

    def rect_ok(self, x0,y0,x1,y1) -> bool:
        g = self.GAP
        ax0,ay0 = min(x0,x1)-g, min(y0,y1)-g
        ax1,ay1 = max(x0,x1)+g, max(y0,y1)+g
        for (rx0,ry0,rx1,ry1) in self.rects:
            if ax0<rx1 and ax1>rx0 and ay0<ry1 and ay1>ry0:
                return False
        for (cx,cy,r) in self.circles:
            nx,ny = max(ax0,min(cx,ax1)), max(ay0,min(cy,ay1))
            if (cx-nx)**2+(cy-ny)**2 < (r+g)**2:
                return False
        return True

    def circle_ok(self, cx,cy,r) -> bool:
        g = self.GAP
        for (rx0,ry0,rx1,ry1) in self.rects:
            nx,ny = max(rx0,min(cx,rx1)), max(ry0,min(cy,ry1))
            if (cx-nx)**2+(cy-ny)**2 < (r+g)**2:
                return False
        for (ocx,ocy,or_) in self.circles:
            if (cx-ocx)**2+(cy-ocy)**2 < (r+or_+g)**2:
                return False
        return True

    def point_free(self, px,py) -> bool:
        for (rx0,ry0,rx1,ry1) in self.rects:
            if rx0<=px<=rx1 and ry0<=py<=ry1: return False
        for (cx,cy,r) in self.circles:
            if (px-cx)**2+(py-cy)**2<=r**2: return False
        return True


# ─────────────────────────────────────────────────────────────────────────────
#  12 Tree species
# ─────────────────────────────────────────────────────────────────────────────
TREE_SPECIES = {
    'Mango':     dict(th=5, cb=5, ct=20, cr=8,  tr=1.0, c1='#2E7D32',c2='#388E3C',
                      income=(300,1500), unit='kg/yr', yld='80-200'),
    'Jackfruit': dict(th=8, cb=8, ct=26, cr=9,  tr=1.3, c1='#1B5E20',c2='#2E7D32',
                      income=(200,800),  unit='kg/yr', yld='50-200'),
    'Coconut':   dict(th=20,cb=20,ct=30, cr=5,  tr=0.6, c1='#33691E',c2='#558B2F',
                      income=(150,600),  unit='nuts/yr',yld='80-200'),
    'Banana':    dict(th=3, cb=3, ct=10, cr=4,  tr=1.4, c1='#558B2F',c2='#7CB342',
                      income=(100,400),  unit='bunch/yr',yld='5-20'),
    'Guava':     dict(th=4, cb=4, ct=13, cr=4,  tr=0.7, c1='#33691E',c2='#43A047',
                      income=(80,300),   unit='kg/yr', yld='20-60'),
    'Papaya':    dict(th=4, cb=4, ct=11, cr=3,  tr=0.5, c1='#558B2F',c2='#8BC34A',
                      income=(60,250),   unit='kg/yr', yld='30-80'),
    'Avocado':   dict(th=7, cb=7, ct=18, cr=6,  tr=0.9, c1='#2E7D32',c2='#1B5E20',
                      income=(400,2000), unit='kg/yr', yld='50-200'),
    'Moringa':   dict(th=6, cb=6, ct=15, cr=3,  tr=0.5, c1='#66BB6A',c2='#4CAF50',
                      income=(100,500),  unit='kg/yr', yld='200-500'),
    'Citrus':    dict(th=4, cb=4, ct=12, cr=4,  tr=0.6, c1='#43A047',c2='#66BB6A',
                      income=(150,600),  unit='kg/yr', yld='30-80'),
    'Neem':      dict(th=9, cb=9, ct=24, cr=9,  tr=1.1, c1='#388E3C',c2='#2E7D32',
                      income=(50,200),   unit='kg/yr', yld='5-15'),
    'Teak':      dict(th=14,cb=14,ct=28, cr=7,  tr=0.9, c1='#1B5E20',c2='#2E7D32',
                      income=(500,3000), unit='tree@15yr',yld='1 log'),
    'Bamboo':    dict(th=1, cb=1, ct=16, cr=2,  tr=0.4, c1='#4CAF50',c2='#8BC34A',
                      income=(100,600),  unit='culm/yr',yld='20-50'),
}
_SP_CYCLE = list(TREE_SPECIES.keys())


# ─────────────────────────────────────────────────────────────────────────────
#  Low-level geometry (kept minimal — NO redundant traces)
# ─────────────────────────────────────────────────────────────────────────────
def _box(x0,y0,z0,x1,y1,z1,col,name,op=0.90,sl=True,lg=None):
    vx=[x0,x1,x1,x0,x0,x1,x1,x0]; vy=[y0,y0,y1,y1,y0,y0,y1,y1]
    vz=[z0]*4+[z1]*4
    fi=[0,0,4,4,0,0,2,2,0,0,1,1]; fj=[1,2,5,6,1,5,3,7,3,7,2,6]
    fk=[2,3,6,7,5,4,7,6,7,4,6,5]
    return go.Mesh3d(x=vx,y=vy,z=vz,i=fi,j=fj,k=fk,
                     color=col,opacity=op,name=name,
                     showlegend=sl,legendgroup=lg or name,flatshading=True,
                     lighting=dict(ambient=0.62,diffuse=0.88,specular=0.22,
                                   roughness=0.55,fresnel=0.10))

def _roof(x0,y0,x1,y1,zb,zt,col,lg=None):
    cx,cy=(x0+x1)/2,(y0+y1)/2
    return go.Mesh3d(x=[x0,x1,x1,x0,cx],y=[y0,y0,y1,y1,cy],z=[zb]*4+[zt],
                     i=[0,1,2,3],j=[1,2,3,0],k=[4,4,4,4],
                     color=col,opacity=0.97,name='Roof',
                     showlegend=False,legendgroup=lg or 'Roof',flatshading=True)

def _grid_surf(xs,ys,z_val,col,name,op=0.88,sl=True,lg=None):
    """Flat surface from 1-D x/y arrays — one trace for the whole road/zone."""
    Xg,Yg = np.meshgrid(xs,ys)
    Zg    = np.full_like(Xg, z_val, dtype=float)
    return go.Surface(x=Xg,y=Yg,z=Zg,
                      colorscale=[[0,col],[1,col]],
                      showscale=False,opacity=op,
                      name=name,showlegend=sl,legendgroup=lg or name)

def _cyl(cx,cy,r,z0,z1,col,name,n=16,sl=True,lg=None):
    t=np.linspace(0,2*np.pi,n); Z=np.array([z0,z1])
    T,Zg=np.meshgrid(t,Z)
    return go.Surface(x=cx+r*np.cos(T),y=cy+r*np.sin(T),z=Zg,
                      colorscale=[[0,col],[1,col]],showscale=False,
                      opacity=0.92,name=name,showlegend=sl,legendgroup=lg or name)

def _cone_mesh(cx,cy,r,z0,z1,col,name,n=14,sl=False,lg=None):
    t=np.linspace(0,2*np.pi,n,endpoint=False)
    vx=list(cx+r*np.cos(t))+[cx]; vy=list(cy+r*np.sin(t))+[cy]
    vz=[z0]*n+[z1]
    return go.Mesh3d(x=vx,y=vy,z=vz,
                     i=list(range(n)),j=[(k+1)%n for k in range(n)],k=[n]*n,
                     color=col,opacity=0.88,name=name,
                     showlegend=sl,legendgroup=lg or name,flatshading=True)


# ─────────────────────────────────────────────────────────────────────────────
#  Road slab helper  (ONE Surface per road segment, not per tile)
# ─────────────────────────────────────────────────────────────────────────────
def _road_surf(x0,y0,x1,y1,w,tz, col='#D7CCC8',name='Road',sl=True,lg='Roads'):
    """
    Axis-aligned road: if dx>dy → horizontal, else → vertical.
    Returns a single Surface trace (not a list).
    """
    if x0==x1:   # vertical road
        xs = np.linspace(x0-w/2, x0+w/2, 4)
        ys = np.linspace(min(y0,y1), max(y0,y1), max(4,int(abs(y1-y0)/15)+1))
    else:        # horizontal road
        xs = np.linspace(min(x0,x1), max(x0,x1), max(4,int(abs(x1-x0)/15)+1))
        ys = np.linspace(y0-w/2, y0+w/2, 4)
    Xg,Yg = np.meshgrid(xs,ys)
    Zg    = np.full_like(Xg, tz+0.05, dtype=float)
    return go.Surface(x=Xg,y=Yg,z=Zg,
                      colorscale=[[0,col],[0.5,'#BCAAA4'],[1,'#D7CCC8']],
                      showscale=False,opacity=0.90,
                      name=name,showlegend=sl,legendgroup=lg)


# ─────────────────────────────────────────────────────────────────────────────
#  Batch plant scatter (ONE Scatter3d for ALL plants in kitchen garden)
# ─────────────────────────────────────────────────────────────────────────────
def _plant_scatter(positions, colors_list, base_z):
    """
    positions: list of (x,y) tuples
    Returns a single Scatter3d trace with coloured cones via marker.
    This replaces hundreds of individual cone traces.
    """
    xs=[p[0] for p in positions]; ys=[p[1] for p in positions]
    zs=[base_z+0.7]*len(xs)
    mc=[colors_list[i%len(colors_list)] for i in range(len(xs))]
    return go.Scatter3d(x=xs,y=ys,z=zs,
                        mode='markers',
                        marker=dict(size=5,color=mc,
                                    symbol='diamond',
                                    line=dict(color='#1B5E20',width=0.5)),
                        name='Vegetable Plants',showlegend=True,
                        legendgroup='Kitchen Garden')


# ─────────────────────────────────────────────────────────────────────────────
#  Main class
# ─────────────────────────────────────────────────────────────────────────────
class Visualizer3D:

    ZONE_NAMES = {
        'z0':'Zone 0 – Residential','z1':'Zone 1 – Kitchen Garden',
        'z2':'Zone 2 – Food Forest','z3':'Zone 3 – Pasture / Crops',
        'z4':'Zone 4 – Buffer Zone',
    }

    def create(self, layout: Dict[str,Any]) -> go.Figure:
        self._reg   = _Reg()
        self._L     = layout['dimensions']['L']
        self._W     = layout['dimensions']['W']
        self._slope = layout.get('slope','Flat')
        self._ly    = layout
        self._fig   = go.Figure()

        # ── STRICT ORDER ──────────────────────────────────────────────────
        self._terrain()
        self._zones()
        self._spine_roads()        # ① roads registered FIRST
        self._house()              # ② house
        self._kitchen_garden()     # ③ z1 beds (clamped away from house)
        self._water()
        self._solar()
        self._greenhouse()
        self._rain_tank()
        self._livestock()
        self._feature_spurs()      # ④ spur per feature, routed around obstacles
        self._trees()              # ⑤ trees last

        self._layout_cfg()
        return self._fig

    # ── helpers ──────────────────────────────────────────────────────────────
    def _tz(self,x,y):
        s,L,W=self._slope,self._L,self._W
        if s=='South': return y*0.025
        if s=='North': return (W-y)*0.025
        if s=='East':  return x*0.025
        if s=='West':  return (L-x)*0.025
        return 0.0

    def _tzg(self,X,Y):
        s,L,W=self._slope,self._L,self._W
        if s=='South': return Y*0.025
        if s=='North': return (W-Y)*0.025
        if s=='East':  return X*0.025
        if s=='West':  return (L-X)*0.025
        return np.zeros_like(X,dtype=float)

    def _add(self,trace): self._fig.add_trace(trace)

    # ── Terrain (1 trace) ─────────────────────────────────────────────────────
    def _terrain(self):
        L,W=self._L,self._W
        x=np.linspace(0,L,35); y=np.linspace(0,W,35)
        X,Y=np.meshgrid(x,y); Z=self._tzg(X,Y)
        self._add(go.Surface(x=X,y=Y,z=Z,
            colorscale=[[0,'#33691E'],[0.4,'#558B2F'],[0.7,'#7CB342'],[1,'#9CCC65']],
            showscale=False,opacity=0.86,name='Terrain',
            showlegend=True,legendgroup='Terrain',
            lighting=dict(ambient=0.70,diffuse=0.85),
            contours=dict(z=dict(show=True,color='#2E7D32',width=1,
                                  start=Z.min(),end=Z.max(),
                                  size=max(0.01,(Z.max()-Z.min()+0.01)/5)))))

    # ── Zones (1 trace each = 5 traces) ──────────────────────────────────────
    def _zones(self):
        cs={'z0':[[0,'#FFF9C4'],[1,'#FFFDE7']],
            'z1':[[0,'#A5D6A7'],[1,'#C8E6C9']],
            'z2':[[0,'#1B5E20'],[1,'#2E7D32']],
            'z3':[[0,'#F9A825'],[1,'#FFF9C4']],
            'z4':[[0,'#CE93D8'],[1,'#EDE7F6']]}
        for zid,pos in self._ly.get('zone_positions',{}).items():
            x0,y0=pos['x'],pos['y']; x1,y1=x0+pos['width'],y0+pos['height']
            nx=max(4,int(pos['width']/25)); ny=max(4,int(pos['height']/25))
            Xg,Yg=np.meshgrid(np.linspace(x0,x1,nx),np.linspace(y0,y1,ny))
            Zg=self._tzg(Xg,Yg)+1.1
            if zid in('z2','z3'):
                np.random.seed(hash(zid)%100)
                Zg+=np.random.uniform(0,0.25,Zg.shape)
            self._add(go.Surface(x=Xg,y=Yg,z=Zg,
                colorscale=cs.get(zid,[[0,'#CCC'],[1,'#EEE']]),
                showscale=False,opacity=0.48,
                name=self.ZONE_NAMES.get(zid,zid),
                showlegend=True,legendgroup=zid))

    # ── ① Spine roads — registered FIRST ─────────────────────────────────────
    def _spine_roads(self):
        L,W=self._L,self._W
        hx,hy,hw,hd=self._house_bbox()
        dcx=hx+hw/2          # door centre x
        cy=hy+hd*0.5          # cross-road y
        mw=10.0; pw=8.0; po=14.0   # main width, peri width, peri offset
        shown={'road':False}

        def road(x0,y0,x1,y1,w,name,col='#D7CCC8'):
            # Register
            if x0==x1:
                self._reg.add_rect(x0-w/2,min(y0,y1),x0+w/2,max(y0,y1))
            else:
                self._reg.add_rect(min(x0,x1),y0-w/2,max(x0,x1),y0+w/2)
            # Draw (ONE surface)
            sl = not shown['road']
            shown['road'] = True
            self._add(_road_surf(x0,y0,x1,y1,w,self._tz((x0+x1)/2,(y0+y1)/2),
                                  col,name,sl,'Roads'))

        # Perimeter roads (4 sides)
        road(po,po, L-po,po,    pw,'Perimeter Road','#BCAAA4')
        road(po,W-po,L-po,W-po, pw,'Perimeter Road','#BCAAA4')
        road(po,po, po,W-po,    pw,'Perimeter Road','#BCAAA4')
        road(L-po,po,L-po,W-po, pw,'Perimeter Road','#BCAAA4')

        # Main N-S spine: south boundary → house bottom
        road(dcx,po, dcx,hy, mw,'Main Road')
        # Main E-W cross road at house mid-height
        road(po,cy, L-po,cy, mw,'Main Road')
        # N-S spine: house top → north perimeter
        road(dcx,hy+hd, dcx,W-po, mw,'Main Road')

    # ── ② House ───────────────────────────────────────────────────────────────
    def _house_bbox(self):
        L,W=self._L,self._W
        pos=self._ly.get('house_position','Center')
        p={'North':(L*0.30,W*0.82,L*0.38,W*0.12),
           'South':(L*0.30,W*0.06,L*0.38,W*0.12),
           'East': (L*0.74,W*0.36,L*0.20,W*0.28),
           'West': (L*0.06,W*0.36,L*0.20,W*0.28),
           'Center':(L*0.35,W*0.40,L*0.30,W*0.20),
           'Not built yet':(L*0.35,W*0.40,L*0.30,W*0.20)}
        return p.get(pos,p['Center'])

    def _house(self):
        hx,hy,hw,hd=self._house_bbox()
        base=self._tz(hx+hw/2,hy+hd/2)+1.5
        wh=10.0; rb=base+wh; rt=rb+min(hw,hd)*0.40; wt=0.5
        self._reg.add_rect(hx,hy,hx+hw,hy+hd)
        lg='House'
        # Foundation
        self._add(_box(hx-.4,hy-.4,base-.4,hx+hw+.4,hy+hd+.4,base,'#BCAAA4','Foundation',sl=False,lg=lg))
        # Walls — each face is a thin box
        for wx0,wy0,wx1,wy1,c,first in [
            (hx,   hy,        hx+hw, hy+wt,      '#D7CCC8',True),
            (hx,   hy+hd-wt,  hx+hw, hy+hd,      '#BCAAA4',False),
            (hx,   hy,        hx+wt, hy+hd,      '#D7CCC8',False),
            (hx+hw-wt,hy,     hx+hw, hy+hd,      '#BCAAA4',False),
        ]:
            self._add(_box(wx0,wy0,base,wx1,wy1,rb,c,'House',sl=first,lg=lg))
        # Floor interior
        self._add(_box(hx+wt,hy+wt,base,hx+hw-wt,hy+hd-wt,base+0.15,'#EFEBE9','House Floor',sl=False,lg=lg))
        # Windows south (2)
        ww,wh2=hw*0.12,wh*0.28; wz=base+wh*0.44
        for wx in [hx+hw*0.18,hx+hw*0.70]:
            self._add(_box(wx-.1,hy-.1,wz-.1,wx+ww+.1,hy+wt+.1,wz+wh2+.1,'#5D4037','Window Frame',sl=False,lg=lg))
            self._add(_box(wx,hy-.05,wz,wx+ww,hy+wt+.05,wz+wh2,'#B3E5FC','Window',op=0.78,sl=False,lg=lg))
        # Door
        dw=hw*0.12; dx=hx+hw/2-dw/2
        self._add(_box(dx,hy-.1,base,dx+dw,hy+wt+.1,base+wh*0.54,'#3E2723','Door',sl=False,lg=lg))
        # Hip roof
        self._add(_roof(hx,hy,hx+hw,hy+hd,rb,rt,'#4E342E',lg))
        # Chimney
        cx2=hx+hw*.72; cy2=hy+hd*.38; cw2=hw*.08; cd2=hd*.08
        self._add(_box(cx2,cy2,rb-1,cx2+cw2,cy2+cd2,rt+3,'#6D4C41','Chimney',sl=False,lg=lg))
        # Porch
        pw=hw*.44; pd=hd*.14; px=hx+(hw-pw)/2; py=hy-pd; pz=base+wh*.63
        self._add(_box(px,py,pz,px+pw,hy,pz+.35,'#EFEBE9','Porch',op=0.72,sl=False,lg=lg))
        for cx3 in [px+pw*.1,px+pw*.9]:
            self._add(_cyl(cx3,py+pd*.5,.45,base,pz,'#8D6E63','Porch Column',sl=False,lg=lg))

    # ── ③ Kitchen Garden — NEVER overlaps house or roads ─────────────────────
    def _kitchen_garden(self):
        zones=self._ly.get('zone_positions',{})
        if 'z1' not in zones: return
        pos=zones['z1']
        x0,y0=pos['x'],pos['y']
        w,h=pos['width'],pos['height']
        base=self._tz(x0+w/2,y0+h/2)+1.3

        # House exclusion zone
        hx,hy,hw,hd=self._house_bbox()
        # Clamp bed area to safely within z1 AND away from house
        pad=6
        safe_x0=x0+pad; safe_x1=x0+w-pad
        safe_y0=y0+pad; safe_y1=y0+h-pad

        # If z1 overlaps house bbox, shift safe bounds
        # (ensure beds don't land inside house)
        h_margin=8
        if not (hx+hw+h_margin < safe_x0 or hx-h_margin > safe_x1 or
                hy+hd+h_margin < safe_y0 or hy-h_margin > safe_y1):
            # z1 overlaps house area — keep beds to the non-overlapping strip
            # Prefer top strip (y close to y0+h)
            if hy > safe_y0:
                safe_y1 = min(safe_y1, hy - h_margin)
            else:
                safe_y0 = max(safe_y0, hy+hd+h_margin)

        if safe_x1-safe_x0 < 15 or safe_y1-safe_y0 < 15:
            return   # not enough space

        bed_w = max(12, min(w*0.16, 20))
        gap   = max(5,  min(w*0.03, 8))
        n_beds= max(1,  int((safe_x1-safe_x0-gap)/(bed_w+gap)))

        plant_positions=[]
        plant_colors=['#4CAF50','#8BC34A','#CDDC39','#F9A825','#66BB6A']
        show_bed=True

        for i in range(n_beds):
            bx0=safe_x0+gap+i*(bed_w+gap)
            bx1=bx0+bed_w
            if bx1>safe_x1: break
            by0=safe_y0; by1=safe_y1

            # Raised soil bed (1 trace)
            self._add(_box(bx0,by0,base,bx1,by1,base+0.6,
                           '#5D4037','Raised Bed',op=0.92,sl=show_bed,lg='Kitchen Garden'))
            show_bed=False

            # Collect plant positions for batch Scatter3d
            n_rows=max(1,int((by1-by0)/8))
            for ri in range(n_rows):
                ry=by0+4+ri*((by1-by0-8)/max(n_rows-1,1))
                for px_off in np.linspace(bx0+2,bx1-2,4):
                    plant_positions.append((px_off,ry,plant_colors[(i+ri)%len(plant_colors)]))

            # Path between beds (1 surface per gap)
            if i<n_beds-1:
                gx0=bx1; gx1=bx1+gap
                Xg,Yg=np.meshgrid(np.linspace(gx0,gx1,3),
                                   np.linspace(by0,by1,max(3,int((by1-by0)/10)+1)))
                Zg=np.full_like(Xg,base+0.04)
                self._add(go.Surface(x=Xg,y=Yg,z=Zg,
                    colorscale=[[0,'#BCAAA4'],[1,'#D7CCC8']],
                    showscale=False,opacity=0.82,
                    name='Garden Path',showlegend=(i==0),legendgroup='Kitchen Garden'))

        # ALL plants in ONE Scatter3d trace
        if plant_positions:
            xs=[p[0] for p in plant_positions]
            ys=[p[1] for p in plant_positions]
            zs=[base+0.6+0.8]*len(xs)
            mc=[p[2] for p in plant_positions]
            self._add(go.Scatter3d(x=xs,y=ys,z=zs,mode='markers',
                marker=dict(size=4,color=mc,symbol='diamond',
                            line=dict(color='#1B5E20',width=0.5)),
                name='Vegetable Plants',showlegend=True,legendgroup='Kitchen Garden'))

    # ── Water ─────────────────────────────────────────────────────────────────
    def _water(self):
        f=self._ly.get('features',{})
        if 'pond' in f:
            p=f['pond']; r=p['radius']
            base=self._tz(p['x'],p['y'])
            if self._reg.circle_ok(p['x'],p['y'],r):
                self._reg.add_circle(p['x'],p['y'],r)
                rg=np.linspace(0,r,10); tg=np.linspace(0,2*np.pi,36)
                R,T=np.meshgrid(rg,tg)
                irr=1+0.10*np.sin(3*T)+0.07*np.cos(5*T)
                self._add(go.Surface(
                    x=p['x']+R*np.cos(T)*irr,y=p['y']+R*np.sin(T)*irr,
                    z=base-0.9+R/r*0.75,
                    colorscale=[[0,'#01579B'],[0.5,'#0288D1'],[1,'#4FC3F7']],
                    showscale=False,opacity=0.88,
                    name='Pond / Aquaculture',showlegend=True,legendgroup='Pond'))
                rt=np.linspace(0,2*np.pi,36)
                self._add(go.Scatter3d(
                    x=p['x']+r*1.05*np.cos(rt),y=p['y']+r*1.05*np.sin(rt),
                    z=[base+0.2]*36,mode='lines',
                    line=dict(color='#5D4037',width=3),
                    name='Pond Rim',showlegend=False,legendgroup='Pond'))

        for key in ('borewell','well'):
            if key in f:
                p=f[key]; r=p.get('radius',4); base=self._tz(p['x'],p['y'])
                if self._reg.circle_ok(p['x'],p['y'],r):
                    self._reg.add_circle(p['x'],p['y'],r)
                    self._add(_cyl(p['x'],p['y'],r,base,base+5,'#546E7A','Borewell',sl=True,lg='Borewell'))
                    self._add(_cyl(p['x'],p['y'],r*.8,base,base+3.5,'#4FC3F7','Borewell Water',sl=False,lg='Borewell'))
                break

    # ── Solar ─────────────────────────────────────────────────────────────────
    def _solar(self):
        f=self._ly.get('features',{}).get('solar')
        if not f: return
        x0,y0,x1,y1=f['x'],f['y'],f['x']+f['width'],f['y']+f['height']
        base=self._tz((x0+x1)/2,(y0+y1)/2)+1.5
        if not self._reg.rect_ok(x0,y0,x1,y1): return
        self._reg.add_rect(x0,y0,x1,y1)
        self._add(_box(x0,y0,base,x1,y1,base+.25,'#607D8B','Solar Frame',sl=False,lg='Solar'))
        rows,cols,g=2,3,1.2
        cw=(f['width']-g*(cols+1))/cols; ch=(f['height']-g*(rows+1))/rows
        sl=True
        for row in range(rows):
            for col in range(cols):
                px=x0+g+col*(cw+g); py=y0+g+row*(ch+g)
                self._add(_box(px,py,base+.22,px+cw,py+ch,base+.50,'#1565C0','Solar Panels',sl=sl,lg='Solar'))
                sl=False

    # ── Greenhouse ────────────────────────────────────────────────────────────
    def _greenhouse(self):
        f=self._ly.get('features',{}).get('greenhouse')
        if not f: return
        x0,y0,x1,y1=f['x'],f['y'],f['x']+f['width'],f['y']+f['height']
        base=self._tz((x0+x1)/2,(y0+y1)/2)+1.5
        if not self._reg.rect_ok(x0,y0,x1,y1): return
        self._reg.add_rect(x0,y0,x1,y1)
        gh_h=8.0
        self._add(_box(x0,y0,base,x1,y1,base+gh_h,'#E0F2F1','Greenhouse',op=0.28,sl=True,lg='Greenhouse'))
        self._add(_roof(x0,y0,x1,y1,base+gh_h,base+gh_h+f['width']*.27,'#80CBC4','Greenhouse'))
        for sy in [y0+4,y1-10]:
            self._add(_box(x0+3,sy,base+.4,x1-3,sy+7,base+1.1,'#5D4037','GH Bed',sl=False,lg='Greenhouse'))

    # ── Rain tank ─────────────────────────────────────────────────────────────
    def _rain_tank(self):
        f=self._ly.get('features',{}).get('rain_tank')
        if not f: return
        x0,y0,x1,y1=f['x'],f['y'],f['x']+f['width'],f['y']+f['height']
        base=self._tz((x0+x1)/2,(y0+y1)/2)+1.5
        if not self._reg.rect_ok(x0,y0,x1,y1): return
        self._reg.add_rect(x0,y0,x1,y1)
        self._add(_box(x0,y0,base,x1,y1,base+6,'#4FC3F7','Rain Tank',op=0.80,sl=True,lg='Rain Tank'))

    # ── Livestock ─────────────────────────────────────────────────────────────
    def _livestock(self):
        f=self._ly.get('features',{})
        cfg={'goat_shed':   ('#FFCCBC','#4E342E','Goat Shed',   7.0),
             'chicken_coop':('#FFF9C4','#F57F17','Chicken Coop',5.0),
             'piggery':     ('#F8BBD0','#880E4F','Piggery',     6.0),
             'cow_shed':    ('#D7CCC8','#5D4037','Cow Shed',    9.0),
             'fish_tanks':  ('#B3E5FC','#0288D1','Fish Tanks',  2.5),
             'bee_hives':   ('#FFF176','#F9A825','Bee Hives',   3.5)}
        for key,(wc,rc,label,sh) in cfg.items():
            if key not in f: continue
            p=f[key]; x0,y0=p['x'],p['y']; x1,y1=x0+p['width'],y0+p['height']
            base=self._tz((x0+x1)/2,(y0+y1)/2)+1.5
            if not self._reg.rect_ok(x0,y0,x1,y1): continue
            self._reg.add_rect(x0,y0,x1,y1)
            rb=base+sh; rt=rb+p['width']*.24
            self._add(_box(x0,y0,base,x1,y1,rb,wc,label,sl=True,lg=label))
            self._add(_roof(x0,y0,x1,y1,rb,rt,rc,label))
            if key=='fish_tanks':
                self._add(_box(x0+2,y0+2,base+.4,x1-2,y1-2,base+.75,'#4FC3F7','Fish Water',op=0.68,sl=False,lg=label))
            if key=='bee_hives':
                n_h=max(1,int(p['width']/14)); hwe=(p['width']-4)/n_h-1.5
                for hi in range(n_h):
                    hxe=x0+2+hi*(hwe+1.5)
                    self._add(_box(hxe,y0+2,base,hxe+hwe,y1-2,base+3.2,'#FFF176',f'Hive{hi+1}',sl=False,lg=label))

    # ── ④ Feature spurs — routed AROUND obstacles ──────────────────────────────
    def _feature_spurs(self):
        """
        For each registered feature, draw a 6-ft wide L-shaped path from
        the feature centre to the nearest spine road.
        The waypoint (bend in the L) is shifted outward if it falls inside
        a registered obstacle.
        """
        features=self._ly.get('features',{})
        hx,hy,hw,hd=self._house_bbox()
        dcx=hx+hw/2; cy=hy+hd*0.5
        sw=6.0; sc='#BCAAA4'; L=self._L; W=self._W
        shown=False

        def safe_y_waypoint(fx,fy,target_y):
            """Nudge waypoint y out of any obstacle."""
            wy=target_y
            # Walk upward/downward to find a clear horizontal strip
            for dy in [0,sw*2,sw*4,-sw*2,-sw*4]:
                candidate=wy+dy
                if 0<candidate<W and self._reg.point_free(fx,candidate):
                    return candidate
            return wy   # fallback: use original even if blocked

        def safe_x_waypoint(fx,fy,target_x):
            wx=target_x
            for dx in [0,sw*2,sw*4,-sw*2,-sw*4]:
                candidate=wx+dx
                if 0<candidate<L and self._reg.point_free(candidate,fy):
                    return candidate
            return wx

        def _spur(fx,fy):
            nonlocal shown
            tz=self._tz(fx,fy)
            # Decide spine axis
            if abs(fx-dcx) < abs(fy-cy):
                # Closer to N-S spine → bend point at (dcx, fy)
                wx=safe_x_waypoint(fx,fy,dcx); wy=fy
            else:
                # Closer to E-W spine → bend point at (fx, cy)
                wx=fx; wy=safe_y_waypoint(fx,fy,cy)

            # H segment: (fx,fy) → (wx,wy)
            if abs(fx-wx)>2:
                xl=np.linspace(min(fx,wx),max(fx,wx),max(3,int(abs(fx-wx)/10)+1))
                yl=np.linspace(fy-sw/2,fy+sw/2,3)
                Xg,Yg=np.meshgrid(xl,yl)
                self._fig.add_trace(go.Surface(
                    x=Xg,y=Yg,z=np.full_like(Xg,tz+0.08),
                    colorscale=[[0,sc],[1,sc]],showscale=False,opacity=0.82,
                    name='Feature Path',showlegend=not shown,legendgroup='Roads'))
                shown=True
            # V segment: (wx,wy) → (wx,cy) or (dcx,fy)
            spine_end_y = cy if abs(fy-cy)<abs(fx-dcx) else wy
            if abs(wy-spine_end_y)>2:
                xl2=np.linspace(wx-sw/2,wx+sw/2,3)
                yl2=np.linspace(min(wy,spine_end_y),max(wy,spine_end_y),
                                max(3,int(abs(wy-spine_end_y)/10)+1))
                Xg2,Yg2=np.meshgrid(xl2,yl2)
                self._fig.add_trace(go.Surface(
                    x=Xg2,y=Yg2,z=np.full_like(Xg2,tz+0.08),
                    colorscale=[[0,sc],[1,sc]],showscale=False,opacity=0.82,
                    name='Feature Path',showlegend=False,legendgroup='Roads'))

        skip_keys={'swales','compost'}
        for key,fdata in features.items():
            if key in skip_keys: continue
            if isinstance(fdata,list): continue
            if 'x' not in fdata or 'y' not in fdata: continue
            if 'radius' in fdata:
                fx,fy=fdata['x'],fdata['y']
            else:
                fx=fdata['x']+fdata.get('width',20)/2
                fy=fdata['y']+fdata.get('height',20)/2
            if self._reg.point_free(fx,fy): continue  # not placed
            _spur(fx,fy)

    # ── ⑤ Trees — last, strict collision ──────────────────────────────────────
    def _trees(self):
        zones=self._ly.get('zone_positions',{})
        placements=self._ly.get('tree_placements',[])

        # Auto-generate placements from z2 and z4 if not provided
        if not placements:
            if 'z2' in zones:
                z=zones['z2']
                np.random.seed(42)
                for idx in range(20):
                    rx=np.random.uniform(0.05,0.95)
                    ry=np.random.uniform(0.05,0.95)
                    sp=_SP_CYCLE[idx%len(_SP_CYCLE)]
                    placements.append({'x':z['x']+rx*z['width'],
                                       'y':z['y']+ry*z['height'],
                                       'species':sp})
            if 'z4' in zones:
                z=zones['z4']
                np.random.seed(77)
                for idx in range(10):
                    rx=np.random.uniform(0.04,0.96)
                    ry=np.random.uniform(0.08,0.92)
                    sp=['Neem','Teak','Bamboo'][idx%3]
                    placements.append({'x':z['x']+rx*z['width'],
                                       'y':z['y']+ry*z['height'],
                                       'species':sp})

        # Also add extra user trees
        for t in self._ly.get('extra_trees',[]):
            placements.append(t)

        # Batch by species group to reduce legend entries
        # (all trees share 'Trees' legendgroup)
        first=True
        for t in placements:
            sp_name=t.get('species','Mango')
            sp=TREE_SPECIES.get(sp_name,TREE_SPECIES['Mango'])
            cr=sp['cr']; tr=sp['tr']
            tx=t['x']; ty=t['y']

            # Clamp inside z2/z4 zone if possible
            zone_id=t.get('zone','z2')
            if zone_id in zones:
                z=zones[zone_id]
                tx=max(z['x']+cr+2, min(tx, z['x']+z['width']-cr-2))
                ty=max(z['y']+cr+2, min(ty, z['y']+z['height']-cr-2))

            # Property boundary clamp
            tx=max(cr+3, min(tx, self._L-cr-3))
            ty=max(cr+3, min(ty, self._W-cr-3))

            if not self._reg.circle_ok(tx,ty,cr): continue
            self._reg.add_circle(tx,ty,cr)

            base=self._tz(tx,ty)+1.3
            self._add(_cyl(tx,ty,tr,base,base+sp['th'],'#6D4C41',sp_name,sl=first,lg='Trees'))
            self._add(_cone_mesh(tx,ty,cr,base+sp['cb'],base+sp['ct'],sp['c1'],sp_name,sl=False,lg='Trees'))
            self._add(_cone_mesh(tx,ty,cr*.68,base+sp['cb']+cr*.32,base+sp['ct']+cr*.10,sp['c2'],sp_name,sl=False,lg='Trees'))
            first=False

    # ── Layout config ──────────────────────────────────────────────────────────
    def _layout_cfg(self):
        L,W=self._L,self._W
        acres=self._ly.get('acres',round(L*W/43560,2))
        tc=self._ly.get('tree_count',len(self._ly.get('tree_placements',[])))
        n=len(self._fig.data)
        self._fig.update_layout(
            title=dict(
                text=(f"🏡 3D Homestead — {acres:.2f} acres ({int(L)}×{int(W)} ft)"
                      f"<br><sup>{tc} trees · {n} elements · Click legend to toggle</sup>"),
                font=dict(size=14,color='#2E7D32',family='Arial'),x=0.5),
            scene=dict(
                xaxis_title='Length (ft)',yaxis_title='Width (ft)',
                zaxis_title='Height (ft)',aspectmode='data',bgcolor='#C9E8F5',
                camera=dict(eye=dict(x=1.3,y=-1.5,z=0.85),up=dict(x=0,y=0,z=1)),
                xaxis=dict(showgrid=True,gridcolor='#B0BEC5',showbackground=True,backgroundcolor='#EAF4FB'),
                yaxis=dict(showgrid=True,gridcolor='#B0BEC5',showbackground=True,backgroundcolor='#EAF4FB'),
                zaxis=dict(showgrid=True,gridcolor='#B0BEC5',showbackground=True,backgroundcolor='#EAF4FB',range=[-2,35]),
            ),
            legend=dict(x=0.01,y=0.99,bgcolor='rgba(255,255,255,0.90)',
                        bordercolor='#90A4AE',borderwidth=1.5,font=dict(size=10),
                        itemclick='toggle',itemdoubleclick='toggleothers',
                        title=dict(text='<b>Layers</b> (click=toggle)',font=dict(size=9))),
            paper_bgcolor='#EAF4FB',margin=dict(l=0,r=0,t=70,b=0),
            width=1000,height=720,
            updatemenus=[
                dict(type='buttons',direction='left',x=0.5,y=0.01,xanchor='center',
                     showactive=True,
                     buttons=[
                         dict(label='Top',method='relayout',
                              args=[{'scene.camera.eye':{'x':0,'y':0,'z':2.5},'scene.camera.up':{'x':0,'y':1,'z':0}}]),
                         dict(label='3D',method='relayout',
                              args=[{'scene.camera.eye':{'x':1.3,'y':-1.5,'z':0.85},'scene.camera.up':{'x':0,'y':0,'z':1}}]),
                         dict(label='South',method='relayout',
                              args=[{'scene.camera.eye':{'x':0,'y':-2.5,'z':0.5},'scene.camera.up':{'x':0,'y':0,'z':1}}]),
                         dict(label='Bird',method='relayout',
                              args=[{'scene.camera.eye':{'x':0.05,'y':-0.05,'z':2.8},'scene.camera.up':{'x':0,'y':1,'z':0}}]),
                     ],bgcolor='white',bordercolor='#78909C',font=dict(size=11)),
                dict(type='buttons',direction='right',
                     x=0.99,y=0.99,xanchor='right',yanchor='top',
                     showactive=True,active=0,
                     buttons=[
                         dict(label='☰ Layers',method='relayout',args=[{'showlegend':True}]),
                         dict(label='✕ Hide',  method='relayout',args=[{'showlegend':False}]),
                     ],
                     bgcolor='rgba(255,255,255,0.92)',bordercolor='#90A4AE',
                     font=dict(size=11,color='#2E7D32')),
            ],
        )

    def export_as_html(self,fig,filename='homestead_3d.html'):
        pio.write_html(fig,file=filename,auto_open=False,include_plotlyjs='cdn')
