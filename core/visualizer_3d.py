"""
3D Visualization Engine — Fixed & Professional
Homestead Architect Pro 2026
Global Edition
"""

import plotly.graph_objects as go
import numpy as np
from typing import Dict, Any, Tuple, List


class Visualizer3D:
    """Creates interactive 3D homestead models using Plotly"""

    # ── Zone styling ────────────────────────────────────────────────────────
    ZONE_COLORS = {
        "z0": "#F5F5DC",   # Residential – beige
        "z1": "#90EE90",   # Kitchen Garden – light green
        "z2": "#228B22",   # Food Forest – dark green
        "z3": "#F0E68C",   # Pasture/Crops – khaki
        "z4": "#DDA0DD",   # Buffer Zone – plum
    }
    ZONE_NAMES = {
        "z0": "Zone 0 – Residential",
        "z1": "Zone 1 – Kitchen Garden",
        "z2": "Zone 2 – Food Forest",
        "z3": "Zone 3 – Pasture / Crops",
        "z4": "Zone 4 – Buffer Zone",
    }

    # ── Public API ───────────────────────────────────────────────────────────
    def create(self, layout: Dict[str, Any]) -> go.Figure:
        """Generate fully interactive 3D scene from layout dict."""
        fig = go.Figure()

        self._add_terrain(fig, layout)
        self._add_zones_3d(fig, layout)
        self._add_house_3d(fig, layout)
        self._add_features_3d(fig, layout)
        self._add_trees_3d(fig, layout)
        self._add_livestock_housing_3d(fig, layout)

        L = layout["dimensions"]["L"]
        W = layout["dimensions"]["W"]
        acres = layout.get("acres", round(L * W / 43560, 2))

        fig.update_layout(
            title=dict(
                text=f"🏡 3D Homestead View — {acres:.2f} acres "
                     f"({int(L)} × {int(W)} ft)",
                font=dict(size=17, color="#2E7D32", family="Arial"),
                x=0.5,
            ),
            scene=dict(
                xaxis_title="Length (ft)",
                yaxis_title="Width (ft)",
                zaxis_title="Height (ft)",
                aspectmode="data",
                bgcolor="#D0E8F5",           # sky colour
                camera=dict(
                    eye=dict(x=1.4, y=-1.4, z=0.9),
                    up=dict(x=0, y=0, z=1),
                ),
                xaxis=dict(showgrid=True, gridcolor="#BBBBBB"),
                yaxis=dict(showgrid=True, gridcolor="#BBBBBB"),
                zaxis=dict(showgrid=True, gridcolor="#BBBBBB"),
            ),
            legend=dict(
                x=0.01, y=0.99,
                bgcolor="rgba(255,255,255,0.85)",
                bordercolor="#AAAAAA",
                borderwidth=1,
                font=dict(size=11),
            ),
            paper_bgcolor="#EAF4FB",
            margin=dict(l=0, r=0, t=55, b=0),
            width=950,
            height=670,
        )
        return fig

    # ── Private helpers: geometry primitives ────────────────────────────────

    @staticmethod
    def _box_mesh(
        x0: float, y0: float, z0: float,
        x1: float, y1: float, z1: float,
        color: str,
        name: str,
        opacity: float = 0.85,
        show_legend: bool = True,
    ) -> go.Mesh3d:
        """
        Correct 3D axis-aligned box using explicit face (i,j,k) indices.
        Without i/j/k, Plotly's alphahull can fail or look wrong.

        Vertex layout (index):
          Bottom face:  0(x0,y0,z0)  1(x1,y0,z0)  2(x1,y1,z0)  3(x0,y1,z0)
          Top face:     4(x0,y0,z1)  5(x1,y0,z1)  6(x1,y1,z1)  7(x0,y1,z1)
        """
        vx = [x0, x1, x1, x0,  x0, x1, x1, x0]
        vy = [y0, y0, y1, y1,  y0, y0, y1, y1]
        vz = [z0, z0, z0, z0,  z1, z1, z1, z1]

        # 12 triangles = 6 faces × 2
        fi = [0, 0,   4, 4,   0, 0,   2, 2,   0, 0,   1, 1]
        fj = [1, 2,   5, 6,   1, 5,   3, 7,   3, 7,   2, 6]
        fk = [2, 3,   6, 7,   5, 4,   7, 6,   7, 4,   6, 5]

        return go.Mesh3d(
            x=vx, y=vy, z=vz,
            i=fi, j=fj, k=fk,
            color=color,
            opacity=opacity,
            name=name,
            showlegend=show_legend,
            flatshading=True,
            lighting=dict(ambient=0.65, diffuse=0.9, specular=0.2,
                          roughness=0.6, fresnel=0.1),
        )

    @staticmethod
    def _hip_roof(
        x0: float, y0: float,
        x1: float, y1: float,
        base_z: float,
        apex_z: float,
        color: str,
        name: str = "Roof",
    ) -> go.Mesh3d:
        """Hip roof (pyramid) — 4 triangular faces meeting at apex."""
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        # 4 base corners + apex
        vx = [x0, x1, x1, x0, cx]
        vy = [y0, y0, y1, y1, cy]
        vz = [base_z] * 4 + [apex_z]
        # 4 triangular side faces; no bottom (walls cover it)
        fi = [0, 1, 2, 3]
        fj = [1, 2, 3, 0]
        fk = [4, 4, 4, 4]
        return go.Mesh3d(
            x=vx, y=vy, z=vz,
            i=fi, j=fj, k=fk,
            color=color,
            opacity=0.97,
            name=name,
            showlegend=False,
            flatshading=True,
        )

    @staticmethod
    def _cone_tree(
        tx: float, ty: float,
        trunk_bot_z: float = 1.5,
        trunk_top_z: float = 7.0,
        canopy_bot_z: float = 7.0,
        canopy_top_z: float = 18.0,
        canopy_r: float = 7.5,
        trunk_r: float = 1.2,
        color_canopy: str = "#2E7D32",
        label: str = "",
        show_legend: bool = False,
    ) -> List[go.BaseTraceType]:
        """Stylised tree: cylinder trunk + cone canopy."""
        traces = []
        n = 18  # polygon resolution

        # ── Trunk (cylinder as Surface) ──────────────────────────────────
        theta_t = np.linspace(0, 2 * np.pi, n)
        z_t = np.array([trunk_bot_z, trunk_top_z])
        T_grid, Z_grid = np.meshgrid(theta_t, z_t)
        Xt = tx + trunk_r * np.cos(T_grid)
        Yt = ty + trunk_r * np.sin(T_grid)
        traces.append(go.Surface(
            x=Xt, y=Yt, z=Z_grid,
            colorscale=[[0, "#6D4C41"], [1, "#8D6E63"]],
            showscale=False,
            showlegend=False,
            opacity=0.95,
            name="Tree Trunk",
        ))

        # ── Canopy (cone with Mesh3d) ────────────────────────────────────
        theta_c = np.linspace(0, 2 * np.pi, n, endpoint=False)
        vx = list(tx + canopy_r * np.cos(theta_c)) + [tx]
        vy = list(ty + canopy_r * np.sin(theta_c)) + [ty]
        vz = [canopy_bot_z] * n + [canopy_top_z]
        apex = n
        fi = list(range(n))
        fj = [(k + 1) % n for k in range(n)]
        fk = [apex] * n
        traces.append(go.Mesh3d(
            x=vx, y=vy, z=vz,
            i=fi, j=fj, k=fk,
            color=color_canopy,
            opacity=0.88,
            name=label if label else "Tree",
            showlegend=show_legend,
            flatshading=True,
        ))
        return traces

    # ── Scene layers ─────────────────────────────────────────────────────────

    def _add_terrain(self, fig: go.Figure, layout: Dict[str, Any]):
        L = layout["dimensions"]["L"]
        W = layout["dimensions"]["W"]

        x = np.linspace(0, L, 30)
        y = np.linspace(0, W, 30)
        X, Y = np.meshgrid(x, y)

        slope = layout.get("slope", "Flat")
        Z = np.zeros_like(X)
        if slope == "South":   Z = Y * 0.03
        elif slope == "North": Z = (W - Y) * 0.03
        elif slope == "East":  Z = X * 0.03
        elif slope == "West":  Z = (L - X) * 0.03

        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z,
            colorscale=[[0, "#81C784"], [0.5, "#4CAF50"], [1, "#2E7D32"]],
            showscale=False,
            opacity=0.82,
            name="Terrain",
            showlegend=True,
            lighting=dict(ambient=0.7, diffuse=0.85),
        ))

    def _add_zones_3d(self, fig: go.Figure, layout: Dict[str, Any]):
        """Thin coloured slabs showing permaculture zones."""
        zone_height = 1.5

        for zone_id, pos in layout.get("zone_positions", {}).items():
            color = self.ZONE_COLORS.get(zone_id, "#CCCCCC")
            name = self.ZONE_NAMES.get(zone_id, zone_id)
            fig.add_trace(self._box_mesh(
                pos["x"], pos["y"], 0,
                pos["x"] + pos["width"], pos["y"] + pos["height"], zone_height,
                color=color, name=name, opacity=0.40,
            ))

    def _add_house_3d(self, fig: go.Figure, layout: Dict[str, Any]):
        """Realistic house: walls + hip roof."""
        L = layout["dimensions"]["L"]
        W = layout["dimensions"]["W"]
        pos = layout.get("house_position", "Center")

        positions = {
            "North":  (L*0.30, W*0.82, L*0.40, W*0.12),
            "South":  (L*0.30, W*0.06, L*0.40, W*0.12),
            "East":   (L*0.75, W*0.35, L*0.20, W*0.30),
            "West":   (L*0.05, W*0.35, L*0.20, W*0.30),
            "Center": (L*0.35, W*0.40, L*0.30, W*0.20),
        }
        hx, hy, hw, hd = positions.get(pos, positions["Center"])

        wall_h   = 10.0
        base_z   = 1.5
        roof_bot = base_z + wall_h
        roof_top = roof_bot + min(hw, hd) * 0.42

        # Walls
        fig.add_trace(self._box_mesh(
            hx, hy, base_z,
            hx + hw, hy + hd, roof_bot,
            color="#8D6E63", name="House", opacity=0.96,
        ))
        # Hip roof
        fig.add_trace(self._hip_roof(
            hx, hy, hx + hw, hy + hd,
            base_z=roof_bot, apex_z=roof_top,
            color="#4E342E",
        ))

    def _add_features_3d(self, fig: go.Figure, layout: Dict[str, Any]):
        """Pond, borewell, solar panels, greenhouse."""
        features = layout.get("features", {})

        # ── Pond ─────────────────────────────────────────────────────────
        if "pond" in features:
            f = features["pond"]
            r = f["radius"]

            # Pond floor (depressed Surface disc)
            rg = np.linspace(0, r, 10)
            tg = np.linspace(0, 2 * np.pi, 36)
            R, T = np.meshgrid(rg, tg)
            Xp = f["x"] + R * np.cos(T) * (1 + 0.1 * np.sin(3 * T))
            Yp = f["y"] + R * np.sin(T) * (1 + 0.1 * np.cos(2 * T))
            Zp = np.full_like(Xp, -0.8)
            fig.add_trace(go.Surface(
                x=Xp, y=Yp, z=Zp,
                colorscale=[[0, "#4FC3F7"], [1, "#0288D1"]],
                showscale=False, opacity=0.85,
                name="Pond", showlegend=True,
            ))

        # ── Borewell / Well ───────────────────────────────────────────────
        if "well" in features:
            f = features["well"]
            rw = f.get("radius", 4)
            theta_w = np.linspace(0, 2 * np.pi, 24)
            z_w = np.array([1.5, 5.0])
            Tw, Zw = np.meshgrid(theta_w, z_w)
            fig.add_trace(go.Surface(
                x=f["x"] + rw * np.cos(Tw),
                y=f["y"] + rw * np.sin(Tw),
                z=Zw,
                colorscale=[[0, "#546E7A"], [1, "#90A4AE"]],
                showscale=False, opacity=0.95,
                name="Borewell", showlegend=True,
            ))

        # ── Solar panels ──────────────────────────────────────────────────
        if "solar" in features:
            f = features["solar"]
            pw, ph = f["width"] / 3, f["height"] / 2
            for col in range(3):
                for row in range(2):
                    px = f["x"] + col * pw + 1
                    py = f["y"] + row * ph + 1
                    fig.add_trace(self._box_mesh(
                        px, py, 4.0,
                        px + pw - 2, py + ph - 2, 4.4,
                        color="#1565C0",
                        name="Solar Panels" if (col == 0 and row == 0) else "",
                        opacity=0.95,
                        show_legend=(col == 0 and row == 0),
                    ))

        # ── Greenhouse ────────────────────────────────────────────────────
        if "greenhouse" in features:
            f = features["greenhouse"]
            gh_h = 8.0
            base_z = 1.5
            # Glass walls (semi-transparent)
            fig.add_trace(self._box_mesh(
                f["x"], f["y"], base_z,
                f["x"] + f["width"], f["y"] + f["height"], base_z + gh_h,
                color="#E0F2F1", name="Greenhouse", opacity=0.35,
            ))
            # Ridge roof
            fig.add_trace(self._hip_roof(
                f["x"], f["y"],
                f["x"] + f["width"], f["y"] + f["height"],
                base_z=base_z + gh_h,
                apex_z=base_z + gh_h + f["width"] * 0.28,
                color="#80CBC4", name="GH Roof",
            ))

    def _add_trees_3d(self, fig: go.Figure, layout: Dict[str, Any]):
        """Stylised 3D trees in the Food Forest zone."""
        zone_pos = layout.get("zone_positions", {})
        if "z2" not in zone_pos:
            return

        z = zone_pos["z2"]
        rel_pos = [
            (0.18, 0.30), (0.48, 0.58), (0.78, 0.38),
            (0.28, 0.72), (0.68, 0.20), (0.58, 0.82),
        ]
        canopy_colors = [
            "#2E7D32", "#388E3C", "#1B5E20",
            "#43A047", "#66BB6A", "#33691E",
        ]
        tree_labels = ["Mango", "Coconut", "Jackfruit",
                       "Banana", "Guava", "Papaya"]

        for idx, (rx, ry) in enumerate(rel_pos):
            tx = z["x"] + rx * z["width"]
            ty = z["y"] + ry * z["height"]
            for trace in self._cone_tree(
                tx, ty,
                color_canopy=canopy_colors[idx % len(canopy_colors)],
                label=tree_labels[idx % len(tree_labels)],
                show_legend=(idx == 0),
            ):
                fig.add_trace(trace)

    def _add_livestock_housing_3d(self, fig: go.Figure, layout: Dict[str, Any]):
        """Simple shed for livestock if present in layout."""
        features = layout.get("features", {})
        if "livestock" not in features:
            return

        f = features["livestock"]
        shed_h = 8.0
        base_z = 1.5

        fig.add_trace(self._box_mesh(
            f["x"], f["y"], base_z,
            f["x"] + f["width"], f["y"] + f["height"], base_z + shed_h,
            color="#DEB887", name="Livestock Shed", opacity=0.90,
        ))
        fig.add_trace(self._hip_roof(
            f["x"], f["y"],
            f["x"] + f["width"], f["y"] + f["height"],
            base_z=base_z + shed_h,
            apex_z=base_z + shed_h + f["width"] * 0.25,
            color="#A0522D", name="Shed Roof",
        ))
