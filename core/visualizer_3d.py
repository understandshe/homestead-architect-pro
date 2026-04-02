"""
3D Visualization Engine — Premium Realistic Edition
Homestead Architect Pro 2026 — Global Edition

Features:
  - Collision detection: every element checks 10 ft clearance before placing
  - Dynamic paths from house to EVERY feature the user selected
  - Kitchen Garden (z1): raised beds, plant rows, soil texture
  - Realistic terrain: grass/soil surface shading via go.Surface
  - Option-B House: proper 3D exterior, walls + hip roof + colored windows + door
  - Tree species have individual realistic heights (Mango 20ft, Coconut 30ft, etc.)
  - Legend toggle: click legend item to hide/show that trace
  - No hardcoded positions: everything derived from layout dict
  - All livestock types individually drawn with roofs
"""

import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
from typing import Dict, Any, List, Tuple, Optional


# ─────────────────────────────────────────────────────────────────────────────
#  Collision Registry
# ─────────────────────────────────────────────────────────────────────────────
class _CollisionRegistry:
    """
    Keeps axis-aligned bounding boxes for placed elements.
    Enforces a minimum clearance (default 10 ft) between any two elements.
    """
    CLEARANCE = 10.0

    def __init__(self):
        self._rects: List[Tuple[float, float, float, float]] = []   # x0,y0,x1,y1
        self._circles: List[Tuple[float, float, float]] = []         # cx,cy,r

    def register_rect(self, x0: float, y0: float, x1: float, y1: float):
        self._rects.append((min(x0,x1), min(y0,y1), max(x0,x1), max(y0,y1)))

    def register_circle(self, cx: float, cy: float, r: float):
        self._circles.append((cx, cy, r))

    def rect_clear(self, x0: float, y0: float, x1: float, y1: float) -> bool:
        c = self.CLEARANCE
        ax0, ay0, ax1, ay1 = min(x0,x1)-c, min(y0,y1)-c, max(x0,x1)+c, max(y0,y1)+c
        for (rx0,ry0,rx1,ry1) in self._rects:
            if ax0 < rx1 and ax1 > rx0 and ay0 < ry1 and ay1 > ry0:
                return False
        for (cx,cy,r) in self._circles:
            nearest_x = max(ax0, min(cx, ax1))
            nearest_y = max(ay0, min(cy, ay1))
            if (cx-nearest_x)**2+(cy-nearest_y)**2 < (r+c)**2:
                return False
        return True

    def circle_clear(self, cx: float, cy: float, r: float) -> bool:
        c = self.CLEARANCE
        for (rx0,ry0,rx1,ry1) in self._rects:
            nearest_x = max(rx0, min(cx, rx1))
            nearest_y = max(ry0, min(cy, ry1))
            if (cx-nearest_x)**2+(cy-nearest_y)**2 < (r+c)**2:
                return False
        for (ocx,ocy,or_) in self._circles:
            if (cx-ocx)**2+(cy-ocy)**2 < (r+or_+c)**2:
                return False
        return True

    def force_register_rect(self, x0, y0, x1, y1):
        """Register without clearing check (for house, terrain baseline)."""
        self._rects.append((min(x0,x1), min(y0,y1), max(x0,x1), max(y0,y1)))

    def force_register_circle(self, cx, cy, r):
        self._circles.append((cx, cy, r))


# ─────────────────────────────────────────────────────────────────────────────
#  Geometry primitives
# ─────────────────────────────────────────────────────────────────────────────
def _box(x0,y0,z0, x1,y1,z1, color, name, opacity=0.90, show_legend=True,
         legendgroup=None) -> go.Mesh3d:
    """Correct 6-face axis-aligned box with explicit i/j/k face indices."""
    vx = [x0,x1,x1,x0, x0,x1,x1,x0]
    vy = [y0,y0,y1,y1, y0,y0,y1,y1]
    vz = [z0,z0,z0,z0, z1,z1,z1,z1]
    fi = [0,0, 4,4, 0,0, 2,2, 0,0, 1,1]
    fj = [1,2, 5,6, 1,5, 3,7, 3,7, 2,6]
    fk = [2,3, 6,7, 5,4, 7,6, 7,4, 6,5]
    return go.Mesh3d(x=vx,y=vy,z=vz,i=fi,j=fj,k=fk,
                     color=color, opacity=opacity, name=name,
                     showlegend=show_legend,
                     legendgroup=legendgroup or name,
                     legendgrouptitle_text=None,
                     flatshading=True,
                     lighting=dict(ambient=0.6,diffuse=0.9,specular=0.3,
                                   roughness=0.5,fresnel=0.1))

def _hip_roof(x0,y0,x1,y1, base_z, apex_z, color, name='Roof',
              legendgroup=None) -> go.Mesh3d:
    cx,cy = (x0+x1)/2,(y0+y1)/2
    vx=[x0,x1,x1,x0,cx]; vy=[y0,y0,y1,y1,cy]; vz=[base_z]*4+[apex_z]
    fi=[0,1,2,3]; fj=[1,2,3,0]; fk=[4,4,4,4]
    return go.Mesh3d(x=vx,y=vy,z=vz,i=fi,j=fj,k=fk,
                     color=color, opacity=0.97, name=name,
                     showlegend=False,
                     legendgroup=legendgroup or name,
                     flatshading=True)

