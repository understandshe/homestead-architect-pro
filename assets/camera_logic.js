/**
 * Homestead Architect Pro 2026 - Global Edition
 * Module: Smooth Cinematic Camera & Orbit Controls
 * Responsibility: Handle auto-rotation and manual user interaction
 */

import { OrbitControls } from 'https://unpkg.com/three@0.128.0/examples/jsm/controls/OrbitControls.js';

// Global variables for camera management
let controls;
let autoRotate = true;
const rotationSpeed = 0.0002;
const cameraRadius = 60;
const cameraHeight = 35;

/**
 * Initialize Camera Controls
 * @param {THREE.Camera} camera 
 * @param {HTMLElement} rendererElement 
 */
export function initCameraControls(camera, rendererElement) {
    controls = new OrbitControls(camera, rendererElement);
    
    // Enable smooth damping (inertia)
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    
    // Limit vertical rotation to stay above ground
    controls.maxPolarAngle = Math.PI / 2.1;

    // Disable auto-rotation when user starts interacting
    controls.addEventListener('start', () => {
        autoRotate = false;
    });

    return controls;
}

/**
 * Update Camera Position in Animation Loop
 * @param {THREE.Camera} camera 
 * @param {number} time 
 */
export function updateCameraView(camera, time) {
    if (autoRotate) {
        // Cinematic Orbit Logic
        camera.position.x = Math.sin(time * rotationSpeed) * cameraRadius;
        camera.position.z = Math.cos(time * rotationSpeed) * cameraRadius;
        camera.position.y = cameraHeight;
        camera.lookAt(0, 0, 0);
    }
    
    if (controls) {
        controls.update();
    }
}
