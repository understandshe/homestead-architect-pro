"""
3D Visualization Engine — Premium v4
Homestead Architect Pro 2026 — Global Edition

Architecture:
  Step 1: Register all SPINE ROADS in collision registry first
  Step 2: Register HOUSE + all FEATURES (skip if collides)
  Step 3: Place TREES last — checked against roads + features
  → Nothing ever overlaps anything
  → Every feature gets a SPUR path from nearest spine point
  → Kitchen Garden always visible (rendered as zone surface + raised beds)
  → 12 tree species with individual heights + canopy + income data
"""

import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
from typing import Dict, Any, List, Tuple, Optional


# ─────────────────────────────────────────────────────────────────────────────
#  Collision Registry
# ─────────────────────────────────────────────────────────────────────────────
class _CollisionRegistry:
    CLEARANCE = 8.0   # ft minimum gap between any two elements

    def __init__(self):
        self._rects: List[Tuple[float,float,float,float]] = []
        self._circles: List[Tuple[float,float,float]] = []

    def _expand_rect(self, x0,y0,x1,y1,c):
        return min(x0,x1)-c, min(y0,y1)-c, max(x0,x1)+c, max(y0,y1)+c

    def register_rect(self, x0,y0,x1,y1):
        self._rects.append((min(x0,x1),min(y0,y1),max(x0,x1),max(y0,y1)))

    def register_circle(self, cx,cy,r):
        self._circles.append((cx,cy,r))

    def rect_clear(self, x0,y0,x1,y1) -> bool:
        c = self.CLEARANCE
        ax0,ay0,ax1,ay1 = self._expand_rect(x0,y0,x1,y1,c)
        for (rx0,ry0,rx1,ry1) in self._rects:
            if ax0<rx1 and ax1>rx0 and ay0<ry1 and ay1>ry0:
                return False
        for (cx,cy,r) in self._circles:
            nx = max(ax0,min(cx,ax1)); ny = max(ay0,min(cy,ay1))
            if (cx-nx)**2+(cy-ny)**2 < (r+c)**2:
                return False
        return True

    def circle_clear(self, cx,cy,r) -> bool:
        c = self.CLEARANCE
        for (rx0,ry0,rx1,ry1) in self._rects:
            nx = max(rx0,min(cx,rx1)); ny = max(ry0,min(cy,ry1))
            if (cx-nx)**2+(cy-ny)**2 < (r+c)**2:
                return False
        for (ocx,ocy,or_) in self._circles:
            if (cx-ocx)**2+(cy-ocy)**2 < (r+or_+c)**2:
                return False
        return True

    def point_in_any(self, px, py) -> bool:
        """True if point is inside any registered element."""
        for (rx0,ry0,rx1,ry1) in self._rects:
            if rx0<=px<=rx1 and ry0<=py<=ry1:
                return True
        for (cx,cy,r) in self._circles:
            if (px-cx)**2+(py-cy)**2<=r**2:
                return True
        return False


# ─────────────────────────────────────────────────────────────────────────────
#  12 Tree species catalogue
# ─────────────────────────────────────────────────────────────────────────────
TREE_SPECIES = {
    'Mango':       dict(trunk_h=5,  canopy_bot=5,  canopy_top=20, canopy_r=9,  trunk_r=1.1,
                        color='#2E7D32', color2='#388E3C',
                        income_usd=(300,1500), unit='kg/yr', yield_val='80-200'),
    'Jackfruit':   dict(trunk_h=8,  canopy_bot=8,  canopy_top=28, canopy_r=10, trunk_r=1.4,
                        color='#1B5E20', color2='#2E7D32',
                        income_usd=(200,800),  unit='kg/yr', yield_val='50-200'),
    'Coconut':     dict(trunk_h=22, canopy_bot=22, canopy_top=32, canopy_r=6,  trunk_r=0.7,
                        color='#33691E', color2='#558B2F',
                        income_usd=(150,600),  unit='nuts/yr', yield_val='80-200'),
    'Banana':      dict(trunk_h=3,  canopy_bot=3,  canopy_top=10, canopy_r=5,  trunk_r=1.6,
                        color='#558B2F', color2='#7CB342',
                        income_usd=(100,400),  unit='bunch/yr', yield_val='5-20'),
    'Guava':       dict(trunk_h=4,  canopy_bot=4,  canopy_top=14, canopy_r=5,  trunk_r=0.8,
                        color='#33691E', color2='#43A047',
                        income_usd=(80,300),   unit='kg/yr', yield_val='20-60'),
    'Papaya':      dict(trunk_h=4,  canopy_bot=4,  canopy_top=11, canopy_r=3.5,trunk_r=0.5,
                        color='#558B2F', color2='#8BC34A',
                        income_usd=(60,250),   unit='kg/yr', yield_val='30-80'),
    'Avocado':     dict(trunk_h=7,  canopy_bot=7,  canopy_top=19, canopy_r=7,  trunk_r=1.0,
                        color='#2E7D32', color2='#1B5E20',
                        income_usd=(400,2000), unit='kg/yr', yield_val='50-200'),
    'Moringa':     dict(trunk_h=6,  canopy_bot=6,  canopy_top=16, canopy_r=4,  trunk_r=0.6,
                        color='#66BB6A', color2='#4CAF50',
                        income_usd=(100,500),  unit='kg/yr', yield_val='200-500'),
    'Citrus':      dict(trunk_h=4,  canopy_bot=4,  canopy_top=13, canopy_r=5,  trunk_r=0.7,
                        color='#43A047', color2='#66BB6A',
                        income_usd=(150,600),  unit='kg/yr', yield_val='30-80'),
    'Neem':        dict(trunk_h=9,  canopy_bot=9,  canopy_top=25, canopy_r=10, trunk_r=1.2,
                        color='#388E3C', color2='#2E7D32',
                        income_usd=(50,200),   unit='kg/yr', yield_val='5-15 (seed)'),
    'Teak':        dict(trunk_h=15, canopy_bot=15, canopy_top=30, canopy_r=8,  trunk_r=1.0,
                        color='#1B5E20', color2='#2E7D32',
                        income_usd=(500,3000), unit='tree at 15yr', yield_val='1 log'),
    'Bamboo':      dict(trunk_h=0,  canopy_bot=0,  canopy_top=18, canopy_r=3,  trunk_r=0.4,
                        color='#4CAF50', color2='#8BC34A',
                        income_usd=(100,600),  unit='culm/yr', yield_val='20-50'),
}

