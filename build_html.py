import json

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Munsell Color Solid</title>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background-color: #222;
            color: #fff;
            font-family: sans-serif;
        }
        #info-panel {
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(0, 0, 0, 0.7);
            padding: 15px;
            border-radius: 8px;
            pointer-events: none;
            display: none;
            z-index: 10;
        }
        #controls {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.7);
            padding: 15px;
            border-radius: 8px;
            z-index: 10;
        }
        #color-box {
            width: 40px;
            height: 40px;
            border: 1px solid #fff;
            margin-top: 10px;
        }
        select, button {
            background: #444;
            color: #fff;
            border: 1px solid #666;
            padding: 5px;
            margin-top: 5px;
            width: 100%;
        }
    </style>
    <script type="importmap">
        {
            "imports": {
                "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
                "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
            }
        }
    </script>
</head>
<body>
    <div id="info-panel">
        <h3 style="margin-top: 0">Munsell Color</h3>
        <div><strong>Hue:</strong> <span id="info-hue"></span></div>
        <div><strong>Value:</strong> <span id="info-value"></span></div>
        <div><strong>Chroma:</strong> <span id="info-chroma"></span></div>
        <div id="color-box"></div>
    </div>
    <div id="controls">
        <h3 style="margin-top: 0">Controls</h3>
        <label>Slice Mode:</label>
        <select id="slice-mode">
            <option value="none">Full Solid</option>
            <option value="value">Value Slice (Horizontal)</option>
            <option value="hue">Hue Wedge (Vertical)</option>
        </select>
        
        <div id="value-slider-container" style="display: none; margin-top: 10px;">
            <label>Value: <span id="value-label">5</span></label>
            <input type="range" id="value-slider" min="1" max="10" step="1" value="5" style="width: 100%">
        </div>
        
        <div id="hue-slider-container" style="display: none; margin-top: 10px;">
            <label>Hue: <span id="hue-label">5R</span></label>
            <input type="range" id="hue-slider" min="0" max="39" step="1" value="0" style="width: 100%">
        </div>
    </div>

    <script type="module">
        import * as THREE from 'three';
        import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

        // CSV DATA INJECTED HERE
        const csvData = `{{CSV_DATA}}`;

        const hues = [
            '2.5R', '5R', '7.5R', '10R', 
            '2.5YR', '5YR', '7.5YR', '10YR', 
            '2.5Y', '5Y', '7.5Y', '10Y', 
            '2.5GY', '5GY', '7.5GY', '10GY', 
            '2.5G', '5G', '7.5G', '10G', 
            '2.5BG', '5BG', '7.5BG', '10BG', 
            '2.5B', '5B', '7.5B', '10B', 
            '2.5PB', '5PB', '7.5PB', '10PB', 
            '2.5P', '5P', '7.5P', '10P', 
            '2.5RP', '5RP', '7.5RP', '10RP'
        ];

        function xyY_to_sRGB(x, y, Y) {
            // If completely dark or Y is 0 (though V=1 min in this dataset)
            if (y === 0 || Y === 0) return [0,0,0];
            
            // 1. xyY to XYZ (Illuminant C)
            const X = (x * Y) / y;
            const Z = ((1 - x - y) * Y) / y;

            // 2. Bradford adaptation from Illuminant C to D65
            const M_adapt = [
                [ 0.97224054, -0.0072489 , -0.00810646],
                [-0.01209482,  0.99671245, -0.00185945],
                [-0.0027434 ,  0.00531596,  0.92110922]
            ];
            
            const X_d65 = M_adapt[0][0]*X + M_adapt[0][1]*Y + M_adapt[0][2]*Z;
            const Y_d65 = M_adapt[1][0]*X + M_adapt[1][1]*Y + M_adapt[1][2]*Z;
            const Z_d65 = M_adapt[2][0]*X + M_adapt[2][1]*Y + M_adapt[2][2]*Z;

            // 3. XYZ (D65) to linear sRGB
            // sRGB matrix
            const r_l =  3.2404542 * X_d65 - 1.5371385 * Y_d65 - 0.4985314 * Z_d65;
            const g_l = -0.9692660 * X_d65 + 1.8760108 * Y_d65 + 0.0415560 * Z_d65;
            const b_l =  0.0556434 * X_d65 - 0.2040259 * Y_d65 + 1.0572252 * Z_d65;

            // 4. Linear sRGB to sRGB (gamma 2.4 / 1/2.4 approx)
            function gamma(v) {
                // scale is 0 to 100 for Y in Munsell typically, need to divide by 100
                v = v / 100.0;
                if (v <= 0) return 0;
                if (v >= 1) return 1;
                return v <= 0.0031308 ? 12.92 * v : 1.055 * Math.pow(v, 1.0 / 2.4) - 0.055;
            }

            let r = gamma(r_l);
            let g = gamma(g_l);
            let b = gamma(b_l);

            return [
                Math.max(0, Math.min(255, Math.round(r * 255))),
                Math.max(0, Math.min(255, Math.round(g * 255))),
                Math.max(0, Math.min(255, Math.round(b * 255)))
            ];
        }

        // Parse CSV
        const lines = csvData.trim().split('\\n');
        const munsellColors = [];
        
        for (let i = 1; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line) continue;
            const parts = line.split(',');
            if (parts.length < 6) continue;
            
            const H = parts[0];
            const V = parseFloat(parts[1]);
            const C = parseFloat(parts[2]);
            const x = parseFloat(parts[3]);
            const y = parseFloat(parts[4]);
            const Y_val = parseFloat(parts[5]);
            
            const rgb = xyY_to_sRGB(x, y, Y_val);
            const hueIndex = hues.indexOf(H);
            
            if (hueIndex !== -1 || C === 0) { // Neutral colors have 0 chroma, H might be anything but usually listed under all or specific
                munsellColors.push({
                    H: H,
                    V: V,
                    C: C,
                    rgb: rgb,
                    hueIndex: hueIndex
                });
            }
        }

        const boundaryValues = Array.from(new Set(
            munsellColors
                .filter(color => color.C > 0 && color.V > 0 && color.V < 10 && color.hueIndex !== -1)
                .map(color => color.V)
        )).sort((a, b) => a - b);

        const maxChromaByHue = Array.from({ length: hues.length }, () => []);
        munsellColors.forEach(color => {
            if (color.C <= 0 || color.hueIndex === -1 || color.V <= 0 || color.V >= 10) return;
            const samples = maxChromaByHue[color.hueIndex];
            const existing = samples.find(sample => sample.V === color.V);
            if (existing) {
                existing.C = Math.max(existing.C, color.C);
            } else {
                samples.push({ V: color.V, C: color.C });
            }
        });
        maxChromaByHue.forEach(samples => samples.sort((a, b) => a.V - b.V));

        function boundaryChroma(hueIndex, value) {
            const samples = maxChromaByHue[hueIndex];
            if (!samples.length) return 0;
            if (value <= samples[0].V) return samples[0].C;
            if (value >= samples[samples.length - 1].V) return samples[samples.length - 1].C;
            for (let i = 0; i < samples.length - 1; i++) {
                const lower = samples[i];
                const upper = samples[i + 1];
                if (value >= lower.V && value <= upper.V) {
                    const t = (value - lower.V) / (upper.V - lower.V);
                    return lower.C + (upper.C - lower.C) * t;
                }
            }
            return samples[samples.length - 1].C;
        }

        // Three.js setup
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x333333);
        
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(40, 30, 40);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        document.body.appendChild(renderer.domElement);

        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.target.set(0, 15, 0);

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);
        
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(10, 20, 10);
        scene.add(dirLight);
        
        const dirLight2 = new THREE.DirectionalLight(0xffffff, 0.4);
        dirLight2.position.set(-10, 10, -10);
        scene.add(dirLight2);

        // Group to hold all cubes
        const solidGroup = new THREE.Group();
        scene.add(solidGroup);

        const shellGeometry = new THREE.BufferGeometry();
        const shellPositions = [];
        const shellIndices = [];
        const ringVertexIndices = [];
        const hueCount = hues.length;
        const bottomCenterIndex = 0;
        const topCenterIndex = 1;
        shellPositions.push(0, 0, 0);
        shellPositions.push(0, 30, 0);

        boundaryValues.forEach(value => {
            const ring = [];
            for (let hueIdx = 0; hueIdx < hueCount; hueIdx++) {
                const angle = (hueIdx / hueCount) * Math.PI * 2;
                const radius = boundaryChroma(hueIdx, value) * 1.5;
                const xPos = Math.cos(angle) * radius;
                const yPos = value * 3;
                const zPos = -Math.sin(angle) * radius;
                ring.push(shellPositions.length / 3);
                shellPositions.push(xPos, yPos, zPos);
            }
            ringVertexIndices.push(ring);
        });

        if (ringVertexIndices.length > 0) {
            const firstRing = ringVertexIndices[0];
            const lastRing = ringVertexIndices[ringVertexIndices.length - 1];
            for (let hueIdx = 0; hueIdx < hueCount; hueIdx++) {
                const nextHueIdx = (hueIdx + 1) % hueCount;
                shellIndices.push(bottomCenterIndex, firstRing[hueIdx], firstRing[nextHueIdx]);
                shellIndices.push(topCenterIndex, lastRing[nextHueIdx], lastRing[hueIdx]);
            }
            for (let valueIdx = 0; valueIdx < ringVertexIndices.length - 1; valueIdx++) {
                const lowerRing = ringVertexIndices[valueIdx];
                const upperRing = ringVertexIndices[valueIdx + 1];
                for (let hueIdx = 0; hueIdx < hueCount; hueIdx++) {
                    const nextHueIdx = (hueIdx + 1) % hueCount;
                    const a = lowerRing[hueIdx];
                    const b = lowerRing[nextHueIdx];
                    const c = upperRing[hueIdx];
                    const d = upperRing[nextHueIdx];
                    shellIndices.push(a, c, b);
                    shellIndices.push(b, c, d);
                }
            }
            shellGeometry.setAttribute('position', new THREE.Float32BufferAttribute(shellPositions, 3));
            shellGeometry.setIndex(shellIndices);
            shellGeometry.computeVertexNormals();

            const shellMaterial = new THREE.MeshStandardMaterial({
                color: 0xe8e8e8,
                transparent: true,
                opacity: 0.08,
                roughness: 1.0,
                metalness: 0.0,
                side: THREE.DoubleSide,
                depthWrite: false
            });

            const shellMesh = new THREE.Mesh(shellGeometry, shellMaterial);
            shellMesh.renderOrder = -1;
            solidGroup.add(shellMesh);
        }

        // Geometry & Material
        const boxGeometry = new THREE.BoxGeometry(1.4, 2.8, 1.4);
        
        const cubes = [];

        munsellColors.forEach(color => {
            // Mapping to 3D space
            // Height = Value
            const yPos = color.V * 3;
            
            // For neutral colors (C=0), place in center.
            // If they are duplicated for each hue in CSV, we only need to add it once. 
            // Wait, we can just add them all, but let's place neutral exactly at center.
            let xPos = 0;
            let zPos = 0;
            let hIndex = color.hueIndex;
            
            if (color.C > 0 && hIndex !== -1) {
                const angle = (hIndex / 40.0) * Math.PI * 2;
                // Radius = Chroma
                const radius = color.C * 1.5;
                xPos = Math.cos(angle) * radius;
                zPos = -Math.sin(angle) * radius; // negative so hues go around correctly depending on coordinate system
            }
            
            const material = new THREE.MeshStandardMaterial({
                color: new THREE.Color(`rgb(${color.rgb[0]}, ${color.rgb[1]}, ${color.rgb[2]})`),
                roughness: 0.8,
                metalness: 0.1
            });
            
            const mesh = new THREE.Mesh(boxGeometry, material);
            mesh.position.set(xPos, yPos, zPos);
            
            // Add custom data for raycasting
            mesh.userData = {
                H: color.C === 0 ? 'N' : color.H,
                V: color.V,
                C: color.C,
                rgb: color.rgb,
                hueIndex: hIndex
            };
            
            // Align cubes so they face the center?
            // Optional: rotate cubes so their sides align with radius
            if (color.C > 0 && hIndex !== -1) {
                mesh.rotation.y = (hIndex / 40.0) * Math.PI * 2;
            }
            
            cubes.push(mesh);
            solidGroup.add(mesh);
        });

        // Center solid
        solidGroup.position.y = -15;

        // Raycasting for hover info
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        const infoPanel = document.getElementById('info-panel');
        const infoHue = document.getElementById('info-hue');
        const infoValue = document.getElementById('info-value');
        const infoChroma = document.getElementById('info-chroma');
        const colorBox = document.getElementById('color-box');
        
        let hoveredMesh = null;
        let originalEmissive = new THREE.Color(0x000000);

        window.addEventListener('mousemove', (event) => {
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
            
            // Update info panel position
            infoPanel.style.left = (event.clientX + 15) + 'px';
            infoPanel.style.top = (event.clientY + 15) + 'px';
        });

        // UI Controls
        const sliceModeSelect = document.getElementById('slice-mode');
        const valueSliderContainer = document.getElementById('value-slider-container');
        const hueSliderContainer = document.getElementById('hue-slider-container');
        const valueSlider = document.getElementById('value-slider');
        const hueSlider = document.getElementById('hue-slider');
        const valueLabel = document.getElementById('value-label');
        const hueLabel = document.getElementById('hue-label');

        function updateVisibility() {
            const mode = sliceModeSelect.value;
            const valLevel = parseInt(valueSlider.value);
            const hueIdx = parseInt(hueSlider.value);
            
            cubes.forEach(cube => {
                let visible = true;
                if (mode === 'value') {
                    if (cube.userData.V !== valLevel) visible = false;
                } else if (mode === 'hue') {
                    // Show neutral axis + one hue wedge
                    if (cube.userData.C !== 0 && cube.userData.hueIndex !== hueIdx) visible = false;
                }
                cube.visible = visible;
            });
        }

        sliceModeSelect.addEventListener('change', () => {
            const mode = sliceModeSelect.value;
            valueSliderContainer.style.display = mode === 'value' ? 'block' : 'none';
            hueSliderContainer.style.display = mode === 'hue' ? 'block' : 'none';
            updateVisibility();
        });

        valueSlider.addEventListener('input', () => {
            valueLabel.innerText = valueSlider.value;
            updateVisibility();
        });

        hueSlider.addEventListener('input', () => {
            hueLabel.innerText = hues[hueSlider.value];
            updateVisibility();
        });

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            
            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(solidGroup.children).filter(i => i.object.visible);
            
            if (intersects.length > 0) {
                const object = intersects[0].object;
                if (hoveredMesh !== object) {
                    if (hoveredMesh) hoveredMesh.material.emissive.copy(originalEmissive);
                    hoveredMesh = object;
                    originalEmissive.copy(hoveredMesh.material.emissive);
                    hoveredMesh.material.emissive.setHex(0x555555); // Highlight
                    
                    infoPanel.style.display = 'block';
                    infoHue.innerText = object.userData.H;
                    infoValue.innerText = object.userData.V;
                    infoChroma.innerText = object.userData.C;
                    colorBox.style.backgroundColor = `rgb(${object.userData.rgb[0]}, ${object.userData.rgb[1]}, ${object.userData.rgb[2]})`;
                }
            } else {
                if (hoveredMesh) {
                    hoveredMesh.material.emissive.copy(originalEmissive);
                    hoveredMesh = null;
                    infoPanel.style.display = 'none';
                }
            }
            
            renderer.render(scene, camera);
        }

        animate();
    </script>
</body>
</html>
"""

with open('munsell_3-3.csv', 'r') as f:
    csv_data = f.read()

final_html = html_template.replace('{{CSV_DATA}}', csv_data)

with open('munsell_solid.html', 'w') as f:
    f.write(final_html)

print("Generated munsell_solid.html successfully.")
