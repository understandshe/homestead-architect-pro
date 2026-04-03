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
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#87CEEB; overflow:hidden; font-family:'Segoe UI',sans-serif; }}

  #canvas-wrap {{ position:relative; width:100%; height:750px; }}

  /* ── Premium HUD ── */
  #hud {{
    position:absolute; top:14px; left:14px; z-index:10;
    background:linear-gradient(135deg,rgba(15,23,42,0.88),rgba(30,41,59,0.82));
    border:1px solid rgba(255,255,255,0.15); border-radius:14px;
    padding:12px 16px; color:#e2e8f0; pointer-events:none;
    backdrop-filter:blur(12px); box-shadow:0 8px 32px rgba(0,0,0,0.4);
    min-width:200px;
  }}
  #hud h3 {{ font-size:13px; font-weight:700; color:#7dd3fc; letter-spacing:.5px; margin-bottom:6px; }}
  #hud .stat {{ font-size:11px; color:#94a3b8; margin-top:3px; }}
  #hud .stat span {{ color:#f1f5f9; font-weight:600; }}

  /* ── Controls ── */
  #controls {{
    position:absolute; bottom:16px; right:16px; z-index:10; display:flex; gap:8px;
  }}
  .ctrl-btn {{
    background:rgba(15,23,42,0.85); border:1px solid rgba(255,255,255,0.18);
    color:#e2e8f0; border-radius:10px; padding:8px 14px; cursor:pointer;
    font-size:12px; backdrop-filter:blur(8px); transition:all .2s;
    pointer-events:all;
  }}
  .ctrl-btn:hover {{ background:rgba(56,189,248,0.25); border-color:#38bdf8; }}

  /* ── Legend ── */
  #legend {{
    position:absolute; bottom:16px; left:14px; z-index:10;
    background:rgba(15,23,42,0.82); border:1px solid rgba(255,255,255,0.12);
    border-radius:12px; padding:10px 14px; color:#e2e8f0;
    backdrop-filter:blur(10px); font-size:11px;
  }}
  #legend .row {{ display:flex; align-items:center; gap:6px; margin-top:4px; }}
  #legend .dot {{ width:10px; height:10px; border-radius:50%; flex-shrink:0; }}

  /* ── Loading Screen ── */
  #loading {{
    position:absolute; inset:0; background:linear-gradient(135deg,#0f172a,#1e3a5f);
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    z-index:99; color:white; gap:16px;
  }}
  #loading h2 {{ font-size:20px; color:#7dd3fc; }}
  #loading p  {{ font-size:13px; color:#94a3b8; }}
  .spinner {{
    width:40px; height:40px; border:3px solid #1e40af;
    border-top-color:#38bdf8; border-radius:50%; animation:spin .8s linear infinite;
  }}
  @keyframes spin {{ to {{ transform:rotate(360deg); }} }}
</style>
</head>
<body>
<div id="canvas-wrap">

  <!-- Loading -->
  <div id="loading">
    <div class="spinner"></div>
    <h2>🌿 Rendering Homestead</h2>
    <p>Building your 3D world…</p>
  </div>

  <!-- HUD -->
  <div id="hud">
    <h3>🏡 HOMESTEAD DESIGNER PRO</h3>
    <div class="stat">Plot: <span id="s-dim">—</span></div>
    <div class="stat">Location: <span id="s-loc">—</span></div>
    <div class="stat">Water: <span id="s-water">—</span></div>
    <div class="stat">Animals: <span id="s-animals">—</span></div>
    <div class="stat">Trees: <span id="s-trees">—</span></div>
  </div>

  <!-- Zoom / Reset controls -->
  <div id="controls">
    <button class="ctrl-btn" onclick="resetCamera()">🎯 Reset View</button>
    <button class="ctrl-btn" onclick="toggleWire()">📐 Wireframe</button>
    <button class="ctrl-btn" onclick="cycleCamera()">📷 Angle</button>
  </div>

  <!-- Legend -->
  <div id="legend">
    <div class="row"><div class="dot" style="background:#4ade80"></div>Food Forest</div>
    <div class="row"><div class="dot" style="background:#fbbf24"></div>Livestock Zone</div>
    <div class="row"><div class="dot" style="background:#60a5fa"></div>Water Systems</div>
    <div class="row"><div class="dot" style="background:#f87171"></div>Living Area</div>
    <div class="row"><div class="dot" style="background:#a78bfa"></div>Garden Beds</div>
  </div>

</div>

