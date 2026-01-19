"""
Smart Intent-Driven Buying Assistant (SIDBA) Engine

This module implements the core intelligence for understanding user intent,
detecting trade-offs, simulating buyer personas, and generating human-friendly explanations.
"""

import json
import re
from typing import Dict, List, Tuple, Optional


class IntentDecompositionEngine:
    """Decomposes user input into structured decision factors"""
    
    def __init__(self):
        self.user_type_keywords = {
            'student': ['student', 'mca', 'mba', 'college', 'university', 'study', 'academic'],
            'gamer': ['gaming', 'gamer', 'games', 'bgmi', 'valorant', 'pubg', 'esports'],
            'professional': ['work', 'office', 'business', 'professional', 'corporate', 'job'],
            'creator': ['video editing', 'photo editing', 'design', 'content creation', 'youtube', 'creator', 'photoshop', 'premiere', 'after effects', 'adobe', '4k', 'hdr', 'color accurate', 'color accuracy', 'color grading', 'video production'],
            'traveller': ['travel', 'portable', 'lightweight', 'on-the-go', 'mobile']
        }
    
    def extract_user_type(self, text: str) -> str:
        """Detect user type from text with priority to content creation"""
        text_lower = text.lower()
        
        # Check for content creation keywords first (highest priority)
        creator_keywords = self.user_type_keywords['creator']
        if any(keyword in text_lower for keyword in creator_keywords):
            return 'creator'
            
        # Check other user types
        for user_type, keywords in self.user_type_keywords.items():
            if user_type == 'creator':
                continue  # Already checked
                
            if any(keyword in text_lower for keyword in keywords):
                return user_type
        
        return 'general'
    
    def extract_longevity_priority(self, text: str) -> int:
        """Extract longevity/future-proof priority (1-5 scale)"""
        text_lower = text.lower()
        
        high_priority_keywords = ['future-proof', 'futureproof', 'long-term', 'long term', 'durable', 'last long']
        medium_priority_keywords = ['good for years', 'reliable', 'quality']
        
        if any(kw in text_lower for kw in high_priority_keywords):
            return 5
        elif any(kw in text_lower for kw in medium_priority_keywords):
            return 3
        
        return 2  # Default moderate priority


class TradeOffIntelligence:
    """Detects conflicting requirements and explains trade-offs"""
    
    def __init__(self):
        # Known trade-offs in tech products
        self.trade_offs = {
            'gaming_gpu_vs_battery': {
                'conflict': ['gaming', 'rtx', 'gtx', 'gpu'],
                'vs': ['battery', 'battery life', 'long battery', '10 hour', '12 hour'],
                'explanation': 'Gaming GPUs consume high power, reducing battery life. RTX laptops typically last 3-5 hours under load.',
                'severity': 'high'
            },
            'lightweight_vs_performance': {
                'conflict': ['lightweight', 'light', 'portable', 'under 2kg', 'under 1.5kg'],
                'vs': ['i9', 'ryzen 9', 'high performance', 'powerful'],
                'explanation': 'Ultra-lightweight laptops often use lower-power processors to manage heat and weight.',
                'severity': 'medium'
            },
            'creator_display_quality': {
                'conflict': ['video editing', 'photo editing', 'photoshop', 'color accuracy', '4k', 'hdr'],
                'vs': ['low budget', 'cheap', 'under 50k', 'under 60k'],
                'explanation': 'Professional-grade displays with accurate colors and high resolution (4K/HDR) are typically found in premium laptops above ₹60,000.',
                'severity': 'high'
            },
            'creator_performance_needs': {
                'conflict': ['4k editing', 'video rendering', 'after effects', 'premiere pro'],
                'vs': ['i3', 'i5', 'ryzen 3', 'ryzen 5', '8gb ram', '256gb ssd'],
                'explanation': '4K video editing requires at least an i7/Ryzen 7 processor, 16GB+ RAM, and a dedicated GPU for smooth performance.',
                'severity': 'high'
            },
            'budget_vs_premium_features': {
                'conflict': ['budget', 'cheap', 'affordable', 'under 50k', 'under 60k'],
                'vs': ['rtx 4080', 'rtx 4090', 'i9', 'premium', 'high-end'],
                'explanation': 'Premium features like RTX 4080/4090 and i9 processors are typically priced above ₹1,00,000.',
                'severity': 'high'
            },
            'compact_vs_screen_size': {
                'conflict': ['compact', 'small', 'mini', 'under 6 inch', 'under 14 inch'],
                'vs': ['large screen', 'big display', '15 inch', '16 inch', '17 inch'],
                'explanation': 'Compact devices have smaller screens. Large screens require larger devices.',
                'severity': 'low'
            },
            'ml_cuda_vs_battery': {
                'conflict': ['ml', 'machine learning', 'cuda', 'deep learning', 'ai'],
                'vs': ['battery', 'battery life', 'portable'],
                'explanation': 'ML workloads require CUDA-capable GPUs which consume significant power, reducing battery life.',
                'severity': 'medium'
            }
        }
    
    def detect_conflicts(self, requirements: Dict, user_text: str = '') -> List[Dict]:
        """Detect conflicting requirements"""
        conflicts = []
        text_lower = user_text.lower()
        
        for tradeoff_name, tradeoff_data in self.trade_offs.items():
            conflict_keywords = tradeoff_data['conflict']
            vs_keywords = tradeoff_data['vs']
            
            has_conflict = any(kw in text_lower for kw in conflict_keywords)
            has_vs = any(kw in text_lower for kw in vs_keywords)
            
            # Also check parsed requirements
            if not has_conflict:
                if 'gaming' in tradeoff_name and ('gaming' in str(requirements.get('use_case') or []).lower() or 
                                                   'rtx' in str(requirements.get('gpu_required', '')).lower()):
                    has_conflict = True
            
            if has_conflict and has_vs:
                conflicts.append({
                    'type': tradeoff_name,
                    'explanation': tradeoff_data['explanation'],
                    'severity': tradeoff_data['severity'],
                    'conflict_terms': [kw for kw in conflict_keywords if kw in text_lower],
                    'vs_terms': [kw for kw in vs_keywords if kw in text_lower]
                })
        
        return conflicts
    
    def generate_tradeoff_explanation(self, conflicts: List[Dict]) -> str:
        """Generate human-friendly trade-off explanation"""
        if not conflicts:
            return None
        
        high_severity = [c for c in conflicts if c['severity'] == 'high']
        
        if high_severity:
            return high_severity[0]['explanation']
        
        return conflicts[0]['explanation']


