from pathlib import Path
from app.core.config import settings
from app.services.pipeline import convert_to_wav, transcribe_audio, summarize

def run_pipeline(input_path: str) -> dict:
    input_file = Path(input_path)

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    output_audio_path: str = str(settings.audio_dir / f"{input_file.stem}.wav")

    try:
        convert_to_wav(input_path, output_audio_path)
    except Exception as e:
        raise RuntimeError(f"Failed to convert audio: {e}") from e
    
    try:
        transcript_segments = transcribe_audio(output_audio_path)
    except Exception as e:
        raise RuntimeError(f"Failed to transcribe audio: {e}") from e
    
    transcript = ""

    for segment in transcript_segments:
        transcript += segment["text"] + " "
    
    try:
        meeting_output = summarize(transcript)
    except Exception as e:
        raise RuntimeError(f"Failed to summarize transcript: {e}") from e
    
    return {
        "segments": transcript_segments,
        "minutes": meeting_output
    }

if __name__ == "__main__":
    result = run_pipeline(str(settings.uploads_dir / "videoplayback.mp4"))
    print("\n--- Meeting Minutes ---")
    print(f"Summary: {result['minutes'].summary}\n")
    print(f"Key Points: {result['minutes'].key_points}\n")
    print(f"Action Items: {result['minutes'].action_items}\n")
    print(f"Decisions: {result['minutes'].decisions}\n")
    print(f"Segments: {len(result['segments'])}")