<!-- Three.js r128 (stable CDN) -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
// ═══════════════════════════════════════════════════════════
//  DATA
// ═══════════════════════════════════════════════════════════
const DATA = {json_layout};
const L = DATA.dimensions?.L || 100;
const W = DATA.dimensions?.W || 100;
const loc = DATA.location || 'Unknown';
const water = DATA.water_source || 'Well';
const animals = (DATA.animals || []).join(', ') || 'None';
const trees = DATA.fruit_trees || 0;
const housePos = DATA.house_position || 'North';
const budget = DATA.budget || '';

// Fill HUD
document.getElementById('s-dim').textContent    = L + ' × ' + W + ' ft';
document.getElementById('s-loc').textContent    = loc;
document.getElementById('s-water').textContent  = water;
document.getElementById('s-animals').textContent= animals;
document.getElementById('s-trees').textContent  = trees + ' trees';

// ═══════════════════════════════════════════════════════════
//  SCENE SETUP
// ═══════════════════════════════════════════════════════════
const scene    = new THREE.Scene();
const W3 = window.innerWidth, H3 = 750;
const renderer = new THREE.WebGLRenderer({{ antialias:true }});
renderer.setSize(W3, H3);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type    = THREE.PCFSoftShadowMap;
renderer.outputEncoding    = THREE.sRGBEncoding;
renderer.toneMapping       = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;
document.getElementById('canvas-wrap').appendChild(renderer.domElement);

const camera = new THREE.PerspectiveCamera(52, W3/H3, 0.5, 8000);
let camAngle = 0;
const CAM_POSITIONS = [
  new THREE.Vector3(L*0.9,  L*0.55, L*0.9),
  new THREE.Vector3(0,      L*0.9,  L*1.1),
  new THREE.Vector3(-L*0.9, L*0.55, L*0.9),
  new THREE.Vector3(L*1.1,  L*0.4,  0),
];
camera.position.copy(CAM_POSITIONS[0]);
camera.lookAt(0, 0, 0);

// ── Sky Gradient (shader-less, 2-color bg) ──
const skyGeo = new THREE.SphereGeometry(3000, 8, 8);
const skyMat = new THREE.MeshBasicMaterial({{
  color:0x87CEEB, side: THREE.BackSide
}});
scene.add(new THREE.Mesh(skyGeo, skyMat));
scene.fog = new THREE.FogExp2(0xc9e8f5, 0.0008);

// ═══════════════════════════════════════════════════════════
//  LIGHTING
// ═══════════════════════════════════════════════════════════
// Sky bounce (blue top, warm ground)
const hemi = new THREE.HemisphereLight(0x87CEEB, 0x5a7a3a, 0.6);
scene.add(hemi);

// Main sun
const sun = new THREE.DirectionalLight(0xfff5e0, 2.2);
sun.position.set(L*0.8, 200, W*0.6);
sun.castShadow = true;
sun.shadow.mapSize.set(4096, 4096);
sun.shadow.camera.near   = 1;
sun.shadow.camera.far    = 1000;
sun.shadow.camera.left   = -L;
sun.shadow.camera.right  =  L;
sun.shadow.camera.top    =  W;
sun.shadow.camera.bottom = -W;
sun.shadow.bias          = -0.0003;
scene.add(sun);

// Soft fill from opposite side
const fill = new THREE.DirectionalLight(0xadd8e6, 0.4);
fill.position.set(-L, 80, -W);
scene.add(fill);

// ═══════════════════════════════════════════════════════════
//  MATERIAL FACTORY
// ═══════════════════════════════════════════════════════════
const M = (color, rough=0.75, metal=0.05, extra={{}}) =>
  new THREE.MeshStandardMaterial({{ color, roughness:rough, metalness:metal, ...extra }});

// ═══════════════════════════════════════════════════════════
//  GEOMETRY HELPERS
// ═══════════════════════════════════════════════════════════
function mkBox(w,h,d,mat) {{
  const m = new THREE.Mesh(new THREE.BoxGeometry(w,h,d), mat);
  m.castShadow = m.receiveShadow = true; return m;
}}
function mkCyl(r1,r2,h,mat,seg=16) {{
  const m = new THREE.Mesh(new THREE.CylinderGeometry(r1,r2,h,seg), mat);
  m.castShadow = m.receiveShadow = true; return m;
}}
function mkCone(r,h,mat,seg=8) {{
  const m = new THREE.Mesh(new THREE.ConeGeometry(r,h,seg), mat);
  m.castShadow = m.receiveShadow = true; return m;
}}
function mkSphere(r,mat,ws=12,hs=12) {{
  const m = new THREE.Mesh(new THREE.SphereGeometry(r,ws,hs), mat);
  m.castShadow = m.receiveShadow = true; return m;
}}
function place(obj, x, y, z) {{ obj.position.set(x,y,z); return obj; }}
function add(...objs) {{ const g=new THREE.Group(); objs.forEach(o=>g.add(o)); return g; }}

