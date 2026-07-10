import os
import nvidia.cublas
import nvidia.cudnn

os.add_dll_directory(os.path.join(list(nvidia.cublas.__path__)[0], "bin"))
os.add_dll_directory(os.path.join(list(nvidia.cudnn.__path__)[0], "bin"))

from typing import Any
from faster_whisper import WhisperModel
from app.core.config import settings
import ffmpy
from pathlib import Path

def convert_to_wav(input_path: str, output_path: str)-> None:
    ff = ffmpy.FFmpeg(
        inputs={input_path: None},
        outputs={output_path: "-ac 1 -ar 16000 -y"}
    )
    try:
        ff.run()
    except ffmpy.FFRuntimeError as e:
        print(f"Error converting {input_path} to WAV: {e}")
        raise
    if not Path(output_path).exists():
        raise RuntimeError(f"Conversion completed but no output file found at {output_path}")
    
model = None

def transcribe_audio(audio_path: str)-> list[dict]:
    global model
    if not Path(audio_path).exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    if model is None:
        model = WhisperModel(settings.whisper_model, device=settings.whisper_device, compute_type=settings.whisper_compute_type)
    segments, info = model.transcribe(audio_path, beam_size=5)
    texts: list[dict[str, Any]] = []
    for segment in segments:
        texts.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip()
        })
    return texts