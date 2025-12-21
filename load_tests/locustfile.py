import time
import json
import gevent
from locust import HttpUser, task, between, events, User
import websocket

# --- Helper to track full job duration ---
def track_job_duration(request_type, name, start_time, exception=None):
    duration = (time.time() - start_time) * 1000
    events.request.fire(
        request_type=request_type,
        name=name,
        response_time=duration,
        response_length=0,
        exception=exception,
    )

# 13-15%
class ReqRespUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def process_job(self):
        start_time = time.time()
        # This is a blocking call
        with self.client.post("/api/req_resp/process", json={"data": {}}, catch_response=True) as response:
            if response.status_code == 200:
                track_job_duration("Job", "Req/Resp Full", start_time)
                response.success()
            else:
                response.failure(f"Failed with {response.status_code}")

# 23-30%
class ShortPollingUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def process_job(self):
        job_start_time = time.time()
        
        # 1. Start Job
        res = self.client.post("/api/polling/process", json={"data": {}})
        if res.status_code != 200:
            return
        
        job_id = res.json()
        
        # 2. Poll Loop
        while True:
            # We tag this as "Poll Request" to separate it from the full job time
            with self.client.get(f"/api/polling/status/{job_id}", name="/api/polling/status/[id]", catch_response=True) as response:
                if response.status_code == 200:
                    data = response.json()
                    if data["status"] == "completed":
                        track_job_duration("Job", "Short Poll Full", job_start_time)
                        break
                    # Wait 1s before next poll (simulating client logic)
                    time.sleep(1)
                else:
                    response.failure("Polling failed")
                    break

# 15-20% Ocassional Spikes
class LongPollingUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def process_job(self):
        job_start_time = time.time()
        
        # 1. Start Job
        res = self.client.post("/api/polling/process", json={"data": {}})
        if res.status_code != 200:
            return
        job_id = res.json()

        # 2. Long Poll (Waits on server)
        # We increase timeout because long poll hangs
        with self.client.get(f"/api/polling/result/{job_id}", name="/api/polling/result/[id]", timeout=60, catch_response=True) as response:
            if response.status_code == 200:
                track_job_duration("Job", "Long Poll Full", job_start_time)
            else:
                response.failure(f"Long poll failed: {response.status_code}")

# 15-20%
class SSEUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def process_job(self):
        job_start_time = time.time()
        
        # 1. Start Job
        res = self.client.post("/api/polling/process", json={"data": {}})
        if res.status_code != 200:
            return
        job_id = res.json()

        # 2. Stream
        try:
            # stream=True is key here
            with self.client.get(f"/api/sse/stream/{job_id}", name="/api/sse/stream/[id]", stream=True, timeout=60, catch_response=True) as response:
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith("data:"):
                            data_str = decoded_line.replace("data: ", "")
                            try:
                                data = json.loads(data_str)
                                if data["status"] == "completed":
                                    track_job_duration("Job", "SSE Full", job_start_time)
                                    response.success()
                                    break
                            except:
                                pass
        except Exception as e:
            events.request.fire(
                request_type="Job",
                name="SSE Full",
                response_time=(time.time() - job_start_time) * 1000,
                response_length=0,
                exception=e,
            )

# 20-30%
class WebSocketUser(User):
    # WebSocketUser doesn't inherit from HttpUser because we use a raw socket
    wait_time = between(1, 3)

    def on_start(self):
        # We need to manually handle the host since we aren't using self.client
        self.host = self.host or "http://localhost:8000"

    @task
    def process_job(self):
        # We need a standard HTTP client just to trigger the job first
        # We can use requests directly or a lightweight wrapper. 
        # Locust 'User' doesn't have 'client', so we import requests.
        import requests
        
        job_start_time = time.time()
        
        try:
            # 1. Start Job (Standard HTTP)
            # Use self.host to build URL
            res = requests.post(f"{self.host}/api/polling/process", json={"data": {}})
            if res.status_code != 200:
                events.request.fire(request_type="HTTP", name="WS Trigger", response_time=0, exception=Exception("Trigger Failed"))
                return
            
            job_id = res.json()

            # 2. WebSocket Connection
            ws_url = str(self.host).replace("http", "ws") + f"/api/websocket/ws/{job_id}"
            
            ws = websocket.create_connection(ws_url, timeout=60)
            
            while True:
                result = ws.recv()
                data = json.loads(result)
                if data["status"] == "completed":
                    track_job_duration("Job", "WebSocket Full", job_start_time)
                    ws.close()
                    break
                    
        except Exception as e:
            track_job_duration("Job", "WebSocket Full", job_start_time, exception=e)

