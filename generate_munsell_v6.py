import json

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Munsell Color Solid with Pigments (v6)</title>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background-color: #222;
            color: #fff;
            font-family: sans-serif;
        }
        #controls {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.8);
            padding: 15px;
            border-radius: 8px;
            z-index: 20;
            width: 300px;
            pointer-events: auto;
        }
        input[type=range] {
            width: 100%;
            margin-top: 5px;
            box-sizing: border-box;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        button {
            background-color: #222;
            color: #ddd;
            border: 1px solid #444;
            border-radius: 4px;
            width: 36px;
            height: 36px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0;
            transition: all 0.2s ease;
        }
        button:hover {
            background-color: #333;
            border-color: #666;
            color: #fff;
        }
        .pigment-label {
            background: rgba(0, 0, 0, 0.85);
            color: #fff;
            padding: 6px 12px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
            cursor: pointer;
            user-select: none;
            white-space: nowrap;
            border: 1px solid #555;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            pointer-events: auto;
        }
        .pigment-label div {
            font-size: 11px;
            color: #aaa;
            margin-top: 2px;
        }
        .hue-anchor-label {
            color: #fff;
            font-size: 24px;
            font-weight: bold;
            text-shadow: 0 0 5px #000, 0 0 10px #000;
            pointer-events: none;
            transition: opacity 0.2s;
        }
        .pigment-label:hover {
            border-color: #fff;
        }
        .sample-label {
            background: rgba(0, 50, 100, 0.9); /* distinct blue background */
            color: #fff;
            padding: 6px 12px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 13px;
            cursor: pointer;
            user-select: none;
            white-space: nowrap;
            border: 1px solid #3a86ff;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            pointer-events: auto;
        }
        .sample-label div {
            font-size: 11px;
            color: #bbb;
            margin-top: 2px;
        }
        .sample-label:hover {
            border-color: #fff;
        }
        #drop-zone.dragover {
            background: rgba(255,255,255,0.1);
            border-color: #aaa;
        }
        .ctrl-btn {
            background-color: #222 !important;
            color: #ddd !important;
            border: 1px solid #444 !important;
            border-radius: 4px !important;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .ctrl-btn:hover:not(:disabled) {
            background-color: #333 !important;
            border-color: #666 !important;
            color: #fff !important;
        }
        .ctrl-btn:disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }
    </style>
    <script type="importmap">
        {
            "imports": {
                "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
                "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
            }
        }
    </script>
