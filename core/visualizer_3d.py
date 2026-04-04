import streamlit as st
import plotly.graph_objects as go
import numpy as np
from typing import Dict, Any, List

class Visualizer3D:

    ZONE_COLORS = {
        'z0': '#F5F5DC',
        'z1': '#90EE90',
        'z2': '#2E7D32',
        'z3': '#F0E68C',
        'z4': '#CE93D8',
    }

    ZONE_NAMES = {
        'z0': 'Residential',
        'z1': 'Kitchen Garden',
        'z2': 'Food Forest',
        'z3': 'Crops',
        'z4': 'Buffer',
    }

    # ================= MAIN =================
    def create(self, layout: Dict[str, Any]):
        if not layout or 'dimensions' not in layout:
            st.info("Generate layout first")
            return

        fig = go.Figure()

        self._add_terrain(fig, layout)
        self._add_zones(fig, layout)
        self._add_house(fig, layout)
        self._add_features(fig, layout)
        self._add_livestock(fig, layout)
        self._add_trees(fig, layout)
        self._add_paths(fig, layout)
        self._add_labels(fig, layout)

        fig.update_layout(
            scene=dict(
                bgcolor='#87CEEB',
                aspectmode='data',
                camera=dict(
                    eye=dict(x=1.9, y=-1.9, z=1.3)
                )
            ),
            margin=dict(l=0, r=0, t=40, b=0),
            height=700
        )

        st.plotly_chart(fig, use_container_width=True)

        # ✅ HTML DOWNLOAD (तेरा original feature वापस)
        html = fig.to_html(include_plotlyjs='cdn', full_html=True)
        st.download_button(
            "Download 3D Map",
            html,
            "3d_map.html",
            "text/html"
        )

    # ================= TERRAIN =================
    def _add_terrain(self, fig, layout):
        L, W = layout['dimensions']['L'], layout['dimensions']['W']

        x = np.linspace(0, L, 80)
        y = np.linspace(0, W, 80)
        X, Y = np.meshgrid(x, y)

        noise = (
            4*np.sin(X/50) +
            3*np.cos(Y/40) +
            2*np.sin((X+Y)/70)
        )

        Z = noise

        slope = layout.get('slope', 'Flat')
        if slope == 'South': Z += Y * 0.05
        elif slope == 'North': Z += (W-Y)*0.05
        elif slope == 'East': Z += X * 0.05
        elif slope == 'West': Z += (L-X)*0.05

        self.X, self.Y, self.Z = X, Y, Z

        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z,
            colorscale=[
                [0, '#4CAF50'],
                [0.5, '#2E7D32'],
                [1, '#1B5E20']
            ],
            showscale=False,
            opacity=1
        ))

    def _get_z(self, x, y):
        xi = np.abs(self.X[0]-x).argmin()
        yi = np.abs(self.Y[:,0]-y).argmin()
        return self.Z[yi][xi]

    # ================= ZONES =================
    def _add_zones(self, fig, layout):
        for zid, z in layout.get('zone_positions', {}).items():
            base = self._get_z(z['x'], z['y'])

            fig.add_trace(go.Mesh3d(
                x=[z['x'], z['x']+z['width'], z['x']+z['width'], z['x']],
                y=[z['y'], z['y'], z['y']+z['height'], z['y']+z['height']],
                z=[base+1.2]*4,
                color=self.ZONE_COLORS[zid],
                opacity=0.25,
                name=self.ZONE_NAMES[zid]
            ))

    # ================= HOUSE =================
    def _add_house(self, fig, layout):
        L, W = layout['dimensions']['L'], layout['dimensions']['W']

        hx, hy = L*0.4, W*0.4
        hw, hd = L*0.2, W*0.2

        base = self._get_z(hx, hy)

        fig.add_trace(go.Mesh3d(
            x=[hx,hx+hw,hx+hw,hx,hx,hx+hw,hx+hw,hx],
            y=[hy,hy,hy+hd,hy+hd,hy,hy,hy+hd,hy+hd],
            z=[base,base,base,base, base+15,base+15,base+15,base+15],
            color='#8D6E63'
        ))

        fig.add_trace(go.Mesh3d(
            x=[hx,hx+hw,hx+hw,hx,hx+hw/2],
            y=[hy,hy,hy+hd,hy+hd,hy+hd/2],
            z=[base+15,base+15,base+15,base+15,base+22],
            color='#4E342E'
        ))

    # ================= FEATURES =================
    def _add_features(self, fig, layout):
        f = layout.get('features', {})

        if 'pond' in f:
            p = f['pond']
            base = self._get_z(p['x'], p['y'])

            r = p['radius']
            t = np.linspace(0, 2*np.pi, 40)
            R, T = np.meshgrid(np.linspace(0,r,10), t)

            fig.add_trace(go.Surface(
                x=p['x']+R*np.cos(T),
                y=p['y']+R*np.sin(T),
                z=np.full_like(R, base-1),
                colorscale='Blues',
                showscale=False
            ))

    # ================= LIVESTOCK =================
    def _add_livestock(self, fig, layout):
        for k, f in layout.get('features', {}).items():
            if 'shed' not in k:
                continue

            base = self._get_z(f['x'], f['y'])

            fig.add_trace(go.Mesh3d(
                x=[f['x'],f['x']+f['width'],f['x']+f['width'],f['x'],f['x'],f['x']+f['width'],f['x']+f['width'],f['x']],
                y=[f['y'],f['y'],f['y']+f['height'],f['y']+f['height'],f['y'],f['y'],f['y']+f['height'],f['y']+f['height']],
                z=[base,base,base,base, base+8,base+8,base+8,base+8],
                color='#D7CCC8'
            ))

    # ================= TREES =================
    def _add_trees(self, fig, layout):
        if 'z2' not in layout.get('zone_positions', {}):
            return

        z = layout['zone_positions']['z2']

        for _ in range(25):
            tx = z['x'] + np.random.uniform(0, z['width'])
            ty = z['y'] + np.random.uniform(0, z['height'])

            base = self._get_z(tx, ty)

            fig.add_trace(go.Mesh3d(
                x=[tx, tx+3, tx-3, tx],
                y=[ty, ty+3, ty+3, ty],
                z=[base+5, base+5, base+5, base+15],
                color=np.random.choice(['#2E7D32','#1B5E20','#388E3C'])
            ))

    # ================= PATH =================
    def _add_paths(self, fig, layout):
        L, W = layout['dimensions']['L'], layout['dimensions']['W']

        x = np.linspace(0, L, 120)
        y = np.full_like(x, W*0.5)
        z = [self._get_z(xi, yi)+1 for xi, yi in zip(x,y)]

        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode='lines',
            line=dict(width=10, color='#A1887F')
        ))

    # ================= LABELS =================
    def _add_labels(self, fig, layout):
        L, W = layout['dimensions']['L'], layout['dimensions']['W']

        fig.add_trace(go.Scatter3d(
            x=[L*0.5],
            y=[W*0.5],
            z=[30],
            mode='text',
            text=['Main House'],
            showlegend=False
        ))
