#!/usr/bin/env python3
# =============================================
# UNSW Predators Downloader with LIVE PROGRESS
# - 50% sample per class
# - Real-time terminal progress (e.g., "goanna: 1243/42180")
# - Resumable & reproducible
# - Uses gsutil + Google Cloud (fast & reliable)
# =============================================

import os
import json
import random
import requests
import zipfile
from collections import defaultdict
import shutil
import subprocess
import time
import threading
from pathlib import Path

# ====== CONFIG ======
METADATA_URL = "https://storage.googleapis.com/public-datasets-lila/unsw-predators/unsw-predators.json.zip"
SAMPLE_FRACTION = 0.5
RANDOM_SEED = 42
DESIRED_CLASSES = {'dingo', 'fox', 'goanna', 'possum', 'quoll'}

# ====== 1. Download & parse metadata ======
def download_metadata():
    zip_path = "unsw-predators.json.zip"
    json_path = "unsw-predators.json"

    if not os.path.exists(json_path):
        print("📥 Downloading metadata from Google Cloud...")
        resp = requests.get(METADATA_URL)
        resp.raise_for_status()
        with open(zip_path, "wb") as f:
            f.write(resp.content)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(".")
        print("✅ Metadata ready.")
    else:
        print("✅ Metadata already exists.")

    with open(json_path, "r") as f:
        return json.load(f)

# ====== 2. Sample files reproducibly ======
def get_sampled_files(data):
    sample_file = "sampled_files.json"
    if os.path.exists(sample_file):
        print("🔁 Loading existing sample list...")
        with open(sample_file, "r") as f:
            return json.load(f)

    print(f"🎲 Sampling {SAMPLE_FRACTION*100:.0f}% per class (seed={RANDOM_SEED})...")
    random.seed(RANDOM_SEED)

    cat_id_to_name = {c['id']: c['name'] for c in data['categories']}
    img_id_to_file = {img['id']: img['file_name'] for img in data['images']}
    file_to_class = {
        img_id_to_file[ann['image_id']]: cat_id_to_name[ann['category_id']]
        for ann in data['annotations']
    }

    class_to_files = defaultdict(list)
    for fname, cls in file_to_class.items():
        if cls in DESIRED_CLASSES:
            class_to_files[cls].append(fname)

    sampled = {}
    for cls, files in class_to_files.items():
        n = max(1, int(len(files) * SAMPLE_FRACTION))
        sampled[cls] = random.sample(files, n)
        print(f"✅ {cls}: {n} / {len(files)}")

    with open(sample_file, "w") as f:
        json.dump(sampled, f)
    return sampled

# ====== 3. Live progress monitor ======
def monitor_progress(sampled_by_class, raw_dir):
    """Print live progress every 2 seconds."""
    while True:
        time.sleep(2)
        total_done = 0
        total_expected = 0
        lines = []
        for cls, files in sampled_by_class.items():
            done = sum(1 for f in files if (Path(raw_dir) / f).exists())
            total = len(files)
            pct = 100 * done / total if total > 0 else 0
            lines.append(f"{cls:<10} {done:>6}/{total:<6} ({pct:>5.1f}%)")
            total_done += done
            total_expected += total

        os.system('clear' if os.name == 'posix' else 'cls')  # Clear screen
        print("🚀 DOWNLOADING IMAGES (live progress)\n")
        for line in lines:
            print(line)
        overall_pct = 100 * total_done / total_expected if total_expected > 0 else 0
        print(f"\n📊 Overall: {total_done}/{total_expected} ({overall_pct:.1f}%)")
        print("\n(Press Ctrl+C to stop — download will resume next time)")

        if total_done >= total_expected:
            break

# ====== 4. Main ======
def main():
    # Setup
    raw_dir = "unsw_raw_images"
    os.makedirs(raw_dir, exist_ok=True)

    # Load data
    data = download_metadata()
    sampled_by_class = get_sampled_files(data)

    # Flatten list for gsutil
    all_files = [f for files in sampled_by_class.values() for f in files]
    with open("download_list.txt", "w") as f:
        for fname in all_files:
            f.write(f"gs://public-datasets-lila/unsw-predators/images/{fname}\n")

    # Start progress monitor in background
    monitor_thread = threading.Thread(
        target=monitor_progress,
        args=(sampled_by_class, raw_dir),
        daemon=True
    )
    monitor_thread.start()

    # Start download (output suppressed to avoid clutter)
    print("\n⏳ Starting download... (progress shown above)\n")
    try:
        subprocess.run(
            ["gsutil", "-m", "cp", "-I", raw_dir + "/"],
            stdin=open("download_list.txt", "r"),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False  # gsutil returns non-zero if some files exist
        )
    except FileNotFoundError:
        print("❌ ERROR: 'gsutil' not found. Install Google Cloud SDK:")
        print("   https://cloud.google.com/sdk/docs/install")
        return

    # Wait for final update
    time.sleep(2)

    # Organize into class folders
    print("\n\n📂 Organizing images by class...")
    base_dir = "unsw_images_organized"
    os.makedirs(base_dir, exist_ok=True)
    for cls in DESIRED_CLASSES:
        os.makedirs(os.path.join(base_dir, cls), exist_ok=True)

    moved = 0
    for cls, files in sampled_by_class.items():
        for fname in files:
            src = os.path.join(raw_dir, fname)
            dst = os.path.join(base_dir, cls, fname)
            if os.path.exists(src):
                shutil.move(src, dst)
                moved += 1

    print(f"✅ Done! {moved} images organized in '{base_dir}/'")

if __name__ == "__main__":
    main()