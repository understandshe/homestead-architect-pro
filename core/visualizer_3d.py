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
                body {{ margin: 0; background-color: #87CEEB; overflow: hidden; }}
                #ui {{ position: absolute; top: 10px; left: 10px; color: white; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 5px; font-family: sans-serif; }}
            </style>
        </head>
        <body>
            <div id="ui">🌳 3D Realistic View - v6</div>
            <script type="module">
                import * as THREE from 'https://unpkg.com/three@0.128.0/build/three.module.js';
                import {{ OrbitControls }} from 'https://unpkg.com/three@0.128.0/examples/jsm/controls/OrbitControls.js';

                const scene = new THREE.Scene();
                scene.background = new THREE.Color(0x87CEEB);
                const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 5000);
                const renderer = new THREE.WebGLRenderer({{ antialias: true }});
                renderer.setSize(window.innerWidth, window.innerHeight);
                document.body.appendChild(renderer.domElement);

                // Lighting
                scene.add(new THREE.AmbientLight(0xffffff, 0.8));
                const sun = new THREE.DirectionalLight(0xffffff, 1);
                sun.position.set(100, 200, 100);
                scene.add(sun);

                // --- DATA ---
                const data = {json_layout};
                const L = data.dimensions?.L || 100;
                const W = data.dimensions?.W || 100;

                // --- GROUND ---
                const ground = new THREE.Mesh(
                    new THREE.PlaneGeometry(L, W),
                    new THREE.MeshStandardMaterial({{ color: 0x3d8c40 }})
                );
                ground.rotation.x = -Math.PI / 2;
                scene.add(ground);

                // --- REAL HOUSE (No more white boxes!) ---
                function createHouse(x, z) {{
                    const group = new THREE.Group();
                    const body = new THREE.Mesh(new THREE.BoxGeometry(15, 10, 15), new THREE.MeshStandardMaterial({{color: 0xdbad76}}));
                    body.position.y = 5;
                    const roof = new THREE.Mesh(new THREE.ConeGeometry(12, 8, 4), new THREE.MeshStandardMaterial({{color: 0x5a2d0c}}));
                    roof.position.y = 14;
                    roof.rotation.y = Math.PI / 4;
                    group.add(body, roof);
                    group.position.set(x, 0, z);
                    scene.add(group);
                }}
                createHouse(0, 0);

                // --- ANIMATED TREES (Based on Slider) ---
                const treeCount = data.tree_count || 15;
                for(let i=0; i<treeCount; i++) {{
                    const tx = (Math.random() - 0.5) * (L - 40);
                    const tz = (Math.random() - 0.5) * (W - 40);
                    
                    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, 5), new THREE.MeshStandardMaterial({{color: 0x4d2911}}));
                    const leaves = new THREE.Mesh(new THREE.SphereGeometry(4), new THREE.MeshStandardMaterial({{color: 0x228b22}}));
                    trunk.position.set(tx, 2.5, tz);
                    leaves.position.set(tx, 7, tz);
                    
                    scene.add(trunk, leaves);
                }}

                // --- CAMERA & CONTROLS ---
                const controls = new OrbitControls(camera, renderer.domElement);
                camera.position.set(L*0.8, L*0.6, L*0.8);
                controls.update();

                function animate() {{
                    requestAnimationFrame(animate);
                    controls.update();
                    renderer.render(scene, camera);
                }}
                animate();
            </script>
        </body>
        </html>
        """
        st.components.v1.html(html_template, height=750)
