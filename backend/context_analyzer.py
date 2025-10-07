"""
PHASE 3: AI Transcription & Context Detection
Advanced context understanding and Professor Layer integration
"""

import re
import logging
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from collections import Counter
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class ContextAnalysis:
    """Structured context analysis results"""
    primary_subject: str
    secondary_subjects: List[str]
    confidence_score: float
    topic_segments: List[Dict[str, Any]]
    key_concepts: List[str]
    difficulty_level: str
    lesson_type: str  # lecture, discussion, problem_solving, review
    speaker_roles: List[str]  # professor, student, multiple
    important_timestamps: List[Tuple[float, str]]

class AdvancedContextAnalyzer:
    """
    PHASE 3: Advanced Context Detection and Analysis
    Provides intelligent subject detection, topic segmentation, and content understanding
    """
    
    def __init__(self):
        self.subject_keywords = {
            'mathematics': {
                'primary': [
                    'equation', 'integral', 'derivative', 'theorem', 'formula', 'calculate',
                    'algebra', 'geometry', 'trigonometry', 'calculus', 'statistics',
                    'polynomial', 'matrix', 'vector', 'limit', 'probability'
                ],
                'secondary': [
                    'solve', 'proof', 'function', 'graph', 'coordinate', 'angle',
                    'variable', 'coefficient', 'exponential', 'logarithm'
                ]
            },
            'physics': {
                'primary': [
                    'force', 'energy', 'momentum', 'velocity', 'acceleration', 'quantum',
                    'electromagnetic', 'thermodynamics', 'mechanics', 'relativity',
                    'particle', 'wave', 'frequency', 'amplitude', 'potential'
                ],
                'secondary': [
                    'motion', 'gravity', 'electric', 'magnetic', 'current', 'voltage',
                    'power', 'work', 'heat', 'temperature', 'pressure'
                ]
            },
            'chemistry': {
                'primary': [
                    'molecule', 'reaction', 'element', 'compound', 'oxidation', 'bond',
                    'periodic table', 'atomic', 'electron', 'proton', 'neutron',
                    'catalyst', 'equilibrium', 'acid', 'base', 'organic'
                ],
                'secondary': [
                    'chemical', 'solution', 'concentration', 'molar', 'ionic',
                    'covalent', 'synthesis', 'decomposition', 'ph', 'buffer'
                ]
            },
            'biology': {
                'primary': [
                    'cell', 'organism', 'dna', 'protein', 'evolution', 'ecosystem',
                    'photosynthesis', 'respiration', 'genetics', 'chromosome',
                    'enzyme', 'membrane', 'nucleus', 'mitochondria', 'bacteria'
                ],
                'secondary': [
                    'species', 'habitat', 'biodiversity', 'adaptation', 'metabolism',
                    'reproduction', 'mutation', 'inheritance', 'tissue', 'organ'
                ]
            },
            'computer_science': {
                'primary': [
                    'algorithm', 'data structure', 'programming', 'software', 'database',
                    'artificial intelligence', 'machine learning', 'network', 'security',
                    'compiler', 'debugging', 'recursion', 'complexity', 'encryption'
                ],
                'secondary': [
                    'code', 'function', 'variable', 'loop', 'array', 'string',
                    'object', 'class', 'method', 'interface', 'protocol'
                ]
            }
        }
        
        self.difficulty_indicators = {
            'beginner': [
                'introduction', 'basic', 'fundamental', 'overview', 'simple',
                'elementary', 'first', 'begin with', 'start with'
            ],
            'intermediate': [
                'now let\'s', 'moving on', 'next step', 'building on', 'expand',
                'develop', 'extend', 'apply', 'use this'
            ],
            'advanced': [
                'complex', 'sophisticated', 'advanced', 'research', 'cutting edge',
                'state of the art', 'theoretical', 'abstract', 'prove that'
            ],
            'expert': [
                'novel', 'breakthrough', 'revolutionary', 'paradigm', 'hypothesis',
                'conjecture', 'postulate', 'axiom', 'lemma'
            ]
        }
        
        self.lesson_type_indicators = {
            'lecture': [
                'today we will learn', 'the topic is', 'chapter', 'lesson',
                'I will explain', 'let me show you', 'as you can see'
            ],
            'discussion': [
                'what do you think', 'any questions', 'let\'s discuss',
                'your opinion', 'thoughts on', 'agree or disagree'
            ],
            'problem_solving': [
                'solve this', 'find the', 'calculate', 'determine',
                'given that', 'if we have', 'step by step'
            ],
            'review': [
                'remember', 'recall', 'we learned', 'previously',
                'last time', 'review', 'summarize', 'key points'
            ],
            'exam_prep': [
                'exam', 'test', 'quiz', 'assessment', 'important for test',
                'will be asked', 'likely question', 'prepare for'
            ]
        }

    def analyze_context(self, transcript: str, segments: Optional[List[Dict]] = None) -> ContextAnalysis:
        """
        Perform comprehensive context analysis on transcript
        
        Args:
            transcript: Full transcript text
            segments: Optional Whisper segments with timestamps
            
        Returns:
            ContextAnalysis object with detailed analysis
        """
        try:
            logger.info("Starting advanced context analysis")
            
            # Normalize text
            text_lower = transcript.lower()
            
            # Subject detection
            primary_subject, secondary_subjects, confidence = self._detect_subjects(text_lower)
            
            # Topic segmentation
            topic_segments = self._segment_topics(transcript, segments)
            
            # Extract key concepts
            key_concepts = self._extract_key_concepts(transcript, primary_subject)
            
            # Determine difficulty level
            difficulty_level = self._determine_difficulty(text_lower)
            
            # Classify lesson type
            lesson_type = self._classify_lesson_type(text_lower)
            
            # Analyze speakers (basic implementation)
            speaker_roles = self._analyze_speakers(text_lower)
            
            # Find important timestamps
            important_timestamps = self._find_important_moments(transcript, segments)
            
            return ContextAnalysis(
                primary_subject=primary_subject,
                secondary_subjects=secondary_subjects,
                confidence_score=confidence,
                topic_segments=topic_segments,
                key_concepts=key_concepts,
                difficulty_level=difficulty_level,
                lesson_type=lesson_type,
                speaker_roles=speaker_roles,
                important_timestamps=important_timestamps
            )
            
        except Exception as e:
            logger.error(f"Context analysis failed: {e}")
            # Return default analysis
            return ContextAnalysis(
                primary_subject="general",
                secondary_subjects=[],
                confidence_score=0.0,
                topic_segments=[],
                key_concepts=[],
                difficulty_level="intermediate",
                lesson_type="lecture",
                speaker_roles=["professor"],
                important_timestamps=[]
            )

    def _detect_subjects(self, text: str) -> Tuple[str, List[str], float]:
        """Detect primary and secondary subjects with confidence scores"""
        subject_scores = {}
        
        for subject, keywords in self.subject_keywords.items():
            primary_score = sum(1.5 for keyword in keywords['primary'] if keyword in text)
            secondary_score = sum(1.0 for keyword in keywords['secondary'] if keyword in text)
            
            # Weighted score
            total_score = primary_score + secondary_score
            
            # Normalize by text length
            word_count = len(text.split())
            normalized_score = total_score / max(1, word_count / 100)
            
            subject_scores[subject] = normalized_score
        
        # Sort by score
        sorted_subjects = sorted(subject_scores.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_subjects or sorted_subjects[0][1] == 0:
            return "general", [], 0.0
        
        primary_subject = sorted_subjects[0][0]
        primary_score = sorted_subjects[0][1]
        
        # Secondary subjects (score > 0.1 * primary_score)
        threshold = primary_score * 0.1
        secondary_subjects = [
            subject for subject, score in sorted_subjects[1:] 
            if score > threshold
        ][:3]  # Max 3 secondary subjects
        
        # Calculate confidence (0-1 scale)
        confidence = min(1.0, primary_score / 5.0)
        
        return primary_subject, secondary_subjects, confidence

    def _segment_topics(self, transcript: str, segments: Optional[List[Dict]] = None) -> List[Dict[str, Any]]:
        """Segment transcript into topic-based sections"""
        topic_segments = []
        
        if not segments:
            # Simple paragraph-based segmentation
            paragraphs = transcript.split('\n\n')
            for i, paragraph in enumerate(paragraphs):
                if len(paragraph.strip()) > 50:  # Minimum length
                    topic_segments.append({
                        'start_time': i * 30,  # Estimate 30 seconds per paragraph
                        'end_time': (i + 1) * 30,
                        'text': paragraph.strip(),
                        'topic': self._extract_topic_from_text(paragraph),
                        'confidence': 0.6
                    })
        else:
            # Use Whisper segments for more accurate timing
            current_topic = None
            current_text = ""
            segment_start = 0
            
            for segment in segments:
                segment_text = segment.get('text', '').strip()
                
                if not segment_text:
                    continue
                
                # Detect topic change (simplified heuristic)
                detected_topic = self._extract_topic_from_text(segment_text)
                
                if detected_topic != current_topic and current_text:
                    # Save previous segment
                    topic_segments.append({
                        'start_time': segment_start,
                        'end_time': segment.get('start', segment_start),
                        'text': current_text,
                        'topic': current_topic or 'general',
                        'confidence': 0.7
                    })
                    
                    # Start new segment
                    segment_start = segment.get('start', segment_start)
                    current_text = segment_text
                    current_topic = detected_topic
                else:
                    current_text += " " + segment_text
                    if not current_topic:
                        current_topic = detected_topic
            
            # Add final segment
            if current_text:
                topic_segments.append({
                    'start_time': segment_start,
                    'end_time': segments[-1].get('end', segment_start + 30),
                    'text': current_text,
                    'topic': current_topic or 'general',
                    'confidence': 0.7
                })
        
        return topic_segments[:20]  # Limit to 20 segments

    def _extract_topic_from_text(self, text: str) -> str:
        """Extract topic from a text segment"""
        text_lower = text.lower()
        
        # Look for explicit topic indicators
        topic_patterns = [
            r'today we will (?:learn|discuss|cover) (?:about )?(.{1,50}?)(?:\.|,|$)',
            r'the topic (?:is|of today is) (.{1,50}?)(?:\.|,|$)',
            r'let\'s talk about (.{1,50}?)(?:\.|,|$)',
            r'now we\'ll (?:move to|discuss) (.{1,50}?)(?:\.|,|$)',
            r'chapter \d+:? (.{1,50}?)(?:\.|,|$)',
        ]
        
        for pattern in topic_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return match.group(1).strip().title()
        
        # Fallback: extract key nouns as topic
        # Simple noun extraction (words that appear multiple times)
        words = re.findall(r'\b[a-z]+\b', text_lower)
        word_counts = Counter(words)
        
        # Filter out common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        meaningful_words = {word: count for word, count in word_counts.items() 
                          if count > 1 and word not in common_words and len(word) > 3}
        
        if meaningful_words:
            top_word = max(meaningful_words.items(), key=lambda x: x[1])[0]
            return top_word.title()
        
        return "General Discussion"

    def _extract_key_concepts(self, transcript: str, subject: str) -> List[str]:
        """Extract key concepts based on subject and content"""
        concepts = []
        text_lower = transcript.lower()
        
        # Subject-specific concept extraction
        if subject in self.subject_keywords:
            subject_words = (self.subject_keywords[subject]['primary'] + 
                           self.subject_keywords[subject]['secondary'])
            
            for word in subject_words:
                if word in text_lower:
                    concepts.append(word.title())
        
        # Look for definition patterns
        definition_patterns = [
            r'(.{1,30}) is (?:defined as|known as) (.{1,50}?)(?:\.|,)',
            r'(.{1,30}) means (.{1,50}?)(?:\.|,)',
            r'the definition of (.{1,30}) is (.{1,50}?)(?:\.|,)',
            r'(.{1,30}) can be (?:defined|described) as (.{1,50}?)(?:\.|,)'
        ]
        
        for pattern in definition_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                concept = match.group(1).strip()
                if 3 < len(concept) < 30:  # Reasonable concept length
                    concepts.append(concept.title())
        
        # Extract formula/equation references
        if subject in ['mathematics', 'physics', 'chemistry']:
            formula_patterns = [
                r'(.{1,20}) (?:formula|equation)',
                r'(?:formula|equation) (?:for|of) (.{1,20})',
                r'(.{1,20}) (?:law|theorem|principle)'
            ]
            
            for pattern in formula_patterns:
                matches = re.finditer(pattern, text_lower)
                for match in matches:
                    formula_name = match.group(1).strip()
                    if 3 < len(formula_name) < 25:
                        concepts.append(f"{formula_name.title()} Formula")
        
        # Remove duplicates and return top concepts
        unique_concepts = list(dict.fromkeys(concepts))  # Preserve order
        return unique_concepts[:15]  # Max 15 concepts

    def _determine_difficulty(self, text: str) -> str:
        """Determine difficulty level based on language complexity"""
        difficulty_scores = {}
        
        for level, indicators in self.difficulty_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text)
            difficulty_scores[level] = score
        
        # Additional heuristics
        # Complex sentence structure
        avg_sentence_length = np.mean([len(s.split()) for s in text.split('.') if s.strip()])
        
        # Technical vocabulary density
        technical_words = 0
        total_words = len(text.split())
        
        for subject_keywords in self.subject_keywords.values():
            for word in subject_keywords['primary']:
                technical_words += text.count(word)
        
        technical_density = technical_words / max(1, total_words)
        
        # Adjust scores based on heuristics
        if avg_sentence_length > 20:
            difficulty_scores['advanced'] += 1
            difficulty_scores['expert'] += 1
        
        if technical_density > 0.05:
            difficulty_scores['intermediate'] += 1
            difficulty_scores['advanced'] += 2
        
        # Return highest scoring difficulty
        if not any(difficulty_scores.values()):
            return 'intermediate'
        
        return max(difficulty_scores.items(), key=lambda x: x[1])[0]

    def _classify_lesson_type(self, text: str) -> str:
        """Classify the type of lesson/content"""
        type_scores = {}
        
        for lesson_type, indicators in self.lesson_type_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text)
            type_scores[lesson_type] = score
        
        # Additional heuristics
        question_count = text.count('?')
        imperative_count = sum(1 for phrase in ['calculate', 'find', 'solve', 'determine'] 
                              if phrase in text)
        
        # Adjust scores
        if question_count > 5:
            type_scores['discussion'] += 2
        
        if imperative_count > 3:
            type_scores['problem_solving'] += 2
        
        if not any(type_scores.values()):
            return 'lecture'
        
        return max(type_scores.items(), key=lambda x: x[1])[0]

    def _analyze_speakers(self, text: str) -> List[str]:
        """Analyze speaker roles (basic implementation)"""
        # Simple heuristics for speaker detection
        teacher_indicators = [
            'I will explain', 'let me show', 'as you can see',
            'today we will', 'the answer is', 'remember that'
        ]
        
        student_indicators = [
            'I don\'t understand', 'can you explain', 'what if',
            'I think', 'is it', 'could you'
        ]
        
        teacher_score = sum(1 for indicator in teacher_indicators if indicator in text)
        student_score = sum(1 for indicator in student_indicators if indicator in text)
        
        speakers = []
        
        if teacher_score > 0:
            speakers.append('professor')
        
        if student_score > 0:
            speakers.append('student')
        
        if teacher_score > 0 and student_score > 0:
            speakers.append('interactive')
        
        return speakers or ['professor']

    def _find_important_moments(self, transcript: str, segments: Optional[List[Dict]] = None) -> List[Tuple[float, str]]:
        """Find important timestamps in the content"""
        important_moments = []
        
        # Important phrases that indicate key moments
        key_phrases = [
            'important', 'remember this', 'key point', 'crucial', 'essential',
            'don\'t forget', 'note that', 'pay attention', 'this will be on the test',
            'in summary', 'to conclude', 'the main idea', 'in other words'
        ]
        
        if segments:
            for segment in segments:
                segment_text = segment.get('text', '').lower()
                start_time = segment.get('start', 0)
                
                for phrase in key_phrases:
                    if phrase in segment_text:
                        important_moments.append((
                            start_time,
                            f"Key moment: {phrase}"
                        ))
        else:
            # Fallback: estimate timestamps for important phrases
            for i, phrase in enumerate(key_phrases):
                if phrase in transcript.lower():
                    # Estimate timestamp based on position in text
                    phrase_position = transcript.lower().find(phrase)
                    estimated_time = (phrase_position / len(transcript)) * 1800  # Assume 30 min max
                    important_moments.append((
                        estimated_time,
                        f"Key moment: {phrase}"
                    ))
        
        # Sort by timestamp and limit results
        important_moments.sort(key=lambda x: x[0])
        return important_moments[:10]

# Global context analyzer instance
context_analyzer = AdvancedContextAnalyzer()