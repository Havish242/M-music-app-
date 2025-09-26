"""Safe shim to call MusicGen / audiocraft models if installed.

This file intentionally does not install any heavy libraries. It tries to import them
when `generate_with_musicgen` is called and raises a clear error if unavailable.
"""
from typing import Optional
import numpy as np


def is_musicgen_available() -> bool:
    try:
        import audiocraft  # type: ignore
        return True
    except Exception:
        return False


def generate_with_musicgen(prompt: str, duration: int = 15, device: str = 'cpu') -> np.ndarray:
    """Generate audio with MusicGen/audiocraft if installed.

    Returns a float32 numpy array (samples, mono) at 44100 Hz.
    If the package is not installed, raises ImportError with guidance.
    """
    try:
        # audiocraft import may vary; try common entry points
        from audiocraft.models import MusicGen  # type: ignore
    except Exception as e:
        raise ImportError(
            "MusicGen/audiocraft is not installed or failed to import. "
            "Install with: pip install audiocraft torch --extra-index-url https://download.pytorch.org/whl/cu117"
        ) from e

    # Load model (this may download weights on first call)
    model = MusicGen.get_pretrained('melody') if hasattr(MusicGen, 'get_pretrained') else None
    if model is None:
        # Fallback API attempt
        try:
            model = MusicGen()
        except Exception:
            raise RuntimeError('Failed to instantiate MusicGen model.')

    model.to(device)

    # Model generate API varies; this is a best-effort sketch.
    out = model.generate([prompt], length=duration)

    # `out` might be a list of tensors or numpy arrays — coerce to numpy
    audio = out[0]
    try:
        import torch
        if hasattr(audio, 'cpu'):
            audio = audio.cpu().numpy()
    except Exception:
        pass

    # If stereo, convert to mono
    if audio.ndim > 1:
        if audio.shape[0] == 2:  # shape (2, N)
            audio = np.mean(audio, axis=0)
        elif audio.shape[1] == 2:  # shape (N, 2)
            audio = np.mean(audio, axis=1)

    # Ensure float32
    return audio.astype('float32')