// ═══════════════════════════════════════════════════════════
//  GROUND — Zone-coloured tiles
// ═══════════════════════════════════════════════════════════
function createZonedGround() {{
  const g = new THREE.Group();

  // Base grass
  const base = mkBox(L*2.5, 0.5, W*2.5, M(0x4a7c59, 0.95, 0));
  place(base, 0, -0.25, 0); g.add(base);

  // Zone colours (semi-transparent overlays lifted slightly)
  const zones = [
    {{ x: 0,       z: -W*0.3,  w: L*0.6, d: W*0.4, color: 0xf87171, label:'living'    }}, // house area
    {{ x: -L*0.32, z:  W*0.2,  w: L*0.55, d: W*0.5, color: 0x4ade80, label:'food'      }}, // food forest
    {{ x:  L*0.32, z:  W*0.2,  w: L*0.55, d: W*0.5, color: 0xfbbf24, label:'livestock' }}, // animals
    {{ x: 0,       z:  W*0.38, w: L*0.4,  d: W*0.2, color: 0x60a5fa, label:'water'     }}, // water
    {{ x: -L*0.1,  z:  0,      w: L*0.25, d: W*0.25,color: 0xa78bfa, label:'garden'    }}, // garden
  ];
  zones.forEach(z => {{
    const overlay = mkBox(z.w, 0.15, z.d,
      M(z.color, 0.9, 0, {{ transparent:true, opacity:0.25 }}));
    place(overlay, z.x, 0.08, z.z);
    g.add(overlay);
  }});

  // Gravel path (cross shape)
  [{{ x:0,z:0,w:L*1.6,d:3 }}, {{ x:0,z:0,w:3,d:W*1.6 }}].forEach(p => {{
    const path = mkBox(p.w, 0.12, p.d, M(0xb0a090, 0.98, 0));
    place(path, p.x, 0.06, p.z); g.add(path);
  }});

  return g;
}}
scene.add(createZonedGround());

// ═══════════════════════════════════════════════════════════
//  MODELS
// ═══════════════════════════════════════════════════════════

// ── MAIN HOUSE (detailed) ──────────────────────────────────
function createHouse(x, z, scale=1) {{
  const g = new THREE.Group();

  // Foundation
  const found = mkBox(18,0.8,14, M(0x9e9e9e,0.9));
  place(found, 0, 0.4, 0); g.add(found);

  // Main body
  const body = mkBox(16, 9, 12, M(0xd4a97a, 0.78));
  place(body, 0, 5.3, 0); g.add(body);

  // Side wing
  const wing = mkBox(8, 6, 8, M(0xc8976a, 0.8));
  place(wing, -6, 3.6, -9); g.add(wing);

  // Roof (gabled — two halves)
  const roofMat = M(0x6b3a2a, 0.85);
  const roof1 = mkBox(18.5, 0.6, 7, roofMat);
  roof1.rotation.z = 0.45;
  place(roof1, -4.2, 10.5, 0); g.add(roof1);
  const roof2 = mkBox(18.5, 0.6, 7, roofMat);
  roof2.rotation.z = -0.45;
  place(roof2, 4.2, 10.5, 0); g.add(roof2);
  // Ridge beam
  const ridge = mkBox(18.5, 0.8, 1, M(0x5a2e1a,0.9));
  place(ridge, 0, 13.2, 0); g.add(ridge);

  // Wing roof
  const wingRoof = mkCone(7, 4, roofMat, 4);
  wingRoof.rotation.y = Math.PI/4;
  place(wingRoof, -6, 9, -9); g.add(wingRoof);

  // Door
  const door = mkBox(1.6, 2.8, 0.2, M(0x4a2800, 0.9));
  place(door, 0, 1.8, 6.1); g.add(door);
  // Door frame
  const dframe = mkBox(2, 3.2, 0.15, M(0x8b5e3c, 0.8));
  place(dframe, 0, 2, 6.15); g.add(dframe);

  // Windows (×4)
  [[-5,5,3],[5,5,3],[-5,5,-3],[5,5,-3]].forEach(([wx,wy,wz]) => {{
    const win = mkBox(2, 1.8, 0.15, M(0x9ecae1,0.1,0.5,{{ transparent:true,opacity:0.65 }}));
    place(win, wx, wy, wz > 0 ? 6.1 : -6.1); g.add(win);
    // Sill
    const sill = mkBox(2.4, 0.2, 0.4, M(0xffffff,0.6));
    place(sill, wx, wy-1, wz > 0 ? 6.2 : -6.2); g.add(sill);
  }});

  // Chimney
  const chimney = mkBox(1.5, 5, 1.5, M(0x8b6050, 0.9));
  place(chimney, 5, 13, -2); g.add(chimney);
  const cap = mkBox(2, 0.4, 2, M(0x555555, 0.9));
  place(cap, 5, 15.7, -2); g.add(cap);

  // Porch columns (×3)
  [-4,0,4].forEach(px => {{
    const col = mkCyl(0.25, 0.25, 2.5, M(0xf0ede8,0.7));
    place(col, px, 1.5, 6.5); g.add(col);
  }});
  // Porch roof
  const porch = mkBox(10, 0.3, 3, M(0xb07a50,0.85));
  place(porch, 0, 2.8, 7); g.add(porch);

  g.scale.setScalar(scale);
  place(g, x, 0, z);
  return g;
}}

