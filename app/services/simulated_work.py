import asyncio
import time
import json

jobs = {}

async def simulated_work(job_id: str) -> dict:
    jobs[job_id] = {"status": "in_progress", "progress": 0, "started_at": time.time()}
    
    for i in range(100):
        jobs[job_id]["progress"] = i + 1
        await asyncio.sleep(0.1)

    jobs[job_id]["status"] = "completed"
    jobs[job_id]["completed_at"] = time.time()
    return jobs[job_id]

async def get_job_status(job_id: str) -> dict:
    return jobs.get(job_id, {"status": "not_found"})

# For long polling
async def get_job_result(job_id: str) -> dict:
    start_time = time.time()
    timeout = 30  # seconds

    while time.time() - start_time < timeout:
        job = jobs.get(job_id)
        if job and job["status"] == "completed":
            return job
        await asyncio.sleep(1)
    
    return {"status": "timeout"}

# For Server-Sent Events (SSE)
async def get_job_status_stream(job_id: str):
    start_time = time.time()
    timeout = 30  # seconds

    while time.time() - start_time < timeout:
        job = jobs.get(job_id)
        if job:
            yield f"data: {json.dumps(job)}\n\n"
            if job["status"] == "completed":
                return
        await asyncio.sleep(0.1)