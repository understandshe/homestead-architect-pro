"""
Homestead Architect Pro 2026 - PREMIUM 3D EDITION
Ultimate Three.js Renderer with PBR, Shadows, Animations, Cinematic Camera
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import base64
from typing import Dict, Any, List

class PremiumVisualizer3D:
    """
    Premium 3D visualization using Three.js
    Features: PBR materials, dynamic shadows, animated elements, cinematic camera
    """
    
    def create(self, layout: Dict[str, Any], user_models: List[str] = None):
        """Render premium 3D scene"""
        if not layout or 'dimensions' not in layout:
            st.info("Please generate a design in the Design tab first.")
            return
        
        L = layout['dimensions']['L']
        W = layout['dimensions']['W']
        acres = layout.get('acres', round(L * W / 43560, 2))
        loc_name = layout.get('location', 'Custom Plot')
        
        # UI Controls
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            st.subheader(f"Premium 3D View: {loc_name} - {acres:.2f} acres")
        
        with col2:
            camera_mode = st.selectbox(
                "Camera View",
                ["Isometric", "Top Down", "North View", "South View", "Cinematic Tour"],
                key="cam_mode"
            )
        
        with col3:
            show_legend = st.toggle("Show Legend", value=False, key="legend_toggle")
        
        with col4:
            auto_rotate = st.toggle("Auto Rotate", value=False, key="auto_rotate")
        
        # Generate Three.js HTML
        html_scene = self._generate_threejs_scene(layout, camera_mode, show_legend, auto_rotate)
        
        # Render
        components.html(html_scene, height=850, scrolling=False)
        
        # Download button
        b64 = base64.b64encode(html_scene.encode()).decode()
        href = f'<a href="data:text/html;base64,{b64}" download="premium_homestead_{acres:.1f}acres.html" style="text-decoration:none; background:#1976D2; color:white; padding:12px 24px; border-radius:8px; display:inline-block; margin-top:10px; font-weight:600;">Download Premium 3D HTML</a>'
        st.markdown(href, unsafe_allow_html=True)
    
    def _generate_threejs_scene(self, layout, camera_mode, show_legend, auto_rotate):
        """Generate complete Three.js HTML with all premium features"""
        
        L = layout['dimensions']['L']
        W = layout['dimensions']['W']
        features = layout.get('features', {})
        zones = layout.get('zone_positions', {})
        acres = layout.get('acres', round(L * W / 43560, 2))
        
        # Build scene objects
        scene_objects = self._build_scene_objects(layout, L, W, features, zones)
        
        # Camera configuration
        camera_config = self._get_camera_config(camera_mode, L, W)
        
        # Generate HTML
        legend_display = "block" if show_legend else "none"
        auto_rotate_str = str(auto_rotate).lower()
        
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Premium Homestead 3D - {acres:.2f} acres</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; overflow: hidden; background: linear-gradient(135deg, #87CEEB 0%, #E0F6FF 100%); }}
        #canvas-container {{ width: 100vw; height: 100vh; position: relative; }}
        .hud {{ position: absolute; top: 20px; left: 20px; background: rgba(255, 255, 255, 0.95); padding: 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); min-width: 220px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.5); }}
        .hud h2 {{ margin: 0 0 12px 0; color: #1B5E20; font-size: 18px; font-weight: 700; letter-spacing: 0.5px; }}
        .hud .stat {{ display: flex; justify-content: space-between; margin: 8px 0; font-size: 14px; color: #444; }}
        .hud .stat-value {{ font-weight: 600; color: #2E7D32; }}
        .legend {{ position: absolute; top: 20px; right: 20px; background: rgba(255, 255, 255, 0.95); padding: 15px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); display: {legend_display}; backdrop-filter: blur(10px); }}
        .legend h3 {{ margin: 0 0 10px 0; color: #333; font-size: 14px; font-weight: 600; }}
        .legend-item {{ display: flex; align-items: center; margin: 6px 0; font-size: 13px; color: #555; }}
        .legend-color {{ width: 16px; height: 16px; margin-right: 10px; border-radius: 3px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
        .controls {{ position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%); display: flex; gap: 12px; background: rgba(255, 255, 255, 0.95); padding: 15px 25px; border-radius: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); backdrop-filter: blur(10px); }}
        .control-btn {{ padding: 10px 20px; border: none; border-radius: 20px; background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%); color: white; font-weight: 600; cursor: pointer; transition: all 0.3s ease; font-size: 13px; letter-spacing: 0.5px; }}
        .control-btn:hover {{ transform: translateY(-2px); box-shadow: 0 6px 15px rgba(76, 175, 80, 0.4); }}
        .control-btn.secondary {{ background: linear-gradient(135deg, #757575 0%, #424242 100%); }}
        .control-btn.secondary:hover {{ box-shadow: 0 6px 15px rgba(117, 117, 117, 0.4); }}
        #loading {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(135deg, #87CEEB 0%, #E0F6FF 100%); display: flex; align-items: center; justify-content: center; z-index: 1000; transition: opacity 0.5s ease; }}
        .loader {{ width: 60px; height: 60px; border: 4px solid rgba(255,255,255,0.3); border-top-color: #2E7D32; border-radius: 50%; animation: spin 1s linear infinite; }}
        @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    </style>
</head>
<body>
    <div id="loading"><div class="loader"></div></div>
    <div id="canvas-container"></div>
    <div class="hud">
        <h2>Homestead Pro</h2>
        <div class="stat"><span>Area:</span><span class="stat-value">{acres:.2f} acres</span></div>
        <div class="stat"><span>Dimensions:</span><span class="stat-value">{int(L)} x {int(W)} ft</span></div>
        <div class="stat"><span>Scale:</span><span class="stat-value">1:100</span></div>
    </div>
    <div class="legend" id="legend">
        <h3>Map Legend</h3>
        <div class="legend-item"><div class="legend-color" style="background: #8D6E63;"></div><span>Main House</span></div>
        <div class="legend-item"><div class="legend-color" style="background: #2E7D32;"></div><span>Trees</span></div>
        <div class="legend-item"><div class="legend-color" style="background: #4FC3F7;"></div><span>Water Body</span></div>
        <div class="legend-item"><div class="legend-color" style="background: #FFCCBC;"></div><span>Livestock</span></div>
        <div class="legend-item"><div class="legend-color" style="background: #1565C0;"></div><span>Solar Array</span></div>
    </div>
    <div class="controls">
        <button class="control-btn" onclick="resetCamera()">Reset View</button>
        <button class="control-btn" onclick="toggleRotation()">Auto Rotate</button>
        <button class="control-btn secondary" onclick="toggleShadows()">Toggle Shadows</button>
        <button class="control-btn secondary" onclick="cinematicTour()">Cinematic Tour</button>
    </div>
    <script>
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x87CEEB);
        scene.fog = new THREE.Fog(0x87CEEB, 200, 800);
        
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 0.1, 2000);
        camera.position.set({camera_config['x']}, {camera_config['y']}, {camera_config['z']});
        
        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.outputEncoding = THREE.sRGBEncoding;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.2;
        document.getElementById("canvas-container").appendChild(renderer.domElement);
        
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.maxPolarAngle = Math.PI / 2 - 0.05;
        controls.minDistance = 50;
        controls.maxDistance = 1000;
        
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
        scene.add(ambientLight);
        
        const sunLight = new THREE.DirectionalLight(0xfff4e5, 1.2);
        sunLight.position.set(200, 300, 150);
        sunLight.castShadow = true;
        sunLight.shadow.mapSize.width = 2048;
        sunLight.shadow.mapSize.height = 2048;
        sunLight.shadow.camera.near = 0.5;
        sunLight.shadow.camera.far = 1000;
        sunLight.shadow.camera.left = -400;
        sunLight.shadow.camera.right = 400;
        sunLight.shadow.camera.top = 400;
        sunLight.shadow.camera.bottom = -400;
        sunLight.shadow.bias = -0.0005;
        scene.add(sunLight);
        
        const fillLight = new THREE.DirectionalLight(0xcce0ff, 0.4);
        fillLight.position.set(-200, 100, -200);
        scene.add(fillLight);
        
        const groundGeometry = new THREE.PlaneGeometry({L * 1.5}, {W * 1.5}, 64, 64);
        const positions = groundGeometry.attributes.position;
        for (let i = 0; i < positions.count; i++) {{
            const x = positions.getX(i);
            const y = positions.getY(i);
            const z = Math.sin(x * 0.02) * 3 + Math.cos(y * 0.02) * 3 + Math.random() * 0.5;
            positions.setZ(i, z);
        }}
        groundGeometry.computeVertexNormals();
        
        const groundMaterial = new THREE.MeshStandardMaterial({{ color: 0x7cb342, roughness: 0.9, metalness: 0.0 }});
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        scene.add(ground);
        
        const gridHelper = new THREE.GridHelper(Math.max({L}, {W}), 20, 0x444444, 0x888888);
        gridHelper.position.y = 0.1;
        gridHelper.material.opacity = 0.3;
        gridHelper.material.transparent = true;
        scene.add(gridHelper);
        
        const objects = {scene_objects};
        const animatedObjects = [];
        
        objects.forEach(obj => {{
            if (obj.type === "house") {{
                const houseGroup = new THREE.Group();
                const foundationGeo = new THREE.BoxGeometry(obj.width + 2, 1, obj.depth + 2);
                const foundationMat = new THREE.MeshStandardMaterial({{ color: 0x9e9e9e, roughness: 0.9 }});
                const foundation = new THREE.Mesh(foundationGeo, foundationMat);
                foundation.position.y = 0.5;
                foundation.castShadow = true;
                foundation.receiveShadow = true;
                houseGroup.add(foundation);
                
                const wallGeo = new THREE.BoxGeometry(obj.width, obj.height, obj.depth);
                const wallMat = new THREE.MeshStandardMaterial({{ color: 0x8d6e63, roughness: 0.8 }});
                const walls = new THREE.Mesh(wallGeo, wallMat);
                walls.position.y = obj.height / 2 + 1;
                walls.castShadow = true;
                walls.receiveShadow = true;
                houseGroup.add(walls);
                
                const roofHeight = 8;
                const roofGeo = new THREE.ConeGeometry(Math.max(obj.width, obj.depth) * 0.7, roofHeight, 4);
                const roofMat = new THREE.MeshStandardMaterial({{ color: 0x4e342e, roughness: 0.7, metalness: 0.1 }});
                const roof = new THREE.Mesh(roofGeo, roofMat);
                roof.position.y = obj.height + 1 + roofHeight / 2;
                roof.rotation.y = Math.PI / 4;
                roof.castShadow = true;
                houseGroup.add(roof);
                
                houseGroup.position.set(obj.x, 0, obj.z);
                scene.add(houseGroup);
                createLabel(obj.x, obj.height + 15, obj.z, "Main House");
            }}
        }});
        
        function createLabel(x, y, z, text) {{
            const canvas = document.createElement("canvas");
            const context = canvas.getContext("2d");
            canvas.width = 256;
            canvas.height = 64;
            context.fillStyle = "rgba(255, 255, 255, 0.9)";
            context.fillRect(0, 0, 256, 64);
            context.strokeStyle = "#2E7D32";
            context.lineWidth = 2;
            context.strokeRect(2, 2, 252, 60);
            context.font = "bold 24px Arial";
            context.fillStyle = "#1B5E20";
            context.textAlign = "center";
            context.textBaseline = "middle";
            context.fillText(text, 128, 32);
            const texture = new THREE.CanvasTexture(canvas);
            const spriteMaterial = new THREE.SpriteMaterial({{ map: texture }});
            const sprite = new THREE.Sprite(spriteMaterial);
            sprite.position.set(x, y, z);
            sprite.scale.set(20, 5, 1);
            scene.add(sprite);
        }}
        
        let autoRotateEnabled = {auto_rotate_str};
        let shadowsEnabled = true;
        let cinematicMode = false;
        let cinematicTime = 0;
        
        function animate() {{
            requestAnimationFrame(animate);
            const time = Date.now() * 0.001;
            
            if (autoRotateEnabled && !cinematicMode) {{
                controls.autoRotate = true;
                controls.autoRotateSpeed = 2.0;
            }} else {{
                controls.autoRotate = false;
            }}
            
            animatedObjects.forEach(obj => {{
                if (obj.type === "pond") {{
                    const scale = obj.baseScale + Math.sin(time * 2) * 0.05;
                    obj.mesh.scale.set(scale, scale, 1);
                    obj.mesh.material.opacity = 0.6 + Math.sin(time * 3) * 0.2;
                }}
            }});
            
            if (cinematicMode) {{
                cinematicTime += 0.005;
                const radius = Math.max({L}, {W}) * 0.8;
                camera.position.x = {L/2} + Math.cos(cinematicTime * Math.PI * 2) * radius;
                camera.position.z = {W/2} + Math.sin(cinematicTime * Math.PI * 2) * radius;
                camera.position.y = Math.max({L}, {W}) * 0.5;
                camera.lookAt({L/2}, 0, {W/2});
                
                if (cinematicTime >= 1) {{
                    cinematicMode = false;
                    cinematicTime = 0;
                    controls.target.set({L/2}, 0, {W/2});
                }}
            }}
            
            controls.update();
            renderer.render(scene, camera);
        }}
        
        window.resetCamera = function() {{
            cinematicMode = false;
            camera.position.set({camera_config['x']}, {camera_config['y']}, {camera_config['z']});
            controls.target.set({L/2}, 0, {W/2});
            controls.update();
        }};
        
        window.toggleRotation = function() {{
            autoRotateEnabled = !autoRotateEnabled;
        }};
        
        window.toggleShadows = function() {{
            shadowsEnabled = !shadowsEnabled;
            sunLight.castShadow = shadowsEnabled;
            renderer.shadowMap.enabled = shadowsEnabled;
            scene.traverse(child => {{
                if (child.material) child.material.needsUpdate = true;
            }});
        }};
        
        window.cinematicTour = function() {{
            cinematicMode = true;
            cinematicTime = 0;
        }};
        
        window.addEventListener("resize", () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
        
        setTimeout(() => {{
            document.getElementById("loading").style.opacity = "0";
            setTimeout(() => {{
                document.getElementById("loading").style.display = "none";
            }}, 500);
        }}, 1500);
        
        animate();
    </script>
</body>
</html>"""
        
        return html_template
    
    def _build_scene_objects(self, layout, L, W, features, zones):
        """Build scene object list for Three.js"""
        objects = []
        
        # Terrain base
        objects.append({
            "type": "terrain",
            "width": L,
            "depth": W
        })
        
        # House
        if "house_position" in layout:
            house_pos = layout["house_position"]
            positions = {
                "North": {"x": L*0.35, "z": W*0.75},
                "South": {"x": L*0.35, "z": W*0.15},
                "East": {"x": L*0.75, "z": W*0.4},
                "West": {"x": L*0.15, "z": W*0.4},
                "Center": {"x": L*0.4, "z": W*0.4}
            }
            pos = positions.get(house_pos, positions["Center"])
            objects.append({
                "type": "house",
                "x": pos["x"],
                "z": pos["z"],
                "width": 30,
                "depth": 40,
                "height": 12
            })
        
        return json.dumps(objects)
    
    def _get_camera_config(self, mode, L, W):
        """Get camera position based on mode"""
        configs = {
            "Isometric": {"x": L*0.8, "y": max(L,W)*0.6, "z": W*0.8},
            "Top Down": {"x": L/2, "y": max(L,W)*1.2, "z": W/2},
            "North View": {"x": L/2, "y": max(L,W)*0.4, "z": -W*0.3},
            "South View": {"x": L/2, "y": max(L,W)*0.4, "z": W*1.3},
            "Cinematic Tour": {"x": L*0.8, "y": max(L,W)*0.6, "z": W*0.8}
        }
        
