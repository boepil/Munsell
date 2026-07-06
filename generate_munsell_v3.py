import json

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Munsell Color Solid with Pigments (v3)</title>
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
            z-index: 10;
            width: 300px;
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
    <div id="controls">
        <div style="margin-bottom: 15px;">
            <label>Value Cutoff: <span id="value-label">1</span></label>
            <input type="range" id="value-slider" min="1" max="10" step="1" value="1">
        </div>
        
        <div>
            <label>Transparency: <span id="transparency-label">0</span>%</label>
            <input type="range" id="transparency-slider" min="0" max="100" step="1" value="0">
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
        scene.add(solidGroup);
        scene.add(pigmentsGroup);

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
                depthWrite: true // Important for transparency sorting
            });
            
            const mesh = new THREE.Mesh(boxGeometry, material);
            mesh.position.set(xPos, yPos, zPos);
            mesh.userData = { V: color.V };
            if (color.C > 0 && hIndex !== -1) mesh.rotation.y = (hIndex / 40.0) * Math.PI * 2;
            
            cubes.push(mesh);
            solidGroup.add(mesh);
        });

        // Function to create text sprites
        function createTextSprite(message) {
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            const fontSize = 28;
            context.font = "Bold " + fontSize + "px Arial";
            const metrics = context.measureText(message);
            const textWidth = metrics.width;
            
            canvas.width = textWidth + 24;
            canvas.height = fontSize + 20;
            
            context.fillStyle = "rgba(0, 0, 0, 0.7)";
            context.beginPath();
            context.roundRect(0, 0, canvas.width, canvas.height, 8);
            context.fill();
            
            context.fillStyle = "rgba(255, 255, 255, 1.0)";
            context.font = "Bold " + fontSize + "px Arial";
            context.textAlign = "center";
            context.textBaseline = "middle";
            context.fillText(message, canvas.width / 2, canvas.height / 2);
            
            const texture = new THREE.CanvasTexture(canvas);
            texture.minFilter = THREE.LinearFilter;
            const spriteMaterial = new THREE.SpriteMaterial({ map: texture, depthTest: false, depthWrite: false });
            const sprite = new THREE.Sprite(spriteMaterial);
            
            const scale = 0.08;
            sprite.scale.set(canvas.width * scale, canvas.height * scale, 1);
            sprite.userData = { width: canvas.width * scale, height: canvas.height * scale };
            return sprite;
        }

        const pigmentData = [];

        // Build Pigments
        const markerGeometry = new THREE.SphereGeometry(0.5, 16, 16);
        pigmentsList.forEach(pigment => {
            const rgb = hexToRGB(pigment.hex);
            const nearest = findNearestMunsell(rgb[0], rgb[1], rgb[2]);
            
            const markerMaterial = new THREE.MeshStandardMaterial({
                color: new THREE.Color(`rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`),
                roughness: 0.2, metalness: 0.5
            });
            const marker = new THREE.Mesh(markerGeometry, markerMaterial);
            const basePos = new THREE.Vector3(nearest.xPos, nearest.yPos, nearest.zPos);
            marker.position.copy(basePos);
            pigmentsGroup.add(marker);

            const sprite = createTextSprite(pigment.name);
            pigmentsGroup.add(sprite);

            const lineMaterial = new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.5 });
            const lineGeometry = new THREE.BufferGeometry().setFromPoints([basePos, basePos]);
            const line = new THREE.Line(lineGeometry, lineMaterial);
            pigmentsGroup.add(line);

            pigmentData.push({
                basePos: basePos,
                marker: marker,
                sprite: sprite,
                line: line,
                currentPos: new THREE.Vector3()
            });
        });

        solidGroup.position.y = -15;
        pigmentsGroup.position.y = -15;

        // Collision avoidance logic
        function updateLabelPositions() {
            // 1. Reset to base radial offset
            pigmentData.forEach(p => {
                const rDir = new THREE.Vector3(p.basePos.x, 0, p.basePos.z).normalize();
                if (rDir.lengthSq() === 0) rDir.set(1, 0, 0); // fallback for neutral
                
                // Fixed outward distance
                p.currentPos.copy(p.basePos).add(rDir.clone().multiplyScalar(6));
                p.tangentDir = new THREE.Vector3(0, 1, 0).cross(rDir).normalize();
            });

            // 2. Resolve collisions tangentially
            const iterations = 15;
            for (let iter = 0; iter < iterations; iter++) {
                for (let i = 0; i < pigmentData.length; i++) {
                    for (let j = i + 1; j < pigmentData.length; j++) {
                        const p1 = pigmentData[i];
                        const p2 = pigmentData[j];
                        
                        // Check screen space overlap
                        const pos1 = p1.currentPos.clone().project(camera);
                        const pos2 = p2.currentPos.clone().project(camera);
                        
                        if (pos1.z > 1 || pos2.z > 1 || pos1.z < -1 || pos2.z < -1) continue;
                        
                        // Screen coordinates are [-1, 1], so width is 2. 
                        // camera.aspect is width/height.
                        const dx = (pos1.x - pos2.x) * camera.aspect;
                        const dy = pos1.y - pos2.y;
                        
                        // Use approximate bounding box or ellipse based on sprite scales
                        const w1 = p1.sprite.userData.width / 30; // empirical screen-space scaling 
                        const w2 = p2.sprite.userData.width / 30;
                        const h1 = p1.sprite.userData.height / 30;
                        const h2 = p2.sprite.userData.height / 30;
                        
                        const minDistX = (w1 + w2) / 2;
                        const minDistY = (h1 + h2) / 2 + 0.02; // add small padding
                        
                        if (Math.abs(dx) < minDistX && Math.abs(dy) < minDistY) {
                            // Overlap! Push apart tangentially in 3D
                            const shiftAmount = 0.5;
                            const relPos = p1.currentPos.clone().sub(p2.currentPos);
                            
                            let dir1 = p1.tangentDir.clone();
                            if (relPos.dot(dir1) < 0) dir1.negate();
                            
                            let dir2 = p2.tangentDir.clone();
                            if (relPos.dot(dir2) > 0) dir2.negate();

                            p1.currentPos.add(dir1.multiplyScalar(shiftAmount));
                            p2.currentPos.add(dir2.multiplyScalar(shiftAmount));
                        }
                    }
                }
            }
            
            // 3. Apply positions
            pigmentData.forEach(p => {
                p.sprite.position.copy(p.currentPos);
                
                const positions = p.line.geometry.attributes.position.array;
                positions[0] = p.basePos.x;
                positions[1] = p.basePos.y;
                positions[2] = p.basePos.z;
                positions[3] = p.currentPos.x;
                positions[4] = p.currentPos.y;
                positions[5] = p.currentPos.z;
                p.line.geometry.attributes.position.needsUpdate = true;
            });
        }

        // Initialize label positions
        updateLabelPositions();

        // Update on camera move
        controls.addEventListener('change', updateLabelPositions);

        // UI Controls logic
        const valueSlider = document.getElementById('value-slider');
        const valueLabel = document.getElementById('value-label');
        const transparencySlider = document.getElementById('transparency-slider');
        const transparencyLabel = document.getElementById('transparency-label');

        function updateVoxels() {
            const cutoffValue = parseInt(valueSlider.value);
            const transparency = parseInt(transparencySlider.value) / 100.0;
            const opacity = 1.0 - transparency;

            cubes.forEach(cube => {
                cube.visible = cube.userData.V >= cutoffValue && opacity > 0;
                // Only enable depthWrite if nearly fully opaque, to fix sorting glitches
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
            updateLabelPositions();
        });

        function animate() {
            requestAnimationFrame(animate);
            controls.update();
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

with open('munsell_solid_v3.html', 'w') as f:
    f.write(final_html)

print("Generated munsell_solid_v3.html successfully.")
