import multiprocessing
import os

# Bind to all interfaces on port 8000
bind = os.getenv("BIND", "0.0.0.0:8000")

# Calculate workers based on CPU cores
# Rule of thumb: (2 x CPU cores) + 1
workers = int(os.getenv("WORKERS", multiprocessing.cpu_count() * 2 + 1))

# Use Uvicorn's async worker class for ASGI support
worker_class = "uvicorn.workers.UvicornWorker"

# Timeout for worker processes (seconds)
# Increase if you have slow endpoints
timeout = int(os.getenv("TIMEOUT", 120))

# Restart workers after this many requests to prevent memory leaks
max_requests = int(os.getenv("MAX_REQUESTS", 1000))
max_requests_jitter = int(os.getenv("MAX_REQUESTS_JITTER", 50))

# Graceful timeout - time to finish current requests before force kill
graceful_timeout = 30

# Keep-alive connections
keepalive = 5

# Logging configuration
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = os.getenv("LOG_LEVEL", "info")

# Process naming for easier identification in ps/htop
proc_name = "fastapi-app"

# Preload application code before forking workers
# Saves memory through copy-on-write but means code changes require full restart
preload_app = True