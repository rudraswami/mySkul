"""
PHASE 2: Celery Task Queue Configuration
Handles asynchronous audio processing tasks
"""

import os
import logging
from celery import Celery
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis configuration for Celery broker
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Create Celery application
app = Celery(
    'dhruv_ai_audio_processor',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['celery_tasks']  # Import tasks module
)

# Celery configuration
app.conf.update(
    # Task configuration
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task routing
    task_routes={
        'celery_tasks.process_audio_async': {'queue': 'audio_processing'},
        'celery_tasks.enhance_audio_async': {'queue': 'audio_enhancement'},
        'celery_tasks.transcribe_audio_async': {'queue': 'transcription'},
    },
    
    # Worker configuration
    worker_prefetch_multiplier=1,  # Process one task at a time for memory efficiency
    task_acks_late=True,           # Acknowledge tasks only after completion
    worker_disable_rate_limits=False,
    
    # Task time limits (important for audio processing)
    task_time_limit=300,           # 5 minutes max per task
    task_soft_time_limit=240,      # Soft limit at 4 minutes
    
    # Result backend settings
    result_expires=3600,           # Results expire after 1 hour
    result_compression='gzip',
    
    # Task retry configuration
    task_reject_on_worker_lost=True,
    task_acks_on_failure_or_timeout=True,
)

# Queue configuration
app.conf.task_default_queue = 'default'
app.conf.task_queues = {
    'audio_processing': {
        'exchange': 'audio_processing',
        'routing_key': 'audio_processing',
    },
    'audio_enhancement': {
        'exchange': 'audio_enhancement', 
        'routing_key': 'audio_enhancement',
    },
    'transcription': {
        'exchange': 'transcription',
        'routing_key': 'transcription',
    },
}

if __name__ == '__main__':
    app.start()