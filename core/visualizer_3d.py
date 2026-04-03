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
</style>
</head>

<body>

<script type="module">

import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.128/build/three.module.js';
import {{ OrbitControls }} from 'https://cdn.jsdelivr.net/npm/three@0.128/examples/jsm/controls/OrbitControls.js';

/* ========= DATA ========= */
const data = {json_layout};
const L = data.dimensions?.L || 100;
const W = data.dimensions?.W || 100;

/* ========= SCENE ========= */
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xaec6cf);

/* ========= CAMERA ========= */
const camera = new THREE.PerspectiveCamera(60, window.innerWidth / 750, 0.1, 2000);
camera.position.set(80, 60, 80);
camera.lookAt(0, 0, 0);

/* ========= RENDERER ========= */
const renderer = new THREE.WebGLRenderer({{ antialias: true }});
const width = window.innerWidth;
const height = 750;

renderer.setSize(width, height);
renderer.setPixelRatio(window.devicePixelRatio);
renderer.shadowMap.enabled = true;

document.body.appendChild(renderer.domElement);

/* ========= LIGHT ========= */
const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 1);
scene.add(hemiLight);

const sun = new THREE.DirectionalLight(0xffffff, 1.2);
sun.position.set(50, 100, 50);
sun.castShadow = true;
scene.add(sun);

/* ========= GROUND ========= */
const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(L * 2, W * 2),
  new THREE.MeshStandardMaterial({{ color: 0x567d46 }})
);
ground.rotation.x = -Math.PI / 2;
ground.receiveShadow = true;
ground.material.side = THREE.DoubleSide;
scene.add(ground);

/* ========= DEBUG CUBE ========= */
const cube = new THREE.Mesh(
  new THREE.BoxGeometry(10, 10, 10),
  new THREE.MeshStandardMaterial({{ color: 0xff0000 }})
);
cube.position.y = 5;
scene.add(cube);

/* ========= HOUSE ========= */
const house = new THREE.Group();

const body = new THREE.Mesh(
  new THREE.BoxGeometry(20, 12, 20),
  new THREE.MeshStandardMaterial({{ color: 0xdbad76 }})
);
body.position.y = 6;
body.castShadow = true;

const roof = new THREE.Mesh(
  new THREE.ConeGeometry(16, 10, 4),
  new THREE.MeshStandardMaterial({{ color: 0x5a2d0c }})
);
roof.position.y = 17;
roof.rotation.y = Math.PI / 4;

house.add(body, roof);
scene.add(house);

/* ========= TREES ========= */
function createTree(x, z) {{
  const g = new THREE.Group();

  const trunk = new THREE.Mesh(
    new THREE.CylinderGeometry(1, 1.5, 8, 10),
    new THREE.MeshStandardMaterial({{ color: 0x4d2911 }})
  );
  trunk.position.y = 4;

  const leaves = new THREE.Mesh(
    new THREE.SphereGeometry(6, 12, 12),
    new THREE.MeshStandardMaterial({{ color: 0x2e7d32 }})
  );
  leaves.position.y = 12;

  g.add(trunk, leaves);
  g.position.set(x, 0, z);

  scene.add(g);
}}

for (let i = 0; i < 20; i++) {{
  createTree(
    (Math.random() - 0.5) * L,
    (Math.random() - 0.5) * W
  );
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
  const w = window.innerWidth;
  const h = 750;

  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h);
}});

</script>

</body>
</html>
"""

        st.components.v1.html(html_template, height=750, scrolling=True)
