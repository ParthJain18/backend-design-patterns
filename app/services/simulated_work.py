import asyncio
import time
import json

jobs = {}
jobs_2 = {}

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


async def simulated_work_queue(job_id: str) -> dict:
    jobs_2[job_id] = asyncio.Queue()
    job = {"status": "in_progress", "progress": 0, "started_at": time.time()}
    await jobs_2[job_id].put(job)
    
    for i in range(100):
        job["progress"] = i + 1
        await jobs_2[job_id].put(job.copy())
        await asyncio.sleep(0.1)

    job["status"] = "completed"
    job["completed_at"] = time.time()
    await jobs_2[job_id].put(job.copy())

    return job


async def get_job_status_stream_2(job_id: str):
    queue = jobs_2.get(job_id)

    if not queue:
        yield f"data: {json.dumps({'status': 'not_found'})}\n\n"
        return

    while True:
        data = await queue.get() # type: ignore
        yield f"data: {json.dumps(data)}\n\n"
        
        if data["status"] == "completed":
            break
        
    jobs_2[job_id].task_done()
    jobs_2.pop(job_id, None)