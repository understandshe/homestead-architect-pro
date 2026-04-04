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
<title>🏡 Smart Homestead Designer Pro 2026</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',Arial,sans-serif;background:#EAF4FB;color:#1a1a1a}
#main{display:flex;height:100vh;overflow:hidden}
#sidebar{width:310px;min-width:260px;background:#fff;border-right:1px solid #cde;overflow-y:auto;display:flex;flex-direction:column;z-index:10}
#sidebar-header{background:#166534;color:#fff;padding:12px 14px}
#sidebar-header h2{font-size:14px;font-weight:600;margin-bottom:1px}
#sidebar-header p{font-size:10px;opacity:0.8}
#form-body{padding:12px;flex:1}
.sec{font-size:10px;font-weight:700;color:#166534;text-transform:uppercase;letter-spacing:0.6px;margin:12px 0 5px;border-bottom:1px solid #e0eed8;padding-bottom:3px}
.field{margin-bottom:8px}
.field label{display:block;font-size:11px;color:#444;margin-bottom:2px;font-weight:500}
.field input[type=text],.field input[type=number],.field select{width:100%;padding:5px 8px;font-size:12px;border:1px solid #ccc;border-radius:6px;background:#fafffe;color:#1a1a1a;outline:none}
.field input:focus,.field select:focus{border-color:#166534}
.dim-row{display:grid;grid-template-columns:1fr 1fr;gap:7px}
.check-group{display:flex;flex-wrap:wrap;gap:4px}
.chip{display:flex;align-items:center;gap:3px;padding:3px 8px;font-size:11px;border:1px solid #ccc;border-radius:16px;cursor:pointer;background:#f9f9f9;user-select:none;transition:all 0.12s}
.chip input{display:none}
.chip.active{background:#166534;color:#fff;border-color:#166534}
.rw{display:flex;align-items:center;gap:6px}
.rw input[type=range]{flex:1;accent-color:#166534;height:4px}
.rv{font-size:12px;font-weight:600;color:#166534;min-width:22px;text-align:right}
#btn-gen{width:100%;padding:9px;background:#166534;color:#fff;border:none;border-radius:7px;font-size:13px;font-weight:600;cursor:pointer;margin-top:5px}
#btn-gen:hover{background:#15803d}
#btn-dl{width:100%;padding:7px;background:#fff;color:#166534;border:1.5px solid #166534;border-radius:7px;font-size:12px;font-weight:500;cursor:pointer;margin-top:5px}
#btn-dl:hover{background:#f0fdf4}
#status{font-size:10px;color:#555;text-align:center;padding:5px 0;min-height:20px}
#map-panel{flex:1;display:flex;flex-direction:column;overflow:hidden;position:relative}
#toolbar{background:#fff;border-bottom:1px solid #cde;padding:6px 10px;display:flex;align-items:center;gap:5px;flex-wrap:wrap}
#toolbar span{font-size:11px;color:#555;margin-right:2px;font-weight:600}
.tgl-btn{padding:3px 8px;font-size:10px;border:1px solid #aaa;border-radius:5px;background:#f5f5f5;cursor:pointer;transition:all 0.12s;white-space:nowrap}
.tgl-btn:hover{border-color:#166634;color:#166534}
.tgl-btn.off{opacity:0.38;text-decoration:line-through}
#cam-btns{margin-left:auto;display:flex;gap:4px}
.cam-btn{padding:3px 9px;font-size:10px;border:1px solid #90CAF9;border-radius:5px;background:#E3F2FD;cursor:pointer;color:#1565C0;white-space:nowrap}
.cam-btn:hover{background:#BBDEFB}
#plotly-wrap{flex:1;min-height:0;position:relative}
#plot{width:100%;height:100%}
#ph{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;color:#888;gap:8px;background:#EAF4FB;position:absolute;inset:0}
#ph .icon{font-size:44px}
#ph p{font-size:13px}
#ov{display:none;position:absolute;inset:0;background:rgba(234,244,251,0.85);align-items:center;justify-content:center;flex-direction:column;gap:10px;z-index:50}
#ov.on{display:flex}
.spin{width:36px;height:36px;border:3px solid #cde;border-top-color:#166534;border-radius:50%;animation:sp 0.75s linear infinite}
@keyframes sp{to{transform:rotate(360deg)}}
</style>
</head>
<body>
<div id="main">
<div id="sidebar">
  <div id="sidebar-header">
    <h2>🌿 Smart Homestead Designer Pro</h2>
    <p>Homestead Architect — Global Edition 2026</p>
  </div>
  <div id="form-body">
    <div class="sec">📍 Location</div>
    <div class="field"><label>Homestead location</label><input type="text" id="f-loc" value="Pune, India" placeholder="City, Country"/></div>

    <div class="sec">📐 Plot Dimensions</div>
    <div class="dim-row">
      <div class="field"><label>Length (ft)</label><input type="number" id="f-len" value="300" min="50" max="5000"/></div>
      <div class="field"><label>Width (ft)</label><input type="number" id="f-wid" value="300" min="50" max="5000"/></div>
    </div>

    <div class="sec">🏠 House &amp; Terrain</div>
    <div class="field"><label>House position</label>
      <select id="f-hpos"><option value="North">North</option><option value="South">South</option><option value="East">East</option><option value="West">West</option><option value="Center" selected>Center</option><option value="Not built yet">Not built yet</option></select>
    </div>
    <div class="field"><label>Slope direction</label>
      <select id="f-slope"><option value="Flat" selected>Flat</option><option value="North">North</option><option value="South">South</option><option value="East">East</option><option value="West">West</option></select>
    </div>

    <div class="sec">💧 Water Source</div>
    <div class="field"><label>Primary water source</label>
      <select id="f-water"><option value="Borewell/Well" selected>Borewell/Well</option><option value="Municipal Supply">Municipal Supply</option><option value="Rainwater">Rainwater</option><option value="River/Pond">River/Pond</option><option value="None yet">None yet</option></select>
    </div>

    <div class="sec">🐄 Animals to Keep</div>
    <div class="check-group" id="animals">
      <label class="chip active"><input type="checkbox" value="Chickens" checked>🐔 Chickens</label>
      <label class="chip active"><input type="checkbox" value="Goats" checked>🐐 Goats</label>
      <label class="chip"><input type="checkbox" value="Pigs">🐷 Pigs</label>
      <label class="chip active"><input type="checkbox" value="Cows" checked>🐄 Cows</label>
      <label class="chip"><input type="checkbox" value="Bees">🐝 Bees</label>
      <label class="chip"><input type="checkbox" value="Fish">🐟 Fish</label>
    </div>

    <div class="sec">🌳 Food Forest</div>
    <div class="field"><label>Fruit/Nut trees: <span id="tv">15</span></label>
      <div class="rw"><input type="range" id="f-trees" min="5" max="50" value="15" oninput="document.getElementById('tv').textContent=this.value"/><span class="rv" id="f-trees-val">15</span></div>
    </div>

    <div class="sec">💰 Budget</div>
    <div class="field"><label>Budget range</label>
      <select id="f-budget"><option>Under $5,000</option><option>$5,000 - $25,000</option><option>$25,000 - $100,000</option><option>$100,000+</option><option>Not sure</option></select>
    </div>

    <div id="status">Fill in details and click Generate</div>
    <button id="btn-gen" onclick="generateMap()">🚀 Generate My Homestead Design</button>
    <button id="btn-dl" onclick="downloadMap()">⬇ Download 3D Map (HTML)</button>
  </div>
</div>

<div id="map-panel">
  <div id="toolbar">
    <span>Layers:</span>
    <button class="tgl-btn" data-lg="Terrain" onclick="toggleLG(this)">🌍 Terrain</button>
    <button class="tgl-btn" data-lg="Zones" onclick="toggleLG(this)">🗺 Zones</button>
    <button class="tgl-btn" data-lg="Roads" onclick="toggleLG(this)">🛤 Roads</button>
    <button class="tgl-btn" data-lg="House" onclick="toggleLG(this)">🏡 House</button>
    <button class="tgl-btn" data-lg="Trees" onclick="toggleLG(this)">🌳 Trees</button>
    <button class="tgl-btn" data-lg="Water" onclick="toggleLG(this)">💧 Water</button>
    <button class="tgl-btn" data-lg="Livestock" onclick="toggleLG(this)">🐄 Animals</button>
    <button class="tgl-btn" data-lg="Solar" onclick="toggleLG(this)">☀ Solar</button>
    <button class="tgl-btn" data-lg="Garden" onclick="toggleLG(this)">🥬 Garden</button>
    <div id="cam-btns">
      <button class="cam-btn" onclick="setCam(1.3,-1.5,0.85)">3D</button>
      <button class="cam-btn" onclick="setCam(0,0,2.5)">Top</button>
      <button class="cam-btn" onclick="setCam(0,-2.5,0.5)">South</button>
      <button class="cam-btn" onclick="setCam(0.05,-0.05,2.8)">Bird</button>
    </div>
  </div>
  <div id="plotly-wrap">
    <div id="ph"><div class="icon">🌿</div><p>Fill the form and click <b>Generate My Homestead Design</b></p></div>
    <div id="plot"></div>
    <div id="ov"><div class="spin"></div><p style="color:#166534;font-weight:500">Building 3D homestead...</p></div>
  </div>
</div>
</div>

<script>
// Chip toggles
document.querySelectorAll('.chip').forEach(c=>{
  c.addEventListener('click',()=>{const cb=c.querySelector('input');cb.checked=!cb.checked;c.classList.toggle('active',cb.checked);});
});
// Sync range display
document.getElementById('f-trees').addEventListener('input',function(){
  document.getElementById('tv').textContent=this.value;
  document.getElementById('f-trees-val').textContent=this.value;
});

function getAnimals(){return[...document.querySelectorAll('#animals input:checked')].map(c=>c.value);}
function clamp(v,lo,hi){return Math.max(lo,Math.min(hi,v));}
function linspace(a,b,n){const r=[];for(let i=0;i<n;i++)r.push(a+(b-a)*(n>1?i/(n-1):0));return r;}

function getTZ(x,y,L,W,slope){
  if(slope==='South')return y*0.025;
  if(slope==='North')return(W-y)*0.025;
  if(slope==='East')return x*0.025;
  if(slope==='West')return(L-x)*0.025;
  return 0;
}

function zoneRatios(acres){
  if(acres<0.5)return{z0:.10,z1:.18,z2:.22,z3:.38,z4:.12};
  if(acres<5)  return{z0:.08,z1:.14,z2:.28,z3:.35,z4:.15};
  return             {z0:.05,z1:.10,z2:.35,z3:.30,z4:.20};
}

function makeZonePos(L,W,zr,hpos){
  const pos={};
  if(hpos==='North'){let y=W;for(const z of['z0','z1','z2','z3','z4']){const h=W*zr[z];y-=h;pos[z]={x:0,y,width:L,height:h};}}
  else if(hpos==='East'){let x=L;for(const z of['z0','z1','z2','z3','z4']){const w=L*zr[z];x-=w;pos[z]={x,y:0,width:w,height:W};}}
  else if(hpos==='West'){let x=0;for(const z of['z0','z1','z2','z3','z4']){const w=L*zr[z];pos[z]={x,y:0,width:w,height:W};x+=w;}}
  else{let y=0;for(const z of['z0','z1','z2','z3','z4']){const h=W*zr[z];pos[z]={x:0,y,width:L,height:h};y+=h;}}
  return pos;
}

function houseBbox(L,W,hpos){
  const m={
    'North':[L*.30,W*.82,L*.38,W*.12],'South':[L*.30,W*.06,L*.38,W*.12],
    'East':[L*.74,W*.36,L*.20,W*.28],'West':[L*.06,W*.36,L*.20,W*.28],
    'Center':[L*.35,W*.40,L*.30,W*.20],'Not built yet':[L*.35,W*.40,L*.30,W*.20]
  };
  return m[hpos]||m['Center'];
}

class Reg{
  constructor(){this.rects=[];this.circles=[];this.GAP=8;}
  addRect(x0,y0,x1,y1){this.rects.push([Math.min(x0,x1),Math.min(y0,y1),Math.max(x0,x1),Math.max(y0,y1)]);}
  addCircle(cx,cy,r){this.circles.push([cx,cy,r]);}
  rectOk(x0,y0,x1,y1){
    const g=this.GAP,ax0=Math.min(x0,x1)-g,ay0=Math.min(y0,y1)-g,ax1=Math.max(x0,x1)+g,ay1=Math.max(y0,y1)+g;
    for(const[rx0,ry0,rx1,ry1]of this.rects)if(ax0<rx1&&ax1>rx0&&ay0<ry1&&ay1>ry0)return false;
    for(const[cx,cy,r]of this.circles){const nx=clamp(cx,ax0,ax1),ny=clamp(cy,ay0,ay1);if((cx-nx)**2+(cy-ny)**2<(r+g)**2)return false;}
    return true;
  }
  circleOk(cx,cy,r){
    const g=this.GAP;
    for(const[rx0,ry0,rx1,ry1]of this.rects){const nx=clamp(cx,rx0,rx1),ny=clamp(cy,ry0,ry1);if((cx-nx)**2+(cy-ny)**2<(r+g)**2)return false;}
    for(const[ocx,ocy,or_]of this.circles)if((cx-ocx)**2+(cy-ocy)**2<(r+or_+g)**2)return false;
    return true;
  }
}

const TREE_SP={
  Mango:    {th:5,cb:5,ct:20,cr:8, tr:1.0,c1:'#2E7D32',c2:'#388E3C'},
  Jackfruit:{th:8,cb:8,ct:26,cr:9, tr:1.3,c1:'#1B5E20',c2:'#2E7D32'},
  Coconut:  {th:20,cb:20,ct:30,cr:5,tr:0.6,c1:'#33691E',c2:'#558B2F'},
  Banana:   {th:3,cb:3,ct:10,cr:4, tr:1.4,c1:'#558B2F',c2:'#7CB342'},
  Guava:    {th:4,cb:4,ct:13,cr:4, tr:0.7,c1:'#33691E',c2:'#43A047'},
  Papaya:   {th:4,cb:4,ct:11,cr:3, tr:0.5,c1:'#558B2F',c2:'#8BC34A'},
  Avocado:  {th:7,cb:7,ct:18,cr:6, tr:0.9,c1:'#2E7D32',c2:'#1B5E20'},
  Moringa:  {th:6,cb:6,ct:15,cr:3, tr:0.5,c1:'#66BB6A',c2:'#4CAF50'},
  Citrus:   {th:4,cb:4,ct:12,cr:4, tr:0.6,c1:'#43A047',c2:'#66BB6A'},
  Neem:     {th:9,cb:9,ct:24,cr:9, tr:1.1,c1:'#388E3C',c2:'#2E7D32'},
  Teak:     {th:14,cb:14,ct:28,cr:7,tr:0.9,c1:'#1B5E20',c2:'#2E7D32'},
  Bamboo:   {th:1,cb:1,ct:16,cr:2, tr:0.4,c1:'#4CAF50',c2:'#8BC34A'},
};
const SP_CYCLE=Object.keys(TREE_SP);

// Trace builders
function MB(x0,y0,z0,x1,y1,z1,col,name,lg,op=0.92,sl=false){
  return{type:'mesh3d',
    x:[x0,x1,x1,x0,x0,x1,x1,x0],y:[y0,y0,y1,y1,y0,y0,y1,y1],z:[z0,z0,z0,z0,z1,z1,z1,z1],
    i:[0,0,4,4,0,0,2,2,0,0,1,1],j:[1,2,5,6,1,5,3,7,3,7,2,6],k:[2,3,6,7,5,4,7,6,7,4,6,5],
    color:col,opacity:op,name,legendgroup:lg,showlegend:sl,flatshading:true,
    lighting:{ambient:0.65,diffuse:0.88,specular:0.25,roughness:0.55}};
}
function MR(x0,y0,x1,y1,zb,zt,col,lg){
  const cx=(x0+x1)/2,cy=(y0+y1)/2;
  return{type:'mesh3d',x:[x0,x1,x1,x0,cx],y:[y0,y0,y1,y1,cy],z:[zb,zb,zb,zb,zt],
    i:[0,1,2,3],j:[1,2,3,0],k:[4,4,4,4],color:col,opacity:.97,name:'Roof',legendgroup:lg,showlegend:false,flatshading:true};
}
function CYL(cx,cy,r,z0,z1,col,name,lg,sl=false,n=18){
  const t=linspace(0,2*Math.PI,n);
  const X=[],Y=[],Z=[];
  for(const zi of[z0,z1]){X.push(t.map(a=>cx+r*Math.cos(a)));Y.push(t.map(a=>cy+r*Math.sin(a)));Z.push(t.map(()=>zi));}
  return{type:'surface',x:X,y:Y,z:Z,colorscale:[[0,col],[1,col]],showscale:false,opacity:.92,name,legendgroup:lg,showlegend:sl};
}
function CONE(cx,cy,r,zb,zt,col,name,lg,sl=false,n=14){
  const t=linspace(0,2*Math.PI,n);
  const xs=t.map(a=>cx+r*Math.cos(a)).concat([cx]),ys=t.map(a=>cy+r*Math.sin(a)).concat([cy]),zs=t.map(()=>zb).concat([zt]);
  const ii=[],jj=[],kk=[];for(let i=0;i<n;i++){ii.push(i);jj.push((i+1)%n);kk.push(n);}
  return{type:'mesh3d',x:xs,y:ys,z:zs,i:ii,j:jj,k:kk,color:col,opacity:.88,name,legendgroup:lg,showlegend:sl,flatshading:true};
}
function SURF(xs,ys,ZFn,cs,name,lg,op=0.45,sl=false){
  const X=[],Y=[],Z=[];
  for(let j=0;j<ys.length;j++){X.push(xs.slice());Y.push(xs.map(()=>ys[j]));Z.push(xs.map((x,i)=>ZFn(x,ys[j])));}
  return{type:'surface',x:X,y:Y,z:Z,colorscale:cs,showscale:false,opacity:op,name,legendgroup:lg,showlegend:sl};
}
function ROADSUF(x0,y0,x1,y1,w,L,W,slope,name,lg,sl=false,col='#D7CCC8'){
  const vert=Math.abs(x1-x0)<Math.abs(y1-y0);
  const X=[],Y=[],Z=[];
  if(vert){
    const xs=linspace(x0-w/2,x0+w/2,3),ys=linspace(Math.min(y0,y1),Math.max(y0,y1),Math.max(4,Math.round(Math.abs(y1-y0)/15)+1));
    for(let j=0;j<ys.length;j++){X.push(xs.slice());Y.push(xs.map(()=>ys[j]));Z.push(xs.map(x=>getTZ(x,ys[j],L,W,slope)+.1));}
  }else{
    const xs=linspace(Math.min(x0,x1),Math.max(x0,x1),Math.max(4,Math.round(Math.abs(x1-x0)/15)+1)),ys=linspace(y0-w/2,y0+w/2,3);
    for(let j=0;j<ys.length;j++){X.push(xs.slice());Y.push(xs.map(()=>ys[j]));Z.push(xs.map(x=>getTZ(x,ys[j],L,W,slope)+.1));}
  }
  return{type:'surface',x:X,y:Y,z:Z,colorscale:[[0,col],[1,'#BCAAA4']],showscale:false,opacity:.9,name,legendgroup:lg,showlegend:sl};
}

// Seeded RNG
function makeRNG(seed){
  let s=seed>>>0;
  return ()=>{s=(s*1664525+1013904223)>>>0;return s/0xFFFFFFFF;};
}

let figData=null, lgMap={}, lgVis={};

function generateMap(){
  const L=parseFloat(document.getElementById('f-len').value)||300;
  const W=parseFloat(document.getElementById('f-wid').value)||300;
  const loc=document.getElementById('f-loc').value.trim()||'My Homestead';
  const hpos=document.getElementById('f-hpos').value;
  const slope=document.getElementById('f-slope').value;
  const water=document.getElementById('f-water').value;
  const animals=getAnimals();
  const treeCount=parseInt(document.getElementById('f-trees').value)||15;

  if(!loc){document.getElementById('status').textContent='⚠ Enter location';return;}
  document.getElementById('ov').classList.add('on');
  document.getElementById('ph').style.display='none';
  document.getElementById('status').textContent='Generating...';

  setTimeout(()=>{
    try{
      _build(L,W,loc,hpos,slope,water,animals,treeCount);
      const acres=(L*W/43560).toFixed(2);
      document.getElementById('status').textContent=`✅ ${loc} — ${L}×${W} ft — ${treeCount} trees — ${acres} acres`;
    }catch(e){
      document.getElementById('status').textContent='❌ '+e.message;
      console.error(e);
    }
    document.getElementById('ov').classList.remove('on');
  },80);
}

function _build(L,W,loc,hpos,slope,water,animals,treeCount){
  const acres=L*W/43560;
  const zr=zoneRatios(acres);
  const zPos=makeZonePos(L,W,zr,hpos);
  const [hx,hy,hw,hd]=houseBbox(L,W,hpos);
  const reg=new Reg();
  const traces=[];
  lgMap={};lgVis={};

  function add(tr,lg){
    if(!lgMap[lg])lgMap[lg]=[];
    lgMap[lg].push(traces.length);
    traces.push(tr);
  }
  function tz(x,y){return getTZ(x,y,L,W,slope);}

  // TERRAIN
  const tN=35,tXa=linspace(0,L,tN),tYa=linspace(0,W,tN);
  const TX=[],TY=[],TZ_=[];
  for(let j=0;j<tN;j++){TX.push(tXa.slice());TY.push(tXa.map(()=>tYa[j]));TZ_.push(tXa.map(x=>tz(x,tYa[j])));}
  add({type:'surface',x:TX,y:TY,z:TZ_,colorscale:[[0,'#33691E'],[.4,'#558B2F'],[.7,'#7CB342'],[1,'#9CCC65']],
    showscale:false,opacity:.85,name:'Terrain',legendgroup:'Terrain',showlegend:true,
    lighting:{ambient:.70,diffuse:.85}},'Terrain');

  // ZONES
  const ZC={z0:[[0,'#FFF9C4'],[1,'#FFFDE7']],z1:[[0,'#A5D6A7'],[1,'#C8E6C9']],
    z2:[[0,'#1B5E20'],[1,'#2E7D32']],z3:[[0,'#F9A825'],[1,'#FFF9C4']],z4:[[0,'#CE93D8'],[1,'#EDE7F6']]};
  const ZN={z0:'Zone 0 – Residential',z1:'Zone 1 – Kitchen Garden',z2:'Zone 2 – Food Forest',z3:'Zone 3 – Pasture',z4:'Zone 4 – Buffer'};
  let fz=true;
  for(const[zid,pos]of Object.entries(zPos)){
    const{x:zx,y:zy,width:zw,height:zh}=pos;
    const nX=Math.max(4,Math.round(zw/30)),nY=Math.max(4,Math.round(zh/30));
    const ZX=[],ZY=[],ZZ=[];
    for(let j=0;j<nY;j++){const ry=zy+zh*j/(nY-1);ZX.push(linspace(zx,zx+zw,nX));ZY.push(linspace(zx,zx+zw,nX).map(()=>ry));ZZ.push(linspace(zx,zx+zw,nX).map(x=>tz(x,ry)+1.1));}
    add({type:'surface',x:ZX,y:ZY,z:ZZ,colorscale:ZC[zid]||[[0,'#ccc'],[1,'#eee']],showscale:false,opacity:.40,
      name:ZN[zid]||zid,legendgroup:'Zones',showlegend:fz},'Zones');
    fz=false;
  }

  // ROADS
  const mw=10,pw=8,po=Math.min(14,L*.04,W*.04);
  const hcx=hx+hw/2,hcy=hy+hd/2;
  let fr=true;
  function addRoad(x0,y0,x1,y1,w,col='#D7CCC8'){
    const vert=Math.abs(x1-x0)<Math.abs(y1-y0);
    if(vert)reg.addRect(x0-w/2,Math.min(y0,y1),x0+w/2,Math.max(y0,y1));
    else reg.addRect(Math.min(x0,x1),y0-w/2,Math.max(x0,x1),y0+w/2);
    add(ROADSUF(x0,y0,x1,y1,w,L,W,slope,'Road','Roads',fr,col),'Roads');fr=false;
  }
  addRoad(po,po,L-po,po,pw,'#BCAAA4');addRoad(po,W-po,L-po,W-po,pw,'#BCAAA4');
  addRoad(po,po,po,W-po,pw,'#BCAAA4');addRoad(L-po,po,L-po,W-po,pw,'#BCAAA4');
  addRoad(hcx,po,hcx,hy,mw);addRoad(po,hcy,L-po,hcy,mw);addRoad(hcx,hy+hd,hcx,W-po,mw);
  reg.addRect(hx,hy,hx+hw,hy+hd);

  // HOUSE
  const hb=tz(hx+hw/2,hy+hd/2)+1.5,wh_=10,rb=hb+wh_,rt=rb+Math.min(hw,hd)*.40,wt=.5;
  const LGH='House';
  add(MB(hx-.4,hy-.4,hb-.4,hx+hw+.4,hy+hd+.4,hb,'#BCAAA4','Foundation',LGH,.90,true),'House');
  for(const[wx0,wy0,wx1,wy1,c]of[[hx,hy,hx+hw,hy+wt,'#D7CCC8'],[hx,hy+hd-wt,hx+hw,hy+hd,'#BCAAA4'],[hx,hy,hx+wt,hy+hd,'#D7CCC8'],[hx+hw-wt,hy,hx+hw,hy+hd,'#BCAAA4']])
    add(MB(wx0,wy0,hb,wx1,wy1,rb,c,'Wall',LGH,.95,false),'House');
  add(MB(hx+wt,hy+wt,hb,hx+hw-wt,hy+hd-wt,hb+.15,'#EFEBE9','Floor',LGH,.9,false),'House');
  const wwW=hw*.12,whH=wh_*.28,wZ=hb+wh_*.44;
  for(const wx of[hx+hw*.18,hx+hw*.70]){
    add(MB(wx-.1,hy-.1,wZ-.1,wx+wwW+.1,hy+wt+.1,wZ+whH+.1,'#5D4037','Window Frame',LGH,.9,false),'House');
    add(MB(wx,hy-.05,wZ,wx+wwW,hy+wt+.05,wZ+whH,'#B3E5FC','Window',LGH,.78,false),'House');
  }
  const dw=hw*.12,dx=hx+hw/2-dw/2;
  add(MB(dx,hy-.1,hb,dx+dw,hy+wt+.1,hb+wh_*.54,'#3E2723','Door',LGH,.95,false),'House');
  add(MR(hx,hy,hx+hw,hy+hd,rb,rt,'#4E342E',LGH),'House');
  add(MB(hx+hw*.72,hy+hd*.38,rb-1,hx+hw*.80,hy+hd*.46,rt+3,'#6D4C41','Chimney',LGH,.95,false),'House');
  const pW=hw*.44,pD=hd*.14,pX=hx+(hw-pW)/2,pY=hy-pD,pZ=hb+wh_*.63;
  add(MB(pX,pY,pZ,pX+pW,hy,pZ+.35,'#EFEBE9','Porch',LGH,.75,false),'House');
  for(const cx3 of[pX+pW*.1,pX+pW*.9])add(CYL(cx3,pY+pD*.5,.45,hb,pZ,'#8D6E63','Porch Col',LGH,false),'House');

  // KITCHEN GARDEN (z1, no house overlap)
  if(zPos.z1){
    const{x:gx,y:gy,width:gw,height:gh}=zPos.z1;
    const pad=6,hm=10;
    let sx0=gx+pad,sx1=gx+gw-pad,sy0=gy+pad,sy1=gy+gh-pad;
    if(!(hx+hw+hm<sx0||hx-hm>sx1||hy+hd+hm<sy0||hy-hm>sy1)){
      if(hy>sy0)sy1=Math.min(sy1,hy-hm);else sy0=Math.max(sy0,hy+hd+hm);
    }
    if(sx1-sx0>15&&sy1-sy0>15){
      const bedW=clamp(gw*.16,12,20),gap=clamp(gw*.03,5,8);
      const nBeds=Math.max(1,Math.floor((sx1-sx0-gap)/(bedW+gap)));
      const bedH=clamp(gh*.28,10,22);
      const bedB=tz(gx+gw/2,gy+gh/2)+1.3;
      let fg=true;
      for(let i=0;i<nBeds;i++){
        const bx=sx0+gap+i*(bedW+gap),by=sy0+(sy1-sy0-bedH)/2;
        if(!reg.rectOk(bx,by,bx+bedW,by+bedH))continue;
        reg.addRect(bx,by,bx+bedW,by+bedH);
        add(MB(bx,by,bedB,bx+bedW,by+bedH,bedB+.55,'#6D4C41','Garden Bed','Garden',.90,fg),'Garden');
        add(MB(bx+.3,by+.3,bedB+.55,bx+bedW-.3,by+bedH-.3,bedB+.7,'#3E2723','Soil','Garden',.95,false),'Garden');
        const pxs=[],pys=[],pzs=[];
        for(let pi=0;pi<6;pi++){pxs.push(bx+bedW*.1+pi*(bedW*.8/5));pys.push(by+bedH/2);pzs.push(bedB+.9);}
        add({type:'scatter3d',x:pxs,y:pys,z:pzs,mode:'markers',marker:{size:4,color:'#00C853',symbol:'diamond'},name:'Plants',legendgroup:'Garden',showlegend:false},'Garden');
        fg=false;
      }
    }
  }

  // GREENHOUSE
  const gh_w=clamp(hw*.45,25,L*.15),gh_hh=clamp(hd*.80,18,W*.08);
  const gh_x=clamp(hx+hw+15,0,L-gh_w),gh_y=clamp(hcy-gh_hh/2,0,W-gh_hh);
  if(reg.rectOk(gh_x,gh_y,gh_x+gh_w,gh_y+gh_hh)){
    reg.addRect(gh_x,gh_y,gh_x+gh_w,gh_y+gh_hh);
    const ghb=tz(gh_x+gh_w/2,gh_y+gh_hh/2)+1.3;
    for(const[fx_,fy_]of[[0,0],[0,1],[1,0],[1,1]])
      add(MB(gh_x+fx_*gh_w-.25,gh_y+fy_*gh_hh-.25,ghb,gh_x+fx_*gh_w+.25,gh_y+fy_*gh_hh+.25,ghb+5,'#E0E0E0','GH Frame','Garden',.9,false),'Garden');
    add(MB(gh_x,gh_y,ghb,gh_x+gh_w,gh_y+.3,ghb+5,'#B3E5FC','Greenhouse','Garden',.32,false),'Garden');
    add(MB(gh_x,gh_y+gh_hh-.3,ghb,gh_x+gh_w,gh_y+gh_hh,ghb+5,'#B3E5FC','GH Wall','Garden',.32,false),'Garden');
    add(MB(gh_x,gh_y,ghb,gh_x+.3,gh_y+gh_hh,ghb+5,'#B3E5FC','GH Wall','Garden',.32,false),'Garden');
    add(MB(gh_x+gh_w-.3,gh_y,ghb,gh_x+gh_w,gh_y+gh_hh,ghb+5,'#B3E5FC','GH Wall','Garden',.32,false),'Garden');
    add(MR(gh_x,gh_y,gh_x+gh_w,gh_y+gh_hh,ghb+5,ghb+7,'rgba(179,229,252,0.4)','Garden'),'Garden');
  }

  // COMPOST
  const z1=zPos.z1||{y:W*.1,height:W*.1,x:0};
  const cmpX=clamp(hx-38,5,L-22),cmpY=clamp(z1.y+z1.height*.6,0,W-8);
  if(reg.rectOk(cmpX,cmpY,cmpX+20,cmpY+7)){
    reg.addRect(cmpX,cmpY,cmpX+20,cmpY+7);
    const cpb=tz(cmpX+10,cmpY+3.5)+1.3;
    for(let ci=0;ci<3;ci++)add(MB(cmpX+ci*6.5,cmpY,cpb,cmpX+ci*6.5+6,cmpY+6,cpb+2.2,'#5D4037','Compost','Garden',.88,ci===0),'Garden');
  }

  // WATER
  const z3=zPos.z3||{x:0,y:W*.5,width:L,height:W*.35};
  let fw=true;
  let pondCX=z3.x+40,pondCY=z3.y+z3.height*.35,pondR=30;

  if(water.includes('Borewell')||water.includes('Well')){
    const wr=clamp(Math.min(L,W)*.015,8,18);
    let wx_=hx+hw+32,wy_=hy+hd/2;
    wx_=clamp(wx_,wr+2,L-wr-2);wy_=clamp(wy_,wr+2,W-wr-2);
    if(reg.circleOk(wx_,wy_,wr)){
      reg.addCircle(wx_,wy_,wr);
      const wb=tz(wx_,wy_);
      add(CYL(wx_,wy_,wr,wb,wb+1.5,'#8D8D8D','Well','Water',fw),'Water');fw=false;
      add(CYL(wx_,wy_,wr*.6,wb+1.5,wb+2.2,'#455A64','Well Top','Water',false),'Water');
      for(const[px_,py_]of[[wx_-wr*.8,wy_],[wx_+wr*.8,wy_]])
        add(MB(px_-.25,py_-.25,wb+1.5,px_+.25,py_+.25,wb+4.5,'#5D4037','Well Post','Water',.95,false),'Water');
      add(MB(wx_-wr*.8-.3,wy_-.15,wb+4.3,wx_+wr*.8+.3,wy_+.15,wb+4.7,'#4E342E','Well Beam','Water',.95,false),'Water');
    }
  }

  if(water.includes('River')||water.includes('Pond')||animals.includes('Fish')){
    pondR=clamp(Math.min(L,W)*.06,20,60);
    pondCX=z3.x+pondR+z3.width*.05;pondCY=z3.y+z3.height*.35;
    if(reg.circleOk(pondCX,pondCY,pondR)){
      reg.addCircle(pondCX,pondCY,pondR);
      const pb=tz(pondCX,pondCY);
      const pN=28,pt=linspace(0,2*Math.PI,pN);
      const pX=[],pY=[],pZ_=[];
      for(let j=0;j<3;j++){pX.push(pt.map(a=>pondCX+pondR*(.85+j*.075)*Math.cos(a)));pY.push(pt.map(a=>pondCY+pondR*(.85+j*.075)*Math.sin(a)));pZ_.push(pt.map(()=>pb+.2));}
      add({type:'surface',x:pX,y:pY,z:pZ_,colorscale:[[0,'#0277BD'],[1,'#4FC3F7']],showscale:false,opacity:.75,name:'Pond',legendgroup:'Water',showlegend:fw},'Water');fw=false;
      add(CYL(pondCX,pondCY,pondR+1,pb-.3,pb+.3,'#8D6E63','Pond Shore','Water',false,24),'Water');
      for(let ri=0;ri<8;ri++){const ra=(ri/8)*2*Math.PI;const rx=pondCX+(pondR+2)*Math.cos(ra),ry=pondCY+(pondR+2)*Math.sin(ra);add(CYL(rx,ry,.15,pb+.3,pb+3.5,'#558B2F','Reed','Water',false,6),'Water');}
    }
  }

  if(water.includes('Rainwater')){
    const rt_w=clamp(L*.05,15,40),rt_h_=clamp(hd*.4,10,25);
    const rtx=clamp(hx-rt_w-18,0,L-rt_w),rty=hy;
    if(reg.rectOk(rtx,rty,rtx+rt_w,rty+rt_h_)){
      reg.addRect(rtx,rty,rtx+rt_w,rty+rt_h_);
      const rb2=tz(rtx+rt_w/2,rty+rt_h_/2)+1.3;
      add(MB(rtx,rty,rb2,rtx+rt_w,rty+rt_h_,rb2+6,'#1565C0','Rain Tank','Water',.88,fw),'Water');fw=false;
      add(MB(rtx-.3,rty-.3,rb2+6,rtx+rt_w+.3,rty+rt_h_+.3,rb2+6.5,'#0D47A1','Tank Lid','Water',.9,false),'Water');
    }
  }

  // Water tank (always)
  const wt_x=clamp(hcx-5,0,L-12),wt_y=clamp(hcy+22,0,W-12);
  if(reg.rectOk(wt_x,wt_y,wt_x+12,wt_y+12)){
    reg.addRect(wt_x,wt_y,wt_x+12,wt_y+12);
    const wtb=tz(wt_x+6,wt_y+6)+1.3;
    for(const[lx_,ly_]of[[-3,-3],[-3,3],[3,-3],[3,3]])
      add(MB(wt_x+6+lx_-.25,wt_y+6+ly_-.25,wtb,wt_x+6+lx_+.25,wt_y+6+ly_+.25,wtb+5,'#546E7A','Tank Leg','Water',.9,fw),'Water');
    add(CYL(wt_x+6,wt_y+6,3.5,wtb+5,wtb+9,'#263238','Water Tank','Water',false),'Water');
    fw=false;
  }

  // SOLAR
  const sol_x=clamp(hx-42,5,L-40),sol_y=clamp(hy-28,5,W-15);
  if(reg.rectOk(sol_x,sol_y,sol_x+36,sol_y+12)){
    reg.addRect(sol_x,sol_y,sol_x+36,sol_y+12);
    const sb=tz(sol_x+18,sol_y+6)+1.3;
    let fs=true;
    for(let si=0;si<3;si++){
      const sx=sol_x+si*12+1;
      add(MB(sx,sol_y,sb+1.5,sx+10,sol_y+8,sb+1.7,'#212121','Solar Panel','Solar',.9,fs),'Solar');
      add(MB(sx+.3,sol_y+.3,sb+1.72,sx+9.7,sol_y+7.7,sb+1.8,'#1565C0','PV Cell','Solar',.9,false),'Solar');
      add(MB(sx+4.5,sol_y+3,sb,sx+5.5,sol_y+4,sb+1.5,'#9E9E9E','Sol Post','Solar',.9,false),'Solar');
      fs=false;
    }
  }

  // WIND TURBINE
  const tb_x=clamp(L*.88,0,L-8),tb_y=clamp(W*.88,0,W-8);
  if(reg.circleOk(tb_x,tb_y,5)){
    reg.addCircle(tb_x,tb_y,5);
    const tbb=tz(tb_x,tb_y)+1.3;
    add(CYL(tb_x,tb_y,.6,tbb,tbb+25,'#E0E0E0','Wind Turbine','Solar',false),'Solar');
    add(CYL(tb_x,tb_y,1,tbb+25,tbb+25.5,'#BDBDBD','Hub','Solar',false,12),'Solar');
    for(let bi=0;bi<3;bi++){
      const ba=bi*2*Math.PI/3;const bx=tb_x+Math.cos(ba)*7,by_=tb_y+Math.sin(ba)*7;
      add(MB(Math.min(tb_x,bx)-.4,Math.min(tb_y,by_)-.4,tbb+25,Math.max(tb_x,bx)+.4,Math.max(tb_y,by_)+.4,tbb+25.5,'#FAFAFA','Blade','Solar',.9,false),'Solar');
    }
  }

  // LIVESTOCK (zone 3, right portion, no overlap)
  const SHED_COL={Goats:'#8D6E63',Chickens:'#A1887F',Pigs:'#F48FB1',Cows:'#795548',Bees:'#FDD835'};
  const SHED_SZ={Goats:[30,22],Chickens:[25,18],Pigs:[28,20],Cows:[35,25],Bees:[15,12]};
  const animalKeys=animals.filter(a=>a!=='None'&&a!=='Fish');
  if(animalKeys.length>0){
    const lv_margin=Math.max(z3.width*.25,50);
    const gx0=z3.x+lv_margin,gy0=z3.y+z3.height*.04;
    const gW=z3.width-lv_margin-z3.width*.03,gH=z3.height*.92;
    const n=animalKeys.length,cols=n>1?2:1,rows=Math.ceil(n/cols);
    const gap=Math.max(gW*.04,10);
    const cellW=Math.max((gW-(cols+1)*gap)/cols,30);
    const cellH=Math.max((gH-(rows+1)*gap)/rows,25);
    let fl=true;
    for(let idx=0;idx<n;idx++){
      const animal=animalKeys[idx],col=idx%cols,row=Math.floor(idx/cols);
      const sx_=gx0+gap+col*(cellW+gap),sy_=gy0+gap+row*(cellH+gap);
      const[swF,shF]=SHED_SZ[animal]||[25,18];
      const swW=clamp(cellW*.85,swF,L*.2),swH=clamp(cellH*.75,shF,W*.18);
      const sx2=clamp(sx_,0,L-swW),sy2=clamp(sy_,0,W-swH);
      if(!reg.rectOk(sx2,sy2,sx2+swW,sy2+swH))continue;
      reg.addRect(sx2,sy2,sx2+swW,sy2+swH);
      const sbase=tz(sx2+swW/2,sy2+swH/2)+1.3,sc=SHED_COL[animal]||'#8D6E63';
      add(MB(sx2,sy2,sbase,sx2+swW,sy2+swH,sbase+4,sc,animal+' Shed','Livestock',.92,fl),'Livestock');
      add(MR(sx2,sy2,sx2+swW,sy2+swH,sbase+4,sbase+6,'#4E342E','Livestock'),'Livestock');
      add({type:'scatter3d',x:[sx2+swW/2],y:[sy2+swH/2],z:[sbase+7],mode:'text',text:[animal],
        textfont:{size:9,color:'#1a1a1a'},name:animal,legendgroup:'Livestock',showlegend:false},'Livestock');
      fl=false;
    }
  }
  if(animals.includes('Fish')){
    const ft_w=clamp(pondR*1.8,20,80),ft_h_=clamp(pondR*1.2,15,50);
    const ftx=clamp(pondCX-ft_w/2,0,L-ft_w),fty=clamp(pondCY+pondR+14,0,W-ft_h_);
    if(reg.rectOk(ftx,fty,ftx+ft_w,fty+ft_h_)){
      reg.addRect(ftx,fty,ftx+ft_w,fty+ft_h_);
      const fb=tz(ftx+ft_w/2,fty+ft_h_/2)+1.3;
      add(MB(ftx,fty,fb,ftx+ft_w,fty+ft_h_,fb+1.5,'#0288D1','Fish Tank','Livestock',.8,false),'Livestock');
    }
  }

  // SWALES (if slope)
  if(slope!=='Flat'){
    const sw_h_=clamp(W*.004,3,8);let fsw=true;
    for(const fy_ of[z3.y+z3.height*.28,z3.y+z3.height*.62]){
      add(MB(z3.x,fy_,tz(z3.x+z3.width*.37,fy_)+1.05,z3.x+z3.width*.75,fy_+sw_h_,tz(z3.x+z3.width*.37,fy_)+1.5,'#5D4037','Swale','Water',.8,fsw),'Water');
      fsw=false;
    }
  }

  // TREES (zone 2, strict collision)
  const z2=zPos.z2;
  if(z2){
    const min_sp=Math.max(z2.width/Math.max(treeCount,1),15);
    const placed_=[];let ftree=true,cnt=0,att=0;
    const rng=makeRNG(42);
    while(cnt<Math.min(treeCount,40)&&att<treeCount*15){
      att++;
      const margin=Math.max(min_sp*.4,10);
      const tx_=z2.x+margin+rng()*(z2.width-2*margin);
      const ty_=z2.y+margin+rng()*(z2.height-2*margin);
      if(placed_.some(([px_,py_])=>(tx_-px_)**2+(ty_-py_)**2<min_sp**2))continue;
      const spN=SP_CYCLE[cnt%SP_CYCLE.length],sp=TREE_SP[spN];
      const tx2=clamp(tx_,z2.x+sp.cr+2,z2.x+z2.width-sp.cr-2);
      const ty2=clamp(ty_,z2.y+sp.cr+2,z2.y+z2.height-sp.cr-2);
      if(!reg.circleOk(tx2,ty2,sp.cr))continue;
      reg.addCircle(tx2,ty2,sp.cr);placed_.push([tx2,ty2]);
      const tb=tz(tx2,ty2)+1.3;
      add(CYL(tx2,ty2,sp.tr,tb,tb+sp.th,'#5D4037',spN,'Trees',ftree),'Trees');
      add(CONE(tx2,ty2,sp.cr,tb+sp.cb,tb+sp.ct,sp.c1,spN,'Trees',false),'Trees');
      add(CONE(tx2,ty2,sp.cr*.65,tb+sp.cb+sp.cr*.3,tb+sp.ct+sp.cr*.1,sp.c2,spN,'Trees',false),'Trees');
      ftree=false;cnt++;
    }
    // Buffer (z4)
    if(zPos.z4&&treeCount>15){
      const z4=zPos.z4,rng2=makeRNG(77);
      for(let i=0;i<Math.min(treeCount-15,15);i++){
        const tx_=z4.x+12+rng2()*(z4.width-24),ty_=z4.y+12+rng2()*(z4.height-24);
        const spN=['Neem','Teak','Bamboo'][i%3],sp=TREE_SP[spN];
        if(!reg.circleOk(tx_,ty_,sp.cr))continue;
        reg.addCircle(tx_,ty_,sp.cr);
        const tb=tz(tx_,ty_)+1.3;
        add(CYL(tx_,ty_,sp.tr,tb,tb+sp.th,'#5D4037',spN,'Trees',false),'Trees');
        add(CONE(tx_,ty_,sp.cr,tb+sp.cb,tb+sp.ct,sp.c1,spN,'Trees',false),'Trees');
        add(CONE(tx_,ty_,sp.cr*.65,tb+sp.cb+sp.cr*.3,tb+sp.ct+sp.cr*.1,sp.c2,spN,'Trees',false),'Trees');
      }
    }
  }

  // FENCE
  const fo=2,fsegs=[[fo,fo,L-fo,fo],[L-fo,fo,L-fo,W-fo],[L-fo,W-fo,fo,W-fo],[fo,W-fo,fo,fo]];
  let ffn=true;
  for(const[fx0,fy0,fx1,fy1]of fsegs){
    const flen=Math.sqrt((fx1-fx0)**2+(fy1-fy0)**2),nP=Math.max(2,Math.round(flen/20));
    for(let fpi=0;fpi<=nP;fpi++){
      const t_=fpi/nP,fpx=fx0+t_*(fx1-fx0),fpy=fy0+t_*(fy1-fy0);
      const fpb=tz(fpx,fpy)+.1;
      add(MB(fpx-.2,fpy-.2,fpb,fpx+.2,fpy+.2,fpb+1.8,'#795548','Fence Post','Roads',.9,ffn),'Roads');
      ffn=false;
    }
  }

  // GATE
  const gx_=clamp(hcx-4,fo+1,L-fo-9);
  add(MB(gx_,fo-.2,tz(gx_,fo)+.1,gx_+8,fo+.2,tz(gx_,fo)+2.5,'#FDD835','Gate','Roads',.95,false),'Roads');

  // LAYOUT
  const layout={
    title:{text:`🏡 ${loc} — ${(acres).toFixed(2)} acres  (${L}×${W} ft)<br><sup>${treeCount} trees · Animals: ${animals.join(', ')||'None'} · Budget: ${document.getElementById('f-budget').value} · Click legend to toggle layers</sup>`,
      font:{size:13,color:'#2E7D32',family:'Segoe UI,Arial'},x:.5},
    scene:{
      xaxis:{title:'Length (ft)',showgrid:true,gridcolor:'#B0BEC5',showbackground:true,backgroundcolor:'#EAF4FB'},
      yaxis:{title:'Width (ft)',showgrid:true,gridcolor:'#B0BEC5',showbackground:true,backgroundcolor:'#EAF4FB'},
      zaxis:{title:'Height (ft)',showgrid:true,gridcolor:'#B0BEC5',showbackground:true,backgroundcolor:'#EAF4FB',range:[-2,40]},
      aspectmode:'data',bgcolor:'#C9E8F5',
      camera:{eye:{x:1.3,y:-1.5,z:.85},up:{x:0,y:0,z:1}}
    },
    legend:{x:.01,y:.98,bgcolor:'rgba(255,255,255,0.93)',bordercolor:'#90A4AE',borderwidth:1.5,
      font:{size:10},itemclick:'toggle',itemdoubleclick:'toggleothers',
      title:{text:'<b>Layers</b>',font:{size:9}}},
    paper_bgcolor:'#EAF4FB',margin:{l:0,r:0,t:65,b:0},autosize:true,
  };

  figData={traces,layout,loc,L,W,treeCount,animals,acres};
  lgMap={...lgMap,...(()=>{const m={};Object.assign(m,lgMap);return lgMap;})()};
  // rebuild lgMap
  const newLgMap={};
  traces.forEach((tr,i)=>{const lg=tr.legendgroup;if(!newLgMap[lg])newLgMap[lg]=[];newLgMap[lg].push(i);});
  lgMap=newLgMap;lgVis={};

  Plotly.newPlot('plot',traces,layout,{responsive:true,scrollZoom:true,displayModeBar:true,
    modeBarButtonsToRemove:[],displaylogo:false});

  // Reset toggle buttons
  document.querySelectorAll('.tgl-btn').forEach(b=>b.classList.remove('off'));
}

function toggleLG(btn){
  const lg=btn.dataset.lg;
  if(!lgMap[lg])return;
  const nowHidden=lgVis[lg]===false;
  lgVis[lg]=nowHidden?true:false;
  Plotly.restyle('plot',{visible:nowHidden?true:'legendonly'},lgMap[lg]);
  btn.classList.toggle('off',!nowHidden?true:false);
}

function setCam(ex,ey,ez){
  if(!document.getElementById('plot').data)return;
  Plotly.relayout('plot',{'scene.camera.eye':{x:ex,y:ey,z:ez},'scene.camera.up':{x:0,y:ez>1.5?1:0,z:ez>1.5?0:1}});
}

function downloadMap(){
  if(!figData){alert('Please generate the map first!');return;}
  const{traces,layout,loc}=figData;
  const htmlContent=`<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Homestead — ${loc}</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"><\/script>
<style>*{margin:0;padding:0}body{background:#EAF4FB}#p{width:100vw;height:100vh}<\/style>
</head><body><div id="p"></div>
<script>
var t=${JSON.stringify(traces)};
var l=${JSON.stringify(layout)};
l.autosize=true;l.width=undefined;l.height=undefined;
Plotly.newPlot('p',t,l,{responsive:true,scrollZoom:true,displayModeBar:true,displaylogo:false});
<\/script></body></html>`;
  const blob=new Blob([htmlContent],{type:'text/html'});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download=`homestead-${loc.replace(/[\s,]+/g,'-').toLowerCase()}.html`;
  a.click();
}

window.addEventListener('load',()=>setTimeout(generateMap,300));
window.addEventListener('resize',()=>{if(document.getElementById('plot').data)Plotly.relayout('plot',{autosize:true});});
</script>
</body>
</html>
