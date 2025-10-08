"""
PHASE 2: Celery Tasks for Audio Processing
Asynchronous audio enhancement and transcription tasks
"""

import os
import logging
import tempfile
import traceback
from pathlib import Path
from typing import Dict, Any, Optional
import asyncio

from celery import Task
from celery_app import app
from audio_processor import audio_processor

logger = logging.getLogger(__name__)

class CallbackTask(Task):
    """Base task class with error handling and progress updates"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails"""
        logger.error(f'Task {task_id} failed: {exc}')
        logger.error(f'Traceback: {einfo}')
    
    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds"""
        logger.info(f'Task {task_id} completed successfully')
    
    def update_progress(self, current: int, total: int, message: str = ""):
        """Update task progress"""
        self.update_state(
            state='PROGRESS',
            meta={
                'current': current,
                'total': total,
                'message': message,
                'percentage': int((current / total) * 100)
            }
        )

@app.task(bind=True, base=CallbackTask, name='celery_tasks.process_audio_async')
def process_audio_async(self, file_path: str, session_id: str, enhance_audio: bool = True) -> Dict[str, Any]:
    """
    PHASE 2: Complete audio processing pipeline (async)
    
    Args:
        file_path: Path to audio file to process
        session_id: Auto-Note Mentor session ID
        enhance_audio: Whether to apply audio enhancement
        
    Returns:
        Dict containing processing results
    """
    try:
        logger.info(f"Starting async audio processing for session {session_id}")
        self.update_progress(10, 100, "Initializing audio processing...")
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        # Step 1: Load audio
        self.update_progress(20, 100, "Loading audio file...")
        
        # Since we're in a sync context, we need to handle the async call properly
        def run_async_processing():
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    audio_processor.process_audio_file(file_path, enhance_audio)
                )
            finally:
                loop.close()
        
        self.update_progress(30, 100, "Enhancing audio quality...")
        
        # Process audio
        result = run_async_processing()
        
        self.update_progress(90, 100, "Finalizing results...")
        
        # Add session metadata
        result['session_id'] = session_id
        result['processed_file'] = file_path
        
        self.update_progress(100, 100, "Audio processing completed!")
        
        logger.info(f"Audio processing completed for session {session_id}")
        return {
            'status': 'success',
            'data': result
        }
        
    except Exception as e:
        logger.error(f"Audio processing failed for session {session_id}: {e}")
        logger.error(traceback.format_exc())
        
        return {
            'status': 'error',
            'error': str(e),
            'session_id': session_id
        }

@app.task(bind=True, base=CallbackTask, name='celery_tasks.enhance_audio_async')  
def enhance_audio_async(self, file_path: str, output_path: str) -> Dict[str, Any]:
    """
    PHASE 2: Audio enhancement only (async)
    
    Args:
        file_path: Input audio file path
        output_path: Output enhanced audio file path
        
    Returns:
        Dict containing enhancement results
    """
    try:
        logger.info(f"Starting audio enhancement: {file_path}")
        self.update_progress(20, 100, "Loading audio for enhancement...")
        
        # Load audio
        audio_data, sr = audio_processor._load_audio(file_path)
        
        self.update_progress(50, 100, "Applying audio enhancement...")
        
        # Run enhancement
        def run_async_enhancement():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    audio_processor._enhance_audio(audio_data, sr)
                )
            finally:
                loop.close()
        
        enhanced_audio = run_async_enhancement()
        
        self.update_progress(80, 100, "Saving enhanced audio...")
        
        # Save enhanced audio
        import soundfile as sf
        sf.write(output_path, enhanced_audio, sr)
        
        self.update_progress(100, 100, "Audio enhancement completed!")
        
        # Analyze quality improvement
        original_analysis = audio_processor._analyze_audio_quality(audio_data, sr)
        enhanced_analysis = audio_processor._analyze_audio_quality(enhanced_audio, sr)
        
        return {
            'status': 'success',
            'enhanced_file': output_path,
            'original_quality': original_analysis,
            'enhanced_quality': enhanced_analysis,
            'improvement': {
                'quality_score_delta': enhanced_analysis['quality_score'] - original_analysis['quality_score'],
                'snr_improvement_db': enhanced_analysis['snr_estimate_db'] - original_analysis['snr_estimate_db']
            }
        }
        
    except Exception as e:
        logger.error(f"Audio enhancement failed: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

@app.task(bind=True, base=CallbackTask, name='celery_tasks.transcribe_audio_async')
def transcribe_audio_async(self, file_path: str, language: str = 'en') -> Dict[str, Any]:
    """
    PHASE 2: Transcription only (async)
    
    Args:
        file_path: Audio file to transcribe
        language: Target language for transcription
        
    Returns:
        Dict containing transcription results
    """
    try:
        logger.info(f"Starting transcription: {file_path}")
        self.update_progress(20, 100, "Loading audio for transcription...")
        
        # Load and prepare audio
        audio_data, sr = audio_processor._load_audio(file_path)
        
        self.update_progress(40, 100, "Preparing audio for Whisper...")
        
        # Resample to Whisper's preferred rate
        if sr != audio_processor.sample_rate:
            import librosa
            audio_data = librosa.resample(audio_data, orig_sr=sr, target_sr=audio_processor.sample_rate)
        
        self.update_progress(60, 100, "Running Whisper transcription...")
        
        # Transcribe
        def run_async_transcription():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    audio_processor._transcribe_with_whisper(audio_data)
                )
            finally:
                loop.close()
        
        result = run_async_transcription()
        
        self.update_progress(90, 100, "Analyzing context...")
        
        # Add context analysis
        context_info = audio_processor._detect_context(result['text'])
        result['context_info'] = context_info
        
        self.update_progress(100, 100, "Transcription completed!")
        
        return {
            'status': 'success',
            'transcription': result
        }
        
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

@app.task(bind=True, base=CallbackTask, name='celery_tasks.batch_process_audio_chunks')
def batch_process_audio_chunks(self, chunk_paths: list, session_id: str) -> Dict[str, Any]:
    """
    PHASE 2: Process multiple audio chunks in sequence
    Useful for live recording where audio comes in chunks
    
    Args:
        chunk_paths: List of audio chunk file paths
        session_id: Session ID for tracking
        
    Returns:
        Combined processing results
    """
    try:
        logger.info(f"Processing {len(chunk_paths)} audio chunks for session {session_id}")
        
        combined_transcript = ""
        all_segments = []
        quality_metrics = []
        
        total_chunks = len(chunk_paths)
        
        for i, chunk_path in enumerate(chunk_paths):
            self.update_progress(
                int((i / total_chunks) * 90), 
                100, 
                f"Processing chunk {i+1}/{total_chunks}..."
            )
            
            # Process individual chunk
            chunk_result = process_audio_async.apply(
                args=[chunk_path, session_id, True]
            ).get()
            
            if chunk_result['status'] == 'success':
                data = chunk_result['data']
                combined_transcript += " " + data['transcription']
                all_segments.extend(data.get('segments', []))
                quality_metrics.append(data['audio_analysis'])
            else:
                logger.warning(f"Chunk {i+1} processing failed: {chunk_result['error']}")
        
        self.update_progress(95, 100, "Combining results...")
        
        # Calculate average quality metrics
        avg_quality = {}
        if quality_metrics:
            numeric_fields = ['rms_level', 'peak_level', 'snr_estimate_db', 'quality_score']
            for field in numeric_fields:
                values = [m.get(field, 0) for m in quality_metrics if field in m]
                avg_quality[field] = sum(values) / len(values) if values else 0
        
        # Final context analysis on combined transcript
        context_info = audio_processor._detect_context(combined_transcript.strip())
        
        self.update_progress(100, 100, "Batch processing completed!")
        
        return {
            'status': 'success',
            'session_id': session_id,
            'combined_transcript': combined_transcript.strip(),
            'total_segments': len(all_segments),
            'processed_chunks': len(chunk_paths),
            'average_quality': avg_quality,
            'context_info': context_info
        }
        
    except Exception as e:
        logger.error(f"Batch processing failed for session {session_id}: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'session_id': session_id
        }