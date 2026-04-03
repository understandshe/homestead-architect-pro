import streamlit as st
import json

class Visualizer3D:
    def create(self, layout_data: dict):
        # Python data to JSON for the JavaScript logic
        json_layout = json.dumps(layout_data)
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Homestead 3D Designer Pro</title>
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{font-family:sans-serif;background:#0f172a;overflow:hidden;}}
        #viewer-wrap{{position:relative; width:100vw; height:750px;}}
        #three-canvas{{display:block;width:100%;height:100%}}
        
        /* UI Panels */
        #hud{{position:absolute;top:20px;left:20px;background:rgba(15,23,42,0.85);color:#e2e8f0;
             border-radius:12px;padding:15px;font-size:12px;border:1px solid rgba(255,255,255,0.1);pointer-events:none;}}
        #hud b{{color:#38bdf8;font-size:14px;}}
        
        #toggle-bar{{position:absolute;top:20px;right:20px;display:flex;flex-direction:column;gap:8px;}}
        .tgl{{background:rgba(15,23,42,0.8);color:#f1f5f9;border:1px solid rgba(255,255,255,0.2);
              border-radius:8px;padding:8px 15px;font-size:12px;cursor:pointer;text-align:left;transition:0.2s;}}
        .tgl:hover{{background:#1e293b; border-color:#38bdf8;}}
        .tgl.off{{opacity:0.4; background:#000;}}

        #legend{{position:absolute;bottom:20px;left:20px;background:rgba(15,23,42,0.8);color:#e2e8f0;
                border-radius:10px;padding:12px;font-size:11px;border:1px solid rgba(255,255,255,0.1);}}
        .ldot{{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:8px;}}
    </style>
</head>
<body>

<div id="viewer-wrap">
    <canvas id="three-canvas"></canvas>
    
    <div id="hud">
        <b>🌿 {layout_data.get('location', 'Global Homestead')}</b><br/>
        <span>Dimensions: {layout_data.get('dimensions', {}).get('L', 100)}x{layout_data.get('dimensions', {}).get('W', 100)} ft</span><br>
        <span>Status: <span style="color:#4ade80">Realistic Engine Active</span></span>
    </div>

    <div id="toggle-bar">
        <button class="tgl" onclick="toggleLayer('house',this)">🏡 Main House</button>
        <button class="tgl" onclick="toggleLayer('trees',this)">🌳 Fruit Trees</button>
        <button class="tgl" onclick="toggleLayer('water',this)">💧 Water Systems</button>
        <button class="tgl" onclick="toggleLayer('solar',this)">☀️ Energy Array</button>
    </div>

    <div id="legend">
        <span class="ldot" style="background:#4ade80"></span>Food Forest<br>
        <span class="ldot" style="background:#60a5fa"></span>Aquaculture<br>
        <span class="ldot" style="background:#f87171"></span>Residential
    </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

<script>
    let scene, camera, renderer, controls;
    const layers = {{}};
    const data = {json_layout};
    const L = data.dimensions?.L || 100;
    const W = data.dimensions?.W || 100;

    function init() {{
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0xaec6cf);
        scene.fog = new THREE.FogExp2(0xc9e8f5, 0.001);

        camera = new THREE.PerspectiveCamera(50, window.innerWidth / 750, 1, 10000);
        camera.position.set(L, L*0.7, W);

        renderer = new THREE.WebGLRenderer({{ 
            canvas: document.getElementById('three-canvas'),
            antialias: true 
        }});
        renderer.setSize(window.innerWidth, 750);
        renderer.setPixelRatio(window.devicePixelRatio);
        
        // --- REALISM SETTINGS ---
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.outputEncoding = THREE.sRGBEncoding;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.2;

        // Lights
        const ambient = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambient);
        
        const sun = new THREE.DirectionalLight(0xffffff, 1.5);
        sun.position.set(L, 200, W);
        sun.castShadow = true;
        sun.shadow.mapSize.set(2048, 2048);
        scene.add(sun);

        // Ground
        const ground = new THREE.Mesh(
            new THREE.PlaneGeometry(L, W),
            new THREE.MeshStandardMaterial({{ color: 0x4a7c59, roughness: 0.8 }})
        );
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        scene.add(ground);

        buildModels();

        controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        
        animate();
    }}

    function buildModels() {{
        // House Layer
        const houseLayer = new THREE.Group();
        const body = new THREE.Mesh(new THREE.BoxGeometry(20, 12, 18), new THREE.MeshStandardMaterial({{color: 0xefebe9, roughness: 0.7}}));
        body.position.y = 6; body.castShadow = true;
        const roof = new THREE.Mesh(new THREE.ConeGeometry(16, 10, 4), new THREE.MeshStandardMaterial({{color: 0x3e2723, roughness: 0.8}}));
        roof.position.y = 17; roof.rotation.y = Math.PI/4; roof.castShadow = true;
        houseLayer.add(body, roof);
        
        // Placement logic based on data
        if(data.house_position === 'West') houseLayer.position.x = -L/3;
        if(data.house_position === 'East') houseLayer.position.x = L/3;
        
        layers['house'] = houseLayer;
        scene.add(houseLayer);

        // Trees Layer
        const treeLayer = new THREE.Group();
        const treeCount = data.tree_count || 15;
        for(let i=0; i<treeCount; i++) {{
            const tx = (Math.random() - 0.5) * (L - 40);
            const tz = (Math.random() - 0.5) * (W - 40);
            const g = new THREE.Group();
            const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.8, 1, 6), new THREE.MeshStandardMaterial({{color: 0x4d2911}}));
            trunk.position.y = 3; trunk.castShadow = true;
            const leaves = new THREE.Mesh(new THREE.SphereGeometry(5), new THREE.MeshStandardMaterial({{color: 0x2e7d32, roughness: 0.9}}));
            leaves.position.y = 10; leaves.castShadow = true;
            g.add(trunk, leaves); g.position.set(tx, 0, tz);
            treeLayer.add(g);
        }}
        layers['trees'] = treeLayer;
        scene.add(treeLayer);
    }}

    window.toggleLayer = (name, btn) => {{
        if(layers[name]) {{
            layers[name].visible = !layers[name].visible;
            btn.classList.toggle('off', !layers[name].visible);
        }}
    }};

    function animate() {{
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }}

    init();
    
    window.addEventListener('resize', () => {{
        camera.aspect = window.innerWidth / 750;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, 750);
    }});
</script>
</body>
</html>
"""
        st.components.v1.html(html_template, height=780)
