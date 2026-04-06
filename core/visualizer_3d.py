"""
Homestead Architect Pro 2026 - REALISTIC EDITION
Premium 3D visualization with realistic terrain and high-fidelity architectural models.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from typing import Dict, Any, List, Tuple


class Visualizer3D:
    """Creates realistic interactive 3D homestead models using Plotly."""

    # Realistic Earthy Tones
    ZONE_COLORS = {
        "z0": "#C2B280",  # Sand/Residential
        "z1": "#4F7942",  # Fern Green/Kitchen Garden
        "z2": "#228B22",  # Forest Green/Food Forest
        "z3": "#8DB600",  # Apple Green/Pasture
        "z4": "#013220",  # Dark Green/Buffer
    }
    
    ZONE_NAMES = {
        "z0": "Zone 0 - Residential",
        "z1": "Zone 1 - Kitchen Garden",
        "z2": "Zone 2 - Food Forest",
        "z3": "Zone 3 - Pasture / Crops",
        "z4": "Zone 4 - Buffer Zone",
    }

    def __init__(self):
        self._terrain_amp = 4.5

    def create(self, layout: Dict[str, Any]):
        """Main entry point for Streamlit to render the 3D map."""
        if not layout or "dimensions" not in layout:
            st.info("Please generate your map in the Design tab first.")
            return

        fig = go.Figure()

        # Add components
        self._add_realistic_terrain(fig, layout)
        self._add_zones_3d(fig, layout)
        self._add_house_3d(fig, layout)
        self._add_trees_3d(fig, layout)
        self._add_paths_3d(fig, layout)

        L = layout["dimensions"]["L"]
        W = layout["dimensions"]["W"]
        acres = layout.get("acres", round(L * W / 43560, 2))
        loc_name = layout.get("location", "Custom Plot")
        title_text = f"<b>{loc_name}</b> | {acres:.2f} Acres | {int(L)}x{int(W)} ft"

        camera_iso = dict(eye=dict(x=1.8, y=-1.8, z=1.0), up=dict(x=0, y=0, z=1))
        z_ratio = max(0.25, min(0.50, (self._terrain_amp + 10) / max(L, W)))

        fig.update_layout(
            title=dict(text=title_text, font=dict(size=18, color="#2C3E50", family="Serif"), x=0.5),
            scene=dict(
                xaxis_title="Length (ft)",
                yaxis_title="Width (ft)",
                zaxis_title="Elevation",
                aspectmode="manual",
                aspectratio=dict(x=1.0, y=max(0.7, W / max(L, 1)), z=z_ratio),
                bgcolor="#F8F9FA",
                camera=camera_iso,
                xaxis=dict(showgrid=True, gridcolor="#E0E0E0"),
                yaxis=dict(showgrid=True, gridcolor="#E0E0E0"),
                zaxis=dict(showgrid=True, gridcolor="#E0E0E0"),
            ),
            margin=dict(l=0, r=0, t=60, b=0),
            height=800,
            showlegend=True,
            legend=dict(x=0.02, y=0.98, bgcolor="rgba(255,255,255,0.7)"),
            paper_bgcolor="#FFFFFF",
        )

        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})

        # Download button
        try:
            html_bytes = fig.to_html(include_plotlyjs="cdn", full_html=True)
            safe_name = loc_name.replace(" ", "_")
            st.download_button(
                label="Download Realistic 3D Map (HTML)",
                data=html_bytes,
                file_name=f"realistic_homestead_{safe_name}.html",
                mime="text/html",
                use_container_width=True,
            )
        except Exception:
            pass

    def _terrain_height(self, x: float, y: float) -> float:
        x, y = float(x), float(y)
        h1 = np.sin(x * 0.015) * 1.2 + np.cos(y * 0.012) * 1.0
        h2 = np.sin((x + y) * 0.04) * 0.4 + np.cos((x - y) * 0.035) * 0.3
        return (h1 + h2) * self._terrain_amp

    def _add_realistic_terrain(self, fig, layout):
        L, W = layout["dimensions"]["L"], layout["dimensions"]["W"]
        res = 30
        x = np.linspace(0, L, res)
        y = np.linspace(0, W, res)
        X, Y = np.meshgrid(x, y)
        Z = np.vectorize(self._terrain_height)(X, Y)

        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z,
            colorscale=[[0, "#8B4513"], [0.2, "#A0522D"], [0.4, "#228B22"], [1.0, "#006400"]],
            opacity=0.9,
            showscale=False,
            name="Terrain"
        ))

    def _add_zones_3d(self, fig, layout):
        zones = layout.get("zone_positions", {})
        for zid, zdata in zones.items():
            x0, y0 = zdata["x"], zdata["y"]
            x1, y1 = x0 + zdata["width"], y0 + zdata["height"]
            
            res = 5
            zx = np.linspace(x0, x1, res)
            zy = np.linspace(y0, y1, res)
            ZX, ZY = np.meshgrid(zx, zy)
            ZZ = np.vectorize(self._terrain_height)(ZX, ZY) + 0.2
            
            color = self.ZONE_COLORS.get(zid, "#CCCCCC")
            fig.add_trace(go.Surface(
                x=ZX, y=ZY, z=ZZ,
                colorscale=[[0, color], [1, color]],
                opacity=0.5,
                showscale=False,
                name=self.ZONE_NAMES.get(zid, zid)
            ))

    def _box_mesh(self, x0, y0, z0, x1, y1, z1, color, name):
        x = [x0, x1, x1, x0, x0, x1, x1, x0]
        y = [y0, y0, y1, y1, y0, y0, y1, y1]
        z = [z0, z0, z0, z0, z1, z1, z1, z1]
        i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
        j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
        k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]
        return go.Mesh3d(
            x=x, y=y, z=z, i=i, j=j, k=k,
            color=color, name=name, opacity=1.0
        )

    def _add_house_3d(self, fig, layout):
        L, W = layout["dimensions"]["L"], layout["dimensions"]["W"]
        h_pos = layout.get("house_position", "Center")
        hx, hy = L * 0.5, W * 0.5
        if h_pos == "North": hy = W * 0.8
        elif h_pos == "South": hy = W * 0.2
        
        hw, hh = 25, 20
        x0, y0 = hx - hw/2, hy - hh/2
        x1, y1 = hx + hw/2, hy + hh/2
        base_z = self._terrain_height(hx, hy)
        wall_z = base_z + 10
        roof_z = wall_z + 6
        
        fig.add_trace(self._box_mesh(x0, y0, base_z, x1, y1, wall_z, "#FDF5E6", "Main House"))
        
        fig.add_trace(go.Mesh3d(
            x=[x0, x1, x1, x0, hx],
            y=[y0, y0, y1, y1, hy],
            z=[wall_z, wall_z, wall_z, wall_z, roof_z],
            i=[0, 0, 1, 2], j=[1, 4, 2, 3], k=[4, 3, 4, 4],
            color="#4682B4", name="Roof"
        ))

    def _add_trees_3d(self, fig, layout):
        zones = layout.get("zone_positions", {})
        if "z2" not in zones: return
        z = zones["z2"]
        rng = np.random.default_rng(42)
        
        for _ in range(10):
            tx = rng.uniform(z["x"] + 5, z["x"] + z["width"] - 5)
            ty = rng.uniform(z["y"] + 5, z["y"] + z["height"] - 5)
            ground = self._terrain_height(tx, ty)
            
            # Trunk
            fig.add_trace(go.Mesh3d(
                x=[tx-0.4, tx+0.4, tx+0.4, tx-0.4, tx-0.4, tx+0.4, tx+0.4, tx-0.4],
                y=[ty-0.4, ty-0.4, ty+0.4, ty+0.4, ty-0.4, ty-0.4, ty+0.4, ty+0.4],
                z=[ground, ground, ground, ground, ground+6, ground+6, ground+6, ground+6],
                i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2], j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3], k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
                color="#8B4513", showlegend=False
            ))
            
            # Foliage
            fig.add_trace(go.Cone(
                x=[tx], y=[ty], z=[ground + 9],
                u=[0], v=[0], w=[8],
                sizemode="absolute", sizeref=10,
                colorscale=[[0, "#228B22"], [1, "#006400"]],
                showscale=False, name="Tree"
            ))

    def _add_paths_3d(self, fig, layout):
        zones = layout.get("zone_positions", {})
        if "z0" in zones and "z1" in zones:
            z0, z1 = zones["z0"], zones["z1"]
            sx, sy = z0["x"] + z0["width"]/2, z0["y"]
            ex, ey = z1["x"] + z1["width"]/2, z1["y"] + z1["height"]
            
            t = np.linspace(0, 1, 20)
            px = sx + (ex - sx) * t
            py = sy + (ey - sy) * t
            pz = np.vectorize(self._terrain_height)(px, py) + 0.25
            
            fig.add_trace(go.Scatter3d(
                x=px, y=py, z=pz,
                mode="lines",
                line=dict(color="#D2B48C", width=8),
                name="Path"
            ))
