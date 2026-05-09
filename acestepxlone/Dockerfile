FROM docker.io/harveyff/acestep15:v2.0.3

# Update ACE-Step code to latest (includes XL model support)
RUN apt-get update -qq && apt-get install -y -qq wget unzip > /dev/null 2>&1 && \
    wget -q https://github.com/ace-step/ACE-Step-1.5/archive/refs/heads/main.zip -O /tmp/ace.zip && \
    unzip -qo /tmp/ace.zip -d /tmp/ && \
    cp -r /tmp/ACE-Step-1.5-main/acestep/* /app/acestep/ && \
    mkdir -p /app/ui && \
    cp -r /tmp/ACE-Step-1.5-main/ui/* /app/ui/ 2>/dev/null || true && \
    rm -rf /tmp/ace.zip /tmp/ACE-Step-1.5-main /var/lib/apt/lists/*

# Fix: torchaudio 2.10 uses torchcodec internally which is broken (ABI mismatch)
# Replace torchaudio with a soundfile+ffmpeg shim in audio_utils
COPY torchaudio_shim.py /app/torchaudio_shim.py
RUN sed -i 's/^import torchaudio$/import torchaudio_shim as torchaudio/' /app/acestep/audio_utils.py && \
    grep -q "torchaudio_shim" /app/acestep/audio_utils.py && \
    echo "audio_utils.py patched: torchaudio -> torchaudio_shim"
