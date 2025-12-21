import asyncio
import uuid
from fastapi import APIRouter
from ..services.simulated_work import simulated_work, get_job_status, get_job_result, jobs

router = APIRouter()

@router.post("/process")
async def process_request(data: dict):
    job_id = str(uuid.uuid4())
    asyncio.create_task(simulated_work(job_id))
    return job_id

@router.get("/status/{job_id}")
async def check_status(job_id: str):
    status = await get_job_status(job_id)
    return status

# For long polling
@router.get("/result/{job_id}")
async def get_result(job_id: str):
    result = await get_job_result(job_id)
    return result