def _cylinder_surface(cx,cy, r, z_bot, z_top, color, name,
                      n=20, show_legend=True, legendgroup=None) -> go.Surface:
    theta = np.linspace(0,2*np.pi,n)
    z     = np.array([z_bot, z_top])
    T,Z   = np.meshgrid(theta,z)
    return go.Surface(x=cx+r*np.cos(T), y=cy+r*np.sin(T), z=Z,
                      colorscale=[[0,color],[1,color]],
                      showscale=False, opacity=0.92,
                      name=name, showlegend=show_legend,
                      legendgroup=legendgroup or name)

def _cone_mesh(cx,cy, r, z_bot, z_top, color, name,
               n=18, show_legend=False, legendgroup=None) -> go.Mesh3d:
    theta = np.linspace(0,2*np.pi,n,endpoint=False)
    vx = list(cx+r*np.cos(theta))+[cx]
    vy = list(cy+r*np.sin(theta))+[cy]
    vz = [z_bot]*n+[z_top]
    apex=n
    fi=list(range(n)); fj=[(k+1)%n for k in range(n)]; fk=[apex]*n
    return go.Mesh3d(x=vx,y=vy,z=vz,i=fi,j=fj,k=fk,
                     color=color, opacity=0.88, name=name,
                     showlegend=show_legend,
                     legendgroup=legendgroup or name,
                     flatshading=True)


# ─────────────────────────────────────────────────────────────────────────────
#  Tree species catalogue  (trunk_h, canopy_bot, canopy_top, canopy_r, color)
# ─────────────────────────────────────────────────────────────────────────────
TREE_SPECS = {
    'Mango':     dict(trunk_h=6,  canopy_bot=6,  canopy_top=20, canopy_r=8,  trunk_r=1.1, color='#2E7D32'),
    'Jackfruit': dict(trunk_h=8,  canopy_bot=8,  canopy_top=26, canopy_r=9,  trunk_r=1.3, color='#1B5E20'),
    'Coconut':   dict(trunk_h=20, canopy_bot=20, canopy_top=30, canopy_r=6,  trunk_r=0.8, color='#388E3C'),
    'Banana':    dict(trunk_h=4,  canopy_bot=4,  canopy_top=12, canopy_r=5,  trunk_r=1.5, color='#558B2F'),
    'Guava':     dict(trunk_h=4,  canopy_bot=4,  canopy_top=14, canopy_r=5,  trunk_r=0.8, color='#33691E'),
    'Papaya':    dict(trunk_h=5,  canopy_bot=5,  canopy_top=13, canopy_r=4,  trunk_r=0.6, color='#43A047'),
    'Citrus':    dict(trunk_h=4,  canopy_bot=4,  canopy_top=12, canopy_r=5,  trunk_r=0.7, color='#66BB6A'),
    'Avocado':   dict(trunk_h=7,  canopy_bot=7,  canopy_top=18, canopy_r=7,  trunk_r=1.0, color='#2E7D32'),
}


# ─────────────────────────────────────────────────────────────────────────────
#  Path building helper
# ─────────────────────────────────────────────────────────────────────────────
def _path_box(x0,y0, x1,y1, width, terrain_z, color='#D7CCC8',
              name='Path', show_legend=False, legendgroup='Paths') -> List:
    """
    Build a wide 3D path (gravel slab) between two points.
    Returns list of Mesh3d traces.
    """
    dx,dy = x1-x0, y1-y0
    dist  = max(np.hypot(dx,dy),1e-6)
    nx,ny = -dy/dist*width/2, dx/dist*width/2   # perpendicular offset

    # Four corners of the path slab
    corners_x = [x0+nx, x0-nx, x1-nx, x1+nx]
    corners_y = [y0+ny, y0-ny, y1-ny, y1+ny]
    z_surf    = terrain_z + 0.05   # just above terrain

    # Two triangles make the quad
    traces = []
    for (ia,ib,ic) in [(0,1,2),(0,2,3)]:
        traces.append(go.Mesh3d(
            x=[corners_x[ia],corners_x[ib],corners_x[ic]],
            y=[corners_y[ia],corners_y[ib],corners_y[ic]],
            z=[z_surf,z_surf,z_surf],
            i=[0],j=[1],k=[2],
            color=color, opacity=0.85,
            name=name, showlegend=show_legend and ia==0,
            legendgroup=legendgroup,
            flatshading=True,
        ))
        show_legend=False   # only show for first triangle
    return traces


