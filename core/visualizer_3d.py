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
        body {{ margin: 0; background: #cce0ff; overflow: hidden; }}
        #ui {{ position: absolute; top: 15px; left: 15px; color: white; background: rgba(0,0,0,0.8); 
               padding: 15px; border-radius: 12px; font-family: sans-serif; pointer-events: none; }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="ui">🚀 <b>Architect Pro 2026</b> | Realistic Mode</div>
    
    <script>
        const data = {json_layout};
        const L = data.dimensions?.L || 100;
        const W = data.dimensions?.W || 100;

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0xaec6cf);
        // Realistic Fog (धुंध से गहराई आती है)
        scene.fog = new THREE.Fog(0xcce0ff, 100, 1500);

        const camera = new THREE.PerspectiveCamera(50, window.innerWidth / 750, 1, 10000);
        camera.position.set(L, L*0.6, L);

        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth, 750);
        
        // --- REALISM SETTINGS (यही सबसे ज़रूरी है) ---
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap; // सॉफ्ट परछाई
        renderer.outputEncoding = THREE.sRGBEncoding; // असली रंग
        renderer.toneMapping = THREE.ACESFilmicToneMapping; // सिनेमाई लुक
        renderer.toneMappingExposure = 1.2;

        document.body.appendChild(renderer.domElement);

        // --- LIGHTING (सफ़ेद लाइट के बजाय सूरज की रोशनी) ---
        scene.add(new THREE.AmbientLight(0xffffff, 0.4)); // हल्की रोशनी हर तरफ
        
        const sun = new THREE.DirectionalLight(0xffffff, 1.5);
        sun.position.set(L, 200, W);
        sun.castShadow = true;
        // परछाई को साफ़ बनाने के लिए Resolution बढ़ाना
        sun.shadow.mapSize.width = 2048;
        sun.shadow.mapSize.height = 2048;
        scene.add(sun);

        // --- GROUND (Texture की जगह Gradient Mesh) ---
        const ground = new THREE.Mesh(
            new THREE.PlaneGeometry(L*2, W*2),
            new THREE.MeshStandardMaterial({{ color: 0x567d46, roughness: 0.8, metalness: 0.1 }})
        );
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true; // ज़मीन पर परछाईं गिरेगी
        scene.add(ground);

        // --- यहाँ तेरे library.js के मॉडल्स कॉल होंगे ---
        // अभी के लिए एक Demo House (Shadows के साथ)
        const body = new THREE.Mesh(new THREE.BoxGeometry(20, 12, 20), new THREE.MeshStandardMaterial({{ color: 0xdbad76, roughness: 0.7 }}));
        body.position.y = 6;
        body.castShadow = true; // घर परछाईं बनाएगा
        scene.add(body);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;

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
