import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter
import os

SAMPLE_RATE = 44100


def _butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def _lowpass_filter(data, cutoff=4000, fs=SAMPLE_RATE, order=6):
    b, a = _butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y


def generate_from_prompt(prompt: str, duration=15, style='lofi', mood: float = 0.0) -> np.ndarray:
    """Simple heuristic generator: create base sine + noise depending on prompt keywords.

    This is a placeholder for a real model like MusicGen. It returns a float32 numpy array.
    """
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    # Base frequency selection from prompt
    # mood: -1.0 (calm) .. 0 .. 1.0 (energetic)
    mood = max(-1.0, min(1.0, mood))
    if 'lofi' in prompt.lower():
        freqs = [110, 220]  # low warm
        noise_amp = 0.06 - 0.03 * mood
    elif 'edm' in prompt.lower() or 'dance' in prompt.lower():
        freqs = [440, 880]
        noise_amp = 0.02 + 0.03 * mood
    elif 'classical' in prompt.lower() or 'orchestra' in prompt.lower():
        freqs = [220, 330, 440]
        noise_amp = 0.01 + 0.02 * mood
    else:
        freqs = [261.63, 329.63]  # C4, E4
        noise_amp = 0.04 + 0.01 * mood

    signal = np.zeros_like(t)
    for f in freqs:
        signal += 0.3 * np.sin(2 * np.pi * f * t)

    # Add a slow amplitude LFO for movement; mood changes LFO rate
    lfo_rate = 0.07 + 0.2 * max(0.0, mood)  # calmer -> slower LFO
    lfo = 0.5 * (1 + np.sin(2 * np.pi * lfo_rate * t))
    signal *= lfo

    # Add noise for 'lofi' texture
    signal += noise_amp * np.random.normal(0, 1, size=signal.shape)

    # Simple lowpass for warmth
    # mood affects cutoff: energetic -> brighter
    cutoff = int(4000 + 3000 * max(0.0, mood))
    signal = _lowpass_filter(signal, cutoff=cutoff)

    # Normalize
    maxv = np.max(np.abs(signal))
    if maxv > 0:
        signal = signal / maxv * 0.9

    return signal.astype('float32')


def remix_audio_from_file(path: str, intensity: float = 0.5, overlay_prompt: str = None, mood: float = 0.0) -> np.ndarray:
    """A simple remix: read audio file, time-stretch/pitch-shift a bit and optionally overlay a short generated motif.

    intensity: 0.0..1.0 how strong the remix effects are.
    overlay_prompt: optional prompt to synthesize a short motif to overlay.
    mood: forwarded to generator if overlay is used.
    """
    import soundfile as sf
    data, sr = sf.read(path, dtype='float32')
    # mix to mono
    if data.ndim > 1:
        data = np.mean(data, axis=1)

    # Attempt to use librosa for higher-quality time-stretch and pitch-shift
    try:
        import librosa
        # librosa expects float64 mono at its sample rate — convert if needed
        if sr != SAMPLE_RATE:
            data = librosa.resample(data.astype('float32'), orig_sr=sr, target_sr=SAMPLE_RATE)
            sr = SAMPLE_RATE
        else:
            data = data.astype('float32')

        # choose stretch rate based on intensity (closer to 1.0 is less change)
        stretch_rate = 1.0 + (0.15 * (intensity - 0.5))
        if stretch_rate <= 0:
            stretch_rate = 0.5

        # librosa.effects.time_stretch requires mono
        y = librosa.to_mono(data) if data.ndim > 1 else data
        stretched = librosa.effects.time_stretch(y, rate=stretch_rate)

        # slight pitch shift for creative remixing (in semitones)
        semitones = (intensity - 0.5) * 4.0  # -2 .. +2 semitones
        if abs(semitones) > 0.01:
            stretched = librosa.effects.pitch_shift(stretched, sr=SAMPLE_RATE, n_steps=semitones)

    except Exception:
        # Fallback to naive resampling if librosa is not available or fails
        from scipy.signal import resample

        factor = 1.0 - (0.15 * (intensity - 0.5))  # intensity mid -> little change
        if factor <= 0:
            factor = 0.5
        new_len = int(len(data) / factor)
        try:
            stretched = resample(data, new_len)
        except Exception:
            # fallback: naive repeat/truncate
            stretched = np.interp(np.linspace(0, len(data), new_len), np.arange(len(data)), data)

    # apply a simple lowpass/highpass depending on intensity
    if intensity > 0.6:
        processed = _lowpass_filter(stretched, cutoff=6000 + int(2000 * intensity))
    else:
        processed = _lowpass_filter(stretched, cutoff=4000)

    # overlay generated motif if requested
    if overlay_prompt:
        motif = generate_from_prompt(overlay_prompt, duration=min(8, len(processed)/SAMPLE_RATE), style='default', mood=mood)
        # trim or pad motif
        if len(motif) < len(processed):
            motif = np.pad(motif, (0, len(processed) - len(motif)))
        else:
            motif = motif[:len(processed)]
        processed = (1.0 - intensity) * processed + intensity * 0.6 * motif

    # normalize
    maxv = np.max(np.abs(processed))
    if maxv > 0:
        processed = processed / maxv * 0.9

    return processed.astype('float32')


def save_wav(signal: np.ndarray, out_path: str):
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    sf.write(out_path, signal, SAMPLE_RATE, subtype='PCM_16')
