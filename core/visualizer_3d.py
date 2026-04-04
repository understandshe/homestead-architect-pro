"""
Homestead Architect Pro 2026 — ULTRA PREMIUM EDITION
Features: Large 3D Labels, Dynamic Camera Logic, Toggle HUD, and Full Data Sync.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import json
from typing import Dict, Any, List

class Visualizer3D:
    """Creates high-end interactive 3D homestead models using Plotly."""

    ZONE_COLORS = {
        'z0': '#F5F5DC', 'z1': '#90EE90', 'z2': '#228B22', 'z3': '#F0E68C', 'z4': '#DDA0DD',
    }
    ZONE_NAMES = {
        'z0': 'Zone 0 – Residential', 'z1': 'Zone 1 – Kitchen Garden',
        'z2': 'Zone 2 – Food Forest', 'z3': 'Zone 3 – Pasture', 'z4': 'Zone 4 – Buffer',
    }

    def create(self, layout: Dict[str, Any]):
        if not layout or 'dimensions' not in layout:
            st.info("👈 पहले 'Design' टैब में अपना नक्शा जनरेट करें।")
            return

        fig = go.Figure()

        # --- Scene Layers (वही पुराना सॉलिड लॉजिक) ---
        self._add_terrain(fig, layout)
        self._add_zones_3d(fig, layout)
        self._add_house_3d(fig, layout)
        self._add_features_3d(fig, layout)
        self._add_all_livestock_3d(fig, layout)
        self._add_trees_3d(fig, layout)

        # --- नया फीचर: बड़े अक्षरों में नाम (Large 3D Labels) ---
        self._add_large_labels(fig, layout)

        L = layout['dimensions']['L']
        W = layout['dimensions']['W']
        acres = layout.get('acres', round(L * W / 43560, 2))

        # --- कैमरा लॉजिक और UI बटन (Smooth कैमरा और डिब्बा छुपाने का ऑप्शन) ---
        fig.update_layout(
            title=dict(
                text=f"🏡 {layout.get('location', 'Premium Plot')} — {acres:.2f} acres",
                font=dict(size=18, color='#166534', family='Arial Black'),
                x=0.5,
            ),
            scene=dict(
                xaxis_title='Length (ft)', yaxis_title='Width (ft)', zaxis_title='Height (ft)',
                aspectmode='data', bgcolor='#D0E8F5',
                # कैमरा एंगल्स जो 'camera_logic.js' की तरह काम करेंगे
                camera=dict(eye=dict(x=1.4, y=-1.4, z=1.0)), 
                xaxis=dict(showgrid=True, gridcolor='#BBBBBB'),
                yaxis=dict(showgrid=True, gridcolor='#BBBBBB'),
                zaxis=dict(showgrid=True, gridcolor='#BBBBBB', range=[-5, 50]),
            ),
            # नया UI पैनल: डिब्बा छुपाना और कैमरा बदलना
            updatemenus=[
                # 1. 'Legend/सफ़ेद डिब्बा' छुपाने का बटन
                dict(
                    type="buttons", direction="right", x=0.01, y=1.05,
                    buttons=[
                        dict(label="👁️ Show Legend", method="relayout", args=[{"showlegend": True}]),
                        dict(label="🚫 Hide Legend", method="relayout", args=[{"showlegend": False}])
                    ]
                ),
                # 2. कैमरा एंगल्स (Smooth Camera Angles)
                dict(
                    type="dropdown", direction="down", x=0.99, y=1.05,
                    buttons=[
                        dict(label="🎥 Cinematic View", method="relayout", args=[{"scene.camera.eye": {"x": 1.4, "y": -1.4, "z": 1.0}}]),
                        dict(label="🗺️ Top View", method="relayout", args=[{"scene.camera.eye": {"x": 0, "y": 0, "z": 2.5}}]),
                        dict(label="🏚️ Side View", method="relayout", args=[{"scene.camera.eye": {"x": 2.2, "y": 0, "z": 0.5}}])
                    ]
                )
            ],
            legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.85)', borderwidth=1),
            paper_bgcolor='#EAF4FB', margin=dict(l=0, r=0, t=60, b=0), height=750,
        )

        # 1. 3D मैप डिस्प्ले
        st.plotly_chart(fig, use_container_width=True)

        # 2. HTML डाउनलोड बटन (ताकि यूजर अपने पास रख सके)
        html_bytes = fig.to_html(include_plotlyjs='cdn', full_html=True)
        st.download_button(
            label="📥 Download 3D Architectural Map (HTML)",
            data=html_bytes, file_name="homestead_3d_pro.html", mime="text/html", use_container_width=True
        )

    def _add_large_labels(self, fig, layout):
        """सभी मॉडल्स के ऊपर बड़े अक्षरों में नाम लिखना (Large Text Scatter)"""
        labels = []
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        
        # घर का लेबल (House Location के हिसाब से)
        h_pos = layout.get('house_position', 'Center')
        hx, hy = L*0.5, W*0.5
        if h_pos == 'North': hy = W*0.85
        elif h_pos == 'South': hy = W*0.1
        labels.append({'x': hx, 'y': hy, 'z': 22, 'txt': '🏠 MAIN HOUSE'})

        # फीचर्स के नाम (Pond, Well, Solar)
        feats = layout.get('features', {})
        if 'pond' in feats: labels.append({'x': feats['pond']['x'], 'y': feats['pond']['y'], 'z': 5, 'txt': '💧 POND'})
        if 'well' in feats: labels.append({'x': feats['well']['x'], 'y': feats['well']['y'], 'z': 10, 'txt': '🚰 WELL'})
        if 'solar' in feats: labels.append({'x': feats['solar']['x'], 'y': feats['solar']['y'], 'z': 8, 'txt': '☀️ SOLAR ARRAY'})

        # जानवरों के शेड के नाम
        for k, label in {'goat_shed': '🐐 GOATS', 'chicken_coop': '🐔 POULTRY', 'cow_shed': '🐄 COWS'}.items():
            if k in feats:
                labels.append({'x': feats[k]['x']+5, 'y': feats[k]['y']+5, 'z': 12, 'txt': label})

        fig.add_trace(go.Scatter3d(
            x=[l['x'] for l in labels], y=[l['y'] for l in labels], z=[l['z'] for l in labels],
            mode='text', text=[l['txt'] for l in labels],
            textfont=dict(size=14, color="black", family="Arial Black"), 
            name="Object Names", showlegend=False
        ))

    # --- Geometry Primitives (सारे पुराने कोड को वैसे ही रखा है) ---
    @staticmethod
    def _box_mesh(x0, y0, z0, x1, y1, z1, color, name, opacity=0.85, show_legend=True) -> go.Mesh3d:
        vx, vy, vz = [x0, x1, x1, x0, x0, x1, x1, x0], [y0, y0, y1, y1, y0, y0, y1, y1], [z0, z0, z0, z0, z1, z1, z1, z1]
        return go.Mesh3d(x=vx, y=vy, z=vz, i=[0,0,4,4,0,0,2,2,0,0,1,1], j=[1,2,5,6,1,5,3,7,3,7,2,6], k=[2,3,6,7,5,4,7,6,7,4,6,5],
                         color=color, opacity=opacity, name=name, showlegend=show_legend, flatshading=True)

    @staticmethod
    def _hip_roof(x0, y0, x1, y1, base_z, apex_z, color, name='Roof') -> go.Mesh3d:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        vx, vy, vz = [x0, x1, x1, x0, cx], [y0, y0, y1, y1, cy], [base_z]*4 + [apex_z]
        return go.Mesh3d(x=vx, y=vy, z=vz, i=[0,1,2,3], j=[1,2,3,0], k=[4,4,4,4], color=color, opacity=0.97, name=name, showlegend=False)

    @staticmethod
    def _cone_tree(tx, ty, trunk_bot_z=1.5, trunk_top_z=7.0, canopy_bot_z=7.0, canopy_top_z=18.0, canopy_r=7.5, trunk_r=1.2, color_canopy='#2E7D32', label='', show_legend=False) -> List:
        traces = []
        n = 18; theta_t = np.linspace(0, 2*np.pi, n); z_t = np.array([trunk_bot_z, trunk_top_z])
        T_grid, Z_grid = np.meshgrid(theta_t, z_t)
        traces.append(go.Surface(x=tx + trunk_r * np.cos(T_grid), y=ty + trunk_r * np.sin(T_grid), z=Z_grid, colorscale=[[0, '#6D4C41'], [1, '#8D6E63']], showscale=False, showlegend=False, opacity=0.95))
        theta_c = np.linspace(0, 2*np.pi, n, endpoint=False); vx = list(tx + canopy_r * np.cos(theta_c)) + [tx]; vy = list(ty + canopy_r * np.sin(theta_c)) + [ty]; vz = [canopy_bot_z] * n + [canopy_top_z]
        traces.append(go.Mesh3d(x=vx, y=vy, z=vz, i=list(range(n)), j=[(k+1)%n for k in range(n)], k=[n]*n, color=color_canopy, opacity=0.88, name=label if label else 'Tree', showlegend=show_legend, flatshading=True))
        return traces

    # --- Scene Layers (Data-Driven) ---
    def _add_terrain(self, fig, layout):
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        x, y = np.linspace(0, L, 30), np.linspace(0, W, 30); X, Y = np.meshgrid(x, y); slope = layout.get('slope', 'Flat'); Z = np.zeros_like(X)
        if slope == 'South': Z = Y * 0.03
        elif slope == 'North': Z = (W - Y) * 0.03
        fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale=[[0, '#81C784'], [1, '#2E7D32']], showscale=False, opacity=0.82, name='Terrain', showlegend=True))

    def _add_zones_3d(self, fig, layout):
        for zone_id, pos in layout.get('zone_positions', {}).items():
            fig.add_trace(self._box_mesh(pos['x'], pos['y'], 0, pos['x']+pos['width'], pos['y']+pos['height'], 1.5, color=self.ZONE_COLORS.get(zone_id, '#CCCCCC'), name=self.ZONE_NAMES.get(zone_id, zone_id), opacity=0.40))

    def _add_house_3d(self, fig, layout):
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        pos = layout.get('house_position', 'Center'); positions = {'North': (L*0.30, W*0.82, L*0.40, W*0.12), 'South': (L*0.30, W*0.06, L*0.40, W*0.12), 'Center': (L*0.35, W*0.40, L*0.30, W*0.20)}
        hx, hy, hw, hd = positions.get(pos, positions['Center'])
        fig.add_trace(self._box_mesh(hx, hy, 1.5, hx+hw, hy+hd, 11.5, color='#8D6E63', name='House', opacity=0.96))
        fig.add_trace(self._hip_roof(hx, hy, hx+hw, hy+hd, 11.5, 17.5, color='#4E342E'))

    def _add_features_3d(self, fig, layout):
        features = layout.get('features', {})
        if 'pond' in features:
            f = features['pond']; r = f['radius']; rg = np.linspace(0, r, 10); tg = np.linspace(0, 2*np.pi, 36); R, T = np.meshgrid(rg, tg)
            fig.add_trace(go.Surface(x=f['x'] + R*np.cos(T), y=f['y'] + R*np.sin(T), z=np.full_like(R, -0.8), colorscale=[[0, '#4FC3F7'], [1, '#0288D1']], showscale=False, name='Pond', showlegend=True))
        if 'well' in features:
            f = features['well']; theta_w = np.linspace(0, 2*np.pi, 24); z_w = np.array([1.5, 6.0]); Tw, Zw = np.meshgrid(theta_w, z_w)
            fig.add_trace(go.Surface(x=f['x']+4*np.cos(Tw), y=f['y']+4*np.sin(Tw), z=Zw, colorscale='Greys', showscale=False, name='Well', showlegend=True))

    def _add_all_livestock_3d(self, fig, layout):
        features = layout.get('features', {})
        configs = {'goat_shed': ('#FFCCBC', '#4E342E', 'Goat Shed', 7), 'chicken_coop': ('#FFF9C4', '#F57F17', 'Chicken Coop', 5), 'cow_shed': ('#D7CCC8', '#5D4037', 'Cow Shed', 9)}
        for k, (wc, rc, label, sh) in configs.items():
            if k in features:
                f = features[k]; fig.add_trace(self._box_mesh(f['x'], f['y'], 1.5, f['x']+f['width'], f['y']+f['height'], 1.5+sh, wc, label))
                fig.add_trace(self._hip_roof(f['x'], f['y'], f['x']+f['width'], f['y']+f['height'], 1.5+sh, 1.5+sh+f['width']*0.3, rc))

    def _add_trees_3d(self, fig, layout):
        z_pos = layout.get('zone_positions', {}); z2 = z_pos.get('z2')
        if not z2: return
        rel_pos = [(0.2, 0.3), (0.5, 0.6), (0.8, 0.4)]; tree_labels = ['Mango', 'Jackfruit', 'Coconut']
        for i, (rx, ry) in enumerate(rel_pos):
            for trace in self._cone_tree(z2['x']+rx*z2['width'], z2['y']+ry*z2['height'], label=tree_labels[i], show_legend=(i==0)):
                fig.add_trace(trace)
