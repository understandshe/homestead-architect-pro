import streamlit as st
import json

class Visualizer3D:
    def create(self, layout_data: dict):
        json_layout = json.dumps(layout_data)
        
        # अपना सही GitHub URL यहाँ चेक करें
        github_base = "https://raw.githubusercontent.com/understandshe/homestead-architect-pro/main/assets"
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ margin: 0; background-color: #87CEEB; }}
                #ui {{ position: absolute; top: 10px; left: 10px; color: white; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 5px; font-family: sans-serif; }}
            </style>
        </head>
        <body>
            <div id="ui">🏗️ 3D View: {layout_data.get('location', 'Plot')}</div>
            <script type="module">
                import * as THREE from 'https://unpkg.com/three@0.128.0/build/three.module.js';
                
                // --- SCENE SETUP ---
                const scene = new THREE.Scene();
                scene.background = new THREE.Color(0x87CEEB);

                const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 5000);
                const renderer = new THREE.WebGLRenderer({{ antialias: true }});
                renderer.setSize(window.innerWidth, window.innerHeight);
                document.body.appendChild(renderer.domElement);

                // Lighting
                scene.add(new THREE.AmbientLight(0xffffff, 0.7));
                const sun = new THREE.DirectionalLight(0xffffff, 1);
                sun.position.set(100, 200, 100);
                scene.add(sun);

                // --- GROUND (Matches your 600x600 plot) ---
                const data = {json_layout};
                const plotL = data.dimensions?.L || 100;
                const plotW = data.dimensions?.W || 100;
                
                const ground = new THREE.Mesh(
                    new THREE.PlaneGeometry(plotL, plotW),
                    new THREE.MeshStandardMaterial({{ color: 0x3d8c40, side: THREE.DoubleSide }})
                );
                ground.rotation.x = -Math.PI / 2;
                scene.add(ground);

                // --- FALLBACK HOUSE (अगर Library लोड न हो तो भी दिखेगा) ---
                const houseGroup = new THREE.Group();
                const body = new THREE.Mesh(new THREE.BoxGeometry(10, 8, 10), new THREE.MeshStandardMaterial({{color: 0xffffff}}));
                body.position.y = 4;
                const roof = new THREE.Mesh(new THREE.ConeGeometry(8, 6, 4), new THREE.MeshStandardMaterial({{color: 0x8b4513}}));
                roof.position.y = 11;
                roof.rotation.y = Math.PI / 4;
                houseGroup.add(body, roof);
                scene.add(houseGroup);

                // --- CAMERA POSITION (Crucial Fix) ---
                camera.position.set(plotL/2, plotL/2, plotL/2);
                camera.lookAt(0, 0, 0);

                // Try loading External Modules
                try {{
                    const LIB = await import('{github_base}/library.js');
                    const CAM = await import('{github_base}/camera_logic.js');
                    
                    // If successful, use your custom camera
                    if(CAM.initCameraControls) CAM.initCameraControls(camera, renderer.domElement);
                    
                    // Add your custom animated assets
                    if(LIB.createFarmhouse_B) {{
                        const myHouse = LIB.createFarmhouse_B(0, 0, 0, 1.5);
                        scene.add(myHouse);
                        houseGroup.visible = false; // Hide fallback house
                    }}
                }} catch(e) {{
                    console.warn("External JS failed to load, using basic view", e);
                }}

                function animate() {{
                    requestAnimationFrame(animate);
                    renderer.render(scene, camera);
                }}
                animate();

                window.addEventListener('resize', () => {{
                    camera.aspect = window.innerWidth / window.innerHeight;
                    camera.updateProjectionMatrix();
                    renderer.setSize(window.innerWidth, window.innerHeight);
                }});
            </script>
        </body>
        </html>
        """
        st.components.v1.html(html_template, height=700)
        
        st.download_button("📥 Download 3D HTML", data=html_template, file_name="homestead_3d.html", mime="text/html")
