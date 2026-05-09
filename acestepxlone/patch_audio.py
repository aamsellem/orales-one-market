"""
Patch ACE-Step to use soundfile+ffmpeg instead of broken torchcodec.
Strategy: create a wrapper module that patches save_audio at import time.
"""
import os

# 1. Create a sitecustomize.py that patches save_audio when acestep loads
SITE_DIR = "/venv/main/lib/python3.11/site-packages"
PATCH_FILE = os.path.join(SITE_DIR, "acestep_audio_patch.py")

with open(PATCH_FILE, "w") as f:
    f.write('''
import soundfile as sf
import subprocess
import numpy as np
import os

def save_audio_ffmpeg(audio_data, output_path, sample_rate=48000, format=None,
                      channels_first=True, mp3_bitrate=None, mp3_sample_rate=None):
    """Save audio using soundfile + ffmpeg."""
    import torch

    output_path = str(output_path)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    if isinstance(audio_data, torch.Tensor):
        audio_np = audio_data.cpu().float().numpy()
    else:
        audio_np = np.array(audio_data, dtype=np.float32)

    if channels_first and audio_np.ndim == 2:
        audio_np = audio_np.T
    if audio_np.ndim == 1:
        audio_np = audio_np.reshape(-1, 1)

    audio_np = np.clip(audio_np, -1.0, 1.0)
    ext = (format or os.path.splitext(output_path)[1].lstrip(".") or "wav").lower()

    if ext in ("mp3", "aac", "opus", "ogg", "flac"):
        tmp_wav = output_path + ".tmp.wav"
        sf.write(tmp_wav, audio_np, sample_rate, subtype="FLOAT")
        cmd = ["ffmpeg", "-y", "-i", tmp_wav, "-ar", str(sample_rate)]
        if ext == "mp3":
            br = mp3_bitrate or "192k"
            sr = mp3_sample_rate or sample_rate
            cmd += ["-codec:a", "libmp3lame", "-b:a", br, "-ar", str(sr)]
        cmd.append(output_path)
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        if os.path.exists(tmp_wav):
            os.remove(tmp_wav)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {result.stderr.decode()}")
    else:
        sf.write(output_path, audio_np, sample_rate)

    return output_path
''')

# 2. Create a .pth file that patches acestep.audio_utils.save_audio on import
PTH_FILE = os.path.join(SITE_DIR, "patch_acestep.pth")
with open(PTH_FILE, "w") as f:
    f.write("import acestep_audio_patch_loader\n")

LOADER_FILE = os.path.join(SITE_DIR, "acestep_audio_patch_loader.py")
with open(LOADER_FILE, "w") as f:
    f.write('''
import importlib
import sys

class AcestepPatcher:
    """Patches acestep.audio_utils.save_audio when the module is first imported."""
    def find_module(self, name, path=None):
        if name == "acestep.audio_utils":
            return self
        return None

    def load_module(self, name):
        # Remove ourselves to avoid recursion
        sys.meta_path.remove(self)
        # Import the real module
        mod = importlib.import_module(name)
        # Patch it
        from acestep_audio_patch import save_audio_ffmpeg
        mod.save_audio = save_audio_ffmpeg
        # Also patch any module that already imported it
        for modname, m in list(sys.modules.items()):
            if m and hasattr(m, "save_audio") and modname.startswith("acestep"):
                try:
                    if m.save_audio.__module__ == "acestep.audio_utils":
                        m.save_audio = save_audio_ffmpeg
                except:
                    pass
        return mod

sys.meta_path.insert(0, AcestepPatcher())
''')

print("[patch] Created import hook to patch save_audio at runtime")
print(f"  - {PATCH_FILE}")
print(f"  - {PTH_FILE}")
print(f"  - {LOADER_FILE}")
