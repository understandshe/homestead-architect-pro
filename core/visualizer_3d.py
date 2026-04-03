import streamlit as st
import json

class Visualizer3D:
    def create(self, layout_data: dict):
        # Python data को JSON में बदलें ताकि JS समझ सके
        json_layout = json.dumps(layout_data)
        
        # पूरा 3D इंजन अब इसी एक स्ट्रिंग के अंदर है
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ margin: 0; background-color: #87CEEB; overflow: hidden; touch-action: none; }}
                #ui {{ position: absolute; top: 10px; left: 10px; color: white; background: rgba(0,0,0,0.6); 
                       padding: 12px; border-radius: 8px; font-family: sans-serif; pointer-events: none; }}
                canvas {{ display: block; }}
            </style>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        </head>
        <body>
            <div id="ui">
                <b>🌿 Homestead 3D View</b><br>
                Plot: {layout_data.get('dimensions', {}).get('L', 100)}x{layout_data.get('dimensions', {}).get('W', 100)} ft
            </div>
            
            <script>
                // --- 1. SETUP ENGINE ---
                const scene = new THREE.Scene();
                scene.background = new THREE.Color(0x87CEEB);
                
                const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 1, 10000);
                const renderer = new THREE.WebGLRenderer({{ antialias: true }});
                renderer.setSize(window.innerWidth, window.innerHeight);
                renderer.setPixelRatio(window.devicePixelRatio);
                document.body.appendChild(renderer.domElement);

                // Lighting
                scene.add(new THREE.AmbientLight(0xffffff, 0.8));
                const sun = new THREE.DirectionalLight(0xffffff, 1);
                sun.position.set(200, 400, 200);
                scene.add(sun);

                // --- 2. DATA & GROUND ---
                const data = {json_layout};
                const L = data.dimensions?.L || 100;
                const W = data.dimensions?.W || 100;

                const groundGeo = new THREE.PlaneGeometry(L, W);
                const groundMat = new THREE.MeshStandardMaterial({{ color: 0x3d8c40, side: THREE.DoubleSide }});
                const ground = new THREE.Mesh(groundGeo, groundMat);
                ground.rotation.x = -Math.PI / 2;
                scene.add(ground);

                // --- 3. MODELS (Built-in) ---
                // House
                const createHouse = (x, z) => {{
                    const g = new THREE.Group();
                    const b = new THREE.Mesh(new THREE.BoxGeometry(15, 12, 18), new THREE.MeshStandardMaterial({{color: 0xdbad76}}));
                    b.position.y = 6;
                    const r = new THREE.Mesh(new THREE.ConeGeometry(14, 10, 4), new THREE.MeshStandardMaterial({{color: 0x5a2d0c}}));
                    r.position.y = 17;
                    r.rotation.y = Math.PI / 4;
                    g.add(b, r);
                    g.position.set(x, 0, z);
                    scene.add(g);
                }};
                createHouse(0, 0);

                // Trees
                const treeCount = data.tree_count || 20;
                for(let i=0; i<treeCount; i++) {{
                    const tx = (Math.random() - 0.5) * (L * 0.8);
                    const tz = (Math.random() - 0.5) * (W * 0.8);
                    if (Math.abs(tx) > 15 || Math.abs(tz) > 15) {{ // घर के ऊपर पेड़ न आए
                        const trunk = new THREE.Mesh(new THREE.CylinderGeometry(1.5, 1.5, 8), new THREE.MeshStandardMaterial({{color: 0x4d2911}}));
                        const leaves = new THREE.Mesh(new THREE.SphereGeometry(6), new THREE.MeshStandardMaterial({{color: 0x228b22}}));
                        trunk.position.set(tx, 4, tz);
                        leaves.position.set(tx, 12, tz);
                        scene.add(trunk, leaves);
                    }}
                }}

                // --- 4. CONTROLS ---
                const controls = new THREE.OrbitControls(camera, renderer.domElement);
                camera.position.set(L, L*0.8, L);
                controls.enableDamping = true;
                controls.update();

                // --- 5. RENDER LOOP ---
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
