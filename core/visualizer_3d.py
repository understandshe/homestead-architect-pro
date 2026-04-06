"""
Homestead Architect Pro 2026 â€” ULTRA EDITION
Features: 3D Labels, HTML Download, Toggle HUD/Data.
"""

import streamlit as st
import plotly.graph_objects as go
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
        'z0': 'Zone 0 â€“ Residential',
        'z1': 'Zone 1 â€“ Kitchen Garden',
        'z2': 'Zone 2 â€“ Food Forest',
        'z3': 'Zone 3 â€“ Pasture / Crops',
        'z4': 'Zone 4 â€“ Buffer Zone',
    }

    def create(self, layout: Dict[str, Any]):
        """Main entry point for Streamlit to render the 3D map."""
        if not layout or 'dimensions' not in layout:
            st.info("ðŸ‘ˆ à¤ªà¤¹à¤²à¥‡ 'Design' à¤Ÿà¥ˆà¤¬ à¤®à¥‡à¤‚ à¤…à¤ªà¤¨à¤¾ à¤¨à¤•à¥à¤¶à¤¾ à¤œà¤¨à¤°à¥‡à¤Ÿ à¤•à¤°à¥‡à¤‚à¥¤")
            return

        fig = go.Figure()

        # à¤ªà¤°à¤¤à¥‹à¤‚ (Layers) à¤•à¥‹ à¤œà¥‹à¤¡à¤¼à¤¨à¤¾ - à¤ªà¥à¤°à¤¾à¤¨à¥‡ à¤«à¤‚à¤•à¥à¤¶à¤¨
        self._add_terrain(fig, layout)
        self._add_zones_3d(fig, layout)
        self._add_house_3d(fig, layout)
        self._add_features_3d(fig, layout)
        self._add_all_livestock_3d(fig, layout)
        self._add_trees_3d(fig, layout)
        
        # à¤¨à¤¯à¤¾ à¤«à¥€à¤šà¤°: 3D à¤²à¥‡à¤¬à¤²à¥à¤¸ (à¤®à¥‰à¤¡à¤²à¥à¤¸ à¤•à¥‡ à¤Šà¤ªà¤° à¤¨à¤¾à¤®)
        self._add_3d_labels(fig, layout)

        L = layout['dimensions']['L']
        W = layout['dimensions']['W']
        acres = layout.get('acres', round(L * W / 43560, 2))
        loc_name = layout.get('location', 'Custom Plot')

        fig.update_layout(
            title=dict(
                text=f"ðŸ¡ {loc_name} â€” {acres:.2f} acres ({int(L)} Ã— {int(W)} ft)",
                font=dict(size=17, color='#2E7D32', family='Arial'),
                x=0.5,
            ),
            # à¤¨à¤¯à¤¾ à¤«à¥€à¤šà¤°: HUD/Title à¤›à¥à¤ªà¤¾à¤¨à¥‡ à¤•à¥‡ à¤²à¤¿à¤ à¤¬à¤Ÿà¤¨
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    x=0.1,
                    y=1.12,
                    showactive=True,
                    buttons=[
                        dict(
                            label="ðŸ“Š Show Info",
                            method="relayout",
                            args=[{"title.text": f"ðŸ¡ {loc_name} â€” {acres:.2f} acres"}]
                        ),
                        dict(
                            label="ðŸš« Hide Info",
                            method="relayout",
                            args=[{"title.text": ""}]
                        )
                    ]
                )
            ],
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
            ),
            legend=dict(
                x=0.01, y=0.99,
                bgcolor='rgba(255,255,255,0.85)',
                font=dict(size=11),
            ),
            paper_bgcolor='#EAF4FB',
            margin=dict(l=0, r=0, t=65, b=0),
            height=700,
        )
        
        # 1. Plotly à¤šà¤¾à¤°à¥à¤Ÿ à¤¦à¤¿à¤–à¤¾à¤¨à¤¾
        st.plotly_chart(fig, use_container_width=True)
        
        # 2. à¤¨à¤¯à¤¾ à¤«à¥€à¤šà¤°: HTML à¤¡à¤¾à¤‰à¤¨à¤²à¥‹à¤¡ à¤¬à¤Ÿà¤¨
        try:
            html_bytes = fig.to_html(include_plotlyjs='cdn', full_html=True)
            st.download_button(
                label="ðŸ“¥ Download 3D Map (HTML)",
                data=html_bytes,
                file_name=f"homestead_3d_{loc_name.replace(' ', '_')}.html",
                mime="text/html",
                use_container_width=True
            )
        except Exception:
            pass

    def _add_3d_labels(self, fig, layout):
        """à¤®à¥‰à¤¡à¤²à¥à¤¸ à¤•à¥‡ à¤Šà¤ªà¤° à¤Ÿà¥‡à¤•à¥à¤¸à¥à¤Ÿ à¤²à¥‡à¤¬à¤²à¥à¤¸ à¤œà¥‹à¥œà¤¨à¤¾à¥¤"""
        features = layout.get('features', {})
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        label_data = []

        # à¤˜à¤° à¤•à¤¾ à¤²à¥‡à¤¬à¤²
        h_pos = layout.get('house_position', 'Center')
        hx, hy = L*0.5, W*0.5
        if h_pos == 'North': hy = W*0.85
        elif h_pos == 'South': hy = W*0.1
        label_data.append({'x': hx, 'y': hy, 'z': 22, 'text': 'ðŸ  Main House'})

        # à¤œà¤¾à¤¨à¤µà¤°à¥‹à¤‚ à¤•à¥‡ à¤¶à¥‡à¤¡
        livestock_map = {
            'goat_shed': 'ðŸ Goat Shed', 'chicken_coop': 'ðŸ” Chicken Coop',
            'piggery': 'ðŸ· Piggery', 'cow_shed': 'ðŸ„ Cow Shed',
            'fish_tanks': 'ðŸŸ Fish Pond', 'bee_hives': 'ðŸ Bee Hives'
        }
        for key, text in livestock_map.items():
            if key in features:
                f = features[key]
                label_data.append({'x': f['x']+f['width']/2, 'y': f['y']+f['height']/2, 'z': 15, 'text': text})

        fig.add_trace(go.Scatter3d(
            x=[d['x'] for d in label_data],
            y=[d['y'] for d in label_data],
            z=[d['z'] for d in label_data],
            mode='text',
            text=[d['text'] for d in label_data],
            textfont=dict(size=10, color="black"),
            name="Labels",
            showlegend=False
        ))

    # â”€â”€ Geometry primitives (à¤ªà¥à¤°à¤¾à¤¨à¥‡ à¤«à¤‚à¤•à¥à¤¶à¤¨ - à¤¬à¤¿à¤¨à¤¾ à¤¬à¤¦à¤²à¤¾à¤µ à¤•à¥‡) â”€â”€

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
            lighting=dict(ambient=0.65, diffuse=0.9, specular=0.2, roughness=0.6, fresnel=0.1),
        )

    @staticmethod
    def _hip_roof(x0, y0, x1, y1, base_z, apex_z, color, name='Roof') -> go.Mesh3d:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        vx = [x0, x1, x1, x0, cx]
        vy = [y0, y0, y1, y1, cy]
        vz = [base_z] * 4 + [apex_z]
        fi, fj, fk = [0, 1, 2, 3], [1, 2, 3, 0], [4, 4, 4, 4]
        return go.Mesh3d(
            x=vx, y=vy, z=vz, i=fi, j=fj, k=fk,
            color=color, opacity=0.97, name=name,
            showlegend=False, flatshading=True,
        )

    @staticmethod
    def _cone_tree(tx, ty, trunk_bot_z=1.5, trunk_top_z=7.0, canopy_bot_z=7.0, canopy_top_z=18.0,
                   canopy_r=7.5, trunk_r=1.2, color_canopy='#2E7D32', label='', show_legend=False) -> List:
        traces = []
        n = 18
        theta_t = np.linspace(0, 2*np.pi, n)
        z_t = np.array([trunk_bot_z, trunk_top_z])
        T_grid, Z_grid = np.meshgrid(theta_t, z_t)
        traces.append(go.Surface(
            x=tx + trunk_r * np.cos(T_grid), y=ty + trunk_r * np.sin(T_grid), z=Z_grid,
            colorscale=[[0, '#6D4C41'], [1, '#8D6E63']], showscale=False, showlegend=False, opacity=0.95
        ))
        theta_c = np.linspace(0, 2*np.pi, n, endpoint=False)
        vx = list(tx + canopy_r * np.cos(theta_c)) + [tx]
        vy = list(ty + canopy_r * np.sin(theta_c)) + [ty]
        vz = [canopy_bot_z] * n + [canopy_top_z]
        traces.append(go.Mesh3d(
            x=vx, y=vy, z=vz, i=list(range(n)), j=[(k+1) % n for k in range(n)], k=[n] * n,
            color=color_canopy, opacity=0.88, name=label if label else 'Tree',
            showlegend=show_legend, flatshading=True,
        ))
        return traces

    # â”€â”€ Scene layers (à¤ªà¥à¤°à¤¾à¤¨à¥‡ à¤«à¤‚à¤•à¥à¤¶à¤¨) â”€â”€

    def _add_terrain(self, fig, layout):
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        x, y = np.linspace(0, L, 30), np.linspace(0, W, 30)
        X, Y = np.meshgrid(x, y)
        slope = layout.get('slope', 'Flat')
        Z = np.zeros_like(X)
        if slope == 'South': Z = Y * 0.03
        elif slope == 'North': Z = (W - Y) * 0.03
        elif slope == 'East': Z = X * 0.03
        elif slope == 'West': Z = (L - X) * 0.03
        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z, colorscale=[[0, '#81C784'], [1, '#2E7D32']],
            showscale=False, opacity=0.82, name='Terrain', showlegend=True
        ))

    def _add_zones_3d(self, fig, layout):
        for zone_id, pos in layout.get('zone_positions', {}).items():
            fig.add_trace(self._box_mesh(
                pos['x'], pos['y'], 0, pos['x'] + pos['width'], pos['y'] + pos['height'], 1.5,
                color=self.ZONE_COLORS.get(zone_id, '#CCCCCC'),
                name=self.ZONE_NAMES.get(zone_id, zone_id), opacity=0.40
            ))

    def _add_house_3d(self, fig, layout):
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        pos = layout.get('house_position', 'Center')
        positions = {
            'North': (L*0.3, W*0.82, L*0.4, W*0.12), 'South': (L*0.3, W*0.06, L*0.4, W*0.12),
            'East': (L*0.75, W*0.35, L*0.2, W*0.3), 'West': (L*0.05, W*0.35, L*0.2, W*0.3),
            'Center': (L*0.35, W*0.4, L*0.3, W*0.2)
        }
        hx, hy, hw, hd = positions.get(pos, positions['Center'])
        fig.add_trace(self._box_mesh(hx, hy, 1.5, hx+hw, hy+hd, 11.5, color='#8D6E63', name='House'))
        fig.add_trace(self._hip_roof(hx, hy, hx+hw, hy+hd, 11.5, 16.5, color='#4E342E'))

    def _add_features_3d(self, fig, layout):
        features = layout.get('features', {})
        if 'pond' in features:
            f = features['pond']; r = f['radius']
            rg, tg = np.linspace(0, r, 10), np.linspace(0, 2*np.pi, 36)
            R, T = np.meshgrid(rg, tg)
            fig.add_trace(go.Surface(
                x=f['x'] + R * np.cos(T), y=f['y'] + R * np.sin(T), z=np.full_like(R, -0.5),
                colorscale=[[0, '#4FC3F7'], [1, '#0288D1']], showscale=False, name='Pond', showlegend=True
            ))
        if 'well' in features:
            f = features['well']; rw = f.get('radius', 4)
            t_w, z_w = np.linspace(0, 2*np.pi, 24), np.array([1.5, 6.0])
            Tw, Zw = np.meshgrid(t_w, z_w)
            fig.add_trace(go.Surface(
                x=f['x'] + rw * np.cos(Tw), y=f['y'] + rw * np.sin(Tw), z=Zw,
                colorscale=[[0, '#546E7A'], [1, '#90A4AE']], showscale=False, name='Borewell'
            ))

    def _add_all_livestock_3d(self, fig, layout):
        features = layout.get('features', {})
        livestock_config = {
            'goat_shed': ('#FFCCBC', '#4E342E', 'Goat Shed', 7.0),
            'chicken_coop': ('#FFF9C4', '#F57F17', 'Chicken Coop', 5.0),
            'piggery': ('#F8BBD0', '#880E4F', 'Piggery', 6.0),
            'cow_shed': ('#D7CCC8', '#5D4037', 'Cow Shed', 9.0),
            'fish_tanks': ('#B3E5FC', '#0288D1', 'Fish Tanks', 3.0),
            'bee_hives': ('#FFF176', '#F9A825', 'Bee Hives', 4.0),
        }
        for key, (wc, rc, lbl, sh) in livestock_config.items():
            if key not in features: continue
            f = features[key]; bz, rb = 1.5, 1.5 + sh
            rt = rb + f['width'] * 0.25
            fig.add_trace(self._box_mesh(f['x'], f['y'], bz, f['x']+f['width'], f['y']+f['height'], rb, wc, lbl))
            fig.add_trace(self._hip_roof(f['x'], f['y'], f['x']+f['width'], f['y']+f['height'], rb, rt, rc))

    def _add_trees_3d(self, fig, layout):
        zone_pos = layout.get('zone_positions', {})
        if 'z2' not in zone_pos: return
        z = zone_pos['z2']
        rel_pos = [(0.18, 0.3), (0.48, 0.58), (0.78, 0.38), (0.28, 0.72), (0.68, 0.2), (0.58, 0.82)]
        colors = ['#2E7D32', '#388E3C', '#1B5E20', '#43A047', '#66BB6A', '#33691E']
        for idx, (rx, ry) in enumerate(rel_pos):
            tx, ty = z['x'] + rx * z['width'], z['y'] + ry * z['height']
            for trace in self._cone_tree(tx, ty, color_canopy=colors[idx % 6], show_legend=(idx == 0)):
                fig.add_trace(trace)
