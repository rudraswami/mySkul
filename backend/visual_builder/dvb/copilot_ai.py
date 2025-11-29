"""
Druv Visual Builder - Copilot AI
AI assistant that suggests from BAL/VGE only (no hallucination)
Temperature = 0, heavily prompt-engineered
"""

from typing import List, Dict, Any, Optional
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)


class CopilotAI:
    """
    AI copilot for Visual Builder
    Only suggests from BAL assets and VGE grammars
    No generation, only retrieval and suggestion
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize copilot AI
        
        Args:
            api_key: OpenAI API key (defaults to env var)
        """
        self.client = OpenAI(api_key=api_key)
        self.temperature = 0  # Deterministic
        self.max_suggestions = 5
    
    def suggest_grammar(
        self,
        concept: str,
        subject: str,
        available_grammars: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Suggest grammar for concept
        
        Args:
            concept: Concept to visualize (e.g., "Newton's 2nd Law")
            subject: Subject (e.g., "physics")
            available_grammars: List of available grammars
        
        Returns:
            List of suggested grammars with scores
        """
        # Build prompt with 10-shot examples
        prompt = self._build_grammar_suggestion_prompt(concept, subject, available_grammars)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=500
            )
            
            # Parse response
            suggestions = self._parse_suggestions(response.choices[0].message.content)
            
            return suggestions[:self.max_suggestions]
            
        except Exception as e:
            logger.error(f"Error in copilot suggestion: {e}")
            return []
    
    def suggest_assets(
        self,
        grammar_id: str,
        parameter_name: str,
        parameter_tag: str,
        available_assets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Suggest assets for parameter
        
        Args:
            grammar_id: Grammar being used
            parameter_name: Parameter name
            parameter_tag: Asset tag to filter
            available_assets: List of available assets
        
        Returns:
            List of suggested assets
        """
        # Filter assets by tag
        matching_assets = [
            asset for asset in available_assets
            if parameter_tag in asset.get('tags', [])
        ]
        
        # Rank by cultural relevance
        ranked_assets = sorted(
            matching_assets,
            key=lambda a: self._calculate_cultural_relevance_score(a),
            reverse=True
        )
        
        return ranked_assets[:self.max_suggestions]
    
    def suggest_cultural_hook(
        self,
        grammar_id: str,
        assets: Dict[str, str],
        concept: str
    ) -> Optional[str]:
        """
        Suggest cultural hook text
        
        Args:
            grammar_id: Grammar being used
            assets: Selected assets
            concept: Concept being visualized
        
        Returns:
            Suggested cultural hook (Hinglish)
        """
        prompt = f"""
        Suggest a cultural hook for this visual:
        Concept: {concept}
        Grammar: {grammar_id}
        Assets: {assets}
        
        Requirements:
        - Use Hinglish (mix of Hindi and English)
        - Reference daily Indian objects
        - Make it relatable (e.g., "How many Dabbawalas to push your auto?")
        - Keep it short (max 50 words)
        
        Return only the hook text, no explanation.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a cultural expert for Indian students. Suggest relatable, Hinglish hooks."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Slightly creative for hooks
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error suggesting cultural hook: {e}")
            return None
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for copilot"""
        return """
        You are a Visual Builder Copilot for Druv AI.
        
        CRITICAL RULES:
        1. ONLY suggest from available grammars/assets - NEVER generate new ones
        2. Temperature = 0 (deterministic)
        3. If no match found, say "No suitable grammar found"
        4. Always explain WHY you're suggesting (value proposition)
        
        Your role is to HELP, not CREATE. You're a librarian, not an author.
        """
    
    def _build_grammar_suggestion_prompt(
        self,
        concept: str,
        subject: str,
        available_grammars: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for grammar suggestion"""
        grammar_list = "\n".join([
            f"- {g['grammar_id']}: {g.get('description', '')}"
            for g in available_grammars[:20]  # Limit to 20 for context
        ])
        
        return f"""
        Concept to visualize: {concept}
        Subject: {subject}
        
        Available grammars:
        {grammar_list}
        
        Suggest the BEST grammar from the list above. Explain why.
        If no suitable grammar exists, say "No suitable grammar found".
        """
    
    def _parse_suggestions(self, response: str) -> List[Dict[str, Any]]:
        """Parse AI response into structured suggestions"""
        # Simple parsing - in production, use structured output
        suggestions = []
        lines = response.split('\n')
        
        for line in lines:
            if 'grammar_id' in line.lower() or 'physics.' in line.lower():
                # Extract grammar ID
                parts = line.split(':')
                if len(parts) >= 2:
                    grammar_id = parts[0].strip().replace('-', '').strip()
                    reason = ':'.join(parts[1:]).strip()
                    suggestions.append({
                        'grammar_id': grammar_id,
                        'reason': reason,
                        'score': 0.8  # Default score
                    })
        
        return suggestions
    
    def _calculate_cultural_relevance_score(self, asset: Dict[str, Any]) -> float:
        """Calculate cultural relevance score for asset"""
        score = 0.0
        
        # Check tags for Indian objects
        indian_tags = ['auto', 'rickshaw', 'cricket', 'sugarcane', 'lpg', 'dabbawala']
        tags = asset.get('tags', [])
        for tag in tags:
            if any(indian in tag.lower() for indian in indian_tags):
                score += 0.3
        
        # Check cultural region
        if 'pan_india' in asset.get('cultural_region', []):
            score += 0.2
        
        # Check if abstract (penalty)
        abstract_tags = ['block', 'box', 'object', 'thing']
        if any(abstract in ' '.join(tags).lower() for abstract in abstract_tags):
            score -= 0.5
        
        return max(0.0, min(1.0, score))







