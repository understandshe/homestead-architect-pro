import streamlit as st
import json

class Visualizer3D:
    """
    Homestead Architect Pro 2026 - Ultra Realistic 3D Engine.
    Fully Integrated with User Interview Data and PBR Materials.
    """
    def create(self, layout_data: dict):
        # Python डेटा को JSON में बदलें ताकि JS इसे पढ़ सके
        json_layout = json.dumps(layout_data)
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{font-family: 'Segoe UI', sans-serif; background:#0f172a; overflow:hidden;}}
        #viewer-wrap{{position:relative; width:100vw; height:750px;}}
        #three-canvas{{display:block; width:100%; height:100%}}
        
        /* Interactive HUD */
        #hud{{position:absolute; top:20px; left:20px; background:rgba(15,23,42,0.85); color:#e2e8f0;
             border-radius:12px; padding:15px; font-size:12px; border:1px solid rgba(255,255,255,0.1); 
             pointer-events:none; backdrop-filter: blur(8px);}}
        #hud b{{color:#38bdf8; font-size:14px; display:block; margin-bottom:4px;}}
        
        #toggle-bar{{position:absolute; top:20px; right:20px; display:flex; flex-direction:column; gap:8px;}}
        .tgl{{background:rgba(15,23,42,0.8); color:#f1f5f9; border:1px solid rgba(255,255,255,0.2);
              border-radius:8px; padding:10px 16px; font-size:12px; cursor:pointer; transition:0.3s;}}
        .tgl:hover{{background:#1e293b; border-color:#38bdf8;}}
        .tgl.off{{opacity:0.4; background:#000;}}
    </style>
</head>
<body>

<div id="viewer-wrap">
    <canvas id="three-canvas"></canvas>
    <div id="hud">
        <b>🌿 {layout_data.get('location', 'Custom Plot')}</b>
        <span>Size: {layout_data.get('dimensions', {}).get('L', 100)} × {layout_data.get('dimensions', {}).get('W', 100)} ft</span><br>
        <span>Engine: <span style="color:#4ade80">Realistic PBR v4</span></span>
    </div>
    <div id="toggle-bar">
        <button class="tgl" onclick="toggleLayer('house',this)">🏡 House</button>
        <button class="tgl" onclick="toggleLayer('trees',this)">🌳 Trees</button>
        <button class="tgl" onclick="toggleLayer('water',this)">💧 Systems</button>
    </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

<script>
    let scene, camera, renderer, controls;
    const layers = {{}};
    const data = {json_layout}; // User Data Loading
    const L = data.dimensions?.L || 100;
    const W = data.dimensions?.W || 100;

    /* ========= MODEL HELPERS (User's Realistic Logic) ========= */
    const mat = (c, r=0.7, m=0.2) => new THREE.MeshStandardMaterial({{ color: c, roughness: r, metalness: m }});
    
    function init() {{
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0xaec6cf);
        scene.fog = new THREE.FogExp2(0xc9e8f5, 0.0008);

        camera = new THREE.PerspectiveCamera(55, window.innerWidth / 750, 1, 10000);
        camera.position.set(L, L*0.6, W);

        renderer = new THREE.WebGLRenderer({{ canvas: document.getElementById('three-canvas'), antialias: true }});
        renderer.setSize(window.innerWidth, 750);
        renderer.setPixelRatio(window.devicePixelRatio);
        
        // --- PRO SHADOWS & LIGHTING ---
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.outputEncoding = THREE.sRGBEncoding;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;

        scene.add(new THREE.AmbientLight(0xffffff, 0.5));
        const sun = new THREE.DirectionalLight(0xffffff, 1.5);
        sun.position.set(L, 300, W/2);
        sun.castShadow = true;
        sun.shadow.mapSize.set(2048, 2048);
        scene.add(sun);

        // Ground
        const ground = new THREE.Mesh(
            new THREE.PlaneGeometry(L * 1.5, W * 1.5),
            mat(0x4a7c59, 0.9, 0.05)
        );
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        scene.add(ground);

        buildUserScene();

        controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        animate();
    }}

    function buildUserScene() {{
        // 1. HOUSE (Synced with User Choice)
        const houseGroup = new THREE.Group();
        const body = new THREE.Mesh(new THREE.BoxGeometry(22, 14, 18), mat(0xefebe9));
        body.position.y = 7; body.castShadow = true;
        const roof = new THREE.Mesh(new THREE.ConeGeometry(18, 12, 4), mat(0x4b2c20));
        roof.position.y = 19; roof.rotation.y = Math.PI/4; roof.castShadow = true;
        houseGroup.add(body, roof);
        
        // Dynamic Placement
        if(data.house_position === 'North') houseGroup.position.z = -W*0.3;
        else if(data.house_position === 'South') houseGroup.position.z = W*0.3;
        else if(data.house_position === 'West') houseGroup.position.x = -L*0.3;
        else if(data.house_position === 'East') houseGroup.position.x = L*0.3;
        
        layers['house'] = houseGroup;
        scene.add(houseGroup);

        // 2. TREES (Synced with Slider)
        const treeGroup = new THREE.Group();
        const treeCount = data.tree_count || 0;
        for(let i=0; i<treeCount; i++) {{
            const tx = (Math.random() - 0.5) * (L * 0.8);
            const tz = (Math.random() - 0.5) * (W * 0.8);
            const g = new THREE.Group();
            const trunk = new THREE.Mesh(new THREE.CylinderGeometry(1, 1.2, 8), mat(0x3d2b1f));
            trunk.position.y = 4; trunk.castShadow = true;
            const leaves = new THREE.Mesh(new THREE.SphereGeometry(6), mat(0x2d5a27, 0.9));
            leaves.position.y = 12; leaves.castShadow = true;
            g.add(trunk, leaves); g.position.set(tx, 0, tz);
            treeGroup.add(g);
        }}
        layers['trees'] = treeGroup;
        scene.add(treeGroup);

        // 3. WATER & ANIMALS (Conditional)
        const waterGroup = new THREE.Group();
        if(data.livestock && data.livestock.includes('Fish')) {{
            const pond = new THREE.Mesh(new THREE.CircleGeometry(15, 32), mat(0x0077be, 0.1, 0.8));
            pond.rotation.x = -Math.PI/2; pond.position.set(-L*0.2, 0.1, W*0.2);
            waterGroup.add(pond);
        }}
        layers['water'] = waterGroup;
        scene.add(waterGroup);
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
