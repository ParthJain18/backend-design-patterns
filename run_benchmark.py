import subprocess
import time
import os
import signal
import sys
import csv

# Configurations
USERS = 5000
SPAWN_RATE = 500
RUN_TIME = "60s"
HOST = "http://localhost:8000"
CSV_PREFIX = "benchmark_results"

STRATEGIES = [
    "ReqRespUser",
    "ShortPollingUser",
    "LongPollingUser",
    "SSEUser",
    "WebSocketUser"
]

def run_benchmark():
    results = []

    # Ensure clean state
    subprocess.run(["pkill", "uvicorn"], stderr=subprocess.DEVNULL)
    
    print(f"Starting Benchmark: {USERS} Users, {SPAWN_RATE} Spawn Rate, {RUN_TIME} Duration")
    print("-" * 60)

    for strategy in STRATEGIES:
        print(f"Testing Strategy: {strategy}")
        
        # 1. Start Server
        # using 'setsid' to easily kill the process group later if needed
        server_log = open(f"server_{strategy}.log", "w")
        server_process = subprocess.Popen(
            ["uvicorn", "main:app", "--workers", "1", "--port", "8000", "--log-level", "warning"],
            stdout=server_log,
            stderr=server_log,
            preexec_fn=os.setsid
        )
        
        # Wait for server to start
        time.sleep(3)
        
        if server_process.poll() is not None:
            print(f"Server failed to start for {strategy}. Check logs.")
            continue

        # 2. Run Locust
        csv_filename = f"{CSV_PREFIX}_{strategy}"
        # We need to use the venv's locust
        cmd = [
            "locust",
            "-f", "load_tests/locustfile.py",
            "--headless",
            "-u", str(USERS),
            "-r", str(SPAWN_RATE),
            "--run-time", RUN_TIME,
            "--host", HOST,
            "--csv", csv_filename,
            strategy
        ]
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f"Locust failed for {strategy}: {e.stderr.decode()}")
        
        # 3. Stop Server
        os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
        server_process.wait()
        server_log.close()
        
        # 4. Parse Results
        try:
            # Locust generates {csv_filename}_stats.csv
            stats_file = f"{csv_filename}_stats.csv"
            
            target_name_map = {
                "ReqRespUser": "Req/Resp Full",
                "ShortPollingUser": "Short Poll Full",
                "LongPollingUser": "Long Poll Full",
                "SSEUser": "SSE Full",
                "WebSocketUser": "WebSocket Full"
            }
            target_name = target_name_map[strategy]
            
            with open(stats_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                found = False
                for row in reader:
                    if row["Name"] == target_name:
                        req_count = int(row["Request Count"])
                        fail_count = int(row["Failure Count"])
                        rps = float(row["Requests/s"])
                        avg_latency = float(row["Average Response Time"])
                        
                        total = req_count + fail_count
                        fail_rate = (fail_count / total * 100) if total > 0 else 0
                        
                        results.append({
                            "Strategy": strategy,
                            "RPS": rps,
                            "Avg Latency (ms)": avg_latency,
                            "Fail Rate (%)": fail_rate
                        })
                        found = True
                        break
                
                if not found:
                     results.append({
                        "Strategy": strategy,
                        "RPS": 0,
                        "Avg Latency (ms)": 0,
                        "Fail Rate (%)": 100,
                        "Note": "Target request not found in CSV"
                    })

        except Exception as e:
            print(f"Error parsing results for {strategy}: {e}")
            
        print(f"Finished {strategy}\n")
        time.sleep(2) # Cooldown

    # Print Table
    print("\nFinal Results:")
    print(f"{ 'Strategy':<20} | { 'RPS':<10} | { 'Avg Latency (ms)':<18} | { 'Fail Rate (%)':<15}")
    print("-" * 70)
    for r in results:
        print(f"{r['Strategy']:<20} | {r['RPS']:<10.2f} | {r['Avg Latency (ms)']:<18.2f} | {r['Fail Rate (%)']:<15.2f}")

if __name__ == "__main__":
    run_benchmark()