</head>
<body>
    <div id="controls">
        <div style="display: flex; gap: 8px; margin-bottom: 15px;">
            <button id="view-btn" title="Toggle View (Top / Side)">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
            </button>
            <button id="reset-btn" title="Reset Labels">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="m7 21-4.3-4.3c-1-1-1-2.5 0-3.4l9.6-9.6c1-1 2.5-1 3.4 0l5.6 5.6c1 1 1 2.5 0 3.4L13 21"></path>
                    <path d="M22 21H7"></path>
                    <path d="m5 11 9 9"></path>
                </svg>
            </button>
            <button id="toggle-mix-btn" title="Toggle Mix Shape">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2L2 22h20z"></path>
                </svg>
            </button>
            <button id="hide-unpinned-btn" title="Hide Unpinned Pigments">
                <svg id="eye-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                </svg>
                <svg id="eye-slash-icon" style="display: none;" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                    <line x1="1" y1="1" x2="23" y2="23"></line>
                </svg>
            </button>
        </div>
        
        <div style="margin-bottom: 15px;">
            <label>Max Value: <span id="value-label">10</span></label>
            <input type="range" id="value-slider" min="1" max="10" step="1" value="10">
        </div>
        
        <div>
            <label>Transparency: <span id="transparency-label">0</span>%</label>
            <input type="range" id="transparency-slider" min="0" max="100" step="1" value="0">
        </div>
        
        <!-- Image Sampling & Pigment-Constrained Palette Preview -->
        <hr style="border: 0; border-top: 1px solid #444; margin: 15px 0;">
        <div id="image-panel-toggle" style="cursor: pointer; display: flex; justify-content: space-between; align-items: center; font-weight: bold; margin-bottom: 10px; user-select: none;">
            <span>Image Palette Tool</span>
            <span id="image-panel-arrow">[+]</span>
        </div>
        <div id="image-panel-content" style="display: none; flex-direction: column; gap: 12px;">
            <!-- Drag and drop zone / file input -->
            <div id="drop-zone" style="border: 2px dashed #555; border-radius: 6px; padding: 15px; text-align: center; cursor: pointer; transition: background 0.2s; background: rgba(255,255,255,0.02);">
                <span id="drop-text" style="font-size: 13px; color: #aaa;">Drag & drop image here or click to browse</span>
                <input type="file" id="file-input" accept="image/*" style="display: none;">
            </div>
            
            <!-- Thumbnail preview -->
            <div id="thumb-container" style="display: none; position: relative; text-align: center;">
                <canvas id="thumb-canvas" style="max-width: 100%; border-radius: 4px; box-shadow: 0 4px 8px rgba(0,0,0,0.4); display: block; margin: 0 auto;"></canvas>
                <!-- Overlay canvas for selection crosshair -->
                <canvas id="overlay-canvas" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;"></canvas>
            </div>
            
            <!-- Action buttons -->
            <div style="display: flex; gap: 8px;">
                <button id="auto-sample-btn" class="ctrl-btn" style="flex: 1; font-size: 12px; padding: 6px; cursor: pointer; height: auto; width: auto; display: block;" disabled>Auto Sample</button>
                <button id="toggle-view-image-btn" class="ctrl-btn" style="flex: 1; font-size: 12px; padding: 6px; cursor: pointer; height: auto; width: auto; display: none;">Show Original</button>
            </div>

            <!-- Pigment mixture section -->
            <div id="pigment-mix-section" style="border-top: 1px solid #333; padding-top: 10px; display: none;">
                <button id="pigment-preview-btn" class="ctrl-btn" style="font-size: 12px; padding: 6px; cursor: pointer; width: 100%; height: auto; display: block; margin-bottom: 8px;">Pigment Mixture Preview</button>
                
                <div id="pigment-checklist-container" style="display: none; max-height: 150px; overflow-y: auto; border: 1px solid #444; border-radius: 4px; padding: 6px; background: rgba(0,0,0,0.3); margin-bottom: 10px; text-align: left;">
                    <!-- Checkboxes will be populated dynamically -->
                </div>
                
                <div id="accuracy-container" style="display: none; flex-direction: column; gap: 6px; margin-top: 6px;">
                    <label style="font-size: 12px; cursor: pointer; display: flex; align-items: center; gap: 6px; margin: 0; font-weight: normal;">
                        <input type="checkbox" id="show-accuracy-toggle" style="margin: 0;"> Show Palette Accuracy
                    </label>
                    <div id="accuracy-legend" style="display: none; height: 14px; border-radius: 3px; background: linear-gradient(to right, #00ff00, #ffff00, #ff0000); border: 1px solid #555; width: 100%;"></div>
                    <div style="display: flex; justify-content: space-between; font-size: 10px; color: #aaa;">
                        <span>Low error</span>
                        <span id="avg-delta-e" style="font-weight: bold; color: #fff;">Avg &Delta;E: --</span>
                        <span>High error</span>
                    </div>
                </div>
                <button id="highlight-toggle-btn" class="ctrl-btn" style="font-size: 12px; padding: 6px; cursor: pointer; width: 100%; height: auto; display: block; margin-top: 6px;">Highlight Sampled Voxels: OFF</button>
            </div>
        </div>
    </div>

    <script type="module">
        import * as THREE from 'three';
        import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
        import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
        import { ConvexGeometry } from 'three/addons/geometries/ConvexGeometry.js';

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

        const pigmentsList = [
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
            { name: "Alizarin Crimson (PR83)", hex: "#8B1A2B" },
            { name: "Cobalt Violet Deep (PV14)", hex: "#6A3F8F" }
        ];

        function hexToRGB(hex) {
            const r = parseInt(hex.slice(1, 3), 16);
            const g = parseInt(hex.slice(3, 5), 16);
            const b = parseInt(hex.slice(5, 7), 16);
            return [r, g, b];
        }

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

        function XYZ_to_Lab(x, y, z) {
            const ref_X = 95.047, ref_Y = 100.000, ref_Z = 108.883;
            let x_ = x / ref_X, y_ = y / ref_Y, z_ = z / ref_Z;
            x_ = x_ > 0.008856 ? Math.pow(x_, 1/3) : (7.787 * x_) + (16 / 116);
            y_ = y_ > 0.008856 ? Math.pow(y_, 1/3) : (7.787 * y_) + (16 / 116);
            z_ = z_ > 0.008856 ? Math.pow(z_, 1/3) : (7.787 * z_) + (16 / 116);
            return [(116 * y_) - 16, 500 * (x_ - y_), 200 * (y_ - z_)];
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
            const gamma = v => {
                v = v / 100.0;
                if (v <= 0) return 0;
                if (v >= 1) return 1;
                return v <= 0.0031308 ? 12.92 * v : 1.055 * Math.pow(v, 1.0 / 2.4) - 0.055;
            };
            return [
                Math.max(0, Math.min(255, Math.round(gamma(r_l) * 255))),
                Math.max(0, Math.min(255, Math.round(gamma(g_l) * 255))),
                Math.max(0, Math.min(255, Math.round(gamma(b_l) * 255)))
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
                munsellColors.push({ H, V, C, rgb, lab, hueIndex });
            }
        }

        function findNearestMunsell(r, g, b) {
            const targetLab = sRGB_to_Lab(r, g, b);
            let best = null, bestDist = Infinity;
            for (const entry of munsellColors) {
                const d = Math.pow(entry.lab[0]-targetLab[0], 2) + Math.pow(entry.lab[1]-targetLab[1], 2) + Math.pow(entry.lab[2]-targetLab[2], 2);
                if (d < bestDist) { bestDist = d; best = entry; }
            }
            return best;
        }

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x333333);
        
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.01, 50000);
        camera.position.set(40, 30, 40);

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        document.body.appendChild(renderer.domElement);

        // Setup CSS2DRenderer
        const labelRenderer = new CSS2DRenderer();
        labelRenderer.setSize(window.innerWidth, window.innerHeight);
        labelRenderer.domElement.style.position = 'absolute';
        labelRenderer.domElement.style.top = '0px';
        labelRenderer.domElement.style.pointerEvents = 'none'; // let mouse events pass through to canvas
        document.body.appendChild(labelRenderer.domElement);

        // We bind OrbitControls to the renderer domElement so it gets pointer events
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.target.set(0, 15, 0);
        controls.maxDistance = 800;
        controls.minDistance = 5;
        controls.enableZoom = false;

        // Custom smooth zoom — does NOT call controls.update(), letting animate() pick up the change
        renderer.domElement.addEventListener('wheel', (e) => {
            e.preventDefault();
            const step = Math.max(1, camera.position.distanceTo(controls.target) * 0.03);
            const direction = e.deltaY > 0 ? 1 : -1;
            const currentDist = camera.position.distanceTo(controls.target);
            const newDist = Math.max(controls.minDistance, Math.min(controls.maxDistance, currentDist + direction * step));
            const factor = newDist / currentDist;
            const offset = new THREE.Vector3().subVectors(camera.position, controls.target);
            offset.multiplyScalar(factor);
            camera.position.copy(controls.target).add(offset);
            // Diagnostic: log before-andafter state
            console.log(`ZOOM deltaY=${e.deltaY} dist=${newDist.toFixed(2)} cam=(${camera.position.x.toFixed(1)},${camera.position.y.toFixed(1)},${camera.position.z.toFixed(1)})`);
        }, { passive: false });

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
        const mixGroup = new THREE.Group();
        const sampleLabelGroup = new THREE.Group();
        scene.add(solidGroup);
        scene.add(pigmentsGroup);
        scene.add(mixGroup);
        scene.add(sampleLabelGroup);

        const hueAnchors = [];
        const anchorData = [
            { label: 'R', h: 0 },
            { label: 'M', h: 100 / 6 },
            { label: 'B', h: 200 / 6 },
            { label: 'C', h: 300 / 6 },
            { label: 'G', h: 400 / 6 },
            { label: 'Y', h: 500 / 6 }
        ];

        anchorData.forEach(data => {
            const theta = ((data.h * 3.6) - 20) * (Math.PI / 180);
            const radius = 40;
            const x = Math.cos(theta) * radius;
            const z = Math.sin(theta) * radius;
            const y = 33; // Floating above the solid

            const div = document.createElement('div');
            div.className = 'hue-anchor-label';
            div.textContent = data.label;
            
            const cssObj = new CSS2DObject(div);
            cssObj.position.set(x, y, z);
            solidGroup.add(cssObj);
            hueAnchors.push(div);
        });

        const boxGeometry = new THREE.BoxGeometry(1.4, 2.8, 1.4);
        const cubes = [];
        let highlightMode = false;
        const highlightedVoxelIndices = new Set();
        const pinnedPigments = new Set();
        let syncingPigments = false;

        // Build Voxels
        munsellColors.forEach((color, idx) => {
            const yPos = color.V * 3;
            let xPos = 0, zPos = 0;
            let hIndex = color.hueIndex;
            if (color.C > 0 && hIndex !== -1) {
                const angle = (hIndex / 40.0) * Math.PI * 2;
                const radius = color.C * 1.5;
                xPos = Math.cos(angle) * radius;
                zPos = -Math.sin(angle) * radius;
            }
            color.xPos = xPos; color.yPos = yPos; color.zPos = zPos;

            const material = new THREE.MeshStandardMaterial({
                color: new THREE.Color(`rgb(${color.rgb[0]}, ${color.rgb[1]}, ${color.rgb[2]})`),
                roughness: 0.8,
                metalness: 0.1,
                transparent: true,
                opacity: 1.0,
                depthWrite: true
            });
            
            const mesh = new THREE.Mesh(boxGeometry, material);
            mesh.position.set(xPos, yPos, zPos);
            mesh.userData = { V: color.V, cubeIdx: idx };
            if (color.C > 0 && hIndex !== -1) mesh.rotation.y = (hIndex / 40.0) * Math.PI * 2;
            
            cubes.push(mesh);
            solidGroup.add(mesh);
        });

        const pigmentBoxes = [];

        // Build Pigments
        const markerGeometry = new THREE.BoxGeometry(0.8, 1.6, 0.8);
        pigmentsList.forEach((pigment, pigmentIdx) => {
            const rgb = hexToRGB(pigment.hex);
            const nearest = findNearestMunsell(rgb[0], rgb[1], rgb[2]);
            
            const markerMaterial = new THREE.MeshBasicMaterial({
                color: new THREE.Color(`rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`)
            });
            const marker = new THREE.Mesh(markerGeometry, markerMaterial);
            const basePos = new THREE.Vector3(nearest.xPos, nearest.yPos, nearest.zPos);
            marker.position.copy(basePos);
            
            if (nearest.C > 0 && nearest.hueIndex !== -1) {
                marker.rotation.y = (nearest.hueIndex / 40.0) * Math.PI * 2;
            }

            // Create CSS2D Object
            const div = document.createElement('div');
            div.className = 'pigment-label';
            div.textContent = pigment.name;

            const labelObj = new CSS2DObject(div);
            labelObj.position.set(0, 3, 0); // Offset slightly above
            labelObj.visible = false;
            marker.add(labelObj);

            marker.userData = { 
                pigmentIdx: pigmentIdx,
                div: div,
                labelObj: labelObj,
                state: {
                    hoveredVoxel: false,
                    hoveredLabel: false,
                    pinned: false
                },
                updateVisibility: function() {
                    const s = this.state;
                    this.labelObj.visible = (s.hoveredVoxel || s.hoveredLabel || s.pinned);
                }
            };
            
            // Label events
            div.addEventListener('mouseenter', () => {
                marker.userData.state.hoveredLabel = true;
                marker.userData.updateVisibility();
            });
            div.addEventListener('mouseleave', () => {
                marker.userData.state.hoveredLabel = false;
                marker.userData.updateVisibility();
            });
            
            // Clicking label toggles pin via shared state
            div.addEventListener('mousedown', (e) => e.stopPropagation());
            div.addEventListener('mouseup', (e) => {
                e.stopPropagation();
                const idx = marker.userData.pigmentIdx;
                if (pinnedPigments.has(idx)) pinnedPigments.delete(idx);
                else pinnedPigments.add(idx);
                syncPigmentUI();
            });

            pigmentBoxes.push(marker);
            pigmentsGroup.add(marker);
        });

        solidGroup.position.y = -15;
        pigmentsGroup.position.y = -15;
        mixGroup.position.y = -15;
        sampleLabelGroup.position.y = -15;

        // --- Pigment Mixing Logic ---
        const mixMaterial = new THREE.ShaderMaterial({
            vertexShader: `
                attribute vec3 logColor;
                varying vec3 vLogColor;
                void main() {
                    vLogColor = logColor;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                varying vec3 vLogColor;
                void main() {
                    // Hardware interpolation of logs gives weighted arithmetic mean of logs,
                    // which equals the log of the weighted geometric mean!
                    vec3 rgb = exp(vLogColor);
                    gl_FragColor = vec4(rgb, 0.6); // 0.6 opacity as requested
                }
            `,
            transparent: true,
            side: THREE.DoubleSide,
            depthWrite: false
        });
        
        const mixLineMaterial = new THREE.ShaderMaterial({
            vertexShader: `
                attribute vec3 logColor;
                varying vec3 vLogColor;
                void main() {
                    vLogColor = logColor;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                varying vec3 vLogColor;
                void main() {
                    vec3 rgb = exp(vLogColor);
                    gl_FragColor = vec4(rgb, 0.8);
                }
            `,
            transparent: true,
            depthWrite: false
        });

        let isMixVisible = true;
        let currentMixMesh = null;

        function updateMixShape() {
            if (currentMixMesh) {
                mixGroup.remove(currentMixMesh);
                currentMixMesh.geometry.dispose();
                currentMixMesh = null;
            }

            if (!isMixVisible) return;

            const pinned = pigmentBoxes.filter(b => b.userData.state.pinned);
            if (pinned.length < 2) return;

            const points = [];
            const logColorsMap = new Map();

            pinned.forEach(marker => {
                const p = marker.position.clone();
                points.push(p);
                const col = marker.material.color;
                const eps = 0.001; // Clamp to avoid log(0) - -Infinity
                logColorsMap.set(`${p.x.toFixed(4)},${p.y.toFixed(4)},${p.z.toFixed(4)}`, [
                    Math.log(Math.max(col.r, eps)),
                    Math.log(Math.max(col.g, eps)),
                    Math.log(Math.max(col.b, eps))
                ]);
            });

            if (pinned.length === 2) {
                const geometry = new THREE.BufferGeometry().setFromPoints(points);
                const logColors = new Float32Array(6);
                
                const c1 = logColorsMap.get(`${points[0].x.toFixed(4)},${points[0].y.toFixed(4)},${points[0].z.toFixed(4)}`);
                logColors[0] = c1[0]; logColors[1] = c1[1]; logColors[2] = c1[2];
                
                const c2 = logColorsMap.get(`${points[1].x.toFixed(4)},${points[1].y.toFixed(4)},${points[1].z.toFixed(4)}`);
                logColors[3] = c2[0]; logColors[4] = c2[1]; logColors[5] = c2[2];
                
                geometry.setAttribute('logColor', new THREE.BufferAttribute(logColors, 3));
                currentMixMesh = new THREE.Line(geometry, mixLineMaterial);
                mixGroup.add(currentMixMesh);
            } else if (pinned.length === 3) {
                const geometry = new THREE.BufferGeometry().setFromPoints(points);
                const logColors = new Float32Array(9);
                
                for (let i = 0; i < 3; i++) {
                    const c = logColorsMap.get(`${points[i].x.toFixed(4)},${points[i].y.toFixed(4)},${points[i].z.toFixed(4)}`);
                    logColors[i*3] = c[0];
                    logColors[i*3+1] = c[1];
                    logColors[i*3+2] = c[2];
                }
                
                geometry.setAttribute('logColor', new THREE.BufferAttribute(logColors, 3));
                currentMixMesh = new THREE.Mesh(geometry, mixMaterial);
                mixGroup.add(currentMixMesh);
            } else {
                const geometry = new ConvexGeometry(points);
                const posAttr = geometry.attributes.position;
                const logColors = new Float32Array(posAttr.count * 3);
                
                for (let i = 0; i < posAttr.count; i++) {
                    const pt = new THREE.Vector3(posAttr.getX(i), posAttr.getY(i), posAttr.getZ(i));
                    
                    let bestDist = Infinity;
                    let bestKey = null;
                    points.forEach(op => {
                        const d = op.distanceToSquared(pt);
                        if (d < bestDist) {
                            bestDist = d;
                            bestKey = `${op.x.toFixed(4)},${op.y.toFixed(4)},${op.z.toFixed(4)}`;
                        }
                    });
                    
                    const c = logColorsMap.get(bestKey);
                    logColors[i*3] = c[0];
                    logColors[i*3+1] = c[1];
                    logColors[i*3+2] = c[2];
                }
                
                geometry.setAttribute('logColor', new THREE.BufferAttribute(logColors, 3));
                currentMixMesh = new THREE.Mesh(geometry, mixMaterial);
                mixGroup.add(currentMixMesh);
            }
        }
        // -----------------------------

        // Interaction logic
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        
        let isDragging = false;
        let mouseDownPos = new THREE.Vector2();

        window.addEventListener('mousedown', (event) => {
            isDragging = false;
            mouseDownPos.set(event.clientX, event.clientY);
        });

        window.addEventListener('mousemove', (event) => {
            if (mouseDownPos.distanceTo(new THREE.Vector2(event.clientX, event.clientY)) > 5) {
                isDragging = true;
            }
            
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
            
            raycaster.setFromCamera(mouse, camera);
            
            pigmentBoxes.forEach(box => {
                box.userData.state.hoveredVoxel = false;
            });
            sampleBoxes.forEach(box => {
                box.userData.state.hovered = false;
            });
            
            const intersects = raycaster.intersectObjects(pigmentBoxes);
            if (intersects.length > 0) {
                const box = intersects[0].object;
                box.userData.state.hoveredVoxel = true;
            }
            
            const intersectsSample = raycaster.intersectObjects(sampleBoxes);
            if (intersectsSample.length > 0) {
                const box = intersectsSample[0].object;
                box.userData.state.hovered = true;
            }
            
            pigmentBoxes.forEach(box => box.userData.updateVisibility());
            sampleBoxes.forEach(box => box.userData.updateVisibility());
        });

        window.addEventListener('mouseup', (event) => {
            if (isDragging) return;
            
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
            
            raycaster.setFromCamera(mouse, camera);
            
            // Check pigment boxes (to toggle via shared state)
            const intersects = raycaster.intersectObjects(pigmentBoxes);
            if (intersects.length > 0) {
                const marker = intersects[0].object;
                const idx = marker.userData.pigmentIdx;
                if (pinnedPigments.has(idx)) pinnedPigments.delete(idx);
                else pinnedPigments.add(idx);
                syncPigmentUI();
                return;
            }
            
            // Check sample boxes (to pin & show crosshair)
            const intersectsSample = raycaster.intersectObjects(sampleBoxes);
            if (intersectsSample.length > 0) {
                const marker = intersectsSample[0].object;
                const pt = marker.userData.pt;
                
                const wasPinned = marker.userData.state.pinned;
                sampleBoxes.forEach(box => {
                    box.userData.state.pinned = false;
                    box.userData.updateVisibility();
                });
                
                marker.userData.state.pinned = !wasPinned;
                marker.userData.updateVisibility();
                
                if (marker.userData.state.pinned) {
                    showCrosshair(pt);
                } else {
                    showCrosshair(null);
                }
            }
        });

        // --- Image Palette Tool Variables & Logic ---
        let originalImageData = null;
        let recoloredImageData = null;
        let heatmapImageData = null;
        let errorsData = null;
        const sampleBoxes = [];
        const sampleSphereGeom = new THREE.SphereGeometry(0.5, 16, 12);

        const panelToggle = document.getElementById('image-panel-toggle');
        const panelContent = document.getElementById('image-panel-content');
        const panelArrow = document.getElementById('image-panel-arrow');
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('file-input');
        const thumbCanvas = document.getElementById('thumb-canvas');
        const overlayCanvas = document.getElementById('overlay-canvas');
        const autoSampleBtn = document.getElementById('auto-sample-btn');
        const toggleViewBtn = document.getElementById('toggle-view-image-btn');
        const pigmentMixSection = document.getElementById('pigment-mix-section');
        const pigmentPreviewBtn = document.getElementById('pigment-preview-btn');
        const checklistContainer = document.getElementById('pigment-checklist-container');
        const accuracyContainer = document.getElementById('accuracy-container');
        const showAccuracyToggle = document.getElementById('show-accuracy-toggle');
        const overlayCtx = overlayCanvas.getContext('2d');

        panelToggle.addEventListener('click', () => {
            const isHidden = panelContent.style.display === 'none';
            panelContent.style.display = isHidden ? 'flex' : 'none';
            panelArrow.textContent = isHidden ? '[-]' : '[+]';
        });

        dropZone.addEventListener('click', () => fileInput.click());
        dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) handleImageFile(e.dataTransfer.files[0]);
        });
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) handleImageFile(fileInput.files[0]);
        });

        function handleImageFile(file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = new Image();
                img.onload = function() {
                    const maxEdge = 400;
                    let w = img.width, h = img.height;
                    if (w > maxEdge || h > maxEdge) {
                        if (w > h) { h = Math.round((h * maxEdge) / w); w = maxEdge; }
                        else { w = Math.round((w * maxEdge) / h); h = maxEdge; }
                    }
                    thumbCanvas.width = w; thumbCanvas.height = h;
                    overlayCanvas.width = w; overlayCanvas.height = h;
                    
                    const ctx = thumbCanvas.getContext('2d');
                    ctx.drawImage(img, 0, 0, w, h);
                    originalImageData = ctx.getImageData(0, 0, w, h);
                    recoloredImageData = null; heatmapImageData = null; errorsData = null;
                    
                    document.querySelectorAll('.pigment-mix-checkbox').forEach(cb => cb.checked = false);
                    showAccuracyToggle.checked = false;
                    toggleViewBtn.style.display = 'none';
                    toggleViewBtn.textContent = 'Show Original';
                    accuracyContainer.style.display = 'none';
                    document.getElementById('thumb-container').style.display = 'block';
                    autoSampleBtn.disabled = false;
                    pigmentMixSection.style.display = 'block';
                    
                    clearSampleMarkers();
                    showCrosshair(null);
                    pinnedPigments.clear();
                    syncPigmentUI();
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }

        function fastSRGBToLab(r, g, b) {
            let r_ = r / 255.0, g_ = g / 255.0, b_ = b / 255.0;
            r_ = r_ > 0.04045 ? Math.pow((r_ + 0.055) / 1.055, 2.4) : r_ / 12.92;
            g_ = g_ > 0.04045 ? Math.pow((g_ + 0.055) / 1.055, 2.4) : g_ / 12.92;
            b_ = b_ > 0.04045 ? Math.pow((b_ + 0.055) / 1.055, 2.4) : b_ / 12.92;
            const x = (r_ * 0.4124 + g_ * 0.3576 + b_ * 0.1805) * 100.0;
            const y = (r_ * 0.2126 + g_ * 0.7152 + b_ * 0.0722) * 100.0;
            const z = (r_ * 0.0193 + g_ * 0.1192 + b_ * 0.9505) * 100.0;
            const ref_X = 95.047, ref_Y = 100.000, ref_Z = 108.883;
            let x_ = x / ref_X, y_ = y / ref_Y, z_ = z / ref_Z;
            x_ = x_ > 0.008856 ? Math.pow(x_, 1/3) : (7.787 * x_) + (16 / 116);
            y_ = y_ > 0.008856 ? Math.pow(y_, 1/3) : (7.787 * y_) + (16 / 116);
            z_ = z_ > 0.008856 ? Math.pow(z_, 1/3) : (7.787 * z_) + (16 / 116);
            return [(116 * y_) - 16, 500 * (x_ - y_), 200 * (y_ - z_)];
        }

        function findNearestPigment(r, g, b) {
            const sLab = sRGB_to_Lab(r, g, b);
            let nearest = null, minDist = Infinity;
            pigmentsList.forEach(p => {
                const pRGB = hexToRGB(p.hex);
                const pLab = sRGB_to_Lab(pRGB[0], pRGB[1], pRGB[2]);
                const d = Math.pow(pLab[0]-sLab[0], 2) + Math.pow(pLab[1]-sLab[1], 2) + Math.pow(pLab[2]-sLab[2], 2);
                if (d < minDist) { minDist = d; nearest = p; }
            });
            return nearest;
        }

        function clearSampleMarkers() {
            while (sampleLabelGroup.children.length > 0) {
                const child = sampleLabelGroup.children[0];
                sampleLabelGroup.remove(child);
                if (child.geometry) child.geometry.dispose();
                if (child.material) child.material.dispose();
            }
            sampleBoxes.length = 0;
            highlightedVoxelIndices.clear();
        }

        function showCrosshair(pt) {
            overlayCtx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
            if (!pt) return;
            overlayCtx.strokeStyle = '#ff3a3a';
            overlayCtx.lineWidth = 2;
            overlayCtx.beginPath();
            overlayCtx.arc(pt.x, pt.y, 6, 0, Math.PI * 2);
            overlayCtx.stroke();
            overlayCtx.beginPath();
            overlayCtx.moveTo(pt.x - 12, pt.y);
            overlayCtx.lineTo(pt.x + 12, pt.y);
            overlayCtx.moveTo(pt.x, pt.y - 12);
            overlayCtx.lineTo(pt.x, pt.y + 12);
            overlayCtx.stroke();
        }

        function addSamplePoint(x, y, srcData, w, h) {
            // 5x5 neighborhood average at the clicked pixel
            let rSum = 0, gSum = 0, bSum = 0, count = 0;
            for (let dy = -2; dy <= 2; dy++) {
                for (let dx = -2; dx <= 2; dx++) {
                    const nx = x + dx, ny = y + dy;
                    if (nx >= 0 && nx < w && ny >= 0 && ny < h) {
                        const idx = (ny * w + nx) * 4;
                        rSum += srcData[idx]; gSum += srcData[idx+1]; bSum += srcData[idx+2]; count++;
                    }
                }
            }
            const avgR = rSum / count, avgG = gSum / count, avgB = bSum / count;

            const nearest = findNearestMunsell(avgR, avgG, avgB);
            const munsellIdx = munsellColors.indexOf(nearest);
            const targetLab = sRGB_to_Lab(avgR, avgG, avgB);

            console.log(`Sample at (${x},${y}): RGB(${avgR.toFixed(0)},${avgG.toFixed(0)},${avgB.toFixed(0)}) Lab(${targetLab[0].toFixed(1)},${targetLab[1].toFixed(1)},${targetLab[2].toFixed(1)}) -> ${nearest.H} ${nearest.V}/${nearest.C} (Lab ${nearest.lab[0].toFixed(1)},${nearest.lab[1].toFixed(1)},${nearest.lab[2].toFixed(1)}) idx=${munsellIdx}`);

            if (munsellIdx !== -1) {
                highlightedVoxelIndices.add(munsellIdx);
            } else {
                console.warn(`No matching voxel found for sample at (${x},${y})`);
            }

            const nearestPigment = findNearestPigment(avgR, avgG, avgB);
            const div = document.createElement('div');
            div.className = 'sample-label';
            div.innerHTML = `Sample: ${nearest.H} ${nearest.V}/${nearest.C}<div>Nearest: ${nearestPigment.name}</div>`;
            const labelObj = new CSS2DObject(div);
            labelObj.position.set(0, 2, 0);
            labelObj.visible = false;

            const nrgb = nearest.rgb;
            const anchor = new THREE.Mesh(sampleSphereGeom, new THREE.MeshBasicMaterial({
                color: new THREE.Color(`rgb(${nrgb[0]}, ${nrgb[1]}, ${nrgb[2]})`)
            }));
            anchor.position.set(nearest.xPos, nearest.yPos, nearest.zPos);
            anchor.add(labelObj);

            anchor.userData = {
                pt: { x, y }, div, labelObj,
                state: { hovered: false, pinned: false },
                updateVisibility: function() { this.labelObj.visible = (this.state.hovered || this.state.pinned); }
            };

            div.addEventListener('mouseenter', () => { anchor.userData.state.hovered = true; anchor.userData.updateVisibility(); });
            div.addEventListener('mouseleave', () => { anchor.userData.state.hovered = false; anchor.userData.updateVisibility(); });
            div.addEventListener('mousedown', (e) => e.stopPropagation());
            div.addEventListener('mouseup', (e) => {
                e.stopPropagation();
                const wasPinned = anchor.userData.state.pinned;
                sampleBoxes.forEach(box => { box.userData.state.pinned = false; box.userData.updateVisibility(); });
                anchor.userData.state.pinned = !wasPinned;
                anchor.userData.updateVisibility();
                if (anchor.userData.state.pinned) showCrosshair({ x, y });
                else showCrosshair(null);
            });

            sampleBoxes.push(anchor);
            sampleLabelGroup.add(anchor);

            if (!highlightMode) {
                highlightMode = true;
                const hBtn = document.getElementById('highlight-toggle-btn');
                if (hBtn) hBtn.textContent = 'Highlight Sampled Voxels: ON';
            }
            updateVoxels();
        }

        // Click-to-sample on the image canvas
        thumbCanvas.addEventListener('click', (e) => {
            if (!originalImageData) return;
            const rect = thumbCanvas.getBoundingClientRect();
            const x = Math.round((e.clientX - rect.left) * (originalImageData.width / rect.width));
            const y = Math.round((e.clientY - rect.top) * (originalImageData.height / rect.height));
            const cx = Math.max(0, Math.min(originalImageData.width - 1, x));
            const cy = Math.max(0, Math.min(originalImageData.height - 1, y));
            addSamplePoint(cx, cy, originalImageData.data, originalImageData.width, originalImageData.height);
        });

        function updatePreviewDisplay() {
            if (!originalImageData) return;
            const ctx = thumbCanvas.getContext('2d');
            const showOriginal = toggleViewBtn.textContent === 'Show Recolored';
            const accuracyLegend = document.getElementById('accuracy-legend');
            const avgDeltaE = document.getElementById('avg-delta-e');

            if (showOriginal) {
                ctx.putImageData(originalImageData, 0, 0);
                accuracyLegend.style.display = 'none';
                avgDeltaE.textContent = 'Avg dE: --';
            } else if (showAccuracyToggle.checked && heatmapImageData) {
                ctx.putImageData(heatmapImageData, 0, 0);
                accuracyLegend.style.display = 'block';
                // Compute average Delta E from errorsData
                if (errorsData && errorsData.length > 0) {
                    let sum = 0;
                    for (let i = 0; i < errorsData.length; i++) sum += errorsData[i];
                    const avg = (sum / errorsData.length).toFixed(1);
                    avgDeltaE.textContent = `Avg dE: ${avg} - lower is better`;
                }
            } else if (recoloredImageData) {
                ctx.putImageData(recoloredImageData, 0, 0);
                accuracyLegend.style.display = 'none';
                if (errorsData && errorsData.length > 0) {
                    let sum = 0;
                    for (let i = 0; i < errorsData.length; i++) sum += errorsData[i];
                    const avg = (sum / errorsData.length).toFixed(1);
                    avgDeltaE.textContent = `Avg dE: ${avg}`;
                }
            } else {
                ctx.putImageData(originalImageData, 0, 0);
                accuracyLegend.style.display = 'none';
                avgDeltaE.textContent = 'Avg dE: --';
            }
        }

        toggleViewBtn.addEventListener('click', () => {
            if (toggleViewBtn.textContent === 'Show Original') {
                toggleViewBtn.textContent = 'Show Recolored';
            } else {
                toggleViewBtn.textContent = 'Show Original';
            }
            updatePreviewDisplay();
        });

        showAccuracyToggle.addEventListener('change', () => {
            updatePreviewDisplay();
        });

        autoSampleBtn.addEventListener('click', () => {
            if (!originalImageData) return;
            const w = originalImageData.width, h = originalImageData.height;
            const data = originalImageData.data;

            // Grayscale
            const gray = new Float32Array(w * h);
            for (let i = 0; i < w * h; i++) {
                gray[i] = 0.299 * data[i*4] + 0.587 * data[i*4+1] + 0.114 * data[i*4+2];
            }

            // Sobel edge magnitude
            const edge = new Float32Array(w * h);
            let maxEdge = 0;
            for (let y = 1; y < h - 1; y++) {
                for (let x = 1; x < w - 1; x++) {
                    const idx = y * w + x;
                    const gx = -1*gray[(y-1)*w+(x-1)] + 1*gray[(y-1)*w+(x+1)] - 2*gray[y*w+(x-1)] + 2*gray[y*w+(x+1)] - 1*gray[(y+1)*w+(x-1)] + 1*gray[(y+1)*w+(x+1)];
                    const gy = -1*gray[(y-1)*w+(x-1)] - 2*gray[(y-1)*w+x] - 1*gray[(y-1)*w+(x+1)] + 1*gray[(y+1)*w+(x-1)] + 2*gray[(y+1)*w+x] + 1*gray[(y+1)*w+(x+1)];
                    const mag = Math.sqrt(gx*gx + gy*gy);
                    edge[idx] = mag;
                    if (mag > maxEdge) maxEdge = mag;
                }
            }
            if (maxEdge > 0) for (let i = 0; i < edge.length; i++) edge[i] /= maxEdge;

            // Local chroma (Lab C*)
            const chroma = new Float32Array(w * h);
            let maxChroma = 0;
            for (let i = 0; i < w * h; i++) {
                const lab = sRGB_to_Lab(data[i*4], data[i*4+1], data[i*4+2]);
                const cVal = Math.sqrt(lab[1]*lab[1] + lab[2]*lab[2]);
                chroma[i] = cVal;
                if (cVal > maxChroma) maxChroma = cVal;
            }
            if (maxChroma > 0) for (let i = 0; i < chroma.length; i++) chroma[i] /= maxChroma;

            // Combined interest score
            const scores = new Float32Array(w * h);
            for (let i = 0; i < scores.length; i++) scores[i] = 0.5 * edge[i] + 0.5 * chroma[i];

            // Grid clustering: 4x5 cells
            const gridRows = 4, gridCols = 5;
            const cellW = w / gridCols, cellH = h / gridRows;
            const selectedPoints = [];
            for (let r = 0; r < gridRows; r++) {
                for (let c = 0; c < gridCols; c++) {
                    const xStart = Math.floor(c * cellW), xEnd = Math.min(w, Math.floor((c+1)*cellW));
                    const yStart = Math.floor(r * cellH), yEnd = Math.min(h, Math.floor((r+1)*cellH));
                    let bestX = -1, bestY = -1, maxScore = -1;
                    for (let y = yStart; y < yEnd; y++) {
                        for (let x = xStart; x < xEnd; x++) {
                            const idx = y * w + x;
                            if (scores[idx] > maxScore) { maxScore = scores[idx]; bestX = x; bestY = y; }
                        }
                    }
                    if (bestX !== -1 && maxScore > 0.05) selectedPoints.push({ x: bestX, y: bestY, score: maxScore });
                }
            }

            // Mark matched voxels as highlighted and create label anchors
            console.log(`Auto-Sample: Found ${selectedPoints.length} candidate points`);
            clearSampleMarkers();
            showCrosshair(null);

            selectedPoints.forEach((pt, i) => {
                addSamplePoint(pt.x, pt.y, data, w, h);
            });
            console.log(`Auto-Sample: Total highlighted voxels: ${highlightedVoxelIndices.size}`);

            // Auto-enable highlight mode
            highlightMode = true;
            const highlightToggleBtn = document.getElementById('highlight-toggle-btn');
            if (highlightToggleBtn) highlightToggleBtn.textContent = 'Highlight Sampled Voxels: ON';
            updateVoxels();
        });

        // --- Subtractive Mixing Logic ---
        function mixColors(pigmentsWithWeights) {
            const eps = 0.001;
            let sumLogR = 0, sumLogG = 0, sumLogB = 0, totalW = 0;
            for (const pw of pigmentsWithWeights) {
                const rgb = pw.rgb, w = pw.weight;
                sumLogR += w * Math.log(Math.max(rgb[0]/255.0, eps));
                sumLogG += w * Math.log(Math.max(rgb[1]/255.0, eps));
                sumLogB += w * Math.log(Math.max(rgb[2]/255.0, eps));
                totalW += w;
            }
            if (totalW > 0) { sumLogR /= totalW; sumLogG /= totalW; sumLogB /= totalW; }
            return [
                Math.round(Math.exp(sumLogR) * 255),
                Math.round(Math.exp(sumLogG) * 255),
                Math.round(Math.exp(sumLogB) * 255)
            ];
        }

        function generateWeightCombinations(M) {
            let S = 10;
            if (M === 2) S = 40;
            else if (M === 3) S = 20;
            else if (M === 4) S = 8;
            else if (M === 5) S = 5;
            else if (M === 6) S = 4;
            else S = 3;

            const combos = [];
            function recurse(index, currentSum, currentWeights) {
                if (index === M - 1) {
                    currentWeights.push((S - currentSum) / S);
                    combos.push([...currentWeights]);
                    currentWeights.pop();
                    return;
                }
                for (let w = 0; w <= S - currentSum; w++) {
                    currentWeights.push(w / S);
                    recurse(index + 1, currentSum + w, currentWeights);
                    currentWeights.pop();
                }
            }
            recurse(0, 0, []);
            return combos;
        }

        function computeRecoloredImage(srcData, achievableGamut, w, h) {
            const resultData = new Uint8ClampedArray(srcData.length);
            const errors = new Float32Array(w * h);
            for (let i = 0; i < w * h; i++) {
                const idx = i * 4;
                const r = srcData[idx], g = srcData[idx+1], b = srcData[idx+2], a = srcData[idx+3];
                const pixelLab = fastSRGBToLab(r, g, b);
                let bestRGB = null, bestDist = Infinity;
                for (let j = 0; j < achievableGamut.length; j++) {
                    const gc = achievableGamut[j];
                    const d = Math.pow(gc.lab[0]-pixelLab[0],2) + Math.pow(gc.lab[1]-pixelLab[1],2) + Math.pow(gc.lab[2]-pixelLab[2],2);
                    if (d < bestDist) { bestDist = d; bestRGB = gc.rgb; }
                }
                resultData[idx] = bestRGB[0]; resultData[idx+1] = bestRGB[1];
                resultData[idx+2] = bestRGB[2]; resultData[idx+3] = a;
                errors[i] = Math.sqrt(bestDist);
            }
            return { imageData: new ImageData(resultData, w, h), errors };
        }

        function errorToRGB(error) {
            const t = Math.min(1.0, error / 40.0);
            let r = 0, g = 0;
            if (t < 0.5) { r = Math.round(t * 2 * 255); g = 255; }
            else { r = 255; g = Math.round((1 - (t - 0.5) * 2) * 255); }
            return [r, g, 0];
        }

        function generateAccuracyHeatmap(recoloredImageData, errors) {
            const w = recoloredImageData.width, h = recoloredImageData.height;
            const src = recoloredImageData.data;
            const heat = new Uint8ClampedArray(src.length);
            for (let i = 0; i < w * h; i++) {
                const idx = i * 4;
                const [hr, hg, hb] = errorToRGB(errors[i]);
                heat[idx] = Math.round(0.7 * hr + 0.3 * src[idx]);
                heat[idx+1] = Math.round(0.7 * hg + 0.3 * src[idx+1]);
                heat[idx+2] = Math.round(0.7 * hb + 0.3 * src[idx+2]);
                heat[idx+3] = 255;
            }
            return new ImageData(heat, w, h);
        }

        function syncPigmentUI() {
            if (syncingPigments) return;
            syncingPigments = true;

            // Sync checkboxes from shared state
            document.querySelectorAll('.pigment-mix-checkbox').forEach(cb => {
                const idx = parseInt(cb.value);
                cb.checked = pinnedPigments.has(idx);
            });

            // Sync 3D pins from shared state
            pigmentBoxes.forEach((marker, idx) => {
                const shouldBePinned = pinnedPigments.has(idx);
                if (marker.userData.state.pinned !== shouldBePinned) {
                    marker.userData.state.pinned = shouldBePinned;
                    marker.userData.updateVisibility();
                }
            });

            updateMixShape();
            if (typeof updatePigmentBoxVisibility === 'function') updatePigmentBoxVisibility();
            updatePigmentPreview();

            syncingPigments = false;
        }

        function updatePigmentPreview() {
            if (!originalImageData) return;
            const selectedIndices = Array.from(pinnedPigments);
            if (selectedIndices.length === 0) {
                recoloredImageData = null; heatmapImageData = null; errorsData = null;
                toggleViewBtn.style.display = 'none';
                accuracyContainer.style.display = 'none';
                updatePreviewDisplay();
                return;
            }

            const allPigments = selectedIndices.map(idx => ({
                name: pigmentsList[idx].name,
                rgb: hexToRGB(pigmentsList[idx].hex)
            }));

            // Build LUT from all non-empty subsets (guarantees monotonic Delta E)
            const lutMap = new Map();
            const N = allPigments.length;

            // Cache weight combos by subset size
            const comboCache = {};
            function getCombos(k) {
                if (!comboCache[k]) comboCache[k] = generateWeightCombinations(k);
                return comboCache[k];
            }

            function addToLUT(rgb) {
                const lab = sRGB_to_Lab(rgb[0], rgb[1], rgb[2]);
                const key = `${Math.round(lab[0])},${Math.round(lab[1])},${Math.round(lab[2])}`;
                if (!lutMap.has(key)) lutMap.set(key, { rgb, lab });
            }

            // If only one pigment, include white+black for tints/shades (original behavior)
            if (N === 1) {
                const triad = [
                    allPigments[0],
                    { rgb: hexToRGB("#F5F5F0") },
                    { rgb: hexToRGB("#1C1C1C") }
                ];
                const combos = getCombos(3);
                for (const weights of combos) {
                    const mixedRGB = mixColors(triad.map((p, idx) => ({ rgb: p.rgb, weight: weights[idx] })));
                    addToLUT(mixedRGB);
                }
                // Also add pure pigment alone
                addToLUT(allPigments[0].rgb);
            } else {
                // All non-empty subsets via bitmask
                for (let mask = 1; mask < (1 << N); mask++) {
                    const subset = [];
                    for (let i = 0; i < N; i++) {
                        if (mask & (1 << i)) subset.push(allPigments[i]);
                    }
                    const k = subset.length;
                    if (k === 1) {
                        addToLUT(subset[0].rgb);
                    } else {
                        const combos = getCombos(k);
                        for (const weights of combos) {
                            const mixedRGB = mixColors(subset.map((p, idx) => ({ rgb: p.rgb, weight: weights[idx] })));
                            addToLUT(mixedRGB);
                        }
                    }
                }
            }

            const achievableGamut = Array.from(lutMap.values());

            const result = computeRecoloredImage(originalImageData.data, achievableGamut, originalImageData.width, originalImageData.height);
            recoloredImageData = result.imageData;
            errorsData = result.errors;
            heatmapImageData = generateAccuracyHeatmap(recoloredImageData, errorsData);

            toggleViewBtn.style.display = 'block';
            toggleViewBtn.textContent = 'Show Original';
            accuracyContainer.style.display = 'flex';
            updatePreviewDisplay();
        }

        // Populate pigment checklist
        pigmentsList.forEach((pigment, idx) => {
            const label = document.createElement('label');
            label.style.cssText = 'display:flex;align-items:center;gap:6px;font-size:12px;margin-bottom:4px;font-weight:normal;cursor:pointer;';
            const cb = document.createElement('input');
            cb.type = 'checkbox'; cb.value = idx; cb.className = 'pigment-mix-checkbox';
            const swatch = document.createElement('span');
            swatch.style.cssText = `display:inline-block;width:12px;height:12px;background-color:${pigment.hex};border:1px solid #555;border-radius:2px;flex-shrink:0;`;
            label.appendChild(cb);
            label.appendChild(swatch);
            label.appendChild(document.createTextNode(pigment.name));
            checklistContainer.appendChild(label);
            cb.addEventListener('change', () => {
                if (syncingPigments) return;
                if (cb.checked) pinnedPigments.add(idx);
                else pinnedPigments.delete(idx);
                syncPigmentUI();
            });
        });

        pigmentPreviewBtn.addEventListener('click', () => {
            const isHidden = checklistContainer.style.display === 'none';
            checklistContainer.style.display = isHidden ? 'block' : 'none';
        });

        // UI Controls logic
        const viewBtn = document.getElementById('view-btn');
        const resetBtn = document.getElementById('reset-btn');
        const toggleMixBtn = document.getElementById('toggle-mix-btn');
        const hideUnpinnedBtn = document.getElementById('hide-unpinned-btn');
        const valueSlider = document.getElementById('value-slider');
        const valueLabel = document.getElementById('value-label');
        const transparencySlider = document.getElementById('transparency-slider');
        const transparencyLabel = document.getElementById('transparency-label');

        let isTopView = false;
        viewBtn.addEventListener('click', (e) => {
            isTopView = !isTopView;
            if (isTopView) {
                camera.position.set(0, 100, 0.001); 
                controls.target.set(0, 15, 0);
            } else {
                camera.position.set(100, 0, 0);
                controls.target.set(0, 15, 0);
            }
            controls.update();
        });

        resetBtn.addEventListener('click', () => {
            pinnedPigments.clear();
            syncPigmentUI();
        });

        toggleMixBtn.addEventListener('click', () => {
            isMixVisible = !isMixVisible;
            updateMixShape();
        });

        let hideUnpinned = false;
        function updatePigmentBoxVisibility() {
            pigmentBoxes.forEach(box => {
                if (hideUnpinned) {
                    box.visible = box.userData.state.pinned;
                } else {
                    box.visible = true;
                }
            });
        }

        hideUnpinnedBtn.addEventListener('click', () => {
            hideUnpinned = !hideUnpinned;
            if (hideUnpinned) {
                document.getElementById('eye-icon').style.display = 'none';
                document.getElementById('eye-slash-icon').style.display = 'block';
                hideUnpinnedBtn.title = "Show Unpinned Pigments";
            } else {
                document.getElementById('eye-icon').style.display = 'block';
                document.getElementById('eye-slash-icon').style.display = 'none';
                hideUnpinnedBtn.title = "Hide Unpinned Pigments";
            }
            updatePigmentBoxVisibility();
        });

        const highlightToggleBtn = document.getElementById('highlight-toggle-btn');
        highlightToggleBtn.addEventListener('click', () => {
            highlightMode = !highlightMode;
            highlightToggleBtn.textContent = highlightMode ? 'Highlight Sampled Voxels: ON' : 'Highlight Sampled Voxels: OFF';
            updateVoxels();
        });

        function updateVoxels() {
            const cutoffValue = parseInt(valueSlider.value);
            const transparency = parseInt(transparencySlider.value) / 100.0;
            const baseOpacity = 1.0 - transparency;
            const samplesExist = highlightedVoxelIndices.size > 0;
            
            if (highlightMode) {
                console.log(`Updating voxels (Highlight Mode ON): samplesExist=${samplesExist}, count=${highlightedVoxelIndices.size}`);
            }

            cubes.forEach((cube, idx) => {
                const visibleByValue = cube.userData.V <= cutoffValue;
                const highlightMultiplier = (highlightMode && samplesExist) ? 0.2 : 1.0;
                const opacity = baseOpacity * highlightMultiplier;
                
                cube.visible = visibleByValue && opacity > 0;
                cube.material.depthWrite = (opacity > 0.95);
                cube.material.opacity = opacity;
            });

            hueAnchors.forEach(div => {
                div.style.opacity = baseOpacity;
            });
        }

        valueSlider.addEventListener('input', () => {
            valueLabel.innerText = valueSlider.value;
            updateVoxels();
        });

        transparencySlider.addEventListener('input', () => {
            transparencyLabel.innerText = transparencySlider.value;
            updateVoxels();
        });

        // Initialize
        syncPigmentUI();
        updateVoxels();

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
            labelRenderer.setSize(window.innerWidth, window.innerHeight);
        });

        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            try {
                const dist = camera.position.distanceTo(controls.target);
                if (window.lastDist !== undefined && Math.abs(dist - window.lastDist) > 0.5) {
                    console.log(`ZOOM_ANIMATE dist=${dist.toFixed(2)} prev=${window.lastDist.toFixed(2)} step=${(dist-window.lastDist).toFixed(2)}`);
                }
                window.lastDist = dist;
                renderer.render(scene, camera);
                labelRenderer.render(scene, camera);
            } catch(e) {
                console.error('Render error:', e);
            }
        }

        animate();
    </script>
</body>
</html>
"""

with open('munsell_3-3.csv', 'r') as f:
    csv_data = f.read()

final_html = html_template.replace('{{CSV_DATA}}', csv_data)

with open('index.html', 'w') as f:
    f.write(final_html)

print("Generated index.html successfully.")
