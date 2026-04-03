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
        canvas {{ display:block; }}
        #ui {{ position: absolute; top: 10px; left: 10px; color: white; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 5px; font-family: sans-serif; pointer-events: none; }}
    </style>
</head>
<body>
    <div id="ui">🏗️ 3D View: Interactive Mode</div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

    <script>
        // --- 1. SETUP ---
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0xaec6cf);
        
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, 750);
        renderer.shadowMap.enabled = true;
        document.body.appendChild(renderer.domElement);

        // --- 2. DATA ---
        const data = {json_layout};
        const L = data.dimensions?.L || 100;
        const W = data.dimensions?.W || 100;

        // --- 3. CAMERA ---
        // कैमरे को फिक्स 100 की दूरी पर रखा है ताकि नज़ारा साफ़ दिखे
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / 750, 1, 10000);
        camera.position.set(80, 60, 80); 

        // Lighting
        scene.add(new THREE.AmbientLight(0xffffff, 0.7));
        const sun = new THREE.DirectionalLight(0xffffff, 1);
        sun.position.set(100, 200, 100);
        sun.castShadow = true;
        scene.add(sun);

        // --- 4. GROUND ---
        const ground = new THREE.Mesh(
            new THREE.PlaneGeometry(L, W),
            new THREE.MeshStandardMaterial({{ color: 0x567d46, side: THREE.DoubleSide }})
        );
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        scene.add(ground);

        // --- 5. CENTER HOUSE ---
        const house = new THREE.Group();
        const body = new THREE.Mesh(new THREE.BoxGeometry(20, 12, 20), new THREE.MeshStandardMaterial({{ color: 0xdbad76 }}));
        body.position.y = 6;
        body.castShadow = true;
        const roof = new THREE.Mesh(new THREE.ConeGeometry(16, 10, 4), new THREE.MeshStandardMaterial({{ color: 0x5a2d0c }}));
        roof.position.y = 17;
        roof.rotation.y = Math.PI / 4;
        house.add(body, roof);
        scene.add(house);

        // --- 6. TREES ---
        const treePlacements = data.tree_placements || [];
        treePlacements.forEach(t => {{
            const g = new THREE.Group();
            const trunk = new THREE.Mesh(new THREE.CylinderGeometry(1, 1.2, 8), new THREE.MeshStandardMaterial({{ color: 0x4d2911 }}));
            trunk.position.y = 4;
            const leaves = new THREE.Mesh(new THREE.SphereGeometry(6), new THREE.MeshStandardMaterial({{ color: 0x2e7d32 }}));
            leaves.position.y = 12;
            g.add(trunk, leaves);
            
            // डेटा के हिसाब से पोजीशन (सेंटर से ऑफसेट)
            g.position.set(t.x - L/2, 0, t.y - W/2);
            scene.add(g);
        }});

        // --- 7. CONTROLS ---
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.target.set(0, 0, 0);
        controls.enableDamping = true;

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
