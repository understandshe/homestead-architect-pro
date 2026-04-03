import streamlit as st
import json

class Visualizer3D:
    """
    High-Performance 3D Engine for Homestead Architect Pro 2026.
    Fixed Path issues for Global Deployment.
    """

    def create(self, layout_data: dict):
        json_layout = json.dumps(layout_data)
        
        # --- IMPORTANT: Change 'YOUR_USERNAME' to your actual GitHub username ---
        # --- This allows the browser to find your JS files ---
        github_base = "https://raw.githubusercontent.com/understandshe/homestead-architect-pro/main/assets"
        
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ margin: 0; padding: 0; overflow: hidden; background-color: #87CEEB; }}
                #overlay {{
                    position: absolute; top: 20px; left: 20px;
                    color: white; font-family: sans-serif;
                    background: rgba(0,0,0,0.5); padding: 10px 20px; border-radius: 8px;
                    pointer-events: none;
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
                
                // Fetching JS from GitHub directly to fix "File Not Found" error
                async function loadModules() {{
                    const libMod = await import('{github_base}/library.js');
                    const camMod = await import('{github_base}/camera_logic.js');
                    
                    startEngine(libMod, camMod);
                }}

                function startEngine(LIB, CAM) {{
                    const scene = new THREE.Scene();
                    scene.background = new THREE.Color(0x87CEEB);

                    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 2000);
                    const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
                    renderer.setSize(window.innerWidth, window.innerHeight);
                    renderer.shadowMap.enabled = true;
                    document.body.appendChild(renderer.domElement);

                    // Lights
                    const amb = new THREE.AmbientLight(0xffffff, 0.8);
                    scene.add(amb);
                    const sun = new THREE.DirectionalLight(0xffffff, 1);
                    sun.position.set(100, 200, 100);
                    scene.add(sun);

                    // Ground
                    const data = {json_layout};
                    const plotL = data.dimensions?.L || 100;
                    const plotW = data.dimensions?.W || 100;
                    const ground = new THREE.Mesh(
                        new THREE.PlaneGeometry(plotL, plotW),
                        new THREE.MeshStandardMaterial({{ color: 0x3d8c40 }})
                    );
                    ground.rotation.x = -Math.PI / 2;
                    scene.add(ground);

                    // Assets
                    const house = LIB.createFarmhouse_B(0, 0, 0, 1.5);
                    scene.add(house);

                    // Tree Logic
                    const treeCount = data.tree_count || 15;
                    for(let i=0; i<treeCount; i++) {{
                        const tx = (Math.random() - 0.5) * (plotL - 10);
                        const tz = (Math.random() - 0.5) * (plotW - 10);
                        const tree = LIB.createOrchard_Apple(tx, 0, tz, 0.8);
                        scene.add(tree);
                    }}

                    CAM.initCameraControls(camera, renderer.domElement);

                    function animate(time) {{
                        requestAnimationFrame(animate);
                        CAM.updateCameraView(camera, time * 0.001);
                        LIB.updateAssets(scene, time * 0.001);
                        renderer.render(scene, camera);
                    }}
                    animate();
                }}

                loadModules();
            </script>
        </body>
        </html>
        """
        
        # --- RETURN HTML VIEW ---
        st.components.v1.html(html_template, height=700)
        
        # --- RETURN DOWNLOAD BUTTON (Fixed) ---
        st.divider()
        st.download_button(
            label="🚀 Download Interactive 3D Map (HTML)",
            data=html_template,
            file_name="chundalgardens_3d_view.html",
            mime="text/html",
            use_container_width=True
        )
