"""
3D Visualization Engine — FIXED
Homestead Architect Pro 2026

Fixes:
  - All livestock types drawn individually (goat, chicken, pig, cow, fish, bees)
  - Features positioned correctly matching layout_engine output
  - Proper 3D solids for every feature
"""

import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
from typing import Dict, Any, List


class Visualizer3D:
    """Creates interactive 3D homestead models using Plotly."""

    ZONE_COLORS = {
        'z0': '#F5F5DC',
        'z1': '#90EE90',
        'z2': '#228B22',
        'z3': '#F0E68C',
        'z4': '#DDA0DD',
    }
    ZONE_NAMES = {
        'z0': 'Zone 0 – Residential',
        'z1': 'Zone 1 – Kitchen Garden',
        'z2': 'Zone 2 – Food Forest',
        'z3': 'Zone 3 – Pasture / Crops',
        'z4': 'Zone 4 – Buffer Zone',
    }

    def create(self, layout: Dict[str, Any]) -> go.Figure:
        fig = go.Figure()

        self._add_terrain(fig, layout)
        self._add_zones_3d(fig, layout)
        self._add_house_3d(fig, layout)
        self._add_features_3d(fig, layout)
        self._add_all_livestock_3d(fig, layout)
        self._add_trees_3d(fig, layout)

        L = layout['dimensions']['L']
        W = layout['dimensions']['W']
        acres = layout.get('acres', round(L * W / 43560, 2))

        fig.update_layout(
            title=dict(
                text=f"🏠 3D Homestead — {acres:.2f} acres ({int(L)} × {int(W)} ft)",
                font=dict(size=17, color='#2E7D32', family='Arial'),
                x=0.5,
            ),
            scene=dict(
                xaxis_title='Length (ft)',
                yaxis_title='Width (ft)',
                zaxis_title='Height (ft)',
                aspectmode='data',
                bgcolor='#D0E8F5',
                camera=dict(
                    eye=dict(x=1.4, y=-1.4, z=0.9),
                    up=dict(x=0, y=0, z=1),
                ),
                xaxis=dict(showgrid=True, gridcolor='#BBBBBB'),
                yaxis=dict(showgrid=True, gridcolor='#BBBBBB'),
                zaxis=dict(showgrid=True, gridcolor='#BBBBBB'),
            ),
            legend=dict(
                x=0.01, y=0.99,
                bgcolor='rgba(255,255,255,0.85)',
                bordercolor='#AAAAAA', borderwidth=1,
                font=dict(size=11),
            ),
            paper_bgcolor='#EAF4FB',
            margin=dict(l=0, r=0, t=55, b=0),
            width=950, height=670,
        )
        return fig

    # ── Geometry primitives ──────────────────────────────────────────────────────

    @staticmethod
    def _box_mesh(x0, y0, z0, x1, y1, z1, color, name,
                  opacity=0.85, show_legend=True) -> go.Mesh3d:
        vx = [x0, x1, x1, x0,  x0, x1, x1, x0]
        vy = [y0, y0, y1, y1,  y0, y0, y1, y1]
        vz = [z0, z0, z0, z0,  z1, z1, z1, z1]
        fi = [0, 0,  4, 4,  0, 0,  2, 2,  0, 0,  1, 1]
        fj = [1, 2,  5, 6,  1, 5,  3, 7,  3, 7,  2, 6]
        fk = [2, 3,  6, 7,  5, 4,  7, 6,  7, 4,  6, 5]
        return go.Mesh3d(
            x=vx, y=vy, z=vz, i=fi, j=fj, k=fk,
            color=color, opacity=opacity, name=name,
            showlegend=show_legend, flatshading=True,
            lighting=dict(ambient=0.65, diffuse=0.9, specular=0.2,
                          roughness=0.6, fresnel=0.1),
        )

    @staticmethod
    def _hip_roof(x0, y0, x1, y1, base_z, apex_z, color,
                  name='Roof') -> go.Mesh3d:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        vx = [x0, x1, x1, x0, cx]
        vy = [y0, y0, y1, y1, cy]
        vz = [base_z] * 4 + [apex_z]
        fi = [0, 1, 2, 3]
        fj = [1, 2, 3, 0]
        fk = [4, 4, 4, 4]
        return go.Mesh3d(
            x=vx, y=vy, z=vz, i=fi, j=fj, k=fk,
            color=color, opacity=0.97, name=name,
            showlegend=False, flatshading=True,
        )

    @staticmethod
    def _cone_tree(tx, ty, trunk_bot_z=1.5, trunk_top_z=7.0,
                   canopy_bot_z=7.0, canopy_top_z=18.0,
                   canopy_r=7.5, trunk_r=1.2,
                   color_canopy='#2E7D32', label='',
                   show_legend=False) -> List:
        traces = []
        n = 18
        theta_t = np.linspace(0, 2*np.pi, n)
        z_t = np.array([trunk_bot_z, trunk_top_z])
        T_grid, Z_grid = np.meshgrid(theta_t, z_t)
        traces.append(go.Surface(
            x=tx + trunk_r * np.cos(T_grid),
            y=ty + trunk_r * np.sin(T_grid),
            z=Z_grid,
            colorscale=[[0, '#6D4C41'], [1, '#8D6E63']],
            showscale=False, showlegend=False, opacity=0.95, name='Trunk',
        ))
        theta_c = np.linspace(0, 2*np.pi, n, endpoint=False)
        vx = list(tx + canopy_r * np.cos(theta_c)) + [tx]
        vy = list(ty + canopy_r * np.sin(theta_c)) + [ty]
        vz = [canopy_bot_z] * n + [canopy_top_z]
        apex = n
        traces.append(go.Mesh3d(
            x=vx, y=vy, z=vz,
            i=list(range(n)),
            j=[(k+1) % n for k in range(n)],
            k=[apex] * n,
            color=color_canopy, opacity=0.88,
            name=label if label else 'Tree',
            showlegend=show_legend, flatshading=True,
        ))
        return traces

    # ── Scene layers ─────────────────────────────────────────────────────────────

    def _add_terrain(self, fig, layout):
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        x = np.linspace(0, L, 30)
        y = np.linspace(0, W, 30)
        X, Y = np.meshgrid(x, y)
        slope = layout.get('slope', 'Flat')
        Z = np.zeros_like(X)
        if slope == 'South':   Z = Y * 0.03
        elif slope == 'North': Z = (W - Y) * 0.03
        elif slope == 'East':  Z = X * 0.03
        elif slope == 'West':  Z = (L - X) * 0.03
        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z,
            colorscale=[[0, '#81C784'], [0.5, '#4CAF50'], [1, '#2E7D32']],
            showscale=False, opacity=0.82,
            name='Terrain', showlegend=True,
            lighting=dict(ambient=0.7, diffuse=0.85),
        ))

    def _add_zones_3d(self, fig, layout):
        for zone_id, pos in layout.get('zone_positions', {}).items():
            fig.add_trace(self._box_mesh(
                pos['x'], pos['y'], 0,
                pos['x'] + pos['width'], pos['y'] + pos['height'], 1.5,
                color=self.ZONE_COLORS.get(zone_id, '#CCCCCC'),
                name=self.ZONE_NAMES.get(zone_id, zone_id),
                opacity=0.40,
            ))

    def _add_house_3d(self, fig, layout):
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        pos = layout.get('house_position', 'Center')
        positions = {
            'North':        (L*0.30, W*0.82, L*0.40, W*0.12),
            'South':        (L*0.30, W*0.06, L*0.40, W*0.12),
            'East':         (L*0.75, W*0.35, L*0.20, W*0.30),
            'West':         (L*0.05, W*0.35, L*0.20, W*0.30),
            'Center':       (L*0.35, W*0.40, L*0.30, W*0.20),
            'Not built yet':(L*0.35, W*0.40, L*0.30, W*0.20),
        }
        hx, hy, hw, hd = positions.get(pos, positions['Center'])
        wall_h = 10.0
        base_z = 1.5
        roof_bot = base_z + wall_h
        roof_top = roof_bot + min(hw, hd) * 0.42

        fig.add_trace(self._box_mesh(
            hx, hy, base_z, hx+hw, hy+hd, roof_bot,
            color='#8D6E63', name='House', opacity=0.96,
        ))
        fig.add_trace(self._hip_roof(
            hx, hy, hx+hw, hy+hd,
            base_z=roof_bot, apex_z=roof_top,
            color='#4E342E',
        ))

    def _add_features_3d(self, fig, layout):
        features = layout.get('features', {})

        # Pond
        if 'pond' in features:
            f = features['pond']
            r = f['radius']
            rg = np.linspace(0, r, 10)
            tg = np.linspace(0, 2*np.pi, 36)
            R, T = np.meshgrid(rg, tg)
            fig.add_trace(go.Surface(
                x=f['x'] + R * np.cos(T) * (1 + 0.1 * np.sin(3*T)),
                y=f['y'] + R * np.sin(T) * (1 + 0.1 * np.cos(2*T)),
                z=np.full_like(R, -0.8),
                colorscale=[[0, '#4FC3F7'], [1, '#0288D1']],
                showscale=False, opacity=0.85,
                name='Pond / Fish', showlegend=True,
            ))

        # Borewell
        if 'well' in features:
            f = features['well']
            rw = f.get('radius', 4)
            theta_w = np.linspace(0, 2*np.pi, 24)
            z_w = np.array([1.5, 5.0])
            Tw, Zw = np.meshgrid(theta_w, z_w)
            fig.add_trace(go.Surface(
                x=f['x'] + rw * np.cos(Tw),
                y=f['y'] + rw * np.sin(Tw),
                z=Zw,
                colorscale=[[0, '#546E7A'], [1, '#90A4AE']],
                showscale=False, opacity=0.95,
                name='Borewell', showlegend=True,
            ))

        # Solar panels
        if 'solar' in features:
            f = features['solar']
            pw, ph = f['width'] / 3, f['height'] / 2
            for col in range(3):
                for row in range(2):
                    px = f['x'] + col * pw + 1
                    py = f['y'] + row * ph + 1
                    fig.add_trace(self._box_mesh(
                        px, py, 4.0,
                        px + pw - 2, py + ph - 2, 4.4,
                        color='#1565C0',
                        name='Solar Panels' if (col == 0 and row == 0) else '',
                        opacity=0.95,
                        show_legend=(col == 0 and row == 0),
                    ))

        # Greenhouse
        if 'greenhouse' in features:
            f = features['greenhouse']
            gh_h = 8.0
            base_z = 1.5
            fig.add_trace(self._box_mesh(
                f['x'], f['y'], base_z,
                f['x']+f['width'], f['y']+f['height'], base_z+gh_h,
                color='#E0F2F1', name='Greenhouse', opacity=0.35,
            ))
            fig.add_trace(self._hip_roof(
                f['x'], f['y'], f['x']+f['width'], f['y']+f['height'],
                base_z=base_z+gh_h,
                apex_z=base_z+gh_h+f['width']*0.28,
                color='#80CBC4', name='GH Roof',
            ))

        # Rain tank
        if 'rain_tank' in features:
            f = features['rain_tank']
            fig.add_trace(self._box_mesh(
                f['x'], f['y'], 1.5,
                f['x']+f['width'], f['y']+f['height'], 7.0,
                color='#4FC3F7', name='Rain Tank', opacity=0.80,
            ))

    def _add_all_livestock_3d(self, fig, layout):
        """Draw each livestock type as a distinct 3D shed."""
        features = layout.get('features', {})

        livestock_config = {
            'goat_shed':   ('#FFCCBC', '#4E342E', 'Goat Shed',    7.0),
            'chicken_coop':('#FFF9C4', '#F57F17', 'Chicken Coop', 5.0),
            'piggery':     ('#F8BBD0', '#880E4F', 'Piggery',      6.0),
            'cow_shed':    ('#D7CCC8', '#5D4037', 'Cow Shed',     9.0),
            'fish_tanks':  ('#B3E5FC', '#0288D1', 'Fish Tanks',   3.0),
            'bee_hives':   ('#FFF176', '#F9A825', 'Bee Hives',    4.0),
        }

        for key, (wall_color, roof_color, label, shed_h) in livestock_config.items():
            if key not in features:
                continue
            f = features[key]
            base_z = 1.5
            roof_bot = base_z + shed_h
            roof_top = roof_bot + f['width'] * 0.25

            fig.add_trace(self._box_mesh(
                f['x'], f['y'], base_z,
                f['x']+f['width'], f['y']+f['height'], roof_bot,
                color=wall_color, name=label, opacity=0.90,
            ))
            fig.add_trace(self._hip_roof(
                f['x'], f['y'], f['x']+f['width'], f['y']+f['height'],
                base_z=roof_bot, apex_z=roof_top,
                color=roof_color, name=f'{label} Roof',
            ))

    def _add_trees_3d(self, fig, layout):
        zone_pos = layout.get('zone_positions', {})
        if 'z2' not in zone_pos:
            return
        z = zone_pos['z2']
        rel_positions = [
            (0.18, 0.30), (0.48, 0.58), (0.78, 0.38),
            (0.28, 0.72), (0.68, 0.20), (0.58, 0.82),
        ]
        canopy_colors = ['#2E7D32', '#388E3C', '#1B5E20',
                         '#43A047', '#66BB6A', '#33691E']
        tree_labels = ['Mango', 'Coconut', 'Jackfruit',
                       'Banana', 'Guava', 'Papaya']

        for idx, (rx, ry) in enumerate(rel_positions):
            tx = z['x'] + rx * z['width']
            ty = z['y'] + ry * z['height']
            for trace in self._cone_tree(
                tx, ty,
                color_canopy=canopy_colors[idx % len(canopy_colors)],
                label=tree_labels[idx % len(tree_labels)],
                show_legend=(idx == 0),
            ):
                fig.add_trace(trace)

    # ── HTML Export Function ────────────────────────────────────────────────────
    
    def export_as_html(self, fig: go.Figure, filename: str = "homestead_3d.html"):
        """Exports the 3D model into a standalone, rotatable HTML file."""
        pio.write_html(fig, file=filename, auto_open=False, include_plotlyjs='cdn')
        print(f"Interactive 3D model saved to: {filename}")