// ── TREE (detailed, 3 types) ──────────────────────────────
function createTree(x, z, type=0, scale=1) {{
  const g = new THREE.Group();
  const trunkMat = M(0x6b4226, 0.9);

  if(type === 0) {{ // Apple / fruit
    const trunk = mkCyl(0.22, 0.3, 2.8, trunkMat);
    place(trunk, 0, 1.4, 0); g.add(trunk);
    // layered canopy for depth
    [0, 0.6, 1.1].forEach((dy, i) => {{
      const r = 1.8 - i*0.3;
      const leaf = mkSphere(r, M(0x2e7d32+i*0x050500, 0.9), 8, 8);
      place(leaf, (i-1)*0.3, 3+dy, (i%2-0.5)*0.3); g.add(leaf);
    }});
    // apples
    for(let i=0;i<5;i++) {{
      const apple = mkSphere(0.18, M(0xcc2200,0.7));
      apple.position.set(Math.sin(i*1.3)*1.2, 3.2+Math.cos(i)*0.4, Math.cos(i*1.3)*1.2);
      g.add(apple);
    }}
  }} else if(type === 1) {{ // Pine
    const trunk = mkCyl(0.18, 0.25, 3, trunkMat);
    place(trunk, 0, 1.5, 0); g.add(trunk);
    [0,1.2,2.2,3].forEach((dy, i) => {{
      const cone_ = mkCone(1.8-i*0.35, 2, M(0x1a5c1a,0.95), 8);
      place(cone_, 0, 3+dy, 0); g.add(cone_);
    }});
  }} else {{ // Mango / tropical
    const trunk = mkCyl(0.3, 0.4, 3.5, M(0x7a5030, 0.9));
    place(trunk, 0, 1.75, 0); g.add(trunk);
    const canopy = mkSphere(2.5, M(0x1b6b1b, 0.85), 8, 8);
    canopy.scale.y = 0.7;
    place(canopy, 0, 5, 0); g.add(canopy);
    // mangoes
    for(let i=0;i<6;i++) {{
      const mango = mkBox(0.25, 0.35, 0.2, M(0xffa000,0.7));
      mango.position.set(Math.sin(i)*2, 4.5, Math.cos(i)*2);
      g.add(mango);
    }}
  }}
  g.scale.setScalar(scale);
  place(g, x, 0, z);
  return g;
}}

// ── BARN ──────────────────────────────────────────────────
function createBarn(x, z) {{
  const g = new THREE.Group();
  const body = mkBox(14, 8, 10, M(0x8b1a1a, 0.85));
  place(body, 0, 4, 0); g.add(body);
  // Barn roof (pentagon shape via rotated boxes)
  const roofMat = M(0x5a1a1a, 0.9);
  const r1 = mkBox(15, 0.6, 6, roofMat); r1.rotation.z = 0.5;
  place(r1, -3.8, 9.5, 0); g.add(r1);
  const r2 = mkBox(15, 0.6, 6, roofMat); r2.rotation.z = -0.5;
  place(r2, 3.8, 9.5, 0); g.add(r2);
  // Barn doors (big X)
  const d1 = mkBox(0.15, 5, 5, M(0x6b3a1a,0.9));
  place(d1, 0, 3.5, 5.1); g.add(d1);
  const d2 = mkBox(0.15, 5, 5, M(0x6b3a1a,0.9));
  d2.rotation.x = Math.PI/2;
  place(d2, 0, 3.5, 5.1); g.add(d2);
  // Ventilator on roof
  const vent = mkBox(3, 1.5, 2, M(0x5a1a1a,0.9));
  place(vent, 0, 12.5, 0); g.add(vent);
  place(g, x, 0, z); return g;
}}