class BuyerPersonaSimulator:
    """Simulates buyer personas and adjusts ranking logic"""
    
    def __init__(self):
        self.personas = {
            'student': {
                'priorities': ['value', 'longevity', 'versatility'],
                'weight_factors': {
                    'price': 0.3,
                    'battery': 0.2,
                    'performance': 0.25,
                    'durability': 0.15,
                    'portability': 0.1
                },
                'description': '🎓 Student - Values affordability, durability, and versatility'
            },
            'gamer': {
                'priorities': ['fps', 'thermals', 'refresh_rate'],
                'weight_factors': {
                    'gpu': 0.35,
                    'cpu': 0.25,
                    'cooling': 0.2,
                    'display': 0.15,
                    'price': 0.05
                },
                'description': '🎮 Gamer - Prioritizes performance, FPS, and thermal management'
            },
            'professional': {
                'priorities': ['reliability', 'battery', 'build_quality'],
                'weight_factors': {
                    'reliability': 0.3,
                    'battery': 0.25,
                    'build_quality': 0.2,
                    'performance': 0.15,
                    'portability': 0.1
                },
                'description': '👨‍💼 Professional - Needs reliability, battery life, and build quality'
            },
            'creator': {
                'priorities': ['color_accuracy', 'display_quality', 'performance', 'storage'],
                'weight_factors': {
                    'display_quality': 0.4,  # Increased importance
                    'color_accuracy': 0.3,   # Specific for content creation
                    'cpu': 0.2,              # For rendering
                    'gpu': 0.15,             # For GPU acceleration
                    'ram': 0.15,             # For multitasking
                    'storage': 0.15,         # For large media files
                    'battery': 0.05,         # Less important for creators
                    'portability': 0.05      # Less important for creators
                },
                'description': '🎨 Content Creator - Prioritizes display quality, color accuracy, and performance for video/photo editing'
            },
            'traveller': {
                'priorities': ['portability', 'battery', 'durability'],
                'weight_factors': {
                    'weight': 0.35,
                    'battery': 0.3,
                    'durability': 0.2,
                    'portability': 0.15
                },
                'description': '🧳 Traveller - Needs portability, long battery, and durability'
            },
            'general': {
                'priorities': ['balance', 'value'],
                'weight_factors': {
                    'price': 0.25,
                    'performance': 0.25,
                    'battery': 0.2,
                    'build_quality': 0.15,
                    'portability': 0.15
                },
                'description': '👤 General User - Balanced approach to all factors'
            }
        }
    
    def detect_persona(self, requirements: Dict, user_text: str = '', user_type: str = 'general') -> Dict:
        """Detect buyer persona from requirements and user type"""
        # Use provided user_type or detect from requirements
        if user_type == 'general':
            text_lower = user_text.lower()
            
            # Check use cases
            use_cases = requirements.get('use_case') or []
            use_cases_lower = [uc.lower() for uc in use_cases]
            
            if 'gaming' in use_cases_lower or 'gamer' in text_lower:
                user_type = 'gamer'
            elif 'video editing' in text_lower or 'photo editing' in text_lower or 'design' in text_lower:
                user_type = 'creator'
            elif 'work' in text_lower or 'office' in text_lower or 'business' in text_lower:
                user_type = 'professional'
            elif 'travel' in text_lower or 'portable' in text_lower:
                user_type = 'traveller'
            elif 'student' in text_lower or 'mca' in text_lower or 'college' in text_lower:
                user_type = 'student'
        
        persona = self.personas.get(user_type, self.personas['general'])
        
        return {
            'type': user_type,
            'priorities': persona.get('priorities') or [],
            'weight_factors': persona.get('weight_factors') or {},
            'description': persona.get('description', '')
        }
    
    def adjust_ranking_weights(self, persona: Dict, base_requirements: Dict) -> Dict:
        """Adjust ranking weights based on persona"""
        return persona['weight_factors']