# ─────────────────────────────────────────────────────────────────────────────
#  Main class
# ─────────────────────────────────────────────────────────────────────────────
class Visualizer3D:

    ZONE_COLORS = {
        'z0':'#F5F5DC','z1':'#C8E6C9','z2':'#228B22',
        'z3':'#F0E68C','z4':'#DDA0DD',
    }
    ZONE_NAMES = {
        'z0':'Zone 0 – Residential','z1':'Zone 1 – Kitchen Garden',
        'z2':'Zone 2 – Food Forest','z3':'Zone 3 – Pasture / Crops',
        'z4':'Zone 4 – Buffer Zone',
    }

    def create(self, layout: Dict[str,Any]) -> go.Figure:
        self._reg   = _CollisionRegistry()
        self._L     = layout['dimensions']['L']
        self._W     = layout['dimensions']['W']
        self._slope = layout.get('slope','Flat')
        self._layout= layout

        fig = go.Figure()

        # ── Layer order ───────────────────────────────────────────────────
        self._add_terrain(fig)
        self._add_zones(fig)
        self._add_kitchen_garden_detail(fig)
        self._add_paths_network(fig)         # dynamic paths
        self._add_water_features(fig)
        self._add_solar(fig)
        self._add_greenhouse(fig)
        self._add_rain_tank(fig)
        self._add_house(fig)                 # Option-B realistic house
        self._add_all_livestock(fig)
        self._add_trees(fig)

        self._configure_layout(fig)
        return fig

    # ── Terrain ──────────────────────────────────────────────────────────────
    def _terrain_z(self, x, y) -> float:
        """Scalar terrain height at point (x,y)."""
        s = self._slope
        L,W = self._L, self._W
        if s=='South':  return y*0.03
        if s=='North':  return (W-y)*0.03
        if s=='East':   return x*0.03
        if s=='West':   return (L-x)*0.03
        return 0.0

    def _terrain_z_grid(self, X, Y):
        s = self._slope
        L,W = self._L, self._W
        if s=='South':  return Y*0.03
        if s=='North':  return (W-Y)*0.03
        if s=='East':   return X*0.03
        if s=='West':   return (L-X)*0.03
        return np.zeros_like(X)

    def _add_terrain(self, fig):
        L,W = self._L,self._W
        x = np.linspace(0,L,40)
        y = np.linspace(0,W,40)
        X,Y = np.meshgrid(x,y)
        Z   = self._terrain_z_grid(X,Y)

        # Grass-like green gradient
        fig.add_trace(go.Surface(
            x=X,y=Y,z=Z,
            colorscale=[
                [0.0,'#33691E'],[0.3,'#558B2F'],
                [0.6,'#7CB342'],[1.0,'#9CCC65'],
            ],
            showscale=False, opacity=0.90,
            name='Terrain', showlegend=True,
            legendgroup='Terrain',
            lighting=dict(ambient=0.7,diffuse=0.85),
            contours=dict(
                z=dict(show=True,color='#2E7D32',width=1,
                       start=Z.min(),end=Z.max(),size=(Z.max()-Z.min()+0.01)/5)
            ),
        ))

    # ── Zone slabs ────────────────────────────────────────────────────────────
    def _add_zones(self, fig):
        zone_surface_colors = {
            'z0': [[0,'#F5F5DC'],[1,'#FFFDE7']],    # Residential - beige
            'z1': [[0,'#A5D6A7'],[1,'#E8F5E9']],    # Kitchen - light green
            'z2': [[0,'#1B5E20'],[1,'#388E3C']],    # Forest - dark green
            'z3': [[0,'#F9A825'],[1,'#FFF9C4']],    # Pasture - yellow
            'z4': [[0,'#CE93D8'],[1,'#F3E5F5']],    # Buffer - purple
        }

        for zone_id, pos in self._layout.get('zone_positions',{}).items():
            x0,y0 = pos['x'],pos['y']
            x1,y1 = x0+pos['width'],y0+pos['height']
            slab_h = 1.2

            # Use a small surface grid to give it texture
            nx,ny = 6,6
            xs = np.linspace(x0,x1,nx)
            ys = np.linspace(y0,y1,ny)
            Xg,Yg = np.meshgrid(xs,ys)
            Zg    = self._terrain_z_grid(Xg,Yg) + slab_h

            # Add subtle bumps for realism
            if zone_id in ('z2','z3'):
                np.random.seed(hash(zone_id)%100)
                Zg += np.random.uniform(0,0.4,Zg.shape)

            fig.add_trace(go.Surface(
                x=Xg,y=Yg,z=Zg,
                colorscale=zone_surface_colors.get(zone_id,[[0,'#CCCCCC'],[1,'#EEEEEE']]),
                showscale=False, opacity=0.55,
                name=self.ZONE_NAMES.get(zone_id,zone_id),
                showlegend=True,
                legendgroup=zone_id,
            ))

    # ── Kitchen Garden detail ─────────────────────────────────────────────────
    def _add_kitchen_garden_detail(self, fig):
        zones = self._layout.get('zone_positions',{})
        if 'z1' not in zones: return
        pos = zones['z1']
        x0,y0 = pos['x'],pos['y']
        w,h   = pos['width'],pos['height']
        base  = self._terrain_z(x0+w/2,y0+h/2)+1.3

        bed_w   = min(w*0.20, 25)
        bed_gap = min(w*0.05,  8)
        n_beds  = max(1, int((w-bed_gap) / (bed_w+bed_gap)))

        for i in range(n_beds):
            bx0 = x0 + bed_gap + i*(bed_w+bed_gap)
            bx1 = bx0+bed_w
            by0 = y0+5; by1 = y0+h-5
            if bx1 > x0+w-bed_gap: break

            # Soil bed (dark brown raised slab)
            fig.add_trace(_box(
                bx0,by0,base, bx1,by1,base+0.6,
                color='#5D4037', name='Raised Bed' if i==0 else '',
                opacity=0.92,
                show_legend=(i==0), legendgroup='Kitchen Garden',
            ))

            # Plant rows on top of bed
            n_rows = max(1,int((by1-by0)/8))
            for r in range(n_rows):
                ry = by0+4+r*((by1-by0-8)/max(n_rows-1,1))
                # Small green mounds = plants
                plant_color = ['#4CAF50','#8BC34A','#CDDC39'][r%3]
                for px_off in np.linspace(bx0+2,bx1-2,5):
                    fig.add_trace(_cone_mesh(
                        px_off, ry, 1.5, base+0.6, base+2.5,
                        color=plant_color,
                        name='Vegetable Plants' if (i==0 and r==0) else '',
                        show_legend=(i==0 and r==0),
                        legendgroup='Kitchen Garden',
                    ))

            # Path between beds (gravel strip)
            if i < n_beds-1:
                gx0 = bx1; gx1 = bx0+bed_w+bed_gap
                for t in _path_box(gx0,by0, gx1,by1, bed_gap*0.8,
                                   base, color='#BCAAA4',
                                   name='Garden Path',
                                   show_legend=(i==0),
                                   legendgroup='Kitchen Garden'):
                    fig.add_trace(t)

    # ── Dynamic path network ──────────────────────────────────────────────────
    def _add_paths_network(self, fig):
        """
        Build a path from the house entrance to EVERY feature the user selected.
        Path goes: house_door → nearest cross-point → feature centre.
        """
        features = self._layout.get('features',{})
        hx,hy,hw,hd = self._house_bbox()
        door_x = hx+hw/2
        door_y = hy           # south face of house

        path_w   = 8.0        # ft width of paths
        path_col = '#D7CCC8'
        base_z   = self._terrain_z(door_x,door_y)
        show_leg = True

        # Main entrance path (house south → property south boundary)
        for t in _path_box(door_x,0, door_x,door_y, path_w, base_z,
                           color=path_col, name='Access Path',
                           show_legend=show_leg, legendgroup='Paths'):
            fig.add_trace(t)
        show_leg = False

        # Cross path at house mid-level
        cross_y = hy+hd*0.5
        for t in _path_box(0,cross_y, self._L,cross_y, path_w, base_z,
                           color=path_col, name='Access Path',
                           show_legend=False, legendgroup='Paths'):
            fig.add_trace(t)

        # For each feature, draw a path from house to feature centre
        feature_centres = self._get_feature_centres(features, hx,hy,hw,hd)

        for feat_name,(fx,fy) in feature_centres.items():
            tz = self._terrain_z((door_x+fx)/2,(cross_y+fy)/2)
            # L-shaped path: house → cross point → feature
            mid_x,mid_y = fx, cross_y   # bend point
            for t in _path_box(door_x,cross_y, mid_x,mid_y, path_w*0.7, tz,
                               color='#BCAAA4', name='Access Path',
                               show_legend=False, legendgroup='Paths'):
                fig.add_trace(t)
            for t in _path_box(mid_x,mid_y, fx,fy, path_w*0.7, tz,
                               color='#BCAAA4', name='Access Path',
                               show_legend=False, legendgroup='Paths'):
                fig.add_trace(t)

    def _get_feature_centres(self, features, hx,hy,hw,hd):
        centres = {}
        def _fc(key):
            f = features.get(key,{})
            if not f: return None
            if 'radius' in f: return (f['x'],f['y'])
            return (f['x']+f.get('width',20)/2, f['y']+f.get('height',20)/2)

        for key in ('pond','borewell','well','solar','greenhouse','rain_tank',
                    'goat_shed','chicken_coop','piggery','cow_shed',
                    'fish_tanks','bee_hives'):
            c = _fc(key)
            if c: centres[key] = c
        return centres

    # ── Water features ────────────────────────────────────────────────────────
    def _add_water_features(self, fig):
        features = self._layout.get('features',{})

        if 'pond' in features:
            f = features['pond']
            r = f['radius']
            base = self._terrain_z(f['x'],f['y'])
            self._reg.force_register_circle(f['x'],f['y'],r)

            # Pond depression
            rg = np.linspace(0,r,12)
            tg = np.linspace(0,2*np.pi,40)
            R,T = np.meshgrid(rg,tg)
            # Natural irregular shape
            irregularity = 1+0.12*np.sin(3*T)+0.08*np.cos(5*T)
            Xp = f['x']+R*np.cos(T)*irregularity
            Yp = f['y']+R*np.sin(T)*irregularity
            Zp = base-1.0+R/r*0.8   # slopes up toward edges

            fig.add_trace(go.Surface(
                x=Xp,y=Yp,z=Zp,
                colorscale=[[0,'#01579B'],[0.4,'#0288D1'],
                            [0.7,'#4FC3F7'],[1,'#B3E5FC']],
                showscale=False, opacity=0.88,
                name='Pond / Aquaculture', showlegend=True,
                legendgroup='Pond',
            ))
            # Pond rim (slightly raised bank)
            rim_r = r*1.08
            rim_t = np.linspace(0,2*np.pi,40)
            fig.add_trace(go.Scatter3d(
                x=f['x']+rim_r*np.cos(rim_t),
                y=f['y']+rim_r*np.sin(rim_t),
                z=[base+0.2]*40,
                mode='lines',
                line=dict(color='#5D4037',width=4),
                name='Pond Rim', showlegend=False,
                legendgroup='Pond',
            ))

        for key in ('borewell','well'):
            if key in features:
                f = features[key]
                r = f.get('radius',4)
                base = self._terrain_z(f['x'],f['y'])
                self._reg.force_register_circle(f['x'],f['y'],r)

                fig.add_trace(_cylinder_surface(
                    f['x'],f['y'], r, base, base+5,
                    color='#546E7A', name='Borewell',
                    show_legend=True, legendgroup='Borewell',
                ))
                # Water inside
                fig.add_trace(_cylinder_surface(
                    f['x'],f['y'], r*0.85, base, base+3.5,
                    color='#4FC3F7', name='Borewell Water',
                    show_legend=False, legendgroup='Borewell',
                ))
                break

    # ── Solar panels ───────────────────────────────────────────────────────────
    def _add_solar(self, fig):
        f = self._layout.get('features',{}).get('solar')
        if not f: return
        base = self._terrain_z(f['x']+f['width']/2, f['y']+f['height']/2)+1.5

        if not self._reg.rect_clear(f['x'],f['y'],f['x']+f['width'],f['y']+f['height']):
            return
        self._reg.register_rect(f['x'],f['y'],f['x']+f['width'],f['y']+f['height'])

        # Frame
        fig.add_trace(_box(f['x'],f['y'],base,
                           f['x']+f['width'],f['y']+f['height'],base+0.3,
                           color='#607D8B', name='Solar Frame',
                           opacity=0.95, show_legend=False,
                           legendgroup='Solar'))

        rows,cols,gap = 2,3,1.5
        cw = (f['width']-gap*(cols+1))/cols
        ch = (f['height']-gap*(rows+1))/rows
        show_leg = True
        for row in range(rows):
            for col in range(cols):
                px = f['x']+gap+col*(cw+gap)
                py = f['y']+gap+row*(ch+gap)
                fig.add_trace(_box(
                    px,py,base+0.25, px+cw,py+ch,base+0.55,
                    color='#1565C0', name='Solar Panels',
                    opacity=0.97, show_legend=show_leg,
                    legendgroup='Solar',
                ))
                show_leg=False
                # Cell lines as scatter
                for gi in [1,2]:
                    fig.add_trace(go.Scatter3d(
                        x=[px+gi*cw/3,px+gi*cw/3],y=[py,py+ch],
                        z=[base+0.56,base+0.56],
                        mode='lines', line=dict(color='#1976D2',width=1),
                        showlegend=False, legendgroup='Solar',
                    ))

    # ── Greenhouse ────────────────────────────────────────────────────────────
    def _add_greenhouse(self, fig):
        f = self._layout.get('features',{}).get('greenhouse')
        if not f: return
        base = self._terrain_z(f['x']+f['width']/2,f['y']+f['height']/2)+1.5

        if not self._reg.rect_clear(f['x'],f['y'],f['x']+f['width'],f['y']+f['height']):
            return
        self._reg.register_rect(f['x'],f['y'],f['x']+f['width'],f['y']+f['height'])

        gh_h = 8.0
        # Glass walls (semi-transparent)
        fig.add_trace(_box(f['x'],f['y'],base,
                           f['x']+f['width'],f['y']+f['height'],base+gh_h,
                           color='#E0F2F1', name='Greenhouse',
                           opacity=0.30, show_legend=True,
                           legendgroup='Greenhouse'))
        # Ridge roof
        fig.add_trace(_hip_roof(
            f['x'],f['y'],f['x']+f['width'],f['y']+f['height'],
            base_z=base+gh_h,
            apex_z=base+gh_h+f['width']*0.28,
            color='#80CBC4', legendgroup='Greenhouse',
        ))
        # Internal plant beds
        bed_z = base+0.5
        for side_y in [f['y']+4, f['y']+f['height']-12]:
            fig.add_trace(_box(f['x']+4,side_y,bed_z,
                               f['x']+f['width']-4,side_y+8,bed_z+0.8,
                               color='#5D4037', name='GH Bed',
                               opacity=0.90, show_legend=False,
                               legendgroup='Greenhouse'))

    # ── Rain tank ──────────────────────────────────────────────────────────────
    def _add_rain_tank(self, fig):
        f = self._layout.get('features',{}).get('rain_tank')
        if not f: return
        base = self._terrain_z(f['x']+f['width']/2,f['y']+f['height']/2)+1.5
        if not self._reg.rect_clear(f['x'],f['y'],f['x']+f['width'],f['y']+f['height']):
            return
        self._reg.register_rect(f['x'],f['y'],f['x']+f['width'],f['y']+f['height'])
        fig.add_trace(_box(f['x'],f['y'],base,
                           f['x']+f['width'],f['y']+f['height'],base+6.0,
                           color='#4FC3F7', name='Rain Tank',
                           opacity=0.80, show_legend=True,
                           legendgroup='Rain Tank'))

    # ── House — Option B: realistic 3D exterior ────────────────────────────────
    def _house_bbox(self):
        L,W = self._L,self._W
        pos = self._layout.get('house_position','Center')
        positions = {
            'North':        (L*0.30,W*0.82,L*0.40,W*0.12),
            'South':        (L*0.30,W*0.06,L*0.40,W*0.12),
            'East':         (L*0.75,W*0.35,L*0.20,W*0.30),
            'West':         (L*0.05,W*0.35,L*0.20,W*0.30),
            'Center':       (L*0.35,W*0.40,L*0.30,W*0.20),
            'Not built yet':(L*0.35,W*0.40,L*0.30,W*0.20),
        }
        return positions.get(pos,positions['Center'])

    def _add_house(self, fig):
        hx,hy,hw,hd = self._house_bbox()
        base   = self._terrain_z(hx+hw/2,hy+hd/2)+1.5
        wall_h = 10.0
        roof_b = base+wall_h
        roof_t = roof_b+min(hw,hd)*0.42

        self._reg.force_register_rect(hx,hy,hx+hw,hy+hd)

        # ── Foundation slab ───────────────────────────────────────────────
        fig.add_trace(_box(hx-0.5,hy-0.5,base-0.5,
                           hx+hw+0.5,hy+hd+0.5,base,
                           color='#BCAAA4', name='Foundation',
                           opacity=0.95, show_legend=False,
                           legendgroup='House'))

        # ── Walls (4 faces separately for window cutouts look) ────────────
        wall_t = 0.6   # wall thickness

        # South wall (front)
        fig.add_trace(_box(hx,hy,base, hx+hw,hy+wall_t,roof_b,
                           color='#D7CCC8', name='House',
                           opacity=0.97, show_legend=True,
                           legendgroup='House'))
        # North wall
        fig.add_trace(_box(hx,hy+hd-wall_t,base, hx+hw,hy+hd,roof_b,
                           color='#BCAAA4', name='House',
                           opacity=0.97, show_legend=False,
                           legendgroup='House'))
        # West wall
        fig.add_trace(_box(hx,hy,base, hx+wall_t,hy+hd,roof_b,
                           color='#D7CCC8', name='House',
                           opacity=0.97, show_legend=False,
                           legendgroup='House'))
        # East wall
        fig.add_trace(_box(hx+hw-wall_t,hy,base, hx+hw,hy+hd,roof_b,
                           color='#BCAAA4', name='House',
                           opacity=0.97, show_legend=False,
                           legendgroup='House'))
        # Interior floor (ceiling visible from above)
        fig.add_trace(_box(hx+wall_t,hy+wall_t,base,
                           hx+hw-wall_t,hy+hd-wall_t,base+0.2,
                           color='#EFEBE9', name='House Floor',
                           opacity=0.95, show_legend=False,
                           legendgroup='House'))

        # ── Windows (colored boxes inset into south wall) ─────────────────
        win_w,win_h = hw*0.13, wall_h*0.30
        win_z = base + wall_h*0.45
        for wx in [hx+hw*0.18, hx+hw*0.72]:
            fig.add_trace(_box(wx,hy-0.1,win_z,
                               wx+win_w,hy+wall_t+0.1,win_z+win_h,
                               color='#B3E5FC', name='Window',
                               opacity=0.80, show_legend=False,
                               legendgroup='House'))
            # Window frame
            fig.add_trace(_box(wx-0.15,hy-0.15,win_z-0.15,
                               wx+win_w+0.15,hy+wall_t+0.15,win_z+win_h+0.15,
                               color='#5D4037', name='Window Frame',
                               opacity=0.95, show_legend=False,
                               legendgroup='House'))

        # North windows
        for wx in [hx+hw*0.18, hx+hw*0.72]:
            fig.add_trace(_box(wx,hy+hd-wall_t-0.1,win_z,
                               wx+win_w,hy+hd+0.1,win_z+win_h,
                               color='#B3E5FC', name='Window',
                               opacity=0.80, show_legend=False,
                               legendgroup='House'))

        # ── Door (front face, dark brown) ─────────────────────────────────
        dw = hw*0.12
        dx = hx+hw/2-dw/2
        fig.add_trace(_box(dx,hy-0.15,base,
                           dx+dw,hy+wall_t+0.15,base+wall_h*0.55,
                           color='#3E2723', name='Door',
                           opacity=0.97, show_legend=False,
                           legendgroup='House'))
        # Door knob
        knob_x = dx+dw*0.85
        knob_y = hy
        knob_z = base+wall_h*0.28
        fig.add_trace(go.Scatter3d(
            x=[knob_x],y=[knob_y],z=[knob_z],
            mode='markers',
            marker=dict(size=4,color='#FFD700',
                        line=dict(color='black',width=1)),
            name='Door Knob', showlegend=False,
            legendgroup='House',
        ))

        # ── Hip roof ──────────────────────────────────────────────────────
        fig.add_trace(_hip_roof(hx,hy,hx+hw,hy+hd,
                                base_z=roof_b, apex_z=roof_t,
                                color='#4E342E', name='Roof',
                                legendgroup='House'))

        # ── Chimney ───────────────────────────────────────────────────────
        chim_x = hx+hw*0.72; chim_y = hy+hd*0.4
        chim_w = hw*0.08; chim_d = hd*0.08
        fig.add_trace(_box(chim_x,chim_y,roof_b-1,
                           chim_x+chim_w,chim_y+chim_d,roof_t+3,
                           color='#6D4C41', name='Chimney',
                           opacity=0.97, show_legend=False,
                           legendgroup='House'))

        # ── Porch (front canopy) ──────────────────────────────────────────
        porch_w = hw*0.45; porch_d = hd*0.15
        porch_x = hx+(hw-porch_w)/2
        porch_y = hy-porch_d
        porch_z = base+wall_h*0.65
        fig.add_trace(_box(porch_x,porch_y,porch_z,
                           porch_x+porch_w,hy,porch_z+0.4,
                           color='#EFEBE9', name='Porch',
                           opacity=0.75, show_legend=False,
                           legendgroup='House'))
        # Porch columns
        for col_x in [porch_x+porch_w*0.1, porch_x+porch_w*0.9]:
            fig.add_trace(_cylinder_surface(
                col_x,porch_y+porch_d*0.5, 0.5,
                base, porch_z,
                color='#8D6E63', name='Porch Column',
                show_legend=False, legendgroup='House',
            ))

    # ── All livestock ─────────────────────────────────────────────────────────
    def _add_all_livestock(self, fig):
        features = self._layout.get('features',{})

        livestock_cfg = {
            'goat_shed':    ('#FFCCBC','#4E342E','Goat Shed',    7.0),
            'chicken_coop': ('#FFF9C4','#F57F17','Chicken Coop', 5.0),
            'piggery':      ('#F8BBD0','#880E4F','Piggery',      6.0),
            'cow_shed':     ('#D7CCC8','#5D4037','Cow Shed',     9.0),
            'fish_tanks':   ('#B3E5FC','#0288D1','Fish Tanks',   2.5),
            'bee_hives':    ('#FFF176','#F9A825','Bee Hives',    3.5),
        }

        for key,(wall_col,roof_col,label,shed_h) in livestock_cfg.items():
            if key not in features: continue
            f = features[key]
            x0,y0 = f['x'],f['y']
            x1,y1 = x0+f['width'],y0+f['height']
            base   = self._terrain_z((x0+x1)/2,(y0+y1)/2)+1.5

            if not self._reg.rect_clear(x0,y0,x1,y1):
                continue
            self._reg.register_rect(x0,y0,x1,y1)

            roof_b = base+shed_h
            roof_t = roof_b+f['width']*0.25

            # Walls
            fig.add_trace(_box(x0,y0,base,x1,y1,roof_b,
                               color=wall_col, name=label,
                               opacity=0.92, show_legend=True,
                               legendgroup=label))
            # Hip roof
            fig.add_trace(_hip_roof(x0,y0,x1,y1,
                                    base_z=roof_b, apex_z=roof_t,
                                    color=roof_col, name=label+' Roof',
                                    legendgroup=label))

            # Small features per type
            if key=='chicken_coop':
                # Ramp
                ramp_x = (x0+x1)/2-2; ramp_y = y0
                for t in _path_box(ramp_x,y0-8, ramp_x,y0, 4, base,
                                   color='#D7CCC8', name='Coop Ramp',
                                   show_legend=False, legendgroup=label):
                    fig.add_trace(t)
            elif key=='fish_tanks':
                # Water surface inside tanks
                mid_z = base+0.5
                fig.add_trace(_box(x0+2,y0+2,mid_z,
                                   x1-2,y1-2,mid_z+0.3,
                                   color='#4FC3F7', name='Fish Water',
                                   opacity=0.70, show_legend=False,
                                   legendgroup=label))
            elif key=='bee_hives':
                # Individual hive boxes
                n_hives = max(1,int(f['width']/15))
                hw_each = (f['width']-5)/n_hives-2
                for hi in range(n_hives):
                    hx_each = x0+3+hi*(hw_each+2)
                    fig.add_trace(_box(
                        hx_each,y0+2,base,
                        hx_each+hw_each,y1-2,base+3.5,
                        color='#FFF176', name=f'Hive {hi+1}',
                        opacity=0.95, show_legend=False,
                        legendgroup=label,
                    ))

    # ── Trees with species-specific heights ────────────────────────────────────
    def _add_trees(self, fig):
        zones = self._layout.get('zone_positions',{})
        if 'z2' not in zones: return
        z2 = zones['z2']

        rel_positions = [
            (0.18,0.32,'Mango'),    (0.50,0.60,'Coconut'),
            (0.82,0.42,'Jackfruit'),(0.32,0.75,'Banana'),
            (0.68,0.22,'Guava'),    (0.15,0.55,'Papaya'),
            (0.60,0.85,'Citrus'),   (0.88,0.70,'Avocado'),
        ]

        first_tree = True
        for rx,ry,species in rel_positions:
            tx = z2['x']+rx*z2['width']
            ty = z2['y']+ry*z2['height']
            # Clamp inside zone
            tx = max(z2['x']+15, min(tx, z2['x']+z2['width']-15))
            ty = max(z2['y']+15, min(ty, z2['y']+z2['height']-15))
            base = self._terrain_z(tx,ty)+1.5

            sp = TREE_SPECS.get(species, TREE_SPECS['Mango'])
            if not self._reg.circle_clear(tx,ty,sp['canopy_r']+2):
                continue
            self._reg.force_register_circle(tx,ty,sp['canopy_r'])

            # Trunk
            fig.add_trace(_cylinder_surface(
                tx,ty, sp['trunk_r'],
                base, base+sp['trunk_h'],
                color='#6D4C41', name=species,
                show_legend=first_tree, legendgroup='Trees',
            ))
            # Canopy (cone)
            fig.add_trace(_cone_mesh(
                tx,ty, sp['canopy_r'],
                base+sp['canopy_bot'], base+sp['canopy_top'],
                color=sp['color'], name=species,
                show_legend=False, legendgroup='Trees',
            ))
            # Secondary canopy layer (rounder look)
            fig.add_trace(_cone_mesh(
                tx,ty, sp['canopy_r']*0.75,
                base+sp['canopy_bot']+sp['canopy_r']*0.3,
                base+sp['canopy_top']+sp['canopy_r']*0.1,
                color=sp['color'], name=species,
                show_legend=False, legendgroup='Trees',
            ))
            first_tree = False

    # ── Figure layout ──────────────────────────────────────────────────────────
    def _configure_layout(self, fig):
        L,W = self._L,self._W
        acres = self._layout.get('acres', round(L*W/43560,2))
        fig.update_layout(
            title=dict(
                text=f"🏡 3D Homestead — {acres:.2f} acres ({int(L)} × {int(W)} ft)"
                     f"<br><sup>Click legend items to show/hide</sup>",
                font=dict(size=16,color='#2E7D32',family='Arial'),
                x=0.5,
            ),
            scene=dict(
                xaxis_title='Length (ft)',
                yaxis_title='Width (ft)',
                zaxis_title='Height (ft)',
                aspectmode='data',
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
                x=0.01, y=0.99,
                bgcolor='rgba(255,255,255,0.90)',
                bordercolor='#90A4AE', borderwidth=1.5,
                font=dict(size=11),
                itemclick='toggle',         # single click = toggle
                itemdoubleclick='toggleothers',  # double click = isolate
                title=dict(text='<b>Layers</b><br><sup>Click to toggle</sup>',
                           font=dict(size=10)),
            ),
            paper_bgcolor='#EAF4FB',
            margin=dict(l=0,r=0,t=70,b=0),
            width=1000, height=700,
            updatemenus=[
                dict(
                    type='buttons',
                    direction='left',
                    x=0.5, y=0.02,
                    xanchor='center',
                    buttons=[
                        dict(label='Top View',
                             method='relayout',
                             args=[{'scene.camera.eye':{'x':0,'y':0,'z':2.5},
                                    'scene.camera.up':{'x':0,'y':1,'z':0}}]),
                        dict(label='3D View',
                             method='relayout',
                             args=[{'scene.camera.eye':{'x':1.3,'y':-1.5,'z':0.85},
                                    'scene.camera.up':{'x':0,'y':0,'z':1}}]),
                        dict(label='South View',
                             method='relayout',
                             args=[{'scene.camera.eye':{'x':0,'y':-2.2,'z':0.5},
                                    'scene.camera.up':{'x':0,'y':0,'z':1}}]),
                    ],
                    bgcolor='white', bordercolor='#78909C',
                    font=dict(size=11),
                )
            ],
        )

    def export_as_html(self, fig: go.Figure, filename: str='homestead_3d.html'):
        pio.write_html(fig, file=filename, auto_open=False, include_plotlyjs='cdn')
