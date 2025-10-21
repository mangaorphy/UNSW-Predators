#!/usr/bin/env python3
import os
import json
from pathlib import Path
import shutil

raw_dir = Path("unsw_raw_images")
base_dir = "unsw_images_organized"
sample_file = "sampled_files.json"

# Load sampled files (with full paths)
with open(sample_file) as f:
    sampled_by_class = json.load(f)

# Build a map: {filename (no path) -> full path from metadata}
# Also normalize to lowercase for case-insensitive match
expected_files = {}  # basename_lower -> (full_path, class)
for cls, paths in sampled_by_class.items():
    for full_path in paths:
        basename = os.path.basename(full_path)  # e.g., "PS6__CamB__...JPG"
        key = basename.lower()
        expected_files[key] = (full_path, cls)

print(f"✅ Loaded {len(expected_files)} expected images (from paths).")

# Scan actual files in unsw_raw_images (flat)
actual_files = {}
for f in raw_dir.iterdir():
    if f.is_file():
        actual_files[f.name.lower()] = f.name

print(f"📁 Found {len(actual_files)} files in unsw_raw_images/")

# Create output dirs
os.makedirs(base_dir, exist_ok=True)
for cls in sampled_by_class.keys():
    os.makedirs(os.path.join(base_dir, cls), exist_ok=True)

# Match and move
moved = 0
for lower_name, real_name in actual_files.items():
    if lower_name in expected_files:
        full_path, cls = expected_files[lower_name]
        src = raw_dir / real_name
        dst = os.path.join(base_dir, cls, real_name)
        if src.exists() and src.stat().st_size > 0:
            shutil.move(str(src), dst)
            moved += 1

# Final stats
total_expected = len(expected_files)
missing = total_expected - moved
print(f"\n🎉 Organization complete!")
print(f"✅ Moved: {moved}")
print(f"❌ Missing: {missing}")
print(f"📊 Coverage: {100 * moved / total_expected:.1f}%")
print(f"📁 Dataset saved to: {base_dir}/")