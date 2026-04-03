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
<title>Homestead 3D Designer</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:sans-serif;background:#f0f4f0}
#app{display:flex;flex-direction:column;gap:0;max-width:1100px;margin:0 auto;padding:16px}
#form-panel{padding:16px;background:#f8f9f5;border:1px solid #d1d5c8;border-radius:12px;margin-bottom:12px}
#form-panel h3{font-size:15px;font-weight:500;color:#1a1a1a;margin-bottom:12px}
.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.field{display:flex;flex-direction:column;gap:4px}
.field label{font-size:12px;color:#555}
.field input,.field select{font-size:13px;padding:6px 8px;border:1px solid #ccc;border-radius:8px;background:#fff;color:#1a1a1a}
.field input[type=range]{padding:0;height:24px}
.check-group{display:flex;flex-wrap:wrap;gap:6px}
.check-item{display:flex;align-items:center;gap:4px;font-size:12px;color:#1a1a1a;cursor:pointer}
.btn-row{display:flex;gap:8px;margin-top:12px;flex-wrap:wrap}
button{padding:7px 14px;font-size:13px;border:1px solid #ccc;border-radius:8px;background:#fff;color:#1a1a1a;cursor:pointer}
button:hover{background:#eee}
button.primary{background:#166534;color:#fff;border-color:#166534}
button.primary:hover{background:#15803d}
#viewer-wrap{position:relative;border-radius:12px;overflow:hidden;border:1px solid #ccc}
#three-canvas{display:block;width:100%;height:520px}
#hud{position:absolute;top:10px;left:10px;background:rgba(15,23,42,0.82);color:#e2e8f0;border-radius:8px;padding:8px 12px;font-size:11px;line-height:1.7;pointer-events:none;min-width:160px}
#hud b{color:#7dd3fc;font-size:12px;font-weight:500}
#ctrl-bar{position:absolute;bottom:10px;right:10px;display:flex;gap:6px}
.vbtn{background:rgba(15,23,42,0.82);color:#e2e8f0;border:1px solid rgba(255,255,255,0.2);border-radius:8px;padding:6px 11px;font-size:11px;cursor:pointer}
.vbtn:hover{background:rgba(56,189,248,0.2)}
#toggle-bar{position:absolute;top:10px;right:10px;display:flex;flex-direction:column;gap:5px}
.tgl{background:rgba(15,23,42,0.82);color:#e2e8f0;border:1px solid rgba(255,255,255,0.2);border-radius:6px;padding:4px 9px;font-size:11px;cursor:pointer;text-align:left}
.tgl.off{opacity:0.4}
#legend{position:absolute;bottom:10px;left:10px;background:rgba(15,23,42,0.78);color:#e2e8f0;border-radius:8px;padding:8px 12px;font-size:11px;line-height:1.9}
.ldot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px;vertical-align:middle}
</style>
</head>
<body>
<div id="app">
  <div id="form-panel">
    <h3>🌿 Homestead 3D Designer</h3>
    <div class="form-grid">
      <div class="field"><label>Location</label><input id="f-loc" value="USA" placeholder="e.g. Gujarat, India"/></div>
      <div class="field"><label>Length (ft)</label><input id="f-len" type="number" value="300" min="50" max="1000"/></div>
      <div class="field"><label>Width (ft)</label><input id="f-wid" type="number" value="300" min="50" max="1000"/></div>
      <div class="field"><label>House position</label>
        <select id="f-hpos"><option>North</option><option>South</option><option>East</option><option>West</option></select>
      </div>
      <div class="field"><label>Water source</label>
        <select id="f-water"><option>Borewell/Well</option><option>River</option><option>Rainwater</option><option>Municipal</option></select>
      </div>
      <div class="field"><label>Fruit trees: <span id="f-trees-val">15</span></label>
        <input id="f-trees" type="range" min="0" max="30" value="15" oninput="document.getElementById('f-trees-val').textContent=this.value"/>
      </div>
    </div>
    <div class="field" style="margin-top:10px"><label>Animals</label>
      <div class="check-group">
        <label class="check-item"><input type="checkbox" value="Chickens" checked/> Chickens</label>
        <label class="check-item"><input type="checkbox" value="Goats" checked/> Goats</label>
        <label class="check-item"><input type="checkbox" value="Cows"/> Cows</label>
        <label class="check-item"><input type="checkbox" value="Pigs"/> Pigs</label>
        <label class="check-item"><input type="checkbox" value="Bees" checked/> Bees</label>
        <label class="check-item"><input type="checkbox" value="Fish"/> Fish</label>
      </div>
    </div>
    <div class="btn-row">
      <button class="primary" onclick="buildScene()">🚀 Generate 3D Map</button>
    </div>
  </div>

  <div id="viewer-wrap">
    <canvas id="three-canvas"></canvas>
    <div id="hud"><b>HOMESTEAD MAP</b><br/><span id="h-info">— Click Generate —</span></div>
    <div id="ctrl-bar">
      <button class="vbtn" onclick="resetCam()">🎯 Reset</button>
      <button class="vbtn" onclick="toggleWire()">📐 Wire</button>
      <button class="vbtn" onclick="cycleCam()">📷 Angle</button>
      <button class="vbtn" onclick="toggleFS()">⛶ Fullscreen</button>
    </div>
    <div id="toggle-bar">
      <button class="tgl" id="tgl-house" onclick="toggleLayer('house',this)">🏡 House</button>
      <button class="tgl" id="tgl-trees" onclick="toggleLayer('trees',this)">🌳 Trees</button>
      <button class="tgl" id="tgl-barn" onclick="toggleLayer('barn',this)">🏚 Barn</button>
      <button class="tgl" id="tgl-water" onclick="toggleLayer('water',this)">💧 Water</button>
      <button class="tgl" id="tgl-garden" onclick="toggleLayer('garden',this)">🥬 Garden</button>
      <button class="tgl" id="tgl-solar" onclick="toggleLayer('solar',this)">☀ Solar</button>
      <button class="tgl" id="tgl-fence" onclick="toggleLayer('fence',this)">🪵 Fence</button>
    </div>
    <div id="legend">
      <span class="ldot" style="background:#4ade80"></span>Food forest<br>
      <span class="ldot" style="background:#fbbf24"></span>Livestock<br>
      <span class="ldot" style="background:#60a5fa"></span>Water<br>
      <span class="ldot" style="background:#f87171"></span>Living area<br>
      <span class="ldot" style="background:#a78bfa"></span>Garden
    </div>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
let renderer,scene,camera,animId;
let wireMode=false,layers={},turbineBlades=null,camAngleIdx=0;
let L=100,W=100,isDragging=false,prevMouse={x:0,y:0};
let theta=0.8,phi=0.65,radius=150;
let target=new THREE.Vector3(0,5,0);
const CAM_ANGLES=[[0.8,0.65],[0,0.3],[Math.PI/2,0.6],[Math.PI,0.5]];

function getAnimals(){return[...document.querySelectorAll('.check-group input:checked')].map(c=>c.value);}
function M(color,rough=0.75,metal=0.05,extra={}){return new THREE.MeshStandardMaterial({color,roughness:rough,metalness:metal,...extra});}
function mkBox(w,h,d,mat){const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat);m.castShadow=m.receiveShadow=true;return m;}
function mkCyl(r1,r2,h,mat,seg=16){const m=new THREE.Mesh(new THREE.CylinderGeometry(r1,r2,h,seg),mat);m.castShadow=m.receiveShadow=true;return m;}
function mkCone(r,h,mat,seg=8){const m=new THREE.Mesh(new THREE.ConeGeometry(r,h,seg),mat);m.castShadow=m.receiveShadow=true;return m;}
function mkSphere(r,mat,ws=12,hs=12){const m=new THREE.Mesh(new THREE.SphereGeometry(r,ws,hs),mat);m.castShadow=m.receiveShadow=true;return m;}
function place(o,x,y,z){o.position.set(x,y,z);return o;}

function createHouse(x,z){
  const g=new THREE.Group();
  g.add(place(mkBox(18,0.8,14,M(0x9e9e9e,0.9)),0,0.4,0));
  g.add(place(mkBox(16,9,12,M(0xd4a97a,0.78)),0,5.3,0));
  const rm=M(0x6b3a2a,0.85);
  const r1=mkBox(18.5,0.6,7,rm);r1.rotation.z=0.45;place(r1,-4.2,10.5,0);g.add(r1);
  const r2=mkBox(18.5,0.6,7,rm);r2.rotation.z=-0.45;place(r2,4.2,10.5,0);g.add(r2);
  g.add(place(mkBox(18.5,0.8,1,M(0x5a2e1a,0.9)),0,13.2,0));
  g.add(place(mkBox(1.6,2.8,0.2,M(0x4a2800,0.9)),0,1.8,6.1));
  [[-5,5,1],[5,5,1],[-5,5,-1],[5,5,-1]].forEach(([wx,wy,side])=>{
    const win=mkBox(2,1.8,0.15,M(0x9ecae1,0.1,0.5,{transparent:true,opacity:0.65}));
    place(win,wx,wy,side>0?6.1:-6.1);g.add(win);
  });
  g.add(place(mkBox(1.5,5,1.5,M(0x8b6050,0.9)),5,13,-2));
  [-4,0,4].forEach(px=>{g.add(place(mkCyl(0.25,0.25,2.5,M(0xf0ede8,0.7)),px,1.5,6.5));});
  g.add(place(mkBox(10,0.3,3,M(0xb07a50,0.85)),0,2.8,7));
  place(g,x,0,z);return g;
}
function createTree(x,z,type=0,scale=1){
  const g=new THREE.Group();const tm=M(0x6b4226,0.9);
  if(type===0){
    g.add(place(mkCyl(0.22,0.3,2.8,tm),0,1.4,0));
    [0,0.6,1.1].forEach((dy,i)=>{g.add(place(mkSphere(1.8-i*0.3,M(0x2e7d32,0.9),8,8),(i-1)*0.3,3+dy,0));});
    for(let i=0;i<5;i++){const a=mkSphere(0.18,M(0xcc2200,0.7));a.position.set(Math.sin(i*1.3)*1.2,3.2+Math.cos(i)*0.4,Math.cos(i*1.3)*1.2);g.add(a);}
  }else if(type===1){
    g.add(place(mkCyl(0.18,0.25,3,tm),0,1.5,0));
    [0,1.2,2.2,3].forEach((dy,i)=>{g.add(place(mkCone(1.8-i*0.35,2,M(0x1a5c1a,0.95),8),0,3+dy,0));});
  }else{
    g.add(place(mkCyl(0.3,0.4,3.5,M(0x7a5030,0.9)),0,1.75,0));
    const can=mkSphere(2.5,M(0x1b6b1b,0.85),8,8);can.scale.y=0.7;place(can,0,5,0);g.add(can);
    for(let i=0;i<6;i++){const mg=mkBox(0.25,0.35,0.2,M(0xffa000,0.7));mg.position.set(Math.sin(i)*2,4.5,Math.cos(i)*2);g.add(mg);}
  }
  g.scale.setScalar(scale);place(g,x,0,z);return g;
}
function createBarn(x,z){
  const g=new THREE.Group();
  g.add(place(mkBox(14,8,10,M(0x8b1a1a,0.85)),0,4,0));
  const rm=M(0x5a1a1a,0.9);
  const r1=mkBox(15,0.6,6,rm);r1.rotation.z=0.5;place(r1,-3.8,9.5,0);g.add(r1);
  const r2=mkBox(15,0.6,6,rm);r2.rotation.z=-0.5;place(r2,3.8,9.5,0);g.add(r2);
  g.add(place(mkBox(3,1.5,2,M(0x5a1a1a,0.9)),0,12.5,0));
  place(g,x,0,z);return g;
}
function createPond(x,z){
  const g=new THREE.Group();
  g.add(place(mkCyl(5,4.5,0.3,M(0x1a6699,0.05,0.3,{transparent:true,opacity:0.75}),24),0,0.05,0));
  g.add(place(mkCyl(5.5,5,0.4,M(0x8b7355,0.95),24),0,0,0));
  for(let i=0;i<8;i++){const ang=(i/8)*Math.PI*2;const reed=mkCyl(0.08,0.06,2,M(0x5a8a2a,0.9));place(reed,Math.cos(ang)*4.5,1,Math.sin(ang)*4.5);g.add(reed);}
  place(g,x,0,z);return g;
}
function createWaterTank(x,z){
  const g=new THREE.Group();
  [[-1.2,-1.2],[-1.2,1.2],[1.2,-1.2],[1.2,1.2]].forEach(([lx,lz])=>{g.add(place(mkBox(0.25,4,0.25,M(0x444444,0.8,0.6)),lx,2,lz));});
  g.add(place(mkCyl(1.6,1.6,3,M(0x1a1a1a,0.7,0.1),16),0,5.5,0));
  g.add(place(mkCyl(1.7,1.7,0.2,M(0x222222,0.7,0.2),16),0,7.1,0));
  place(g,x,0,z);return g;
}
function createWell(x,z){
  const g=new THREE.Group();
  g.add(place(mkCyl(1.3,1.5,1.2,M(0x888880,0.95),12),0,0.6,0));
  [[-0.9,0],[0.9,0]].forEach(([px,pz])=>{g.add(place(mkBox(0.2,2,0.2,M(0x6b4226,0.9)),px,2,pz));});
  g.add(place(mkBox(2.4,0.25,0.2,M(0x6b4226,0.9)),0,3,0));
  place(g,x,0,z);return g;
}
function createSolarArray(x,z){
  const g=new THREE.Group();
  for(let i=0;i<3;i++){
    const fr=mkBox(3.2,0.1,2.2,M(0x222222,0.6,0.4));fr.rotation.x=-0.55;place(fr,i*3.5-3.5,2.5,0);g.add(fr);
    const cl=mkBox(3,0.05,2,M(0x0a2a8a,0.1,0.5));cl.rotation.x=-0.55;place(cl,i*3.5-3.5,2.55,0);g.add(cl);
    g.add(place(mkBox(0.2,2.5,0.2,M(0x888888,0.7,0.5)),i*3.5-3.5,1.25,0.8));
  }
  place(g,x,0,z);return g;
}
function createWindTurbine(x,z){
  const g=new THREE.Group();
  g.add(place(mkCyl(0.3,0.5,18,M(0xdddddd,0.7,0.1)),0,9,0));
  g.add(place(mkSphere(0.6,M(0xcccccc,0.6,0.3)),0,18,0));
  const blades=new THREE.Group();
  for(let i=0;i<3;i++){const bl=mkBox(0.3,5,0.1,M(0xffffff,0.5,0.1));bl.position.y=2.5;const bg=new THREE.Group();bg.add(bl);bg.rotation.z=(i/3)*Math.PI*2;blades.add(bg);}
  blades.position.set(0.3,18,0);g.add(blades);g._blades=blades;
  place(g,x,0,z);return g;
}
function createFenceRow(x1,z1,x2,z2,posts=8){
  const g=new THREE.Group();
  const dx=x2-x1,dz=z2-z1,len=Math.sqrt(dx*dx+dz*dz),ang=Math.atan2(dz,dx);
  [0.5,1.0].forEach(ry=>{const r=mkBox(len,0.1,0.12,M(0x8b6040,0.9));r.rotation.y=-ang;place(r,(x1+x2)/2,ry,(z1+z2)/2);g.add(r);});
  for(let i=0;i<=posts;i++){const t=i/posts;g.add(place(mkBox(0.15,1.4,0.15,M(0x7a5530,0.9)),x1+dx*t,0.7,z1+dz*t));}
  return g;
}
function createGardenBeds(cx,cz){
  const g=new THREE.Group();
  for(let i=0;i<3;i++)for(let j=0;j<2;j++){
    const ox=i*5.5-5.5,oz=j*3-1.5;
    g.add(place(mkBox(4.5,0.7,2,M(0x6b3a1a,0.9)),ox,0.35,oz));
    g.add(place(mkBox(4.2,0.3,1.7,M(0x3d1e00,0.97)),ox,0.65,oz));
    for(let p=0;p<6;p++){g.add(place(mkCone(0.22,0.7,M(0x00bb44,0.9),6),ox-1.5+p*0.6,1.1,oz));}
  }
  place(g,cx,0,cz);return g;
}
function createChickenCoop(x,z){
  const g=new THREE.Group();
  g.add(place(mkBox(5,3,4,M(0xc8a060,0.85)),0,1.5,0));
  const rm=M(0x8b4513,0.9);
  const r1=mkBox(5.5,0.5,2.5,rm);r1.rotation.z=0.4;place(r1,-1.4,3.6,0);g.add(r1);
  const r2=mkBox(5.5,0.5,2.5,rm);r2.rotation.z=-0.4;place(r2,1.4,3.6,0);g.add(r2);
  place(g,x,0,z);return g;
}

function buildScene(){
  L=parseInt(document.getElementById('f-len').value)||100;
  W=parseInt(document.getElementById('f-wid').value)||100;
  const loc=document.getElementById('f-loc').value||'Location';
  const water=document.getElementById('f-water').value;
  const trees=parseInt(document.getElementById('f-trees').value)||0;
  const animals=getAnimals();
  const hpos=document.getElementById('f-hpos').value;
  document.getElementById('h-info').innerHTML=`${loc} | ${L}×${W} ft<br>Water: ${water}<br>Trees: ${trees}<br>Animals: ${animals.join(', ')||'None'}`;
  if(animId)cancelAnimationFrame(animId);
  if(renderer)renderer.dispose();
  const canvas=document.getElementById('three-canvas');
  renderer=new THREE.WebGLRenderer({canvas,antialias:true});
  renderer.setSize(canvas.offsetWidth,520);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
  renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
  scene=new THREE.Scene();scene.background=new THREE.Color(0x87CEEB);
  scene.fog=new THREE.FogExp2(0xc9e8f5,0.0008);
  camera=new THREE.PerspectiveCamera(52,canvas.offsetWidth/520,0.5,8000);
  radius=L*1.5;theta=0.8;phi=0.65;updateCam();
  scene.add(new THREE.HemisphereLight(0x87CEEB,0x5a7a3a,0.6));
  const sun=new THREE.DirectionalLight(0xfff5e0,2.2);
  sun.position.set(L*0.8,200,W*0.6);sun.castShadow=true;
  sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.left=-L;sun.shadow.camera.right=L;
  sun.shadow.camera.top=W;sun.shadow.camera.bottom=-W;sun.shadow.camera.far=1000;sun.shadow.bias=-0.0003;
  scene.add(sun);
  layers={};
  function addLayer(name,obj){layers[name]=obj;scene.add(obj);}
  scene.add(place(mkBox(L*2.5,0.5,W*2.5,M(0x4a7c59,0.95,0)),0,-0.25,0));
  [{x:0,z:-W*0.3,w:L*0.6,d:W*0.4,c:0xf87171},{x:-L*0.32,z:W*0.2,w:L*0.55,d:W*0.5,c:0x4ade80},
   {x:L*0.32,z:W*0.2,w:L*0.55,d:W*0.5,c:0xfbbf24},{x:0,z:W*0.38,w:L*0.4,d:W*0.2,c:0x60a5fa},
   {x:-L*0.1,z:0,w:L*0.25,d:W*0.25,c:0xa78bfa}].forEach(z=>{
    const ov=mkBox(z.w,0.15,z.d,M(z.c,0.9,0,{transparent:true,opacity:0.22}));
    place(ov,z.x,0.08,z.z);scene.add(ov);
  });
  const hX=hpos==='East'?L*0.28:hpos==='West'?-L*0.28:0;
  const hZ=hpos==='North'?-W*0.28:hpos==='South'?W*0.28:0;
  const houseG=new THREE.Group();houseG.add(createHouse(hX,hZ));addLayer('house',houseG);
  const treesG=new THREE.Group();
  for(let i=0;i<Math.min(trees,25);i++){const row=Math.floor(i/5),col=i%5;treesG.add(createTree(-L*0.32+(col-2)*9,W*0.12+row*9,i%3,0.9+Math.random()*0.2));}
  for(let i=0;i<10;i++){const ang=(i/10)*Math.PI*2,r=L*0.5+Math.random()*L*0.12;treesG.add(createTree(Math.cos(ang)*r,Math.sin(ang)*r,1,0.7+Math.random()*0.4));}
  addLayer('trees',treesG);
  const barnG=new THREE.Group();
  if(animals.length>0)barnG.add(createBarn(L*0.3,W*0.18));
  barnG.add(createChickenCoop(L*0.38,W*0.28));addLayer('barn',barnG);
  const waterG=new THREE.Group();
  waterG.add(createPond(-L*0.05,W*0.35));waterG.add(createWaterTank(L*0.18,W*0.3));
  if(water.includes('Well')||water.includes('Bore'))waterG.add(createWell(L*0.1,W*0.38));
  addLayer('water',waterG);
  const gardenG=new THREE.Group();gardenG.add(createGardenBeds(-L*0.08,W*0.02));addLayer('garden',gardenG);
  const solarG=new THREE.Group();solarG.add(createSolarArray(-L*0.35,-W*0.15));
  const turb=createWindTurbine(L*0.4,-W*0.3);turbineBlades=turb._blades;solarG.add(turb);addLayer('solar',solarG);
  const fenceG=new THREE.Group();const hl=L*0.62,hw=W*0.62;
  fenceG.add(createFenceRow(-hl,-hw,hl,-hw));fenceG.add(createFenceRow(hl,-hw,hl,hw));
  fenceG.add(createFenceRow(hl,hw,-hl,hw));fenceG.add(createFenceRow(-hl,hw,-hl,-hw));
  addLayer('fence',fenceG);
  document.querySelectorAll('.tgl').forEach(b=>b.classList.remove('off'));
  function animate(){animId=requestAnimationFrame(animate);if(turbineBlades)turbineBlades.rotation.z+=0.02;renderer.render(scene,camera);}
  animate();setupControls();
}
function updateCam(){
  if(!camera)return;
  camera.position.set(target.x+radius*Math.sin(phi)*Math.sin(theta),target.y+radius*Math.cos(phi),target.z+radius*Math.sin(phi)*Math.cos(theta));
  camera.lookAt(target);
}
function setupControls(){
  const el=document.getElementById('three-canvas');
  el.onmousedown=e=>{isDragging=true;prevMouse={x:e.clientX,y:e.clientY};};
  el.onmouseup=()=>isDragging=false;el.onmouseleave=()=>isDragging=false;
  el.onmousemove=e=>{if(!isDragging)return;theta-=(e.clientX-prevMouse.x)*0.005;phi=Math.max(0.08,Math.min(Math.PI/2-0.05,phi+(e.clientY-prevMouse.y)*0.005));prevMouse={x:e.clientX,y:e.clientY};updateCam();};
  el.onwheel=e=>{radius=Math.max(L*0.3,Math.min(L*3,radius+e.deltaY*0.4));updateCam();e.preventDefault();};
  let t0=null;
  el.ontouchstart=e=>{t0={x:e.touches[0].clientX,y:e.touches[0].clientY};};
  el.ontouchend=()=>t0=null;
  el.ontouchmove=e=>{if(!t0)return;theta-=(e.touches[0].clientX-t0.x)*0.006;phi=Math.max(0.08,Math.min(Math.PI/2-0.05,phi+(e.touches[0].clientY-t0.y)*0.006));t0={x:e.touches[0].clientX,y:e.touches[0].clientY};updateCam();};
}
function resetCam(){theta=0.8;phi=0.65;radius=L*1.5;updateCam();}
function toggleWire(){wireMode=!wireMode;scene&&scene.traverse(o=>{if(o.isMesh&&o.material&&!o.material.transparent)o.material.wireframe=wireMode;});}
function cycleCam(){camAngleIdx=(camAngleIdx+1)%CAM_ANGLES.length;[theta,phi]=CAM_ANGLES[camAngleIdx];updateCam();}
function toggleFS(){const el=document.getElementById('viewer-wrap');if(!document.fullscreenElement)el.requestFullscreen&&el.requestFullscreen();else document.exitFullscreen&&document.exitFullscreen();}
function toggleLayer(name,btn){if(!layers[name])return;layers[name].visible=!layers[name].visible;btn.classList.toggle('off',!layers[name].visible);}
window.addEventListener('resize',()=>{if(!renderer||!camera)return;const c=document.getElementById('three-canvas');renderer.setSize(c.offsetWidth,520);camera.aspect=c.offsetWidth/520;camera.updateProjectionMatrix();});
</script>
</body>
</html>
