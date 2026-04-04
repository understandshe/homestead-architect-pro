"""
Homestead Architect Pro 2026 — ULTIMATE 3D ENGINE
Features: 
- 3D Text Labels on Models
- HUD Data Toggle (Show/Hide Info)
- One-Click HTML Download
- High-Performance Plotly Backend
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from typing import Dict, Any, List
import json

class Visualizer3D:
    ZONE_COLORS = {'z0': '#F5F5DC', 'z1': '#90EE90', 'z2': '#228B22', 'z3': '#F0E68C', 'z4': '#DDA0DD'}
    ZONE_NAMES = {'z0': 'Residential', 'z1': 'Kitchen Garden', 'z2': 'Food Forest', 'z3': 'Pasture', 'z4': 'Buffer'}

    def create(self, layout: Dict[str, Any]):
        if not layout or 'dimensions' not in layout:
            st.info("👈 पहले 'Design' टैब में अपना नक्शा जनरेट करें।")
            return

        fig = go.Figure()

        # 1. ADD CORE LAYERS
        self._add_terrain(fig, layout)
        self._add_zones_3d(fig, layout)
        self._add_house_3d(fig, layout)
        self._add_features_3d(fig, layout)
        self._add_all_livestock_3d(fig, layout)
        self._add_trees_3d(fig, layout)

        # 2. DIMENSIONS & TEXT
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        acres = layout.get('acres', round(L * W / 43560, 2))
        loc = layout.get('location', 'My Homestead')

        # 3. LAYOUT & HUD CONFIG
        fig.update_layout(
            title=dict(
                text=f"🌿 {loc} | {acres:.2f} Acres",
                font=dict(size=16, color='#2E7D32'), x=0.5
            ),
            scene=dict(
                xaxis_title='Length (ft)', yaxis_title='Width (ft)', zaxis_title='Height (ft)',
                aspectmode='data', bgcolor='#D0E8F5',
                camera=dict(eye=dict(x=1.5, y=-1.5, z=1.2))
            ),
            # UPGRADED LEGEND FOR BETTER NAVIGATION
            legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)', borderwidth=1),
            margin=dict(l=0, r=0, t=60, b=0), height=700,
            
            # HUD TOGGLE OPTION (To hide/show data)
            updatemenus=[dict(
                type="buttons", direction="right", x=0.1, y=1.1,
                buttons=[
                    dict(label="👁️ Show HUD", method="relayout", args=[{"title.text": f"🌿 {loc} | {acres:.2f} Acres"}]),
                    dict(label="🚫 Hide HUD", method="relayout", args=[{"title.text": ""}])
                ]
            )]
        )

        # 4. DOWNLOAD BUTTON (STREAMLIT NATIVE)
        st.plotly_chart(fig, use_container_width=True)
        
        # HTML DOWNLOAD LOGIC
        html_buffer = io.StringIO()
        fig.write_html(html_buffer, full_html=True)
        st.download_button(
            label="⬇️ Download 3D Map (Interactive HTML)",
            data=html_buffer.getvalue(),
            file_name=f"homestead_3d_{loc.lower()}.html",
            mime="text/html",
            use_container_width=True
        )

    # --- GEOMETRY PRIMITIVES WITH LABELS ---

    def _add_label(self, fig, x, y, z, text):
        """Adds a 3D text label above a model"""
        fig.add_trace(go.Scatter3d(
            x=[x], y=[y], z=[z + 5], # Labels appear 5ft above
            mode='text', text=[text],
            textfont=dict(size=10, color='black'),
            showlegend=False, hoverinfo='none'
        ))

    def _box_mesh(self, x0, y0, z0, x1, y1, z1, color, name):
        return go.Mesh3d(
            x=[x0, x1, x1, x0, x0, x1, x1, x0],
            y=[y0, y0, y1, y1, y0, y0, y1, y1],
            z=[z0, z0, z0, z0, z1, z1, z1, z1],
            i=[0, 0, 4, 4, 0, 0, 2, 2, 0, 0, 1, 1],
            j=[1, 2, 5, 6, 1, 5, 3, 7, 3, 7, 2, 6],
            k=[2, 3, 6, 7, 5, 4, 7, 6, 7, 4, 6, 5],
            color=color, opacity=0.9, name=name, flatshading=True
        )

    # --- UPDATED LAYERS WITH LABELS ---

    def _add_house_3d(self, fig, layout):
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        hx, hy, hw, hd = L*0.35, W*0.4, L*0.3, W*0.2 # Default center
        fig.add_trace(self._box_mesh(hx, hy, 1.5, hx+hw, hy+hd, 11.5, '#8D6E63', 'Main House'))
        self._add_label(fig, hx + hw/2, hy + hd/2, 12, "🏡 Main House")

    def _add_all_livestock_3d(self, fig, layout):
        features = layout.get('features', {})
        configs = {
            'goat_shed': ('#FFCCBC', '🐐 Goat Shed'),
            'chicken_coop': ('#FFF9C4', '🐔 Chicken Coop'),
            'cow_shed': ('#D7CCC8', '🐄 Cow Shed'),
            'fish_tanks': ('#B3E5FC', '🐟 Fish Tanks')
        }
        for key, (color, label) in configs.items():
            if key in features:
                f = features[key]
                fig.add_trace(self._box_mesh(f['x'], f['y'], 1.5, f['x']+f['width'], f['y']+f['height'], 8.5, color, label))
                self._add_label(fig, f['x'] + f['width']/2, f['y'] + f['height']/2, 9, label)

    def _add_trees_3d(self, fig, layout):
        if 'z2' not in layout.get('zone_positions', {}): return
        z = layout['zone_positions']['z2']
        # Add a few representative trees with labels
        tree_pos = [(0.2, 0.3, "Mango"), (0.7, 0.6, "Coconut")]
        for rx, ry, name in tree_pos:
            tx, ty = z['x'] + rx * z['width'], z['y'] + ry * z['height']
            fig.add_trace(go.Mesh3d(x=[tx], y=[ty], z=[15], color='#2E7D32', name=name))
            self._add_label(fig, tx, ty, 16, f"🌳 {name}")

    # [Remaining original methods: _add_terrain, _add_zones_3d, _add_features_3d go here...]
    # (नोट: पिछले वर्किंग कोड के बाकी हिस्से जैसे _add_terrain वैसे ही रहेंगे)

import io # For HTML Download
