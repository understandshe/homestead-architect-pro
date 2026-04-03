import streamlit as st
import json

class Visualizer3D:
    """
    High-Performance 3D Engine for Homestead Architect Pro 2026.
    Uses Three.js for realistic, animated, and smooth visualization.
    """

    def create(self, layout_data: dict):
        # 1. Convert Python data to JSON for the JavaScript Engine
        # This ensures 3D matches exactly with the User Interview data
        json_layout = json.dumps(layout_data)
        
        # 2. The Premium 3D HTML Template
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>3D Homestead - Global Edition</title>
            <style>
                body {{ margin: 0; padding: 0; overflow: hidden; background-color: #87CEEB; }}
                #overlay {{
                    position: absolute; top: 20px; left: 20px;
                    color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: rgba(0,0,0,0.5); padding: 10px 20px; border-radius: 8px;
                    pointer-events: none; border: 1px solid rgba(255,255,255,0.2);
                }}
            </style>
        </head>
        <body>
            <div id="overlay">
                <h3 style="margin:0;">🌿 {layout_data.get('location', 'Custom Plot')}</h3>
                <p style="margin:5px 0 0 0; font-size:12px; opacity:0.8;">
                    Dimensions: {layout_data.get('dimensions', {}).get('L', 100)}x{layout_data.get('dimensions', {}).get('W', 100)} ft
                </p>
            </div>

            <script type="module">
                import * as THREE from 'https://unpkg.com/three@0.128.0/build/three.module.js';
                // Importing your custom library and camera logic from assets
                import * as LIB from './assets/library.js';
                import {{ initCameraControls, updateCameraView }} from './assets/camera_logic.js';

                // --- SCENE SETUP ---
                const scene = new THREE.Scene();
                scene.background = new THREE.Color(0x87CEEB); // Sky color

                const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
                const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
                renderer.setSize(window.innerWidth, window.innerHeight);
                renderer.setPixelRatio(window.devicePixelRatio);
                renderer.shadowMap.enabled = true;
                document.body.appendChild(renderer.domElement);

                // --- LIGHTING ---
                const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
                scene.add(ambientLight);

                const sunLight = new THREE.DirectionalLight(0xffffff, 1.2);
                sunLight.position.set(50, 100, 50);
                sunLight.castShadow = true;
                scene.add(sunLight);

                // --- GROUND GEN (Matches Plot Dimensions) ---
                const data = {json_layout};
                const plotL = data.dimensions?.L || 100;
                const plotW = data.dimensions?.W || 100;

                const groundGeo = new THREE.PlaneGeometry(plotL, plotW);
                const groundMat = new THREE.MeshStandardMaterial({{ color: 0x3d8c40 }});
                const ground = new THREE.Mesh(groundGeo, groundMat);
                ground.rotation.x = -Math.PI / 2;
                ground.receiveShadow = true;
                scene.add(ground);

                // --- ASSET PLACEMENT LOGIC ---
                // House Placement (Matches 2D Location)
                const hPos = data.house_position || 'Center';
                let hX = 0, hZ = 0;
                if(hPos === 'North') hZ = -plotW/3;
                if(hPos === 'South') hZ = plotW/3;
                
                const house = LIB.createFarmhouse_B(hX, 0, hZ, 1.2);
                scene.add(house);

                // Tree Placement (Matches Slider Count)
                const treeCount = data.tree_count || 15;
                for(let i=0; i < treeCount; i++) {{
                    const tx = (Math.random() - 0.5) * (plotL - 20);
                    const tz = (Math.random() - 0.5) * (plotW - 20);
                    // Avoid placing trees on the house
                    if(Math.abs(tx - hX) > 15 || Math.abs(tz - hZ) > 15) {{
                        const tree = LIB.createOrchard_Apple(tx, 0, tz, 0.8 + Math.random() * 0.4);
                        scene.add(tree);
                    }}
                }}

                // --- INITIALIZE CAMERA ---
                initCameraControls(camera, renderer.domElement);

                // --- ANIMATION LOOP ---
                function animate(time) {{
                    requestAnimationFrame(animate);
                    const t = time * 0.001; // convert to seconds

                    // Update Realistic Camera
                    updateCameraView(camera, t);

                    // Update Animated Assets (Chickens, Water, etc.)
                    LIB.updateAssets(scene, t);

                    renderer.render(scene, camera);
                }}
                animate();

                // Handle Window Resize
                window.addEventListener('resize', () => {{
                    camera.aspect = window.innerWidth / window.innerHeight;
                    camera.updateProjectionMatrix();
                    renderer.setSize(window.innerWidth, window.innerHeight);
                }});

            </script>
        </body>
        </html>
        """
        # Render the 3D Viewer in Streamlit
        return st.components.v1.html(html_template, height=700)
