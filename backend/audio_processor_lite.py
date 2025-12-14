"""
Lightweight Audio Processor - Deployment Ready
Uses external APIs instead of heavy ML models
No PyTorch, Transformers, or local ML dependencies
"""

import os
import logging
from typing import Dict, Any, Optional
import requests
from openai import OpenAI

logger = logging.getLogger(__name__)

class LightweightAudioProcessor:
    """
    Lightweight audio processor using external APIs
    - Uses OpenAI Whisper API for transcription (or Emergent LLM key)
    - No local ML models
    - Fast and deployment-ready
    """
    
    def __init__(self):
        """Initialize with API credentials"""
        self.openai_api_key = os.environ.get('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY')
        
        if not self.openai_api_key:
            logger.warning("No API key found for transcription. Set OPENAI_API_KEY or OPENAI_API_KEY")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=self.openai_api_key)
                logger.info("✅ OpenAI Whisper API initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None
    
    async def transcribe_audio(self, audio_file_path: str, language: str = "en") -> Dict[str, Any]:
        """
        Transcribe audio file using OpenAI Whisper API
        
        Args:
            audio_file_path: Path to audio file
            language: Language code (default: "en")
            
        Returns:
            Dict with transcription text and metadata
        """
        try:
            if not self.client:
                return {
                    "success": False,
                    "error": "Transcription service not available. Please configure OPENAI_API_KEY.",
                    "text": "",
                    "fallback": True
                }
            
            logger.info(f"Transcribing audio file: {audio_file_path}")
            
            # Open audio file
            with open(audio_file_path, "rb") as audio_file:
                # Use OpenAI Whisper API
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="verbose_json"
                )
            
            logger.info(f"✅ Transcription complete: {len(transcript.text)} characters")
            
            return {
                "success": True,
                "text": transcript.text,
                "language": transcript.language,
                "duration": transcript.duration if hasattr(transcript, 'duration') else None,
                "segments": transcript.segments if hasattr(transcript, 'segments') else [],
                "fallback": False
            }
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            
            # Fallback: Return placeholder text
            return {
                "success": False,
                "error": str(e),
                "text": "Transcription failed. Please try uploading a smaller audio file or check your API configuration.",
                "fallback": True
            }
    
    def extract_key_concepts(self, text: str, subject: str = "General") -> list:
        """
        Extract key concepts from text using simple NLP
        No heavy ML models - just pattern matching and frequency analysis
        
        Args:
            text: Transcription text
            subject: Subject area (Physics, Chemistry, Math, etc.)
            
        Returns:
            List of key concepts
        """
        try:
            import re
            from collections import Counter
            
            # Simple concept extraction
            # Remove common words
            stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'as', 'are', 'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'to', 'of', 'and', 'or', 'but', 'in', 'for', 'with', 'from', 'by', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further', 'then', 'once'}
            
            # Extract words
            words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
            
            # Filter stop words and count frequency
            meaningful_words = [w for w in words if w not in stop_words]
            word_freq = Counter(meaningful_words)
            
            # Get top 10 most common concepts
            key_concepts = [word.capitalize() for word, count in word_freq.most_common(10)]
            
            logger.info(f"✅ Extracted {len(key_concepts)} key concepts")
            return key_concepts
            
        except Exception as e:
            logger.error(f"Concept extraction failed: {e}")
            return []
    
    def analyze_audio_quality(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Basic audio quality analysis without heavy ML
        Just checks file properties
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Dict with quality metrics
        """
        try:
            import os
            
            file_size = os.path.getsize(audio_file_path)
            file_extension = os.path.splitext(audio_file_path)[1]
            
            # Simple quality assessment based on file properties
            quality_score = 0.8  # Default good quality
            
            if file_size < 100000:  # Less than 100KB
                quality_score = 0.5
                quality_status = "Low quality - file too small"
            elif file_size > 50000000:  # More than 50MB
                quality_score = 0.7
                quality_status = "Large file - may take longer to process"
            else:
                quality_status = "Good quality"
            
            return {
                "quality_score": quality_score,
                "file_size": file_size,
                "file_format": file_extension,
                "status": quality_status,
                "recommendations": "Audio quality is acceptable for transcription"
            }
            
        except Exception as e:
            logger.error(f"Quality analysis failed: {e}")
            return {
                "quality_score": 0.5,
                "status": "Unable to assess quality",
                "error": str(e)
            }
    
    def process_audio_file(self, audio_file_path: str, subject: str = "General") -> Dict[str, Any]:
        """
        Complete audio processing pipeline - lightweight version
        
        Args:
            audio_file_path: Path to audio file
            subject: Subject area
            
        Returns:
            Dict with all processing results
        """
        results = {
            "success": False,
            "transcription": None,
            "concepts": [],
            "quality": None,
            "error": None
        }
        
        try:
            # Step 1: Quality check
            logger.info("Step 1: Checking audio quality...")
            results["quality"] = self.analyze_audio_quality(audio_file_path)
            
            # Step 2: Transcription
            logger.info("Step 2: Transcribing audio...")
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            transcription_result = loop.run_until_complete(
                self.transcribe_audio(audio_file_path)
            )
            loop.close()
            
            results["transcription"] = transcription_result
            
            if not transcription_result.get("success"):
                results["error"] = transcription_result.get("error", "Transcription failed")
                return results
            
            # Step 3: Extract concepts
            logger.info("Step 3: Extracting key concepts...")
            text = transcription_result.get("text", "")
            results["concepts"] = self.extract_key_concepts(text, subject)
            
            results["success"] = True
            logger.info("✅ Audio processing complete!")
            
        except Exception as e:
            logger.error(f"Audio processing failed: {str(e)}")
            results["error"] = str(e)
        
        return results


# Global instance
_audio_processor = None

def get_audio_processor() -> LightweightAudioProcessor:
    """Get singleton audio processor instance"""
    global _audio_processor
    if _audio_processor is None:
        _audio_processor = LightweightAudioProcessor()
    return _audio_processor