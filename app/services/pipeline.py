from typing import Any
from app.core.config import settings
import ffmpy
from pathlib import Path
from groq import Groq
import ollama 
from pydantic import BaseModel

groq_client = Groq(api_key=settings.groq_api_key) 
client = ollama.Client(host=settings.ollama_base_url)

class MeetingOutput(BaseModel):
    summary: str
    key_points: list[str]
    action_items: list[str]
    decisions: list[str]

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
    
def transcribe_audio(audio_path: str)-> list[dict]:
    if not Path(audio_path).exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    with open(audio_path, "rb") as f:
        response = groq_client.audio.transcriptions.create(
            model = "whisper-large-v3-turbo",
            file = f,
            language = "en",
            response_format = "verbose_json"
        )
    texts: list[dict[str, Any]] = []
    for segment in response.segments: #type: ignore
        texts.append({
            "start":segment["start"],
            "end":segment["end"],
            "text":segment["text"].strip()
        })
    return texts

def summarize(transcript: str)->MeetingOutput:
    response = client.chat(
        model = settings.ollama_model,
        messages = [{"role": "user","content": f"summarize the following transcript and provide a summary, key points, action items, and decisions in JSON format:\n\n{transcript}"}],
        format = MeetingOutput.model_json_schema(),

    )
    return MeetingOutput.model_validate_json(response["message"]["content"])
