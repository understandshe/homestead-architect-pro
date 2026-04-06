"""
Homestead Architect Pro 2026 - HIGH-END REALISTIC ENGINE
A data-driven 3D visualization system that maps user interview data to a high-fidelity environment.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from typing import Dict, Any, List, Tuple


class Visualizer3D:
    """High-fidelity 3D homestead engine using advanced Plotly techniques."""

    # Realistic Material Palette
    MATERIALS = {
        'grass': '#2D5A27',
        'soil': '#5D4037',
        'water': '#0077BE',
        'wood': '#795548',
        'wall': '#ECEFF1',
        'roof': '#455A64',
        'path': '#BDBDBD',
        'fence': '#8D6E63',
        'tree_trunk': '#4E342E',
        'tree_foliage': '#1B5E20',
    }

    def __init__(self):
        self.terrain_noise_amp = 3.0
        self.base_elevation = 5.0

    def create(self, layout: Dict[str, Any]):
        """Main entry point to render the high-end 3D map."""
        if not layout or 'dimensions' not in layout:
            st.warning("No design data found. Please complete the interview first.")
            return

        fig = go.Figure()

        # 1. Generate Realistic Terrain with Slope
        self._add_advanced_terrain(fig, layout)

        # 2. Add Structures (House, Sheds)
        self._add_realistic_house(fig, layout)
        self._add_livestock_enclosures(fig, layout)

        # 3. Add Nature (Trees, Water)
        self._add_high_poly_trees(fig, layout)
        self._add_water_source(fig, layout)

        # 4. Add Infrastructure (Paths, Fences)
        self._add_perimeter_fence(fig, layout)

        # Layout & Camera Configuration
        L, W = layout['dimensions']['length'], layout['dimensions']['width']
        loc = layout.get('location', 'Your Homestead')
        
        fig.update_layout(
            title=dict(
                text=f"<b>{loc}</b> | Realistic 3D Visualization",
                font=dict(size=24, color='#263238', family='Arial Black'),
                x=0.5
            ),
            scene=dict(
                xaxis=dict(title='Length (ft)', backgroundcolor="#F1F8E9", showbackground=True, gridcolor="#CFD8DC"),
                yaxis=dict(title='Width (ft)', backgroundcolor="#F1F8E9", showbackground=True, gridcolor="#CFD8DC"),
                zaxis=dict(title='Elevation', backgroundcolor="#E1F5FE", showbackground=True, gridcolor="#CFD8DC"),
                aspectmode='manual',
                aspectratio=dict(x=1, y=W/L if L > 0 else 1, z=0.3),
                camera=dict(eye=dict(x=1.5, y=-1.5, z=1.2)),
            ),
            margin=dict(l=0, r=0, t=80, b=0),
            height=900,
            paper_bgcolor='white',
            showlegend=True,
            legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.8)')
        )

        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})

        # Download Option
        html_data = fig.to_html(include_plotlyjs='cdn', full_html=True)
        st.download_button(
            label="📥 Download High-Res 3D Model (HTML)",
            data=html_data,
            file_name=f"homestead_3d_{loc.replace(' ', '_')}.html",
            mime="text/html",
            use_container_width=True
        )

    def _get_elevation(self, x: float, y: float, layout: Dict) -> float:
        """Calculate elevation based on slope direction and noise."""
        L, W = layout['dimensions']['length'], layout['dimensions']['width']
        slope = layout.get('slope', 'Flat')
        
        # Base slope effect
        z_slope = 0
        if slope == 'North': z_slope = (y / W) * 10
        elif slope == 'South': z_slope = ((W - y) / W) * 10
        elif slope == 'East': z_slope = (x / L) * 10
        elif slope == 'West': z_slope = ((L - x) / L) * 10
        
        # Natural noise
        noise = np.sin(x * 0.05) * np.cos(y * 0.05) * self.terrain_noise_amp
        return self.base_elevation + z_slope + noise

    def _add_advanced_terrain(self, fig, layout):
        L, W = layout['dimensions']['length'], layout['dimensions']['width']
        res = 40
        x = np.linspace(0, L, res)
        y = np.linspace(0, W, res)
        X, Y = np.meshgrid(x, y)
        Z = np.vectorize(lambda xi, yi: self._get_elevation(xi, yi, layout))(X, Y)

        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z,
            colorscale=[
                [0, '#3E2723'],   # Deep Soil
                [0.2, '#5D4037'], # Soil
                [0.4, '#2E7D32'], # Grass
                [1.0, '#1B5E20']  # Lush Grass
            ],
            showscale=False,
            name='Terrain',
            opacity=1.0,
            lighting=dict(ambient=0.6, diffuse=0.8, roughness=0.9, specular=0.1)
        ))

    def _create_box(self, x0, y0, z0, dx, dy, dz, color, name, showlegend=False):
        """Helper to create a 3D box mesh."""
        x = [x0, x0+dx, x0+dx, x0, x0, x0+dx, x0+dx, x0]
        y = [y0, y0, y0+dy, y0+dy, y0, y0, y0+dy, y0+dy]
        z = [z0, z0, z0, z0, z0+dz, z0+dz, z0+dz, z0+dz]
        i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
        j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
        k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]
        return go.Mesh3d(
            x=x, y=y, z=z, i=i, j=j, k=k,
            color=color, name=name, opacity=1, showlegend=showlegend
        )

    def _add_realistic_house(self, fig, layout):
        L, W = layout['dimensions']['length'], layout['dimensions']['width']
        pos = layout.get('house_position', 'Center')
        
        # Determine coordinates
        hx, hy = L/2, W/2
        if pos == 'North': hy = W * 0.8
        elif pos == 'South': hy = W * 0.2
        elif pos == 'East': hx = L * 0.8
        elif pos == 'West': hx = L * 0.2
        
        base_z = self._get_elevation(hx, hy, layout)
        hw, hl, hh = 30, 25, 15
        
        # Main Walls
        fig.add_trace(self._create_box(hx-hw/2, hy-hl/2, base_z, hw, hl, hh, self.MATERIALS['wall'], 'Main House', True))
        
        # Roof (Pyramid)
        rx = [hx-hw/2-2, hx+hw/2+2, hx+hw/2+2, hx-hw/2-2, hx]
        ry = [hy-hl/2-2, hy-hl/2-2, hy+hl/2+2, hy+hl/2+2, hy]
        rz = [base_z+hh, base_z+hh, base_z+hh, base_z+hh, base_z+hh+8]
        fig.add_trace(go.Mesh3d(
            x=rx, y=ry, z=rz,
            i=[0, 0, 1, 2], j=[1, 4, 2, 3], k=[4, 3, 4, 4],
            color=self.MATERIALS['roof'], name='Roof', showlegend=False
        ))

    def _add_high_poly_trees(self, fig, layout):
        count = layout.get('tree_count', 15)
        L, W = layout['dimensions']['length'], layout['dimensions']['width']
        rng = np.random.default_rng(42)
        
        for i in range(count):
            tx = rng.uniform(10, L-10)
            ty = rng.uniform(10, W-10)
            # Avoid house area
            if abs(tx - L/2) < 40 and abs(ty - W/2) < 40: continue
            
            base_z = self._get_elevation(tx, ty, layout)
            
            # Trunk
            fig.add_trace(self._create_box(tx-0.5, ty-0.5, base_z, 1, 1, 6, self.MATERIALS['tree_trunk'], 'Tree'))
            
            # Foliage (Cone)
            fig.add_trace(go.Cone(
                x=[tx], y=[ty], z=[base_z+10],
                u=[0], v=[0], w=[8],
                sizemode="absolute", sizeref=12,
                colorscale=[[0, self.MATERIALS['tree_foliage']], [1, '#004D40']],
                showscale=False, name='Fruit Tree', showlegend=(i==0)
            ))

    def _add_water_source(self, fig, layout):
        source = layout.get('water_source', 'None yet')
        L, W = layout['dimensions']['length'], layout['dimensions']['width']
        
        if source == 'Borewell/Well':
            # Well structure
            wx, wy = L*0.2, W*0.8
            wz = self._get_elevation(wx, wy, layout)
            fig.add_trace(self._create_box(wx-3, wy-3, wz, 6, 6, 4, '#78909C', 'Borewell', True))
        
        elif source == 'River/Pond':
            # Pond
            px, py = L*0.1, W*0.1
            res = 15
            theta = np.linspace(0, 2*np.pi, res)
            r = 15
            cx = px + r * np.cos(theta)
            cy = py + r * np.sin(theta)
            cz = [self._get_elevation(px, py, layout) + 0.1] * res
            
            fig.add_trace(go.Mesh3d(
                x=cx, y=cy, z=cz,
                color=self.MATERIALS['water'], opacity=0.8, name='Pond', showlegend=True
            ))

    def _add_livestock_enclosures(self, fig, layout):
        animals = layout.get('livestock', [])
        if not animals or 'None' in animals: return
        
        L, W = layout['dimensions']['length'], layout['dimensions']['width']
        for idx, animal in enumerate(animals):
            if animal == 'None': continue
            # Place enclosures in a grid
            ex = 20 + (idx * 40) % (L - 40)
            ey = W - 40
            ez = self._get_elevation(ex, ey, layout)
            
            # Enclosure Fence
            fig.add_trace(self._create_box(ex-10, ey-10, ez, 20, 20, 0.5, self.MATERIALS['fence'], f'{animal} Area', True))
            # Small Shed
            fig.add_trace(self._create_box(ex-5, ey-5, ez, 10, 10, 6, self.MATERIALS['wood'], f'{animal} Shed'))

    def _add_perimeter_fence(self, fig, layout):
        L, W = layout['dimensions']['length'], layout['dimensions']['width']
        # Simple perimeter line at elevation
        px = [0, L, L, 0, 0]
        py = [0, 0, W, W, 0]
        pz = [self._get_elevation(xi, yi, layout) + 1 for xi, yi in zip(px, py)]
        
        fig.add_trace(go.Scatter3d(
            x=px, y=py, z=pz,
            mode='lines',
            line=dict(color=self.MATERIALS['fence'], width=5),
            name='Perimeter Fence'
        ))
