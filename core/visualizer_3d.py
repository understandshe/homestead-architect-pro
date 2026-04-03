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
                body {{ margin: 0; background: linear-gradient(to bottom, #87CEEB 0%, #E0F7FA 100%); overflow: hidden; }}
                #ui {{ position: absolute; top: 15px; left: 15px; color: white; background: rgba(0,0,0,0.7); 
                       padding: 15px; border-radius: 12px; font-family: 'Segoe UI', sans-serif; pointer-events: none;
                       border: 1px solid rgba(255,255,255,0.2); }}
            </style>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        </head>
        <body>
            <div id="ui">
                <b style="font-size:16px;">🌿 {layout_data.get('location', 'Global Homestead')}</b><br>
                <small>Plot Area: {layout_data.get('total_sqft', 0):,.0f} sq.ft.</small>
            </div>
            
            <script>
                const data = {json_layout};
                const L = data.dimensions?.L || 100;
                const W = data.dimensions?.W || 100;

                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 1, 5000);
                const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
                renderer.setSize(window.innerWidth, window.innerHeight);
                renderer.shadowMap.enabled = true; // Enable Shadows
                renderer.shadowMap.type = THREE.PCFSoftShadowMap;
                document.body.appendChild(renderer.domElement);

                // Professional Lighting
                scene.add(new THREE.AmbientLight(0xffffff, 0.5));
                const sun = new THREE.DirectionalLight(0xffffff, 1.2);
                sun.position.set(L, 200, W);
                sun.castShadow = true;
                // Better Shadow Resolution
                sun.shadow.mapSize.width = 1024;
                sun.shadow.mapSize.height = 1024;
                scene.add(sun);

                // --- Ground with Realistic Texture Look ---
                const groundGeo = new THREE.PlaneGeometry(L, W);
                const groundMat = new THREE.MeshStandardMaterial({{ 
                    color: 0x448a44, 
                    roughness: 0.8,
                    metalness: 0.1
                }});
                const ground = new THREE.Mesh(groundGeo, groundMat);
                ground.rotation.x = -Math.PI / 2;
                ground.receiveShadow = true;
                scene.add(ground);

                // --- SMART HOUSE PLACEMENT (Syncs with 2D) ---
                const createHouse = () => {{
                    const g = new THREE.Group();
                    // Walls
                    const body = new THREE.Mesh(new THREE.BoxGeometry(20, 12, 16), new THREE.MeshStandardMaterial({{color: 0xefebe9}}));
                    body.position.y = 6;
                    body.castShadow = true;
                    // Roof
                    const roof = new THREE.Mesh(new THREE.ConeGeometry(16, 10, 4), new THREE.MeshStandardMaterial({{color: 0x3e2723}}));
                    roof.position.y = 17;
                    roof.rotation.y = Math.PI / 4;
                    roof.castShadow = true;
                    g.add(body, roof);

                    // Position logic based on 'house_position'
                    const pos = data.house_position || 'Center';
                    if(pos === 'North') g.position.z = -(W/2.5);
                    if(pos === 'South') g.position.z = (W/2.5);
                    if(pos === 'East')  g.position.x = (L/2.5);
                    if(pos === 'West')  g.position.x = -(L/2.5);
                    
                    scene.add(g);
                }};
                createHouse();

                // --- DETAILED TREES (By Species) ---
                const speciesColors = {{
                    'Mango': 0x1b5e20, 'Coconut': 0x2e7d32, 'Lemon': 0x43a047
                }};

                const placements = data.tree_placements || [];
                placements.forEach(t => {{
                    const treeGroup = new THREE.Group();
                    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(1, 1.2, 8), new THREE.MeshStandardMaterial({{color: 0x4d2911}}));
                    trunk.position.y = 4;
                    trunk.castShadow = true;

                    const leafColor = speciesColors[t.species] || 0x228b22;
                    const leaves = new THREE.Mesh(new THREE.SphereGeometry(6, 12, 12), new THREE.MeshStandardMaterial({{color: leafColor}}));
                    leaves.position.y = 12;
                    leaves.castShadow = true;

                    treeGroup.add(trunk, leaves);
                    // Standard Three.js coordinates: Y is up, X/Z is ground
                    treeGroup.position.set(t.x - L/2, 0, t.y - W/2); 
                    scene.add(treeGroup);
                }});

                // --- CONTROLS ---
                const controls = new THREE.OrbitControls(camera, renderer.domElement);
                camera.position.set(L, L*0.7, L);
                controls.enableDamping = true;
                controls.dampingFactor = 0.05;

                function animate() {{
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
        st.components.v1.html(html_template, height=750)
