import os
import shutil

# Path to the root of your project
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

count = 0
for root, dirs, files in os.walk(PROJECT_ROOT):
    for d in dirs:
        if d == '__pycache__':
            pycache_path = os.path.join(root, d)
            print(f"Deleting: {pycache_path}")
            shutil.rmtree(pycache_path)
            count += 1
print(f"Selesai. {count} folder __pycache__ dihapus.")
