import uuid
from fastapi import APIRouter
from ..services.simulated_work import simulated_work, get_job_status, jobs

router = APIRouter()

@router.post("/process")
async def process_request(data: dict):
    job_id = str(uuid.uuid4())
    job = await simulated_work(job_id)
    return job

