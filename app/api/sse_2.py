import uuid
import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from ..services.simulated_work import get_job_status_stream_2, simulated_work_queue

router = APIRouter()

@router.post("/process")
async def process_request(data: dict):
    job_id = str(uuid.uuid4())
    asyncio.create_task(simulated_work_queue(job_id))
    return job_id

@router.get("/stream/{job_id}")
async def stream_job_status(job_id: str):
    return StreamingResponse(get_job_status_stream_2(job_id), media_type="text/event-stream")