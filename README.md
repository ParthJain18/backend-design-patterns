
# Benchmarks

Ran with **5000 users** on a local machine (Linux), spawning 250 users/sec.

| Strategy | RPS | Avg Latency (ms) | Fail Rate (%) | Avg CPU Usage (%) |
|----------|-----|------------------|---------------|-------------------|
| Req/Resp | 248.92 | 12,918 | 0.00% | 25.17% |
| Short Polling | 120.55 | 19,706 | 0.00% | 24.96% |
| Long Polling | 192.33 | 16,594 | 0.00% | 25.95% |
| SSE | 8.33 | 27,557 | 0.00% | 28.27% |
| WebSocket | 83.72 | 36,611 | 100.00%* | 29.31% |

*WebSocket failed to sustain connections at this concurrency level (likely file descriptor or client-side limitation).*
