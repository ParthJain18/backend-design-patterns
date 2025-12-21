from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import time
import json
from ..services.simulated_work import jobs, get_job_status_stream


router = APIRouter()

@router.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await websocket.accept()
    try:
        start_time = time.time()
        timeout = 30  # seconds

        while time.time() - start_time < timeout:
            job = jobs.get(job_id)
            if job:
                await websocket.send_text(json.dumps(job))
                if job["status"] == "completed":
                    break
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for job_id: {job_id}")
