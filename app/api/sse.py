from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from ..services.simulated_work import get_job_status_stream

router = APIRouter()

@router.get("/stream/{job_id}")
async def stream_job_status(job_id: str):
    return StreamingResponse(get_job_status_stream(job_id), media_type="text/event-stream")