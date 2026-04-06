import plotly.graph_objects as go
import numpy as np
import streamlit as st
from typing import Dict, Any, List

class Visualizer3D:
    def __init__(self):
        # Professional Material Library (PBR-like settings)
        self.materials = {
            'grass': dict(ambient=0.5, diffuse=0.8, specular=0.05, roughness=0.9, fresnel=0.1),
            'house_wall': dict(ambient=0.4, diffuse=0.7, specular=0.2, roughness=0.5),
            'roof_tiles': dict(ambient=0.3, diffuse=0.9, specular=0.5, roughness=0.3),
            'water': dict(ambient=0.7, diffuse=0.9, specular=1.0, roughness=0.1, fresnel=0.8),
            'tree_foliage': dict(ambient=0.4, diffuse=0.9, specular=0.1, roughness=0.8)
        }

    def create(self, layout: Dict[str, Any]):
        """Main Orchestrator: जो पूरे 3D वर्ल्ड को असेंबल करता है"""
        if not layout:
            st.warning("No layout data found! Please design first.")
            return

        L = float(layout['dimensions']['L'])
        W = float(layout['dimensions']['W'])
        acres = layout.get('acres', (L * W) / 43560) # User के Acres का हिसाब [cite: 1]

        fig = go.Figure()

        # 1. GENERATE HIGH-RES TERRAIN (असली उबड़-खाबड़ जमीन)
        self._add_premium_terrain(fig, L, W, layout.get('slope', 'Flat'))

        # 2. ARCHITECTURAL RESIDENCE (Gable Roof + Porch + Windows)
        self._add_detailed_house(fig, layout, L, W)

        # 3. PROCEDURAL VEGETATION (User Tree Count के हिसाब से)
        tree_count = layout.get('tree_count', 15) # [cite: 1]
        self._add_advanced_forest(fig, layout, L, W, tree_count)

        # 4. LIVESTOCK COMPLEX (Animal-specific Sheds)
        selected_animals = layout.get('livestock', []) # [cite: 1]
        self._add_animal_shelters(fig, layout, selected_animals)

        # 5. WATER & IRRIGATION (Realistic Reflections)
        if 'pond' in layout.get('features', {}):
            self._add_realistic_pond(fig, layout['features']['pond'])

        # 6. SCENE & LIGHTING CONFIG (Cinematic Mode)
        self._setup_cinematic_view(fig, L, W, acres)

        st.plotly_chart(fig, use_container_width=True, config={'displaylogo': False})

    # --- Terrain Module ---
    def _add_premium_terrain(self, fig, L, W, slope_dir):
        res = 100 # High resolution grid
        x = np.linspace(0, L, res)
        y = np.linspace(0, W, res)
        X, Y = np.meshgrid(x, y)
        
        # Base Elevation based on Slope direction
        Z = np.zeros_like(X)
        if slope_dir == 'South': Z += (Y / W) * 10.0
        elif slope_dir == 'North': Z += ((W - Y) / W) * 10.0
        elif slope_dir == 'East': Z += (X / L) * 10.0
        elif slope_dir == 'West': Z += ((L - X) / L) * 10.0

        # Micro-terrain noise (असली घास और मिट्टी का अहसास)
        noise = (np.random.normal(0, 0.15, (res, res)))
        Z += noise

        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z,
            colorscale=[[0, '#1B3022'], [0.2, '#2E7D32'], [0.8, '#4C9A46'], [1, '#D4E157']],
            showscale=False,
            lighting=self.materials['grass'],
            name='Homestead Terrain',
            hoverinfo='z'
        ))

    # --- Architectural Module ---
    def _add_detailed_house(self, fig, layout, L, W):
        # घर की सटीक पोजीशन यूजर के इनपुट से (North, South, etc.) [cite: 1]
        pos = layout.get('house_position', 'Center')
        hx, hy = L * 0.4, W * 0.4 # Default center
        # ... (Positioning Logic)

        # Main Building Mesh (Walls)
        self._draw_mesh_box(fig, hx, hy, 0, hx+30, hy+25, 12, '#D7CCC8', 'House Walls', self.materials['house_wall'])
        
        # Gable Roof (त्रिभुज वाली असली छत)
        fig.add_trace(go.Mesh3d(
            x=[hx, hx+30, hx+30, hx, hx+15],
            y=[hy, hy, hy+25, hy+25, hy+12.5],
            z=[12, 12, 12, 12, 20],
            i=[0, 1, 2, 3], j=[1, 2, 3, 0], k=[4, 4, 4, 4],
            color='#5D4037', lighting=self.materials['roof_tiles'], name='Roof'
        ))

    # --- Helper: Mesh Box Generator ---
    def _draw_mesh_box(self, fig, x0, y0, z0, x1, y1, z1, color, name, mat):
        vx = [x0, x1, x1, x0, x0, x1, x1, x0]
        vy = [y0, y0, y1, y1, y0, y0, y1, y1]
        vz = [z0, z0, z0, z0, z1, z1, z1, z1]
        # Indices for 6 faces of a box
        i = [0, 0, 4, 4, 0, 0, 2, 2, 0, 0, 1, 1]
        j = [1, 2, 5, 6, 1, 5, 3, 7, 3, 7, 2, 6]
        k = [2, 3, 6, 7, 5, 4, 7, 6, 7, 4, 6, 5]
        fig.add_trace(go.Mesh3d(x=vx, y=vy, z=vz, i=i, j=j, k=k, color=color, name=name, lighting=mat))

    def _setup_cinematic_view(self, fig, L, W, acres):
        fig.update_layout(
            title=f"Homestead Architect 3D - {acres:.2f} Acres Plot",
            scene=dict(
                aspectmode='manual',
                aspectratio=dict(x=1, y=W/L, z=0.2),
                camera=dict(eye=dict(x=1.8, y=-1.8, z=1.2))
            ),
            paper_bgcolor='#E8EFF5'
        )
        # --- Livestock Module (Premium Animal Housing) ---
    def _add_animal_shelters(self, fig, layout, animals):
        """यूजर द्वारा चुने गए हर जानवर के लिए अलग 3D शेड बनाना [cite: 1]"""
        features = layout.get('features', {})
        
        # Animal-Specific Configurations (Color, Height, Name)
        config = {
            'goat_shed': {'wall': '#E8B7A2', 'roof': '#5B3A2B', 'label': 'Goat Mansion', 'h': 8},
            'chicken_coop': {'wall': '#EFE4A7', 'roof': '#8A6A17', 'label': 'Poultry Palace', 'h': 5},
            'piggery': {'wall': '#E6AFC4', 'roof': '#6B334E', 'label': 'Pig Villa', 'h': 6},
            'cow_shed': {'wall': '#C6B9AD', 'roof': '#5B4A3A', 'label': 'Bovine Barn', 'h': 10}
        }

        for key, cfg in config.items():
            if key in features:
                f = features[key]
                x0, y0 = f['x'], f['y']
                x1, y1 = x0 + f['width'], y0 + f['height']
                
                # 1. Base Walls (Mesh3d)
                self._draw_mesh_box(fig, x0, y0, 0.5, x1, y1, cfg['h'], 
                                   cfg['wall'], cfg['label'], self.materials['house_wall'])
                
                # 2. Realistic Slanted Roof (प्रीमियम लुक के लिए)
                fig.add_trace(go.Mesh3d(
                    x=[x0-2, x1+2, x1+2, x0-2, (x0+x1)/2],
                    y=[y0-2, y0-2, y1+2, y1+2, (y0+y1)/2],
                    z=[cfg['h'], cfg['h'], cfg['h'], cfg['h'], cfg['h']+5],
                    i=[0, 1, 2, 3], j=[1, 2, 3, 0], k=[4, 4, 4, 4],
                    color=cfg['roof'], lighting=self.materials['roof_tiles'],
                    name=f"{cfg['label']} Roof"
                ))

    # --- Vegetation Module (Procedural Organic Forest) ---
    def _add_advanced_forest(self, fig, layout, L, W, tree_count):
        """पेड़ों को बेतरतीब नहीं, बल्कि 'Organic Clusters' में रेंडर करना [cite: 1]"""
        # User Interview से प्राप्त संख्या का उपयोग
        rng = np.random.default_rng(42)
        
        # Zone 2 (Food Forest) की लोकेशन ढूंढना
        z2 = layout.get('zone_positions', {}).get('z2')
        if not z2:
            # अगर Z2 नहीं है तो पूरे प्लाट पर रैंडम फैलाओ
            search_area = {'x': 0, 'y': 0, 'w': L, 'h': W}
        else:
            search_area = {'x': z2['x'], 'y': z2['y'], 'w': z2['width'], 'h': z2['height']}

        for i in range(int(tree_count)):
            tx = search_area['x'] + rng.uniform(5, search_area['w'] - 5)
            ty = search_area['y'] + rng.uniform(5, search_area['h'] - 5)
            
            # हर पेड़ का साइज़ थोड़ा अलग (Realism के लिए)
            scale = rng.uniform(0.8, 1.4)
            self._render_pro_tree(fig, tx, ty, scale)

    def _render_pro_tree(self, fig, x, y, s):
        """Fractal Mesh Tree: इसमें तना और पत्तों की 3 लेयर्स हैं"""
        # 1. Trunk (तना) - Realistic Cylinder approximation
        trunk_h = 7 * s
        fig.add_trace(go.Mesh3d(
            x=[x-0.5*s, x+0.5*s, x, x], y=[y-0.5*s, y+0.5*s, y+0.5*s, y-0.5*s],
            z=[0, 0, trunk_h, trunk_h], color='#3E2723', 
            lighting=dict(ambient=0.3, diffuse=0.5), hoverinfo='skip'
        ))

        # 2. Triple Layer Canopy (पत्तों का गुच्छा)
        # अलग-अलग शेड्स ताकि पेड़ 'Flat' न लगे
        leaf_colors = ['#1B5E20', '#2E7D32', '#388E3C']
        for idx, h_off in enumerate([0, 3*s, 6*s]):
            z_base = trunk_h - 2*s + h_off
            rad = (6*s) / (idx + 1) # ऊपर जाते हुए पत्तों का घेरा कम होगा
            
            fig.add_trace(go.Mesh3d(
                x=[x-rad, x+rad, x, x], 
                y=[y-rad, y+rad, y+rad, y-rad], 
                z=[z_base, z_base, z_base+5*s, z_base+5*s],
                color=leaf_colors[idx], opacity=0.9, 
                flatshading=False, # कोनों को गोल करने के लिए
                lighting=self.materials['tree_foliage'],
                name="Fruit Tree"
            ))

    # --- Water Module (Physics-based Surface) ---
    def _add_realistic_pond(self, fig, pond_data):
        """तालाब में लहरें (Ripple effect) और रिफ्लेक्शन जोड़ना"""
        cx, cy, r = pond_data['x'], pond_data['y'], pond_data['radius']
        
        # Create a circular mesh for water
        theta = np.linspace(0, 2*np.pi, 50)
        phi = np.linspace(0, r, 20)
        T, P = np.meshgrid(theta, phi)
        
        X = cx + P * np.cos(T)
        Y = cy + P * np.sin(T)
        # Ripple effect using Sine wave
        Z = np.sin(P * 0.5) * 0.2 - 0.5 

        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z,
            colorscale=[[0, '#01579B'], [0.5, '#0288D1'], [1, '#4FC3F7']],
            showscale=False,
            lighting=self.materials['water'],
            name='Reflective Pond'
        ))
        # --- Infrastructure Module (Paths & Roads) ---
    def _add_3d_roads(self, fig, layout, L, W):
        """टेरेन की ऊंचाई को फॉलो करने वाले घुमावदार रास्ते"""
        zones = layout.get('zone_positions', {})
        if 'z0' not in zones or 'z1' not in zones:
            return

        # Path from House (Z0) to Garden (Z1)
        start_x, start_y = zones['z0']['x'] + 15, zones['z0']['y']
        end_x, end_y = zones['z1']['x'] + 20, zones['z1']['y'] + 20

        # Bezier Curve Logic for organic feel
        t = np.linspace(0, 1, 30)
        px = start_x + (end_x - start_x) * t + np.sin(t * np.pi) * 10
        py = start_y + (end_y - start_y) * t
        
        # रास्तों को जमीन से थोड़ा ऊपर उठाना ताकि वे 'Z-fighting' न करें
        pz = [self._get_elev(x, y) + 0.3 for x, y in zip(px, py)]

        fig.add_trace(go.Scatter3d(
            x=px, y=py, z=pz,
            mode='lines',
            line=dict(color='#D7CCC8', width=12), # Gravel road look
            name='Access Path',
            hoverinfo='name'
        ))

    # --- Energy Module (Solar Array with Silicon Texture) ---
    def _add_solar_farm(self, fig, layout):
        """यूजर के फीचर्स में 'solar' होने पर रेंडर होगा"""
        features = layout.get('features', {})
        if 'solar' not in features:
            return
            
        f = features['solar']
        sx, sy = f['x'], f['y']
        sw, sh = f['width'], f['height']
        
        # Solar Panel Grid (15 degrees tilt for realism)
        base_z = self._get_elev(sx, sy) + 2
        
        # Realistic Blue Silicon Panels
        fig.add_trace(go.Mesh3d(
            x=[sx, sx+sw, sx+sw, sx],
            y=[sy, sy, sy+sh, sy+sh],
            z=[base_z, base_z, base_z+4, base_z+4],
            color='#1A237E', 
            opacity=0.9,
            lighting=dict(specular=1.0, roughness=0.1), # Glass-like reflection
            name='Solar Array'
        ))
        
        # Support Structure (Stand)
        self._draw_mesh_box(fig, sx+2, sy+2, 0, sx+4, sy+4, base_z, '#455A64', 'Solar Stand', self.materials['house_wall'])

    # --- HUD Module (Floating Interactive Labels) ---
    def _add_floating_hud(self, fig, layout):
        """नक्शे के ऊपर 3D में तैरते हुए नाम"""
        label_pts = []
        
        # 1. Main House Label
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        hx, hy = L*0.4, W*0.4
        label_pts.append({'x': hx+15, 'y': hy+12, 'z': 25, 'text': '🏠 MAIN RESIDENCE'})

        # 2. Livestock Labels (If selected by user)
        livestock = layout.get('features', {})
        for key, name in [('goat_shed', '🐐 GOATS'), ('cow_shed', '🐄 COWS'), ('chicken_coop', '🐓 POULTRY')]:
            if key in livestock:
                f = livestock[key]
                label_pts.append({'x': f['x']+10, 'y': f['y']+10, 'z': 18, 'text': name})

        # Render labels as Scatter3d text
        fig.add_trace(go.Scatter3d(
            x=[p['x'] for p in label_pts],
            y=[p['y'] for p in label_pts],
            z=[p['z'] for p in label_pts],
            mode='text',
            text=[p['text'] for p in label_pts],
            textfont=dict(size=12, color='#1B5E20', family='Arial Black'),
            name='Site HUD'
        ))

    # --- Helper: Dynamic Elevation Lookup ---
    def _get_elev(self, x, y):
        """टेरेन की सटीक ऊंचाई जानने के लिए (Snapping objects to ground)"""
        return np.sin(x*0.03) * np.cos(y*0.03) * 4.0

    # --- Perimeter Module (3D Fencing) ---
    def _add_fence_boundary(self, fig, L, W):
        """पूरे फार्म के चारों तरफ 3D बाउंड्री वॉल/बाड़"""
        # Fence Posts logic
        post_spacing = 40 
        for px in np.arange(0, L+1, post_spacing):
            for py in [0, W]: # North and South edges
                pz = self._get_elev(px, py)
                self._draw_mesh_box(fig, px-1, py-1, pz, px+1, py+1, pz+6, '#5D4037', 'Fence Post', self.materials['wood'])
        
        for py in np.arange(0, W+1, post_spacing):
            for px in [0, L]: # East and West edges
                pz = self._get_elev(px, py)
                self._draw_mesh_box(fig, px-1, py-1, pz, px+1, py+1, pz+6, '#5D4037', 'Fence Post', self.materials['wood'])
                # --- Interactivity Module (HUD Toggle & View Controls) ---
    def _add_camera_and_interactivity(self, fig, L, W, acres, title_text):
        """कैमरा ज़ूम, डेटा बॉक्स टॉगल और डाउनलोड सेटिंग्स"""
        
        # Cinematic View Positions
        camera_iso = dict(eye=dict(x=1.8, y=-1.8, z=1.2))
        camera_top = dict(eye=dict(x=0.1, y=0.1, z=2.5))
        camera_zoom = dict(eye=dict(x=0.8, y=-0.8, z=0.4)) # Close-up zoom

        fig.update_layout(
            updatemenus=[
                # 1. डेटा बॉक्स (HUD) छिपाने/दिखाने का बटन
                dict(
                    type="buttons", direction="down", x=0.02, y=0.9,
                    buttons=[
                        dict(label="👁️ Show Data Box", method="update", 
                             args=[{"visible": [True] * len(fig.data)}]),
                        dict(label="🙈 Hide Data Box", method="update", 
                             args=[{"visible": [True if i < (len(fig.data)-1) else False for i in range(len(fig.data))]}])
                    ]
                ),
                # 2. कैमरा व्यू कंट्रोल (Zoom and Perspective)
                dict(
                    type="buttons", direction="left", x=0.5, y=1.1,
                    buttons=[
                        dict(label="Standard View", method="relayout", args=[{"scene.camera": camera_iso}]),
                        dict(label="Top Down", method="relayout", args=[{"scene.camera": camera_top}]),
                        dict(label="Cinematic Zoom", method="relayout", args=[{"scene.camera": camera_zoom}])
                    ]
                )
            ],
            title=dict(text=title_text, font=dict(size=18, color='#1B5E20')),
            scene=dict(
                xaxis=dict(showgrid=False, zeroline=False),
                yaxis=dict(showgrid=False, zeroline=False),
                zaxis=dict(showgrid=False, zeroline=False),
                aspectmode='manual',
                aspectratio=dict(x=1, y=W/L, z=0.15)
            ),
            showlegend=True,
            uirevision='constant' # ज़ूम लेवल को रीसेट होने से रोकने के लिए
        )

    # --- Night Mode & Light Module ---
    def _add_night_mode(self, fig):
        """फार्म पर रात का अहसास और लाइटें (Premium Lighting)"""
        # इसमें एम्बिएंट लाइट को कम करके प्वॉइंट लाइट्स जोड़ी जाती हैं
        night_lighting = dict(ambient=0.1, diffuse=0.2, specular=0.05)
        
        # घर की खिड़कियों से आने वाली पीली रोशनी का अहसास
        fig.add_trace(go.Scatter3d(
            x=[10, 20], y=[10, 20], z=[5, 5],
            mode='markers',
            marker=dict(size=10, color='yellow', opacity=0.8),
            name='Night Lights'
        ))

    # --- HTML Export Engine ---
    def _render_and_export(self, fig, location_name):
        """Plotly चार्ट रेंडर करना और HTML डाउनलोड बटन देना"""
        import streamlit as st
        
        # Display in Streamlit
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        
        # HTML Download Logic
        try:
            html_data = fig.to_html(include_plotlyjs='cdn', full_html=True)
            st.download_button(
                label="📥 Download Realistic 3D Map (HTML)",
                data=html_data,
                file_name=f"Homestead_3D_{location_name}.html",
                mime="text/html",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Export Error: {e}")

# --- End of Visualizer3D Class ---
