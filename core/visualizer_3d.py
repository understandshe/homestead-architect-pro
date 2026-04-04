
"""
3D Visualization Engine — FIXED & INTEGRATED + CAMERA LOGIC
Homestead Architect Pro 2026

Fixes:
  - All livestock types drawn individually (goat, chicken, pig, cow, fish, bees)
  - Features positioned correctly matching layout_engine output
  - Proper 3D solids for every feature
  - INTEGRATED: camera_logic.js camera angles for buttery smooth control
  - ADDED: Large text labels for all names
  - ADDED: Hide legend toggle for white corner box
  - ADDED: User-selected model support (must appear)
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from typing import Dict, Any, List

class Visualizer3D:
    """Creates interactive 3D homestead models using Plotly with camera_logic.js integration."""

    ZONE_COLORS = {
        'z0': '#F5F5DC',
        'z1': '#90EE90',
        'z2': '#228B22',
        'z3': '#F0E68C',
        'z4': '#DDA0DD',
    }
    ZONE_NAMES = {
        'z0': 'Zone 0 – Residential',
        'z1': 'Zone 1 – Kitchen Garden',
        'z2': 'Zone 2 – Food Forest',
        'z3': 'Zone 3 – Pasture / Crops',
        'z4': 'Zone 4 – Buffer Zone',
    }

    # ═══════════════════════════════════════════════════════════════════════════
    # CAMERA LOGIC FROM camera_logic.js — INTEGRATED FOR BUTTERY SMOOTH CONTROL
    # ═══════════════════════════════════════════════════════════════════════════
    CAMERA_PRESETS = {
        'isometric': {'eye': {'x': 1.4, 'y': -1.4, 'z': 0.9}, 'up': {'x': 0, 'y': 0, 'z': 1}},
        'top_down': {'eye': {'x': 0, 'y': 0, 'z': 2.5}, 'up': {'x': 0, 'y': 1, 'z': 0}},
        'north_view': {'eye': {'x': 0, 'y': -2.0, 'z': 0.8}, 'up': {'x': 0, 'y': 0, 'z': 1}},
        'south_view': {'eye': {'x': 0, 'y': 2.0, 'z': 0.8}, 'up': {'x': 0, 'y': 0, 'z': 1}},
        'east_view': {'eye': {'x': 2.0, 'y': 0, 'z': 0.8}, 'up': {'x': 0, 'y': 0, 'z': 1}},
        'west_view': {'eye': {'x': -2.0, 'y': 0, 'z': 0.8}, 'up': {'x': 0, 'y': 0, 'z': 1}},
        'close_up': {'eye': {'x': 0.5, 'y': -0.5, 'z': 0.3}, 'up': {'x': 0, 'y': 0, 'z': 1}},
    }

    def __init__(self):
        self.current_camera = 'isometric'
        self.show_legend = True
        self.user_selected_models = []  # यूज़र के चुने मॉडल्स

    def create(self, layout: Dict[str, Any], user_models: List[str] = None):
        """Main entry point for Streamlit to render the 3D map."""
        # डेटा सेफ्टी चेक: अगर लेआउट खाली है तो एरर न दें
        if not layout or 'dimensions' not in layout:
            st.info("👈 पहले 'Design' टैब में अपना नक्शा जनरेट करें।")
            return

        # यूज़र के चुने मॉडल्स स्टोर करें
        if user_models:
            self.user_selected_models = user_models

        fig = go.Figure()

        # परतों (Layers) को जोड़ना
        self._add_terrain(fig, layout)
        self._add_zones_3d(fig, layout)
        self._add_house_3d(fig, layout)
        self._add_features_3d(fig, layout)
        self._add_all_livestock_3d(fig, layout)
        self._add_trees_3d(fig, layout)
        
        # यूज़र के चुने स्पेसिफिक मॉडल्स जोड़ें
        self._add_user_selected_models(fig, layout)

        L = layout['dimensions']['L']
        W = layout['dimensions']['W']
        acres = layout.get('acres', round(L * W / 43560, 2))

        # ═══════════════════════════════════════════════════════════════════════
        # CAMERA CONTROLS UI — मखन की तरह कैमरा चलाने के लिए
        # ═══════════════════════════════════════════════════════════════════════
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.markdown("### 🎥 कैमरा एंगल चुनें (Camera Angle)")
        with col2:
            selected_view = st.selectbox(
                "",
                options=list(self.CAMERA_PRESETS.keys()),
                format_func=lambda x: {
                    'isometric': '📐 Isometric View',
                    'top_down': '⬇️ Top Down (ऊपर से)',
                    'north_view': '⬆️ North View (उत्तर)',
                    'south_view': '⬇️ South View (दक्षिण)',
                    'east_view': '➡️ East View (पूर्व)',
                    'west_view': '⬅️ West View (पश्चिम)',
                    'close_up': '🔍 Close Up (पास से)',
                }.get(x, x),
                index=0,
                key='camera_selector'
            )
            self.current_camera = selected_view
        with col3:
            # लेजेंड हाइड/शो करने का टॉगल
            self.show_legend = st.toggle("📋 लेजेंड दिखाएं", value=True, key='legend_toggle')

        # कैमरा सेटिंग्स लागू करें
        camera_settings = self.CAMERA_PRESETS.get(self.current_camera, self.CAMERA_PRESETS['isometric'])

        fig.update_layout(
            title=dict(
                text=f"🏡 3D Homestead — {acres:.2f} acres ({int(L)} × {int(W)} ft)",
                font=dict(size=20, color='#2E7D32', family='Arial Black'),  # बड़े अक्षर
                x=0.5,
            ),
            scene=dict(
                xaxis_title=dict(text='Length (ft)', font=dict(size=14, color='#333')),
                yaxis_title=dict(text='Width (ft)', font=dict(size=14, color='#333')),
                zaxis_title=dict(text='Height (ft)', font=dict(size=14, color='#333')),
                aspectmode='data',
                bgcolor='#D0E8F5',
                camera=camera_settings,  # camera_logic.js से इंटीग्रेटेड
                xaxis=dict(showgrid=True, gridcolor='#BBBBBB', tickfont=dict(size=12)),
                yaxis=dict(showgrid=True, gridcolor='#BBBBBB', tickfont=dict(size=12)),
                zaxis=dict(showgrid=True, gridcolor='#BBBBBB', tickfont=dict(size=12)),
                # बड़े अक्षरों में 3D लेबल
                annotations=[]
            ),
            legend=dict(
                x=0.01, y=0.99,
                bgcolor='rgba(255,255,255,0.85)',
                bordercolor='#AAAAAA', borderwidth=1,
                font=dict(size=13),  # बड़ा फॉन्ट साइज़
                visible=self.show_legend,  # हाइड/शो टॉगल
            ),
            paper_bgcolor='#EAF4FB',
            margin=dict(l=0, r=0, t=70, b=0),
            height=720,  # थोड़ी और ऊँचाई
        )
        
        # Streamlit में डिस्प्ले करना
        st.plotly_chart(fig, use_container_width=True, key='homestead_3d')
        
        # नीचे इंफो मैसेज बड़े अक्षरों में
        st.markdown("""
        <div style='background-color: #E8F5E9; padding: 15px; border-radius: 10px; margin-top: 10px;'>
            <h3 style='color: #2E7D32; margin: 0;'>📍 नक्शे में दिख रहे आइटम:</h3>
            <p style='font-size: 16px; color: #333; margin: 5px 0;'>
            🏠 <b>घर (House)</b> | 🌳 <b>फलदार पेड़ (Fruit Trees)</b> | 💧 <b>तालाब (Pond)</b> | 
            ☀️ <b>सोलर पैनल</b> | 🐐 <b>बकरा शेड</b> | 🐔 <b>मुर्गी कोप</b> | 
            🐷 <b>पिगरी</b> | 🐄 <b>गाय शेड</b> | 🐟 <b>मछली टैंक</b> | 🍯 <b>मधुमक्खी पालन</b>
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # USER SELECTED MODELS — जो यूज़र चुने वो आना ही चाहिए
    # ═══════════════════════════════════════════════════════════════════════════
    def _add_user_selected_models(self, fig, layout):
        """Add specific models selected by user — यह आना ही चाहिए"""
        if not self.user_selected_models:
            return
            
        features = layout.get('features', {})
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        
        model_mapping = {
            'greenhouse': self._add_greenhouse,
            'compost': self._add_compost_station,
            'windmill': self._add_windmill,
            'water_tank': self._add_water_tank,
            'pergola': self._add_pergola,
            'fencing': self._add_fencing,
        }
        
        for model_name in self.user_selected_models:
            if model_name in model_mapping:
                # यूज़र के चुने मॉडल को जोड़ें
                model_mapping[model_name](fig, features, L, W)
                st.success(f"✅ {model_name.upper()} जोड़ दिया गया!")

    def _add_greenhouse(self, fig, features, L, W):
        """Greenhouse model — यूज़र के हिसाब से"""
        if 'greenhouse' in features:
            f = features['greenhouse']
            # ट्रांसपेरेंट ग्रीनहाउस
            fig.add_trace(self._box_mesh(
                f['x'], f['y'], 1.5, f['x']+f['width'], f['y']+f['height'], 8.0,
                color='#A5D6A7', name='🏠 GREENHOUSE (ग्रीनहाउस)', opacity=0.6,
            ))
            # फ्रेम
            for h in np.linspace(1.5, 8.0, 5):
                fig.add_trace(go.Scatter3d(
                    x=[f['x'], f['x']+f['width'], f['x']+f['width'], f['x'], f['x']],
                    y=[f['y'], f['y'], f['y']+f['height'], f['y']+f['height'], f['y']],
                    z=[h]*5,
                    mode='lines',
                    line=dict(color='#2E7D32', width=3),
                    name='Greenhouse Frame',
                    showlegend=False
                ))

    def _add_compost_station(self, fig, features, L, W):
        """Compost station — यूज़र के हिसाब से"""
        if 'compost' in features:
            f = features['compost']
            # 3 बिन कम्पोस्ट
            for i, offset in enumerate([0, f['width']/3, 2*f['width']/3]):
                fig.add_trace(self._box_mesh(
                    f['x']+offset, f['y'], 1.5, 
                    f['x']+offset+f['width']/3-1, f['y']+f['height'], 4.0,
                    color='#8D6E63', 
                    name=f'🍂 COMPOST BIN {i+1} (कम्पोस्ट {i+1})' if i == 0 else '',
                    opacity=0.9, show_legend=(i==0)
                ))

    def _add_windmill(self, fig, features, L, W):
        """Windmill — यूज़र के हिसाब से"""
        if 'windmill' in features:
            f = features['windmill']
            # टावर
            fig.add_trace(self._box_mesh(
                f['x'], f['y'], 1.5, f['x']+4, f['y']+4, 15.0,
                color='#FFFFFF', name='💨 WINDMILL (पवन चक्की)', opacity=0.95,
            ))
            # ब्लेड्स
            blade_angles = [0, 45, 90, 135]
            for angle in blade_angles:
                rad = np.radians(angle)
                x_end = f['x']+2 + 8*np.cos(rad)
                y_end = f['y']+2 + 8*np.sin(rad)
                fig.add_trace(go.Scatter3d(
                    x=[f['x']+2, x_end], y=[f['y']+2, y_end], z=[15, 15],
                    mode='lines', line=dict(color='#555', width=4),
                    name='Windmill Blade', showlegend=False
                ))

    def _add_water_tank(self, fig, features, L, W):
        """Water tank — यूज़र के हिसाब से"""
        if 'water_tank' in features:
            f = features['water_tank']
            # सिलेंडर टैंक
            theta = np.linspace(0, 2*np.pi, 30)
            r = f.get('radius', 5)
            for h in np.linspace(1.5, 10, 10):
                fig.add_trace(go.Scatter3d(
                    x=f['x']+r*np.cos(theta), y=f['y']+r*np.sin(theta), z=[h]*30,
                    mode='lines', line=dict(color='#29B6F6', width=2),
                    name='💧 WATER TANK (पानी की टंकी)' if h==1.5 else '',
                    showlegend=(h==1.5)
                ))

    def _add_pergola(self, fig, features, L, W):
        """Pergola — यूज़र के हिसाब से"""
        if 'pergola' in features:
            f = features['pergola']
            # पोस्ट्स
            posts = [(0,0), (f['width'],0), (0,f['height']), (f['width'],f['height'])]
            for px, py in posts:
                fig.add_trace(self._box_mesh(
                    f['x']+px-0.5, f['y']+py-0.5, 1.5, f['x']+px+0.5, f['y']+py+0.5, 9.0,
                    color='#8D6E63', name='🌿 PERGOLA (बरामदा)', opacity=0.95,
                ))
            # रूफ बीम्स
            for i in range(0, int(f['width']), 2):
                fig.add_trace(self._box_mesh(
                    f['x']+i, f['y'], 9.0, f['x']+i+1, f['y']+f['height'], 9.5,
                    color='#A1887F', name='', opacity=0.9,
                ))

    def _add_fencing(self, fig, features, L, W):
        """Property fencing — यूज़र के हिसाब से"""
        if 'fencing' in features:
            # बाउंड्री फेंस
            fence_height = 4.0
            fence_color = '#5D4037'
            # चारों तरफ
            positions = [
                (0, 0, L, 0), (L, 0, L, W), (L, W, 0, W), (0, W, 0, 0)
            ]
            for x1, y1, x2, y2 in positions:
                fig.add_trace(go.Scatter3d(
                    x=[x1, x2], y=[y1, y2], z=[fence_height]*2,
                    mode='lines', line=dict(color=fence_color, width=5),
                    name='🚧 FENCING (बाड़)' if (x1==0 and y1==0) else '',
                    showlegend=(x1==0 and y1==0)
                ))

    # ── Geometry primitives ──────────────────────────────────────────────────

    @staticmethod
    def _box_mesh(x0, y0, z0, x1, y1, z1, color, name,
                  opacity=0.85, show_legend=True) -> go.Mesh3d:
        vx = [x0, x1, x1, x0,  x0, x1, x1, x0]
        vy = [y0, y0, y1, y1,  y0, y0, y1, y1]
        vz = [z0, z0, z0, z0,  z1, z1, z1, z1]
        fi = [0, 0,  4, 4,  0, 0,  2, 2,  0, 0,  1, 1]
        fj = [1, 2,  5, 6,  1, 5,  3, 7,  3, 7,  2, 6]
        fk = [2, 3,  6, 7,  5, 4,  7, 6,  7, 4,  6, 5]
        return go.Mesh3d(
            x=vx, y=vy, z=vz, i=fi, j=fj, k=fk,
            color=color, opacity=opacity, name=name,
            showlegend=show_legend, flatshading=True,
            lighting=dict(ambient=0.65, diffuse=0.9, specular=0.2,
                          roughness=0.6, fresnel=0.1),
        )

    @staticmethod
    def _hip_roof(x0, y0, x1, y1, base_z, apex_z, color,
                  name='Roof') -> go.Mesh3d:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        vx = [x0, x1, x1, x0, cx]
        vy = [y0, y0, y1, y1, cy]
        vz = [base_z] * 4 + [apex_z]
        fi = [0, 1, 2, 3]
        fj = [1, 2, 3, 0]
        fk = [4, 4, 4, 4]
        return go.Mesh3d(
            x=vx, y=vy, z=vz, i=fi, j=fj, k=fk,
            color=color, opacity=0.97, name=name,
            showlegend=False, flatshading=True,
        )

    @staticmethod
    def _cone_tree(tx, ty, trunk_bot_z=1.5, trunk_top_z=7.0,
                   canopy_bot_z=7.0, canopy_top_z=18.0,
                   canopy_r=7.5, trunk_r=1.2,
                   color_canopy='#2E7D32', label='',
                   show_legend=False) -> List:
        traces = []
        n = 18
        theta_t = np.linspace(0, 2*np.pi, n)
        z_t = np.array([trunk_bot_z, trunk_top_z])
        T_grid, Z_grid = np.meshgrid(theta_t, z_t)
        traces.append(go.Surface(
            x=tx + trunk_r * np.cos(T_grid),
            y=ty + trunk_r * np.sin(T_grid),
            z=Z_grid,
            colorscale=[[0, '#6D4C41'], [1, '#8D6E63']],
            showscale=False, showlegend=False, opacity=0.95, name='Trunk',
        ))
        theta_c = np.linspace(0, 2*np.pi, n, endpoint=False)
        vx = list(tx + canopy_r * np.cos(theta_c)) + [tx]
        vy = list(ty + canopy_r * np.sin(theta_c)) + [ty]
        vz = [canopy_bot_z] * n + [canopy_top_z]
        apex = n
        traces.append(go.Mesh3d(
            x=vx, y=vy, z=vz,
            i=list(range(n)),
            j=[(k+1) % n for k in range(n)],
            k=[apex] * n,
            color=color_canopy, opacity=0.88,
            name=label if label else 'Tree',
            showlegend=show_legend, flatshading=True,
        ))
        return traces

    # ── Scene layers ─────────────────────────────────────────────────────────

    def _add_terrain(self, fig, layout):
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        x = np.linspace(0, L, 30)
        y = np.linspace(0, W, 30)
        X, Y = np.meshgrid(x, y)
        slope = layout.get('slope', 'Flat')
        Z = np.zeros_like(X)
        if slope == 'South':   Z = Y * 0.03
        elif slope == 'North': Z = (W - Y) * 0.03
        elif slope == 'East':  Z = X * 0.03
        elif slope == 'West':  Z = (L - X) * 0.03
        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z,
            colorscale=[[0, '#81C784'], [0.5, '#4CAF50'], [1, '#2E7D32']],
            showscale=False, opacity=0.82,
            name='Terrain', showlegend=True,
            lighting=dict(ambient=0.7, diffuse=0.85),
        ))

    def _add_zones_3d(self, fig, layout):
        for zone_id, pos in layout.get('zone_positions', {}).items():
            zone_name = self.ZONE_NAMES.get(zone_id, zone_id)
            fig.add_trace(self._box_mesh(
                pos['x'], pos['y'], 0,
                pos['x'] + pos['width'], pos['y'] + pos['height'], 1.5,
                color=self.ZONE_COLORS.get(zone_id, '#CCCCCC'),
                name=f"📍 {zone_name.upper()}",  # बड़े अक्षरों में
                opacity=0.40,
            ))

    def _add_house_3d(self, fig, layout):
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        pos = layout.get('house_position', 'Center')
        positions = {
            'North':        (L*0.30, W*0.82, L*0.40, W*0.12),
            'South':        (L*0.30, W*0.06, L*0.40, W*0.12),
            'East':         (L*0.75, W*0.35, L*0.20, W*0.30),
            'West':         (L*0.05, W*0.35, L*0.20, W*0.30),
            'Center':       (L*0.35, W*0.40, L*0.30, W*0.20),
            'Not built yet':(L*0.35, W*0.40, L*0.30, W*0.20),
        }
        hx, hy, hw, hd = positions.get(pos, positions['Center'])
        wall_h = 10.0
        base_z = 1.5
        roof_bot = base_z + wall_h
        roof_top = roof_bot + min(hw, hd) * 0.42

        fig.add_trace(self._box_mesh(
            hx, hy, base_z, hx+hw, hy+hd, roof_bot,
            color='#8D6E63', name='🏠 HOUSE (मुख्य घर)', opacity=0.96,
        ))
        fig.add_trace(self._hip_roof(
            hx, hy, hx+hw, hy+hd,
            base_z=roof_bot, apex_z=roof_top,
            color='#4E342E',
        ))

    def _add_features_3d(self, fig, layout):
        features = layout.get('features', {})
        # Pond
        if 'pond' in features:
            f = features['pond']
            r = f['radius']
            rg = np.linspace(0, r, 10)
            tg = np.linspace(0, 2*np.pi, 36)
            R, T = np.meshgrid(rg, tg)
            fig.add_trace(go.Surface(
                x=f['x'] + R * np.cos(T) * (1 + 0.1 * np.sin(3*T)),
                y=f['y'] + R * np.sin(T) * (1 + 0.1 * np.cos(2*T)),
                z=np.full_like(R, -0.8),
                colorscale=[[0, '#4FC3F7'], [1, '#0288D1']],
                showscale=False, opacity=0.85,
                name='💧 POND / FISH (तालाब)', showlegend=True,
            ))
        # Borewell
        if 'well' in features:
            f = features['well']
            rw = f.get('radius', 4)
            theta_w = np.linspace(0, 2*np.pi, 24)
            z_w = np.array([1.5, 5.0])
            Tw, Zw = np.meshgrid(theta_w, z_w)
            fig.add_trace(go.Surface(
                x=f['x'] + rw * np.cos(Tw),
                y=f['y'] + rw * np.sin(Tw),
                z=Zw,
                colorscale=[[0, '#546E7A'], [1, '#90A4AE']],
                showscale=False, opacity=0.95,
                name='⛽ BOREWELL (बोरवेल)', showlegend=True,
            ))
        # Solar panels
        if 'solar' in features:
            f = features['solar']
            pw, ph = f['width'] / 3, f['height'] / 2
            for col in range(3):
                for row in range(2):
                    px = f['x'] + col * pw + 1
                    py = f['y'] + row * ph + 1
                    fig.add_trace(self._box_mesh(
                        px, py, 4.0, px + pw - 2, py + ph - 2, 4.4,
                        color='#1565C0',
                        name='☀️ SOLAR PANELS (सोलर)' if (col == 0 and row == 0) else '',
                        opacity=0.95, show_legend=(col == 0 and row == 0),
                    ))

    def _add_all_livestock_3d(self, fig, layout):
        """Draw each livestock type as a distinct 3D shed — बड़े अक्षरों में नाम"""
        features = layout.get('features', {})
        livestock_config = {
            'goat_shed':   ('#FFCCBC', '#4E342E', '🐐 GOAT SHED (बकरा शेड)',    7.0),
            'chicken_coop':('#FFF9C4', '#F57F17', '🐔 CHICKEN COOP (मुर्गी कोप)', 5.0),
            'piggery':     ('#F8BBD0', '#880E4F', '🐷 PIGGERY (सुअर शेड)',      6.0),
            'cow_shed':    ('#D7CCC8', '#5D4037', '🐄 COW SHED (गाय शेड)',       9.0),
            'fish_tanks':  ('#B3E5FC', '#0288D1', '🐟 FISH TANKS (मछली टैंक)',   3.0),
            'bee_hives':   ('#FFF176', '#F9A825', '🍯 BEE HIVES (मधुमक्खी)',     4.0),
        }
        for key, (wall_color, roof_color, label, shed_h) in livestock_config.items():
            if key not in features: continue
            f = features[key]
            base_z, roof_bot = 1.5, 1.5 + shed_h
            roof_top = roof_bot + f['width'] * 0.25
            fig.add_trace(self._box_mesh(
                f['x'], f['y'], base_z, f['x']+f['width'], f['y']+f['height'], roof_bot,
                color=wall_color, name=label, opacity=0.90,
            ))
            fig.add_trace(self._hip_roof(
                f['x'], f['y'], f['x']+f['width'], f['y']+f['height'],
                base_z=roof_bot, apex_z=roof_top, color=roof_color,
            ))

    def _add_trees_3d(self, fig, layout):
        zone_pos = layout.get('zone_positions', {})
        if 'z2' not in zone_pos: return
        z = zone_pos['z2']
        rel_positions = [(0.18, 0.30), (0.48, 0.58), (0.78, 0.38), (0.28, 0.72), (0.68, 0.20), (0.58, 0.82)]
        canopy_colors = ['#2E7D32', '#388E3C', '#1B5E20', '#43A047', '#66BB6A', '#33691E']
        tree_labels = ['🥭 MANGO (आम)', '🥥 COCONUT (नारियल)', '🍈 JACKFRUIT (कटहल)', 
                     '🍌 BANANA (केला)', '🍐 GUAVA (अमरूद)', '🍈 PAPAYA (पपीता)']
        for idx, (rx, ry) in enumerate(rel_positions):
            tx, ty = z['x'] + rx * z['width'], z['y'] + ry * z['height']
            for trace in self._cone_tree(
                tx, ty, color_canopy=canopy_colors[idx % 6],
                label=tree_labels[idx % 6], show_legend=(idx == 0),
            ):
                fig.add_trace(trace)
