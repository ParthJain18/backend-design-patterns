from fastapi import FastAPI
from app.api import req_resp, polling, sse, sse_2, websocket


app = FastAPI()

app.include_router(req_resp.router, prefix="/api/req_resp", tags=["Request-Response"])
app.include_router(polling.router, prefix="/api/polling", tags=["Polling"])
app.include_router(sse.router, prefix="/api/sse", tags=["Server-Sent Events"])
app.include_router(sse_2.router, prefix="/api/sse_2", tags=["SSE Queue-based"])
app.include_router(websocket.router, prefix="/api/websocket", tags=["WebSocket"])

def main():
    print("Hello from backend-design-patterns!")
    import uvicorn
    uvicorn.run(app, port=8000)


if __name__ == "__main__":
    main()
