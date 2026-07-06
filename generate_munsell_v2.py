import json

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Munsell Color Solid with Pigments</title>
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
            background: rgba(0, 0, 0, 0.8);
            padding: 15px;
            border-radius: 8px;
            pointer-events: none;
            display: none;
            z-index: 10;
        }
        #pigment-info {
            color: #ffaa00;
            font-weight: bold;
            margin-bottom: 5px;
            display: none;
        }
        #controls {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.8);
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
        select, button, input {
            background: #444;
            color: #fff;
            border: 1px solid #666;
            padding: 5px;
            margin-top: 5px;
            width: 100%;
            box-sizing: border-box;
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
        <div id="pigment-info"></div>
        <div><strong>Hue:</strong> <span id="info-hue"></span></div>
        <div><strong>Value:</strong> <span id="info-value"></span></div>
        <div><strong>Chroma:</strong> <span id="info-chroma"></span></div>
        <div id="color-box"></div>
    </div>
    <div id="controls">
        <h3 style="margin-top: 0">Controls</h3>
        <label>View Mode:</label>
        <select id="view-mode">
            <option value="both">Voxels + Pigments</option>
            <option value="voxels">Voxels Only</option>
            <option value="pigments">Pigments Only</option>
        </select>
        
        <label style="margin-top: 10px; display: block;">Slice Mode:</label>
        <select id="slice-mode">
            <option value="none">Full Solid</option>
            <option value="value">Value Slice (Horizontal)</option>
            <option value="hue">Hue Wedge (Vertical)</option>
        </select>
        
        <div id="value-slider-container" style="display: none; margin-top: 10px;">
            <label>Value: <span id="value-label">5</span></label>
            <input type="range" id="value-slider" min="1" max="10" step="1" value="5">
        </div>
        
        <div id="hue-slider-container" style="display: none; margin-top: 10px;">
            <label>Hue: <span id="hue-label">5R</span></label>
            <input type="range" id="hue-slider" min="0" max="39" step="1" value="0">
        </div>
    </div>

    <script type="module">
        import * as THREE from 'three';
        import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

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

        const pigments = [
            { name: "Hansa Yellow (PY97)", hex: "#F5E03C" },
            { name: "Cadmium Yellow (PY35)", hex: "#FFDE00" },
            { name: "Cadmium Lemon (PY35)", hex: "#FFF166" },
            { name: "Bismuth Yellow (PY184)", hex: "#FFE97F" },
            { name: "Nickel Titanate (PY53)", hex: "#EAD98A" },
            { name: "Yellow Ochre (PY43)", hex: "#C89B3C" },
            { name: "Raw Sienna (PBr7)", hex: "#9A6324" },
            { name: "Cadmium Orange (PO20)", hex: "#FF7300" },
            { name: "Pyrrole Orange (PO73)", hex: "#FF5F1F" },
            { name: "Quinacridone Gold (PO49)", hex: "#C77B23" },
            { name: "Pyrrole Red (PR254)", hex: "#E8290B" },
            { name: "Cadmium Scarlet (PR108)", hex: "#E62020" },
            { name: "Naphthol Scarlet (PR188)", hex: "#D8261E" },
            { name: "Quinacridone Red (PR209)", hex: "#C0143C" },
            { name: "Cadmium Red Deep (PR108)", hex: "#B7211A" },
            { name: "Venetian Red (PR101)", hex: "#A6473A" },
            { name: "Burnt Sienna (PBr7)", hex: "#914E2B" },
            { name: "Burnt Umber (PBr7)", hex: "#5A3A29" },
            { name: "Raw Umber (PBr7)", hex: "#6B5B3E" },
            { name: "Perylene Maroon (PR179)", hex: "#5C1A1E" },
            { name: "Quinacridone Rose (PV19)", hex: "#C9184A" },
            { name: "Quinacridone Violet (PV19)", hex: "#8E2043" },
            { name: "Quinacridone Magenta (PR122)", hex: "#A31545" },
            { name: "Manganese Violet (PV16)", hex: "#6B3FA0" },
            { name: "Cobalt Violet (PV49)", hex: "#8B5FBF" },
            { name: "Dioxazine Violet (PV23)", hex: "#46246B" },
            { name: "Ultramarine Violet (PV15)", hex: "#4B2E83" },
            { name: "Phthalo Green YS (PG36)", hex: "#00785A" },
            { name: "Phthalo Green BS (PG7)", hex: "#00543C" },
            { name: "Viridian (PG18)", hex: "#40826D" },
            { name: "Cobalt Titanate Green (PG50)", hex: "#4F8A6D" },
            { name: "Chromium Oxide Green (PG17)", hex: "#6E7F3C" },
            { name: "Sap Green", hex: "#5E7A3D" },
            { name: "Hooker's Green", hex: "#29524A" },
            { name: "Titanium White (PW6)", hex: "#F5F5F0" },
            { name: "Carbon Black (PBk6)", hex: "#1C1C1C" },
            { name: "Mars Violet (PR101)", hex: "#5A3A3A" },
            { name: "Sepia", hex: "#4A3728" },
            { name: "Indigo", hex: "#1B2A4A" },
            { name: "Cobalt Teal Blue (PG50)", hex: "#2A8F8C" },
            { name: "Phthalo Turquoise (PB16)", hex: "#007A87" },
            { name: "Cerulean Blue (PB35)", hex: "#2A8FBF" },
            { name: "Prussian Blue (PB27)", hex: "#0F2A4A" },
            { name: "Phthalo Blue (PB15)", hex: "#0C1F8F" },
            { name: "Phthalo Cyan (PB17)", hex: "#0F4FA0" },
            { name: "Manganese Blue (PB33)", hex: "#1E7FA0" },
            { name: "Cobalt Blue (PB28)", hex: "#1F4FA0" },
            { name: "Ultramarine Blue (PB29)", hex: "#2E2E8F" },
            { name: "Cobalt Violet Deep (PV14)", hex: "#6A3F8F" }
        ];

        function hexToRGB(hex) {
            const r = parseInt(hex.slice(1, 3), 16);
            const g = parseInt(hex.slice(3, 5), 16);
            const b = parseInt(hex.slice(5, 7), 16);
            return [r, g, b];
        }

        // Standard sRGB to XYZ conversion (D65)
        function sRGB_to_XYZ(r, g, b) {
            let r_ = r / 255.0;
            let g_ = g / 255.0;
            let b_ = b / 255.0;
            r_ = r_ > 0.04045 ? Math.pow((r_ + 0.055) / 1.055, 2.4) : r_ / 12.92;
            g_ = g_ > 0.04045 ? Math.pow((g_ + 0.055) / 1.055, 2.4) : g_ / 12.92;
            b_ = b_ > 0.04045 ? Math.pow((b_ + 0.055) / 1.055, 2.4) : b_ / 12.92;

            const x = (r_ * 0.4124 + g_ * 0.3576 + b_ * 0.1805) * 100.0;
            const y = (r_ * 0.2126 + g_ * 0.7152 + b_ * 0.0722) * 100.0;
            const z = (r_ * 0.0193 + g_ * 0.1192 + b_ * 0.9505) * 100.0;
            return [x, y, z];
        }

        // Standard XYZ to Lab conversion (D65)
        function XYZ_to_Lab(x, y, z) {
            const ref_X = 95.047;
            const ref_Y = 100.000;
            const ref_Z = 108.883;
            
            let x_ = x / ref_X;
            let y_ = y / ref_Y;
            let z_ = z / ref_Z;

            x_ = x_ > 0.008856 ? Math.pow(x_, 1/3) : (7.787 * x_) + (16 / 116);
            y_ = y_ > 0.008856 ? Math.pow(y_, 1/3) : (7.787 * y_) + (16 / 116);
            z_ = z_ > 0.008856 ? Math.pow(z_, 1/3) : (7.787 * z_) + (16 / 116);

            const L = (116 * y_) - 16;
            const a = 500 * (x_ - y_);
            const b = 200 * (y_ - z_);
            
            return [L, a, b];
        }

        function sRGB_to_Lab(r, g, b) {
            const xyz = sRGB_to_XYZ(r, g, b);
            return XYZ_to_Lab(xyz[0], xyz[1], xyz[2]);
        }

        function xyY_to_sRGB(x, y, Y) {
            if (y === 0 || Y === 0) return [0,0,0];
            
            const X = (x * Y) / y;
            const Z = ((1 - x - y) * Y) / y;

            const M_adapt = [
                [ 0.97224054, -0.0072489 , -0.00810646],
                [-0.01209482,  0.99671245, -0.00185945],
                [-0.0027434 ,  0.00531596,  0.92110922]
            ];
            
            const X_d65 = M_adapt[0][0]*X + M_adapt[0][1]*Y + M_adapt[0][2]*Z;
            const Y_d65 = M_adapt[1][0]*X + M_adapt[1][1]*Y + M_adapt[1][2]*Z;
            const Z_d65 = M_adapt[2][0]*X + M_adapt[2][1]*Y + M_adapt[2][2]*Z;

            const r_l =  3.2404542 * X_d65 - 1.5371385 * Y_d65 - 0.4985314 * Z_d65;
            const g_l = -0.9692660 * X_d65 + 1.8760108 * Y_d65 + 0.0415560 * Z_d65;
            const b_l =  0.0556434 * X_d65 - 0.2040259 * Y_d65 + 1.0572252 * Z_d65;

            function gamma(v) {
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
            const lab = sRGB_to_Lab(rgb[0], rgb[1], rgb[2]);
            const hueIndex = hues.indexOf(H);
            
            if (hueIndex !== -1 || C === 0) {
                munsellColors.push({
                    H: H,
                    V: V,
                    C: C,
                    rgb: rgb,
                    lab: lab,
                    hueIndex: hueIndex
                });
            }
        }

        function findNearestMunsell(r, g, b) {
            const targetLab = sRGB_to_Lab(r, g, b);
            let best = null;
            let bestDist = Infinity;
            for (const entry of munsellColors) {
                const d = Math.pow(entry.lab[0]-targetLab[0], 2) + Math.pow(entry.lab[1]-targetLab[1], 2) + Math.pow(entry.lab[2]-targetLab[2], 2);
                if (d < bestDist) {
                    bestDist = d;
                    best = entry;
                }
            }
            return best;
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

        const solidGroup = new THREE.Group();
        const pigmentsGroup = new THREE.Group();
        scene.add(solidGroup);
        scene.add(pigmentsGroup);

        const boxGeometry = new THREE.BoxGeometry(1.4, 2.8, 1.4);
        const sphereGeometry = new THREE.SphereGeometry(1.2, 32, 32);
        
        const cubes = [];
        const pigmentMarkers = [];

        // Build Voxels
        munsellColors.forEach(color => {
            const yPos = color.V * 3;
            let xPos = 0;
            let zPos = 0;
            let hIndex = color.hueIndex;
            
            if (color.C > 0 && hIndex !== -1) {
                const angle = (hIndex / 40.0) * Math.PI * 2;
                const radius = color.C * 1.5;
                xPos = Math.cos(angle) * radius;
                zPos = -Math.sin(angle) * radius;
            }
            
            // save positions for pigment matching
            color.xPos = xPos;
            color.yPos = yPos;
            color.zPos = zPos;

            const material = new THREE.MeshStandardMaterial({
                color: new THREE.Color(`rgb(${color.rgb[0]}, ${color.rgb[1]}, ${color.rgb[2]})`),
                roughness: 0.8,
                metalness: 0.1
            });
            
            const mesh = new THREE.Mesh(boxGeometry, material);
            mesh.position.set(xPos, yPos, zPos);
            
            mesh.userData = {
                type: 'voxel',
                H: color.C === 0 ? 'N' : color.H,
                V: color.V,
                C: color.C,
                rgb: color.rgb,
                hueIndex: hIndex
            };
            
            if (color.C > 0 && hIndex !== -1) {
                mesh.rotation.y = (hIndex / 40.0) * Math.PI * 2;
            }
            
            cubes.push(mesh);
            solidGroup.add(mesh);
        });

        // Build Pigments
        pigments.forEach(pigment => {
            const rgb = hexToRGB(pigment.hex);
            const nearest = findNearestMunsell(rgb[0], rgb[1], rgb[2]);
            
            const material = new THREE.MeshStandardMaterial({
                color: new THREE.Color(`rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`),
                roughness: 0.2, // Make them shiny to stand out
                metalness: 0.5
            });

            const mesh = new THREE.Mesh(sphereGeometry, material);
            
            // Position slightly shifted if we want to not intersect perfectly, or exactly at the nearest Munsell voxel
            mesh.position.set(nearest.xPos, nearest.yPos, nearest.zPos);
            
            mesh.userData = {
                type: 'pigment',
                name: pigment.name,
                hex: pigment.hex,
                rgb: rgb,
                H: nearest.C === 0 ? 'N' : nearest.H,
                V: nearest.V,
                C: nearest.C
            };

            pigmentMarkers.push(mesh);
            pigmentsGroup.add(mesh);
        });

        solidGroup.position.y = -15;
        pigmentsGroup.position.y = -15;

        // Raycasting for hover info
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        const infoPanel = document.getElementById('info-panel');
        const pigmentInfo = document.getElementById('pigment-info');
        const infoHue = document.getElementById('info-hue');
        const infoValue = document.getElementById('info-value');
        const infoChroma = document.getElementById('info-chroma');
        const colorBox = document.getElementById('color-box');
        
        let hoveredMesh = null;
        let originalEmissive = new THREE.Color(0x000000);

        window.addEventListener('mousemove', (event) => {
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
            
            infoPanel.style.left = (event.clientX + 15) + 'px';
            infoPanel.style.top = (event.clientY + 15) + 'px';
        });

        // UI Controls
        const viewModeSelect = document.getElementById('view-mode');
        const sliceModeSelect = document.getElementById('slice-mode');
        const valueSliderContainer = document.getElementById('value-slider-container');
        const hueSliderContainer = document.getElementById('hue-slider-container');
        const valueSlider = document.getElementById('value-slider');
        const hueSlider = document.getElementById('hue-slider');
        const valueLabel = document.getElementById('value-label');
        const hueLabel = document.getElementById('hue-label');

        function updateVisibility() {
            const viewMode = viewModeSelect.value;
            const sliceMode = sliceModeSelect.value;
            const valLevel = parseInt(valueSlider.value);
            const hueIdx = parseInt(hueSlider.value);
            
            // Set group visibility based on view mode
            solidGroup.visible = (viewMode === 'both' || viewMode === 'voxels');
            pigmentsGroup.visible = (viewMode === 'both' || viewMode === 'pigments');

            // Apply slices to voxels
            cubes.forEach(cube => {
                let visible = true;
                if (sliceMode === 'value') {
                    if (cube.userData.V !== valLevel) visible = false;
                } else if (sliceMode === 'hue') {
                    if (cube.userData.C !== 0 && cube.userData.hueIndex !== hueIdx) visible = false;
                }
                cube.visible = visible;
            });

            // Pigments can also be sliced for consistency? The prompt didn't specify, but it usually makes sense.
            // "toggle to show/hide pigment markers independently from the voxel solid" 
            // We'll apply the slice to pigments too if they are in that slice.
            pigmentMarkers.forEach(marker => {
                let visible = true;
                if (sliceMode === 'value') {
                    if (marker.userData.V !== valLevel) visible = false;
                } else if (sliceMode === 'hue') {
                    // Have to calculate hueIndex of the nearest Munsell voxel for slicing
                    const hIndex = marker.userData.H === 'N' ? -1 : hues.indexOf(marker.userData.H);
                    if (marker.userData.C !== 0 && hIndex !== hueIdx) visible = false;
                }
                marker.visible = visible;
            });
        }

        viewModeSelect.addEventListener('change', updateVisibility);
        
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
            
            // Collect all currently visible objects
            let visibleObjects = [];
            if (solidGroup.visible) {
                visibleObjects = visibleObjects.concat(solidGroup.children.filter(c => c.visible));
            }
            if (pigmentsGroup.visible) {
                visibleObjects = visibleObjects.concat(pigmentsGroup.children.filter(c => c.visible));
            }

            const intersects = raycaster.intersectObjects(visibleObjects);
            
            if (intersects.length > 0) {
                // Find first intersect that isn't wireframe etc
                const object = intersects[0].object;
                if (hoveredMesh !== object) {
                    if (hoveredMesh) hoveredMesh.material.emissive.copy(originalEmissive);
                    hoveredMesh = object;
                    originalEmissive.copy(hoveredMesh.material.emissive);
                    hoveredMesh.material.emissive.setHex(0x555555);
                    
                    infoPanel.style.display = 'block';
                    
                    if (object.userData.type === 'pigment') {
                        pigmentInfo.style.display = 'block';
                        pigmentInfo.innerText = object.userData.name;
                    } else {
                        pigmentInfo.style.display = 'none';
                    }

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

with open('munsell_solid_pigments.html', 'w') as f:
    f.write(final_html)

print("Generated munsell_solid_pigments.html successfully.")
