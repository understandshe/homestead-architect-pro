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
    <style>
        body {{ margin:0; overflow:hidden; background:#87CEEB; }} /* डिफ़ॉल्ट बैकग्राउंड नीला रखा है */
        canvas {{ display:block; }}
    </script>
</head>
<body>
    <script type="module">
        // UNPKG इस्तेमाल करना सबसे ज़्यादा स्टेबल है
        import * as THREE from 'https://unpkg.com/three@0.128.0/build/three.module.js';
        import {{ OrbitControls }} from 'https://unpkg.com/three@0.128.0/examples/jsm/controls/OrbitControls.js';

        /* ========= DATA ========= */
        const data = {json_layout};
        const L = data.dimensions?.L || 100;
        const W = data.dimensions?.W || 100;

        /* ========= SCENE ========= */
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0xaec6cf);

        /* ========= CAMERA ========= */
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / 750, 0.1, 5000);
        // कैमरा को थोड़ा दूर रखा है ताकि बड़ा प्लॉट दिखे
        camera.position.set(L, L, L); 

        /* ========= RENDERER ========= */
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, 750);
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.shadowMap.enabled = true;
        document.body.appendChild(renderer.domElement);

        /* ========= LIGHT ========= */
        scene.add(new THREE.AmbientLight(0xffffff, 0.6));
        const sun = new THREE.DirectionalLight(0xffffff, 1.2);
        sun.position.set(L, 200, L/2);
        sun.castShadow = true;
        scene.add(sun);

        /* ========= GROUND ========= */
        const ground = new THREE.Mesh(
            new THREE.PlaneGeometry(L * 2, W * 2),
            new THREE.MeshStandardMaterial({{ color: 0x567d46, side: THREE.DoubleSide }})
        );
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        scene.add(ground);

        /* ========= HOUSE (Position Synced) ========= */
        const house = new THREE.Group();
        const body = new THREE.Mesh(new THREE.BoxGeometry(20, 12, 20), new THREE.MeshStandardMaterial({{ color: 0xdbad76 }}));
        body.position.y = 6;
        body.castShadow = true;
        const roof = new THREE.Mesh(new THREE.ConeGeometry(16, 10, 4), new THREE.MeshStandardMaterial({{ color: 0x5a2d0c }}));
        roof.position.y = 17;
        roof.rotation.y = Math.PI / 4;
        house.add(body, roof);
        
        // घर को थोड़ा साइड में रखा है ताकि ग्राउंड दिखे
        house.position.set(0, 0, 0);
        scene.add(house);

        /* ========= TREES ========= */
        const treeGeo = new THREE.CylinderGeometry(1, 1.5, 8, 10);
        const leafGeo = new THREE.SphereGeometry(6, 12, 12);
        const treeMat = new THREE.MeshStandardMaterial({{ color: 0x4d2911 }});
        const leafMat = new THREE.MeshStandardMaterial({{ color: 0x2e7d32 }});

        for (let i = 0; i < 25; i++) {{
            const g = new THREE.Group();
            const trunk = new THREE.Mesh(treeGeo, treeMat);
            trunk.position.y = 4;
            const leaves = new THREE.Mesh(leafGeo, leafMat);
            leaves.position.y = 12;
            g.add(trunk, leaves);
            
            g.position.set((Math.random() - 0.5) * L * 1.5, 0, (Math.random() - 0.5) * W * 1.5);
            scene.add(g);
        }}

        /* ========= CONTROLS ========= */
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;

        /* ========= LOOP ========= */
        function animate() {{
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }}
        animate();

        /* ========= RESIZE ========= */
        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / 750;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, 750);
        }});
    </script>
</body>
</html>
"""
        st.components.v1.html(html_template, height=750, scrolling=False)