// ── GREENHOUSE ────────────────────────────────────────────
function createGreenhouse(x, z) {{
  const g = new THREE.Group();
  const glassMat = M(0xaadfff, 0.05, 0.1, {{ transparent:true, opacity:0.35, side:THREE.DoubleSide }});
  const frameMat = M(0xffffff, 0.6, 0.4);

  // Frame posts (4 corners)
  [[-3,2],[-3,-2],[3,2],[3,-2]].forEach(([px,pz]) => {{
    const post = mkBox(0.15, 3, 0.15, frameMat);
    place(post, px, 1.5, pz); g.add(post);
  }});
  // Glass walls
  const sides = [
    {{ w:6.3, h:3, d:0.1, x:0,  z:2  }},
    {{ w:6.3, h:3, d:0.1, x:0,  z:-2 }},
    {{ w:0.1, h:3, d:4,   x:3,  z:0  }},
    {{ w:0.1, h:3, d:4,   x:-3, z:0  }},
  ];
  sides.forEach(s => {{
    const wall = mkBox(s.w, s.h, s.d, glassMat);
    place(wall, s.x, 1.5, s.z); g.add(wall);
  }});
  // Arched roof (approximated)
  for(let a=0; a<6; a++) {{
    const ang = (a/5)*Math.PI;
    const panel = mkBox(6.3, 0.1, 0.8, glassMat);
    panel.rotation.z = -(ang - Math.PI/2)*0.8;
    panel.position.set(0, 2.8 + Math.sin(ang)*1.2, -2 + a*0.8);
    g.add(panel);
  }}
  // Interior plant rows
  for(let i=0; i<3; i++) {{
    const bed = mkBox(5, 0.4, 0.6, M(0x5a3010,0.95));
    place(bed, 0, 0.2, -1.2+i*1.2); g.add(bed);
    for(let j=0; j<5; j++) {{
      const plant = mkCone(0.3, 1, M(0x00aa44,0.9), 6);
      place(plant, -2+j, 1.2, -1.2+i*1.2); g.add(plant);
    }}
  }}
  place(g, x, 0, z); return g;
}}

// ── WATER TANK ────────────────────────────────────────────
function createWaterTank(x, z) {{
  const g = new THREE.Group();
  // Stand (4 legs)
  [[-1.2,-1.2],[-1.2,1.2],[1.2,-1.2],[1.2,1.2]].forEach(([lx,lz]) => {{
    const leg = mkBox(0.25, 4, 0.25, M(0x444444, 0.8, 0.6));
    place(leg, lx, 2, lz); g.add(leg);
  }});
  // Tank body
  const tank = mkCyl(1.6, 1.6, 3, M(0x1a1a1a,0.7,0.1), 16);
  place(tank, 0, 5.5, 0); g.add(tank);
  // Lid
  const lid = mkCyl(1.7, 1.7, 0.2, M(0x222222,0.7,0.2), 16);
  place(lid, 0, 7.1, 0); g.add(lid);
  // Pipe
  const pipe = mkCyl(0.1, 0.1, 3, M(0x888888,0.7,0.6));
  pipe.rotation.z = Math.PI/2;
  place(pipe, 1.8, 1.5, 0); g.add(pipe);
  place(g, x, 0, z); return g;
}}

// ── SOLAR PANELS ──────────────────────────────────────────
function createSolarArray(x, z) {{
  const g = new THREE.Group();
  for(let i=0; i<3; i++) {{
    const frame = mkBox(3.2, 0.1, 2.2, M(0x222222,0.6,0.4));
    frame.rotation.x = -0.55;
    place(frame, i*3.5-3.5, 2.5, 0); g.add(frame);
    // Cell grid (blue)
    const cell = mkBox(3, 0.05, 2, M(0x0a2a8a,0.1,0.5));
    cell.rotation.x = -0.55;
    place(cell, i*3.5-3.5, 2.55, 0); g.add(cell);
    // Reflection highlight
    const shine = mkBox(1, 0.04, 0.5, M(0x6699ff,0.05,0.9,{{ transparent:true,opacity:0.5 }}));
    shine.rotation.x = -0.55;
    place(shine, i*3.5-4, 2.6, -0.3); g.add(shine);
    // Post
    const post = mkBox(0.2, 2.5, 0.2, M(0x888888,0.7,0.5));
    place(post, i*3.5-3.5, 1.25, 0.8); g.add(post);
  }}
  place(g, x, 0, z); return g;
}}