class DecisionExplanationGenerator:
    """Generates human-friendly explanations for product recommendations"""
    
    def generate_explanation(self, product: Dict, requirements: Dict, persona: Dict, 
                          conflicts: List[Dict] = None) -> Dict:
        """Generate comprehensive explanation for why a product matches"""
        
        explanations = {
            'why_this_product': [],
            'trade_offs': [],
            'best_for': [],
            'compromises': []
        }
        
        # Extract product info
        name = product.get('name', '')
        price = product.get('price', 0)
        specs = product.get('specs', '').lower()
        match_score = product.get('match_score', 0)
        
        # Budget match
        budget_max = requirements.get('budget_max')
        if budget_max and price <= budget_max:
            explanations['why_this_product'].append(f"Fits your ₹{budget_max:,} budget (₹{price:,})")
        
        # Use case matching
        use_cases = requirements.get('use_case') or []
        if 'gaming' in [uc.lower() for uc in use_cases]:
            if 'rtx' in specs or 'gaming' in specs:
                explanations['best_for'].append('Gaming')
                explanations['why_this_product'].append('Gaming-optimized GPU')
        
        if 'coding' in [uc.lower() for uc in use_cases]:
            if 'i7' in specs or 'i9' in specs or 'ryzen 7' in specs:
                explanations['best_for'].append('Coding & Development')
                explanations['why_this_product'].append('High-performance processor')
        
        # Persona-specific explanations
        persona_type = persona.get('type', 'general')
        if persona_type == 'student':
            if price < budget_max * 0.8 if budget_max else True:
                explanations['why_this_product'].append('Great value for students')
        
        # Trade-offs
        if conflicts:
            for conflict in conflicts:
                if conflict['severity'] == 'high':
                    explanations['trade_offs'].append(conflict['explanation'])
        
        # Generate summary
        if not explanations['why_this_product']:
            explanations['why_this_product'].append('Matches your basic requirements')
        
        return explanations
    
    def generate_product_summary(self, product: Dict, explanations: Dict) -> str:
        """Generate a concise summary for the product"""
        why = explanations.get('why_this_product', [])
        best_for = explanations.get('best_for', [])
        
        summary_parts = []
        
        if why:
            summary_parts.append(why[0])
        
        if best_for:
            summary_parts.append(f"Best for: {', '.join(best_for)}")
        
        return ". ".join(summary_parts) if summary_parts else "Matches your requirements"


class SIDBAEngine:
    """Main SIDBA engine that orchestrates all components"""
    
    def __init__(self):
        self.intent_engine = IntentDecompositionEngine()
        self.tradeoff_intelligence = TradeOffIntelligence()
        self.persona_simulator = BuyerPersonaSimulator()
        self.explanation_generator = DecisionExplanationGenerator()
    
    def process_intent(self, user_text: str, parsed_requirements: Dict) -> Dict:
        """Process user intent and return enriched requirements with SIDBA insights"""
        
        # Extract user type
        user_type = self.intent_engine.extract_user_type(user_text)
        longevity_priority = self.intent_engine.extract_longevity_priority(user_text)
        
        # Detect conflicts
        conflicts = self.tradeoff_intelligence.detect_conflicts(parsed_requirements, user_text)
        tradeoff_explanation = self.tradeoff_intelligence.generate_tradeoff_explanation(conflicts)
        
        # Detect persona
        persona = self.persona_simulator.detect_persona(parsed_requirements, user_text, user_type)
        
        # Enrich parsed requirements
        enriched_requirements = parsed_requirements.copy()
        enriched_requirements['user_type'] = user_type
        enriched_requirements['longevity_priority'] = longevity_priority
        enriched_requirements['persona'] = persona
        enriched_requirements['conflicts'] = conflicts
        enriched_requirements['tradeoff_explanation'] = tradeoff_explanation
        
        return enriched_requirements
    
    def enhance_product_explanations(self, products: List[Dict], requirements: Dict) -> List[Dict]:
        """Enhance products with SIDBA explanations"""
        persona = requirements.get('persona') or {}
        conflicts = requirements.get('conflicts') or []
        
        enhanced_products = []
        for product in products:
            product_copy = product.copy()
            
            # Generate explanations
            explanations = self.explanation_generator.generate_explanation(
                product, requirements, persona, conflicts
            )
            
            product_copy['sidba_explanations'] = explanations
            product_copy['summary'] = self.explanation_generator.generate_product_summary(
                product, explanations
            )
            
            enhanced_products.append(product_copy)
        
        return enhanced_products

