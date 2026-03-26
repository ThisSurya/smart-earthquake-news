import time
import requests
import os
import sys
from datetime import datetime

# URL for the cron job endpoint
# When running inside Docker, use 'backend' (service name) or 'localhost' if running locally
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")  # Default to 'backend' for Docker, can be overridden by env variable
CRON_ENDPOINT = f"{BACKEND_URL}/news/cron"
INTERVAL_MINUTES = 5

def trigger_cron():
    """Execute a single call to the cron endpoint."""
    try:
        print(f"[{datetime.now()}] Triggering cron job at {CRON_ENDPOINT}...")
        response = requests.post(CRON_ENDPOINT)
        
        if response.status_code == 201:
            data = response.json()
            print(f"[{datetime.now()}] Success: {data.get('message')}")
            print(f"Total clusters processed: {data.get('total_clusters')}")
            return True
        else:
            print(f"[{datetime.now()}] Error: Received status code {response.status_code}")
            print(response.text)
            return False
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now()}] Connection error: {e}")
        return False
    except Exception as e:
        print(f"[{datetime.now()}] Unexpected error: {e}")
        return False

def run_loop():
    """Run the trigger continuously with a delay."""
    print(f"[{datetime.now()}] Starting continuous cron trigger loop...")
    print(f"Interval: {INTERVAL_MINUTES} minutes")
    
    while True:
        trigger_cron()
        print(f"[{datetime.now()}] Waiting {INTERVAL_MINUTES} minutes for next run...")
        time.sleep(INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        if trigger_cron():
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        run_loop()