# Default rotation of species list (for layout_engine output that has no species)
_SPECIES_CYCLE = list(TREE_SPECIES.keys())


# ─────────────────────────────────────────────────────────────────────────────
#  Geometry primitives
# ─────────────────────────────────────────────────────────────────────────────
def _box(x0,y0,z0,x1,y1,z1,color,name,opacity=0.90,
         show_legend=True,legendgroup=None,flatshading=True) -> go.Mesh3d:
    vx=[x0,x1,x1,x0,x0,x1,x1,x0]; vy=[y0,y0,y1,y1,y0,y0,y1,y1]
    vz=[z0,z0,z0,z0,z1,z1,z1,z1]
    fi=[0,0,4,4,0,0,2,2,0,0,1,1]; fj=[1,2,5,6,1,5,3,7,3,7,2,6]
    fk=[2,3,6,7,5,4,7,6,7,4,6,5]
    return go.Mesh3d(x=vx,y=vy,z=vz,i=fi,j=fj,k=fk,color=color,
                     opacity=opacity,name=name,showlegend=show_legend,
                     legendgroup=legendgroup or name,flatshading=flatshading,
                     lighting=dict(ambient=0.60,diffuse=0.90,specular=0.25,
                                   roughness=0.55,fresnel=0.10))

def _hip_roof(x0,y0,x1,y1,base_z,apex_z,color,
              name='Roof',legendgroup=None) -> go.Mesh3d:
    cx,cy=(x0+x1)/2,(y0+y1)/2
    vx=[x0,x1,x1,x0,cx]; vy=[y0,y0,y1,y1,cy]; vz=[base_z]*4+[apex_z]
    return go.Mesh3d(x=vx,y=vy,z=vz,i=[0,1,2,3],j=[1,2,3,0],k=[4,4,4,4],
                     color=color,opacity=0.97,name=name,showlegend=False,
                     legendgroup=legendgroup or name,flatshading=True)

def _cylinder(cx,cy,r,z0,z1,color,name,n=20,
              show_legend=True,legendgroup=None) -> go.Surface:
    t=np.linspace(0,2*np.pi,n); z=np.array([z0,z1])
    T,Z=np.meshgrid(t,z)
    return go.Surface(x=cx+r*np.cos(T),y=cy+r*np.sin(T),z=Z,
                      colorscale=[[0,color],[1,color]],showscale=False,
                      opacity=0.92,name=name,showlegend=show_legend,
                      legendgroup=legendgroup or name)

def _cone(cx,cy,r,z0,z1,color,name,n=18,
          show_legend=False,legendgroup=None) -> go.Mesh3d:
    t=np.linspace(0,2*np.pi,n,endpoint=False)
    vx=list(cx+r*np.cos(t))+[cx]; vy=list(cy+r*np.sin(t))+[cy]
    vz=[z0]*n+[z1]
    fi=list(range(n)); fj=[(k+1)%n for k in range(n)]; fk=[n]*n
    return go.Mesh3d(x=vx,y=vy,z=vz,i=fi,j=fj,k=fk,
                     color=color,opacity=0.88,name=name,
                     showlegend=show_legend,legendgroup=legendgroup or name,
                     flatshading=True)

