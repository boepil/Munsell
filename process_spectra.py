import json
import numpy as np
import pandas as pd
from scipy.interpolate import NearestNDInterpolator
import colour

# 1. Load Munsell Data to create a mapping from Lab to Munsell (V, C, hIndex)
print("Loading Munsell data for interpolation...")
munsell_df = pd.read_csv('munsell_3-3.csv')

hues = [
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
]

lab_points = []
munsell_targets = []

ILLUMINANT_C = colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer']['C']
ILLUMINANT_D65 = colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer']['D65']

for _, row in munsell_df.iterrows():
    H = str(row['H']).strip()
    try:
        hIndex = hues.index(H)
    except ValueError:
        hIndex = -1
    
    if hIndex == -1 and row['C'] > 0:
        continue # Skip unknown hues if chroma > 0
        
    V = float(row['V'])
    C = float(row['C'])
    x = float(row['x'])
    y = float(row['y'])
    Y = float(row['Y'])
    
    if y == 0:
        continue
        
    XYZ = colour.xyY_to_XYZ([x, y, Y / 100.0])
    Lab = colour.XYZ_to_Lab(XYZ, ILLUMINANT_C)
    
    lab_points.append(Lab)
    
    if C == 0:
        hIndex_cont = 0
        cos_h = 0
        sin_h = 0
    else:
        angle = (hIndex / 40.0) * 2 * np.pi
        cos_h = np.cos(angle)
        sin_h = np.sin(angle)
        
    munsell_targets.append([V, C, cos_h, sin_h])

lab_points = np.array(lab_points)
munsell_targets = np.array(munsell_targets)

interpolator = NearestNDInterpolator(lab_points, munsell_targets)

def lab_to_munsell(L, a, b):
    res = interpolator([[L, a, b]])[0]
    V, C, cos_h, sin_h = res
    if C == 0:
        hIndex_cont = 0
    else:
        angle = np.arctan2(sin_h, cos_h)
        if angle < 0:
            angle += 2 * np.pi
        hIndex_cont = (angle / (2 * np.pi)) * 40.0
    return float(V), float(C), float(hIndex_cont)

def XYZ_to_sRGB_D65(XYZ):
    RGB = colour.XYZ_to_sRGB(XYZ, ILLUMINANT_D65)
    RGB = np.clip(np.round(RGB * 255), 0, 255).astype(int)
    return RGB.tolist()

natural_lights = []

print("Generating natural light spectra...")
cmfs = colour.MSDS_CMFS['CIE 1931 2 Degree Standard Observer']

print(" - Sky and Sunset")
for temp in np.linspace(2000, 4000, 300):
    sd = colour.sd_blackbody(temp, cmfs.shape)
    XYZ = colour.sd_to_XYZ(sd, cmfs)
    XYZ = XYZ / XYZ[1] * np.random.uniform(10, 80) / 100.0 
    
    # Adapt blackbody to Illum C directly
    xy_w = colour.XYZ_to_xy(colour.sd_to_XYZ(sd, cmfs))
    XYZ_w_source = colour.xy_to_XYZ(xy_w)
    XYZ_w_target = colour.xy_to_XYZ(ILLUMINANT_C)
    
    XYZ_C = colour.adaptation.chromatic_adaptation_VonKries(XYZ, XYZ_w_source, XYZ_w_target)
    Lab_C = colour.XYZ_to_Lab(XYZ_C, ILLUMINANT_C)
    
    V, C, hIndex = lab_to_munsell(Lab_C[0], Lab_C[1], Lab_C[2])
    
    XYZ_w_d65 = colour.xy_to_XYZ(ILLUMINANT_D65)
    XYZ_D65 = colour.adaptation.chromatic_adaptation_VonKries(XYZ, XYZ_w_source, XYZ_w_d65)
    rgb = XYZ_to_sRGB_D65(XYZ_D65)
    
    natural_lights.append({
        'category': 'Sunset',
        'is_radiance': True,
        'V': V, 'C': C, 'hIndex': hIndex,
        'rgb': rgb,
        'illuminant': f"Blackbody {int(temp)}K"
    })

