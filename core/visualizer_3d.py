"""
Homestead Architect Pro 2026 — ULTRA EDITION v2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Features:
  ✅ User interview data se dynamic layout
  ✅ Sabhi livestock user selection se auto-place
  ✅ Kitchen Garden (Zone 1) clearly visible
  ✅ Food Forest trees = user ka tree_count
  ✅ Realistic terrain with grass texture
  ✅ Realistic buildings with windows/doors
  ✅ House position user ke anusar
  ✅ Slope direction terrain me reflect
  ✅ Water source (borewell/pond) auto show
  ✅ Info box hide/show toggle button
  ✅ HTML download working
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from typing import Dict, Any, List, Tuple
import math


class Visualizer3D:
    """
    User interview data se bilkul sahi 3D homestead map banata hai.
    Layout engine se jo bhi data aata hai, usse directly use karta hai.
    Agar koi feature layout me nahi hai, to khud calculate karke place karta hai.
    """

    # ── Zone Colors (semi-transparent slabs) ──
    ZONE_COLORS = {
        'z0': '#D7CCC8',   # Residential - warm gray
        'z1': '#A5D6A7',   # Kitchen Garden - light green
        'z2': '#2E7D32',   # Food Forest - dark green
        'z3': '#FFF9C4',   # Pasture - light yellow
        'z4': '#CE93D8',   # Buffer - light purple
    }
    ZONE_NAMES = {
        'z0': 'Zone 0 – Ghar (House)',
        'z1': 'Zone 1 – Kitchen Garden',
        'z2': 'Zone 2 – Food Forest',
        'z3': 'Zone 3 – Pasture/Crops',
        'z4': 'Zone 4 – Buffer/Wild',
    }

    # ── Livestock placement config: key → (wall_color, roof_color, label, shed_height, emoji) ──
    LIVESTOCK_CONFIG = {
        'chicken_coop': ('#FFF9C4', '#F57F17', 'Chicken Coop', 5.0, '🐔'),
        'goat_shed':    ('#FFCCBC', '#4E342E', 'Goat Shed',    7.5, '🐐'),
        'piggery':      ('#F8BBD0', '#880E4F', 'Piggery',      6.5, '🐷'),
        'cow_shed':     ('#D7CCC8', '#5D4037', 'Cow Shed',    10.0, '🐄'),
        'fish_tanks':   ('#B3E5FC', '#0288D1', 'Fish Pond',    2.5, '🐟'),
        'bee_hives':    ('#FFF176', '#F9A825', 'Bee Hives',    3.5, '🐝'),
    }

    # Livestock name → shed key mapping (user interview options)
    ANIMAL_TO_KEY = {
        'Chickens': 'chicken_coop',
        'Goats':    'goat_shed',
        'Pigs':     'piggery',
        'Cows':     'cow_shed',
        'Fish':     'fish_tanks',
        'Bees':     'bee_hives',
    }

    # ══════════════════════════════════════════════════
    #  MAIN ENTRY POINT
    # ══════════════════════════════════════════════════

    def create(self, layout: Dict[str, Any]):
        """Streamlit me 3D map render karo."""

        if not layout or 'dimensions' not in layout:
            st.info("👈 पहले 'Design' टैब में अपना नक्शा जनरेट करें।")
            return

        # Layout se dimensions nikalo
        dims = layout.get('dimensions', {})
        L = float(dims.get('L', dims.get('length', 300)))
        W = float(dims.get('W', dims.get('width', 300)))

        # Agar layout me L/W nahi, try karo
        if L <= 0:
            L = 300.0
        if W <= 0:
            W = 300.0

        # Poora layout recalculate with user data
        computed = self._compute_full_layout(layout, L, W)

        fig = go.Figure()

        # Layer by layer add karo (bottom to top)
        self._add_terrain(fig, computed, L, W)
        self._add_ground_zones(fig, computed, L, W)
        self._add_paths(fig, computed, L, W)
        self._add_house_3d(fig, computed, L, W)
        self._add_kitchen_garden(fig, computed, L, W)
        self._add_water_features(fig, computed, L, W)
        self._add_livestock_sheds(fig, computed, L, W)
        self._add_food_forest_trees(fig, computed, L, W)
        self._add_pasture_crops(fig, computed, L, W)
        self._add_3d_labels(fig, computed, L, W)

        # Layout settings
        acres = layout.get('acres', round(L * W / 43560, 2))
        loc_name = layout.get('location', 'Custom Plot')
        title_text = f"🏡 {loc_name} — {acres:.2f} acres ({int(L)}×{int(W)} ft)"

        fig.update_layout(
            title=dict(
                text=title_text,
                font=dict(size=16, color='#1B5E20', family='Arial Black'),
                x=0.5,
            ),
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    x=0.02,
                    y=1.10,
                    showactive=True,
                    bgcolor='rgba(255,255,255,0.9)',
                    bordercolor='#2E7D32',
                    font=dict(size=12),
                    buttons=[
                        dict(
                            label="📊 Info दिखाओ",
                            method="relayout",
                            args=[{
                                "title.text": title_text,
                                "showlegend": True
                            }]
                        ),
                        dict(
                            label="🗺️ Full Map",
                            method="relayout",
                            args=[{
                                "title.text": "",
                                "showlegend": False
                            }]
                        ),
                    ]
                )
            ],
            scene=dict(
                xaxis=dict(title='Length (ft)', showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
                yaxis=dict(title='Width (ft)',  showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
                zaxis=dict(title='Height (ft)', showgrid=False, range=[-2, max(L, W) * 0.15]),
                aspectmode='manual',
                aspectratio=dict(x=1.0, y=W/L, z=0.25),
                bgcolor='#C8E6C9',
                camera=dict(
                    eye=dict(x=1.6, y=-1.6, z=1.1),
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=0, y=0, z=-0.1),
                ),
            ),
            legend=dict(
                x=0.01, y=0.98,
                bgcolor='rgba(255,255,255,0.88)',
                bordercolor='#ccc',
                borderwidth=1,
                font=dict(size=10),
                tracegroupgap=2,
            ),
            paper_bgcolor='#E8F5E9',
            margin=dict(l=0, r=0, t=70, b=0),
            height=720,
        )

        st.plotly_chart(fig, use_container_width=True)

        # HTML Download
        col1, col2 = st.columns([3, 1])
        with col1:
            try:
                html_str = fig.to_html(include_plotlyjs='cdn', full_html=True)
                st.download_button(
                    label="📥 3D Map Download करो (HTML - Offline भी चलेगा)",
                    data=html_str,
                    file_name=f"homestead_3d_{loc_name.replace(' ', '_').replace(',', '')}.html",
                    mime="text/html",
                    use_container_width=True
                )
            except Exception:
                pass
        with col2:
            st.info(f"🌳 {computed.get('tree_count', 15)} Trees")

    # ══════════════════════════════════════════════════
    #  LAYOUT COMPUTATION - User data se sab calculate
    # ══════════════════════════════════════════════════

    def _compute_full_layout(self, layout: Dict, L: float, W: float) -> Dict:
        """
        User interview answers + layout engine data se
        poora placement dictionary banao.
        """
        answers = layout.get('answers', {})

        # House position
        house_pos = layout.get('house_position', 'North')
        if house_pos not in ['North', 'South', 'East', 'West', 'Center']:
            house_pos = 'Center'

        # Slope
        slope = layout.get('slope', 'Flat')

        # Water source
        water_source = layout.get('water_source', 'None yet')

        # Livestock list (user ne select kiya)
        raw_livestock = layout.get('livestock', [])
        if isinstance(raw_livestock, list):
            livestock_list = [a for a in raw_livestock if a and a != 'None']
        else:
            livestock_list = []

        # Tree count
        tree_count = layout.get('tree_count', 15)
        if not isinstance(tree_count, int):
            try:
                tree_count = int(tree_count)
            except Exception:
                tree_count = 15
        tree_count = max(3, min(50, tree_count))

        # ── House position calculate ──
        hw = L * 0.18   # house width
        hd = W * 0.14   # house depth
        margin = L * 0.05

        house_positions = {
            'North':  (L * 0.41, W * 0.80, hw, hd),
            'South':  (L * 0.41, W * 0.06, hw, hd),
            'East':   (L * 0.76, W * 0.43, hw * 0.9, hd * 1.2),
            'West':   (L * 0.06, W * 0.43, hw * 0.9, hd * 1.2),
            'Center': (L * 0.41, W * 0.43, hw, hd),
        }
        hx, hy, hw_, hd_ = house_positions[house_pos]

        # ── Zone layout (house ke position ke hisab se) ──
        # Zone 1 (Kitchen Garden) house ke paas
        # Zone 2 (Food Forest) plot ka ek bada hissa
        # Zone 3 (Pasture) livestock ke paas
        # Zone 4 (Buffer) edges pe

        if house_pos == 'North':
            z1 = {'x': hx - hw_*0.3, 'y': hy - hd_*2.2, 'w': hw_*1.6, 'h': hd_*2.0}   # south of house
            z2 = {'x': L*0.05, 'y': W*0.35, 'w': L*0.38, 'h': W*0.38}
            z3 = {'x': L*0.52, 'y': W*0.05, 'w': L*0.42, 'h': W*0.55}
            z4 = {'x': L*0.0,  'y': W*0.0,  'w': L*0.04, 'h': W*1.0}
        elif house_pos == 'South':
            z1 = {'x': hx - hw_*0.3, 'y': hy + hd_*1.1, 'w': hw_*1.6, 'h': hd_*2.0}
            z2 = {'x': L*0.05, 'y': W*0.40, 'w': L*0.38, 'h': W*0.50}
            z3 = {'x': L*0.50, 'y': W*0.25, 'w': L*0.44, 'h': W*0.65}
            z4 = {'x': L*0.0,  'y': W*0.96, 'w': L*1.0,  'h': W*0.04}
        elif house_pos == 'East':
            z1 = {'x': hx - hw_*2.2, 'y': hy, 'w': hw_*2.0, 'h': hd_*1.2}
            z2 = {'x': L*0.05, 'y': W*0.05, 'w': L*0.55, 'h': W*0.42}
            z3 = {'x': L*0.05, 'y': W*0.55, 'w': L*0.55, 'h': W*0.40}
            z4 = {'x': L*0.0,  'y': W*0.0,  'w': L*0.04, 'h': W*1.0}
        elif house_pos == 'West':
            z1 = {'x': hx + hw_*1.1, 'y': hy, 'w': hw_*2.0, 'h': hd_*1.2}
            z2 = {'x': L*0.42, 'y': W*0.05, 'w': L*0.53, 'h': W*0.42}
            z3 = {'x': L*0.42, 'y': W*0.55, 'w': L*0.53, 'h': W*0.40}
            z4 = {'x': L*0.96, 'y': W*0.0,  'w': L*0.04, 'h': W*1.0}
        else:  # Center
            z1 = {'x': hx + hw_*1.1, 'y': hy, 'w': hw_*1.5, 'h': hd_}
            z2 = {'x': L*0.05, 'y': W*0.05, 'w': L*0.32, 'h': W*0.38}
            z3 = {'x': L*0.63, 'y': W*0.05, 'w': L*0.32, 'h': W*0.38}
            z4 = {'x': L*0.05, 'y': W*0.65, 'w': L*0.90, 'h': W*0.30}

        # ── Livestock placement ──
        # Zone 3 me systematic grid pe place karo
        z3_x0, z3_y0 = z3['x'], z3['y']
        z3_w, z3_h = z3['w'], z3['h']

        shed_placements = {}
        num_animals = len(livestock_list)

        if num_animals > 0:
            # Grid me rakhna: max 3 per row
            cols = min(3, num_animals)
            rows = math.ceil(num_animals / cols)
            cell_w = z3_w / cols
            cell_h = z3_h / rows

            for i, animal in enumerate(livestock_list):
                key = self.ANIMAL_TO_KEY.get(animal)
                if not key:
                    continue
                row = i // cols
                col = i % cols
                # Shed size
                sh_w = cell_w * 0.65
                sh_h = cell_h * 0.60
                # Padding
                pad_x = cell_w * 0.17
                pad_y = cell_h * 0.20
                sx = z3_x0 + col * cell_w + pad_x
                sy = z3_y0 + row * cell_h + pad_y

                # Clamp inside zone
                sx = max(z3_x0 + 2, min(sx, z3_x0 + z3_w - sh_w - 2))
                sy = max(z3_y0 + 2, min(sy, z3_y0 + z3_h - sh_h - 2))

                shed_placements[key] = {
                    'x': sx, 'y': sy,
                    'width': sh_w, 'height': sh_h
                }

        # ── Water feature position ──
        water_feat = {}
        if water_source in ['Borewell/Well', 'Municipal Supply']:
            # Borewell near house
            water_feat['borewell'] = {
                'x': hx + hw_ + L*0.03,
                'y': hy + hd_ * 0.4,
                'radius': max(3.0, L * 0.012)
            }
        if water_source in ['Rainwater', 'River/Pond']:
            # Pond in food forest area
            water_feat['pond'] = {
                'x': z2['x'] + z2['w'] * 0.6,
                'y': z2['y'] + z2['h'] * 0.5,
                'radius': max(8.0, min(L * 0.04, 20.0))
            }
        # Always add small pond in food forest for ecosystem
        if 'pond' not in water_feat and water_source not in ['Borewell/Well', 'Municipal Supply']:
            water_feat['pond'] = {
                'x': z2['x'] + z2['w'] * 0.5,
                'y': z2['y'] + z2['h'] * 0.6,
                'radius': max(6.0, L * 0.025)
            }

        return {
            'L': L, 'W': W,
            'slope': slope,
            'house_pos': house_pos,
            'house': {'x': hx, 'y': hy, 'w': hw_, 'h': hd_},
            'zones': {
                'z1': z1,   # Kitchen Garden
                'z2': z2,   # Food Forest
                'z3': z3,   # Pasture
                'z4': z4,   # Buffer
            },
            'sheds': shed_placements,
            'water': water_feat,
            'tree_count': tree_count,
            'livestock_list': livestock_list,
            'loc_name': layout.get('location', 'Custom Plot'),
        }

    # ══════════════════════════════════════════════════
    #  TERRAIN - Realistic grass with slope
    # ══════════════════════════════════════════════════

    def _add_terrain(self, fig, c: Dict, L: float, W: float):
        """Realistic grass terrain with gentle undulation + slope."""
        nx, ny = 45, 45
        x = np.linspace(0, L, nx)
        y = np.linspace(0, W, ny)
        X, Y = np.meshgrid(x, y)

        # Slope
        slope = c.get('slope', 'Flat')
        Z = np.zeros_like(X, dtype=float)
        slope_factor = max(L, W) * 0.015

        if slope == 'South':   Z += Y / W * slope_factor
        elif slope == 'North': Z += (1 - Y / W) * slope_factor
        elif slope == 'East':  Z += X / L * slope_factor
        elif slope == 'West':  Z += (1 - X / L) * slope_factor
        elif slope == 'Mixed/Undulating':
            Z += np.sin(X / L * np.pi) * slope_factor * 0.5 + np.cos(Y / W * np.pi) * slope_factor * 0.3

        # Subtle noise for natural look
        np.random.seed(42)
        noise = np.random.normal(0, slope_factor * 0.06, X.shape)
        # Smooth the noise
        from scipy.ndimage import gaussian_filter
        try:
            noise = gaussian_filter(noise, sigma=2)
        except Exception:
            pass
        Z += noise

        # Grass color: darker green on higher areas, lighter on low
        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z,
            colorscale=[
                [0.0,  '#558B2F'],   # lower - darker
                [0.3,  '#689F38'],
                [0.6,  '#7CB342'],
                [0.85, '#8BC34A'],
                [1.0,  '#9CCC65'],   # higher - lighter
            ],
            showscale=False,
            opacity=1.0,
            name='🌿 Terrain',
            showlegend=True,
            lighting=dict(ambient=0.7, diffuse=0.9, specular=0.1),
            contours=dict(
                z=dict(show=False),
            ),
            hovertemplate='Elevation: %{z:.1f} ft<extra>Terrain</extra>',
        ))

        # Ground border
        bx = [0, L, L, 0, 0]
        by = [0, 0, W, W, 0]
        bz = [0, 0, 0, 0, 0]
        fig.add_trace(go.Scatter3d(
            x=bx, y=by, z=bz,
            mode='lines',
            line=dict(color='#33691E', width=3),
            name='Plot Boundary',
            showlegend=True,
            hoverinfo='skip',
        ))

    # ══════════════════════════════════════════════════
    #  GROUND ZONES - Colored semi-transparent slabs
    # ══════════════════════════════════════════════════

    def _add_ground_zones(self, fig, c: Dict, L: float, W: float):
        """Har zone ko ek colored transparent slab ke roop me dikhao."""
        slope = c.get('slope', 'Flat')
        sf = max(L, W) * 0.015

        for zid, z in c['zones'].items():
            x0, y0 = z['x'], z['y']
            x1, y1 = x0 + z['w'], y0 + z['h']

            # Slope adjust
            def sz(xi, yi):
                base = 0.3
                if slope == 'South':   return base + yi / W * sf
                elif slope == 'North': return base + (1 - yi/W) * sf
                elif slope == 'East':  return base + xi / L * sf
                elif slope == 'West':  return base + (1 - xi/L) * sf
                return base

            # Zone slab as flat mesh at zone height
            xg = np.linspace(x0, x1, 8)
            yg = np.linspace(y0, y1, 8)
            XG, YG = np.meshgrid(xg, yg)
            ZG = np.array([[sz(xi, yi) for xi in xg] for yi in yg])

            col = self.ZONE_COLORS.get(zid, '#CCCCCC')
            name = self.ZONE_NAMES.get(zid, zid)

            fig.add_trace(go.Surface(
                x=XG, y=YG, z=ZG,
                colorscale=[[0, col], [1, col]],
                showscale=False,
                opacity=0.45,
                name=name,
                showlegend=True,
                hovertemplate=f'{name}<extra></extra>',
            ))

            # Zone border
            bx = [x0, x1, x1, x0, x0]
            by = [y0, y0, y1, y1, y0]
            bz_ = [sz(xx, yy) + 0.2 for xx, yy in zip(bx, by)]
            fig.add_trace(go.Scatter3d(
                x=bx, y=by, z=bz_,
                mode='lines',
                line=dict(color=col, width=2),
                showlegend=False,
                hoverinfo='skip',
            ))

    # ══════════════════════════════════════════════════
    #  PATHS - Gravel paths between zones
    # ══════════════════════════════════════════════════

    def _add_paths(self, fig, c: Dict, L: float, W: float):
        """Main path from house to plot edges."""
        h = c['house']
        hcx = h['x'] + h['w'] / 2
        hcy = h['y'] + h['h'] / 2

        path_color = '#D2B48C'   # tan/gravel color

        # Main path to south edge
        px = [hcx - 2, hcx + 2, hcx + 2, hcx - 2, hcx - 2]
        py = [0, 0, hcy, hcy, 0]
        pz = [0.5] * 5

        fig.add_trace(go.Scatter3d(
            x=px, y=py, z=pz,
            mode='lines',
            line=dict(color=path_color, width=6),
            name='Path',
            showlegend=True,
            hoverinfo='skip',
        ))

        # Cross path (horizontal)
        fig.add_trace(go.Scatter3d(
            x=[0, L], y=[hcy, hcy], z=[0.5, 0.5],
            mode='lines',
            line=dict(color=path_color, width=4, dash='dot'),
            showlegend=False,
            hoverinfo='skip',
        ))

    # ══════════════════════════════════════════════════
    #  HOUSE - Realistic with roof, door, windows
    # ══════════════════════════════════════════════════

    def _add_house_3d(self, fig, c: Dict, L: float, W: float):
        h = c['house']
        x0, y0 = h['x'], h['y']
        x1, y1 = x0 + h['w'], y0 + h['h']
        wall_h = max(L, W) * 0.055   # ~16 ft for 300ft plot
        roof_peak = wall_h * 1.4

        # Foundation slab
        fig.add_trace(self._flat_slab(x0-1, y0-1, x1+1, y1+1, 0.2, 1.5,
                                       '#BDBDBD', 'House Foundation', show_legend=False))

        # Walls (box)
        fig.add_trace(self._box_mesh(x0, y0, 1.5, x1, y1, 1.5 + wall_h,
                                      '#8D6E63', '🏠 Main House', opacity=0.95))

        # Windows (small light-colored boxes)
        win_w = h['w'] * 0.12
        win_h = wall_h * 0.3
        win_z0 = 1.5 + wall_h * 0.45
        # Front windows
        for wx in [x0 + h['w']*0.18, x0 + h['w']*0.60]:
            fig.add_trace(self._box_mesh(wx, y0 - 0.3, win_z0,
                                          wx + win_w, y0, win_z0 + win_h,
                                          '#B3E5FC', 'Window', opacity=0.8, show_legend=False))

        # Door
        door_w = h['w'] * 0.14
        door_h = wall_h * 0.55
        door_x = x0 + h['w']*0.43 - door_w/2
        fig.add_trace(self._box_mesh(door_x, y0 - 0.3, 1.5,
                                      door_x + door_w, y0, 1.5 + door_h,
                                      '#5D4037', 'Door', opacity=1.0, show_legend=False))

        # Hip Roof
        fig.add_trace(self._hip_roof(x0, y0, x1, y1,
                                      1.5 + wall_h, 1.5 + roof_peak,
                                      '#4E342E', '🏠 Roof'))

        # Chimney
        cx = x1 - h['w'] * 0.15
        cy = y0 + h['h'] * 0.3
        fig.add_trace(self._box_mesh(cx, cy, 1.5 + wall_h, cx + h['w']*0.04, cy + h['h']*0.06,
                                      1.5 + roof_peak + wall_h*0.2,
                                      '#616161', 'Chimney', opacity=1.0, show_legend=False))

    # ══════════════════════════════════════════════════
    #  KITCHEN GARDEN - Zone 1, clearly visible
    # ══════════════════════════════════════════════════

    def _add_kitchen_garden(self, fig, c: Dict, L: float, W: float):
        """Kitchen garden: raised beds, small plants, clearly labeled."""
        z = c['zones']['z1']
        x0, y0 = z['x'], z['y']
        gw, gh = z['w'], z['h']

        # Raised bed rows
        bed_color = '#5D4037'       # dark brown soil
        plant_color = '#1B5E20'    # dark green plants
        n_beds = max(2, min(5, int(gh / 15)))
        bed_h_each = gh / (n_beds * 2)
        bed_w = gw * 0.75
        bed_x0 = x0 + gw * 0.12

        for i in range(n_beds):
            by0 = y0 + i * (gh / n_beds) + gh * 0.08
            by1 = by0 + bed_h_each
            bx1 = bed_x0 + bed_w

            # Soil bed (raised)
            fig.add_trace(self._box_mesh(bed_x0, by0, 1.5, bx1, by1, 2.8,
                                          bed_color, '🥬 Kitchen Garden', opacity=0.9,
                                          show_legend=(i == 0)))

            # Plants on bed (small green bumps)
            n_plants = max(3, int(bed_w / 10))
            for j in range(n_plants):
                px = bed_x0 + (j + 0.5) * (bed_w / n_plants)
                py = (by0 + by1) / 2
                pr = min(bed_w / n_plants * 0.35, 4.0)
                fig.add_trace(self._hemisphere(px, py, 2.8, pr, plant_color,
                                                show_legend=False))

        # Compost bin (small cube at corner)
        cx = x0 + gw * 0.82
        cy = y0 + gh * 0.65
        csz = min(gw, gh) * 0.12
        fig.add_trace(self._box_mesh(cx, cy, 1.5, cx+csz, cy+csz, 1.5+csz*1.5,
                                      '#795548', 'Compost', opacity=0.9, show_legend=False))

    # ══════════════════════════════════════════════════
    #  WATER FEATURES
    # ══════════════════════════════════════════════════

    def _add_water_features(self, fig, c: Dict, L: float, W: float):
        """Borewell aur Pond."""
        water = c.get('water', {})

        if 'borewell' in water:
            f = water['borewell']
            rw = f['radius']
            t_w = np.linspace(0, 2*np.pi, 28)
            z_w = np.array([1.5, 1.5 + rw * 2.5])
            Tw, Zw = np.meshgrid(t_w, z_w)
            fig.add_trace(go.Surface(
                x=f['x'] + rw * np.cos(Tw),
                y=f['y'] + rw * np.sin(Tw),
                z=Zw,
                colorscale=[[0, '#546E7A'], [1, '#90A4AE']],
                showscale=False,
                name='💧 Borewell',
                showlegend=True,
                opacity=0.95,
            ))
            # Cap on top
            fig.add_trace(self._flat_slab(
                f['x']-rw, f['y']-rw, f['x']+rw, f['y']+rw,
                1.5 + rw*2.5, 1.5 + rw*2.8,
                '#37474F', 'Borewell Cap', show_legend=False
            ))

        if 'pond' in water:
            f = water['pond']
            r = f['radius']
            rg = np.linspace(0, r, 14)
            tg = np.linspace(0, 2*np.pi, 36)
            R, T = np.meshgrid(rg, tg)
            # Pond bowl shape
            Z_pond = -1.0 * (1 - (R/r)**2)   # concave
            fig.add_trace(go.Surface(
                x=f['x'] + R * np.cos(T),
                y=f['y'] + R * np.sin(T),
                z=Z_pond,
                colorscale=[
                    [0.0, '#01579B'],
                    [0.4, '#0288D1'],
                    [0.7, '#4FC3F7'],
                    [1.0, '#80DEEA'],
                ],
                showscale=False,
                name='🐠 Pond / Water',
                showlegend=True,
                opacity=0.88,
            ))

    # ══════════════════════════════════════════════════
    #  LIVESTOCK SHEDS - User selection se dynamic
    # ══════════════════════════════════════════════════

    def _add_livestock_sheds(self, fig, c: Dict, L: float, W: float):
        """Sirf user ke selected animals ke shed banao, sahi jagah."""
        sheds = c.get('sheds', {})

        for key, f in sheds.items():
            if key not in self.LIVESTOCK_CONFIG:
                continue
            wc, rc, lbl, sh_height, emoji = self.LIVESTOCK_CONFIG[key]

            x0, y0 = f['x'], f['y']
            sw, sd = f['width'], f['height']

            bz = 1.5
            top_z = bz + sh_height
            roof_z = top_z + sw * 0.22

            # Shed walls
            fig.add_trace(self._box_mesh(
                x0, y0, bz, x0+sw, y0+sd, top_z,
                wc, f'{emoji} {lbl}', opacity=0.92
            ))

            # Shed roof
            fig.add_trace(self._hip_roof(
                x0, y0, x0+sw, y0+sd,
                top_z, roof_z,
                rc, f'{lbl} Roof'
            ))

            # Small door on shed
            dw = sw * 0.20
            fig.add_trace(self._box_mesh(
                x0 + sw*0.4, y0 - 0.2, bz,
                x0 + sw*0.4 + dw, y0, bz + sh_height*0.6,
                '#4E342E', 'Shed Door', opacity=1.0, show_legend=False
            ))

            # Fenced area in front
            fence_pts = [
                (x0 - sd*0.1, y0 - sd*0.6),
                (x0 + sw + sd*0.1, y0 - sd*0.6),
                (x0 + sw + sd*0.1, y0),
                (x0 - sd*0.1, y0),
                (x0 - sd*0.1, y0 - sd*0.6),
            ]
            fig.add_trace(go.Scatter3d(
                x=[p[0] for p in fence_pts],
                y=[p[1] for p in fence_pts],
                z=[bz] * len(fence_pts),
                mode='lines',
                line=dict(color='#795548', width=3),
                showlegend=False,
                hoverinfo='skip',
            ))

    # ══════════════════════════════════════════════════
    #  FOOD FOREST TREES - User ke tree_count se
    # ══════════════════════════════════════════════════

    def _add_food_forest_trees(self, fig, c: Dict, L: float, W: float):
        """Food Forest me user ke tree_count ke hisab se trees lagao."""
        z2 = c['zones']['z2']
        tree_count = c.get('tree_count', 15)
        water = c.get('water', {})

        x0, y0 = z2['x'], z2['y']
        zw, zh = z2['w'], z2['h']

        # Pond area avoid karna
        pond_x = water.get('pond', {}).get('x', -999)
        pond_y = water.get('pond', {}).get('y', -999)
        pond_r = water.get('pond', {}).get('radius', 10)

        # Tree sizes (variety)
        tree_types = [
            # canopy_r, height, color, label
            (8.0, 18.0, '#1B5E20', 'Mango'),
            (7.5, 16.0, '#2E7D32', 'Jackfruit'),
            (6.0, 14.0, '#388E3C', 'Coconut'),
            (5.5, 13.0, '#43A047', 'Guava'),
            (5.0, 12.0, '#4CAF50', 'Banana'),
            (4.5, 11.0, '#66BB6A', 'Papaya'),
            (4.0, 10.0, '#81C784', 'Lemon'),
            (3.5,  9.0, '#A5D6A7', 'Curry Leaf'),
        ]

        # Quasi-random but deterministic positions
        np.random.seed(99)
        positions = []
        attempts = 0
        min_spacing = min(zw, zh) * 0.12

        while len(positions) < tree_count and attempts < tree_count * 15:
            attempts += 1
            rx = np.random.uniform(0.05, 0.95)
            ry = np.random.uniform(0.05, 0.95)
            tx = x0 + rx * zw
            ty = y0 + ry * zh

            # Avoid pond
            if abs(tx - pond_x) < pond_r * 1.5 and abs(ty - pond_y) < pond_r * 1.5:
                continue

            # Avoid too close to other trees
            too_close = any(
                math.hypot(tx - px, ty - py) < min_spacing
                for px, py in positions
            )
            if too_close:
                continue

            positions.append((tx, ty))

        # Draw trees
        tree_legend_added = set()
        for idx, (tx, ty) in enumerate(positions):
            ttype = tree_types[idx % len(tree_types)]
            canopy_r, height, color, t_label = ttype
            # Scale trees to plot size
            scale = max(L, W) / 300.0
            cr = canopy_r * scale
            h_tree = height * scale

            trunk_r = max(0.8, cr * 0.14)
            show_leg = t_label not in tree_legend_added
            if show_leg:
                tree_legend_added.add(t_label)

            for trace in self._cone_tree(
                tx, ty,
                trunk_bot_z=1.5,
                trunk_top_z=1.5 + h_tree * 0.38,
                canopy_bot_z=1.5 + h_tree * 0.35,
                canopy_top_z=1.5 + h_tree,
                canopy_r=cr,
                trunk_r=trunk_r,
                color_canopy=color,
                label=f'🌳 {t_label}',
                show_legend=show_leg,
            ):
                fig.add_trace(trace)

    # ══════════════════════════════════════════════════
    #  PASTURE / CROPS decoration
    # ══════════════════════════════════════════════════

    def _add_pasture_crops(self, fig, c: Dict, L: float, W: float):
        """Zone 3 me crop rows dikhao (sirf agar koi livestock nahi)."""
        sheds = c.get('sheds', {})
        z3 = c['zones']['z3']
        x0, y0 = z3['x'], z3['y']
        gw, gh = z3['w'], z3['h']

        # Agar sheds hain, crops nahi dikhate (overlap avoid)
        if sheds:
            return

        # Crop rows
        n_rows = max(3, int(gh / 20))
        for i in range(n_rows):
            ry = y0 + (i + 0.5) * (gh / n_rows)
            fig.add_trace(go.Scatter3d(
                x=[x0 + gw*0.05, x0 + gw*0.95],
                y=[ry, ry],
                z=[1.8, 1.8],
                mode='lines',
                line=dict(color='#558B2F', width=4),
                showlegend=(i == 0),
                name='🌾 Crop Rows' if i == 0 else '',
                hoverinfo='skip',
            ))

    # ══════════════════════════════════════════════════
    #  3D LABELS
    # ══════════════════════════════════════════════════

    def _add_3d_labels(self, fig, c: Dict, L: float, W: float):
        """Sabhi structures ke upar labels."""
        scale = max(L, W) / 300.0
        label_z_offset = max(L, W) * 0.07

        labels = []

        # House label
        h = c['house']
        labels.append({
            'x': h['x'] + h['w']/2,
            'y': h['y'] + h['h']/2,
            'z': label_z_offset,
            'text': '🏠 Main House'
        })

        # Zone labels
        for zid, z in c['zones'].items():
            labels.append({
                'x': z['x'] + z['w'] * 0.45,
                'y': z['y'] + z['h'] * 0.9,
                'z': label_z_offset * 0.45,
                'text': self.ZONE_NAMES.get(zid, zid).split('–')[-1].strip()
            })

        # Shed labels
        for key, f in c.get('sheds', {}).items():
            if key in self.LIVESTOCK_CONFIG:
                _, _, lbl, sh_h, emoji = self.LIVESTOCK_CONFIG[key]
                labels.append({
                    'x': f['x'] + f['width']/2,
                    'y': f['y'] + f['height']/2,
                    'z': sh_h * scale + label_z_offset * 0.5,
                    'text': f'{emoji} {lbl}'
                })

        # Water labels
        for wkey, wf in c.get('water', {}).items():
            emoji = '💧' if wkey == 'borewell' else '🐠'
            name = 'Borewell' if wkey == 'borewell' else 'Pond'
            labels.append({
                'x': wf['x'],
                'y': wf['y'],
                'z': label_z_offset * 0.6,
                'text': f'{emoji} {name}'
            })

        fig.add_trace(go.Scatter3d(
            x=[d['x'] for d in labels],
            y=[d['y'] for d in labels],
            z=[d['z'] for d in labels],
            mode='text',
            text=[d['text'] for d in labels],
            textfont=dict(
                size=11,
                color='#1A237E',
                family='Arial Black',
            ),
            name='Labels',
            showlegend=False,
        ))

    # ══════════════════════════════════════════════════
    #  GEOMETRY PRIMITIVES
    # ══════════════════════════════════════════════════

    @staticmethod
    def _box_mesh(x0, y0, z0, x1, y1, z1, color, name,
                  opacity=0.88, show_legend=True) -> go.Mesh3d:
        """Solid 3D box."""
        vx = [x0, x1, x1, x0,  x0, x1, x1, x0]
        vy = [y0, y0, y1, y1,  y0, y0, y1, y1]
        vz = [z0, z0, z0, z0,  z1, z1, z1, z1]
        fi = [0, 0, 4, 4, 0, 0, 2, 2, 0, 0, 1, 1]
        fj = [1, 2, 5, 6, 1, 5, 3, 7, 3, 7, 2, 6]
        fk = [2, 3, 6, 7, 5, 4, 7, 6, 7, 4, 6, 5]
        return go.Mesh3d(
            x=vx, y=vy, z=vz, i=fi, j=fj, k=fk,
            color=color, opacity=opacity, name=name,
            showlegend=show_legend, flatshading=True,
            lighting=dict(ambient=0.68, diffuse=0.92, specular=0.25, roughness=0.55, fresnel=0.15),
        )

    @staticmethod
    def _flat_slab(x0, y0, x1, y1, z0, z1, color, name, show_legend=False) -> go.Mesh3d:
        """Thin flat slab (for foundation, etc.)."""
        vx = [x0, x1, x1, x0,  x0, x1, x1, x0]
        vy = [y0, y0, y1, y1,  y0, y0, y1, y1]
        vz = [z0, z0, z0, z0,  z1, z1, z1, z1]
        fi = [0, 0, 4, 4, 0, 0, 2, 2, 0, 0, 1, 1]
        fj = [1, 2, 5, 6, 1, 5, 3, 7, 3, 7, 2, 6]
        fk = [2, 3, 6, 7, 5, 4, 7, 6, 7, 4, 6, 5]
        return go.Mesh3d(
            x=vx, y=vy, z=vz, i=fi, j=fj, k=fk,
            color=color, opacity=0.9, name=name,
            showlegend=show_legend, flatshading=True,
        )

    @staticmethod
    def _hip_roof(x0, y0, x1, y1, base_z, apex_z, color, name='Roof') -> go.Mesh3d:
        """Hip-style roof."""
        cx, cy = (x0+x1)/2, (y0+y1)/2
        vx = [x0, x1, x1, x0, cx]
        vy = [y0, y0, y1, y1, cy]
        vz = [base_z]*4 + [apex_z]
        fi, fj, fk = [0, 1, 2, 3], [1, 2, 3, 0], [4, 4, 4, 4]
        return go.Mesh3d(
            x=vx, y=vy, z=vz, i=fi, j=fj, k=fk,
            color=color, opacity=0.97, name=name,
            showlegend=False, flatshading=True,
            lighting=dict(ambient=0.6, diffuse=0.95, specular=0.3),
        )

    @staticmethod
    def _hemisphere(cx, cy, base_z, r, color, show_legend=False) -> go.Mesh3d:
        """Hemisphere for plants/bushes."""
        n = 10
        theta = np.linspace(0, np.pi/2, n)
        phi = np.linspace(0, 2*np.pi, n)
        T, P = np.meshgrid(theta, phi)
        x_ = cx + r * np.sin(T) * np.cos(P)
        y_ = cy + r * np.sin(T) * np.sin(P)
        z_ = base_z + r * np.cos(T)
        return go.Surface(
            x=x_, y=y_, z=z_,
            colorscale=[[0, color], [1, '#A5D6A7']],
            showscale=False,
            opacity=0.88,
            showlegend=show_legend,
            name='Plant',
        )

    @staticmethod
    def _cone_tree(tx, ty,
                   trunk_bot_z=1.5, trunk_top_z=7.0,
                   canopy_bot_z=7.0, canopy_top_z=18.0,
                   canopy_r=7.5, trunk_r=1.2,
                   color_canopy='#2E7D32',
                   label='', show_legend=False) -> List:
        """Realistic cone tree with trunk and canopy."""
        traces = []
        n = 20

        # Trunk cylinder
        theta_t = np.linspace(0, 2*np.pi, n)
        z_t = np.array([trunk_bot_z, trunk_top_z])
        Tg, Zg = np.meshgrid(theta_t, z_t)
        traces.append(go.Surface(
            x=tx + trunk_r * np.cos(Tg),
            y=ty + trunk_r * np.sin(Tg),
            z=Zg,
            colorscale=[[0, '#5D4037'], [1, '#795548']],
            showscale=False, showlegend=False, opacity=0.97,
        ))

        # Canopy cone
        theta_c = np.linspace(0, 2*np.pi, n, endpoint=False)
        vx = list(tx + canopy_r * np.cos(theta_c)) + [tx]
        vy = list(ty + canopy_r * np.sin(theta_c)) + [ty]
        vz = [canopy_bot_z] * n + [canopy_top_z]
        traces.append(go.Mesh3d(
            x=vx, y=vy, z=vz,
            i=list(range(n)),
            j=[(k+1) % n for k in range(n)],
            k=[n] * n,
            color=color_canopy, opacity=0.90,
            name=label if label else 'Tree',
            showlegend=show_legend, flatshading=True,
            lighting=dict(ambient=0.6, diffuse=0.9, specular=0.1),
        ))

        # Canopy base disk
        rg = np.linspace(0, canopy_r, 6)
        tg = np.linspace(0, 2*np.pi, n)
        R2, T2 = np.meshgrid(rg, tg)
        traces.append(go.Surface(
            x=tx + R2*np.cos(T2), y=ty + R2*np.sin(T2),
            z=np.full_like(R2, canopy_bot_z),
            colorscale=[[0, color_canopy], [1, color_canopy]],
            showscale=False, showlegend=False, opacity=0.75,
        ))

        return traces
