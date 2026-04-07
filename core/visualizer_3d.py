"""
Homestead Architect Pro 2026 — ULTRA EDITION v3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KEY FIX: 3D map ab 2D map ke SAME zone_positions aur features use karta hai.
Dono map bilkul same layout dikhate hain.

Features:
  ✅ 2D ke same zone_positions → 3D me same jagah
  ✅ 2D ke same features (livestock, pond, well) → 3D me same
  ✅ 2D jaisi house placement (same _house_bbox logic)
  ✅ Realistic grass terrain with slope + noise
  ✅ Realistic house: walls, hip roof, windows, door, porch, chimney
  ✅ Kitchen Garden: raised beds + plants (Zone 1 se)
  ✅ Food Forest: user tree_count trees (Zone 2 se)
  ✅ Livestock sheds: SIRF wahi jo layout['features'] me hai
  ✅ Water features: pond / borewell / rain_tank
  ✅ Info box hide/show toggle
  ✅ HTML download
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from typing import Dict, Any, List
import math


class Visualizer3D:

    # Same colors as Visualizer2D
    ZONE_COLORS = {
        'z0': '#F0EAD6',
        'z1': '#C5E1A5',
        'z2': '#388E3C',
        'z3': '#FFF9C4',
        'z4': '#A5D6A7',
    }
    ZONE_NAMES = {
        'z0': 'Zone 0 – Residential',
        'z1': 'Zone 1 – Kitchen Garden',
        'z2': 'Zone 2 – Food Forest',
        'z3': 'Zone 3 – Pasture / Crops',
        'z4': 'Zone 4 – Buffer Zone',
    }

    # Livestock feature_key → (wall_color, roof_color, label, height_ft, emoji)
    LIVESTOCK_CFG = {
        'chicken_coop': ('#FFF8E1', '#F57F17', 'Chicken Coop',  5.0, 'Chicken Coop'),
        'goat_shed':    ('#FFCCBC', '#5D4037', 'Goat Shed',     8.0, 'Goat Shed'),
        'piggery':      ('#FFCCBC', '#BF360C', 'Piggery',       7.0, 'Piggery'),
        'cow_shed':     ('#D7CCC8', '#5D4037', 'Cow Shed',     10.0, 'Cow Shed'),
        'fish_tanks':   ('#B3E5FC', '#0288D1', 'Fish Tanks',    3.0, 'Fish Tanks'),
        'bee_hives':    ('#FFF176', '#F9A825', 'Bee Hives',     4.0, 'Bee Hives'),
    }

    # ══════════════════════════════════════════════════════
    #  MAIN ENTRY POINT
    # ══════════════════════════════════════════════════════

    def create(self, layout: Dict[str, Any]):
        if not layout or 'dimensions' not in layout:
            st.info("pehle 'Design' tab mein apna naksha generate karein.")
            return

        dims = layout['dimensions']
        L = float(dims.get('L', dims.get('length', 300)))
        W = float(dims.get('W', dims.get('width', 300)))
        if L <= 0: L = 300.0
        if W <= 0: W = 300.0

        scale = max(L, W) / 300.0

        fig = go.Figure()

        self._terrain(fig, layout, L, W, scale)
        self._zones(fig, layout, L, W, scale)
        self._paths(fig, layout, L, W, scale)
        self._water_features(fig, layout, L, W, scale)
        self._house(fig, layout, L, W, scale)
        self._kitchen_garden(fig, layout, L, W, scale)
        self._livestock(fig, layout, L, W, scale)
        self._food_forest(fig, layout, L, W, scale)
        self._utilities(fig, layout, L, W, scale)
        self._labels(fig, layout, L, W, scale)

        acres     = layout.get('acres', round(L * W / 43560, 2))
        loc_name  = layout.get('location', 'Custom Plot')
        tree_count = self._get_tree_count(layout)
        title_text = f"Homestead: {loc_name} | {acres:.2f} acres ({int(L)}x{int(W)} ft)"

        fig.update_layout(
            title=dict(
                text=title_text,
                font=dict(size=15, color='#1B5E20', family='Arial Black'),
                x=0.5,
            ),
            updatemenus=[dict(
                type="buttons", direction="left",
                x=0.01, y=1.09,
                showactive=True,
                bgcolor='rgba(255,255,255,0.92)',
                bordercolor='#2E7D32',
                font=dict(size=12),
                buttons=[
                    dict(label="Info Dikhao",
                         method="relayout",
                         args=[{"title.text": title_text, "showlegend": True}]),
                    dict(label="Full Map",
                         method="relayout",
                         args=[{"title.text": "", "showlegend": False}]),
                ]
            )],
            scene=dict(
                xaxis=dict(title='Length (ft)', showgrid=True,
                           gridcolor='rgba(0,0,0,0.08)', zeroline=False),
                yaxis=dict(title='Width (ft)', showgrid=True,
                           gridcolor='rgba(0,0,0,0.08)', zeroline=False),
                zaxis=dict(title='Height (ft)', showgrid=False,
                           range=[-2, max(L, W) * 0.16]),
                aspectmode='manual',
                aspectratio=dict(x=1.0, y=W / L, z=0.22),
                bgcolor='#B2DFDB',
                camera=dict(
                    eye=dict(x=1.55, y=-1.55, z=1.05),
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=0, y=0, z=-0.08),
                ),
            ),
            legend=dict(
                x=0.01, y=0.97,
                bgcolor='rgba(255,255,255,0.90)',
                bordercolor='#ccc', borderwidth=1,
                font=dict(size=10),
                tracegroupgap=1,
            ),
            paper_bgcolor='#E8F5E9',
            margin=dict(l=0, r=0, t=68, b=0),
            height=730,
        )

        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns([3, 1])
        with col1:
            try:
                html_str = fig.to_html(include_plotlyjs='cdn', full_html=True)
                st.download_button(
                    label="3D Map Download (HTML - Offline bhi chalega)",
                    data=html_str,
                    file_name=f"homestead_3d_{loc_name.replace(' ','_').replace(',','')}.html",
                    mime="text/html",
                    use_container_width=True,
                )
            except Exception:
                pass
        with col2:
            st.info(f"{tree_count} Trees")

    # ══════════════════════════════════════════════════════
    #  HELPERS
    # ══════════════════════════════════════════════════════

    def _get_tree_count(self, layout) -> int:
        tc = layout.get('tree_count', 15)
        try:
            tc = int(tc)
        except Exception:
            tc = 15
        return max(3, min(60, tc))

    def _house_bbox(self, layout, L, W):
        """
        EXACT mirror of Visualizer2D._house_bbox.
        Returns (hx, hy, hw, hh).
        """
        zone_positions = layout.get('zone_positions', {})
        z0 = zone_positions.get('z0', {'x': 0, 'y': 0, 'width': L, 'height': W})

        MIN_HW = max(L * 0.08, 40.0)
        MIN_HH = max(W * 0.03, 30.0)
        hw = max(z0['width'] * 0.55, MIN_HW)
        hh = max(z0['height'] * 0.65, MIN_HH)
        hw = min(hw, z0['width'] * 0.85)
        hh = min(hh, z0['height'] * 0.90)
        hx = z0['x'] + (z0['width'] - hw) / 2
        hy = z0['y'] + (z0['height'] - hh) / 2
        return hx, hy, hw, hh

    def _slope_z(self, x, y, layout, L, W, scale) -> float:
        slope = layout.get('slope', 'Flat')
        sf = max(L, W) * 0.018 * scale
        if slope == 'South':   return y / W * sf
        if slope == 'North':   return (1 - y / W) * sf
        if slope == 'East':    return x / L * sf
        if slope == 'West':    return (1 - x / L) * sf
        if slope == 'Mixed/Undulating':
            return (math.sin(x / L * math.pi) * 0.5 + math.cos(y / W * math.pi) * 0.3) * sf
        return 0.0

    # ══════════════════════════════════════════════════════
    #  TERRAIN
    # ══════════════════════════════════════════════════════

    def _terrain(self, fig, layout, L, W, scale):
        nx, ny = 48, 48
        x = np.linspace(0, L, nx)
        y = np.linspace(0, W, ny)
        X, Y = np.meshgrid(x, y)

        slope = layout.get('slope', 'Flat')
        sf = max(L, W) * 0.018 * scale
        Z = np.zeros_like(X, dtype=float)

        if slope == 'South':            Z = Y / W * sf
        elif slope == 'North':          Z = (1 - Y / W) * sf
        elif slope == 'East':           Z = X / L * sf
        elif slope == 'West':           Z = (1 - X / L) * sf
        elif slope == 'Mixed/Undulating':
            Z = (np.sin(X / L * np.pi) * 0.5 + np.cos(Y / W * np.pi) * 0.3) * sf

        # Smooth random noise for natural terrain
        np.random.seed(42)
        noise_raw = np.random.normal(0, sf * 0.04, X.shape)
        # Simple box blur
        padded = np.pad(noise_raw, 1, mode='edge')
        noise = np.zeros_like(noise_raw)
        for i in range(noise.shape[0]):
            for j in range(noise.shape[1]):
                noise[i, j] = padded[i:i+3, j:j+3].mean()
        Z += noise

        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z,
            colorscale=[
                [0.00, '#33691E'],
                [0.25, '#558B2F'],
                [0.55, '#689F38'],
                [0.80, '#7CB342'],
                [1.00, '#9CCC65'],
            ],
            showscale=False,
            opacity=1.0,
            name='Terrain (Grass)',
            showlegend=True,
            lighting=dict(ambient=0.72, diffuse=0.88, specular=0.08),
            hovertemplate='Terrain | Elevation: %{z:.1f} ft<extra></extra>',
        ))

        # Plot boundary
        bz0 = self._slope_z(0, 0, layout, L, W, scale) + 0.3
        fig.add_trace(go.Scatter3d(
            x=[0, L, L, 0, 0], y=[0, 0, W, W, 0], z=[bz0] * 5,
            mode='lines',
            line=dict(color='#1B5E20', width=4),
            name='Plot Boundary',
            showlegend=True,
            hoverinfo='skip',
        ))

    # ══════════════════════════════════════════════════════
    #  ZONES (from layout['zone_positions'])
    # ══════════════════════════════════════════════════════

    def _zones(self, fig, layout, L, W, scale):
        for zid, pos in layout.get('zone_positions', {}).items():
            x0, y0 = pos['x'], pos['y']
            x1 = x0 + pos['width']
            y1 = y0 + pos['height']
            col  = self.ZONE_COLORS.get(zid, '#CCCCCC')
            name = self.ZONE_NAMES.get(zid, zid)

            xg = np.linspace(x0, x1, 10)
            yg = np.linspace(y0, y1, 10)
            XG, YG = np.meshgrid(xg, yg)
            ZG = np.vectorize(
                lambda xi, yi: self._slope_z(xi, yi, layout, L, W, scale) + 0.38
            )(XG, YG)

            fig.add_trace(go.Surface(
                x=XG, y=YG, z=ZG,
                colorscale=[[0, col], [1, col]],
                showscale=False, opacity=0.40,
                name=name, showlegend=True,
                hovertemplate=f'{name}<extra></extra>',
            ))

            cx = [x0, x1, x1, x0, x0]
            cy = [y0, y0, y1, y1, y0]
            cz = [self._slope_z(xi, yi, layout, L, W, scale) + 0.55
                  for xi, yi in zip(cx, cy)]
            fig.add_trace(go.Scatter3d(
                x=cx, y=cy, z=cz, mode='lines',
                line=dict(color=col, width=2),
                showlegend=False, hoverinfo='skip',
            ))

    # ══════════════════════════════════════════════════════
    #  PATHS
    # ══════════════════════════════════════════════════════

    def _paths(self, fig, layout, L, W, scale):
        hx, hy, hw, hh = self._house_bbox(layout, L, W)
        door_cx = hx + hw / 2

        n_pts = 14
        path_x, path_y, path_z = [], [], []
        for i in range(n_pts):
            t = i / (n_pts - 1)
            px = door_cx + math.sin(t * math.pi) * L * 0.022 * (1 - t)
            py = t * hy
            pz = self._slope_z(px, py, layout, L, W, scale) + 0.7
            path_x.append(px); path_y.append(py); path_z.append(pz)

        fig.add_trace(go.Scatter3d(
            x=path_x, y=path_y, z=path_z,
            mode='lines', line=dict(color='#D2B48C', width=10),
            name='Gravel Path', showlegend=True, hoverinfo='skip',
        ))

        # Farm road to z3
        z3 = layout.get('zone_positions', {}).get('z3')
        if z3:
            farm_x = hx + hw * 0.75
            z3_cx = z3['x'] + z3['width'] * 0.4
            z3_cy = z3['y']
            farm_pts = [
                (farm_x, hy + hh),
                ((farm_x + z3_cx) / 2 + L * 0.02, (hy + hh + z3_cy) / 2),
                (z3_cx, z3_cy),
            ]
            fig.add_trace(go.Scatter3d(
                x=[p[0] for p in farm_pts],
                y=[p[1] for p in farm_pts],
                z=[self._slope_z(p[0], p[1], layout, L, W, scale) + 0.7 for p in farm_pts],
                mode='lines', line=dict(color='#BCAAA4', width=7, dash='dot'),
                showlegend=False, hoverinfo='skip',
            ))

    # ══════════════════════════════════════════════════════
    #  WATER FEATURES (from layout['features'])
    # ══════════════════════════════════════════════════════

    def _water_features(self, fig, layout, L, W, scale):
        features = layout.get('features', {})

        for key in ('borewell', 'well'):
            if key not in features:
                continue
            f = features[key]
            if not f:
                continue
            wx, wy = f['x'], f['y']
            r = max(3.0, f.get('radius', min(L, W) * 0.022))
            wz_base = self._slope_z(wx, wy, layout, L, W, scale) + 1.5
            wall_h  = r * 2.2 * scale

            theta = np.linspace(0, 2 * math.pi, 32)
            zz    = np.array([wz_base, wz_base + wall_h])
            TH, ZZ = np.meshgrid(theta, zz)
            fig.add_trace(go.Surface(
                x=wx + r * np.cos(TH), y=wy + r * np.sin(TH), z=ZZ,
                colorscale=[[0, '#546E7A'], [1, '#90A4AE']],
                showscale=False, name='Borewell/Well', showlegend=True, opacity=0.96,
            ))
            rg = np.linspace(0, r, 6)
            RG, TG = np.meshgrid(rg, theta)
            fig.add_trace(go.Surface(
                x=wx + RG * np.cos(TG), y=wy + RG * np.sin(TG),
                z=np.full_like(RG, wz_base + wall_h),
                colorscale=[[0, '#37474F'], [1, '#455A64']],
                showscale=False, showlegend=False, opacity=1.0,
            ))
            break

        if 'pond' in features and features['pond']:
            f = features['pond']
            px, py = f['x'], f['y']
            pr = max(6.0, f['radius'])
            pz_base = self._slope_z(px, py, layout, L, W, scale) - 0.8

            theta = np.linspace(0, 2 * math.pi, 40)
            rim_r = pr * (1 + 0.10 * np.sin(3 * theta) + 0.06 * np.cos(5 * theta))
            rg = np.linspace(0, 1, 14)
            RG2, TG2 = np.meshgrid(rg, theta)
            R_actual = RG2 * rim_r[:, np.newaxis]
            ZP = pz_base * (1 - RG2 ** 2) + self._slope_z(px, py, layout, L, W, scale) * RG2 ** 2

            fig.add_trace(go.Surface(
                x=px + R_actual * np.cos(TG2),
                y=py + R_actual * np.sin(TG2),
                z=ZP,
                colorscale=[
                    [0.0, '#01579B'], [0.35, '#0288D1'],
                    [0.7, '#4FC3F7'], [1.0, '#80DEEA'],
                ],
                showscale=False, name='Pond', showlegend=True, opacity=0.88,
            ))

        if 'rain_tank' in features and features['rain_tank']:
            f = features['rain_tank']
            rx, ry = f['x'], f['y']
            rw, rh2 = f['width'], f['height']
            gz_rt = self._slope_z(rx + rw / 2, ry + rh2 / 2, layout, L, W, scale) + 1.5
            tank_h = max(L, W) * 0.04 * scale
            fig.add_trace(self._box_mesh(
                rx, ry, gz_rt, rx + rw, ry + rh2, gz_rt + tank_h,
                '#B3E5FC', 'Rain Tank', opacity=0.90
            ))

    # ══════════════════════════════════════════════════════
    #  HOUSE (same position as 2D via _house_bbox)
    # ══════════════════════════════════════════════════════

    def _house(self, fig, layout, L, W, scale):
        hx, hy, hw, hh = self._house_bbox(layout, L, W)
        gz      = self._slope_z(hx + hw / 2, hy + hh / 2, layout, L, W, scale)
        found_t = gz + 1.5
        wall_h  = max(L, W) * 0.055 * scale
        wall_t  = found_t + wall_h
        apex    = wall_t + hw * 0.40 * scale

        # Foundation
        fig.add_trace(self._box_mesh(
            hx - 1.5, hy - 1.5, gz + 0.3,
            hx + hw + 1.5, hy + hh + 1.5, found_t,
            '#BDBDBD', 'House Foundation', opacity=0.95, show_legend=False
        ))

        # Main walls
        fig.add_trace(self._box_mesh(
            hx, hy, found_t, hx + hw, hy + hh, wall_t,
            '#8D6E63', 'Residence', opacity=0.95
        ))

        # Wall texture bands (front)
        for zb in np.linspace(found_t + wall_h * 0.2, wall_t - wall_h * 0.12, 4):
            fig.add_trace(go.Scatter3d(
                x=[hx, hx + hw], y=[hy, hy], z=[zb, zb],
                mode='lines', line=dict(color='#6D4C41', width=1),
                showlegend=False, hoverinfo='skip',
            ))

        # Hip Roof
        fig.add_trace(self._hip_roof(hx, hy, hx + hw, hy + hh, wall_t, apex, '#4E342E', 'House Roof'))
        # Ridge
        fig.add_trace(go.Scatter3d(
            x=[hx + hw / 2, hx + hw / 2],
            y=[hy + hh * 0.15, hy + hh * 0.85],
            z=[apex, apex],
            mode='lines', line=dict(color='#3E2723', width=3),
            showlegend=False, hoverinfo='skip',
        ))

        # Front Windows
        win_w = hw * 0.13
        win_h = wall_h * 0.28
        win_z0 = found_t + wall_h * 0.42
        for wfx in [hx + hw * 0.15, hx + hw * 0.58]:
            fig.add_trace(self._box_mesh(
                wfx, hy - 0.4, win_z0, wfx + win_w, hy, win_z0 + win_h,
                '#B3E5FC', 'Window', opacity=0.85, show_legend=False
            ))
            # Cross
            fig.add_trace(go.Scatter3d(
                x=[wfx, wfx + win_w, None, wfx + win_w / 2, wfx + win_w / 2],
                y=[hy - 0.1, hy - 0.1, None, hy - 0.1, hy - 0.1],
                z=[win_z0 + win_h / 2, win_z0 + win_h / 2, None, win_z0, win_z0 + win_h],
                mode='lines', line=dict(color='#1565C0', width=1),
                showlegend=False, hoverinfo='skip',
            ))

        # Side windows
        swin_z0 = found_t + wall_h * 0.40
        swin_h  = wall_h * 0.25
        swin_w  = hh * 0.14
        for swy in [hy + hh * 0.2, hy + hh * 0.65]:
            fig.add_trace(self._box_mesh(
                hx - 0.4, swy, swin_z0, hx, swy + swin_w, swin_z0 + swin_h,
                '#B3E5FC', 'Window', opacity=0.80, show_legend=False
            ))

        # Front Door
        door_w = hw * 0.14
        door_h = wall_h * 0.55
        door_x = hx + hw / 2 - door_w / 2
        fig.add_trace(self._box_mesh(
            door_x, hy - 0.5, found_t,
            door_x + door_w, hy, found_t + door_h,
            '#3E2723', 'Door', opacity=1.0, show_legend=False
        ))
        # Door arch
        arch_pts = 12
        arch_cx  = door_x + door_w / 2
        arch_r   = door_w / 2
        fig.add_trace(go.Scatter3d(
            x=[arch_cx + arch_r * math.cos(t) for t in np.linspace(0, math.pi, arch_pts)],
            y=[hy - 0.2] * arch_pts,
            z=[found_t + door_h + arch_r * math.sin(t) for t in np.linspace(0, math.pi, arch_pts)],
            mode='lines', line=dict(color='#3E2723', width=3),
            showlegend=False, hoverinfo='skip',
        ))

        # Porch / Deck
        porch_w = hw * 0.52
        porch_d = hh * 0.14
        px2, py2 = hx + (hw - porch_w) / 2, hy - porch_d
        porch_top = gz + 0.3 + (found_t - gz - 0.3) * 0.55
        fig.add_trace(self._box_mesh(
            px2, py2, gz + 0.3, px2 + porch_w, hy, porch_top,
            '#D7CCC8', 'Porch', opacity=0.88, show_legend=False
        ))
        for by_deck in np.linspace(py2 + 2, hy - 2, 5):
            fig.add_trace(go.Scatter3d(
                x=[px2 + 3, px2 + porch_w - 3],
                y=[by_deck, by_deck],
                z=[porch_top + 0.1] * 2,
                mode='lines', line=dict(color='#A1887F', width=2),
                showlegend=False, hoverinfo='skip',
            ))

        # Chimney
        cw = hw * 0.07; cd = hh * 0.07
        cx2 = hx + hw * 0.72; cy2 = hy + hh * 0.35
        fig.add_trace(self._box_mesh(
            cx2, cy2, wall_t - wall_h * 0.15,
            cx2 + cw, cy2 + cd, apex + wall_h * 0.18,
            '#616161', 'Chimney', opacity=1.0, show_legend=False
        ))
        # Smoke
        for si, (sox, soy, sr_s, sa_s) in enumerate([
            (cw * 0.5, 8 * scale, 2.5 * scale, 0.22),
            (cw * 0.9, 16 * scale, 3.8 * scale, 0.13),
            (cw * 0.2, 24 * scale, 5.0 * scale, 0.07),
        ]):
            scx = cx2 + sox
            scy = cy2 + cd / 2 + soy
            scz = apex + wall_h * 0.18 + si * 3 * scale
            theta_s = np.linspace(0, 2 * math.pi, 18)
            rg_s = np.linspace(0, sr_s, 6)
            RS, TS = np.meshgrid(rg_s, theta_s)
            fig.add_trace(go.Surface(
                x=scx + RS * np.cos(TS),
                y=scy + RS * np.sin(TS),
                z=np.full_like(RS, scz),
                colorscale=[[0, '#90A4AE'], [1, '#ECEFF1']],
                showscale=False, showlegend=False, opacity=sa_s,
            ))

    # ══════════════════════════════════════════════════════
    #  KITCHEN GARDEN (from zone_positions['z1'])
    # ══════════════════════════════════════════════════════

    def _kitchen_garden(self, fig, layout, L, W, scale):
        zones = layout.get('zone_positions', {})
        if 'z1' not in zones:
            return
        pos = zones['z1']
        x0, y0 = pos['x'], pos['y']
        gw, gh = pos['width'], pos['height']

        pad   = 8.0
        bed_w = max(10.0, min(gw * 0.14, 18.0))
        bed_h = max(20.0, min(gh * 0.55, gh * 0.88))
        gap   = max(5.0, min(gw * 0.025, 8.0))
        n_beds = max(1, int((gw - 2 * pad - gap) / (bed_w + gap)))

        for i in range(n_beds):
            bx = x0 + pad + i * (bed_w + gap)
            if bx + bed_w > x0 + gw - pad:
                break
            by = y0 + pad
            bz = self._slope_z(bx + bed_w / 2, by + bed_h / 2, layout, L, W, scale) + 0.5
            raise_h = 1.3 * scale

            # Wooden frame
            fig.add_trace(self._box_mesh(
                bx, by, bz, bx + bed_w, by + bed_h, bz + raise_h * 0.28,
                '#8D6E63', 'Kitchen Garden' if i == 0 else 'KG',
                opacity=0.95, show_legend=(i == 0)
            ))
            # Soil
            ft = bed_w * 0.12
            fig.add_trace(self._box_mesh(
                bx + ft, by + ft, bz + raise_h * 0.28,
                bx + bed_w - ft, by + bed_h - ft, bz + raise_h,
                '#3E2723', 'Soil', opacity=0.90, show_legend=False
            ))
            # Plants
            n_px = max(2, int((bed_w - 2 * ft) / 8))
            n_py = max(2, int((bed_h - 2 * ft) / 8))
            p_cols = ['#4CAF50', '#66BB6A', '#81C784', '#A5D6A7', '#2E7D32']
            for ci in range(n_px):
                for ri in range(n_py):
                    ppx = bx + ft + (ci + 0.5) * (bed_w - 2 * ft) / n_px
                    ppy = by + ft + (ri + 0.5) * (bed_h - 2 * ft) / n_py
                    pr_p = min(2.8, (bed_w - 2 * ft) / n_px * 0.38) * scale
                    pc = p_cols[(ci + ri) % len(p_cols)]
                    for tr in self._hemisphere(ppx, ppy, bz + raise_h, pr_p, pc):
                        fig.add_trace(tr)

        # Compost bin
        cxc = x0 + gw * 0.80
        cyc = y0 + gh * 0.65
        csz = min(gw, gh) * 0.11
        gzc = self._slope_z(cxc, cyc, layout, L, W, scale) + 0.5
        fig.add_trace(self._box_mesh(
            cxc, cyc, gzc, cxc + csz, cyc + csz, gzc + csz * 1.5 * scale,
            '#795548', 'Compost', opacity=0.92, show_legend=False
        ))

    # ══════════════════════════════════════════════════════
    #  LIVESTOCK (from layout['features'])
    # ══════════════════════════════════════════════════════

    def _livestock(self, fig, layout, L, W, scale):
        features = layout.get('features', {})

        for key, cfg in self.LIVESTOCK_CFG.items():
            if key not in features:
                continue
            f = features[key]
            if not f:
                continue

            wc, rc, lbl, shed_h_base, _lbl2 = cfg
            sx, sy = f['x'], f['y']
            sw, sd = f['width'], f['height']

            gz_s = self._slope_z(sx + sw / 2, sy + sd / 2, layout, L, W, scale)
            bz   = gz_s + 1.5
            top  = bz + shed_h_base * scale
            rt   = top + sw * 0.22 * scale

            # Foundation
            fig.add_trace(self._box_mesh(
                sx - 1, sy - 1, gz_s + 0.3,
                sx + sw + 1, sy + sd + 1, bz,
                '#BCAAA4', 'Shed Base', opacity=0.85, show_legend=False
            ))

            # Walls
            fig.add_trace(self._box_mesh(
                sx, sy, bz, sx + sw, sy + sd, top,
                wc, lbl, opacity=0.93
            ))

            # Wall texture
            for zb in np.linspace(bz + (top - bz) * 0.2, top - (top - bz) * 0.1, 3):
                fig.add_trace(go.Scatter3d(
                    x=[sx, sx + sw], y=[sy, sy], z=[zb, zb],
                    mode='lines', line=dict(color=rc, width=1),
                    showlegend=False, hoverinfo='skip',
                ))

            # Hip Roof
            fig.add_trace(self._hip_roof(sx, sy, sx + sw, sy + sd, top, rt, rc, f'{lbl} Roof'))

            # Door
            dw = sw * 0.22
            dh = (top - bz) * 0.62
            dx_d = sx + sw * 0.39 - dw / 2
            fig.add_trace(self._box_mesh(
                dx_d, sy - 0.3, bz, dx_d + dw, sy, bz + dh,
                '#4E342E', 'Shed Door', opacity=1.0, show_legend=False
            ))

            # Fence
            fence_ext = sd * 0.55
            fp = [
                (sx - sd * 0.08, sy - fence_ext),
                (sx + sw + sd * 0.08, sy - fence_ext),
                (sx + sw + sd * 0.08, sy),
                (sx - sd * 0.08, sy),
                (sx - sd * 0.08, sy - fence_ext),
            ]
            fig.add_trace(go.Scatter3d(
                x=[p[0] for p in fp], y=[p[1] for p in fp],
                z=[gz_s + 1.6] * len(fp),
                mode='lines', line=dict(color='#8D6E63', width=3),
                showlegend=False, hoverinfo='skip',
            ))
            for fpt in fp[:-1]:
                fig.add_trace(go.Scatter3d(
                    x=[fpt[0], fpt[0]], y=[fpt[1], fpt[1]],
                    z=[gz_s + 1.5, gz_s + 1.5 + shed_h_base * scale * 0.32],
                    mode='lines', line=dict(color='#6D4C41', width=3),
                    showlegend=False, hoverinfo='skip',
                ))

    # ══════════════════════════════════════════════════════
    #  FOOD FOREST TREES (from zone_positions['z2'])
    # ══════════════════════════════════════════════════════

    def _food_forest(self, fig, layout, L, W, scale):
        zones = layout.get('zone_positions', {})
        if 'z2' not in zones:
            return
        z2 = zones['z2']
        tree_count = self._get_tree_count(layout)

        x0, y0 = z2['x'], z2['y']
        zw, zh = z2['width'], z2['height']

        features = layout.get('features', {})
        pond = features.get('pond', {}) or {}
        pond_x = pond.get('x', -9999)
        pond_y = pond.get('y', -9999)
        pond_r = pond.get('radius', 10)

        tree_types = [
            (8.0, 20.0, '#1B5E20', 'Mango'),
            (7.5, 18.0, '#2E7D32', 'Jackfruit'),
            (6.0, 16.0, '#33691E', 'Coconut'),
            (5.5, 14.0, '#388E3C', 'Guava'),
            (5.0, 13.0, '#43A047', 'Banana'),
            (4.5, 12.0, '#4CAF50', 'Papaya'),
            (4.0, 11.0, '#66BB6A', 'Avocado'),
            (3.8, 10.0, '#81C784', 'Citrus'),
            (3.5,  9.5, '#558B2F', 'Moringa'),
            (3.2,  9.0, '#7CB342', 'Neem'),
        ]

        np.random.seed(99)
        positions = []
        min_sep = min(zw, zh) * 0.10
        attempts = 0

        while len(positions) < tree_count and attempts < tree_count * 22:
            attempts += 1
            rx = np.random.uniform(0.04, 0.96)
            ry = np.random.uniform(0.04, 0.96)
            tx_c = x0 + rx * zw
            ty_c = y0 + ry * zh

            if math.hypot(tx_c - pond_x, ty_c - pond_y) < pond_r * 1.4:
                continue
            if any(math.hypot(tx_c - px, ty_c - py) < min_sep for px, py in positions):
                continue
            positions.append((tx_c, ty_c))

        legend_added = set()
        for idx, (tx_c, ty_c) in enumerate(positions):
            cr_b, h_b, color, t_lbl = tree_types[idx % len(tree_types)]
            cr     = cr_b * scale
            h_tree = h_b * scale
            gz_tree = self._slope_z(tx_c, ty_c, layout, L, W, scale)

            trunk_bot = gz_tree + 0.3
            trunk_top = trunk_bot + h_tree * 0.38
            can_bot   = trunk_top - h_tree * 0.05
            can_top   = trunk_bot + h_tree
            trunk_r   = max(0.7, cr * 0.13)

            show_leg = t_lbl not in legend_added
            if show_leg:
                legend_added.add(t_lbl)

            for tr in self._cone_tree(
                tx_c, ty_c,
                trunk_bot_z=trunk_bot, trunk_top_z=trunk_top,
                canopy_bot_z=can_bot, canopy_top_z=can_top,
                canopy_r=cr, trunk_r=trunk_r,
                color_canopy=color, label=t_lbl, show_legend=show_leg,
            ):
                fig.add_trace(tr)

    # ══════════════════════════════════════════════════════
    #  UTILITIES (solar, greenhouse)
    # ══════════════════════════════════════════════════════

    def _utilities(self, fig, layout, L, W, scale):
        features = layout.get('features', {})

        if 'solar' in features and features['solar']:
            f = features['solar']
            sx, sy = f['x'], f['y']
            sw_s, sd_s = f['width'], f['height']
            gz_s = self._slope_z(sx + sw_s / 2, sy + sd_s / 2, layout, L, W, scale) + 1.5
            fig.add_trace(self._box_mesh(
                sx, sy, gz_s, sx + sw_s, sy + sd_s, gz_s + 0.4 * scale + sw_s * 0.12 * scale,
                '#1565C0', 'Solar Array', opacity=0.92
            ))

        if 'greenhouse' in features and features['greenhouse']:
            f = features['greenhouse']
            gx, gy = f['x'], f['y']
            gw_g, gh_g = f['width'], f['height']
            gz_g = self._slope_z(gx + gw_g / 2, gy + gh_g / 2, layout, L, W, scale) + 1.5
            gr_h = gw_g * 0.32 * scale
            fig.add_trace(self._box_mesh(
                gx, gy, gz_g, gx + gw_g, gy + gh_g, gz_g + gr_h,
                '#E0F2F1', 'Greenhouse', opacity=0.60
            ))
            fig.add_trace(self._hip_roof(
                gx, gy, gx + gw_g, gy + gh_g,
                gz_g + gr_h, gz_g + gr_h * 1.35,
                '#00897B', 'GH Roof'
            ))

    # ══════════════════════════════════════════════════════
    #  LABELS
    # ══════════════════════════════════════════════════════

    def _labels(self, fig, layout, L, W, scale):
        label_data = []
        lz = max(L, W) * 0.07 * scale

        hx, hy, hw, hh = self._house_bbox(layout, L, W)
        gz_h = self._slope_z(hx + hw / 2, hy + hh / 2, layout, L, W, scale)
        label_data.append({'x': hx + hw / 2, 'y': hy + hh / 2, 'z': gz_h + lz, 'text': 'RESIDENCE'})

        for zid, pos in layout.get('zone_positions', {}).items():
            cx = pos['x'] + pos['width'] * 0.5
            cy = pos['y'] + pos['height'] * 0.85
            gz_z = self._slope_z(cx, cy, layout, L, W, scale)
            label_data.append({
                'x': cx, 'y': cy, 'z': gz_z + lz * 0.38,
                'text': self.ZONE_NAMES.get(zid, zid).split('–')[-1].strip()
            })

        features = layout.get('features', {})
        for key, cfg in self.LIVESTOCK_CFG.items():
            if key not in features or not features[key]:
                continue
            f = features[key]
            _, _, lbl, sh_h, _e = cfg
            sx, sy = f['x'], f['y']
            sw_l, sd_l = f['width'], f['height']
            gz_lbl = self._slope_z(sx + sw_l / 2, sy + sd_l / 2, layout, L, W, scale)
            label_data.append({
                'x': sx + sw_l / 2, 'y': sy + sd_l / 2,
                'z': gz_lbl + 1.5 + sh_h * scale + lz * 0.32,
                'text': lbl
            })

        for wkey in ('pond', 'borewell', 'well'):
            if wkey in features and features[wkey]:
                f = features[wkey]
                gz_w = self._slope_z(f['x'], f['y'], layout, L, W, scale)
                label_data.append({
                    'x': f['x'], 'y': f['y'],
                    'z': gz_w + lz * 0.5,
                    'text': 'Pond' if wkey == 'pond' else 'Borewell'
                })

        if label_data:
            fig.add_trace(go.Scatter3d(
                x=[d['x'] for d in label_data],
                y=[d['y'] for d in label_data],
                z=[d['z'] for d in label_data],
                mode='text',
                text=[d['text'] for d in label_data],
                textfont=dict(size=11, color='#0D47A1', family='Arial Black'),
                name='Labels', showlegend=False,
            ))

    # ══════════════════════════════════════════════════════
    #  GEOMETRY PRIMITIVES
    # ══════════════════════════════════════════════════════

    @staticmethod
    def _box_mesh(x0, y0, z0, x1, y1, z1, color, name,
                  opacity=0.88, show_legend=True) -> go.Mesh3d:
        vx = [x0, x1, x1, x0, x0, x1, x1, x0]
        vy = [y0, y0, y1, y1, y0, y0, y1, y1]
        vz = [z0, z0, z0, z0, z1, z1, z1, z1]
        fi = [0, 0, 4, 4, 0, 0, 2, 2, 0, 0, 1, 1]
        fj = [1, 2, 5, 6, 1, 5, 3, 7, 3, 7, 2, 6]
        fk = [2, 3, 6, 7, 5, 4, 7, 6, 7, 4, 6, 5]
        return go.Mesh3d(
            x=vx, y=vy, z=vz, i=fi, j=fj, k=fk,
            color=color, opacity=opacity, name=name,
            showlegend=show_legend, flatshading=True,
            lighting=dict(ambient=0.68, diffuse=0.92, specular=0.25,
                          roughness=0.55, fresnel=0.15),
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
            lighting=dict(ambient=0.60, diffuse=0.95, specular=0.30),
        )

    @staticmethod
    def _hemisphere(cx, cy, base_z, r, color, n=10) -> List:
        theta = np.linspace(0, math.pi / 2, n)
        phi   = np.linspace(0, 2 * math.pi, n)
        T, P  = np.meshgrid(theta, phi)
        return [go.Surface(
            x=cx + r * np.sin(T) * np.cos(P),
            y=cy + r * np.sin(T) * np.sin(P),
            z=base_z + r * np.cos(T),
            colorscale=[[0, color], [1, '#A5D6A7']],
            showscale=False, showlegend=False, opacity=0.88,
            name='Plant',
        )]

    @staticmethod
    def _cone_tree(tx, ty,
                   trunk_bot_z=1.5, trunk_top_z=7.0,
                   canopy_bot_z=7.0, canopy_top_z=18.0,
                   canopy_r=7.5, trunk_r=1.2,
                   color_canopy='#2E7D32',
                   label='', show_legend=False) -> List:
        traces = []
        n = 22

        # Trunk
        theta_t = np.linspace(0, 2 * math.pi, n)
        zz      = np.array([trunk_bot_z, trunk_top_z])
        TG, ZG  = np.meshgrid(theta_t, zz)
        traces.append(go.Surface(
            x=tx + trunk_r * np.cos(TG),
            y=ty + trunk_r * np.sin(TG),
            z=ZG,
            colorscale=[[0, '#5D4037'], [1, '#795548']],
            showscale=False, showlegend=False, opacity=0.97,
        ))

        # Canopy cone
        theta_c = np.linspace(0, 2 * math.pi, n, endpoint=False)
        vx = list(tx + canopy_r * np.cos(theta_c)) + [tx]
        vy = list(ty + canopy_r * np.sin(theta_c)) + [ty]
        vz = [canopy_bot_z] * n + [canopy_top_z]
        traces.append(go.Mesh3d(
            x=vx, y=vy, z=vz,
            i=list(range(n)), j=[(k + 1) % n for k in range(n)], k=[n] * n,
            color=color_canopy, opacity=0.90,
            name=label if label else 'Tree',
            showlegend=show_legend, flatshading=True,
            lighting=dict(ambient=0.62, diffuse=0.90, specular=0.08),
        ))

        # Canopy base disk
        rg_d = np.linspace(0, canopy_r, 7)
        RD, TD = np.meshgrid(rg_d, theta_c)
        traces.append(go.Surface(
            x=tx + RD * np.cos(TD), y=ty + RD * np.sin(TD),
            z=np.full_like(RD, canopy_bot_z),
            colorscale=[[0, color_canopy], [1, color_canopy]],
            showscale=False, showlegend=False, opacity=0.72,
        ))

        return traces
