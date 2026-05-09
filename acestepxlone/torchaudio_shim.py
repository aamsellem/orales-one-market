"""
Drop-in shim for torchaudio.save/load using soundfile + ffmpeg.
Replaces torchaudio when torchcodec is broken.
"""
import os
import subprocess
import tempfile
import torch
import numpy as np
import soundfile as sf


class functional:
    """Minimal torchaudio.functional replacement."""

    @staticmethod
    def resample(waveform, orig_freq, new_freq):
        if orig_freq == new_freq:
            return waveform
        # Use linear interpolation for resampling
        ratio = new_freq / orig_freq
        length = waveform.shape[-1]
        new_length = int(length * ratio)
        return torch.nn.functional.interpolate(
            waveform.unsqueeze(0), size=new_length, mode="linear", align_corners=False
        ).squeeze(0)


def save(filepath, src, sample_rate, format=None, **kwargs):
    """Save audio tensor to file using soundfile + ffmpeg."""
    filepath = str(filepath)
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

    if isinstance(src, torch.Tensor):
        audio_np = src.cpu().float().numpy()
    else:
        audio_np = np.array(src, dtype=np.float32)

    # torchaudio uses (channels, samples) layout
    if audio_np.ndim == 2:
        audio_np = audio_np.T  # to (samples, channels) for soundfile

    ext = (format or os.path.splitext(filepath)[1].lstrip(".") or "wav").lower()

    if ext in ("mp3", "aac", "opus", "ogg"):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            sf.write(tmp_path, audio_np, sample_rate, subtype="FLOAT")
            cmd = ["ffmpeg", "-y", "-i", tmp_path, "-ar", str(sample_rate)]
            if ext == "mp3":
                cmd += ["-codec:a", "libmp3lame", "-b:a", "192k"]
            cmd.append(filepath)
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            if result.returncode != 0:
                raise RuntimeError(f"ffmpeg error: {result.stderr.decode()[:200]}")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    elif ext == "flac":
        sf.write(filepath, audio_np, sample_rate, format="FLAC")
    else:
        sf.write(filepath, audio_np, sample_rate)


def load(filepath, **kwargs):
    """Load audio file, returns (waveform, sample_rate) in torchaudio format."""
    filepath = str(filepath)
    audio_np, sample_rate = sf.read(filepath, dtype="float32")
    if audio_np.ndim == 1:
        audio_np = audio_np.reshape(1, -1)  # (1, samples)
    else:
        audio_np = audio_np.T  # (channels, samples)
    return torch.from_numpy(audio_np), sample_rate