for temp in np.linspace(4000, 20000, 400):
    try:
        sd = colour.sd_CIE_illuminant_D_series(temp)
    except:
        continue
    XYZ = colour.sd_to_XYZ(sd, cmfs)
    XYZ = XYZ / XYZ[1] * np.random.uniform(40, 100) / 100.0 
    
    xy_w = colour.XYZ_to_xy(colour.sd_to_XYZ(sd, cmfs))
    XYZ_w_source = colour.xy_to_XYZ(xy_w)
    XYZ_w_target = colour.xy_to_XYZ(ILLUMINANT_C)
    
    XYZ_C = colour.adaptation.chromatic_adaptation_VonKries(XYZ, XYZ_w_source, XYZ_w_target)
    Lab_C = colour.XYZ_to_Lab(XYZ_C, ILLUMINANT_C)
    
    V, C, hIndex = lab_to_munsell(Lab_C[0], Lab_C[1], Lab_C[2])
    
    XYZ_w_d65 = colour.xy_to_XYZ(ILLUMINANT_D65)
    XYZ_D65 = colour.adaptation.chromatic_adaptation_VonKries(XYZ, XYZ_w_source, XYZ_w_d65)
    rgb = XYZ_to_sRGB_D65(XYZ_D65)
    
    natural_lights.append({
        'category': 'Sky',
        'is_radiance': True,
        'V': V, 'C': C, 'hIndex': hIndex,
        'rgb': rgb,
        'illuminant': f"CIE D-Series {int(temp)}K"
    })

print(" - Foliage, Soil, Flowers, Water")
import colour_datasets

try:
    forest_ds = colour_datasets.load('3269920')
    spectra = list(forest_ds.values())[0] # Should be MultiSpectralDistributions
    sd_d65 = colour.SDS_ILLUMINANTS['D65']
    
    # spectra might be a dict of SpectralDistribution or a MultiSpectralDistributions
    # If it's a MultiSpectralDistributions, we can get items like:
    if hasattr(spectra, 'signals'):
        items = spectra.signals.items()
    else:
        items = spectra.items()
        
    for name, sd in items:
        # Interpolate sd to match D65 shape if needed
        sd = sd.copy()
        sd.interpolate(colour.SpectralShape(380, 780, 5))
        sd_d65_interp = sd_d65.copy().interpolate(colour.SpectralShape(380, 780, 5))
        cmfs_interp = cmfs.copy().interpolate(colour.SpectralShape(380, 780, 5))
        
        radiance_sd = sd * sd_d65_interp
        XYZ = colour.sd_to_XYZ(radiance_sd, cmfs_interp)
        
        XYZ_w_source = colour.xy_to_XYZ(ILLUMINANT_D65)
        XYZ_w_target = colour.xy_to_XYZ(ILLUMINANT_C)
        XYZ_C = colour.adaptation.chromatic_adaptation_VonKries(XYZ, XYZ_w_source, XYZ_w_target)
        Lab_C = colour.XYZ_to_Lab(XYZ_C, ILLUMINANT_C)
        V, C, hIndex = lab_to_munsell(Lab_C[0], Lab_C[1], Lab_C[2])
        rgb = XYZ_to_sRGB_D65(XYZ)
        
        if 10 <= hIndex <= 20: category = 'Foliage'
        elif 2 <= hIndex <= 9: category = 'Soil'
        elif 22 <= hIndex <= 30: category = 'Water'
        else: category = 'Flower'
        
        for multiplier in np.random.uniform(0.1, 1.5, 10):
            natural_lights.append({
                'category': category,
                'is_radiance': False,
                'V': max(0, V * (multiplier**0.33)),
                'C': max(0, C * multiplier), 
                'hIndex': hIndex,
                'rgb': [min(255, max(0, int(c*multiplier))) for c in rgb],
                'illuminant': "D65"
            })
except Exception as e:
    print(f"Dataset load failed: {e}")

with open('natural_lights.json', 'w') as f:
    json.dump(natural_lights, f, indent=2)

print(f"Generated {len(natural_lights)} natural light samples.")
print("Saved to natural_lights.json")
