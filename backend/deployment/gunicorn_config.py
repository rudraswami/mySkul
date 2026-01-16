"""
🚀 Gunicorn Production Configuration - Cognito OS v1.0
======================================================

Multi-worker deployment configuration for production.

Usage:
    gunicorn main:app -c deployment/gunicorn_config.py

Environment Variables:
    WEB_CONCURRENCY: Number of worker processes (default: CPU * 2 + 1)
    PORT: Server port (default: 8001)
    LOG_LEVEL: Logging level (default: info)
    WORKER_TIMEOUT: Worker timeout in seconds (default: 30)
    GRACEFUL_TIMEOUT: Graceful shutdown timeout (default: 10)
"""

import multiprocessing
import os

# =============================================================================
# WORKER CONFIGURATION
# =============================================================================

# Number of workers
# Rule of thumb: 2 * CPU cores + 1 for I/O-bound workloads
# Our workload is mostly I/O (LLM API calls, DB queries)
workers = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))

# Worker class - use uvicorn for async support
worker_class = "uvicorn.workers.UvicornWorker"

# Max number of simultaneous clients
worker_connections = 1000

# Restart workers after N requests (prevents memory leaks)
max_requests = 10000
max_requests_jitter = 1000  # Add randomness to prevent thundering herd

# Worker timeout
# CRITICAL: Must be > SUPERVISOR_TIMEOUT (20s) + buffer
timeout = int(os.getenv("WORKER_TIMEOUT", "30"))

# Graceful shutdown timeout
graceful_timeout = int(os.getenv("GRACEFUL_TIMEOUT", "10"))

# Keep-alive connections
keepalive = 5

# =============================================================================
# SERVER SOCKET
# =============================================================================

# Bind address
bind = f"0.0.0.0:{os.getenv('PORT', '8001')}"

# Backlog (pending connections queue)
backlog = 2048

# =============================================================================
# LOGGING
# =============================================================================

# Access log
accesslog = "-"  # stdout

# Error log
errorlog = "-"  # stderr

# Log level
loglevel = os.getenv("LOG_LEVEL", "info")

# Access log format
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# =============================================================================
# PROCESS NAMING
# =============================================================================

proc_name = "cognito-os"

# =============================================================================
# HOOKS
# =============================================================================

def on_starting(server):
    """Called just before the master process is initialized."""
    import logging
    logging.info("🚀 Cognito OS starting (Gunicorn master)")


def post_fork(server, worker):
    """Called just after a worker has been forked."""
    import logging
    logging.info(f"👷 Worker {worker.pid} spawned")
    
    # Reset scalability singletons for this worker
    # Each worker needs its own instances
    try:
        from services.scalability import reset_singletons
        reset_singletons()
    except ImportError:
        pass


def worker_int(worker):
    """Called when a worker receives SIGINT/SIGTERM."""
    import logging
    logging.info(f"🛑 Worker {worker.pid} interrupted")


def worker_abort(worker):
    """Called when a worker times out."""
    import logging
    logging.error(f"💀 Worker {worker.pid} aborted (timeout)")


def pre_exec(server):
    """Called just before a new master process is forked."""
    import logging
    logging.info("🔄 Gunicorn pre-exec (forking new master)")


def on_exit(server):
    """Called just before exiting Gunicorn."""
    import logging
    logging.info("👋 Cognito OS shutting down")


# =============================================================================
# SECURITY
# =============================================================================

# Limit request line size (prevents DoS)
limit_request_line = 8190

# Limit request fields (headers)
limit_request_fields = 100
limit_request_field_size = 8190
