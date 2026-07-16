import os
import glob
import scipy.io

DATA_DIR = "d:\\_PROJECTS\\My\\ai\\Munsell\\data"

def verify_datasets():
    results = []
    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith('.mat'):
                filepath = os.path.join(root, file)
                dataset_name = os.path.basename(root)
                
                try:
                    mat = scipy.io.loadmat(filepath)
                    # Find the main data array
                    data_keys = [k for k in mat.keys() if not k.startswith('__')]
                    
                    largest_key = None
                    largest_size = 0
                    shape = None
                    
                    for key in data_keys:
                        if hasattr(mat[key], 'shape'):
                            size = mat[key].size
                            if size > largest_size:
                                largest_size = size
                                largest_key = key
                                shape = mat[key].shape
                                
                    if shape:
                        results.append(f"{dataset_name} | {file} | Array '{largest_key}': {shape}")
                    else:
                        results.append(f"{dataset_name} | {file} | No valid data array found. Keys: {data_keys}")
                except Exception as e:
                    results.append(f"{dataset_name} | {file} | Error loading file: {e}")
                    
    with open("dataset_verification_report.txt", "w") as f:
        f.write("\n".join(results))
    print("Verification complete. See dataset_verification_report.txt")

if __name__ == "__main__":
    verify_datasets()
