import * as THREE from "three";

/* ========= HELPERS ========= */
const mat = (c, o = {}) => new THREE.MeshStandardMaterial({
  color: c,
  roughness: 0.7,
  metalness: 0.2,
  ...o
});

const box = (w,h,d,c)=> new THREE.Mesh(new THREE.BoxGeometry(w,h,d), mat(c));
const cyl = (r1,r2,h,c)=> new THREE.Mesh(new THREE.CylinderGeometry(r1,r2,h,12), mat(c));
const sph = (r,c)=> new THREE.Mesh(new THREE.SphereGeometry(r,12,12), mat(c));
const cone = (r,h,c)=> new THREE.Mesh(new THREE.ConeGeometry(r,h,8), mat(c));

const place = (g,x,y,z,s)=>{g.position.set(x,y,z);g.scale.setScalar(s);return g;};

/* ========= MAIN STRUCTURES ========= */
const createFarmhouse_A=(x,y,z,s=1)=>{const g=new THREE.Group();
const b=box(4,2,4,0xb07d52);b.position.y=1;
const r=cone(3,2,0x5a2d0c);r.position.y=3;
g.add(b,r);return place(g,x,y,z,s);};

const createFarmhouse_B=(x,y,z,s=1)=>{const g=new THREE.Group();
const a=box(6,3,4,0xa0522d);a.position.y=1.5;
const b=box(4,3,6,0xa0522d);b.position.set(-3,1.5,3);
g.add(a,b);return place(g,x,y,z,s);};

const createBarn_Large=(x,y,z,s=1)=>{const g=new THREE.Group();
const b=box(8,4,6,0x8b0000);b.position.y=2;
g.add(b);return place(g,x,y,z,s);};

const createWorkshop_Shed=(x,y,z,s=1)=>{const g=new THREE.Group();
const b=box(3,2,3,0x555555);b.position.y=1;
g.add(b);return place(g,x,y,z,s);};

const createGreenhouse_Glass=(x,y,z,s=1)=>{const g=new THREE.Group();
const m=new THREE.Mesh(new THREE.BoxGeometry(5,2.5,3),
mat(0x99ccff,{transparent:true,opacity:0.4}));
m.position.y=1.25;g.add(m);return place(g,x,y,z,s);};

const createGeodesic_Dome=(x,y,z,s=1)=>{const g=new THREE.Group();
const d=new THREE.Mesh(new THREE.SphereGeometry(2.5,8,8),
mat(0x88ccaa,{wireframe:true}));
d.position.y=2.5;g.add(d);return place(g,x,y,z,s);};

const createGuest_Cottage=(x,y,z,s=1)=>createFarmhouse_A(x,y,z,s*0.8);

const createGarage_Carport=(x,y,z,s=1)=>{const g=new THREE.Group();
const r=box(6,0.4,4,0x444444);r.position.y=2;
g.add(r);return place(g,x,y,z,s);};

/* ========= LIVESTOCK ========= */
const createChicken_Coop=(x,y,z,s=1)=>{const g=new THREE.Group();
const c=box(2,1.5,2,0x8b4513);c.position.y=0.75;g.add(c);
return place(g,x,y,z,s);};

const createChicken_Model=(x,y,z,s=1)=>{const g=new THREE.Group();
const b=sph(0.3,0xffffff);b.position.y=0.3;g.add(b);
g.tick=(t)=>g.position.x+=Math.sin(t*0.001)*0.002;
return place(g,x,y,z,s);};

const createGoat_Pen=(x,y,z,s=1)=>{const g=new THREE.Group();
for(let i=0;i<5;i++){const p=box(0.1,1,0.1,0x8b5a2b);
p.position.set(i,0.5,0);g.add(p);}
return place(g,x,y,z,s);};

const createGoat_Model=(x,y,z,s=1)=>{const g=new THREE.Group();
const b=box(0.8,0.5,0.4,0xdddddd);b.position.y=0.25;g.add(b);
g.tick=(t)=>g.rotation.y=Math.sin(t*0.001)*0.5;
return place(g,x,y,z,s);};

const createCow_Paddock=(x,y,z,s=1)=>createGoat_Pen(x,y,z,s*2);

const createBeehives_Row=(x,y,z,s=1)=>{const g=new THREE.Group();
for(let i=0;i<4;i++){const h=box(0.6,0.6,0.6,0xffcc00);
h.position.set(i,0.3,0);g.add(h);}
g.tick=(t)=>g.children.forEach((h,i)=>h.position.y=0.3+Math.sin(t*0.005+i)*0.05);
return place(g,x,y,z,s);};

