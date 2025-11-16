
import multiprocessing

# Configuración específica para Render
bind = "0.0.0.0:10000"
workers = 1  # Para el plan free, 1 worker es suficiente
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True