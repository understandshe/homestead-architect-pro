"""
Homestead Architect Pro 2026 - Interactive 3D Engine v5.1
Features: 3D Labels, Fullscreen Map, Toggle HUD, and HTML Export.
"""

import streamlit as st
import json

class Visualizer3D:
    def create(self, layout_data: dict):
        # डेटा सेफ्टी चेक
        if not layout_data or 'dimensions' not in layout_data:
            st.info("👈 पहले 'Design' टैब में अपना नक्शा जनरेट करें।")
            return

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
        
        /* Interactive HUD Panel */
        #hud{{position:absolute; top:20px; left:20px; background:rgba(15,23,42,0.85); color:#e2e8f0;
             border-radius:12px; padding:15px; font-size:12px; border:1px solid rgba(255,255,255,0.1); 
             backdrop-filter: blur(8px); transition: 0.3s; z-index: 100;}}
        #hud.hidden{{transform: translateX(-150%); opacity: 0;}}
        #hud b{{color:#38bdf8; font-size:14px; display:block; margin-bottom:4px;}}
        
        /* Control Buttons */
        #controls{{position:absolute; top:20px; right:20px; display:flex; flex-direction:column; gap:8px; z-index: 100;}}
        .btn{{background:rgba(15,23,42,0.8); color:#f1f5f9; border:1px solid rgba(255,255,255,0.2);
              border-radius:8px; padding:10px 16px; font-size:12px; cursor:pointer; transition:0.3s; text-align:center;}}
        .btn:hover{{background:#1e293b; border-color:#38bdf8;}}
        .btn.download{{background:#166534; border-color:#4ade80; font-weight:bold;}}
        
        /* 3D Labels Style */
        .label{{color: white; background: rgba(0,0,0,0.6); padding: 2px 6px; border-radius: 4px; 
               font-size: 10px; pointer-events: none; white-space: nowrap; border: 1px solid rgba(255,255,255,0.2);}}
    </style>
</head>
<body>

<div id="viewer-wrap">
    <canvas id="three-canvas"></canvas>
    
    <div id="hud" id="main-hud">
        <b>🌿 {layout_data.get('location', 'Custom Plot')}</b>
        <span>Size: {layout_data.get('dimensions', {}).get('L', 100)} × {layout_data.get('dimensions', {}).get('W', 100)} ft</span><br>
        <span>Engine: <span style="color:#4ade80">Realistic v5.1</span></span>
    </div>

    <div id="controls">
        <button class="btn" onclick="toggleHUD()">👁️ Toggle Data Panel</button>
        <button class="btn download" onclick="downloadHTML()">📥 Download 3D HTML</button>
    </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

<script>
    let scene, camera, renderer, controls;
    const data = {json_layout}; 
    const L = data.dimensions?.L || 100;
    const W = data.dimensions?.W || 100;

    function init() {{
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0xaec6cf);
        
        camera = new THREE.PerspectiveCamera(55, window.innerWidth / 750, 1, 10000);
        camera.position.set(L, L*0.6, W);

        renderer = new THREE.WebGLRenderer({{ canvas: document.getElementById('three-canvas'), antialias: true }});
        renderer.setSize(window.innerWidth, 750);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;

        // Lighting
        scene.add(new THREE.AmbientLight(0xffffff, 0.5));
        const sun = new THREE.DirectionalLight(0xffffff, 1.2);
        sun.position.set(L, 300, W/2);
        sun.castShadow = true;
        scene.add(sun);

        // Ground
        const ground = new THREE.Mesh(
            new THREE.PlaneGeometry(L * 1.5, W * 1.5),
            new THREE.MeshStandardMaterial({{ color: 0x4a7c59, roughness: 0.8 }})
        );
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        scene.add(ground);

        buildScene();

        controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        animate();
    }}

    function createLabel(text, x, y, z) {{
        const div = document.createElement('div');
        div.className = 'label';
        div.textContent = text;
        div.style.position = 'absolute';
        div.style.pointerEvents = 'none';
        document.getElementById('viewer-wrap').appendChild(div);

        return {{
            element: div,
            position: new THREE.Vector3(x, y, z)
        }};
    }}

    const labels = [];

    function buildScene() {{
        // House
        const house = new THREE.Group();
        const body = new THREE.Mesh(new THREE.BoxGeometry(22, 14, 18), new THREE.MeshStandardMaterial({{color: 0xefebe9}}));
        body.position.y = 7; body.castShadow = true;
        const roof = new THREE.Mesh(new THREE.ConeGeometry(18, 12, 4), new THREE.MeshStandardMaterial({{color: 0x4b2c20}}));
        roof.position.y = 19; roof.rotation.y = Math.PI/4;
        house.add(body, roof);
        
        // Dynamic House Placement
        if(data.house_position === 'North') house.position.z = -W*0.3;
        else if(data.house_position === 'South') house.position.z = W*0.3;
        
        scene.add(house);
        labels.push(createLabel('🏡 Main House', house.position.x, 25, house.position.z));

        // Trees
        const treeCount = data.tree_count || 10;
        for(let i=0; i<treeCount; i++) {{
            const tx = (Math.random() - 0.5) * L;
            const tz = (Math.random() - 0.5) * W;
            const tree = new THREE.Group();
            const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.8, 1, 6), new THREE.MeshStandardMaterial({{color: 0x3d2b1f}}));
            trunk.position.y = 3; tree.add(trunk);
            const leaves = new THREE.Mesh(new THREE.SphereGeometry(5), new THREE.MeshStandardMaterial({{color: 0x2d5a27}}));
            leaves.position.y = 10; tree.add(leaves);
            tree.position.set(tx, 0, tz);
            scene.add(tree);
            if(i === 0) labels.push(createLabel('🌳 Food Forest', tx, 16, tz));
        }}
    }}

    function toggleHUD() {{
        const hud = document.getElementById('hud');
        hud.classList.toggle('hidden');
    }}

    function downloadHTML() {{
        const htmlContent = document.documentElement.outerHTML;
        const blob = new Blob([htmlContent], {{ type: 'text/html' }});
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'Homestead_3D_Design.html';
        a.click();
    }}

    function animate() {{
        requestAnimationFrame(animate);
        controls.update();
        
        // Update Labels Position [3D to 2D Mapping]
        labels.forEach(lbl => {{
            const pos = lbl.position.clone().project(camera);
            if(pos.z > 1) {{
                lbl.element.style.display = 'none';
            }} else {{
                lbl.element.style.display = 'block';
                const x = (pos.x * .5 + .5) * window.innerWidth;
                const y = (pos.y * -.5 + .5) * 750;
                lbl.element.style.left = x + 'px';
                lbl.element.style.top = y + 'px';
            }}
        }});

        renderer.render(scene, camera);
    }}

    init();
</script>
</body>
</html>
"""
        st.components.v1.html(html_template, height=780)
