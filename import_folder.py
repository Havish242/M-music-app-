"""Import all mp3/wav files from a folder into the app library (copy files and register them).

Usage:
    python import_folder.py "C:\path\to\telugu_songs"

This script is provided for convenience. Make sure you have the right to use/copy the songs before importing.
"""
import sys
import os
from library import add_track


def import_folder(src_folder: str):
    if not os.path.isdir(src_folder):
        print(f"Not a folder: {src_folder}")
        return
    dest_dir = os.path.join(os.path.dirname(__file__), 'library')
    os.makedirs(dest_dir, exist_ok=True)
    count = 0
    for fname in os.listdir(src_folder):
        if not fname.lower().endswith(('.mp3', '.wav')):
            continue
        src = os.path.join(src_folder, fname)
        dest = os.path.join(dest_dir, fname)
        with open(src, 'rb') as fsrc, open(dest, 'wb') as fdst:
            fdst.write(fsrc.read())
        add_track(title=os.path.splitext(fname)[0], file_path=dest, duration=0.0, prompt='Imported folder')
        count += 1
    print(f"Imported {count} files from {src_folder}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python import_folder.py <folder_path>')
    else:
        import_folder(sys.argv[1])
