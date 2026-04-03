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
        body {{ margin:0; overflow:hidden; background:#87CEEB; }} 
        #ui {{ position: absolute; top: 15px; left: 15px; color: white; background: rgba(0,0,0,0.7); 
               padding: 15px; border-radius: 10px; font-family: sans-serif; pointer-events: none; border: 1px solid rgba(255,255,255,0.2); }}
    </style>
</head>
<body>
    <div id="ui">
        <b>🌿 {layout_data.get('location', 'Modern Homestead')}</b><br>
        <small>Realistic 3D Engine v7.0</small>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

    <script>
        const data = {json_layout};
        const L = data.dimensions?.L || 100;
        const W = data.dimensions?.W || 100;

        // --- 1. SCENE & RENDERER ---
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0xaec6cf);
        
        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth, 750);
        renderer.shadowMap.enabled = true; // SHADOW ON
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.body.appendChild(renderer.domElement);

        // --- 2. CAMERA ---
        const camera = new THREE.PerspectiveCamera(50, window.innerWidth / 750, 1, 10000);
        camera.position.set(L*0.8, L*0.6, L*0.8); 

        // --- 3. PRO LIGHTING ---
        scene.add(new THREE.AmbientLight(0xffffff, 0.5));
        const sun = new THREE.DirectionalLight(0xffffff, 1.2);
        sun.position.set(L, 200, W);
        sun.castShadow = true;
        sun.shadow.mapSize.width = 2048; // Sharp Shadows
        sun.shadow.mapSize.height = 2048;
        scene.add(sun);

        // --- 4. GROUND ---
        const ground = new THREE.Mesh(
            new THREE.PlaneGeometry(L, W),
            new THREE.MeshStandardMaterial({{ color: 0x4d8c4d, roughness: 0.8 }})
        );
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        scene.add(ground);

        // --- 5. HOUSE (Realistic Geometry) ---
        const createHouse = () => {{
            const g = new THREE.Group();
            const body = new THREE.Mesh(new THREE.BoxGeometry(22, 14, 18), new THREE.MeshStandardMaterial({{color: 0xe0e0e0}}));
            body.position.y = 7; body.castShadow = true;
            const roof = new THREE.Mesh(new THREE.ConeGeometry(18, 12, 4), new THREE.MeshStandardMaterial({{color: 0x4b2c20}}));
            roof.position.y = 19; roof.rotation.y = Math.PI/4; roof.castShadow = true;
            g.add(body, roof);
            
            // Sync Position with 2D Logic
            const hPos = data.house_position || 'Center';
            if(hPos === 'West') g.position.x = -L/3;
            if(hPos === 'East') g.position.x = L/3;
            if(hPos === 'North') g.position.z = -W/3;
            if(hPos === 'South') g.position.z = W/3;
            
            scene.add(g);
        }};
        createHouse();

        // --- 6. FEATURES (Pond, Solar) ---
        if(data.features?.pond) {{
            const p = data.features.pond;
            const pond = new THREE.Mesh(new THREE.CircleGeometry(p.radius, 32), new THREE.MeshStandardMaterial({{color: 0x0077be, transparent:true, opacity:0.8}}));
            pond.rotation.x = -Math.PI/2;
            pond.position.set(p.x - L/2, 0.1, p.y - W/2);
            scene.add(pond);
        }}

        // --- 7. TREES ---
        const treePlacements = data.tree_placements || [];
        treePlacements.forEach(t => {{
            const g = new THREE.Group();
            const trunk = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.5, 8), new THREE.MeshStandardMaterial({{color: 0x3d2b1f}}));
            trunk.position.y = 4; trunk.castShadow = true;
            const leaves = new THREE.Mesh(new THREE.SphereGeometry(6), new THREE.MeshStandardMaterial({{color: 0x2d5a27}}));
            leaves.position.y = 12; leaves.castShadow = true;
            g.add(trunk, leaves);
            g.position.set(t.x - L/2, 0, t.y - W/2);
            scene.add(g);
        }});

        // --- 8. CONTROLS ---
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;

        function animate() {{
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }}
        animate();

        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / 750;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, 750);
        }});
    </script>
</body>
</html>
"""
        st.components.v1.html(html_template, height=750)