// ── POND ──────────────────────────────────────────────────
function createPond(x, z) {{
  const g = new THREE.Group();
  // Water surface
  const water = mkCyl(5, 4.5, 0.3, M(0x1a6699,0.05,0.3,{{ transparent:true,opacity:0.75 }}), 24);
  place(water, 0, 0.05, 0); g.add(water);
  // Shore rim
  const shore = mkCyl(5.5, 5, 0.4, M(0x8b7355,0.95), 24);
  place(shore, 0, 0, 0); g.add(shore);
  // Reeds
  for(let i=0; i<8; i++) {{
    const ang = (i/8)*Math.PI*2;
    const reed = mkCyl(0.08, 0.06, 2, M(0x5a8a2a,0.9));
    place(reed, Math.cos(ang)*4.5, 1, Math.sin(ang)*4.5); g.add(reed);
  }}
  // Lily pads
  for(let i=0; i<5; i++) {{
    const pad = mkCyl(0.5, 0.5, 0.05, M(0x2a7a2a,0.9), 8);
    const ang = i*1.2;
    place(pad, Math.cos(ang)*2.5, 0.25, Math.sin(ang)*2); g.add(pad);
  }}
  place(g, x, 0, z); return g;
}}

// ── WIND TURBINE ─────────────────────────────────────────
function createWindTurbine(x, z) {{
  const g = new THREE.Group();
  const pole = mkCyl(0.3, 0.5, 18, M(0xdddddd,0.7,0.1));
  place(pole, 0, 9, 0); g.add(pole);
  const hub = mkSphere(0.6, M(0xcccccc,0.6,0.3));
  place(hub, 0, 18, 0); g.add(hub);
  // 3 blades
  const blades = new THREE.Group();
  for(let i=0; i<3; i++) {{
    const blade = mkBox(0.3, 5, 0.1, M(0xffffff,0.5,0.1));
    blade.position.y = 2.5;
    const bGroup = new THREE.Group();
    bGroup.add(blade);
    bGroup.rotation.z = (i/3)*Math.PI*2;
    blades.add(bGroup);
  }}
  blades.position.set(0.3, 18, 0);
  g.add(blades);
  g._blades = blades;
  place(g, x, 0, z); return g;
}}

// ── FENCE ROW ─────────────────────────────────────────────
function createFenceRow(x1,z1,x2,z2,posts=8) {{
  const g = new THREE.Group();
  const dx = x2-x1, dz = z2-z1;
  const len = Math.sqrt(dx*dx+dz*dz);
  const ang = Math.atan2(dz,dx);
  // Rails
  [0.5, 1.0].forEach(ry => {{
    const rail = mkBox(len, 0.1, 0.12, M(0x8b6040,0.9));
    rail.rotation.y = -ang;
    place(rail, (x1+x2)/2, ry, (z1+z2)/2);
    g.add(rail);
  }});
  // Posts
  for(let i=0; i<=posts; i++) {{
    const t = i/posts;
    const post = mkBox(0.15, 1.4, 0.15, M(0x7a5530,0.9));
    place(post, x1+dx*t, 0.7, z1+dz*t);
    g.add(post);
  }}
  return g;
}}

// ── RAISED GARDEN BEDS ────────────────────────────────────
function createGardenBeds(cx, cz) {{
  const g = new THREE.Group();
  const bedMat = M(0x6b3a1a,0.9);
  const soilMat = M(0x3d1e00,0.97);
  for(let i=0; i<3; i++) {{
    for(let j=0; j<2; j++) {{
      const frame = mkBox(4.5, 0.7, 2, bedMat);
      const soil  = mkBox(4.2, 0.3, 1.7, soilMat);
      const ox = i*5.5-5.5, oz = j*3-1.5;
      place(frame, ox, 0.35, oz); g.add(frame);
      place(soil,  ox, 0.65, oz); g.add(soil);
      // Small plants
      for(let p=0; p<6; p++) {{
        const plant = mkCone(0.22, 0.7, M(0x00bb44,0.9), 6);
        place(plant, ox-1.5+p*0.6, 1.1, oz); g.add(plant);
      }}
    }}
  }}
  place(g, cx, 0, cz); return g;
}}

