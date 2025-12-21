
# Benchmarks

## Stress Test (5,000 Users)
Ran with **5,000 users** on a local machine (Linux), spawning 500 users/sec.
**Note:** System CPU was saturated (>90%). Client and Server ran on the same machine.

| Strategy | RPS | Avg Latency (ms) | Fail Rate (%) | Notes |
|----------|-----|------------------|---------------|-------|
| Req/Resp | 317.51 | 11,491 | 0.00% | Most stable and lowest latency under load. |
| Short Polling | 117.81 | 19,578 | 0.00% | High overhead, stable but slow. |
| Long Polling | 251.05 | 13,978 | 0.00% | Surprisingly performant, second best throughput. |
| SSE | 32.55 | 19,642 | 0.00% | Streaming is efficient for the Network, but heavy for the CPU/Event Loop. |
| WebSocket | 105.37 | 34,525 | 42.72% | Massive connection drops. Server loop saturation. |
