from fastapi import APIRouter, UploadFile, HTTPException, BackgroundTasks
from uuid import uuid4
from app.core.job_store import create_job, update_job, get_job
from app.services.process import run_pipeline
from app.core.config import settings
from app.services.pipeline import convert_to_wav, transcribe_audio, summarize
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/meetings", tags=["meetings"])

@router.post("/upload")
async def upload_meeting(file: UploadFile, background_tasks: BackgroundTasks):
    if file.filename is None or file.filename == "":
        raise HTTPException(status_code=400, detail="No file uploaded.")
    if not file.filename.endswith((".mp4", ".mp3", ".wav")):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .mp4, .mp3, and .wav files are allowed.")
    job_id = str(uuid4())
    create_job(job_id)
    filename = f"{job_id}_{file.filename}"
    file_path = settings.uploads_dir / filename
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    background_tasks.add_task(process_job, job_id=job_id, file_path=str(file_path))
    return {"job_id": job_id}

def process_job(job_id: str, file_path: str):
    update_job(job_id=job_id, status="in_progress")
    try:
        result = run_pipeline(file_path)
        update_job(job_id=job_id, status="completed", minutes=result["minutes"])
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}")
        update_job(job_id=job_id, status="failed", error_message=str(e))
    finally:
        Path(file_path).unlink(missing_ok=True)

@router.get("/{job_id}/status")
async def get_job_status(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return {
        "status": job.status,
        "error": job.error_message,
    }
    
@router.get("/{job_id}/result")
async def get_job_result(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.status != "completed":
        raise HTTPException(status_code=400, detail="Job is not completed yet.")
    return job.minutes
    
