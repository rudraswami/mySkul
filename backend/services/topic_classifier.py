"""
Topic Classifier - Intelligent metaphor selection based on question content
Maps student questions to appropriate culturally-relevant metaphors
"""
import re
import logging

logger = logging.getLogger(__name__)


class TopicClassifier:
    """
    Classifies student questions into topics and selects appropriate metaphors
    Uses rule-based + keyword matching for speed (<10ms)
    """
    
    # Topic keywords mapping
    TOPIC_KEYWORDS = {
        'quantum_physics': [
            'quantum', 'quantum number', 'electron', 'orbital', 'atomic structure',
            'wave function', 'uncertainty principle', 'schrodinger', 'bohr model',
            'energy levels', 'quantum state', 'spin', 'quantum mechanics'
        ],
        'chemistry_bonding': [
            'bond', 'ionic', 'covalent', 'metallic', 'valence', 'lewis structure',
            'molecular orbital', 'hybridization', 'vsepr', 'electronegativity',
            'chemical bonding', 'molecule'
        ],
        'chemistry_reaction': [
            'reaction', 'chemical reaction', 'reagent', 'product', 'catalyst',
            'equilibrium', 'rate of reaction', 'mechanism', 'redox', 'oxidation',
            'reduction', 'synthesis', 'decomposition'
        ],
        'physics_mechanics': [
            'force', 'motion', 'velocity', 'acceleration', 'newton', 'momentum',
            'friction', 'work', 'energy', 'power', 'collision', 'projectile',
            'circular motion', 'gravitation'
        ],
        'physics_waves': [
            'wave', 'frequency', 'wavelength', 'amplitude', 'sound', 'light',
            'refraction', 'reflection', 'interference', 'diffraction', 'doppler'
        ],
        'physics_electricity': [
            'current', 'voltage', 'resistance', 'ohm', 'circuit', 'capacitor',
            'inductor', 'electric field', 'magnetic field', 'electromagnetic'
        ],
        'calculus': [
            'derivative', 'integral', 'integration', 'differentiation', 'limit',
            'continuity', 'differential equation', 'partial derivative',
            'integration by parts', 'substitution', 'calculus'
        ],
        'algebra': [
            'equation', 'polynomial', 'quadratic', 'factor', 'root', 'solve',
            'linear equation', 'simultaneous', 'inequality', 'expression'
        ],
        'geometry': [
            'triangle', 'circle', 'angle', 'theorem', 'pythagoras', 'area',
            'volume', 'perimeter', 'congruent', 'similar', 'coordinate geometry'
        ],
        'trigonometry': [
            'sin', 'cos', 'tan', 'trigonometry', 'trigonometric', 'sine', 'cosine',
            'tangent', 'radian', 'degree', 'inverse trig'
        ],
        'probability': [
            'probability', 'permutation', 'combination', 'statistics', 'mean',
            'median', 'variance', 'standard deviation', 'distribution', 'random'
        ],
        'biology_cell': [
            'cell', 'mitochondria', 'nucleus', 'organelle', 'membrane', 'dna',
            'rna', 'protein synthesis', 'cellular', 'cytoplasm', 'ribosome'
        ],
        'biology_system': [
            'digestive', 'respiratory', 'circulatory', 'nervous', 'excretory',
            'reproductive', 'system', 'organ', 'tissue', 'blood', 'heart'
        ],
        'biology_genetics': [
            'gene', 'genetics', 'inheritance', 'mendel', 'allele', 'dominant',
            'recessive', 'chromosome', 'mutation', 'heredity', 'genotype'
        ],
        'photosynthesis': [
            'photosynthesis', 'chlorophyll', 'chloroplast', 'light reaction',
            'dark reaction', 'glucose', 'carbon dioxide', 'calvin cycle'
        ]
    }
    
    # Metaphor preferences by topic
    TOPIC_TO_METAPHOR = {
        'quantum_physics': ['hotel_rooms', 'train_compartments', 'apartment_floors'],
        'chemistry_bonding': ['cooking', 'tiffin_assembly', 'rangoli_patterns'],
        'chemistry_reaction': ['cooking', 'street_food_prep', 'biryani_layers'],
        'physics_mechanics': ['cricket_strategy', 'train_motion', 'auto_rickshaw'],
        'physics_waves': ['music', 'cricket_crowd', 'festival_celebration'],
        'physics_electricity': ['water_flow', 'train_network', 'metro_system'],
        'calculus': ['cricket_strategy', 'cooking_process', 'journey_planning'],
        'algebra': ['puzzle', 'cricket_score', 'market_calculation'],
        'geometry': ['rangoli', 'cricket_field', 'building_architecture'],
        'trigonometry': ['cricket_angles', 'kite_flying', 'building_heights'],
        'probability': ['cricket_prediction', 'train_bogies', 'tiffin_distribution'],
        'biology_cell': ['city_system', 'factory', 'kitchen_organization'],
        'biology_system': ['transport_network', 'water_supply', 'food_delivery'],
        'biology_genetics': ['family_resemblance', 'recipe_inheritance', 'traits_passing'],
        'photosynthesis': ['cooking', 'solar_cooking', 'tiffin_preparation']
    }
    
    # Fallback metaphor priorities
    FALLBACK_PRIORITY = ['cooking', 'cricket_strategy', 'train_motion', 'hotel_rooms']
    
    @classmethod
    def classify_topic(cls, question: str) -> str:
        """
        Classify question into topic category
        
        Args:
            question: Student's question
            
        Returns:
            Topic category string (e.g., 'quantum_physics', 'calculus')
        """
        question_lower = question.lower()
        
        # Score each topic based on keyword matches
        topic_scores = {}
        for topic, keywords in cls.TOPIC_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in question_lower)
            if score > 0:
                topic_scores[topic] = score
        
        # Return topic with highest score
        if topic_scores:
            best_topic = max(topic_scores, key=topic_scores.get)
            logger.info(f"📊 Topic classified: {best_topic} (score: {topic_scores[best_topic]})")
            return best_topic
        
        # Generic fallback
        logger.info(f"📊 Topic: generic (no specific match)")
        return 'generic'
    
    @classmethod
    def select_metaphor(cls, question: str, preferred_category: str = None, region: str = 'Bangalore') -> dict:
        """
        Select appropriate metaphor for question
        
        Args:
            question: Student's question
            preferred_category: User's preferred metaphor category (cricket, cooking, etc.)
            region: User's region for cultural relevance
            
        Returns:
            Dict with metaphor_category and topic
        """
        # Classify topic
        topic = cls.classify_topic(question)
        
        # Get appropriate metaphors for this topic
        if topic in cls.TOPIC_TO_METAPHOR:
            appropriate_metaphors = cls.TOPIC_TO_METAPHOR[topic]
            
            # If user has preference and it's appropriate, use it
            if preferred_category:
                # Map user preference to internal metaphor names
                user_pref_map = {
                    'cricket': 'cricket_strategy',
                    'cooking': 'cooking',
                    'bollywood': 'movie_scene',
                    'gaming': 'game_strategy'
                }
                mapped_pref = user_pref_map.get(preferred_category)
                
                if mapped_pref in appropriate_metaphors:
                    logger.info(f"✅ Using user preference: {preferred_category} (topic: {topic})")
                    return {
                        'metaphor_category': preferred_category,
                        'topic': topic,
                        'reason': 'user_preference_appropriate'
                    }
            
            # Otherwise use most appropriate for topic
            best_metaphor = appropriate_metaphors[0]
            # Map back to user-friendly names
            reverse_map = {
                'cricket_strategy': 'cricket',
                'cooking': 'cooking',
                'hotel_rooms': 'accommodation',
                'train_motion': 'transport',
                'train_compartments': 'transport',
                'rangoli_patterns': 'art',
                'tiffin_assembly': 'cooking',
                'street_food_prep': 'cooking',
                'biryani_layers': 'cooking',
                'auto_rickshaw': 'transport',
                'music': 'entertainment',
                'festival_celebration': 'festival',
                'water_flow': 'nature',
                'metro_system': 'transport',
                'journey_planning': 'transport',
                'puzzle': 'gaming',
                'market_calculation': 'market',
                'kite_flying': 'festival',
                'city_system': 'city',
                'factory': 'industry',
                'kitchen_organization': 'cooking',
                'transport_network': 'transport',
                'family_resemblance': 'family',
                'recipe_inheritance': 'cooking'
            }
            
            friendly_name = reverse_map.get(best_metaphor, 'cooking')
            logger.info(f"🎯 Selected metaphor: {friendly_name} for topic: {topic}")
            
            return {
                'metaphor_category': friendly_name,
                'topic': topic,
                'reason': 'topic_appropriate'
            }
        
        # Fallback to user preference or cooking
        fallback = preferred_category or 'cooking'
        logger.info(f"🔄 Fallback metaphor: {fallback} (topic: {topic})")
        
        return {
            'metaphor_category': fallback,
            'topic': topic,
            'reason': 'fallback'
        }
    
    @classmethod
    def get_metaphor_examples(cls, metaphor_category: str, region: str) -> dict:
        """
        Get culturally relevant examples for metaphor category
        
        Args:
            metaphor_category: Category like 'cricket', 'cooking', etc.
            region: User's region
            
        Returns:
            Dict with examples
        """
        regional_examples = {
            'Delhi': {
                'cricket': 'Delhi Capitals batting strategy, like Pant choosing which ball to smash',
                'cooking': 'Making butter chicken - marinate first, then cook step by step',
                'transport': 'Delhi Metro connections, changing lines at Rajiv Chowk',
                'market': 'Sarojini market bargaining, calculating best deals'
            },
            'Mumbai': {
                'cricket': 'Mumbai Indians strategy, like Rohit planning the innings',
                'cooking': 'Assembling vada pav - potato vada first, then pav together',
                'transport': 'Local train journey from Churchgate to Virar',
                'market': 'Crawford market shopping, negotiating prices'
            },
            'Chennai': {
                'cricket': 'CSK calm approach, like Dhoni choosing when to attack',
                'cooking': 'Making perfect dosa - spread batter evenly, cook with timing',
                'transport': 'MTC bus routes, connecting different areas',
                'market': 'T Nagar shopping, Pondy Bazaar calculations'
            },
            'Kolkata': {
                'cricket': 'KKR aggressive fielding, positioning players strategically',
                'cooking': 'Making rasgulla - chenna balls first, then syrup cooking',
                'transport': 'Tram journey through Kolkata streets',
                'market': 'New Market bargaining, finding best rates'
            },
            'Bangalore': {
                'cricket': 'RCB power hitting, like Virat choosing which ball to attack',
                'cooking': 'Brewing filter coffee - decoction first, then milk in layers',
                'transport': 'Namma Metro connections, Silk Board traffic strategy',
                'market': 'Commercial Street shopping, calculating discounts'
            }
        }
        
        region_data = regional_examples.get(region, regional_examples['Bangalore'])
        return region_data.get(metaphor_category, region_data['cooking'])


# Quick test function
def test_classifier():
    """Test the classifier with sample questions"""
    test_questions = [
        "Explain quantum numbers",
        "What is integration by parts?",
        "How does photosynthesis work?",
        "Explain Newton's second law",
        "What are ionic bonds?",
        "Solve this quadratic equation",
        "How does the heart work?"
    ]
    
    print("\n" + "="*60)
    print("TOPIC CLASSIFIER TEST")
    print("="*60)
    
    for question in test_questions:
        result = TopicClassifier.select_metaphor(question, region='Mumbai')
        print(f"\nQuestion: {question}")
        print(f"  → Topic: {result['topic']}")
        print(f"  → Metaphor: {result['metaphor_category']}")
        print(f"  → Reason: {result['reason']}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    test_classifier()
