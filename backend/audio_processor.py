"""
PHASE 2: Audio Processing Pipeline
Enhanced audio processing with Whisper, noise reduction, and quality enhancement
"""

import os
import io
import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import numpy as np

# Audio processing libraries
import librosa
import noisereduce as nr
from pydub import AudioSegment
import whisper

# ML libraries
import torch
from scipy import signal
from scipy.ndimage import gaussian_filter1d

logger = logging.getLogger(__name__)

class AudioProcessor:
    """
    PHASE 2: Enhanced Audio Processing Pipeline
    Provides studio-quality audio enhancement and transcription
    """
    
    def __init__(self):
        self.whisper_model = None
        self.sample_rate = 16000  # Whisper's preferred sample rate
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_whisper_model()
        
    def _load_whisper_model(self):
        """Load Whisper model (base model for balance of speed/accuracy)"""
        try:
            # Use base model for good balance of speed and accuracy
            # Can be upgraded to 'large' for PRO users later
            model_name = "base"
            logger.info(f"Loading Whisper model '{model_name}' on {self.device}")
            self.whisper_model = whisper.load_model(model_name, device=self.device)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    async def process_audio_file(self, file_path: str, enhance_audio: bool = True) -> Dict[str, Any]:
        """
        Complete audio processing pipeline
        
        Args:
            file_path: Path to input audio file
            enhance_audio: Whether to apply audio enhancement
            
        Returns:
            Dict containing transcription and analysis results
        """
        try:
            # Step 1: Load and normalize audio
            logger.info(f"Processing audio file: {file_path}")
            audio_data, sr = self._load_audio(file_path)
            
            # Step 2: Enhance audio quality (if requested)
            if enhance_audio:
                audio_data = await self._enhance_audio(audio_data, sr)
            
            # Step 3: Prepare for Whisper (resample to 16kHz)
            if sr != self.sample_rate:
                audio_data = librosa.resample(audio_data, orig_sr=sr, target_sr=self.sample_rate)
            
            # Step 4: Transcribe with Whisper
            transcription_result = await self._transcribe_with_whisper(audio_data)
            
            # Step 5: Audio analysis
            audio_analysis = self._analyze_audio_quality(audio_data, self.sample_rate)
            
            # Step 6: Enhanced context detection with segments
            context_info = self._detect_context(
                transcription_result['text'], 
                transcription_result.get('segments', [])
            )
            
            return {
                'transcription': transcription_result['text'],
                'segments': transcription_result['segments'],
                'language': transcription_result.get('language', 'en'),
                'audio_analysis': audio_analysis,
                'context_info': context_info,
                'processing_stats': {
                    'original_sample_rate': sr,
                    'processed_sample_rate': self.sample_rate,
                    'enhancement_applied': enhance_audio,
                    'duration_seconds': len(audio_data) / self.sample_rate
                }
            }
            
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            raise
    
    def _load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """Load audio file and convert to numpy array"""
        try:
            # Use librosa for robust audio loading
            audio_data, sample_rate = librosa.load(file_path, sr=None, mono=True)
            logger.info(f"Loaded audio: {len(audio_data)} samples at {sample_rate}Hz")
            return audio_data, sample_rate
        except Exception as e:
            # Fallback to pydub for other formats
            logger.warning(f"Librosa failed, trying pydub: {e}")
            try:
                audio = AudioSegment.from_file(file_path)
                audio = audio.set_channels(1)  # Convert to mono
                sample_rate = audio.frame_rate
                audio_data = np.array(audio.get_array_of_samples(), dtype=np.float32)
                audio_data = audio_data / (2**15)  # Normalize to [-1, 1]
                return audio_data, sample_rate
            except Exception as e2:
                logger.error(f"Both librosa and pydub failed: {e2}")
                raise
    
    async def _enhance_audio(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        PHASE 2: Advanced audio enhancement pipeline
        """
        try:
            logger.info("Starting audio enhancement pipeline")
            
            # Step 1: Noise reduction using noisereduce
            logger.debug("Applying noise reduction")
            enhanced_audio = nr.reduce_noise(
                y=audio_data, 
                sr=sample_rate,
                stationary=False,  # For non-stationary noise (classroom environment)
                prop_decrease=0.8   # Reduce noise by 80%
            )
            
            # Step 2: Dynamic range compression (prevent clipping)
            logger.debug("Applying dynamic range compression")
            enhanced_audio = self._apply_compression(enhanced_audio)
            
            # Step 3: Spectral enhancement
            logger.debug("Applying spectral enhancement")
            enhanced_audio = self._spectral_enhancement(enhanced_audio, sample_rate)
            
            # Step 4: Normalize volume
            logger.debug("Normalizing audio levels")
            enhanced_audio = self._normalize_audio(enhanced_audio)
            
            logger.info("Audio enhancement completed")
            return enhanced_audio
            
        except Exception as e:
            logger.error(f"Audio enhancement failed: {e}")
            # Return original audio if enhancement fails
            return audio_data
    
    def _apply_compression(self, audio_data: np.ndarray, 
                          threshold: float = 0.7, 
                          ratio: float = 4.0) -> np.ndarray:
        """Apply dynamic range compression to prevent clipping"""
        # Simple threshold-based compression
        compressed = np.copy(audio_data)
        
        # Find samples above threshold
        above_thresh = np.abs(compressed) > threshold
        
        # Apply compression to loud samples
        compressed[above_thresh] = np.sign(compressed[above_thresh]) * (
            threshold + (np.abs(compressed[above_thresh]) - threshold) / ratio
        )
        
        return compressed
    
    def _spectral_enhancement(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Enhance speech frequencies using spectral filtering"""
        try:
            # Human speech frequency range enhancement (300-3400 Hz)
            nyquist = sample_rate // 2
            low_freq = 300 / nyquist
            high_freq = 3400 / nyquist
            
            # Create bandpass filter for speech enhancement
            b, a = signal.butter(4, [low_freq, high_freq], btype='band')
            
            # Apply filter with gain boost for speech frequencies
            enhanced = signal.filtfilt(b, a, audio_data)
            
            # Blend with original (70% enhanced, 30% original)
            result = 0.7 * enhanced + 0.3 * audio_data
            
            return result
            
        except Exception as e:
            logger.warning(f"Spectral enhancement failed: {e}")
            return audio_data
    
    def _normalize_audio(self, audio_data: np.ndarray, target_level: float = 0.7) -> np.ndarray:
        """Normalize audio to target level"""
        # Calculate RMS level
        rms = np.sqrt(np.mean(audio_data**2))
        
        if rms > 0:
            # Calculate gain needed
            gain = target_level / rms
            
            # Apply gain with limiting to prevent clipping
            normalized = audio_data * min(gain, 1.0 / np.max(np.abs(audio_data)))
            return normalized
        
        return audio_data
    
    async def _transcribe_with_whisper(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Transcribe audio using Whisper model"""
        try:
            logger.info("Starting Whisper transcription")
            
            # Run transcription in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                lambda: self.whisper_model.transcribe(
                    audio_data,
                    language='en',  # Can be auto-detected later
                    task='transcribe',
                    word_timestamps=True,
                    temperature=0.2  # Lower temperature for more deterministic results
                )
            )
            
            logger.info(f"Transcription completed: {len(result['text'])} characters")
            return result
            
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            raise
    
    def _analyze_audio_quality(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Analyze audio quality metrics"""
        try:
            # Basic quality metrics
            rms_level = np.sqrt(np.mean(audio_data**2))
            peak_level = np.max(np.abs(audio_data))
            
            # Signal-to-noise ratio estimation
            # Use spectral subtraction method for SNR estimation
            stft = librosa.stft(audio_data)
            magnitude = np.abs(stft)
            
            # Estimate noise floor from quiet sections
            power_db = librosa.amplitude_to_db(magnitude)
            noise_floor = np.percentile(power_db, 10)  # Bottom 10% as noise
            signal_level = np.percentile(power_db, 90)  # Top 90% as signal
            snr_estimate = signal_level - noise_floor
            
            # Silence detection
            frame_length = int(0.025 * sample_rate)  # 25ms frames
            hop_length = int(0.010 * sample_rate)    # 10ms hop
            
            silence_threshold = 0.01
            frames = librosa.util.frame(audio_data, frame_length=frame_length, 
                                      hop_length=hop_length, axis=0)
            frame_energy = np.mean(frames**2, axis=0)
            silent_frames = np.sum(frame_energy < silence_threshold)
            silence_percentage = (silent_frames / len(frame_energy)) * 100
            
            quality_score = self._calculate_quality_score(
                rms_level, peak_level, snr_estimate, silence_percentage
            )
            
            return {
                'rms_level': float(rms_level),
                'peak_level': float(peak_level),
                'snr_estimate_db': float(snr_estimate),
                'silence_percentage': float(silence_percentage),
                'quality_score': quality_score,
                'quality_rating': self._get_quality_rating(quality_score),
                'duration_seconds': len(audio_data) / sample_rate
            }
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return {'error': str(e)}
    
    def _calculate_quality_score(self, rms_level: float, peak_level: float, 
                                snr_db: float, silence_percentage: float) -> float:
        """Calculate overall quality score (0-100)"""
        # Scoring factors
        level_score = min(100, rms_level * 200)  # Prefer RMS around 0.5
        peak_score = 100 if peak_level < 0.95 else max(0, 100 - (peak_level - 0.95) * 1000)
        snr_score = min(100, max(0, snr_db * 3))  # Good SNR > 20dB
        silence_score = max(0, 100 - silence_percentage)  # Penalize too much silence
        
        # Weighted average
        quality_score = (
            level_score * 0.3 +
            peak_score * 0.2 +
            snr_score * 0.4 +
            silence_score * 0.1
        )
        
        return min(100, max(0, quality_score))
    
    def _get_quality_rating(self, score: float) -> str:
        """Convert quality score to rating"""
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "fair"
        else:
            return "poor"
    
    def _detect_context(self, transcript: str, segments: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        PHASE 3: Advanced context detection with Professor Layer integration
        """
        try:
            # Import here to avoid circular dependencies
            from context_analyzer import context_analyzer
            
            # Perform advanced context analysis
            analysis = context_analyzer.analyze_context(transcript, segments)
            
            return {
                'primary_subject': analysis.primary_subject,
                'secondary_subjects': analysis.secondary_subjects,
                'confidence_score': analysis.confidence_score,
                'key_concepts': analysis.key_concepts,
                'difficulty_level': analysis.difficulty_level,
                'lesson_type': analysis.lesson_type,
                'speaker_roles': analysis.speaker_roles,
                'topic_segments': analysis.topic_segments,
                'important_timestamps': analysis.important_timestamps,
                'transcript_length': len(transcript),
                'word_count': len(transcript.split()),
                'is_lecture': analysis.lesson_type in ['lecture', 'exam_prep']
            }
            
        except ImportError:
            logger.warning("Advanced context analyzer not available, using basic detection")
            # Fallback to basic detection
            return self._basic_context_detection(transcript)
            
    def _basic_context_detection(self, transcript: str) -> Dict[str, Any]:
        """Fallback basic context detection"""
        subjects = {
            'mathematics': ['equation', 'integral', 'derivative', 'theorem', 'formula', 'calculate'],
            'physics': ['force', 'energy', 'momentum', 'velocity', 'acceleration', 'quantum'],
            'chemistry': ['molecule', 'reaction', 'element', 'compound', 'oxidation', 'bond'],
            'biology': ['cell', 'organism', 'DNA', 'protein', 'evolution', 'ecosystem']
        }
        
        transcript_lower = transcript.lower()
        detected_subjects = []
        
        for subject, keywords in subjects.items():
            if any(keyword in transcript_lower for keyword in keywords):
                detected_subjects.append(subject)
        
        lecture_indicators = ['today we will', 'let us discuss', 'the topic is', 'chapter']
        is_lecture = any(indicator in transcript_lower for indicator in lecture_indicators)
        
        return {
            'primary_subject': detected_subjects[0] if detected_subjects else 'general',
            'secondary_subjects': detected_subjects[1:3] if len(detected_subjects) > 1 else [],
            'confidence_score': 0.6 if detected_subjects else 0.3,
            'key_concepts': [],
            'difficulty_level': 'intermediate',
            'lesson_type': 'lecture' if is_lecture else 'discussion',
            'speaker_roles': ['professor'],
            'topic_segments': [],
            'important_timestamps': [],
            'transcript_length': len(transcript),
            'word_count': len(transcript.split()),
            'is_lecture': is_lecture
        }

# Global audio processor instance
audio_processor = AudioProcessor()