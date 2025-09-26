"""Generate a few sample tracks with the procedural generator and add them to the local library.

Run this script from the workspace root to create files under `library/` and update `library.json`.
"""
from audio_generator import generate_from_prompt, save_wav
from library import add_track
import os
import tempfile


def make_sample(prompt, duration=12, title=None):
    print(f"Generating: {prompt} ({duration}s)")
    sig = generate_from_prompt(prompt, duration=duration, style='default', mood=0.0)
    lib_dir = os.path.join(os.path.dirname(__file__), 'library')
    os.makedirs(lib_dir, exist_ok=True)
    fname = title or prompt.replace(' ', '_')[:24]
    out_path = os.path.join(lib_dir, f"sample_{fname}.wav")
    save_wav(sig, out_path)
    add_track(title=(title or prompt)[:120], file_path=out_path, duration=duration, prompt=prompt)
    print(f"Saved: {out_path}")


def main():
    samples = [
        ("Calm lofi with piano and rain sounds", 15, "Lofi Rain"),
        ("Epic orchestral soundtrack with violins and drums", 20, "Epic Orchestra"),
        ("Upbeat synthwave with arpeggio and bass", 18, "Synthwave"),
    ]
    for prompt, dur, title in samples:
        make_sample(prompt, duration=dur, title=title)

    print('Done generating samples.')


if __name__ == '__main__':
    main()
