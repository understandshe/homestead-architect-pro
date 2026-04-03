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
                body {{ margin: 0; background: #87CEEB; overflow: hidden; }}
                #ui {{ position: absolute; top: 15px; left: 15px; color: white; background: rgba(0,0,0,0.7); 
                       padding: 15px; border-radius: 12px; font-family: sans-serif; pointer-events: none; }}
            </style>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        </head>
        <body>
            <div id="ui">
                <b>🏡 {layout_data.get('location', 'My Homestead')}</b><br>
                <small>Mode: Interactive 3D Architect</small>
            </div>
            
            <script>
                const data = {json_layout};
                const L = data.dimensions?.L || 100;
                const W = data.dimensions?.W || 100;

                // --- ENGINE SETUP ---
                const scene = new THREE.Scene();
                scene.background = new THREE.Color(0x87CEEB);
                const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 1, 5000);
                const renderer = new THREE.WebGLRenderer({{ antialias: true }});
                renderer.setSize(window.innerWidth, window.innerHeight);
                renderer.shadowMap.enabled = true;
                document.body.appendChild(renderer.domElement);

                scene.add(new THREE.AmbientLight(0xffffff, 0.6));
                const sun = new THREE.DirectionalLight(0xffffff, 1.2);
                sun.position.set(L, 200, W);
                sun.castShadow = true;
                scene.add(sun);

                // --- GROUND ---
                const ground = new THREE.Mesh(
                    new THREE.PlaneGeometry(L, W),
                    new THREE.MeshStandardMaterial({{ color: 0x4a934a }})
                );
                ground.rotation.x = -Math.PI / 2;
                ground.receiveShadow = true;
                scene.add(ground);

                // --- HELPER: COORDINATE TRANSFORM ---
                // Transforms 2D (x,y) to 3D (x,z) centered
                const getPos = (x, y) => ({{ x: x - L/2, z: y - W/2 }});

                // --- 1. DYNAMIC HOUSE ---
                const hX = data.house_position === 'West' ? -L/3 : (data.house_position === 'East' ? L/3 : 0);
                const hZ = data.house_position === 'North' ? -W/3 : (data.house_position === 'South' ? W/3 : 0);
                
                const house = new THREE.Group();
                const body = new THREE.Mesh(new THREE.BoxGeometry(20, 12, 16), new THREE.MeshStandardMaterial({{color: 0xefebe9}}));
                body.position.y = 6; body.castShadow = true;
                const roof = new THREE.Mesh(new THREE.ConeGeometry(16, 10, 4), new THREE.MeshStandardMaterial({{color: 0x3e2723}}));
                roof.position.y = 17; roof.rotation.y = Math.PI/4; roof.castShadow = true;
                house.add(body, roof);
                house.position.set(hX, 0, hZ);
                scene.add(house);

                // --- 2. DYNAMIC FEATURES (User Output Sync) ---
                const features = data.features || {{}};

                // Solar Panels
                if (features.solar) {{
                    const s = features.solar;
                    const pos = getPos(s.x + s.width/2, s.y + s.height/2);
                    const panel = new THREE.Mesh(new THREE.BoxGeometry(s.width, 1, s.height), new THREE.MeshStandardMaterial({{color: 0x1a237e}}));
                    panel.position.set(pos.x, 2, pos.z);
                    panel.rotation.x = -0.3; // Tilted towards sun
                    scene.add(panel);
                }}

                // Pond / Water
                if (features.pond) {{
                    const p = features.pond;
                    const pos = getPos(p.x, p.y);
                    const water = new THREE.Mesh(new THREE.CircleGeometry(p.radius, 32), new THREE.MeshStandardMaterial({{color: 0x0288d1, transparent: true, opacity: 0.8}}));
                    water.rotation.x = -Math.PI/2;
                    water.position.set(pos.x, 0.1, pos.z);
                    scene.add(water);
                }}

                // Greenhouse
                if (features.greenhouse) {{
                    const gh = features.greenhouse;
                    const pos = getPos(gh.x + gh.width/2, gh.y + gh.height/2);
                    const glass = new THREE.Mesh(new THREE.BoxGeometry(gh.width, 8, gh.height), new THREE.MeshStandardMaterial({{color: 0xb2dfdb, transparent: true, opacity: 0.4}}));
                    glass.position.set(pos.x, 4, pos.z);
                    scene.add(glass);
                }}

                // --- 3. DYNAMIC TREES ---
                const treePlacements = data.tree_placements || [];
                treePlacements.forEach(t => {{
                    const pos = getPos(t.x, t.y);
                    const tree = new THREE.Group();
                    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.8, 1, 6), new THREE.MeshStandardMaterial({{color: 0x4d2911}}));
                    trunk.position.y = 3; trunk.castShadow = true;
                    const leaves = new THREE.Mesh(new THREE.SphereGeometry(5), new THREE.MeshStandardMaterial({{color: 0x2e7d32}}));
                    leaves.position.y = 10; leaves.castShadow = true;
                    tree.add(trunk, leaves);
                    tree.position.set(pos.x, 0, pos.z);
                    scene.add(tree);
                }});

                // --- CONTROLS & ANIMATION ---
                const controls = new THREE.OrbitControls(camera, renderer.domElement);
                camera.position.set(L*0.8, L*0.6, L*0.8);
                controls.enableDamping = true;

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
