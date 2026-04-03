import streamlit as st
import json

class Visualizer3D:
    def create(self, layout_data: dict):
        json_layout = json.dumps(layout_data)
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ margin: 0; background-color: #000; overflow: hidden; }}
                #ui {{ position: absolute; top: 15px; left: 15px; color: white; background: rgba(0,0,0,0.75); 
                       padding: 15px; border-radius: 10px; font-family: 'Segoe UI', sans-serif; pointer-events: none;
                       border: 1px solid rgba(255,255,255,0.1); }}
            </style>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/RGBELoader.js"></script>
        </head>
        <body>
            <div id="ui">
                <b style="color: #4CAF50;">🏡 Homestead Architect Pro 2026</b><br>
                <small>Location: {layout_data.get('location', 'Global')}</small>
            </div>
            
            <script>
                const data = {json_layout};
                const L = data.dimensions?.L || 100;
                const W = data.dimensions?.W || 100;

                // --- 1. REALISTIC ENGINE SETUP ---
                const scene = new THREE.Scene();
                scene.fog = new THREE.Fog(0xcce0ff, 100, 500);

                const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 2000);
                const renderer = new THREE.WebGLRenderer({{ antialias: true, powerPreference: "high-performance" }});
                renderer.setSize(window.innerWidth, window.innerHeight);
                
                // Realistic Rendering Settings
                renderer.physicallyCorrectLights = true;
                renderer.outputEncoding = THREE.sRGBEncoding;
                renderer.toneMapping = THREE.ACESFilmicToneMapping;
                renderer.toneMappingExposure = 1.2;
                renderer.shadowMap.enabled = true;
                renderer.shadowMap.type = THREE.PCFSoftShadowMap;
                document.body.appendChild(renderer.domElement);

                // --- 2. LIGHTING & HDRI ---
                const sun = new THREE.DirectionalLight(0xffffff, 2.0);
                sun.position.set(L, 150, W/2);
                sun.castShadow = true;
                sun.shadow.mapSize.set(2048, 2048);
                scene.add(sun);
                scene.add(new THREE.AmbientLight(0xffffff, 0.4));

                // Ground Setup
                const groundGeo = new THREE.PlaneGeometry(L, W, 32, 32);
                const groundMat = new THREE.MeshStandardMaterial({{ color: 0x567d46, roughness: 1 }});
                const ground = new THREE.Mesh(groundGeo, groundMat);
                ground.rotation.x = -Math.PI / 2;
                ground.receiveShadow = true;
                scene.add(ground);

                // --- 3. PRO MODELS ---
                const mat = (c, o = {{}}) => new THREE.MeshStandardMaterial({{ color: c, roughness: 0.7, metalness: 0.2, ...o }});

                const createTree = (x, z) => {{
                    const g = new THREE.Group();
                    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.7, 4, 10), mat(0x6b4423));
                    trunk.position.y = 2; trunk.castShadow = true;
                    const leaves = new THREE.Mesh(new THREE.SphereGeometry(5, 12, 12), mat(0x2e7d32));
                    leaves.position.y = 8; leaves.castShadow = true;
                    g.add(trunk, leaves);
                    g.position.set(x - L/2, 0, z - W/2);
                    scene.add(g);
                }};

                const createFarmhouse = (x, z) => {{
                    const g = new THREE.Group();
                    const base = new THREE.Mesh(new THREE.BoxGeometry(20, 12, 20), mat(0xb07d52));
                    base.position.y = 6; base.castShadow = true;
                    const roof = new THREE.Mesh(new THREE.ConeGeometry(18, 12, 4), mat(0x5a2d0c));
                    roof.position.y = 18; roof.rotation.y = Math.PI/4;
                    g.add(base, roof);
                    g.position.set(x, 0, z);
                    scene.add(g);
                }};

                // --- 4. DATA MAPPING (INTERVIEW SYNC) ---
                // House Position
                let hX = 0, hZ = 0;
                if(data.house_position === 'North') hZ = -W/3;
                if(data.house_position === 'South') hZ = W/3;
                createFarmhouse(hX, hZ);

                // Dynamic Trees
                const treePlacements = data.tree_placements || [];
                treePlacements.forEach(t => createTree(t.x, t.y));

                // --- 5. CONTROLS & LOOP ---
                const controls = new THREE.OrbitControls(camera, renderer.domElement);
                camera.position.set(L, L/2, W);
                controls.enableDamping = true;

                function animate(t) {{
                    requestAnimationFrame(animate);
                    controls.update();
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
        st.components.v1.html(html_template, height=800)
