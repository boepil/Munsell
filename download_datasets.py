import os
import urllib.request
import zipfile
import shutil

BASE_URL = "http://personalpages.manchester.ac.uk/staff/d.h.foster/"
DATA_DIR = "d:\\_PROJECTS\\My\\ai\\Munsell\\data"

DATASETS = {
    "nascimento_2016": [
        "Local_Illumination_HSIs/hsi_spatial/Bom_Jesus_Red_flower.zip",
        "Local_Illumination_HSIs/hsi_spatial/Bom_Jesus_Marigolds.zip",
        "Local_Illumination_HSIs/hsi_spatial/Souto_Farm_Barn.zip",
        "Local_Illumination_HSIs/hsi_spatial/Sameiro_Branch.zip",
        "Local_Illumination_HSIs/hsi_spatial/Gualtar_Steps.zip"
    ],
    "foster_2004": [
        "Hyperspectral_images_of_natural_scenes_04_files/scenes/scene1.zip",
        "Hyperspectral_images_of_natural_scenes_04_files/scenes/scene2.zip"
    ],
    "nascimento_2002": [
        "Hyperspectral_images_of_natural_scenes_02_files/scene1.zip",
        "Hyperspectral_images_of_natural_scenes_02_files/scene2.zip"
    ]
}

def download_and_extract():
    for dataset_name, files in DATASETS.items():
        target_dir = os.path.join(DATA_DIR, dataset_name)
        for file_path in files:
            url = BASE_URL + file_path
            filename = os.path.basename(file_path)
            zip_path = os.path.join(target_dir, filename)
            
            print(f"Downloading {filename} to {dataset_name}...")
            try:
                urllib.request.urlretrieve(url, zip_path)
                print(f"Extracting {filename}...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # Only extract .mat files to keep it clean
                    for member in zip_ref.namelist():
                        if member.endswith('.mat'):
                            extracted_path = zip_ref.extract(member, target_dir)
                            # Move out of any inner directories
                            if os.path.dirname(member):
                                final_path = os.path.join(target_dir, os.path.basename(member))
                                if not os.path.exists(final_path):
                                    shutil.move(extracted_path, final_path)
                                # Try to clean up empty directories left behind
                                try:
                                    os.rmdir(os.path.dirname(extracted_path))
                                except OSError:
                                    pass
                # Remove the zip file to save space
                os.remove(zip_path)
            except Exception as e:
                print(f"Error downloading or extracting {url}: {e}")

if __name__ == "__main__":
    download_and_extract()
    print("Download and extraction complete.")