// ── CHICKEN COOP ──────────────────────────────────────────
function createChickenCoop(x, z) {{
  const g = new THREE.Group();
  const body = mkBox(5, 3, 4, M(0xc8a060,0.85));
  place(body, 0, 1.5, 0); g.add(body);
  // Roof
  const roof = mkBox(5.5, 0.5, 2.5, M(0x8b4513,0.9));
  roof.rotation.z = 0.4; place(roof, -1.4, 3.6, 0); g.add(roof);
  const roof2 = mkBox(5.5, 0.5, 2.5, M(0x8b4513,0.9));
  roof2.rotation.z = -0.4; place(roof2, 1.4, 3.6, 0); g.add(roof2);
  // Wire mesh run
  const run = mkBox(5, 2, 4, M(0xaaaaaa,0.5,0.3,{{ transparent:true,opacity:0.3,wireframe:true }}));
  place(run, 5, 1, 0); g.add(run);
  // A few chickens
  for(let i=0; i<4; i++) {{
    const body_c = mkSphere(0.22, M(0xffffff,0.9));
    const head_c = mkSphere(0.14, M(0xffffff,0.9));
    const beak_c = mkCone(0.06, 0.15, M(0xff8800,0.8), 4);
    body_c.position.set(3.5+i*0.5, 0.22, -1+i*0.5);
    head_c.position.set(3.5+i*0.5, 0.45, -0.9+i*0.5);
    beak_c.rotation.z = -Math.PI/2;
    beak_c.position.set(3.58+i*0.5, 0.47, -0.78+i*0.5);
    g.add(body_c, head_c, beak_c);
  }});
  place(g, x, 0, z); return g;
}}

// ── COMPOST BINS ──────────────────────────────────────────
function createCompost(x, z) {{
  const g = new THREE.Group();
  for(let i=0; i<3; i++) {{
    const bin = mkBox(1.8, 1.5, 1.8, M(0x5a3010,0.9));
    place(bin, i*2.2, 0.75, 0); g.add(bin);
    const content = mkBox(1.6, 0.8, 1.6, M(0x3d1e00,0.97));
    place(content, i*2.2, 1.2, 0); g.add(content);
  }}
  place(g, x, 0, z); return g;
}}

// ── WELL ──────────────────────────────────────────────────
function createWell(x, z) {{
  const g = new THREE.Group();
  // Stone base
  const base = mkCyl(1.3, 1.5, 1.2, M(0x888880,0.95), 12);
  place(base, 0, 0.6, 0); g.add(base);
  // Posts
  [[-0.9,0],[0.9,0]].forEach(([px,pz]) => {{
    const post = mkBox(0.2, 2, 0.2, M(0x6b4226,0.9));
    place(post, px, 2, pz); g.add(post);
  }});
  // Crossbeam
  const beam = mkBox(2.4, 0.25, 0.2, M(0x6b4226,0.9));
  place(beam, 0, 3, 0); g.add(beam);
  // Rope + bucket (simplified)
  const rope = mkCyl(0.04, 0.04, 1.5, M(0xaaaa88,0.9));
  place(rope, 0, 2, 0); g.add(rope);
  const bucket = mkCyl(0.25, 0.3, 0.5, M(0x888888,0.7,0.4));
  place(bucket, 0, 1, 0); g.add(bucket);
  place(g, x, 0, z); return g;
}}

// ══════════════════════════════════════════════════════════
//  SCENE ASSEMBLY  (use layout_data to place things)
// ══════════════════════════════════════════════════════════
const hZ = housePos === 'North' ? -W*0.28 :
           housePos === 'South' ?  W*0.28 :
           housePos === 'East'  ?  0 : 0;
const hX = housePos === 'East'  ?  L*0.28 :
           housePos === 'West'  ? -L*0.28 : 0;
scene.add(createHouse(hX, hZ, 1));

// Food forest (trees in grid)
const treeCount = Math.min(trees, 25);
for(let i=0; i<treeCount; i++) {{
  const row = Math.floor(i/5), col = i%5;
  const tx = -L*0.32 + (col-2)*9;
  const tz =  W*0.12 + row*9;
  scene.add(createTree(tx, tz, i%3, 0.9+Math.random()*0.2));
}}

// Barn (if animals exist)
const hasAnimals = (DATA.animals||[]).length > 0;
if(hasAnimals) scene.add(createBarn(L*0.3, W*0.18));
scene.add(createChickenCoop(L*0.38, W*0.28));

// Greenhouse
scene.add(createGreenhouse(-L*0.12, W*0.06));

// Water systems
if(water.toLowerCase().includes('well') || water.toLowerCase().includes('bore')) {{
  scene.add(createWell(L*0.1, W*0.38));
}}
scene.add(createWaterTank(L*0.18, W*0.3));
scene.add(createPond(-L*0.05, W*0.35));

// Energy
scene.add(createSolarArray(-L*0.35, -W*0.15));
const turbine = createWindTurbine(L*0.4, -W*0.3);
scene.add(turbine);

// Garden beds
scene.add(createGardenBeds(-L*0.08, W*0.02));

// Compost
scene.add(createCompost(L*0.05, W*0.15));

