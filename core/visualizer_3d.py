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
        body {{ margin:0; overflow:hidden; background:#87CEEB; }} 
        canvas {{ display:block; width: 100vw; height: 750px; }}
    </style>
</head>
<body>
    <script type="module">
        import * as THREE from 'https://unpkg.com/three@0.128.0/build/three.module.js';
        import {{ OrbitControls }} from 'https://unpkg.com/three@0.128.0/examples/jsm/controls/OrbitControls.js';

        /* ========= DATA & SCENE ========= */
        const data = {json_layout};
        const L = data.dimensions?.L || 100;
        const W = data.dimensions?.W || 100;

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0xaec6cf); // Soft Blue Sky

        /* ========= CAMERA (Adjusted for Large Plots) ========= */
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / 750, 0.1, 10000);
        // कैमरा को प्लॉट के बीच में और थोड़ा ऊपर रखा है
        camera.position.set(L/2, L/3, W/2); 

        /* ========= RENDERER ========= */
        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth, 750);
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.shadowMap.enabled = true;
        document.body.appendChild(renderer.domElement);

        /* ========= LIGHTING ========= */
        scene.add(new THREE.AmbientLight(0xffffff, 0.7));
        const sun = new THREE.DirectionalLight(0xffffff, 1.0);
        sun.position.set(L, 150, W);
        sun.castShadow = true;
        scene.add(sun);

        /* ========= GROUND (Matches User Dimensions) ========= */
        const groundGeo = new THREE.PlaneGeometry(L, W);
        const groundMat = new THREE.MeshStandardMaterial({{ color: 0x567d46, side: THREE.DoubleSide }});
        const ground = new THREE.Mesh(groundGeo, groundMat);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        scene.add(ground);

        /* ========= HOUSE (At Center of Plot) ========= */
        const house = new THREE.Group();
        const body = new THREE.Mesh(new THREE.BoxGeometry(20, 12, 20), new THREE.MeshStandardMaterial({{ color: 0xdbad76 }}));
        body.position.y = 6;
        body.castShadow = true;
        const roof = new THREE.Mesh(new THREE.ConeGeometry(16, 10, 4), new THREE.MeshStandardMaterial({{ color: 0x5a2d0c }}));
        roof.position.y = 17;
        roof.rotation.y = Math.PI / 4;
        house.add(body, roof);
        scene.add(house);

        /* ========= DYNAMIC TREES (From User Layout) ========= */
        const treePlacements = data.tree_placements || [];
        treePlacements.forEach(t => {{
            const g = new THREE.Group();
            const trunk = new THREE.Mesh(new THREE.CylinderGeometry(1, 1.2, 7), new THREE.MeshStandardMaterial({{ color: 0x4d2911 }}));
            trunk.position.y = 3.5;
            const leaves = new THREE.Mesh(new THREE.SphereGeometry(5, 12, 12), new THREE.MeshStandardMaterial({{ color: 0x2e7d32 }}));
            leaves.position.y = 10;
            g.add(trunk, leaves);
            
            // 2D Coordinates को 3D सीन के सेंटर के हिसाब से एडजस्ट किया
            g.position.set(t.x - L/2, 0, t.y - W/2);
            scene.add(g);
        }});

        /* ========= CONTROLS ========= */
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.target.set(0, 0, 0); // कैमरा हमेशा सेंटर (घर) को देखेगा
        controls.enableDamping = true;

        /* ========= LOOP ========= */
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