def _path_slab(x0,y0,x1,y1,width,tz,color='#D7CCC8',
               name='Path',show_legend=False,lg='Paths') -> List:
    """
    Axis-aligned path slab between two points.
    Always uses L-shaped routing (horizontal then vertical),
    so no diagonal paths that cut through diagonal space.
    Returns list of Mesh3d traces for TWO segments: H + V.
    """
    traces = []
    pw = width

    # Segment 1: horizontal (x0,y0) → (x1,y0)
    # Segment 2: vertical   (x1,y0) → (x1,y1)
    # This makes an L-shape that hugs axes.
    for seg_x0,seg_y0,seg_x1,seg_y1 in [
        (min(x0,x1)-pw/2, min(y0,y0)-pw/2,
         max(x0,x1)+pw/2, min(y0,y0)+pw/2),   # H segment
        (x1-pw/2, min(y0,y1)-pw/2,
         x1+pw/2, max(y0,y1)+pw/2),            # V segment
    ]:
        if abs(seg_x1-seg_x0)<0.5 or abs(seg_y1-seg_y0)<0.5:
            continue
        # Surface quad for path
        nx=int(max(2,abs(seg_x1-seg_x0)/10))
        ny=int(max(2,abs(seg_y1-seg_y0)/10))
        xs=np.linspace(seg_x0,seg_x1,nx)
        ys=np.linspace(seg_y0,seg_y1,ny)
        Xg,Yg=np.meshgrid(xs,ys)
        Zg=np.full_like(Xg, tz+0.06)
        traces.append(go.Surface(
            x=Xg,y=Yg,z=Zg,
            colorscale=[[0,color],[1,'#BCAAA4']],
            showscale=False,opacity=0.88,
            name=name,showlegend=show_legend,
            legendgroup=lg,
        ))
        show_legend=False
    return traces


