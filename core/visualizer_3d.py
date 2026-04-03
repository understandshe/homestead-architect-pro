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
body {{ margin:0; overflow:hidden; background:#000; }}
canvas {{ display:block; }}
#ui {{
 position:absolute;
 top:15px;
 left:15px;
 color:white;
 background:rgba(0,0,0,0.7);
 padding:10px;
 border-radius:6px;
 font-family:sans-serif;
}}
</style>
</head>

<body>

<div id="ui">🚀 Architect Pro 2026</div>

<script type="module">

import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.128/build/three.module.js';
import {{ OrbitControls }} from 'https://cdn.jsdelivr.net/npm/three@0.128/examples/jsm/controls/OrbitControls.js';

const data = {json_layout};
const L = data.dimensions?.L || 100;
const W = data.dimensions?.W || 100;

/* ========= SCENE ========= */
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xaec6cf);

/* ========= CAMERA ========= */
const camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 2000);
camera.position.set(L, L*0.8, L);
camera.lookAt(0,0,0);

/* ========= RENDERER ========= */
const renderer = new THREE.WebGLRenderer({{ antialias:true }});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);

renderer.physicallyCorrectLights = true;
renderer.outputEncoding = THREE.sRGBEncoding;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;

renderer.shadowMap.enabled = true;

document.body.appendChild(renderer.domElement);

/* ========= LIGHT ========= */
const sun = new THREE.DirectionalLight(0xffffff, 1.5);
sun.position.set(L, 150, W/2);
sun.castShadow = true;

sun.shadow.mapSize.width = 2048;
sun.shadow.mapSize.height = 2048;

scene.add(sun);

scene.add(new THREE.AmbientLight(0xffffff, 0.4));

/* ========= GROUND ========= */
const ground = new THREE.Mesh(
 new THREE.PlaneGeometry(L*2, W*2),
 new THREE.MeshStandardMaterial({{ color:0x567d46, roughness:1 }})
);

ground.rotation.x = -Math.PI/2;
ground.receiveShadow = true;

scene.add(ground);

/* ========= HELPERS ========= */
const mat = (c) => new THREE.MeshStandardMaterial({{
 color:c,
 roughness:0.7,
 metalness:0.2
}});

/* ========= HOUSE ========= */
const createHouse = (x,z) => {{
 const g = new THREE.Group();

 const body = new THREE.Mesh(
   new THREE.BoxGeometry(20,12,20),
   mat(0xdbad76)
 );
 body.position.y = 6;
 body.castShadow = true;

 const roof = new THREE.Mesh(
   new THREE.ConeGeometry(16,10,4),
   mat(0x5a2d0c)
 );
 roof.position.y = 17;
 roof.rotation.y = Math.PI/4;
 roof.castShadow = true;

 g.add(body, roof);
 g.position.set(x,0,z);

 scene.add(g);
}};

/* ========= TREE ========= */
const createTree = (x,z) => {{
 const g = new THREE.Group();

 const trunk = new THREE.Mesh(
   new THREE.CylinderGeometry(1,1.5,8,10),
   mat(0x4d2911)
 );
 trunk.position.y = 4;
 trunk.castShadow = true;

 const leaves = new THREE.Mesh(
   new THREE.SphereGeometry(6,12,12),
   mat(0x2e7d32)
 );
 leaves.position.y = 12;
 leaves.castShadow = true;

 g.add(trunk, leaves);
 g.position.set(x,0,z);

 scene.add(g);
}};

/* ========= DATA ========= */
const hPos = data.house_position || "Center";
let hX = 0, hZ = 0;

if(hPos === "North") hZ = -W/3;
if(hPos === "South") hZ = W/3;

createHouse(hX, hZ);

/* ========= TREES ========= */
const treeCount = data.tree_count || 20;

for(let i=0;i<treeCount;i++) {{
 const tx = (Math.random()-0.5)*(L*0.9);
 const tz = (Math.random()-0.5)*(W*0.9);

 if(Math.abs(tx-hX)>20 || Math.abs(tz-hZ)>20)
   createTree(tx,tz);
}}

/* ========= CONTROLS ========= */
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

/* ========= LOOP ========= */
function animate() {{
 requestAnimationFrame(animate);
 controls.update();
 renderer.render(scene, camera);
}}

animate();

/* ========= RESIZE ========= */
window.addEventListener('resize', () => {{
 camera.aspect = window.innerWidth / window.innerHeight;
 camera.updateProjectionMatrix();
 renderer.setSize(window.innerWidth, window.innerHeight);
}});

</script>
</body>
</html>
"""

        st.components.v1.html(html_template, height=750, scrolling=True)
        