const createDuck_House=(x,y,z,s=1)=>createChicken_Coop(x,y,z,s*0.8);
const createPig_Sty=(x,y,z,s=1)=>createGoat_Pen(x,y,z,s*1.2);

const createRabbit_Hutch=(x,y,z,s=1)=>{const g=new THREE.Group();
const c=box(2,1,1,0xaaaaaa);c.position.y=0.5;g.add(c);
return place(g,x,y,z,s);};

/* ========= AGRICULTURE ========= */
const createRaised_Bed_Rect=(x,y,z,s=1)=>{const g=new THREE.Group();
const soil=box(4,0.3,2,0x654321);soil.position.y=0.15;g.add(soil);
return place(g,x,y,z,s);};

const createRaised_Bed_L=(x,y,z,s=1)=>{const g=new THREE.Group();
g.add(createRaised_Bed_Rect(0,0,0,1));
g.add(createRaised_Bed_Rect(2,0,2,1));
return place(g,x,y,z,s);};

const createOrchard_Apple=(x,y,z,s=1)=>{const g=new THREE.Group();
const t=cyl(0.2,0.2,1,0x8b5a2b);t.position.y=0.5;
const l=sph(1,0x2e7d32);l.position.y=1.5;
g.add(t,l);return place(g,x,y,z,s);};

const createOrchard_Citrus=(x,y,z,s=1)=>createOrchard_Apple(x,y,z,s);

const createVineyard_Trellis=(x,y,z,s=1)=>createGoat_Pen(x,y,z,s);

const createHerb_Spiral=(x,y,z,s=1)=>{const g=new THREE.Group();
for(let i=0;i<6;i++){const s1=cyl(0.5-i*0.05,0.5-i*0.05,0.2,0x777);
s1.position.y=i*0.1;g.add(s1);}return place(g,x,y,z,s);};

const createCompost_Bin_Triple=(x,y,z,s=1)=>{const g=new THREE.Group();
for(let i=0;i<3;i++){const b=box(1,1,1,0x5a3d1a);
b.position.set(i*1.2,0.5,0);g.add(b);}
return place(g,x,y,z,s);};

const createMushroom_Log=(x,y,z,s=1)=>{const g=new THREE.Group();
const l=cyl(0.3,0.3,2,0x6b4423);l.rotation.z=Math.PI/2;l.position.y=0.3;
g.add(l);return place(g,x,y,z,s);};

const createBerry_Patch=(x,y,z,s=1)=>{const g=new THREE.Group();
for(let i=0;i<6;i++){const b=sph(0.4,0x064);
b.position.set(i*0.8,0.4,0);g.add(b);}
return place(g,x,y,z,s);};

/* ========= WATER & ENERGY ========= */
const createPond_Natural=(x,y,z,s=1)=>{const g=new THREE.Group();
const w=cyl(3,3,0.2,0x336699);w.position.y=0.1;
g.add(w);return place(g,x,y,z,s);};

const createWater_Tank_Black=(x,y,z,s=1)=>{const g=new THREE.Group();
const t=cyl(1.5,1.5,3,0x111111);t.position.y=1.5;
g.add(t);return place(g,x,y,z,s);};

const createSolar_Panel_Roof=(x,y,z,s=1)=>{const g=new THREE.Group();
const p=box(3,0.1,2,0x0000ff);p.rotation.x=-0.5;p.position.y=2;
g.add(p);return place(g,x,y,z,s);};

const createSolar_Array_Ground=(x,y,z,s=1)=>{const g=new THREE.Group();
for(let i=0;i<3;i++){const p=box(2,0.1,1,0x0000ff);
p.position.set(i*2.2,1,0);p.rotation.x=-0.5;g.add(p);}
return place(g,x,y,z,s);};

const createWind_Turbine=(x,y,z,s=1)=>{const g=new THREE.Group();
const p=cyl(0.1,0.1,5,0xffffff);p.position.y=2.5;
const b=box(0.1,2,0.2,0xddd);b.position.y=5;
g.add(p,b);
g.tick=(t)=>b.rotation.z=t*0.005;
return place(g,x,y,z,s);};

const createWater_Well=(x,y,z,s=1)=>{const g=new THREE.Group();
const w=cyl(1,1,1,0x888888);w.position.y=0.5;
g.add(w);return place(g,x,y,z,s);};

const createGraywater_System=(x,y,z,s=1)=>{const g=new THREE.Group();
const p=cyl(0.2,0.2,3,0x999999);p.rotation.z=Math.PI/2;p.position.y=0.5;
g.add(p);return place(g,x,y,z,s);};

