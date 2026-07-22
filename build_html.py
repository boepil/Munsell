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
        .optimal-axis-label {
            position: fixed;
            color: rgba(255, 255, 255, 0.9);
            font: 12px sans-serif;
            text-shadow: 0 1px 3px #000;
            pointer-events: none;
            transform: translate(6px, -50%);
            white-space: nowrap;
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
        
        <div style="margin-bottom: 15px;">
            <label style="font-weight: normal; cursor: pointer; display: flex; align-items: center; gap: 6px;">
                <input type="checkbox" id="toggle-envelope" checked> Show Natural Envelope
            </label>
            <label style="font-weight: normal; cursor: pointer; display: flex; align-items: center; gap: 6px; margin-top: 5px;">
                <input type="checkbox" id="toggle-munsell"> Show Munsell Solid
            </label>
            <label style="font-weight: normal; cursor: pointer; display: flex; align-items: center; gap: 6px; margin-top: 5px;">
                <input type="checkbox" id="toggle-optimal" checked> Optimal Color Solid (MacAdam Limits)
            </label>
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

        const naturalData = `{{NATURAL_DATA}}`;
        let naturalLights = [];
        try {
            naturalLights = JSON.parse(naturalData);
        } catch (e) {
            console.error("No natural light data found");
        }


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
            { name: "Titanium White",              code: "PW6",    munsell: "N 9.5/" },
            { name: "Carbon Black",                code: "PBk6",   munsell: "N 1.5/" },
            { name: "Hansa Yellow",                code: "PY97",   munsell: "2.5Y 8.0/12.0" },
            { name: "Lemon Yellow",                code: "mix",    munsell: "5Y 8.5/10.0" },
            { name: "Cadmium Yellow",              code: "PY35",   munsell: "2.5Y 8.0/14.0" },
            { name: "Yellow Ochre",                code: "PY43",   munsell: "10YR 6.5/6.0" },
            { name: "Raw Sienna",                  code: "PBr7",   munsell: "7.5YR 5.5/5.0" },
            { name: "Cadmium Orange",              code: "PO20",   munsell: "2.5YR 6.5/14.0" },
            { name: "Quinacridone Red",            code: "PR209",  munsell: "2.5R 4.5/13.0" },
            { name: "Cadmium Red Deep",            code: "PR108",  munsell: "7.5R 4.5/15.0" },
            { name: "Quinacridone Red Light",      code: "PR206/207", munsell: "5R 5.0/14.0" },
            { name: "Alizarin Crimson",            code: "PR83",   munsell: "5RP 3.0/9.0" },
            { name: "Venetian Red",                code: "PR101",  munsell: "10R 4.5/10.0" },
            { name: "Burnt Sienna",                code: "PBr7",   munsell: "2.5YR 4.0/8.0" },
            { name: "Burnt Umber",                 code: "PBr7",   munsell: "5YR 3.0/4.0" },
            { name: "Raw Umber",                   code: "PBr7",   munsell: "2.5Y 4.0/3.0" },
            { name: "Sepia",                       code: "mixture",munsell: "10YR 2.5/2.0" },
            { name: "Payne's Grey",                code: "mixture",munsell: "5PB 3.0/2.0" },
            { name: "Quinacridone Rose",           code: "PV19",   munsell: "5RP 5.0/12.0" },
            { name: "Quinacridone Magenta",        code: "PR122",  munsell: "5P 4.5/13.0" },
            { name: "Cobalt Violet",               code: "PV49",   munsell: "7.5P 4.0/8.0" },
            { name: "Ultramarine Violet",          code: "PV15",   munsell: "5P 3.5/9.0" },
            { name: "Phthalo Green BS",            code: "PG7",    munsell: "2.5BG 4.0/10.0" },
            { name: "Viridian",                    code: "PG18",   munsell: "10G 4.5/6.0" },
            { name: "Chromium Oxide Green",        code: "PG17",   munsell: "5G 5.0/4.0" },
            { name: "Phthalo Green YS",            code: "PG36",   munsell: "7.5GY 4.5/10.0" },
            { name: "Phthalo Turquoise",           code: "PB16",   munsell: "5BG 5.0/9.0" },
            { name: "Cerulean Blue",               code: "PB35",   munsell: "10B 6.0/8.0" },
            { name: "Prussian Blue",               code: "PB27",   munsell: "2.5PB 2.5/8.0" },
            { name: "Phthalo Blue GS",             code: "PB15:3", munsell: "2.5PB 3.5/12.0" },
            { name: "Cobalt Blue",                 code: "PB28",   munsell: "5PB 4.5/9.0" },
            { name: "Ultramarine Blue",            code: "PB29",   munsell: "5PB 3.5/11.0" },
        ];

        function parseMunsell(str) {
            const s = str.replace(/^≈/, '').trim();
            if (s.startsWith('N ')) {
                const m = s.match(/^N\s+([\d.]+)\s*\/\s*([\d.]*)$/);
                if (!m) return null;
                return { neutral: true, V: parseFloat(m[1]), C: parseFloat(m[2] || "0") };
            }
            const m = s.match(/^([\d.]+)\s*([A-Z]+)\s+([\d.]+)\s*\/\s*([\d.]*)$/);
            if (!m) return null;
            return { neutral: false, hueNum: parseFloat(m[1]), hueLetter: m[2], V: parseFloat(m[3]), C: parseFloat(m[4] || "0") };
        }

        const hueNames = ['R','YR','Y','GY','G','BG','B','PB','P','RP'];

        function hueToFractionalIndex(num, letter) {
            const baseIdx = hueNames.indexOf(letter);
            if (baseIdx === -1) return -1;
            return baseIdx * 4 + (num - 2.5) / 2.5;
        }

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
            const H = parts[0].replace(/\.0([A-Z]+)$/, '$1');
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
        console.log('DEBUG: CSV loaded, chips:', munsellColors.length);
        console.log('DEBUG: 10Y chips:', munsellColors.filter(c => c.H === '10Y').length);

        function findNearestMunsell(r, g, b) {
            const targetLab = sRGB_to_Lab(r, g, b);
            let best = null, bestDist = Infinity;
            for (const entry of munsellColors) {
                const d = Math.pow(entry.lab[0]-targetLab[0], 2) + Math.pow(entry.lab[1]-targetLab[1], 2) + Math.pow(entry.lab[2]-targetLab[2], 2);
                if (d < bestDist) { bestDist = d; best = entry; }
            }
            return best;
        }

        // Pre-compute voxel chip 3D positions for pigment snapping
        munsellColors.forEach(color => {
            const yPos = color.V * 3;
            let xPos = 0, zPos = 0;
            if (color.C > 0 && color.hueIndex !== -1) {
                const angle = (color.hueIndex / 40.0) * Math.PI * 2;
                const radius = color.C * 1.5;
                xPos = Math.cos(angle) * radius;
                zPos = -Math.sin(angle) * radius;
            }
            color.xPos = xPos; color.yPos = yPos; color.zPos = zPos;
        });

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

        // Compute pigment positions and colors from Munsell data
        pigmentsList.forEach(p => {
            const parsed = parseMunsell(p.munsell);
            if (!parsed) return;
            // Find nearest chip by H, V, C
            let best = null, bestDist = Infinity;
            const targetIdx = hueToFractionalIndex(parsed.hueNum, parsed.hueLetter);
            for (const chip of munsellColors) {
                let dh = 0;
                if (parsed.neutral) {
                    if (chip.C > 0) continue;
                } else {
                    if (chip.hueIndex === -1) continue;
                    dh = Math.abs(targetIdx - chip.hueIndex);
                }
                const dv = Math.abs(chip.V - parsed.V);
                const dc = Math.abs(chip.C - parsed.C);
                const d = dh + dv * 3 + dc * 0.4;
                if (d < bestDist) { bestDist = d; best = chip; }
            }
            console.log('DEBUG: ' + p.name + ' targetIdx=' + targetIdx.toFixed(4) + ' best=' + (best ? best.H + ' V=' + best.V + ' C=' + best.C : 'NONE') + ' pos=(' + (best ? best.xPos.toFixed(2) : '0') + ',' + (best ? best.yPos.toFixed(2) : '0') + ',' + (best ? best.zPos.toFixed(2) : '0') + ')');
            // Snap pigment position to the nearest voxel chip position
            if (best) {
                p.xPos = best.xPos;
                p.yPos = best.yPos;
                p.zPos = best.zPos;
            } else {
                p.xPos = 0; p.yPos = 0; p.zPos = 0;
            }
            p.rgb = best ? best.rgb : (parsed.neutral ? (() => { const g = Math.round(parsed.V / 10 * 255); return [g, g, g]; })() : [128, 128, 128]);
            p.hex = '#' + p.rgb.map(v => v.toString(16).padStart(2, '0')).join('');
        });

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x333333);
        
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
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
        controls.enableZoom = false; // Disable default OrbitControls zoom to use our custom delicate one

        // Delicate custom zoom handler scaling with deltaY
        renderer.domElement.addEventListener('wheel', (e) => {
            e.preventDefault();
            const target = controls.target;
            const offset = new THREE.Vector3().subVectors(camera.position, target);
            const currentDist = offset.length();
            
            // Standard scroll notch is deltaY = 100.
            // 0.00015 sensitivity means a standard notch changes distance by 1.5%.
            const sensitivity = 0.00015;
            const factor = 1 + e.deltaY * sensitivity;
            
            let newDist = currentDist * factor;
            const minD = 5;
            const maxD = 800;
            if (newDist < minD) newDist = minD;
            if (newDist > maxD) newDist = maxD;
            
            offset.setLength(newDist);
            camera.position.copy(target).add(offset);
            controls.update();
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

        const shellGeometry = new THREE.BufferGeometry();
        const shellPositions = [];
        const shellIndices = [];
        const ringVertexIndices = [];
        const hueCount = hues.length;
        const bottomCenterIndex = 0;
        const topCenterIndex = 1;
        shellPositions.push(0, 0, 0);
        shellPositions.push(0, 30, 0);

        boundaryValues.forEach((value, valueIdx) => {
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
                color: new THREE.Color(0xe8e8e8),
                transparent: true,
                opacity: 0.08,
                roughness: 1.0,
                metalness: 0.0,
                side: THREE.DoubleSide,
                depthWrite: false
            });

            const shellMesh = new THREE.Mesh(shellGeometry, shellMaterial);
            shellMesh.renderOrder = -1;
            shellMesh.visible = false; // Hide Munsell envelope as requested
            solidGroup.add(shellMesh);
        }

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
            const rgb = pigment.rgb || [128, 128, 128];
            
            const markerMaterial = new THREE.MeshBasicMaterial({
                color: new THREE.Color(`rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`)
            });
            const marker = new THREE.Mesh(markerGeometry, markerMaterial);
            marker.position.set(pigment.xPos || 0, pigment.yPos || 0, pigment.zPos || 0);
            
            // Rotate marker to face outward
            if (pigment.zPos !== 0 || pigment.xPos !== 0) {
                marker.rotation.y = Math.atan2(-pigment.zPos, pigment.xPos);
            }

            // Create CSS2D Object — compact 1-line label
            const div = document.createElement('div');
            div.className = 'pigment-label';
            div.textContent = pigment.code + ' ' + pigment.name;

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

        
        // Build Natural Light Envelope Shell
        const maxC = Array.from({length: 12}, () => Array(40).fill(0));
        naturalLights.forEach(l => {
            if (l.V < 0.1 || l.C < 0.1) return;
            const v_int = Math.round(l.V);
            const h_int = Math.round(l.hIndex) % 40;
            if (v_int >= 1 && v_int <= 10) {
                maxC[v_int][h_int] = Math.max(maxC[v_int][h_int], l.C);
            }
        });

        // Gap filling per V level
        for (let v = 1; v <= 10; v++) {
            const nonEmpty = [];
            for (let h = 0; h < 40; h++) if (maxC[v][h] > 0) nonEmpty.push(h);
            if (nonEmpty.length === 0 || nonEmpty.length === 40) continue;
            
            for (let h = 0; h < 40; h++) {
                if (maxC[v][h] === 0) {
                    let left = h, right = h;
                    let leftDist = 0, rightDist = 0;
                    while (maxC[v][left] === 0) { left = (left - 1 + 40) % 40; leftDist++; }
                    while (maxC[v][right] === 0) { right = (right + 1) % 40; rightDist++; }
                    maxC[v][h] = (maxC[v][left] * rightDist + maxC[v][right] * leftDist) / (leftDist + rightDist);
                }
            }
        }

        // Extrapolate empty V levels
        let minV = 1, maxV = 10;
        while (minV <= 10 && maxC[minV].every(c => c === 0)) minV++;
        while (maxV >= 1 && maxC[maxV].every(c => c === 0)) maxV--;
        if (minV <= maxV) {
            for (let v = 1; v < minV; v++) {
                for (let h = 0; h < 40; h++) maxC[v][h] = maxC[minV][h] * (v / minV);
            }
            for (let v = maxV + 1; v <= 10; v++) {
                for (let h = 0; h < 40; h++) maxC[v][h] = maxC[maxV][h] * ((11 - v) / (11 - maxV));
            }
        }

        // Smoothing across H
        const smoothedC = Array.from({length: 12}, () => Array(40).fill(0));
        for (let v = 1; v <= 10; v++) {
            for (let h = 0; h < 40; h++) {
                let sum = 0;
                for (let i = -2; i <= 2; i++) sum += maxC[v][(h + i + 40) % 40];
                smoothedC[v][h] = sum / 5;
                const pigmentMax = boundaryChroma(h, v);
                smoothedC[v][h] = Math.max(smoothedC[v][h], pigmentMax + 2.0); // Envelop solid
            }
        }

        function getEnvelopeC(V, H) {
            if (V <= 0 || V >= 11) return 0;
            const v_lower = Math.floor(V);
            const v_upper = Math.ceil(V);
            const t = V - v_lower;
            if (v_lower === v_upper) return smoothedC[v_lower][H];
            return smoothedC[v_lower][H] * (1 - t) + smoothedC[v_upper][H] * t;
        }

        const envPositions = [];
        for (let v_grid = 0; v_grid <= 10; v_grid++) {
            const V = v_grid + 0.5;
            for (let h_grid = 0; h_grid <= 40; h_grid++) {
                const H = h_grid % 40;
                const radius = getEnvelopeC(V, H) * 1.5;
                const angle = (h_grid / 40.0) * Math.PI * 2;
                envPositions.push(Math.cos(angle) * radius, V * 3, -Math.sin(angle) * radius);
            }
        }

        const envQuads = [];
        for (let v_int = 1; v_int <= 10; v_int++) {
            const v_grid = v_int - 1;
            for (let h_int = 0; h_int < 40; h_int++) {
                const A = v_grid * 41 + h_int;
                const B = v_grid * 41 + (h_int + 1);
                const C = (v_grid + 1) * 41 + h_int;
                const D = (v_grid + 1) * 41 + (h_int + 1);
                envQuads.push({ V: v_int, H: h_int, indices: [A, B, C, B, D, C] });
            }
        }

        const envGeometry = new THREE.BufferGeometry();
        envGeometry.setAttribute('position', new THREE.Float32BufferAttribute(envPositions, 3));
        const initialIndices = [];
        envQuads.forEach(q => initialIndices.push(...q.indices));
        envGeometry.setIndex(initialIndices);
        envGeometry.computeVertexNormals();

        const envMaterial = new THREE.MeshStandardMaterial({
            color: 0xcccccc,
            transparent: true,
            opacity: 0.15,
            side: THREE.DoubleSide,
            depthWrite: false
        });
        const envMesh = new THREE.Mesh(envGeometry, envMaterial);
        envMesh.userData.isEnvelope = true;
        solidGroup.add(envMesh);

        // UI Listener for envelope
        const toggleEnvelope = document.getElementById('toggle-envelope');
        if (toggleEnvelope) {
            toggleEnvelope.addEventListener('change', () => {
                envMesh.visible = toggleEnvelope.checked;
            });
        }
        solidGroup.position.y = -15;
        pigmentsGroup.position.y = -15;
        mixGroup.position.y = -15;
        sampleLabelGroup.position.y = -15;

        // ------------------------------------------------------------------
        // Optimal Color Solid (Schrödinger / MacAdam limits)
        // ------------------------------------------------------------------
        // Independent continuous loft.  The pigment cubes and the natural
        // envelope remain untouched; this layer shares only their scene
        // origin, vertical Value scale, and hue-angle convention.
        const optimalColorGroup = new THREE.Group();
        optimalColorGroup.name = 'Optimal Color Solid (MacAdam Limits)';
        solidGroup.add(optimalColorGroup);

        const OPTIMAL_VALUE_SCALE = 3;
        const OPTIMAL_HUE_SEGMENTS = 120;
        const OPTIMAL_VALUE_RINGS = 40;
        const OPTIMAL_CHROMA_SCALE = 1.5;
        const optimalChromaProfile = [
            [0.0, 0.0], [0.5, 5.0], [1.0, 11.0], [1.5, 18.0],
            [2.0, 24.0], [2.5, 30.0], [3.0, 35.0], [3.5, 39.0],
            [4.0, 42.0], [4.5, 44.0], [5.0, 45.0], [5.5, 44.0],
            [6.0, 42.0], [6.5, 39.0], [7.0, 35.0], [7.5, 30.0],
            [8.0, 25.0], [8.5, 20.0], [9.0, 14.0], [9.5, 7.0],
            [10.0, 0.0]
        ];

        function optimalChromaAtValue(value) {
            const v = Math.max(0, Math.min(10, value));
            for (let i = 0; i < optimalChromaProfile.length - 1; i++) {
                const lower = optimalChromaProfile[i];
                const upper = optimalChromaProfile[i + 1];
                if (v >= lower[0] && v <= upper[0]) {
                    const t = (v - lower[0]) / (upper[0] - lower[0]);
                    const smoothT = t * t * (3 - 2 * t);
                    return (lower[1] + (upper[1] - lower[1]) * smoothT) * OPTIMAL_CHROMA_SCALE;
                }
            }
            return 0;
        }

        function optimalSurfaceColor(value, hueFraction) {
            const distanceToPoint = Math.min(value, 10 - value);
            const saturation = Math.min(1, Math.max(0, distanceToPoint / 1.6));
            const color = new THREE.Color().setHSL(hueFraction, 0.92 * saturation, 0.52);
            color.lerp(new THREE.Color(0x9299a1), 1 - saturation);
            return color;
        }

        const optimalPositions = [0, 0, 0];
        const optimalColors = [0.57, 0.60, 0.64];
        const optimalRingIndices = [];
        const optimalRingValues = [];
        for (let ringIndex = 1; ringIndex < OPTIMAL_VALUE_RINGS; ringIndex++) {
            const value = (ringIndex / OPTIMAL_VALUE_RINGS) * 10;
            const radius = optimalChromaAtValue(value);
            const ring = [];
            for (let hueIndex = 0; hueIndex < OPTIMAL_HUE_SEGMENTS; hueIndex++) {
                const angle = (hueIndex / OPTIMAL_HUE_SEGMENTS) * Math.PI * 2;
                const color = optimalSurfaceColor(value, hueIndex / OPTIMAL_HUE_SEGMENTS);
                ring.push(optimalPositions.length / 3);
                optimalPositions.push(Math.cos(angle) * radius, value * OPTIMAL_VALUE_SCALE, -Math.sin(angle) * radius);
                optimalColors.push(color.r, color.g, color.b);
            }
            optimalRingIndices.push(ring);
            optimalRingValues.push(value);
        }

        const optimalFaces = [];
        const optimalAllIndices = [];
        function addOptimalFace(a, b, c, lowerValue, upperValue, hueIndex) {
            optimalFaces.push({ indices: [a, b, c], lowerValue, upperValue, hueIndex });
            optimalAllIndices.push(a, b, c);
        }
        const firstOptimalRing = optimalRingIndices[0];
        for (let hueIndex = 0; hueIndex < OPTIMAL_HUE_SEGMENTS; hueIndex++) {
            const nextHueIndex = (hueIndex + 1) % OPTIMAL_HUE_SEGMENTS;
            addOptimalFace(0, firstOptimalRing[hueIndex], firstOptimalRing[nextHueIndex], 0, optimalRingValues[0], hueIndex);
        }
        for (let ringIndex = 0; ringIndex < optimalRingIndices.length - 1; ringIndex++) {
            const lowerRing = optimalRingIndices[ringIndex];
            const upperRing = optimalRingIndices[ringIndex + 1];
            const lowerValue = optimalRingValues[ringIndex];
            const upperValue = optimalRingValues[ringIndex + 1];
            for (let hueIndex = 0; hueIndex < OPTIMAL_HUE_SEGMENTS; hueIndex++) {
                const nextHueIndex = (hueIndex + 1) % OPTIMAL_HUE_SEGMENTS;
                const a = lowerRing[hueIndex];
                const b = lowerRing[nextHueIndex];
                const c = upperRing[hueIndex];
                const d = upperRing[nextHueIndex];
                addOptimalFace(a, b, c, lowerValue, upperValue, hueIndex);
                addOptimalFace(b, d, c, lowerValue, upperValue, hueIndex);
            }
        }
        const topOptimalIndex = optimalPositions.length / 3;
        optimalPositions.push(0, 10 * OPTIMAL_VALUE_SCALE, 0);
        optimalColors.push(0.57, 0.60, 0.64);
        const lastOptimalRing = optimalRingIndices[optimalRingIndices.length - 1];
        for (let hueIndex = 0; hueIndex < OPTIMAL_HUE_SEGMENTS; hueIndex++) {
            const nextHueIndex = (hueIndex + 1) % OPTIMAL_HUE_SEGMENTS;
            addOptimalFace(topOptimalIndex, lastOptimalRing[hueIndex], lastOptimalRing[nextHueIndex], optimalRingValues[optimalRingValues.length - 1], 10, hueIndex);
        }

        const optimalGeometry = new THREE.BufferGeometry();
        optimalGeometry.setAttribute('position', new THREE.Float32BufferAttribute(optimalPositions, 3));
        optimalGeometry.setAttribute('color', new THREE.Float32BufferAttribute(optimalColors, 3));
        optimalGeometry.setIndex(optimalAllIndices);
        optimalGeometry.computeVertexNormals();
        const optimalMaterial = new THREE.MeshStandardMaterial({
            vertexColors: true,
            transparent: true,
            opacity: 0.36,
            roughness: 0.86,
            metalness: 0.0,
            side: THREE.DoubleSide,
            depthWrite: false
        });
        const optimalSurface = new THREE.Mesh(optimalGeometry, optimalMaterial);
        optimalSurface.name = 'Optimal Color Surface';
        optimalColorGroup.add(optimalSurface);

        const optimalGridGroup = new THREE.Group();
        const optimalGridMaterial = new THREE.LineBasicMaterial({
            color: 0xe8edf2,
            transparent: true,
            opacity: 0.24,
            depthWrite: false,
            toneMapped: false
        });
        for (let value = 0.5; value < 10; value += 0.5) {
            const radius = optimalChromaAtValue(value);
            const points = [];
            for (let hueIndex = 0; hueIndex <= OPTIMAL_HUE_SEGMENTS; hueIndex++) {
                const angle = (hueIndex / OPTIMAL_HUE_SEGMENTS) * Math.PI * 2;
                points.push(new THREE.Vector3(Math.cos(angle) * radius, value * OPTIMAL_VALUE_SCALE, -Math.sin(angle) * radius));
            }
            const ring = new THREE.Line(new THREE.BufferGeometry().setFromPoints(points), optimalGridMaterial);
            ring.userData.value = value;
            optimalGridGroup.add(ring);
        }
        for (let hueIndex = 0; hueIndex < hues.length; hueIndex++) {
            const angle = (hueIndex / hues.length) * Math.PI * 2;
            const points = [];
            for (let sample = 0; sample <= OPTIMAL_VALUE_RINGS; sample++) {
                const value = (sample / OPTIMAL_VALUE_RINGS) * 10;
                const radius = optimalChromaAtValue(value);
                points.push(new THREE.Vector3(Math.cos(angle) * radius, value * OPTIMAL_VALUE_SCALE, -Math.sin(angle) * radius));
            }
            const radial = new THREE.Line(new THREE.BufferGeometry().setFromPoints(points), optimalGridMaterial);
            radial.userData.hueIndex = hueIndex;
            optimalGridGroup.add(radial);
        }
        optimalGridGroup.renderOrder = 1;
        optimalColorGroup.add(optimalGridGroup);

        const optimalAxisGroup = new THREE.Group();
        const optimalAxisMaterial = new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.72, depthWrite: false, toneMapped: false });
        optimalAxisGroup.add(new THREE.Line(
            new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, 10 * OPTIMAL_VALUE_SCALE, 0)]),
            optimalAxisMaterial
        ));
        const tickPositions = [];
        for (let value = 0; value <= 10; value++) {
            const y = value * OPTIMAL_VALUE_SCALE;
            tickPositions.push(-0.65, y, 0, 0.65, y, 0);
        }
        const tickGeometry = new THREE.BufferGeometry();
        tickGeometry.setAttribute('position', new THREE.Float32BufferAttribute(tickPositions, 3));
        optimalAxisGroup.add(new THREE.LineSegments(tickGeometry, optimalAxisMaterial));
        optimalAxisGroup.renderOrder = 2;
        optimalColorGroup.add(optimalAxisGroup);

        const optimalAxisLabels = document.createElement('div');
        optimalAxisLabels.id = 'optimal-axis-labels';
        optimalAxisLabels.style.cssText = 'position:fixed;inset:0;pointer-events:none;z-index:5;';
        document.body.appendChild(optimalAxisLabels);
        const optimalLabelNodes = [];
        for (let value = 0; value <= 10; value++) {
            const label = document.createElement('span');
            label.className = 'optimal-axis-label';
            label.textContent = String(value);
            optimalAxisLabels.appendChild(label);
            optimalLabelNodes.push({ value, node: label });
        }
        const optimalAxisTitle = document.createElement('span');
        optimalAxisTitle.className = 'optimal-axis-label';
        optimalAxisTitle.textContent = 'Value (V)';
        optimalAxisLabels.appendChild(optimalAxisTitle);

        function updateOptimalAxisLabels(show) {
            solidGroup.updateMatrixWorld(true);
            optimalLabelNodes.forEach(entry => {
                const point = new THREE.Vector3(0, entry.value * OPTIMAL_VALUE_SCALE, 0).applyMatrix4(solidGroup.matrixWorld).project(camera);
                const visible = show && point.z >= -1 && point.z <= 1;
                entry.node.style.display = visible ? 'block' : 'none';
                entry.node.style.left = `${(point.x * 0.5 + 0.5) * window.innerWidth}px`;
                entry.node.style.top = `${(-point.y * 0.5 + 0.5) * window.innerHeight}px`;
            });
            const titlePoint = new THREE.Vector3(0, 10 * OPTIMAL_VALUE_SCALE + 1, 0).applyMatrix4(solidGroup.matrixWorld).project(camera);
            optimalAxisTitle.style.display = show ? 'block' : 'none';
            optimalAxisTitle.style.left = `${(titlePoint.x * 0.5 + 0.5) * window.innerWidth}px`;
            optimalAxisTitle.style.top = `${(-titlePoint.y * 0.5 + 0.5) * window.innerHeight}px`;
        }

        function updateOptimalVisibility(cutoffValue, show) {
            optimalColorGroup.visible = show;
            if (!show) {
                updateOptimalAxisLabels(false);
                return;
            }
            const visibleIndices = [];
            optimalFaces.forEach(face => {
                if (face.lowerValue <= cutoffValue) visibleIndices.push(...face.indices);
            });
            optimalGeometry.setIndex(visibleIndices);
            optimalGridGroup.children.forEach(child => {
                if (child.userData.value !== undefined) child.visible = child.userData.value <= cutoffValue;
            });
            updateOptimalAxisLabels(true);
        }

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

            // Local variance in grayscale to prefer regions with tonal structure
            const variance = new Float32Array(w * h);
            let maxVariance = 0;
            for (let y = 2; y < h - 2; y++) {
                for (let x = 2; x < w - 2; x++) {
                    let sum = 0, sumSq = 0, count = 0;
                    for (let dy = -2; dy <= 2; dy++) {
                        for (let dx = -2; dx <= 2; dx++) {
                            const idx = (y + dy) * w + (x + dx);
                            const val = gray[idx];
                            sum += val;
                            sumSq += val * val;
                            count++;
                        }
                    }
                    const mean = sum / count;
                    const varVal = Math.max(0, sumSq / count - mean * mean);
                    variance[y * w + x] = varVal;
                    if (varVal > maxVariance) maxVariance = varVal;
                }
            }
            if (maxVariance > 0) for (let i = 0; i < variance.length; i++) variance[i] /= maxVariance;

            // Combined interest score
            const scores = new Float32Array(w * h);
            for (let i = 0; i < scores.length; i++) scores[i] = 0.35 * edge[i] + 0.30 * chroma[i] + 0.35 * variance[i];

            // Grid clustering with non-max suppression
            const gridRows = 6, gridCols = 8;
            const cellW = w / gridCols, cellH = h / gridRows;
            const selectedPoints = [];
            const suppressionRadiusSq = 18 * 18;
            function isTooClose(x, y, pts) {
                for (const pt of pts) {
                    const dx = pt.x - x;
                    const dy = pt.y - y;
                    if (dx * dx + dy * dy < suppressionRadiusSq) return true;
                }
                return false;
            }

            for (let r = 0; r < gridRows; r++) {
                for (let c = 0; c < gridCols; c++) {
                    const xStart = Math.floor(c * cellW), xEnd = Math.min(w, Math.floor((c+1)*cellW));
                    const yStart = Math.floor(r * cellH), yEnd = Math.min(h, Math.floor((r+1)*cellH));
                    const candidates = [];
                    for (let y = yStart; y < yEnd; y++) {
                        for (let x = xStart; x < xEnd; x++) {
                            const idx = y * w + x;
                            candidates.push({ x, y, score: scores[idx] });
                        }
                    }
                    candidates.sort((a, b) => b.score - a.score);
                    let picked = 0;
                    for (const candidate of candidates) {
                        if (candidate.score <= 0.05) break;
                        if (isTooClose(candidate.x, candidate.y, selectedPoints)) continue;
                        selectedPoints.push(candidate);
                        picked++;
                        if (picked >= 2) break;
                    }
                }
            }

            selectedPoints.sort((a, b) => b.score - a.score);

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
            const blendCount = Math.min(6, achievableGamut.length);
            const blendSigmaSq = 225;
            for (let i = 0; i < w * h; i++) {
                const idx = i * 4;
                const r = srcData[idx], g = srcData[idx+1], b = srcData[idx+2], a = srcData[idx+3];
                const pixelLab = fastSRGBToLab(r, g, b);
                const nearest = [];
                for (let j = 0; j < achievableGamut.length; j++) {
                    const gc = achievableGamut[j];
                    const d = Math.pow(gc.lab[0]-pixelLab[0],2) + Math.pow(gc.lab[1]-pixelLab[1],2) + Math.pow(gc.lab[2]-pixelLab[2],2);
                    if (nearest.length < blendCount) {
                        nearest.push({ d, rgb: gc.rgb });
                        nearest.sort((left, right) => right.d - left.d);
                    } else if (d < nearest[0].d) {
                        nearest[0] = { d, rgb: gc.rgb };
                        nearest.sort((left, right) => right.d - left.d);
                    }
                }
                nearest.sort((left, right) => left.d - right.d);

                let outR = 0, outG = 0, outB = 0, sumW = 0;
                if (nearest.length === 0) {
                    outR = r; outG = g; outB = b;
                } else if (nearest[0].d < 1e-6) {
                    outR = nearest[0].rgb[0];
                    outG = nearest[0].rgb[1];
                    outB = nearest[0].rgb[2];
                } else {
                    for (const candidate of nearest) {
                        const weight = Math.exp(-candidate.d / (2 * blendSigmaSq));
                        sumW += weight;
                        outR += weight * candidate.rgb[0];
                        outG += weight * candidate.rgb[1];
                        outB += weight * candidate.rgb[2];
                    }
                    if (sumW > 0) {
                        outR /= sumW; outG /= sumW; outB /= sumW;
                    }
                }

                resultData[idx] = Math.round(outR); resultData[idx+1] = Math.round(outG);
                resultData[idx+2] = Math.round(outB); resultData[idx+3] = a;
                const blendedLab = sRGB_to_Lab(resultData[idx], resultData[idx+1], resultData[idx+2]);
                errors[i] = Math.sqrt(
                    Math.pow(blendedLab[0] - pixelLab[0], 2) +
                    Math.pow(blendedLab[1] - pixelLab[1], 2) +
                    Math.pow(blendedLab[2] - pixelLab[2], 2)
                );
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
            const showMunsell = toggleMunsell ? toggleMunsell.checked : true;
            pigmentBoxes.forEach(box => {
                if (!showMunsell) {
                    box.visible = false;
                    box.userData.labelObj.visible = false;
                    return;
                }
                if (hideUnpinned) {
                    box.visible = box.userData.state.pinned;
                } else {
                    box.visible = true;
                }
                box.userData.updateVisibility();
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

        const toggleMunsell = document.getElementById('toggle-munsell');
        const toggleOptimal = document.getElementById('toggle-optimal');
        if (toggleMunsell) {
            toggleMunsell.addEventListener('change', () => {
                updateVoxels();
                updatePigmentBoxVisibility();
            });
        }
        if (toggleOptimal) {
            toggleOptimal.addEventListener('change', () => {
                updateOptimalVisibility(parseInt(valueSlider.value), toggleOptimal.checked);
            });
        }

        function updateVoxels() {
            const cutoffValue = parseInt(valueSlider.value);
            const transparency = parseInt(transparencySlider.value) / 100.0;
            const baseOpacity = 1.0 - transparency;
            const samplesExist = highlightedVoxelIndices.size > 0;
            const showMunsell = toggleMunsell ? toggleMunsell.checked : true;
            
            if (highlightMode) {
                console.log(`Updating voxels (Highlight Mode ON): samplesExist=${samplesExist}, count=${highlightedVoxelIndices.size}`);
            }

            cubes.forEach((cube, idx) => {
                const visibleByValue = cube.userData.V <= cutoffValue;
                const highlightMultiplier = (highlightMode && samplesExist) ? 0.2 : 1.0;
                const opacity = baseOpacity * highlightMultiplier;
                
                cube.visible = showMunsell && visibleByValue && opacity > 0;
                cube.material.depthWrite = (opacity > 0.95);
                cube.material.opacity = opacity;
            });

            updateOptimalVisibility(cutoffValue, toggleOptimal ? toggleOptimal.checked : true);

            hueAnchors.forEach(div => {
                div.style.opacity = showMunsell ? baseOpacity : 0;
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

with open('munsell_3-3.csv', 'r', encoding='utf-8') as f:
    csv_data = f.read()

try:
    with open('natural_lights.json', 'r', encoding='utf-8') as f:
        natural_data = f.read()
except FileNotFoundError:
    natural_data = "[]"

final_html = html_template.replace('{{CSV_DATA}}', csv_data).replace('{{NATURAL_DATA}}', natural_data)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print("Generated index.html successfully.")
