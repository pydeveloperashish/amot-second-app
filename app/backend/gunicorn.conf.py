import multiprocessing
import os

max_requests = 1000
max_requests_jitter = 50
log_file = "-"
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
worker_tmp_dir = "/dev/shm"  # Use RAM-based directory for worker temp files
preload_app = True  # Preload application code before worker processes are forked

timeout = 230
graceful_timeout = 30  # Time to wait for worker to finish handling requests before force killing
# https://learn.microsoft.com/troubleshoot/azure/app-service/web-apps-performance-faqs#why-does-my-request-time-out-after-230-seconds

num_cpus = multiprocessing.cpu_count()
if os.getenv("WEBSITE_SKU") == "LinuxFree":
    # Free tier reports 2 CPUs but can't handle multiple workers
    workers = 1
else:
    workers = (num_cpus * 2) + 1
worker_class = "custom_uvicorn_worker.CustomUvicornWorker"
keepalive = 5  # How long to wait for requests before closing connection