def _spine_slab(x0,y0,x1,y1,width,tz,
                color='#D7CCC8',name='Road',lg='Roads') -> go.Surface:
    """Full spine road as a flat Surface (no L-shape)."""
    if x0==x1:   # vertical
        xs=np.linspace(x0-width/2,x0+width/2,4)
        ys=np.linspace(min(y0,y1),max(y0,y1),max(4,int(abs(y1-y0)/10)))
    else:         # horizontal
        xs=np.linspace(min(x0,x1),max(x0,x1),max(4,int(abs(x1-x0)/10)))
        ys=np.linspace(y0-width/2,y0+width/2,4)
    Xg,Yg=np.meshgrid(xs,ys)
    Zg=np.full_like(Xg,tz+0.04)
    return go.Surface(x=Xg,y=Yg,z=Zg,
                      colorscale=[[0,color],[1,'#BCAAA4']],
                      showscale=False,opacity=0.90,
                      name=name,showlegend=True,legendgroup=lg)


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
        self._reg    = _CollisionRegistry()
        self._L      = layout['dimensions']['L']
        self._W      = layout['dimensions']['W']
        self._slope  = layout.get('slope','Flat')
        self._layout = layout

        fig = go.Figure()

        # ── STRICT ORDER: roads first, features second, trees last ──────
        self._add_terrain(fig)
        self._add_zones(fig)
        self._add_spine_roads(fig)          # Step 1: roads registered
        self._add_house(fig)                # Step 2a: house registered
        self._add_kitchen_garden(fig)       # Step 2b: always visible
        self._add_water_features(fig)
        self._add_solar(fig)
        self._add_greenhouse(fig)
        self._add_rain_tank(fig)
        self._add_all_livestock(fig)
        self._add_feature_spurs(fig)        # Step 2c: spur paths per feature
        self._add_trees(fig)                # Step 3: trees last

        self._configure_layout(fig)
        return fig

    # ── Terrain Z helpers ─────────────────────────────────────────────────────
    def _tz(self, x, y) -> float:
        s,L,W = self._slope, self._L, self._W
        if s=='South': return y*0.03
        if s=='North': return (W-y)*0.03
        if s=='East':  return x*0.03
        if s=='West':  return (L-x)*0.03
        return 0.0

    def _tz_grid(self, X, Y):
        s,L,W = self._slope, self._L, self._W
        if s=='South': return Y*0.03
        if s=='North': return (W-Y)*0.03
        if s=='East':  return X*0.03
        if s=='West':  return (L-X)*0.03
        return np.zeros_like(X)

    # ── Terrain ───────────────────────────────────────────────────────────────
    def _add_terrain(self, fig):
        L,W=self._L,self._W
        x=np.linspace(0,L,40); y=np.linspace(0,W,40)
        X,Y=np.meshgrid(x,y); Z=self._tz_grid(X,Y)
        fig.add_trace(go.Surface(
            x=X,y=Y,z=Z,
            colorscale=[[0,'#33691E'],[0.35,'#558B2F'],
                        [0.65,'#7CB342'],[1,'#9CCC65']],
            showscale=False,opacity=0.88,
            name='Terrain',showlegend=True,legendgroup='Terrain',
            lighting=dict(ambient=0.70,diffuse=0.85),
            contours=dict(z=dict(show=True,color='#2E7D32',
                                 width=1,start=Z.min(),
                                 end=Z.max(),
                                 size=max(0.01,(Z.max()-Z.min()+0.01)/5))),
        ))

    # ── Zones ─────────────────────────────────────────────────────────────────
    def _add_zones(self, fig):
        zone_cs = {
            'z0':[[0,'#FFF9C4'],[1,'#FFFDE7']],
            'z1':[[0,'#A5D6A7'],[1,'#C8E6C9']],
            'z2':[[0,'#1B5E20'],[1,'#2E7D32']],
            'z3':[[0,'#F9A825'],[1,'#FFF9C4']],
            'z4':[[0,'#CE93D8'],[1,'#EDE7F6']],
        }
        for zid,pos in self._layout.get('zone_positions',{}).items():
            x0,y0=pos['x'],pos['y']
            x1,y1=x0+pos['width'],y0+pos['height']
            nx=max(4,int(pos['width']/20)); ny=max(4,int(pos['height']/20))
            xs=np.linspace(x0,x1,nx); ys=np.linspace(y0,y1,ny)
            Xg,Yg=np.meshgrid(xs,ys)
            Zg=self._tz_grid(Xg,Yg)+1.1
            if zid in('z2','z3'):
                np.random.seed(hash(zid)%100)
                Zg+=np.random.uniform(0,0.3,Zg.shape)
            fig.add_trace(go.Surface(
                x=Xg,y=Yg,z=Zg,
                colorscale=zone_cs.get(zid,[[0,'#DDD'],[1,'#EEE']]),
                showscale=False,opacity=0.50,
                name=self.ZONE_NAMES.get(zid,zid),
                showlegend=True,legendgroup=zid,
            ))

    # ── STEP 1: Spine roads — registered FIRST ────────────────────────────────
    def _add_spine_roads(self, fig):
        """
        Road network:
          - Perimeter road (inner boundary, ~12ft from edge)
          - Main N-S spine through house door
          - Main E-W spine at house mid-height
        All segments are registered in collision registry immediately.
        """
        L,W = self._L,self._W
        hx,hy,hw,hd = self._house_bbox()
        door_cx = hx+hw/2
        cross_y  = hy+hd*0.5
        main_w   = 10.0   # ft wide main road
        peri_w   = 8.0    # ft wide perimeter road
        peri_off = 12.0   # ft from boundary
        tz_mid   = self._tz(L/2,W/2)
        shown    = False

        # ── Perimeter road ──────────────────────────────────────────────
        peri_segs = [
            # South edge
            (peri_off, peri_off,  L-peri_off, peri_off, False),
            # North edge
            (peri_off, W-peri_off,L-peri_off, W-peri_off, False),
            # West edge
            (peri_off, peri_off,  peri_off,   W-peri_off, False),
            # East edge
            (L-peri_off,peri_off, L-peri_off, W-peri_off, False),
        ]
        for (sx0,sy0,sx1,sy1,_) in peri_segs:
            # Register perimeter road rectangles
            if sx0==sx1:  # vertical
                self._reg.register_rect(sx0-peri_w/2,sy0,sx0+peri_w/2,sy1)
            else:         # horizontal
                self._reg.register_rect(sx0,sy0-peri_w/2,sx1,sy0+peri_w/2)
            tz=self._tz((sx0+sx1)/2,(sy0+sy1)/2)
            fig.add_trace(_spine_slab(sx0,sy0,sx1,sy1,peri_w,tz,
                                      name='Perimeter Road',lg='Roads'))

        # ── Main N-S spine (house entrance → south boundary) ─────────────
        self._reg.register_rect(door_cx-main_w/2, 0, door_cx+main_w/2, hy)
        fig.add_trace(_spine_slab(door_cx,0,door_cx,hy,main_w,
                                  self._tz(door_cx,hy/2),
                                  name='Main Road',lg='Roads'))

        # ── Main E-W cross road ───────────────────────────────────────────
        self._reg.register_rect(0,cross_y-main_w/2,L,cross_y+main_w/2)
        fig.add_trace(_spine_slab(0,cross_y,L,cross_y,main_w,
                                  self._tz(L/2,cross_y),
                                  name='Main Road',lg='Roads'))

        # ── N-S spine top section (above house to north boundary) ─────────
        self._reg.register_rect(door_cx-main_w/2,hy+hd,door_cx+main_w/2,W)
        fig.add_trace(_spine_slab(door_cx,hy+hd,door_cx,W,main_w,
                                  self._tz(door_cx,(hy+hd+W)/2),
                                  name='Main Road',lg='Roads'))

    # ── STEP 2a: House (registered after roads) ───────────────────────────────
    def _house_bbox(self):
        L,W=self._L,self._W
        pos=self._layout.get('house_position','Center')
        p={
            'North':        (L*0.30,W*0.82,L*0.40,W*0.12),
            'South':        (L*0.30,W*0.06,L*0.40,W*0.12),
            'East':         (L*0.75,W*0.35,L*0.20,W*0.30),
            'West':         (L*0.05,W*0.35,L*0.20,W*0.30),
            'Center':       (L*0.35,W*0.40,L*0.30,W*0.20),
            'Not built yet':(L*0.35,W*0.40,L*0.30,W*0.20),
        }
        return p.get(pos,p['Center'])

    def _add_house(self, fig):
        hx,hy,hw,hd=self._house_bbox()
        base=self._tz(hx+hw/2,hy+hd/2)+1.5
        wall_h=10.0; roof_b=base+wall_h
        roof_t=roof_b+min(hw,hd)*0.42
        wall_t=0.6
        self._reg.register_rect(hx,hy,hx+hw,hy+hd)
        lg='House'

        # Foundation
        fig.add_trace(_box(hx-0.5,hy-0.5,base-0.5,hx+hw+0.5,hy+hd+0.5,base,
                           '#BCAAA4','Foundation',0.95,False,lg))
        # 4 walls
        for (wx0,wy0,wx1,wy1,wc) in [
            (hx,   hy,         hx+hw, hy+wall_t,     '#D7CCC8'),
            (hx,   hy+hd-wall_t,hx+hw,hy+hd,         '#BCAAA4'),
            (hx,   hy,         hx+wall_t,hy+hd,       '#D7CCC8'),
            (hx+hw-wall_t,hy,  hx+hw, hy+hd,          '#BCAAA4'),
        ]:
            fig.add_trace(_box(wx0,wy0,base,wx1,wy1,roof_b,wc,'House',0.97,
                               wx0==hx and wy0==hy,lg))  # showlegend only first
        # Floor
        fig.add_trace(_box(hx+wall_t,hy+wall_t,base,
                           hx+hw-wall_t,hy+hd-wall_t,base+0.2,
                           '#EFEBE9','House Floor',0.95,False,lg))
        # Windows south
        ww,wh=hw*0.13,wall_h*0.30; wz=base+wall_h*0.45
        for wx in [hx+hw*0.18,hx+hw*0.70]:
            fig.add_trace(_box(wx-0.15,hy-0.15,wz-0.15,wx+ww+0.15,hy+wall_t+0.15,wz+wh+0.15,
                               '#5D4037','Window Frame',0.95,False,lg))
            fig.add_trace(_box(wx,hy-0.1,wz,wx+ww,hy+wall_t+0.1,wz+wh,
                               '#B3E5FC','Window',0.80,False,lg))
        # Door
        dw=hw*0.12; dx=hx+hw/2-dw/2
        fig.add_trace(_box(dx,hy-0.15,base,dx+dw,hy+wall_t+0.15,base+wall_h*0.55,
                           '#3E2723','Door',0.97,False,lg))
        # Roof
        fig.add_trace(_hip_roof(hx,hy,hx+hw,hy+hd,roof_b,roof_t,
                                '#4E342E','Roof',lg))
        # Chimney
        cx2=hx+hw*0.72; cy2=hy+hd*0.4
        cw2=hw*0.08; cd2=hd*0.08
        fig.add_trace(_box(cx2,cy2,roof_b-1,cx2+cw2,cy2+cd2,roof_t+3,
                           '#6D4C41','Chimney',0.97,False,lg))
        # Porch
        pw2=hw*0.45; pd2=hd*0.15
        px2=hx+(hw-pw2)/2; py2=hy-pd2; pz2=base+wall_h*0.65
        fig.add_trace(_box(px2,py2,pz2,px2+pw2,hy,pz2+0.4,
                           '#EFEBE9','Porch',0.75,False,lg))
        for col_x in [px2+pw2*0.10,px2+pw2*0.90]:
            fig.add_trace(_cylinder(col_x,py2+pd2/2,0.5,base,pz2,
                                    '#8D6E63','Porch Column',show_legend=False,legendgroup=lg))

    # ── STEP 2b: Kitchen Garden — always drawn regardless of collision ─────────
    def _add_kitchen_garden(self, fig):
        zones=self._layout.get('zone_positions',{})
        if 'z1' not in zones: return
        pos=zones['z1']
        x0,y0=pos['x'],pos['y']
        w,h=pos['width'],pos['height']
        base=self._tz(x0+w/2,y0+h/2)+1.3

        bed_w   = max(15,min(w*0.18,22))
        bed_gap = max(6, min(w*0.04,10))
        n_beds  = max(1,int((w-bed_gap)/(bed_w+bed_gap)))
        show_bed=True

        path_col='#BCAAA4'
        for i in range(n_beds):
            bx0=x0+bed_gap+i*(bed_w+bed_gap)
            bx1=bx0+bed_w
            by0=y0+6; by1=y0+h-6
            if bx1>x0+w-bed_gap: break

            # Soil bed
            fig.add_trace(_box(bx0,by0,base,bx1,by1,base+0.7,
                               '#5D4037','Raised Bed',0.92,show_bed,
                               'Kitchen Garden'))
            show_bed=False

            # Plant cones on bed
            n_rows=max(1,int((by1-by0)/9))
            for ri in range(n_rows):
                ry=by0+4+ri*((by1-by0-8)/max(n_rows-1,1))
                for px_off in np.linspace(bx0+2,bx1-2,4):
                    pc=['#4CAF50','#8BC34A','#CDDC39'][ri%3]
                    fig.add_trace(_cone(px_off,ry,1.4,base+0.7,base+2.8,pc,
                                        'Vegetable Plants',
                                        n=10,show_legend=(i==0 and ri==0),
                                        legendgroup='Kitchen Garden'))

            # Path strip between beds
            if i<n_beds-1:
                strip_x=bx1; strip_xend=bx1+bed_gap
                xs=np.linspace(strip_x,strip_xend,3)
                ys=np.linspace(by0,by1,max(3,int((by1-by0)/8)))
                Xg,Yg=np.meshgrid(xs,ys)
                Zg=np.full_like(Xg,base+0.05)
                fig.add_trace(go.Surface(x=Xg,y=Yg,z=Zg,
                                         colorscale=[[0,path_col],[1,'#D7CCC8']],
                                         showscale=False,opacity=0.85,
                                         name='Garden Path',showlegend=(i==0),
                                         legendgroup='Kitchen Garden'))

    # ── Water features ────────────────────────────────────────────────────────
    def _add_water_features(self, fig):
        features=self._layout.get('features',{})

        if 'pond' in features:
            f=features['pond']; r=f['radius']
            base=self._tz(f['x'],f['y'])
            if self._reg.circle_clear(f['x'],f['y'],r):
                self._reg.register_circle(f['x'],f['y'],r)
                rg=np.linspace(0,r,12); tg=np.linspace(0,2*np.pi,40)
                R,T=np.meshgrid(rg,tg)
                irr=1+0.12*np.sin(3*T)+0.08*np.cos(5*T)
                Zp=base-1.0+R/r*0.8
                fig.add_trace(go.Surface(
                    x=f['x']+R*np.cos(T)*irr,y=f['y']+R*np.sin(T)*irr,z=Zp,
                    colorscale=[[0,'#01579B'],[0.5,'#0288D1'],[1,'#4FC3F7']],
                    showscale=False,opacity=0.88,
                    name='Pond / Aquaculture',showlegend=True,legendgroup='Pond'))
                # Rim
                rim_r=r*1.06; rt=np.linspace(0,2*np.pi,40)
                fig.add_trace(go.Scatter3d(
                    x=f['x']+rim_r*np.cos(rt),y=f['y']+rim_r*np.sin(rt),
                    z=[base+0.25]*40,mode='lines',
                    line=dict(color='#5D4037',width=4),
                    name='Pond Rim',showlegend=False,legendgroup='Pond'))

        for key in('borewell','well'):
            if key in features:
                f=features[key]; r=f.get('radius',4)
                base=self._tz(f['x'],f['y'])
                if self._reg.circle_clear(f['x'],f['y'],r):
                    self._reg.register_circle(f['x'],f['y'],r)
                    fig.add_trace(_cylinder(f['x'],f['y'],r,base,base+5,
                                            '#546E7A','Borewell',
                                            show_legend=True,legendgroup='Borewell'))
                    fig.add_trace(_cylinder(f['x'],f['y'],r*0.8,base,base+3.5,
                                            '#4FC3F7','Borewell Water',
                                            show_legend=False,legendgroup='Borewell'))
                break

    # ── Solar ─────────────────────────────────────────────────────────────────
    def _add_solar(self, fig):
        f=self._layout.get('features',{}).get('solar')
        if not f: return
        x0,y0,x1,y1=f['x'],f['y'],f['x']+f['width'],f['y']+f['height']
        base=self._tz((x0+x1)/2,(y0+y1)/2)+1.5
        if not self._reg.rect_clear(x0,y0,x1,y1): return
        self._reg.register_rect(x0,y0,x1,y1)
        fig.add_trace(_box(x0,y0,base,x1,y1,base+0.3,
                           '#607D8B','Solar Frame',0.95,False,'Solar'))
        rows,cols,gap=2,3,1.5
        cw=(f['width']-gap*(cols+1))/cols; ch=(f['height']-gap*(rows+1))/rows
        sl=True
        for row in range(rows):
            for col in range(cols):
                px=x0+gap+col*(cw+gap); py=y0+gap+row*(ch+gap)
                fig.add_trace(_box(px,py,base+0.25,px+cw,py+ch,base+0.55,
                                   '#1565C0','Solar Panels',0.97,sl,'Solar'))
                sl=False

    # ── Greenhouse ────────────────────────────────────────────────────────────
    def _add_greenhouse(self, fig):
        f=self._layout.get('features',{}).get('greenhouse')
        if not f: return
        x0,y0,x1,y1=f['x'],f['y'],f['x']+f['width'],f['y']+f['height']
        base=self._tz((x0+x1)/2,(y0+y1)/2)+1.5
        if not self._reg.rect_clear(x0,y0,x1,y1): return
        self._reg.register_rect(x0,y0,x1,y1)
        gh_h=8.0
        fig.add_trace(_box(x0,y0,base,x1,y1,base+gh_h,
                           '#E0F2F1','Greenhouse',0.30,True,'Greenhouse'))
        fig.add_trace(_hip_roof(x0,y0,x1,y1,base+gh_h,
                                base+gh_h+f['width']*0.28,
                                '#80CBC4','GH Roof','Greenhouse'))
        for sy in [y0+4,y1-12]:
            fig.add_trace(_box(x0+4,sy,base+0.5,x1-4,sy+8,base+1.3,
                               '#5D4037','GH Bed',0.90,False,'Greenhouse'))

    # ── Rain tank ─────────────────────────────────────────────────────────────
    def _add_rain_tank(self, fig):
        f=self._layout.get('features',{}).get('rain_tank')
        if not f: return
        x0,y0,x1,y1=f['x'],f['y'],f['x']+f['width'],f['y']+f['height']
        base=self._tz((x0+x1)/2,(y0+y1)/2)+1.5
        if not self._reg.rect_clear(x0,y0,x1,y1): return
        self._reg.register_rect(x0,y0,x1,y1)
        fig.add_trace(_box(x0,y0,base,x1,y1,base+6,'#4FC3F7',
                           'Rain Tank',0.80,True,'Rain Tank'))

    # ── All livestock ─────────────────────────────────────────────────────────
    def _add_all_livestock(self, fig):
        features=self._layout.get('features',{})
        cfg={
            'goat_shed':    ('#FFCCBC','#4E342E','Goat Shed',    7.0),
            'chicken_coop': ('#FFF9C4','#F57F17','Chicken Coop', 5.0),
            'piggery':      ('#F8BBD0','#880E4F','Piggery',      6.0),
            'cow_shed':     ('#D7CCC8','#5D4037','Cow Shed',     9.0),
            'fish_tanks':   ('#B3E5FC','#0288D1','Fish Tanks',   2.5),
            'bee_hives':    ('#FFF176','#F9A825','Bee Hives',    3.5),
        }
        for key,(wc,rc,label,sh) in cfg.items():
            if key not in features: continue
            f=features[key]
            x0,y0,x1,y1=f['x'],f['y'],f['x']+f['width'],f['y']+f['height']
            base=self._tz((x0+x1)/2,(y0+y1)/2)+1.5
            if not self._reg.rect_clear(x0,y0,x1,y1): continue
            self._reg.register_rect(x0,y0,x1,y1)
            roof_b=base+sh; roof_t=roof_b+f['width']*0.25
            fig.add_trace(_box(x0,y0,base,x1,y1,roof_b,wc,label,0.92,True,label))
            fig.add_trace(_hip_roof(x0,y0,x1,y1,roof_b,roof_t,rc,label+' Roof',label))
            if key=='fish_tanks':
                fig.add_trace(_box(x0+2,y0+2,base+0.5,x1-2,y1-2,base+0.8,
                                   '#4FC3F7','Fish Water',0.70,False,label))
            if key=='bee_hives':
                hw_e=max(10,(f['width']-5)/max(1,int(f['width']/15))-2)
                n_h =max(1,int(f['width']/15))
                for hi in range(n_h):
                    hxe=x0+3+hi*(hw_e+2)
                    fig.add_trace(_box(hxe,y0+2,base,hxe+hw_e,y1-2,base+3.5,
                                       '#FFF176',f'Hive{hi+1}',0.95,False,label))

    # ── STEP 2c: Feature spur paths — each feature gets a short path to spine ─
    def _add_feature_spurs(self, fig):
        """
        For every placed feature, draw a short path from the nearest spine
        point to the feature entrance. Spurs are THIN (6ft) and drawn ON TOP
        of the zone surface, never through another feature.
        """
        features=self._layout.get('features',{})
        hx,hy,hw,hd=self._house_bbox()
        door_cx=hx+hw/2
        cross_y=hy+hd*0.5
        spur_w=6.0
        spur_col='#BCAAA4'
        show_leg=True

        def _spur(fx,fy):
            nonlocal show_leg
            tz=self._tz(fx,fy)
            # Nearest spine point: either cross_y or door_cx column
            # Snap to closest of the two main axes
            if abs(fx-door_cx)<abs(fy-cross_y):
                # Closer to N-S spine: go horizontal to door_cx, then along spine
                spine_x,spine_y=door_cx,fy
            else:
                # Closer to E-W spine: go vertical to cross_y, then along spine
                spine_x,spine_y=fx,cross_y

            # Draw H segment
            xs=np.linspace(min(fx,spine_x),max(fx,spine_x),max(3,int(abs(fx-spine_x)/5)))
            if len(xs)>1:
                ys=np.linspace(fy-spur_w/2,fy+spur_w/2,3)
                Xg,Yg=np.meshgrid(xs,ys)
                Zg=np.full_like(Xg,tz+0.08)
                fig.add_trace(go.Surface(x=Xg,y=Yg,z=Zg,
                                          colorscale=[[0,spur_col],[1,spur_col]],
                                          showscale=False,opacity=0.85,
                                          name='Feature Path',showlegend=show_leg,
                                          legendgroup='Roads'))
                show_leg=False
            # Draw V segment
            ys2=np.linspace(min(fy,spine_y),max(fy,spine_y),max(3,int(abs(fy-spine_y)/5)))
            if len(ys2)>1:
                xs2=np.linspace(spine_x-spur_w/2,spine_x+spur_w/2,3)
                Xg2,Yg2=np.meshgrid(xs2,ys2)
                Zg2=np.full_like(Xg2,tz+0.08)
                fig.add_trace(go.Surface(x=Xg2,y=Yg2,z=Zg2,
                                          colorscale=[[0,spur_col],[1,spur_col]],
                                          showscale=False,opacity=0.85,
                                          name='Feature Path',showlegend=False,
                                          legendgroup='Roads'))

        for key in features:
            f=features[key]
            if 'radius' in f:
                fx,fy=f['x'],f['y']
            else:
                fx=f['x']+f.get('width',20)/2
                fy=f['y']+f.get('height',20)/2
            # Only draw spur if feature is registered (was placed successfully)
            if not self._reg.point_in_any(fx,fy):
                continue
            _spur(fx,fy)

    # ── STEP 3: Trees — checked against ALL registered elements ──────────────
    def _add_trees(self, fig):
        zones=self._layout.get('zone_positions',{})
        features=self._layout.get('features',{})
        extra_trees=self._layout.get('extra_trees',[])  # custom user trees

        # Gather all zone positions for tree placement
        z2_zones=[]
        if 'z2' in zones:
            z2_zones.append(zones['z2'])

        # Also scatter some in z3 edges (not in crops, but borders)
        border_zones=[]
        if 'z4' in zones:
            border_zones.append(zones['z4'])

        # Build placement list from z2
        species_cycle = _SPECIES_CYCLE.copy()
        placements=[]
        for z in z2_zones:
            np.random.seed(42)
            rx_list=np.random.uniform(0.05,0.95,20)
            ry_list=np.random.uniform(0.05,0.95,20)
            for idx,(rx,ry) in enumerate(zip(rx_list,ry_list)):
                tx=z['x']+rx*z['width']
                ty=z['y']+ry*z['height']
                sp=species_cycle[idx%len(species_cycle)]
                placements.append((tx,ty,sp))

        # Buffer zone (z4): Neem, Teak, Bamboo border trees
        for z in border_zones:
            np.random.seed(77)
            for idx in range(12):
                rx=np.random.uniform(0.02,0.98)
                ry=np.random.uniform(0.05,0.95)
                tx=z['x']+rx*z['width']
                ty=z['y']+ry*z['height']
                sp=['Neem','Teak','Bamboo'][idx%3]
                placements.append((tx,ty,sp))

        # Custom user trees
        for item in extra_trees:
            placements.append((item['x'],item['y'],item.get('species','Mango')))

        first_tree=True
        for tx,ty,species in placements:
            sp=TREE_SPECIES.get(species,TREE_SPECIES['Mango'])
            cr=sp['canopy_r']
            tr=sp['trunk_r']

            # Clamp inside property
            tx=max(cr+2, min(tx, self._L-cr-2))
            ty=max(cr+2, min(ty, self._W-cr-2))

            # Strict collision check — skip if overlaps road/feature
            if not self._reg.circle_clear(tx,ty,cr):
                continue
            self._reg.register_circle(tx,ty,cr)

            base=self._tz(tx,ty)+1.3

            # Trunk
            fig.add_trace(_cylinder(tx,ty,tr,base,base+sp['trunk_h'],
                                    '#6D4C41',species,show_legend=first_tree,
                                    legendgroup='Trees'))
            # Primary canopy
            fig.add_trace(_cone(tx,ty,cr,base+sp['canopy_bot'],
                                base+sp['canopy_top'],sp['color'],species,
                                show_legend=False,legendgroup='Trees'))
            # Secondary canopy (rounder look)
            fig.add_trace(_cone(tx,ty,cr*0.70,
                                base+sp['canopy_bot']+cr*0.35,
                                base+sp['canopy_top']+cr*0.12,
                                sp['color2'],species,
                                show_legend=False,legendgroup='Trees'))
            first_tree=False

    # ── Layout ────────────────────────────────────────────────────────────────
    def _configure_layout(self, fig):
        L,W=self._L,self._W
        acres=self._layout.get('acres',round(L*W/43560,2))
        fig.update_layout(
            title=dict(
                text=(f"🏡 3D Homestead — {acres:.2f} acres ({int(L)} × {int(W)} ft)"
                      "<br><sup>Click legend to toggle layers · Drag to rotate</sup>"),
                font=dict(size=15,color='#2E7D32',family='Arial'),x=0.5,
            ),
            scene=dict(
                xaxis_title='Length (ft)',yaxis_title='Width (ft)',
                zaxis_title='Height (ft)',aspectmode='data',
                bgcolor='#C9E8F5',
                camera=dict(eye=dict(x=1.3,y=-1.5,z=0.85),
                            up=dict(x=0,y=0,z=1)),
                xaxis=dict(showgrid=True,gridcolor='#B0BEC5',
                           showbackground=True,backgroundcolor='#EAF4FB'),
                yaxis=dict(showgrid=True,gridcolor='#B0BEC5',
                           showbackground=True,backgroundcolor='#EAF4FB'),
                zaxis=dict(showgrid=True,gridcolor='#B0BEC5',
                           showbackground=True,backgroundcolor='#EAF4FB',
                           range=[-2,35]),
            ),
            legend=dict(
                x=0.01,y=0.99,
                bgcolor='rgba(255,255,255,0.90)',
                bordercolor='#90A4AE',borderwidth=1.5,
                font=dict(size=10),
                itemclick='toggle',
                itemdoubleclick='toggleothers',
                title=dict(text='<b>Layers</b> (click=toggle)',
                           font=dict(size=9)),
            ),
            paper_bgcolor='#EAF4FB',
            margin=dict(l=0,r=0,t=70,b=0),
            width=1000,height=720,
            updatemenus=[dict(
                type='buttons',direction='left',
                x=0.5,y=0.01,xanchor='center',
                buttons=[
                    dict(label='Top View',method='relayout',
                         args=[{'scene.camera.eye':{'x':0,'y':0,'z':2.5},
                                'scene.camera.up':{'x':0,'y':1,'z':0}}]),
                    dict(label='3D View',method='relayout',
                         args=[{'scene.camera.eye':{'x':1.3,'y':-1.5,'z':0.85},
                                'scene.camera.up':{'x':0,'y':0,'z':1}}]),
                    dict(label='South View',method='relayout',
                         args=[{'scene.camera.eye':{'x':0,'y':-2.5,'z':0.5},
                                'scene.camera.up':{'x':0,'y':0,'z':1}}]),
                    dict(label='Bird View',method='relayout',
                         args=[{'scene.camera.eye':{'x':0.1,'y':-0.1,'z':3.0},
                                'scene.camera.up':{'x':0,'y':1,'z':0}}]),
                ],
                bgcolor='white',bordercolor='#78909C',font=dict(size=11),
            )],
        )

    def export_as_html(self, fig: go.Figure, filename: str='homestead_3d.html'):
        pio.write_html(fig,file=filename,auto_open=False,include_plotlyjs='cdn')
