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
            width: 100%;
            padding: 8px;
            margin-bottom: 15px;
            background: #555;
            color: #fff;
            border: 1px solid #777;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover {
            background: #666;
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
        .pigment-label:hover {
            border-color: #fff;
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
        <button id="view-btn">Toggle View (Top / Side)</button>
        <button id="reset-btn" style="margin-bottom: 15px;">Reset Labels</button>
        <button id="toggle-mix-btn" style="margin-bottom: 15px;">Toggle Mix Shape</button>
        <button id="hide-unpinned-btn" style="margin-bottom: 15px;">Hide Unpinned Pigments</button>
        
        <div style="margin-bottom: 15px;">
            <label>Max Value: <span id="value-label">10</span></label>
            <input type="range" id="value-slider" min="1" max="10" step="1" value="10">
        </div>
        
        <div>
            <label>Transparency: <span id="transparency-label">0</span>%</label>
            <input type="range" id="transparency-slider" min="0" max="100" step="1" value="0">
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
        scene.add(solidGroup);
        scene.add(pigmentsGroup);
        scene.add(mixGroup);

        const boxGeometry = new THREE.BoxGeometry(1.4, 2.8, 1.4);
        const cubes = [];

        // Build Voxels
        munsellColors.forEach(color => {
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
            mesh.userData = { V: color.V };
            if (color.C > 0 && hIndex !== -1) mesh.rotation.y = (hIndex / 40.0) * Math.PI * 2;
            
            cubes.push(mesh);
            solidGroup.add(mesh);
        });

        const pigmentBoxes = [];

        // Build Pigments
        const markerGeometry = new THREE.BoxGeometry(1.6, 3.2, 1.6);
        pigmentsList.forEach(pigment => {
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
            
            // Clicking label unpins it (and pins it if not pinned, but we know it must be visible to click it)
            // Stop propagation to prevent window raycast from double toggling
            div.addEventListener('mousedown', (e) => e.stopPropagation());
            div.addEventListener('mouseup', (e) => {
                e.stopPropagation();
                marker.userData.state.pinned = !marker.userData.state.pinned;
                marker.userData.updateVisibility();
                updateMixShape();
                if (typeof updatePigmentBoxVisibility === 'function') updatePigmentBoxVisibility();
            });

            pigmentBoxes.push(marker);
            pigmentsGroup.add(marker);
        });

        solidGroup.position.y = -15;
        pigmentsGroup.position.y = -15;
        mixGroup.position.y = -15;

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
            const intersects = raycaster.intersectObjects(pigmentBoxes);
            
            // Reset all voxel hovers
            pigmentBoxes.forEach(box => {
                box.userData.state.hoveredVoxel = false;
            });
            
            if (intersects.length > 0) {
                const box = intersects[0].object;
                box.userData.state.hoveredVoxel = true;
            }
            
            pigmentBoxes.forEach(box => box.userData.updateVisibility());
        });

        window.addEventListener('mouseup', (event) => {
            if (isDragging) return;
            
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
            
            raycaster.setFromCamera(mouse, camera);
            
            // Check boxes (to toggle)
            const intersects = raycaster.intersectObjects(pigmentBoxes);
            if (intersects.length > 0) {
                const marker = intersects[0].object;
                marker.userData.state.pinned = !marker.userData.state.pinned;
                marker.userData.updateVisibility();
                updateMixShape();
                if (typeof updatePigmentBoxVisibility === 'function') updatePigmentBoxVisibility();
            }
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
                controls.target.set(0, 0, 0);
            } else {
                camera.position.set(100, 0, 0);
                controls.target.set(0, 0, 0);
            }
            controls.update();
        });

        resetBtn.addEventListener('click', () => {
            pigmentBoxes.forEach(marker => {
                marker.userData.state.pinned = false;
                marker.userData.updateVisibility();
            });
            updateMixShape();
            if (typeof updatePigmentBoxVisibility === 'function') updatePigmentBoxVisibility();
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
            hideUnpinnedBtn.innerText = hideUnpinned ? "Show Unpinned Pigments" : "Hide Unpinned Pigments";
            updatePigmentBoxVisibility();
        });

        function updateVoxels() {
            const cutoffValue = parseInt(valueSlider.value);
            const transparency = parseInt(transparencySlider.value) / 100.0;
            const opacity = 1.0 - transparency;

            cubes.forEach(cube => {
                cube.visible = cube.userData.V <= cutoffValue && opacity > 0;
                cube.material.depthWrite = (opacity > 0.95); 
                cube.material.opacity = opacity;
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
            renderer.render(scene, camera);
            labelRenderer.render(scene, camera);
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
