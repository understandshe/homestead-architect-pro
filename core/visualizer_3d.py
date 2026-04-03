import streamlit as st
import json

class Visualizer3D:
    """
    High-Performance 3D Engine for Homestead Architect Pro 2026.
    Integrated with Realistic PBR Textures and Interactive UI.
    """
    def create(self, layout_data: dict):
        # Python dictionary को JSON string में बदलना ताकि JS उसे पढ़ सके
        json_layout = json.dumps(layout_data)
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{font-family: 'Segoe UI', Tahoma, sans-serif; background:#0f172a; overflow:hidden;}}
        #viewer-wrap{{position:relative; width:100vw; height:750px;}}
        #three-canvas{{display:block; width:100%; height:100%}}
        
        /* Professional HUD Overlay */
        #hud{{position:absolute; top:20px; left:20px; background:rgba(15,23,42,0.85); color:#e2e8f0;
             border-radius:12px; padding:15px; font-size:12px; border:1px solid rgba(255,255,255,0.1); 
             pointer-events:none; backdrop-filter: blur(4px);}}
        #hud b{{color:#38bdf8; font-size:14px; display:block; margin-bottom:4px;}}
        
        /* Interactive Toggle Sidebar */
        #toggle-bar{{position:absolute; top:20px; right:20px; display:flex; flex-direction:column; gap:8px;}}
        .tgl{{background:rgba(15,23,42,0.8); color:#f1f5f9; border:1px solid rgba(255,255,255,0.2);
              border-radius:8px; padding:10px 16px; font-size:12px; cursor:pointer; text-align:left; 
              transition:all 0.3s ease;}}
        .tgl:hover{{background:#1e293b; border-color:#38bdf8; transform: translateX(-5px);}}
        .tgl.off{{opacity:0.4; background:#000; border-color: transparent;}}

        /* Map Legend */
        #legend{{position:absolute; bottom:20px; left:20px; background:rgba(15,23,42,0.8); color:#e2e8f0;
                border-radius:10px; padding:12px; font-size:11px; border:1px solid rgba(255,255,255,0.1);}}
        .ldot{{display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:8px; vertical-align:middle;}}
    </style>
</head>
<body>

<div id="viewer-wrap">
    <canvas id="three-canvas"></canvas>
    
    <div id="hud">
        <b>🌿 {layout_data.get('location', 'Custom Homestead')}</b>
        <span>Size: {layout_data.get('dimensions', {}).get('L', 100)} × {layout_data.get('dimensions', {}).get('W', 100)} ft</span><br>
        <span>Engine: <span style="color:#4ade80">PBR Realistic v3</span></span>
    </div>

    <div id="toggle-bar">
        <button class="tgl" onclick="toggleLayer('house',this)">🏡 Main House</button>
        <button class="tgl" onclick="toggleLayer('trees',this)">🌳 Food Forest</button>
        <button class="tgl" onclick="toggleLayer('water',this)">💧 Water Systems</button>
        <button class="tgl" onclick="toggleLayer('energy',this)">☀️ Solar/Wind</button>
    </div>

    <div id="legend">
        <div><span class="ldot" style="background:#4ade80"></span>Agriculture Zone</div>
        <div><span class="ldot" style="background:#60a5fa"></span>Water Source</div>
        <div><span class="ldot" style="background:#f87171"></span>Living Quarters</div>
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
        // 1. Scene & Environment
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0xaec6cf);
        scene.fog = new THREE.FogExp2(0xc9e8f5, 0.0008);

        // 2. Camera Setup
        camera = new THREE.PerspectiveCamera(55, window.innerWidth / 750, 1, 10000);
        camera.position.set(L*0.8, L*0.6, W*0.8);

        // 3. Renderer with Realism Settings
        renderer = new THREE.WebGLRenderer({{ 
            canvas: document.getElementById('three-canvas'),
            antialias: true,
            alpha: true
        }});
        renderer.setSize(window.innerWidth, 750);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.outputEncoding = THREE.sRGBEncoding;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.25;

        // 4. Lights
        scene.add(new THREE.AmbientLight(0xffffff, 0.5));
        const sun = new THREE.DirectionalLight(0xfff5e0, 1.5);
        sun.position.set(L, 250, W/2);
        sun.castShadow = true;
        sun.shadow.mapSize.set(2048, 2048);
        scene.add(sun);

        // 5. Ground
        const ground = new THREE.Mesh(
            new THREE.PlaneGeometry(L * 2, W * 2),
            new THREE.MeshStandardMaterial({{ color: 0x4a7c59, roughness: 0.85, metalness: 0.05 }})
        );
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        scene.add(ground);

        buildHomestead();

        // 6. Interaction
        controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.maxDistance = Math.max(L, W) * 3;
        
        animate();
    }}

    function buildHomestead() {{
        // --- HOUSE LAYER ---
        const houseGroup = new THREE.Group();
        const body = new THREE.Mesh(new THREE.BoxGeometry(22, 14, 18), new THREE.MeshStandardMaterial({{color: 0xefebe9, roughness: 0.6}}));
        body.position.y = 7; body.castShadow = true;
        const roof = new THREE.Mesh(new THREE.ConeGeometry(18, 12, 4), new THREE.MeshStandardMaterial({{color: 0x4b2c20, roughness: 0.8}}));
        roof.position.y = 19; roof.rotation.y = Math.PI/4; roof.castShadow = true;
        houseGroup.add(body, roof);
        
        // Sync Placement
        if(data.house_position === 'West') houseGroup.position.x = -L/3;
        else if(data.house_position === 'East') houseGroup.position.x = L/3;
        else if(data.house_position === 'North') houseGroup.position.z = -W/3;
        else if(data.house_position === 'South') houseGroup.position.z = W/3;
        
        layers['house'] = houseGroup;
        scene.add(houseGroup);

        // --- TREES LAYER ---
        const treeGroup = new THREE.Group();
        const treeCount = data.tree_count || 15;
        for(let i=0; i<treeCount; i++) {{
            const tx = (Math.random() - 0.5) * (L * 0.9);
            const tz = (Math.random() - 0.5) * (W * 0.9);
            if(Math.abs(tx - houseGroup.position.x) > 25 || Math.abs(tz - houseGroup.position.z) > 25) {{
                const g = new THREE.Group();
                const trunk = new THREE.Mesh(new THREE.CylinderGeometry(1, 1.2, 8), new THREE.MeshStandardMaterial({{color: 0x3d2b1f}}));
                trunk.position.y = 4; trunk.castShadow = true;
                const leaves = new THREE.Mesh(new THREE.SphereGeometry(6), new THREE.MeshStandardMaterial({{color: 0x2d5a27, roughness: 0.9}}));
                leaves.position.y = 12; leaves.castShadow = true;
                g.add(trunk, leaves); 
                g.position.set(tx, 0, tz);
                treeGroup.add(g);
            }}
        }}
        layers['trees'] = treeGroup;
        scene.add(treeGroup);

        // --- WATER LAYER ---
        const waterGroup = new THREE.Group();
        if(data.features?.pond) {{
            const p = data.features.pond;
            const pond = new THREE.Mesh(new THREE.CircleGeometry(15, 32), new THREE.MeshStandardMaterial({{color: 0x0077be, transparent:true, opacity:0.7, metalness:0.8, roughness:0.1}}));
            pond.rotation.x = -Math.PI/2; pond.position.set(-L/4, 0.1, W/4);
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
        # Streamlit HTML Component
        st.components.v1.html(html_template, height=780, scrolling=False)
