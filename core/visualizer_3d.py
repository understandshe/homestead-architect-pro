import streamlit as st
import json

class Visualizer3D:
    def create(self, layout_data: dict):
        # Python data to JSON for JS to read
        json_layout = json.dumps(layout_data)
        
        # GitHub Assets Path
        github_base = "https://raw.githubusercontent.com/understandshe/homestead-architect-pro/main/assets"
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ margin: 0; background: #cce0ff; overflow: hidden; }}
                #ui {{ position: absolute; top: 15px; left: 15px; color: white; background: rgba(0,0,0,0.8); 
                       padding: 15px; border-radius: 12px; font-family: sans-serif; pointer-events: none;
                       border: 1px solid rgba(255,255,255,0.2); }}
            </style>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        </head>
        <body>
            <div id="ui">
                <b>🚀 Architect Pro 2026</b><br>
                Plot: {layout_data.get('dimensions', {}).get('L', 100)}x{layout_data.get('dimensions', {}).get('W', 100)} ft
            </div>
            
            <script>
                // --- 1. SETUP PREMIMUM RENDERER ---
                const data = {json_layout};
                const L = data.dimensions?.L || 100;
                const W = data.dimensions?.W || 100;

                const scene = new THREE.Scene();
                // Sky with slight gradient
                scene.background = new THREE.Color(0xaec6cf);
                scene.fog = new THREE.Fog(0xcce0ff, 50, 1500);

                const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 1, 10000);
                
                const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
                renderer.setSize(window.innerWidth, window.innerHeight);
                renderer.setPixelRatio(window.devicePixelRatio);
                
                // CRITICAL FOR REALISM (PBR & Tone Mapping)
                renderer.physicallyCorrectLights = true; 
                renderer.outputEncoding = THREE.sRGBEncoding;
                renderer.toneMapping = THREE.ACESFilmicToneMapping;
                renderer.toneMappingExposure = 1.3;
                
                renderer.shadowMap.enabled = true;
                renderer.shadowMap.type = THREE.PCFSoftShadowMap;
                document.body.appendChild(renderer.domElement);

                // --- 2. ADVANCED LIGHTING ---
                scene.add(new THREE.AmbientLight(0xffffff, 0.6));
                
                const sun = new THREE.DirectionalLight(0xffffff, 2.0);
                sun.position.set(L, 200, W);
                sun.castShadow = true;
                // Sharper shadow map
                sun.shadow.mapSize.width = 2048;
                sun.shadow.mapSize.height = 2048;
                sun.shadow.camera.near = 10;
                sun.shadow.camera.far = 1000;
                sun.shadow.camera.left = -L;
                sun.shadow.camera.right = L;
                sun.shadow.camera.top = W;
                sun.shadow.camera.bottom = -W;
                scene.add(sun);

                // --- 3. DYNAMIC MATERIALS (PBR) ---
                const mat = (c, r, m = 0.1, o = {{}}) => {{
                    return new THREE.MeshStandardMaterial({{ color: c, roughness: r, metalness: m, ...o }});
                }};

                // GROUND (Realistic Grass Texture look via color & roughness)
                const groundGeo = new THREE.PlaneGeometry(L, W);
                const groundMat = mat(0x567d46, 0.9, 0.05); // High Roughness
                const ground = new THREE.Mesh(groundGeo, groundMat);
                ground.rotation.x = -Math.PI / 2;
                ground.receiveShadow = true;
                scene.add(ground);

                // --- 4. REALISTIC MODELS (In-Built PBR) ---
                // House
                const createHouse = () => {{
                    const g = new THREE.Group();
                    // Beige Walls (Slightly rough)
                    const body = new THREE.Mesh(new THREE.BoxGeometry(22, 14, 18), mat(0xe0e0e0, 0.8));
                    body.position.y = 7; body.castShadow = true;
                    // Dark Roof (Rough & Matte)
                    const roof = new THREE.Mesh(new THREE.ConeGeometry(18, 10, 4), mat(0x4b2c20, 0.7));
                    roof.position.y = 19; roof.rotation.y = Math.PI / 4; roof.castShadow = true;
                    g.add(body, roof);
                    
                    // Position Sync from 2D
                    const hPos = data.house_position || 'Center';
                    if(hPos === 'West') g.position.x = -L/3;
                    if(hPos === 'East') g.position.x = L/3;
                    if(hPos === 'North') g.position.z = -W/3;
                    if(hPos === 'South') g.position.z = W/3;
                    
                    scene.add(g);
                }};
                createHouse();

                // Pond
                if(data.features?.pond) {{
                    const p = data.features.pond;
                    // Shiny and Transparent Water
                    const pondGeo = new THREE.CircleGeometry(p.radius, 32);
                    const pondMat = mat(0x0077be, 0.1, 0.8, {{ transparent: true, opacity: 0.8 }});
                    const pond = new THREE.Mesh(pondGeo, pondMat);
                    pond.rotation.x = -Math.PI / 2;
                    pond.position.set(p.x - L/2, 0.1, p.y - W/2);
                    scene.add(pond);
                }}

                // Trees
                const treePlacements = data.tree_placements || [];
                treePlacements.forEach(t => {{
                    const g = new THREE.Group();
                    // Rough Bark
                    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.5, 8), mat(0x3d2b1f, 1));
                    trunk.position.y = 4; trunk.castShadow = true;
                    // Dark matte leaves
                    const leaves = new THREE.Mesh(new THREE.SphereGeometry(6), mat(0x2d5a27, 0.9));
                    leaves.position.y = 12; leaves.castShadow = true;
                    g.add(trunk, leaves);
                    g.position.set(t.x - L/2, 0, t.y - W/2);
                    scene.add(g);
                }});

                // --- 5. CONTROLS ---
                const controls = new THREE.OrbitControls(camera, renderer.domElement);
                camera.position.set(L, L*0.6, L);
                controls.enableDamping = true;
                controls.dampingFactor = 0.05;

                // --- 6. RENDER LOOP ---
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
