import streamlit as st
import plotly.graph_objects as go
import numpy as np
from typing import Dict, Any, List

class Visualizer3D:

    ZONE_COLORS = {
        'z0': '#F5F5DC',
        'z1': '#90EE90',
        'z2': '#228B22',
        'z3': '#F0E68C',
        'z4': '#DDA0DD',
    }

    def create(self, layout: Dict[str, Any]):
        if not layout or 'dimensions' not in layout:
            st.info("Generate layout first")
            return

        fig = go.Figure()

        self._add_terrain(fig, layout)
        self._add_zones_3d(fig, layout)
        self._add_house_3d(fig, layout)
        self._add_features_3d(fig, layout)
        self._add_trees_3d(fig, layout)

        fig.update_layout(
            scene=dict(
                bgcolor='#D0E8F5',
                aspectmode='data',
                camera=dict(
                    eye=dict(x=1.8, y=-1.8, z=1.2)
                )
            ),
            margin=dict(l=0, r=0, t=40, b=0),
            height=700
        )

        st.plotly_chart(fig, use_container_width=True)

    # ================= TERRAIN =================
    def _add_terrain(self, fig, layout):
        L, W = layout['dimensions']['L'], layout['dimensions']['W']

        x = np.linspace(0, L, 60)
        y = np.linspace(0, W, 60)
        X, Y = np.meshgrid(x, y)

        noise = (
            3*np.sin(X/40) +
            2*np.cos(Y/35) +
            1.5*np.sin((X+Y)/60)
        )

        Z = noise

        slope = layout.get('slope', 'Flat')
        if slope == 'South': Z += Y * 0.05
        elif slope == 'North': Z += (W - Y) * 0.05
        elif slope == 'East': Z += X * 0.05
        elif slope == 'West': Z += (L - X) * 0.05

        self.X = X
        self.Y = Y
        self.Z = Z

        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z,
            colorscale=[[0, '#81C784'], [1, '#2E7D32']],
            showscale=False,
            opacity=0.95
        ))

    def _get_height(self, x, y):
        xi = np.abs(self.X[0] - x).argmin()
        yi = np.abs(self.Y[:,0] - y).argmin()
        return self.Z[yi][xi]

    # ================= ZONES =================
    def _add_zones_3d(self, fig, layout):
        for zone_id, pos in layout.get('zone_positions', {}).items():

            z_base = self._get_height(pos['x'], pos['y'])

            fig.add_trace(go.Mesh3d(
                x=[pos['x'], pos['x']+pos['width'], pos['x']+pos['width'], pos['x']],
                y=[pos['y'], pos['y'], pos['y']+pos['height'], pos['y']+pos['height']],
                z=[z_base+1.5]*4,
                color=self.ZONE_COLORS.get(zone_id, '#CCCCCC'),
                opacity=0.3
            ))

    # ================= HOUSE =================
    def _add_house_3d(self, fig, layout):
        L, W = layout['dimensions']['L'], layout['dimensions']['W']

        hx, hy = L*0.4, W*0.4
        hw, hd = L*0.2, W*0.2

        base_z = self._get_height(hx, hy)

        fig.add_trace(go.Mesh3d(
            x=[hx, hx+hw, hx+hw, hx, hx, hx+hw, hx+hw, hx],
            y=[hy, hy, hy+hd, hy+hd, hy, hy, hy+hd, hy+hd],
            z=[base_z,base_z,base_z,base_z, base_z+14,base_z+14,base_z+14,base_z+14],
            color='#8D6E63'
        ))

        fig.add_trace(go.Mesh3d(
            x=[hx, hx+hw, hx+hw, hx, hx+hw/2],
            y=[hy, hy, hy+hd, hy+hd, hy+hd/2],
            z=[base_z+14,base_z+14,base_z+14,base_z+14,base_z+20],
            color='#4E342E'
        ))

    # ================= FEATURES =================
    def _add_features_3d(self, fig, layout):
        features = layout.get('features', {})

        if 'well' in features:
            f = features['well']
            base_z = self._get_height(f['x'], f['y'])

            t = np.linspace(0, 2*np.pi, 24)
            z = np.array([base_z, base_z+6])
            T, Z = np.meshgrid(t, z)

            fig.add_trace(go.Surface(
                x=f['x'] + 4*np.cos(T),
                y=f['y'] + 4*np.sin(T),
                z=Z,
                showscale=False
            ))

    # ================= TREES =================
    def _add_trees_3d(self, fig, layout):
        zone_pos = layout.get('zone_positions', {})
        if 'z2' not in zone_pos:
            return

        z = zone_pos['z2']

        for i in range(15):
            tx = z['x'] + np.random.uniform(0, z['width'])
            ty = z['y'] + np.random.uniform(0, z['height'])

            ground = self._get_height(tx, ty)

            fig.add_trace(go.Mesh3d(
                x=[tx, tx+3, tx-3, tx],
                y=[ty, ty+3, ty+3, ty],
                z=[ground+5,ground+5,ground+5,ground+15],
                color=np.random.choice(['#2E7D32','#1B5E20','#388E3C'])
            ))
