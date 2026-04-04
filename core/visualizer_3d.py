"""
Homestead Architect Pro 2026 — ULTRA CINEMATIC EDITION
Features: 3D Labels (Large Text), camera_logic Integration, Toggle HUD/Legend.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import json
from typing import Dict, Any, List

class Visualizer3D:
    """Creates interactive 3D homestead models with cinematic controls."""

    ZONE_COLORS = {
        'z0': '#F5F5DC', 'z1': '#90EE90', 'z2': '#228B22',
        'z3': '#F0E68C', 'z4': '#DDA0DD',
    }
    ZONE_NAMES = {
        'z0': 'Zone 0 – Residential', 'z1': 'Zone 1 – Kitchen Garden',
        'z2': 'Zone 2 – Food Forest', 'z3': 'Zone 3 – Pasture / Crops',
        'z4': 'Zone 4 – Buffer Zone',
    }

    def create(self, layout: Dict[str, Any]):
        """Main entry point for Streamlit to render the 3D map."""
        if not layout or 'dimensions' not in layout:
            st.info("👈 पहले 'Design' टैब में अपना नक्शा जनरेट करें।")
            return

        fig = go.Figure()

        # --- परतों को जोड़ना (No deletions, as requested) ---
        self._add_terrain(fig, layout)
        self._add_zones_3d(fig, layout)
        self._add_house_3d(fig, layout)
        self._add_features_3d(fig, layout)
        self._add_all_livestock_3d(fig, layout)
        self._add_trees_3d(fig, layout)
        
        # --- नया फीचर: बड़े अक्षरों में नाम (Large 3D Labels) ---
        self._add_3d_labels_large(fig, layout)

        L = layout['dimensions']['L']
        W = layout['dimensions']['W']
        acres = layout.get('acres', round(L * W / 43560, 2))

        # --- camera_logic.js वाले मक्खन जैसे एंगल्स ---
        camera_logic = {
            'default': dict(eye=dict(x=1.4, y=-1.4, z=0.9)),
            'top': dict(eye=dict(x=0, y=0, z=2.5)),
            'cinematic': dict(eye=dict(x=2.0, y=2.0, z=1.2)),
            'front': dict(eye=dict(x=0, y=-2.0, z=0.5))
        }

        fig.update_layout(
            title=dict(
                text=f"🏡 3D Homestead — {acres:.2f} acres ({int(L)} × {int(W)} ft)",
                font=dict(size=17, color='#2E7D32', family='Arial'),
                x=0.5,
            ),
            scene=dict(
                xaxis_title='Length (ft)', yaxis_title='Width (ft)', zaxis_title='Height (ft)',
                aspectmode='data', bgcolor='#D0E8F5',
                camera=camera_logic['default'], # camera_logic apply किया
                xaxis=dict(showgrid=True, gridcolor='#BBBBBB'),
                yaxis=dict(showgrid=True, gridcolor='#BBBBBB'),
                zaxis=dict(showgrid=True, gridcolor='#BBBBBB'),
            ),
            # 'Show/Hide' और 'Camera' कंट्रोल्स
            updatemenus=[
                # बटन 1: सफ़ेद डिब्बा (Legend) और डेटा छुपाने के लिए
                dict(
                    type="buttons", direction="down", x=0.01, y=0.8,
                    buttons=[
                        dict(label="👁️ Show All", method="relayout", args=[{"showlegend": True, "title.text": f"🏡 {acres:.2f} Acres"}]),
                        dict(label="🚫 Hide Box/Data", method="relayout", args=[{"showlegend": False, "title.text": ""}])
                    ]
                ),
                # बटन 2: camera_logic.js वाले मक्खन एंगल्स
                dict(
                    type="buttons", direction="left", x=0.5, y=-0.1, xanchor="center",
                    buttons=[
                        dict(label="🎯 Default", method="relayout", args=[{"scene.camera": camera_logic['default']}]),
                        dict(label="☁️ Top View", method="relayout", args=[{"scene.camera": camera_logic['top']}]),
                        dict(label="🎬 Cinematic", method="relayout", args=[{"scene.camera": camera_logic['cinematic']}]),
                    ]
                )
            ],
            legend=dict(
                x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.85)',
                bordercolor='#AAAAAA', borderwidth=1, font=dict(size=11),
            ),
            paper_bgcolor='#EAF4FB', margin=dict(l=0, r=0, t=55, b=0), height=750,
        )
        
        # Streamlit में डिस्प्ले और HTML डाउनलोड बटन
        st.plotly_chart(fig, use_container_width=True)
        
        html_bytes = fig.to_html(include_plotlyjs='cdn', full_html=True)
        st.download_button(label="⬇️ Download 3D Map (HTML)", data=html_bytes, 
                           file_name="homestead_3d.html", mime="text/html")

    def _add_3d_labels_large(self, fig, layout):
        """बड़े अक्षरों में नाम जोड़ने वाला फंक्शन।"""
        labels = []
        features = layout.get('features', {})
        L, W = layout['dimensions']['L'], layout['dimensions']['W']

        # घर का लेबल
        labels.append({'x': L*0.5, 'y': W*0.5, 'z': 25, 'txt': '🏠 MAIN HOUSE'})

        # जानवरों के शेड के नाम
        livestock_labels = {
            'goat_shed': '🐐 GOATS', 'chicken_coop': '🐔 CHICKENS', 
            'cow_shed': '🐄 COWS', 'pond': '🐟 FISH POND'
        }
        for key, txt in livestock_labels.items():
            if key in features:
                f = features[key]
                labels.append({'x': f.get('x', 0), 'y': f.get('y', 0), 'z': 15, 'txt': txt})

        fig.add_trace(go.Scatter3d(
            x=[l['x'] for l in labels], y=[l['y'] for l in labels], z=[l['z'] for l in labels],
            mode='text', text=[l['txt'] for l in labels],
            textfont=dict(size=14, color="black", family="Arial Black"), # अक्षर बड़े और बोल्ड किए
            showlegend=False, name="Labels"
        ))

    # --- पुराने प्रिमिटिव्स (No Changes) ---
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
        traces.append(go.Surface(x=tx + trunk_r * np.cos(T_grid), y=ty + trunk_r * np.sin(T_grid), z=Z_grid, colorscale=[[0, '#6D4C41'], [1, '#8D6E63']], showscale=False, showlegend=False))
        theta_c = np.linspace(0, 2*np.pi, n, endpoint=False); vx = list(tx + canopy_r * np.cos(theta_c)) + [tx]; vy = list(ty + canopy_r * np.sin(theta_c)) + [ty]; vz = [canopy_bot_z] * n + [canopy_top_z]
        traces.append(go.Mesh3d(x=vx, y=vy, z=vz, i=list(range(n)), j=[(k+1)%n for k in range(n)], k=[n]*n, color=color_canopy, opacity=0.88, name=label, showlegend=show_legend))
        return traces

    # --- लेयर्स (No Changes) ---
    def _add_terrain(self, fig, layout):
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        x, y = np.linspace(0, L, 30), np.linspace(0, W, 30); X, Y = np.meshgrid(x, y); slope = layout.get('slope', 'Flat'); Z = np.zeros_like(X)
        if slope == 'South': Z = Y * 0.03
        fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale='Greens', showscale=False, opacity=0.82, name='Terrain'))

    def _add_zones_3d(self, fig, layout):
        for zid, pos in layout.get('zone_positions', {}).items():
            fig.add_trace(self._box_mesh(pos['x'], pos['y'], 0, pos['x']+pos['width'], pos['y']+pos['height'], 1.5, color=self.ZONE_COLORS.get(zid, '#CCC'), name=zid, opacity=0.4))

    def _add_house_3d(self, fig, layout):
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        hx, hy, hw, hd = L*0.35, W*0.4, L*0.3, W*0.2
        fig.add_trace(self._box_mesh(hx, hy, 1.5, hx+hw, hy+hd, 11.5, '#8D6E63', 'House'))
        fig.add_trace(self._hip_roof(hx, hy, hx+hw, hy+hd, 11.5, 16.5, '#4E342E'))

    def _add_features_3d(self, fig, layout):
        f = layout.get('features', {})
        if 'well' in f:
            fig.add_trace(go.Scatter3d(x=[f['well']['x']], y=[f['well']['y']], z=[5], mode='markers', marker=dict(size=10, color='grey'), name='Well'))

    def _add_all_livestock_3d(self, fig, layout):
        f = layout.get('features', {})
        if 'goat_shed' in f:
            sh = f['goat_shed']
            fig.add_trace(self._box_mesh(sh['x'], sh['y'], 1.5, sh['x']+sh['width'], sh['y']+sh['height'], 8.5, '#FFCCBC', 'Livestock'))

    def _add_trees_3d(self, fig, layout):
        z2 = layout.get('zone_positions', {}).get('z2')
        if z2:
            tx, ty = z2['x']+z2['width']*0.5, z2['y']+z2['height']*0.5
            for tr in self._cone_tree(tx, ty, label='Trees', show_legend=True): fig.add_trace(tr)