// Perimeter fence
const hl = L*0.62, hw = W*0.62;
scene.add(createFenceRow(-hl,-hw,  hl,-hw));
scene.add(createFenceRow( hl,-hw,  hl, hw));
scene.add(createFenceRow( hl, hw, -hl, hw));
scene.add(createFenceRow(-hl, hw, -hl,-hw));

// Scatter some random trees outside main zone
for(let i=0; i<12; i++) {{
  const ang = (i/12)*Math.PI*2;
  const r = L*0.5 + Math.random()*L*0.15;
  scene.add(createTree(Math.cos(ang)*r, Math.sin(ang)*r, 1, 0.7+Math.random()*0.5));
}}

// ══════════════════════════════════════════════════════════
//  SIMPLE ORBIT CONTROLS (inline, no CDN dependency)
// ══════════════════════════════════════════════════════════
let isDragging = false, prevMouse = {{x:0,y:0}};
let theta = 0.785, phi = 0.7, radius = L*1.5;
let target = new THREE.Vector3(0, 5, 0);

function updateCamera() {{
  camera.position.set(
    target.x + radius * Math.sin(phi) * Math.sin(theta),
    target.y + radius * Math.cos(phi),
    target.z + radius * Math.sin(phi) * Math.cos(theta)
  );
  camera.lookAt(target);
}}
updateCamera();

const el = renderer.domElement;
el.addEventListener('mousedown', e => {{ isDragging=true; prevMouse={{x:e.clientX,y:e.clientY}}; }});
el.addEventListener('mouseup', () => isDragging=false);
el.addEventListener('mousemove', e => {{
  if(!isDragging) return;
  const dx=(e.clientX-prevMouse.x)*0.005, dy=(e.clientY-prevMouse.y)*0.005;
  theta -= dx;
  phi   = Math.max(0.1, Math.min(Math.PI/2-0.05, phi+dy));
  prevMouse={{x:e.clientX,y:e.clientY}};
  updateCamera();
}});
el.addEventListener('wheel', e => {{
  radius = Math.max(L*0.4, Math.min(L*3, radius + e.deltaY*0.5));
  updateCamera(); e.preventDefault();
}}, {{passive:false}});
// Touch
let touch0=null;
el.addEventListener('touchstart',  e=>{{ touch0={{x:e.touches[0].clientX,y:e.touches[0].clientY}}; }});
el.addEventListener('touchend',    ()=>touch0=null);
el.addEventListener('touchmove',   e=>{{
  if(!touch0) return;
  const dx=(e.touches[0].clientX-touch0.x)*0.006, dy=(e.touches[0].clientY-touch0.y)*0.006;
  theta -= dx; phi = Math.max(0.1,Math.min(Math.PI/2-0.05,phi+dy));
  touch0={{x:e.touches[0].clientX,y:e.touches[0].clientY}};
  updateCamera();
}});

// ── Control button callbacks ──
let wireMode = false;
function resetCamera() {{ theta=0.785; phi=0.7; radius=L*1.5; updateCamera(); }}
function toggleWire() {{
  wireMode = !wireMode;
  scene.traverse(o => {{ if(o.isMesh && o.material && !o.material.transparent)
    o.material.wireframe = wireMode; }});
}}
function cycleCamera() {{
  camAngle = (camAngle+1)%CAM_POSITIONS.length;
  camera.position.copy(CAM_POSITIONS[camAngle]);
  camera.lookAt(0,5,0);
  // Sync orbit angles
  const dx=camera.position.x-target.x, dy=camera.position.y-target.y, dz=camera.position.z-target.z;
  radius = Math.sqrt(dx*dx+dy*dy+dz*dz);
  phi    = Math.acos(dy/radius);
  theta  = Math.atan2(dx,dz);
}}

// ══════════════════════════════════════════════════════════
//  ANIMATE
// ══════════════════════════════════════════════════════════
const clock = new THREE.Clock();
function animate() {{
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime() * 1000;

  // Wind turbine blades spin
  if(turbine._blades) turbine._blades.rotation.z += 0.018;

  // Gentle sun rotation (slow time of day)
  sun.position.x = Math.cos(t*0.00005)*L;
  sun.position.z = Math.sin(t*0.00005)*W;

  renderer.render(scene, camera);
}}

// Hide loading & start
setTimeout(() => {{
  document.getElementById('loading').style.display = 'none';
  animate();
}}, 600);

window.addEventListener('resize', () => {{
  const nw = window.innerWidth;
  renderer.setSize(nw, 750);
  camera.aspect = nw/750;
  camera.updateProjectionMatrix();
}});
</script>
</body>
</html>
"""
        st.components.v1.html(html_template, height=750, scrolling=False)
