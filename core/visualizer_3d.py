import streamlit as st
import json

class Visualizer3D:
    def create(self, layout_data: dict):
        # 1. डेटा को JSON में बदलें
        json_layout = json.dumps(layout_data)
        
        # 2. PRO HTML Template (तेरा नया Realistic Code यहाँ है)
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ margin: 0; background-color: #000; overflow: hidden; }}
                #ui {{ position: absolute; top: 15px; left: 15px; color: white; background: rgba(0,0,0,0.7); 
                       padding: 12px; border-radius: 8px; font-family: sans-serif; pointer-events: none; }}
            </style>
        </head>
        <body>
            <div id="ui">🚀 <b>Architect Pro 2026</b> | Realistic Engine v7</div>
            
            <script type="module">
                import * as THREE from 'https://unpkg.com/three@0.128.0/build/three.module.js';
                import {{ OrbitControls }} from 'https://unpkg.com/three@0.128.0/examples/jsm/controls/OrbitControls.js';
                import {{ RGBELoader }} from 'https://unpkg.com/three@0.128.0/examples/jsm/loaders/RGBELoader.js';

                const data = {json_layout};
                const L = data.dimensions?.L || 100;
                const W = data.dimensions?.W || 100;

                /* ========= SCENE SETUP ========= */
                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 2000);
                const renderer = new THREE.WebGLRenderer({{ antialias: true, powerPreference: "high-performance" }});
                renderer.setSize(window.innerWidth, window.innerHeight);
                renderer.setPixelRatio(window.devicePixelRatio);
                document.body.appendChild(renderer.domElement);

                /* ========= PRO RENDER SETTINGS ========= */
                renderer.physicallyCorrectLights = true;
                renderer.outputEncoding = THREE.sRGBEncoding;
                renderer.toneMapping = THREE.ACESFilmicToneMapping;
                renderer.toneMappingExposure = 1.2;
                renderer.shadowMap.enabled = true;
                renderer.shadowMap.type = THREE.PCFSoftShadowMap;

                /* ========= LIGHTING ========= */
                const sun = new THREE.DirectionalLight(0xffffff, 1.8);
                sun.position.set(L, 150, W/2);
                sun.castShadow = true;
                sun.shadow.mapSize.set(2048, 2048);
                scene.add(sun);
                scene.add(new THREE.AmbientLight(0xffffff, 0.4));

                /* ========= GROUND & FOG ========= */
                scene.fog = new THREE.Fog(0xcce0ff, 100, 1000);
                const groundGeo = new THREE.PlaneGeometry(L * 2, W * 2, 50, 50);
                const groundMat = new THREE.MeshStandardMaterial({{ color: 0x567d46, roughness: 1 }});
                const ground = new THREE.Mesh(groundGeo, groundMat);
                ground.rotation.x = -Math.PI / 2;
                ground.receiveShadow = true;
                scene.add(ground);

                /* ========= ASSET BUILDERS ========= */
                const mat = (c, o = {{}}) => new THREE.MeshStandardMaterial({{ color: c, roughness: 0.7, metalness: 0.2, ...o }});

                const createTree = (x, z) => {{
                    const g = new THREE.Group();
                    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(1, 1.5, 8, 10), mat(0x4d2911));
                    trunk.position.y = 4; trunk.castShadow = true;
                    const leaves = new THREE.Mesh(new THREE.SphereGeometry(6, 12, 12), mat(0x2e7d32));
                    leaves.position.y = 12; leaves.castShadow = true;
                    g.add(trunk, leaves);
                    g.position.set(x, 0, z);
                    scene.add(g);
                }};

                const createHouse = (x, z) => {{
                    const g = new THREE.Group();
                    const b = new THREE.Mesh(new THREE.BoxGeometry(20, 12, 20), mat(0xdbad76));
                    b.position.y = 6; b.castShadow = true;
                    const r = new THREE.Mesh(new THREE.ConeGeometry(16, 10, 4), mat(0x5a2d0c));
                    r.position.y = 17; r.rotation.y = Math.PI / 4;
                    g.add(b, r);
                    g.position.set(x, 0, z);
                    scene.add(g);
                }};

                /* ========= DATA MAPPING ========= */
                // Place House based on Interview
                const hPos = data.house_position || 'Center';
                let hX = 0, hZ = 0;
                if(hPos === 'North') hZ = -W/3;
                if(hPos === 'South') hZ = W/3;
                createHouse(hX, hZ);

                // Place Trees based on Slider
                const treeCount = data.tree_count || 15;
                for(let i=0; i<treeCount; i++) {{
                    const tx = (Math.random() - 0.5) * (L * 0.9);
                    const tz = (Math.random() - 0.5) * (W * 0.9);
                    if(Math.abs(tx - hX) > 20 || Math.abs(tz - hZ) > 20) createTree(tx, tz);
                }}

                /* ========= ANIMATION & CONTROLS ========= */
                const controls = new THREE.OrbitControls(camera, renderer.domElement);
                camera.position.set(L, L*0.6, L);
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
        st.components.v1.html(html_template, height=750)
