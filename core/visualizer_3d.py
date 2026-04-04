"""
Homestead Architect Pro 2026 - ULTRA EDITION
Premium 3D visualization with terrain, cinematic cameras, HUD toggle,
and high-fidelity export-ready interaction.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from typing import Dict, Any, List, Tuple


class Visualizer3D:
    """Creates interactive 3D homestead models using Plotly."""

    ZONE_COLORS = {
        'z0': '#D9C8A5',
        'z1': '#8BCB88',
        'z2': '#4F8F4B',
        'z3': '#C4B56A',
        'z4': '#8E7FA8',
    }
    ZONE_NAMES = {
        'z0': 'Zone 0 - Residential',
        'z1': 'Zone 1 - Kitchen Garden',
        'z2': 'Zone 2 - Food Forest',
        'z3': 'Zone 3 - Pasture / Crops',
        'z4': 'Zone 4 - Buffer Zone',
    }

    def __init__(self):
        self._terrain_x = None
        self._terrain_y = None
        self._terrain_z = None
        self._terrain_amp = 6.0

    def create(self, layout: Dict[str, Any]):
        """Main entry point for Streamlit to render the 3D map."""
        if not layout or 'dimensions' not in layout:
            st.info("Please generate your map in the Design tab first.")
            return

        fig = go.Figure()

        self._add_terrain(fig, layout)
        self._add_zones_3d(fig, layout)
        self._add_house_3d(fig, layout)
        self._add_features_3d(fig, layout)
        self._add_all_livestock_3d(fig, layout)
        self._add_trees_3d(fig, layout)
        self._add_paths_3d(fig, layout)
        self._add_3d_labels(fig, layout)

        L = layout['dimensions']['L']
        W = layout['dimensions']['W']
        acres = layout.get('acres', round(L * W / 43560, 2))
        loc_name = layout.get('location', 'Custom Plot')
        zones_count = len(layout.get('zone_positions', {}))
        title_text = f"{loc_name} - {acres:.2f} acres ({int(L)} x {int(W)} ft) - {zones_count} zones"

        camera_top = dict(eye=dict(x=0.0, y=0.0, z=2.8), up=dict(x=0, y=1, z=0))
        camera_iso = dict(eye=dict(x=2.0, y=-2.0, z=1.2), up=dict(x=0, y=0, z=1))
        camera_ground = dict(eye=dict(x=2.6, y=-1.2, z=0.42), up=dict(x=0, y=0, z=1))
        z_ratio = max(0.30, min(0.60, (self._terrain_amp + 8) / max(L, W)))

        orbit_frames = self._build_camera_orbit_frames(radius=2.4, z=1.15, steps=40)
        fig.frames = orbit_frames

        fig.update_layout(
            title=dict(
                text=title_text,
                font=dict(size=17, color='#244A2B', family='Arial'),
                x=0.5,
            ),
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    x=0.02,
                    y=1.14,
                    showactive=True,
                    buttons=[
                        dict(label="Show Info", method="relayout", args=[{"title.text": title_text}]),
                        dict(label="Hide Info", method="relayout", args=[{"title.text": ""}]),
                    ],
                ),
                dict(
                    type="buttons",
                    direction="left",
                    x=0.32,
                    y=1.14,
                    showactive=True,
                    buttons=[
                        dict(label="Top View", method="relayout", args=[{"scene.camera": camera_top}]),
                        dict(label="Isometric View", method="relayout", args=[{"scene.camera": camera_iso}]),
                        dict(label="Ground Perspective", method="relayout", args=[{"scene.camera": camera_ground}]),
                    ],
                ),
                dict(
                    type="buttons",
                    direction="left",
                    x=0.72,
                    y=1.14,
                    showactive=True,
                    buttons=[
                        dict(label="Show Legend", method="relayout", args=[{"showlegend": True}]),
                        dict(label="Hide Legend", method="relayout", args=[{"showlegend": False}]),
                    ],
                ),
                dict(
                    type="buttons",
                    direction="left",
                    x=0.02,
                    y=1.08,
                    showactive=False,
                    buttons=[
                        dict(
                            label="Start Tour",
                            method="animate",
                            args=[
                                None,
                                {
                                    "frame": {"duration": 90, "redraw": False},
                                    "transition": {"duration": 50, "easing": "linear"},
                                    "fromcurrent": True,
                                    "mode": "immediate",
                                },
                            ],
                        ),
                        dict(
                            label="Stop Tour",
                            method="animate",
                            args=[
                                [None],
                                {
                                    "frame": {"duration": 0, "redraw": False},
                                    "transition": {"duration": 0},
                                    "mode": "immediate",
                                },
                            ],
                        ),
                    ],
                ),
            ],
            scene=dict(
                xaxis_title='Length (ft)',
                yaxis_title='Width (ft)',
                zaxis_title='Height (ft)',
                aspectmode='manual',
                aspectratio=dict(x=1.0, y=max(0.7, W / max(L, 1)), z=z_ratio),
                bgcolor='#DDE8F1',
                camera=camera_iso,
                dragmode='orbit',
                camera_projection=dict(type='perspective'),
                xaxis=dict(showgrid=False, zeroline=False, showbackground=False),
                yaxis=dict(showgrid=False, zeroline=False, showbackground=False),
                zaxis=dict(showgrid=False, zeroline=False, showbackground=False),
            ),
            legend=dict(
                x=0.01,
                y=0.99,
                bgcolor='rgba(255,255,255,0.82)',
                font=dict(size=10),
            ),
            paper_bgcolor='#E8EFF5',
            margin=dict(l=0, r=0, t=50, b=0),
            clickmode='event+select',
            height=700,
            showlegend=False,
            uirevision='3d-map-keep-zoom',
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displaylogo": False,
                "responsive": True,
                "scrollZoom": True,
                "doubleClick": "reset+autosize",
            }
        )

        try:
            html_bytes = fig.to_html(include_plotlyjs='cdn', full_html=True)
            st.download_button(
                label="Download 3D Map (HTML)",
                data=html_bytes,
                file_name=f"homestead_3d_{loc_name.replace(' ', '_')}.html",
                mime="text/html",
                use_container_width=True,
            )
        except Exception:
            pass

    @staticmethod
    def _build_camera_orbit_frames(radius: float = 2.4, z: float = 1.1, steps: int = 36) -> List[go.Frame]:
        """Create smooth camera orbit frames for cinematic preview."""
        frames = []
        for i in range(steps):
            theta = (2 * np.pi * i) / steps
            cam = dict(
                eye=dict(x=radius * np.cos(theta), y=radius * np.sin(theta), z=z),
                up=dict(x=0, y=0, z=1),
            )
            frames.append(go.Frame(name=f"orbit_{i}", layout=dict(scene_camera=cam)))
        return frames

    def _terrain_height(self, x: float, y: float) -> float:
        """Procedural terrain function for object snapping."""
        x = float(x)
        y = float(y)
        base = (
            np.sin(x * 0.028) * 0.9
            + np.cos(y * 0.023) * 0.8
            + np.sin((x + y) * 0.012) * 0.55
            + np.cos((x - y) * 0.017) * 0.45
        )
        micro = np.sin(x * 0.11) * np.cos(y * 0.09) * 0.14
        return (base + micro) * self._terrain_amp

    def _sample_zone_ground(self, x0: float, y0: float, x1: float, y1: float) -> float:
        pts = [
            (x0, y0), (x1, y0), (x1, y1), (x0, y1), ((x0 + x1) / 2, (y0 + y1) / 2)
        ]
        return float(np.mean([self._terrain_height(px, py) for px, py in pts]))

    @staticmethod
    def _mesh_indices_for_box() -> Tuple[List[int], List[int], List[int]]:
        fi = [0, 0, 4, 4, 0, 0, 2, 2, 0, 0, 1, 1]
        fj = [1, 2, 5, 6, 1, 5, 3, 7, 3, 7, 2, 6]
        fk = [2, 3, 6, 7, 5, 4, 7, 6, 7, 4, 6, 5]
        return fi, fj, fk

    def _add_shadow_rect(self, fig, x0, y0, x1, y1, z, alpha=0.18):
        fig.add_trace(go.Mesh3d(
            x=[x0, x1, x1, x0],
            y=[y0, y0, y1, y1],
            z=[z, z, z, z],
            i=[0, 0], j=[1, 2], k=[2, 3],
            color='#1B1B1B', opacity=alpha,
            showlegend=False, hoverinfo='skip'
        ))

    def _add_3d_labels(self, fig, layout):
        """Add text labels above major 3D objects."""
        features = layout.get('features', {})
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        label_data = []

        h_pos = layout.get('house_position', 'Center')
        hx, hy = L * 0.5, W * 0.5
        if h_pos == 'North':
            hy = W * 0.85
        elif h_pos == 'South':
            hy = W * 0.1
        hz = self._terrain_height(hx, hy)
        label_data.append({'x': hx, 'y': hy, 'z': hz + 22, 'text': 'Main House'})

        livestock_map = {
            'goat_shed': 'Goat Shed',
            'chicken_coop': 'Chicken Coop',
            'piggery': 'Piggery',
            'cow_shed': 'Cow Shed',
            'fish_tanks': 'Fish Pond',
            'bee_hives': 'Bee Hives',
        }
        for key, text in livestock_map.items():
            if key in features:
                f = features[key]
                cx, cy = f['x'] + f['width'] / 2, f['y'] + f['height'] / 2
                label_data.append({'x': cx, 'y': cy, 'z': self._terrain_height(cx, cy) + 14, 'text': text})

        fig.add_trace(go.Scatter3d(
            x=[d['x'] for d in label_data],
            y=[d['y'] for d in label_data],
            z=[d['z'] for d in label_data],
            mode='text',
            text=[d['text'] for d in label_data],
            textfont=dict(size=8, color="#0E2A14"),
            name="Labels",
            showlegend=False,
            hoverinfo='skip',
        ))

    @staticmethod
    def _box_mesh(x0, y0, z0, x1, y1, z1, color, name,
                  opacity=0.88, show_legend=True, hover_text='') -> go.Mesh3d:
        vx = [x0, x1, x1, x0, x0, x1, x1, x0]
        vy = [y0, y0, y1, y1, y0, y0, y1, y1]
        vz = [z0, z0, z0, z0, z1, z1, z1, z1]
        fi, fj, fk = Visualizer3D._mesh_indices_for_box()
        return go.Mesh3d(
            x=vx,
            y=vy,
            z=vz,
            i=fi,
            j=fj,
            k=fk,
            color=color,
            opacity=opacity,
            name=name,
            showlegend=show_legend,
            flatshading=True,
            hovertemplate=hover_text if hover_text else f"{name}<extra></extra>",
            lighting=dict(ambient=0.35, diffuse=0.85, specular=0.45, roughness=0.42, fresnel=0.25),
        )

    @staticmethod
    def _hip_roof(x0, y0, x1, y1, base_z, apex_z, color, name='Roof') -> go.Mesh3d:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        vx = [x0, x1, x1, x0, cx]
        vy = [y0, y0, y1, y1, cy]
        vz = [base_z, base_z + 0.6, base_z + 0.6, base_z, apex_z]
        fi, fj, fk = [0, 1, 2, 3], [1, 2, 3, 0], [4, 4, 4, 4]
        return go.Mesh3d(
            x=vx, y=vy, z=vz, i=fi, j=fj, k=fk,
            color=color, opacity=0.97, name=name,
            showlegend=False, flatshading=True,
            lighting=dict(ambient=0.30, diffuse=0.90, specular=0.55, roughness=0.35, fresnel=0.28),
            hoverinfo='skip',
        )

    @staticmethod
    def _cone_tree(tx, ty, trunk_bot_z=1.5, trunk_top_z=7.0, canopy_bot_z=7.0, canopy_top_z=18.0,
                   canopy_r=7.5, trunk_r=1.2, color_canopy='#2E7D32', label='', show_legend=False) -> List:
        """Layered foliage tree for richer realism."""
        traces = []
        n = 16

        theta_t = np.linspace(0, 2 * np.pi, n)
        z_t = np.array([trunk_bot_z, trunk_top_z])
        T_grid, Z_grid = np.meshgrid(theta_t, z_t)
        traces.append(go.Surface(
            x=tx + trunk_r * np.cos(T_grid),
            y=ty + trunk_r * np.sin(T_grid),
            z=Z_grid,
            colorscale=[[0, '#6D4C41'], [1, '#8D6E63']],
            showscale=False,
            showlegend=False,
            opacity=0.96,
            hoverinfo='skip',
        ))

        def canopy_mesh(radius, z_bottom, z_top, color, opacity):
            theta_c = np.linspace(0, 2 * np.pi, n, endpoint=False)
            vx = list(tx + radius * np.cos(theta_c)) + [tx]
            vy = list(ty + radius * np.sin(theta_c)) + [ty]
            vz = [z_bottom] * n + [z_top]
            return go.Mesh3d(
                x=vx, y=vy, z=vz,
                i=list(range(n)), j=[(k + 1) % n for k in range(n)], k=[n] * n,
                color=color, opacity=opacity,
                name=label if label else 'Tree',
                showlegend=show_legend,
                flatshading=True,
                hovertemplate=(f"{label or 'Tree'}<extra></extra>"),
                lighting=dict(ambient=0.30, diffuse=0.92, specular=0.25, roughness=0.58, fresnel=0.15),
            )

        traces.append(canopy_mesh(canopy_r, canopy_bot_z, canopy_top_z, color_canopy, 0.86))
        traces.append(canopy_mesh(canopy_r * 0.72, canopy_bot_z + 2.8, canopy_top_z + 3.0, '#3E8A3F', 0.80))
        traces.append(canopy_mesh(canopy_r * 0.48, canopy_bot_z + 5.3, canopy_top_z + 5.1, '#2E6F33', 0.74))
        return traces

    def _add_terrain(self, fig, layout):
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        x = np.linspace(0, L, 56)
        y = np.linspace(0, W, 56)
        X, Y = np.meshgrid(x, y)

        Z = np.vectorize(self._terrain_height)(X, Y)
        slope = layout.get('slope', 'Flat')
        if slope == 'South':
            Z += Y * 0.010
        elif slope == 'North':
            Z += (W - Y) * 0.010
        elif slope == 'East':
            Z += X * 0.010
        elif slope == 'West':
            Z += (L - X) * 0.010

        self._terrain_x, self._terrain_y, self._terrain_z = X, Y, Z

        fig.add_trace(go.Surface(
            x=X,
            y=Y,
            z=Z,
            colorscale=[
                [0.0, '#1D5A2C'],
                [0.35, '#2E7D32'],
                [0.60, '#4C9A46'],
                [1.0, '#86C36D'],
            ],
            showscale=False,
            opacity=0.99,
            name='Terrain',
            showlegend=True,
            lighting=dict(ambient=0.28, diffuse=0.88, specular=0.20, roughness=0.66, fresnel=0.08),
            hovertemplate='Terrain elevation: %{z:.2f} ft<extra></extra>',
        ))

    def _add_zones_3d(self, fig, layout):
        for zone_id, pos in layout.get('zone_positions', {}).items():
            x0, y0 = pos['x'], pos['y']
            x1, y1 = pos['x'] + pos['width'], pos['y'] + pos['height']
            base = self._sample_zone_ground(x0, y0, x1, y1)

            fig.add_trace(self._box_mesh(
                x0, y0, base + 0.10, x1, y1, base + 0.95,
                color=self.ZONE_COLORS.get(zone_id, '#CCCCCC'),
                name=self.ZONE_NAMES.get(zone_id, zone_id),
                opacity=0.34,
                show_legend=True,
                hover_text=(
                    f"{self.ZONE_NAMES.get(zone_id, zone_id)}<br>"
                    f"Area: {pos['width'] * pos['height']:.0f} sq.ft.<extra></extra>"
                ),
            ))

            # Click-highlight support on zone centroids.
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            cz = self._terrain_height(cx, cy) + 1.2
            fig.add_trace(go.Scatter3d(
                x=[cx], y=[cy], z=[cz],
                mode='markers',
                marker=dict(size=7, color=self.ZONE_COLORS.get(zone_id, '#CCCCCC'), opacity=0.15),
                selected=dict(marker=dict(size=12, color='#F5F7FA', opacity=0.95)),
                unselected=dict(marker=dict(opacity=0.15)),
                name=f"{self.ZONE_NAMES.get(zone_id, zone_id)} Selector",
                showlegend=False,
                hovertemplate=f"{self.ZONE_NAMES.get(zone_id, zone_id)}<extra></extra>",
            ))

            self._add_shadow_rect(fig, x0, y0, x1, y1, base + 0.05, alpha=0.12)

    def _add_house_3d(self, fig, layout):
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        pos = layout.get('house_position', 'Center')
        positions = {
            'North': (L * 0.3, W * 0.82, L * 0.4, W * 0.12),
            'South': (L * 0.3, W * 0.06, L * 0.4, W * 0.12),
            'East': (L * 0.75, W * 0.35, L * 0.2, W * 0.3),
            'West': (L * 0.05, W * 0.35, L * 0.2, W * 0.3),
            'Center': (L * 0.35, W * 0.4, L * 0.3, W * 0.2),
        }
        hx, hy, hw, hd = positions.get(pos, positions['Center'])
        base = self._sample_zone_ground(hx, hy, hx + hw, hy + hd)
        wall_top = base + 10.8 + (hw / max(L, 1)) * 1.2

        fig.add_trace(self._box_mesh(
            hx, hy, base + 0.1, hx + hw, hy + hd, wall_top,
            color='#A58E7A',
            name='House',
            hover_text='House footprint<extra></extra>',
        ))
        fig.add_trace(self._hip_roof(hx, hy, hx + hw, hy + hd, wall_top, wall_top + 6.4, color='#5E4638'))
        self._add_shadow_rect(fig, hx, hy, hx + hw, hy + hd, base + 0.08, alpha=0.18)

    def _add_features_3d(self, fig, layout):
        features = layout.get('features', {})

        if 'pond' in features:
            f = features['pond']
            r = f['radius']
            cx, cy = f['x'], f['y']
            cz = self._terrain_height(cx, cy)
            rg, tg = np.linspace(0, r, 12), np.linspace(0, 2 * np.pi, 40)
            R, T = np.meshgrid(rg, tg)
            ripple = np.sin(T * 3.0) * 0.05
            Z = (cz - 0.55) - (R / (r + 1e-6)) * 0.55 + ripple
            fig.add_trace(go.Surface(
                x=cx + R * np.cos(T),
                y=cy + R * np.sin(T),
                z=Z,
                colorscale=[[0, '#0D47A1'], [0.45, '#1E88E5'], [1, '#90CAF9']],
                showscale=False,
                name='Pond',
                showlegend=True,
                opacity=0.92,
                hovertemplate='Pond<extra></extra>',
            ))

        if 'well' in features:
            f = features['well']
            rw = f.get('radius', 4)
            cx, cy = f['x'], f['y']
            base = self._terrain_height(cx, cy)
            t_w, z_w = np.linspace(0, 2 * np.pi, 24), np.array([base + 0.2, base + 5.5])
            Tw, Zw = np.meshgrid(t_w, z_w)
            fig.add_trace(go.Surface(
                x=cx + rw * np.cos(Tw),
                y=cy + rw * np.sin(Tw),
                z=Zw,
                colorscale=[[0, '#546E7A'], [1, '#90A4AE']],
                showscale=False,
                name='Borewell',
                hovertemplate='Borewell<extra></extra>',
            ))

    def _add_all_livestock_3d(self, fig, layout):
        features = layout.get('features', {})
        livestock_config = {
            'goat_shed': ('#E8B7A2', '#5B3A2B', 'Goat Shed', 7.0),
            'chicken_coop': ('#EFE4A7', '#8A6A17', 'Chicken Coop', 5.0),
            'piggery': ('#E6AFC4', '#6B334E', 'Piggery', 6.0),
            'cow_shed': ('#C6B9AD', '#5B4A3A', 'Cow Shed', 9.0),
            'fish_tanks': ('#A2D8F2', '#1B75BB', 'Fish Tanks', 3.0),
            'bee_hives': ('#F0D764', '#B8870C', 'Bee Hives', 4.0),
        }
        for key, (wc, rc, lbl, sh) in livestock_config.items():
            if key not in features:
                continue
            f = features[key]
            x0, y0 = f['x'], f['y']
            x1, y1 = f['x'] + f['width'], f['y'] + f['height']
            base = self._sample_zone_ground(x0, y0, x1, y1)
            rb = base + sh
            rt = rb + f['width'] * 0.22

            fig.add_trace(self._box_mesh(
                x0, y0, base + 0.15, x1, y1, rb,
                wc, lbl,
                hover_text=f"{lbl}<extra></extra>"
            ))
            fig.add_trace(self._hip_roof(x0, y0, x1, y1, rb, rt, rc))
            self._add_shadow_rect(fig, x0, y0, x1, y1, base + 0.08, alpha=0.14)

    def _add_trees_3d(self, fig, layout):
        zone_pos = layout.get('zone_positions', {})
        if 'z2' not in zone_pos:
            return

        z = zone_pos['z2']
        rng = np.random.default_rng(42)
        cluster_centers = [(0.22, 0.28), (0.64, 0.52), (0.40, 0.74)]
        colors = ['#2E7D32', '#3B8A3E', '#1F5F28', '#4A9650']
        first = True

        for cx_rel, cy_rel in cluster_centers:
            cx = z['x'] + cx_rel * z['width']
            cy = z['y'] + cy_rel * z['height']
            for _ in range(5):
                tx = cx + rng.normal(0, z['width'] * 0.07)
                ty = cy + rng.normal(0, z['height'] * 0.07)
                tx = float(np.clip(tx, z['x'] + 6, z['x'] + z['width'] - 6))
                ty = float(np.clip(ty, z['y'] + 6, z['y'] + z['height'] - 6))
                ground = self._terrain_height(tx, ty)

                size = float(rng.uniform(0.85, 1.28))
                tree_color = colors[int(rng.integers(0, len(colors)))]
                tree_traces = self._cone_tree(
                    tx,
                    ty,
                    trunk_bot_z=ground + 0.3,
                    trunk_top_z=ground + (6.2 * size),
                    canopy_bot_z=ground + (6.0 * size),
                    canopy_top_z=ground + (15.0 * size),
                    canopy_r=6.6 * size,
                    trunk_r=1.05 * size,
                    color_canopy=tree_color,
                    label='Tree',
                    show_legend=first,
                )
                first = False
                for trace in tree_traces:
                    fig.add_trace(trace)

    def _add_paths_3d(self, fig, layout):
        """Curved service paths that follow terrain elevation."""
        zones = layout.get('zone_positions', {})
        if not zones:
            return

        z0 = zones.get('z0')
        z1 = zones.get('z1')
        if not z0 or not z1:
            return

        sx = z0['x'] + z0['width'] * 0.50
        sy = z0['y']
        ex = z1['x'] + z1['width'] * 0.50
        ey = z1['y'] + z1['height'] * 0.5

        t = np.linspace(0, 1, 48)
        px = sx + (ex - sx) * t + np.sin(t * np.pi) * (layout['dimensions']['L'] * 0.03)
        py = sy + (ey - sy) * t
        pz = np.array([self._terrain_height(x, y) + 0.28 for x, y in zip(px, py)])

        fig.add_trace(go.Scatter3d(
            x=px,
            y=py,
            z=pz,
            mode='lines',
            line=dict(color='#D9C9AC', width=9),
            opacity=0.84,
            name='Main Path',
            hovertemplate='Main Path<extra></extra>',
        ))

        fig.add_trace(go.Scatter3d(
            x=px,
            y=py,
            z=pz + 0.04,
            mode='lines',
            line=dict(color='#BFA988', width=3),
            opacity=0.6,
            showlegend=False,
            hoverinfo='skip',
        ))
