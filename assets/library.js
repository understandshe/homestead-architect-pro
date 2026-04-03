import * as THREE from "three";
import { RGBELoader } from "three/examples/jsm/loaders/RGBELoader.js";

/* ========= SCENE SETUP ========= */
const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(
  60,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
camera.position.set(20, 15, 20);
camera.lookAt(0, 0, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

/* ========= REALISTIC RENDER ========= */
renderer.physicallyCorrectLights = true;
renderer.outputEncoding = THREE.sRGBEncoding;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;

renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

/* ========= LIGHT ========= */
const sun = new THREE.DirectionalLight(0xffffff, 1.5);
sun.position.set(50, 80, 30);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
scene.add(sun);

const ambient = new THREE.AmbientLight(0xffffff, 0.3);
scene.add(ambient);

/* ========= HDRI ========= */
new RGBELoader().load("hdri.hdr", (hdr) => {
  hdr.mapping = THREE.EquirectangularReflectionMapping;
  scene.environment = hdr;
  scene.background = hdr;
});

/* ========= GROUND ========= */
const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(200, 200, 50, 50),
  new THREE.MeshStandardMaterial({ color: 0x6e7f4f, roughness: 1 })
);
ground.rotation.x = -Math.PI / 2;
ground.receiveShadow = true;
scene.add(ground);

/* ========= HELPERS ========= */
const mat = (c, o = {}) =>
  new THREE.MeshStandardMaterial({ color: c, roughness: 0.7, metalness: 0.2, ...o });

const place = (g, x, y, z, s) => {
  g.position.set(x, y, z);
  g.scale.setScalar(s);
  return g;
};

/* ========= FARMHOUSE ========= */
const createFarmhouse = (x, y, z, s = 1) => {
  const g = new THREE.Group();

  const base = new THREE.Mesh(
    new THREE.BoxGeometry(4, 2, 4),
    mat(0xb07d52)
  );
  base.position.y = 1;
  base.castShadow = true;

  const roof = new THREE.Mesh(
    new THREE.ConeGeometry(3, 2, 4),
    mat(0x5a2d0c)
  );
  roof.position.y = 3;
  roof.rotation.y = Math.PI / 4;

  g.add(base, roof);
  return place(g, x, y, z, s);
};

/* ========= TREE ========= */
const createTree = (x, y, z, s = 1) => {
  const g = new THREE.Group();

  const trunk = new THREE.Mesh(
    new THREE.CylinderGeometry(0.3, 0.4, 1.5, 10),
    mat(0x6b4423)
  );
  trunk.position.y = 0.75;

  const leaves = new THREE.Mesh(
    new THREE.SphereGeometry(1.2, 12, 12),
    mat(0x2e7d32)
  );
  leaves.position.y = 2;

  g.add(trunk, leaves);
  return place(g, x, y, z, s);
};

/* ========= WATER ========= */
const createWater = (x, z) => {
  const geo = new THREE.CircleGeometry(5, 32);

  const matWater = new THREE.MeshStandardMaterial({
    color: 0x336699,
    transparent: true,
    opacity: 0.7,
    roughness: 0.2,
    metalness: 0.8,
  });

  const water = new THREE.Mesh(geo, matWater);
  water.rotation.x = -Math.PI / 2;
  water.position.set(x, 0.05, z);

  water.tick = (t) => {
    water.material.opacity = 0.65 + Math.sin(t * 0.001) * 0.05;
  };

  return water;
};

/* ========= FISH ========= */
const createFish = (x, y, z, s = 1) => {
  const g = new THREE.Group();

  const body = new THREE.Mesh(
    new THREE.SphereGeometry(0.5, 16, 16),
    mat(0x7f8c8d, { metalness: 0.5 })
  );
  body.scale.set(2, 0.8, 0.8);
  body.position.y = 0.4;

  const tail = new THREE.Mesh(
    new THREE.PlaneGeometry(0.8, 0.6),
    mat(0x5d6d7e, { side: THREE.DoubleSide })
  );
  tail.position.set(-1.2, 0.4, 0);
  tail.rotation.y = Math.PI / 2;

  g.add(body, tail);

  g.tick = (t) => {
    const time = t * 0.001;
    g.position.x += Math.sin(time) * 0.003;
    g.position.z += Math.cos(time) * 0.003;
    tail.rotation.y = Math.sin(time * 5) * 0.6;
  };

  return place(g, x, y, z, s);
};

/* ========= GRASS ========= */
const createGrassField = (count = 1500) => {
  const g = new THREE.Group();

  const geo = new THREE.PlaneGeometry(0.1, 0.5);
  const m = mat(0x3a5f2a, { side: THREE.DoubleSide });

  for (let i = 0; i < count; i++) {
    const blade = new THREE.Mesh(geo, m);

    blade.position.set(
      (Math.random() - 0.5) * 100,
      0.25,
      (Math.random() - 0.5) * 100
    );

    blade.rotation.y = Math.random() * Math.PI;
    blade.scale.y = 0.5 + Math.random();

    g.add(blade);
  }

  return g;
};

/* ========= FENCE ========= */
const createFence = (points = [], h = 1.2) => {
  const g = new THREE.Group();

  for (let i = 0; i < points.length; i++) {
    const p1 = points[i];
    const p2 = points[(i + 1) % points.length];

    const dx = p2.x - p1.x;
    const dz = p2.z - p1.z;
    const len = Math.sqrt(dx * dx + dz * dz);

    const post = new THREE.Mesh(
      new THREE.CylinderGeometry(0.1, 0.12, h, 10),
      mat(0x5c3b1e)
    );
    post.position.set(p1.x, h / 2, p1.z);

    const rail = new THREE.Mesh(
      new THREE.BoxGeometry(len, 0.08, 0.08),
      mat(0x7a5230)
    );
    rail.position.set(p1.x + dx / 2, h * 0.6, p1.z + dz / 2);
    rail.rotation.y = Math.atan2(dz, dx);

    g.add(post, rail);
  }

  return g;
};

/* ========= ADD OBJECTS ========= */
scene.add(createFarmhouse(0, 0, 0));
scene.add(createTree(5, 0, 5));
scene.add(createTree(-5, 0, -3));

const pond = createWater(10, 0);
scene.add(pond);

scene.add(createFish(10, 0, 0));
scene.add(createGrassField());

scene.add(createFence([
  { x: -10, z: -10 },
  { x: 10, z: -10 },
  { x: 10, z: 10 },
  { x: -10, z: 10 },
]));

/* ========= FOG ========= */
scene.fog = new THREE.Fog(0xcce0ff, 50, 200);

/* ========= UPDATE ========= */
const updateAssets = (scene, time) => {
  scene.traverse((o) => {
    if (o.tick) o.tick(time);
  });
};

/* ========= LOOP ========= */
const animate = (t) => {
  requestAnimationFrame(animate);
  updateAssets(scene, t);
  renderer.render(scene, camera);
};
animate();
