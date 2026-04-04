
"""
Homestead Architect Pro 2026 — v3.2 HTML 3D EDITION
Full-screen HTML renderer with download button
"""

import streamlit as st
import sys
import io
import json
import base64
from pathlib import Path

# Path configuration
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / 'core'))

# Core imports
try:
    from core.user_interview import UserInterview
    from core.layout_engine import LayoutEngine
    from core.livestock_designer import LivestockDesigner
    from core.cost_calculator import CostCalculator
    from core.climate_engine import ClimateEngine
    from core.visualizer_2d import Visualizer2D
    from core.watermark_system import WatermarkEngine
    from core.pdf_generator import PDFGenerator
except ImportError as e:
    st.error(f"Core module error: {e}")
    st.stop()

# Page Configuration
st.set_page_config(
    page_title='Homestead Architect Pro 2026',
    page_icon='🏡',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Custom Styling
st.markdown("""
<style>
.main-header {
    font-size: 2.8rem;
    font-weight: 800;
    color: #1B5E20;
    text-align: center;
    margin-bottom: 0.5rem;
}
.sub-header {
    font-size: 1.2rem;
    color: #555;
    text-align: center;
    margin-bottom: 2rem;
}
.success-box {
    background: linear-gradient(135deg, #C8E6C9 0%, #A5D6A7 100%);
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #2E7D32;
    margin: 10px 0;
}
.download-btn {
    background: #1976D2;
    color: white;
    padding: 12px 24px;
    border-radius: 8px;
    text-decoration: none;
    display: inline-block;
    margin: 10px 5px;
    font-weight: 600;
}
.download-btn:hover {
    background: #1565C0;
}
</style>
""", unsafe_allow_html=True)


def generate_3d_html(layout_data):
    """Generate full HTML with Three.js for realistic 3D rendering"""
    
    if not layout_data or 'dimensions' not in layout_data:
        return None
    
    L = layout_data['dimensions']['L']
    W = layout_data['dimensions']['W']
    acres = layout_data.get('acres', round(L * W / 43560, 2))
    
    # Extract features
    features = layout_data.get('features', {})
    zones = layout_data.get('zone_positions', {})
    
    # Generate objects JSON for Three.js
    objects_json = []
    
    # Terrain
    objects_json.append({
        'type': 'terrain',
        'width': L,
        'depth': W,
        'color': '#81C784'
    })
    
    # House
    if 'house_position' in layout_data:
        house_pos = layout_data['house_position']
        positions = {
            'North': {'x': L*0.3, 'z': W*0.75},
            'South': {'x': L*0.3, 'z': W*0.15},
            'East': {'x': L*0.7, 'z': W*0.4},
            'West': {'x': L*0.1, 'z': W*0.4},
            'Center': {'x': L*0.4, 'z': W*0.4}
        }
        pos = positions.get(house_pos, positions['Center'])
        objects_json.append({
            'type': 'house',
            'x': pos['x'],
            'z': pos['z'],
            'width': 30,
            'depth': 40,
            'height': 12,
            'color': '#8D6E63',
            'roofColor': '#4E342E'
        })
    
    # Trees in Zone 2
    if 'z2' in zones:
        z2 = zones['z2']
        tree_positions = [
            (0.2, 0.3), (0.5, 0.5), (0.8, 0.4),
            (0.3, 0.7), (0.7, 0.2), (0.6, 0.8)
        ]
        colors = ['#2E7D32', '#388E3C', '#1B5E20', '#43A047', '#66BB6A', '#33691E']
        for i, (rx, rz) in enumerate(tree_positions):
            tx = z2['x'] + rx * z2['width']
            tz = z2['y'] + rz * z2['height']
            objects_json.append({
                'type': 'tree',
                'x': tx,
                'z': tz,
                'height': 25 + (i % 3) * 10,
                'color': colors[i % 6]
            })
    
    # Livestock
    livestock_items = [
        ('goat_shed', '#FFCCBC', 'Goat Shed'),
        ('chicken_coop', '#FFF9C4', 'Chicken Coop'),
        ('piggery', '#F8BBD0', 'Piggery'),
        ('cow_shed', '#D7CCC8', 'Cow Shed')
    ]
    
    for key, color, name in livestock_items:
        if key in features:
            f = features[key]
            objects_json.append({
                'type': 'shed',
                'x': f['x'],
                'z': f['y'],
                'width': f['width'],
                'depth': f['height'],
                'height': 8,
                'color': color,
                'name': name
            })
    
    # Pond
    if 'pond' in features:
        f = features['pond']
        objects_json.append({
            'type': 'pond',
            'x': f['x'],
            'z': f['y'],
            'radius': f['radius'],
            'color': '#4FC3F7'
        })
    
    # Well
    if 'well' in features:
        f = features['well']
        objects_json.append({
            'type': 'well',
            'x': f['x'],
            'z': f['y'],
            'radius': f.get('radius', 4),
            'color': '#546E7A'
        })
    
    # Solar
    if 'solar' in features:
        f = features['solar']
        objects_json.append({
            'type': 'solar',
            'x': f['x'],
            'z': f['y'],
            'width': f['width'],
            'depth': f['height'],
            'color': '#1565C0'
        })
    
    objects_json_str = json.dumps(objects_json)
    
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Homestead 3D View - {acres:.2f} acres</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background: #87CEEB; font-family: Arial, sans-serif; }}
        #canvas-container {{ width: 100vw; height: 100vh; }}
        #info {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(255,255,255,0.9);
            padding: 15px;
            border-radius: 8px;
            font-size: 14px;
            max-width: 250px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }}
        #controls {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(255,255,255,0.9);
            padding: 10px;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        button {{
            padding: 8px 12px;
            cursor: pointer;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 12px;
        }}
        button:hover {{ background: #45a049; }}
        .legend-item {{ display: flex; align-items: center; margin: 3px 0; }}
        .legend-color {{ width: 15px; height: 15px; margin-right: 8px; border-radius: 3px; }}
    </style>
</head>
<body>
    <div id="canvas-container"></div>
    <div id="info">
        <h3>🏡 Homestead 3D</h3>
        <p><strong>{acres:.2f} acres</strong></p>
        <p>{int(L)} × {int(W)} ft</p>
        <hr style="margin: 10px 0;">
        <div class="legend-item"><div class="legend-color" style="background:#8D6E63;"></div>House</div>
        <div class="legend-item"><div class="legend-color" style="background:#2E7D32;"></div>Trees</div>
        <div class="legend-item"><div class="legend-color" style="background:#4FC3F7;"></div>Pond</div>
        <div class="legend-item"><div class="legend-color" style="background:#FFCCBC;"></div>Livestock</div>
        <div class="legend-item"><div class="legend-color" style="background:#1565C0;"></div>Solar</div>
    </div>
    <div id="controls">
        <button onclick="resetCamera()">🏠 Reset View</button>
        <button onclick="topView()">⬇️ Top View</button>
        <button onclick="toggleRotation()">🔄 Auto Rotate</button>
    </div>

    <script>
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x87CEEB);
        scene.fog = new THREE.Fog(0x87CEEB, 100, 500);
        
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 1000);
        camera.position.set({L*0.8}, {W*0.8}, {max(L,W)*0.5});
        
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.getElementById('canvas-container').appendChild(renderer.domElement);
        
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.maxPolarAngle = Math.PI / 2 - 0.1;
        
        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);
        
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(100, 200, 100);
        dirLight.castShadow = true;
        dirLight.shadow.camera.left = -200;
        dirLight.shadow.camera.right = 200;
        dirLight.shadow.camera.top = 200;
        dirLight.shadow.camera.bottom = -200;
        dirLight.shadow.mapSize.width = 2048;
        dirLight.shadow.mapSize.height = 2048;
        scene.add(dirLight);
        
        // Ground
        const groundGeometry = new THREE.PlaneGeometry({L*1.2}, {W*1.2});
        const groundMaterial = new THREE.MeshLambertMaterial({{ color: 0x90EE90 }});
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        scene.add(ground);
        
        // Grid
        const gridHelper = new THREE.GridHelper({max(L,W)}, 20, 0x555555, 0x888888);
        scene.add(gridHelper);
        
        // Objects
        const objects = {objects_json_str};
        
        objects.forEach(obj => {{
            if (obj.type === 'terrain') {{
                // Already created ground
            }} else if (obj.type === 'house') {{
                // House body
                const geometry = new THREE.BoxGeometry(obj.width, obj.height, obj.depth);
                const material = new THREE.MeshLambertMaterial({{ color: obj.color }});
                const mesh = new THREE.Mesh(geometry, material);
                mesh.position.set(obj.x + obj.width/2, obj.height/2, obj.z + obj.depth/2);
                mesh.castShadow = true;
                mesh.receiveShadow = true;
                scene.add(mesh);
                
                // Roof
                const roofGeometry = new THREE.ConeGeometry(Math.max(obj.width, obj.depth)*0.7, 8, 4);
                const roofMaterial = new THREE.MeshLambertMaterial({{ color: obj.roofColor }});
                const roof = new THREE.Mesh(roofGeometry, roofMaterial);
                roof.position.set(obj.x + obj.width/2, obj.height + 4, obj.z + obj.depth/2);
                roof.rotation.y = Math.PI / 4;
                roof.castShadow = true;
                scene.add(roof);
                
            }} else if (obj.type === 'tree') {{
                // Trunk
                const trunkGeo = new THREE.CylinderGeometry(1, 1.5, obj.height*0.3, 8);
                const trunkMat = new THREE.MeshLambertMaterial({{ color: 0x8D6E63 }});
                const trunk = new THREE.Mesh(trunkGeo, trunkMat);
                trunk.position.set(obj.x, obj.height*0.15, obj.z);
                trunk.castShadow = true;
                scene.add(trunk);
                
                // Canopy
                const canopyGeo = new THREE.SphereGeometry(obj.height*0.25, 16, 16);
                const canopyMat = new THREE.MeshLambertMaterial({{ color: obj.color }});
                const canopy = new THREE.Mesh(canopyGeo, canopyMat);
                canopy.position.set(obj.x, obj.height*0.6, obj.z);
                canopy.castShadow = true;
                scene.add(canopy);
                
            }} else if (obj.type === 'shed') {{
                const geometry = new THREE.BoxGeometry(obj.width, obj.height, obj.depth);
                const material = new THREE.MeshLambertMaterial({{ color: obj.color }});
                const mesh = new THREE.Mesh(geometry, material);
                mesh.position.set(obj.x + obj.width/2, obj.height/2, obj.z + obj.depth/2);
                mesh.castShadow = true;
                scene.add(mesh);
                
            }} else if (obj.type === 'pond') {{
                const geometry = new THREE.CircleGeometry(obj.radius, 32);
                const material = new THREE.MeshLambertMaterial({{ 
                    color: obj.color, 
                    transparent: true, 
                    opacity: 0.8 
                }});
                const mesh = new THREE.Mesh(geometry, material);
                mesh.rotation.x = -Math.PI / 2;
                mesh.position.set(obj.x, 0.2, obj.z);
                scene.add(mesh);
                
            }} else if (obj.type === 'well') {{
                const geometry = new THREE.CylinderGeometry(obj.radius, obj.radius, 6, 16);
                const material = new THREE.MeshLambertMaterial({{ color: obj.color }});
                const mesh = new THREE.Mesh(geometry, material);
                mesh.position.set(obj.x, 3, obj.z);
                mesh.castShadow = true;
                scene.add(mesh);
                
            }} else if (obj.type === 'solar') {{
                const geometry = new THREE.BoxGeometry(obj.width, 1, obj.depth);
                const material = new THREE.MeshLambertMaterial({{ color: obj.color }});
                const mesh = new THREE.Mesh(geometry, material);
                mesh.position.set(obj.x + obj.width/2, 4, obj.z + obj.depth/2);
                mesh.rotation.x = -0.2;
                mesh.castShadow = true;
                scene.add(mesh);
            }}
        }});
        
        let autoRotate = false;
        
        function animate() {{
            requestAnimationFrame(animate);
            if (autoRotate) {{
                controls.autoRotate = true;
            }} else {{
                controls.autoRotate = false;
            }}
            controls.update();
            renderer.render(scene, camera);
        }}
        
        function resetCamera() {{
            camera.position.set({L*0.8}, {W*0.8}, {max(L,W)*0.5});
            controls.target.set({L/2}, 0, {W/2});
        }}
        
        function topView() {{
            camera.position.set({L/2}, {max(L,W)*1.2}, {W/2});
            controls.target.set({L/2}, 0, {W/2});
        }}
        
        function toggleRotation() {{
            autoRotate = !autoRotate;
        }}
        
        // Handle resize
        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
        
        animate();
    </script>
