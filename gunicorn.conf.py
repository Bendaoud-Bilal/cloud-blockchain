# Gunicorn Configuration for Render Deployment
# This file is optional - you can also pass options via command line

import os

# Server Socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Worker Processes
workers = 2  # Keep low for free tier
worker_class = "sync"  # Use sync workers for Flask
worker_connections = 1000

# Timeout
timeout = 120  # Increase for blockchain operations
graceful_timeout = 30
keepalive = 5

# Server Mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
errorlog = "-"  # Log to stderr
accesslog = "-"  # Log to stdout
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process Naming
proc_name = "blockchain"

# Server Hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print("🚀 Starting Gunicorn server...")

def on_reload(server):
    """Called when a worker received a SIGHUP."""
    print("🔄 Reloading Gunicorn server...")

def worker_int(worker):
    """Called when a worker received a SIGINT or SIGQUIT."""
    print(f"⛔ Worker {worker.pid} interrupted")

def worker_abort(worker):
    """Called when a worker received a SIGABRT."""
    print(f"💥 Worker {worker.pid} aborted")

def pre_fork(server, worker):
    """Called just prior to forking the worker subprocess."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    print(f"✅ Worker {worker.pid} spawned")

def pre_exec(server):
    """Called just prior to forking off a secondary master process."""
    pass

def when_ready(server):
    """Called just after the server is started."""
    print(f"✅ Gunicorn server ready. Listening on {bind}")
