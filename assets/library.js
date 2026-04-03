import * as THREE from "three";

/* ========= HELPERS ========= */
const mat = (c, o = {}) => new THREE.MeshStandardMaterial({ color: c, ...o });
const box = (w,h,d,c)=> new THREE.Mesh(new THREE.BoxGeometry(w,h,d), mat(c));
const cyl = (r1,r2,h,c)=> new THREE.Mesh(new THREE.CylinderGeometry(r1,r2,h,10), mat(c));
const sph = (r,c)=> new THREE.Mesh(new THREE.SphereGeometry(r,10,10), mat(c));
const cone = (r,h,c)=> new THREE.Mesh(new THREE.ConeGeometry(r,h,6), mat(c));
const place = (g,x,y,z,s)=>{g.position.set(x,y,z);g.scale.setScalar(s);return g;};

/* ========= MAIN ========= */
const createFarmhouse_A=(x,y,z,s=1)=>{const g=new THREE.Group();
const b=box(4,2,4,0x8b5a2b);b.position.y=1;
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
const createChicken_Model=(x,y,z,s=1)=>{const g=new THREE.Group();
const b=sph(0.3,0xffffff);b.position.y=0.3;g.add(b);
g.tick=(t)=>g.position.x+=Math.sin(t*0.001)*0.002;
return place(g,x,y,z,s);};

const createGoat_Model=(x,y,z,s=1)=>{const g=new THREE.Group();
const b=box(0.8,0.5,0.4,0xdddddd);b.position.y=0.25;g.add(b);
g.tick=(t)=>g.rotation.y=Math.sin(t*0.001)*0.5;
return place(g,x,y,z,s);};

const createBeehives_Row=(x,y,z,s=1)=>{const g=new THREE.Group();
for(let i=0;i<4;i++){const h=box(0.6,0.6,0.6,0xffcc00);
h.position.set(i,0.3,0);g.add(h);}
g.tick=(t)=>g.children.forEach((h,i)=>h.position.y=0.3+Math.sin(t*0.005+i)*0.05);
return place(g,x,y,z,s);};

const createChicken_Coop=(x,y,z,s=1)=>{const g=new THREE.Group();
const c=box(2,1.5,2,0x8b4513);c.position.y=0.75;g.add(c);
return place(g,x,y,z,s);};

const createGoat_Pen=(x,y,z,s=1)=>{const g=new THREE.Group();
for(let i=0;i<5;i++){const p=box(0.1,1,0.1,0x8b5a2b);
p.position.set(i,0.5,0);g.add(p);}
return place(g,x,y,z,s);};

const createCow_Paddock=(x,y,z,s=1)=>createGoat_Pen(x,y,z,s*2);
const createDuck_House=(x,y,z,s=1)=>createChicken_Coop(x,y,z,s*0.8);
const createPig_Sty=(x,y,z,s=1)=>createGoat_Pen(x,y,z,s*1.2);

const createRabbit_Hutch=(x,y,z,s=1)=>{const g=new THREE.Group();
const c=box(2,1,1,0xaaaaaa);c.position.y=0.5;g.add(c);
return place(g,x,y,z,s);};

/* ========= AGRI ========= */
const createRaised_Bed_Rect=(x,y,z,s=1)=>{const g=new THREE.Group();
const soil=box(4,0.3,2,0x654321);soil.position.y=0.15;g.add(soil);
return place(g,x,y,z,s);};

const createRaised_Bed_L=(x,y,z,s=1)=>{const g=new THREE.Group();
g.add(createRaised_Bed_Rect(0,0,0,1));
g.add(createRaised_Bed_Rect(2,0,2,1));
return place(g,x,y,z,s);};

const createOrchard_Apple=(x,y,z,s=1)=>{const g=new THREE.Group();
const t=cyl(0.2,0.2,1,0x8b5a2b);t.position.y=0.5;
const l=sph(1,0x228b22);l.position.y=1.5;
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

/* ========= ENERGY ========= */
const createWind_Turbine=(x,y,z,s=1)=>{const g=new THREE.Group();
const p=cyl(0.1,0.1,5,0xffffff);p.position.y=2.5;
const b=box(0.1,2,0.2,0xddd);b.position.y=5;
g.add(p,b);
g.tick=(t)=>b.rotation.z=t*0.005;
return place(g,x,y,z,s);};

const createFire_Pit=(x,y,z,s=1)=>{const g=new THREE.Group();
const p=cyl(1,1,0.5,0x444);p.position.y=0.25;
const f=cone(0.5,1,0xff6600);f.position.y=0.8;
g.add(p,f);
g.tick=(t)=>f.scale.y=1+Math.sin(t*0.01)*0.3;
return place(g,x,y,z,s);};

const createClothes_Line=(x,y,z,s=1)=>{const g=new THREE.Group();
const l=box(5,0.05,0.05,0x000);l.position.y=2;g.add(l);
g.tick=(t)=>l.rotation.z=Math.sin(t*0.002)*0.1;
return place(g,x,y,z,s);};

/* ========= NEW: FISH ========= */
const createFish_Model = (x, y, z, s = 1) => {
  const g = new THREE.Group();

  const body = sph(0.4, 0xff8844);
  body.scale.set(1.5, 1, 0.6);
  body.position.y = 0.4;

  const tail = cone(0.3, 0.6, 0xff5522);
  tail.rotation.z = Math.PI / 2;
  tail.position.set(-0.7, 0.4, 0);

  g.add(body, tail);

  g.tick = (t) => {
    const time = t * 0.001;
    g.position.x += Math.sin(time) * 0.01;
    g.position.z += Math.cos(time) * 0.01;
    tail.rotation.y = Math.sin(time * 6) * 0.5;
    body.position.y = 0.4 + Math.sin(time * 2) * 0.05;
  };

  return place(g, x, y, z, s);
};

/* ========= NEW: DYNAMIC FENCE ========= */
const createDynamic_Fence = (points = [], height = 1, s = 1) => {
  const g = new THREE.Group();
  if (!points.length) return g;

  for (let i = 0; i < points.length; i++) {
    const p1 = points[i];
    const p2 = points[(i + 1) % points.length];

    const dx = p2.x - p1.x;
    const dz = p2.z - p1.z;
    const len = Math.sqrt(dx * dx + dz * dz);

    const rail = box(len, 0.1, 0.1, 0x8b5a2b);
    rail.position.set(p1.x + dx / 2, height * 0.7, p1.z + dz / 2);
    rail.rotation.y = Math.atan2(dz, dx);

    const post = box(0.15, height, 0.15, 0x5a3d1a);
    post.position.set(p1.x, height / 2, p1.z);

    g.add(rail, post);
  }

  g.scale.setScalar(s);
  return g;
};

/* ========= UPDATE LOOP ========= */
const updateAssets = (scene, time) => {
  scene.traverse((obj) => {
    if (obj.tick) obj.tick(time);
  });
};

/* ========= EXPORT ========= */
export {
createFarmhouse_A,createFarmhouse_B,createBarn_Large,createWorkshop_Shed,
createGreenhouse_Glass,createGeodesic_Dome,createGuest_Cottage,createGarage_Carport,
createChicken_Coop,createChicken_Model,createGoat_Pen,createGoat_Model,createCow_Paddock,
createBeehives_Row,createDuck_House,createPig_Sty,createRabbit_Hutch,
createRaised_Bed_Rect,createRaised_Bed_L,createOrchard_Apple,createOrchard_Citrus,
createVineyard_Trellis,createHerb_Spiral,createCompost_Bin_Triple,createMushroom_Log,
createBerry_Patch,createWind_Turbine,createFire_Pit,createClothes_Line,
createFish_Model,createDynamic_Fence,
updateAssets
};
