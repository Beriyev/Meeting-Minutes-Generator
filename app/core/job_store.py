from app.models.schemas import MeetingJob
from datetime import datetime

__job_store: dict[str, MeetingJob] = {}

def create_job(job_id: str) -> MeetingJob:
    job = MeetingJob(
        job_id = job_id,
        status = "pending",
        created_at = datetime.now(),
    )
    __job_store[job_id] = job
    return job

def get_job(job_id: str) -> MeetingJob | None:
    if job_id in __job_store:
        return __job_store[job_id]
    else:
        return None
    
def update_job(**kwargs) -> MeetingJob | None:
    job_id = kwargs.get("job_id")
    if not job_id:
        raise ValueError("job_id is required to update a job")
    if not job_id in __job_store:
        raise ValueError(f"Job with job_id {job_id} does not exist")
    duplicate_job = __job_store[job_id].model_copy(update=kwargs)
    __job_store[job_id] = duplicate_job
    return __job_store[job_id]