/* ========= LANDSCAPING ========= */
const createFence_Wood=(x,y,z,s=1)=>{const g=new THREE.Group();
for(let i=0;i<5;i++){const p=box(0.1,1,0.1,0x8b5a2b);
p.position.set(i,0.5,0);g.add(p);}
return place(g,x,y,z,s);};

const createFence_Wire=(x,y,z,s=1)=>createFence_Wood(x,y,z,s);

const createGate_Main=(x,y,z,s=1)=>{const g=new THREE.Group();
const g1=box(3,2,0.2,0x654321);g1.position.y=1;g.add(g1);
return place(g,x,y,z,s);};

const createWindbreak_Pine=(x,y,z,s=1)=>{const g=new THREE.Group();
const t=cyl(0.2,0.2,2,0x6b4423);t.position.y=1;
const l=cone(1.2,3,0x0b6623);l.position.y=3;
g.add(t,l);return place(g,x,y,z,s);};

const createGravel_Path_Straight=(x,y,z,s=1)=>{const g=new THREE.Group();
const p=box(6,0.1,1,0xaaaaaa);p.position.y=0.05;
g.add(p);return place(g,x,y,z,s);};

const createGravel_Path_Curved=(x,y,z,s=1)=>createGravel_Path_Straight(x,y,z,s);

const createStone_Wall=(x,y,z,s=1)=>{const g=new THREE.Group();
const w=box(5,1,0.5,0x888888);w.position.y=0.5;
g.add(w);return place(g,x,y,z,s);};

/* ========= UTILITY ========= */
const createFire_Pit=(x,y,z,s=1)=>{const g=new THREE.Group();
const p=cyl(1,1,0.5,0x444);p.position.y=0.25;
const f=cone(0.5,1,0xff6600);f.position.y=0.8;
g.add(p,f);
g.tick=(t)=>f.scale.y=1+Math.sin(t*0.01)*0.3;
return place(g,x,y,z,s);};

const createOutdoor_Kitchen=(x,y,z,s=1)=>{const g=new THREE.Group();
const b=box(3,1,1,0x777777);b.position.y=0.5;
g.add(b);return place(g,x,y,z,s);};

const createSeating_Bench=(x,y,z,s=1)=>{const g=new THREE.Group();
const s1=box(2,0.2,0.5,0x8b5a2b);s1.position.y=0.6;
g.add(s1);return place(g,x,y,z,s);};

const createHammock=(x,y,z,s=1)=>{const g=new THREE.Group();
const h=box(3,0.2,1,0xffaaaa);h.position.y=1;
g.add(h);return place(g,x,y,z,s);};

const createClothes_Line=(x,y,z,s=1)=>{const g=new THREE.Group();
const l=box(5,0.05,0.05,0x000);l.position.y=2;
g.add(l);
g.tick=(t)=>l.rotation.z=Math.sin(t*0.002)*0.1;
return place(g,x,y,z,s);};

const createWood_Pile=(x,y,z,s=1)=>{const g=new THREE.Group();
for(let i=0;i<5;i++){const l=cyl(0.2,0.2,2,0x6b4423);
l.rotation.z=Math.PI/2;l.position.set(0,0.2+i*0.25,i*0.2);g.add(l);}
return place(g,x,y,z,s);};

const createTool_Rack=(x,y,z,s=1)=>{const g=new THREE.Group();
const r=box(2,1,0.2,0x8b5a2b);r.position.y=0.5;
g.add(r);return place(g,x,y,z,s);};

/* ========= EXPORT ========= */
export {
createFarmhouse_A,createFarmhouse_B,createBarn_Large,createWorkshop_Shed,
createGreenhouse_Glass,createGeodesic_Dome,createGuest_Cottage,createGarage_Carport,
createChicken_Coop,createChicken_Model,createGoat_Pen,createGoat_Model,createCow_Paddock,
createBeehives_Row,createDuck_House,createPig_Sty,createRabbit_Hutch,
createRaised_Bed_Rect,createRaised_Bed_L,createOrchard_Apple,createOrchard_Citrus,
createVineyard_Trellis,createHerb_Spiral,createCompost_Bin_Triple,createMushroom_Log,
createBerry_Patch,createPond_Natural,createWater_Tank_Black,createSolar_Panel_Roof,
createSolar_Array_Ground,createWind_Turbine,createWater_Well,createGraywater_System,
createFence_Wood,createFence_Wire,createGate_Main,createWindbreak_Pine,
createGravel_Path_Straight,createGravel_Path_Curved,createStone_Wall,
createFire_Pit,createOutdoor_Kitchen,createSeating_Bench,createHammock,
createClothes_Line,createWood_Pile,createTool_Rack
};
