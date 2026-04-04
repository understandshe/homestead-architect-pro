import streamlit as st
import json

class Visualizer3D:
    """
    Homestead Architect Pro 2026 - Plotly 3D Engine.
    Integrated with Streamlit and Interactive HTML/JS.
    """
    def create(self, layout_data: dict):
        # Python डेटा को JSON में बदलें ताकि JS इसे पढ़ सके
        json_layout = json.dumps(layout_data)
        
        # पूरा HTML कोड इस f-string के अंदर होना चाहिए
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🏡 Smart Homestead Designer Pro 2026</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',Arial,sans-serif;background:#EAF4FB;color:#1a1a1a}}
#main{{display:flex;height:100vh;overflow:hidden}}
#sidebar{{width:310px;min-width:260px;background:#fff;border-right:1px solid #cde;overflow-y:auto;display:flex;flex-direction:column;z-index:10}}
#sidebar-header{{background:#166534;color:#fff;padding:12px 14px}}
#sidebar-header h2{{font-size:14px;font-weight:600;margin-bottom:1px}}
#sidebar-header p{{font-size:10px;opacity:0.8}}
#form-body{{padding:12px;flex:1}}
.sec{{font-size:10px;font-weight:700;color:#166534;text-transform:uppercase;letter-spacing:0.6px;margin:12px 0 5px;border-bottom:1px solid #e0eed8;padding-bottom:3px}}
.field{{margin-bottom:8px}}
.field label{{display:block;font-size:11px;color:#444;margin-bottom:2px;font-weight:500}}
.field input[type=text],.field input[type=number],.field select{{width:100%;padding:5px 8px;font-size:12px;border:1px solid #ccc;border-radius:6px;background:#fafffe;color:#1a1a1a;outline:none}}
.field input:focus,.field select:focus{{border-color:#166534}}
.dim-row{{display:grid;grid-template-columns:1fr 1fr;gap:7px}}
.check-group{{display:flex;flex-wrap:wrap;gap:4px}}
.chip{{display:flex;align-items:center;gap:3px;padding:3px 8px;font-size:11px;border:1px solid #ccc;border-radius:16px;cursor:pointer;background:#f9f9f9;user-select:none;transition:all 0.12s}}
.chip input{{display:none}}
.chip.active{{background:#166534;color:#fff;border-color:#166534}}
.rw{{display:flex;align-items:center;gap:6px}}
.rw input[type=range]{{flex:1;accent-color:#166534;height:4px}}
.rv{{font-size:12px;font-weight:600;color:#166534;min-width:22px;text-align:right}}
#btn-gen{{width:100%;padding:9px;background:#166534;color:#fff;border:none;border-radius:7px;font-size:13px;font-weight:600;cursor:pointer;margin-top:5px}}
#btn-gen:hover{{background:#15803d}}
#btn-dl{{width:100%;padding:7px;background:#fff;color:#166534;border:1.5px solid #166534;border-radius:7px;font-size:12px;font-weight:500;cursor:pointer;margin-top:5px}}
#btn-dl:hover{{background:#f0fdf4}}
#status{{font-size:10px;color:#555;text-align:center;padding:5px 0;min-height:20px}}
#map-panel{{flex:1;display:flex;flex-direction:column;overflow:hidden;position:relative}}
#toolbar{{background:#fff;border-bottom:1px solid #cde;padding:6px 10px;display:flex;align-items:center;gap:5px;flex-wrap:wrap}}
#toolbar span{{font-size:11px;color:#555;margin-right:2px;font-weight:600}}
.tgl-btn{{padding:3px 8px;font-size:10px;border:1px solid #aaa;border-radius:5px;background:#f5f5f5;cursor:pointer;transition:all 0.12s;white-space:nowrap}}
.tgl-btn:hover{{border-color:#166634;color:#166534}}
.tgl-btn.off{{opacity:0.38;text-decoration:line-through}}
#cam-btns{{margin-left:auto;display:flex;gap:4px}}
.cam-btn{{padding:3px 9px;font-size:10px;border:1px solid #90CAF9;border-radius:5px;background:#E3F2FD;cursor:pointer;color:#1565C0;white-space:nowrap}}
.cam-btn:hover{{background:#BBDEFB}}
#plotly-wrap{{flex:1;min-height:0;position:relative}}
#plot{{width:100%;height:100%}}
#ph{{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;color:#888;gap:8px;background:#EAF4FB;position:absolute;inset:0}}
#ph .icon{{font-size:44px}}
#ph p{{font-size:13px}}
#ov{{display:none;position:absolute;inset:0;background:rgba(234,244,251,0.85);align-items:center;justify-content:center;flex-direction:column;gap:10px;z-index:50}}
#ov.on{{display:flex}}
.spin{{width:36px;height:36px;border:3px solid #cde;border-top-color:#166534;border-radius:50%;animation:sp 0.75s linear infinite}}
@keyframes sp{{to{{transform:rotate(360deg)}}}}
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
      <select id="f-budget"><option>Under $5,000</option><option>$5,000 - $25,000</option><option>$25,000 - $100,000</option><option>$100,00,000+</option><option>Not sure</option></select>
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
document.querySelectorAll('.chip').forEach(c=>{{
  c.addEventListener('click',()=>{{const cb=c.querySelector('input');cb.checked=!cb.checked;c.classList.toggle('active',cb.checked);}});
}});
// Sync range display
document.getElementById('f-trees').addEventListener('input',function(){{
  document.getElementById('tv').textContent=this.value;
  document.getElementById('f-trees-val').textContent=this.value;
}});

function getAnimals(){{return[...document.querySelectorAll('#animals input:checked')].map(c=>c.value);}}
function clamp(v,lo,hi){{return Math.max(lo,Math.min(hi,v));}}
function linspace(a,b,n){{const r=[];for(let i=0;i<n;i++)r.push(a+(b-a)*(n>1?i/(n-1):0));return r;}}

function getTZ(x,y,L,W,slope){{
  if(slope==='South')return y*0.025;
  if(slope==='North')return(W-y)*0.025;
  if(slope==='East')return x*0.025;
  if(slope==='West')return(L-x)*0.025;
  return 0;
}}

function zoneRatios(acres){{
  if(acres<0.5)return{{z0:.10,z1:.18,z2:.22,z3:.38,z4:.12}};
  if(acres<5)  return{{z0:.08,z1:.14,z2:.28,z3:.35,z4:.15}};
  return             {{z0:.05,z1:.10,z2:.35,z3:.30,z4:.20}};
}}

function makeZonePos(L,W,zr,hpos){{
  const pos={{}};
  if(hpos==='North'){{let y=W;for(const z of['z0','z1','z2','z3','z4']){{const h=W*zr[z];y-=h;pos[z]={{x:0,y,width:L,height:h}};}}}}
  else if(hpos==='East'){{let x=L;for(const z of['z0','z1','z2','z3','z4']){{const w=L*zr[z];x-=w;pos[z]={{x,y:0,width:w,height:W}};}}}}
  else if(hpos==='West'){{let x=0;for(const z of['z0','z1','z2','z3','z4']){{const w=L*zr[z];pos[z]={{x,y:0,width:w,height:W}};x+=w;}}}}
  else{{let y=0;for(const z of['z0','z1','z2','z3','z4']){{const h=W*zr[z];pos[z]={{x:0,y,width:L,height:h}};y+=h;}}}}
  return pos;
}}

function houseBbox(L,W,hpos){{
  const m={{
    'North':[L*.30,W*.82,L*.38,W*.12],'South':[L*.30,W*.06,L*.38,W*.12],
    'East':[L*.74,W*.36,L*.20,W*.28],'West':[L*.06,W*.36,L*.20,W*.28],
    'Center':[L*.35,W*.40,L*.30,W*.20],'Not built yet':[L*.35,W*.40,L*.30,W*.20]
  }};
  return m[hpos]||m['Center'];
}}

class Reg{{
  constructor(){{this.rects=[];this.circles=[];this.GAP=8;}}
  addRect(x0,y0,x1,y1){{this.rects.push([Math.min(x0,x1),Math.min(y0,y1),Math.max(x0,x1),Math.max(y0,y1)]);}}
  addCircle(cx,cy,r){{this.circles.push([cx,cy,r]);}}
  rectOk(x0,y0,x1,y1){{
    const g=this.GAP,ax0=Math.min(x0,x1)-g,ay0=Math.min(y0,y1)-g,ax1=Math.max(x0,x1)+g,ay1=Math.max(y0,y1)+g;
    for(const[rx0,ry0,rx1,ry1]of this.rects)if(ax0<rx1&&ax1>rx0&&ay0<ry1&&ay1>ry0)return false;
    for(const[cx,cy,r]of this.circles){{const nx=clamp(cx,ax0,ax1),ny=clamp(cy,ay0,ay1);if((cx-nx)**2+(cy-ny)**2<(r+g)**2)return false;}}
    return true;
  }}
  circleOk(cx,cy,r){{
    const g=this.GAP;
    for(const[rx0,ry0,rx1,ry1]of this.rects){{const nx=clamp(cx,rx0,rx1),ny=clamp(cy,ry0,ry1);if((cx-nx)**2+(cy-ny)**2<(r+g)**2)return false;}}
    for(const[ocx,ocy,or_]of this.circles)if((cx-ocx)**2+(cy-ocy)**2<(r+or_+g)**2)return false;
    return true;
  }}
}}

const TREE_SP={{
  Mango:    {{th:5,cb:5,ct:20,cr:8, tr:1.0,c1:'#2E7D32',c2:'#388E3C'}},
  Jackfruit:{{th:8,cb:8,ct:26,cr:9, tr:1.3,c1:'#1B5E20',c2:'#2E7D32'}},
  Coconut:  {{th:20,cb:20,ct:30,cr:5,tr:0.6,c1:'#33691E',c2:'#558B2F'}},
  Banana:   {{th:3,cb:3,ct:10,cr:4, tr:1.4,c1:'#558B2F',c2:'#7CB342'}},
  Guava:    {{th:4,cb:4,ct:13,cr:4, tr:0.7,c1:'#33691E',c2:'#43A047'}},
  Papaya:   {{th:4,cb:4,ct:11,cr:3, tr:0.5,c1:'#558B2F',c2:'#8BC34A'}},
  Avocado:  {{th:7,cb:7,ct:18,cr:6, tr:0.9,c1:'#2E7D32',c2:'#1B5E20'}},
  Moringa:  {{th:6,cb:6,ct:15,cr:3, tr:0.5,c1:'#66BB6A',c2:'#4CAF50'}},
  Citrus:   {{th:4,cb:4,ct:12,cr:4, tr:0.6,c1:'#43A047',c2:'#66BB6A'}},
  Neem:     {{th:9,cb:9,ct:24,cr:9, tr:1.1,c1:'#388E3C',c2:'#2E7D32'}},
  Teak:     {{th:14,cb:14,ct:28,cr:7,tr:0.9,c1:'#1B5E20',c2:'#2E7D32'}},
  Bamboo:   {{th:1,cb:1,ct:16,cr:2, tr:0.4,c1:'#4CAF50',c2:'#8BC34A'}},
}};
const SP_CYCLE=Object.keys(TREE_SP);

function MB(x0,y0,z0,x1,y1,z1,col,name,lg,op=0.92,sl=false){{
  return{{type:'mesh3d',
    x:[x0,x1,x1,x0,x0,x1,x1,x0],y:[y0,y0,y1,y1,y0,y0,y1,y1],z:[z0,z0,z0,z0,z1,z1,z1,z1],
    i:[0,0,4,4,0,0,2,2,0,0,1,1],j:[1,2,5,6,1,5,3,7,3,7,2,6],k:[2,3,6,7,5,4,7,6,7,4,6,5],
    color:col,opacity:op,name,legendgroup:lg,showlegend:sl,flatshading:true,
    lighting:{{ambient:0.65,diffuse:0.88,specular:0.25,roughness:0.55}}}};
}}
function MR(x0,y0,x1,y1,zb,zt,col,lg){{
  const cx=(x0+x1)/2,cy=(y0+y1)/2;
  return{{type:'mesh3d',x:[x0,x1,x1,x0,cx],y:[y0,y0,y1,y1,cy],z:[zb,zb,zb,zb,zt],
    i:[0,1,2,3],j:[1,2,3,0],k:[4,4,4,4],color:col,opacity:.97,name:'Roof',legendgroup:lg,showlegend:false,flatshading:true}};
}}
function CYL(cx,cy,r,z0,z1,col,name,lg,sl=false,n=18){{
  const t=linspace(0,2*Math.PI,n);
  const X=[],Y=[],Z=[];
  for(const zi of[z0,z1]){{X.push(t.map(a=>cx+r*Math.cos(a)));Y.push(t.map(a=>cy+r*Math.sin(a)));Z.push(t.map(()=>zi));}}
  return{{type:'surface',x:X,y:Y,z:Z,colorscale:[[0,col],[1,col]],showscale:false,opacity:.92,name,legendgroup:lg,showlegend:sl}};
}}
function CONE(cx,cy,r,zb,zt,col,name,lg,sl=false,n=14){{
  const t=linspace(0,2*Math.PI,n);
  const xs=t.map(a=>cx+r*Math.cos(a)).concat([cx]),ys=t.map(a=>cy+r*Math.sin(a)).concat([cy]),zs=t.map(()=>zb).concat([zt]);
  const ii=[],jj=[],kk=[];for(let i=0;i<n;i++){{ii.push(i);jj.push((i+1)%n);kk.push(n);}}
  return{{type:'mesh3d',x:xs,y:ys,z:zs,i:ii,j:jj,k:kk,color:col,opacity:.88,name,legendgroup:lg,showlegend:sl,flatshading:true}};
}}
function ROADSUF(x0,y0,x1,y1,w,L,W,slope,name,lg,sl=false,col='#D7CCC8'){{
  const vert=Math.abs(x1-x0)<Math.abs(y1-y0);
  const X=[],Y=[],Z=[];
  if(vert){{
    const xs=linspace(x0-w/2,x0+w/2,3),ys=linspace(Math.min(y0,y1),Math.max(y0,y1),Math.max(4,Math.round(Math.abs(y1-y0)/15)+1));
    for(let j=0;j<ys.length;j++){{X.push(xs.slice());Y.push(xs.map(()=>ys[j]));Z.push(xs.map(x=>getTZ(x,ys[j],L,W,slope)+.1));}}
  }}else{{
    const xs=linspace(Math.min(x0,x1),Math.max(x0,x1),Math.max(4,Math.round(Math.abs(x1-x0)/15)+1)),ys=linspace(y0-w/2,y0+w/2,3);
    for(let j=0;j<ys.length;j++){{X.push(xs.slice());Y.push(xs.map(()=>ys[j]));Z.push(xs.map(x=>getTZ(x,ys[j],L,W,slope)+.1));}}
  }}
  return{{type:'surface',x:X,y:Y,z:Z,colorscale:[[0,col],[1,'#BCAAA4']],showscale:false,opacity:.9,name,legendgroup:lg,showlegend:sl}};
}}

function makeRNG(seed){{
  let s=seed>>>0;
  return ()=>{{s=(s*1664525+1013904223)>>>0;return s/0xFFFFFFFF;}};
}}

let figData=null, lgMap={{}}, lgVis={{}};

function generateMap(){{
  const L=parseFloat(document.getElementById('f-len').value)||300;
  const W=parseFloat(document.getElementById('f-wid').value)||300;
  const loc=document.getElementById('f-loc').value.trim()||'My Homestead';
  const hpos=document.getElementById('f-hpos').value;
  const slope=document.getElementById('f-slope').value;
  const water=document.getElementById('f-water').value;
  const animals=getAnimals();
  const treeCount=parseInt(document.getElementById('f-trees').value)||15;

  document.getElementById('ov').classList.add('on');
  document.getElementById('ph').style.display='none';
  document.getElementById('status').textContent='Generating...';

  setTimeout(()=>{{
    try{{
      _build(L,W,loc,hpos,slope,water,animals,treeCount);
      const acres=(L*W/43560).toFixed(2);
      document.getElementById('status').textContent=`✅ ${{loc}} — ${{L}}×${{W}} ft — ${{treeCount}} trees`;
    }}catch(e){{
      document.getElementById('status').textContent='❌ '+e.message;
    }}
    document.getElementById('ov').classList.remove('on');
  }},80);
}}

function _build(L,W,loc,hpos,slope,water,animals,treeCount){{
  const acres=L*W/43560;
  const zr=zoneRatios(acres);
  const zPos=makeZonePos(L,W,zr,hpos);
  const [hx,hy,hw,hd]=houseBbox(L,W,hpos);
  const reg=new Reg();
  const traces=[];
  lgMap={{}};lgVis={{}};

  function add(tr,lg){{
    if(!lgMap[lg])lgMap[lg]=[];
    lgMap[lg].push(traces.length);
    traces.push(tr);
  }}
  function tz(x,y){{return getTZ(x,y,L,W,slope);}}

  // Terrain
  const tN=35,tXa=linspace(0,L,tN),tYa=linspace(0,W,tN);
  const TX=[],TY=[],TZ_=[];
  for(let j=0;j<tN;j++){{TX.push(tXa.slice());TY.push(tXa.map(()=>tYa[j]));TZ_.push(tXa.map(x=>tz(x,tYa[j])));}}
  add({{type:'surface',x:TX,y:TY,z:TZ_,colorscale:[[0,'#33691E'],[.4,'#558B2F'],[.7,'#7CB342'],[1,'#9CCC65']],
    showscale:false,opacity:.85,name:'Terrain',legendgroup:'Terrain',showlegend:true}},'Terrain');

  // Zones
  const ZC={{z0:[[0,'#FFF9C4'],[1,'#FFFDE7']],z1:[[0,'#A5D6A7'],[1,'#C8E6C9']],
    z2:[[0,'#1B5E20'],[1,'#2E7D32']],z3:[[0,'#F9A825'],[1,'#FFF9C4']],z4:[[0,'#CE93D8'],[1,'#EDE7F6']]}};
  let fz=true;
  for(const[zid,pos]of Object.entries(zPos)){{
    const{{x:zx,y:zy,width:zw,height:zh}}=pos;
    const nX=Math.max(4,Math.round(zw/30)),nY=Math.max(4,Math.round(zh/30));
    const ZXS=[],ZYS=[],ZZS=[];
    for(let j=0;j<nY;j++){{const ry=zy+zh*j/(nY-1);ZXS.push(linspace(zx,zx+zw,nX));ZYS.push(linspace(zx,zx+zw,nX).map(()=>ry));ZZS.push(linspace(zx,zx+zw,nX).map(x=>tz(x,ry)+1.1));}}
    add({{type:'surface',x:ZXS,y:ZYS,z:ZZS,colorscale:ZC[zid],showscale:false,opacity:.40,name:zid,legendgroup:'Zones',showlegend:fz}},'Zones');fz=false;
  }}

  // Roads & Infrastructure
  const mw=10,pw=8,po=Math.min(14,L*.04,W*.04);
  const hcx=hx+hw/2,hcy=hy+hd/2;
  let fr=true;
  function addRoad(x0,y0,x1,y1,w,col='#D7CCC8'){{
    add(ROADSUF(x0,y0,x1,y1,w,L,W,slope,'Road','Roads',fr,col),'Roads');fr=false;
  }}
  addRoad(po,po,L-po,po,pw);addRoad(po,W-po,L-po,W-po,pw);
  addRoad(hcx,po,hcx,hy,mw);

  // House
  const hb=tz(hcx,hcy)+1.5;
  add(MB(hx,hy,hb,hx+hw,hy+hd,hb+10,'#D7CCC8','House','House',.95,true),'House');
  add(MR(hx,hy,hx+hw,hy+hd,hb+10,hb+15,'#4E342E','House'),'House');

  // Trees
  const z2=zPos.z2;
  if(z2){{
    let ftree=true;
    for(let i=0;i<Math.min(treeCount,40);i++){{
      const tx=z2.x+Math.random()*z2.width, ty=z2.y+Math.random()*z2.height;
      const tbb=tz(tx,ty)+1.3;
      add(CYL(tx,ty,1.2,tbb,tbb+6,'#5D4037','Tree','Trees',ftree),'Trees');
      add(CONE(tx,ty,6,tbb+6,tbb+18,'#2E7D32','Leaves','Trees',false),'Trees');
      ftree=false;
    }}
  }}

  const layout={{
    scene:{{
      xaxis:{{title:'Length',showgrid:true,backgroundcolor:'#EAF4FB'}},
      yaxis:{{title:'Width',showgrid:true,backgroundcolor:'#EAF4FB'}},
      zaxis:{{title:'Height',range:[-2,40]}},
      aspectmode:'data',
      camera:{{eye:{{x:1.3,y:-1.5,z:.85}}}}
    }},
    paper_bgcolor:'#EAF4FB',margin:{{l:0,r:0,t:65,b:0}},autosize:true
  }};

  figData={{traces,layout}};
  Plotly.newPlot('plot',traces,layout,{{responsive:true}});
}}

function toggleLG(btn){{
  const lg=btn.dataset.lg;
  const nowHidden=lgVis[lg]===false;
  lgVis[lg]=nowHidden?true:false;
  Plotly.restyle('plot',{{visible:nowHidden?true:'legendonly'}},lgMap[lg]);
  btn.classList.toggle('off',!nowHidden);
}}

function setCam(ex,ey,ez){{
  Plotly.relayout('plot',{{'scene.camera.eye':{{x:ex,y:ey,z:ez}}}});
}}

function downloadMap(){{
  const htmlContent=`<html><body><div id="p"></div><script src="https://cdn.plot.ly/plotly-2.27.0.min.js"><\/script><script>Plotly.newPlot('p',${{JSON.stringify(figData.traces)}},${{JSON.stringify(figData.layout)}});<\/script></body></html>`;
  const blob=new Blob([htmlContent],{{type:'text/html'}});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='homestead_map.html';a.click();
}}

window.addEventListener('load',()=>setTimeout(generateMap,300));
</script>
</body>
</html>
        """
        st.components.v1.html(html_template, height=800)
```