</body>
</html>
"""
    return html_template


def main():
    # Header
    st.markdown('<p class="main-header">🏡 Homestead Architect Pro</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Design Your Dream Homestead with Realistic 3D Visualization | 2026 Edition</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title('⚙️ Configuration')
        watermark_enabled = st.checkbox('☑️ Enable Watermark', value=True)
        st.divider()
        st.markdown("**Made by: Chundal Gardens**")
        st.markdown("🌐 chundalgardens.com")
    
    # Tabs
    tabs = st.tabs(['🎨 Design Studio', '🌐 Realistic 3D View', '🐑 Livestock', '💰 Costs', '📥 Export'])
    
    with tabs[0]: 
        design_tab(watermark_enabled)
    with tabs[1]: 
        view_3d_tab()
    with tabs[2]: 
        livestock_tab()
    with tabs[3]: 
        costs_tab()
    with tabs[4]: 
        download_tab(watermark_enabled)


def design_tab(watermark_enabled):
    """Design tab"""
    st.header('🎨 Smart Homestead Designer')
    
    interview = UserInterview()
    answers = interview.run()
    
    if not answers:
        return
    
    st.markdown('<div class="success-box">✅ Generating your custom design...</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        with st.spinner('Rendering...'):
            engine = LayoutEngine()
            layout = engine.generate(answers)
            
            viz = Visualizer2D()
            raw_map = viz.create(layout, answers)
            
            raw_map.seek(0)
            st.session_state['raw_map'] = io.BytesIO(raw_map.read())
            
            raw_map.seek(0)
            if watermark_enabled:
                display_map = WatermarkEngine.apply_visible_watermark(raw_map)
            else:
                display_map = WatermarkEngine.apply_protection_watermark(raw_map)
            
            st.image(display_map, use_column_width=True)
            st.session_state['current_map'] = display_map
            st.session_state['layout_data'] = layout
            st.session_state['answers'] = answers
    
    with col2:
        if 'layout_data' in st.session_state:
            ld = st.session_state['layout_data']
            st.metric('Area', f"{ld.get('acres', 0):.2f} acres")
            st.metric('Size', f"{int(ld.get('dimensions', {}).get('L', 0))} × {int(ld.get('dimensions', {}).get('W', 0))} ft")


def view_3d_tab():
    """3D view with HTML renderer and download button"""
    st.header('🌐 Realistic 3D Cinematic View')
    
    if 'layout_data' not in st.session_state:
        st.warning('👈 Generate a design in Design Studio tab first!')
        return
    
    layout_data = st.session_state['layout_data']
    acres = layout_data.get('acres', 0)
    
    st.markdown(f'<div class="success-box">🎯 Rendering {acres:.2f} acres in REALISTIC 3D | Full HTML Engine</div>', unsafe_allow_html=True)
    
    # Generate HTML
    html_content = generate_3d_html(layout_data)
    
    if html_content:
        # Download button for HTML
        b64 = base64.b64encode(html_content.encode()).decode()
        href = f'<a href="data:text/html;base64,{b64}" download="homestead_3d_{acres:.1f}acres.html" class="download-btn">📥 Download 3D HTML File</a>'
        st.markdown(href, unsafe_allow_html=True)
        
        st.info("💡 Tip: Download the HTML file to view in full screen on any device!")
        
        # Render 3D
        st.components.v1.html(html_content, height=800, scrolling=False)
    else:
        st.error("Failed to generate 3D view")


def livestock_tab():
    """Livestock tab"""
    st.header('🐑 Livestock Housing Designer')
    designer = LivestockDesigner()
    
    col1, col2 = st.columns(2)
    with col1:
        animal = st.selectbox('Animal', ['Goats', 'Chickens', 'Pigs', 'Cows'])
        count = st.number_input('Count', 1, 1000, 10)
    with col2:
        climate = st.selectbox('Climate', ['Tropical', 'Dry', 'Temperate', 'Cold'])
        budget = st.selectbox('Budget', ['Basic', 'Standard', 'Premium'])
    
    if st.button('Generate Housing Plan', use_container_width=True):
        with st.spinner('Designing...'):
            design = designer.create_housing(animal, count, climate, budget)
            st.image(design['floor_plan'], use_column_width=True)
            st.write(design['specs'])


def costs_tab():
    """Costs tab"""
    st.header('💰 Global Investment Calculator')
    calc = CostCalculator()
    
    country = st.selectbox('Country', ['USA', 'India', 'UK', 'Canada'])
    currency = st.selectbox('Currency', ['USD', 'INR', 'EUR', 'GBP'])
    size = st.selectbox('Farm Size', ['Small', 'Medium', 'Large'])
    
    if st.button('Calculate Investment'):
        costs = calc.estimate(country, currency, size)
        st.metric('Setup Cost', costs['setup_min'])


def download_tab(watermark_enabled):
    """Download tab"""
    st.header('📥 Export Your Plan')
    
    if 'current_map' not in st.session_state:
        st.warning('Generate a design first!')
        return
    
    buf = st.session_state['current_map']
    buf.seek(0)
    st.download_button('Download Site Map (PNG)', data=buf, file_name='homestead_plan.png', mime='image/png')


if __name__ == '__main__':
    main()
