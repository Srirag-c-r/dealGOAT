"""
Semantic Matcher - Maps user intent to product capabilities

Solves "Literal Blindness" by:
1. Converting vague requirements ("AI laptop") to concrete specs
2. Inferring missing specs from brand/model knowledge
3. Understanding semantic equivalence (not just keyword matching)
"""

from typing import Dict, List, Set
import re


class SemanticMatcher:
    """Intelligent requirement expansion and spec inference"""
    
    def __init__(self):
        # Intent to concrete specs mapping
        self.intent_mappings = {
            # AI/ML workloads
            'ai': {
                'min_ram_gb': 16,
                'min_processor_tier': ['i7', 'i9', 'ryzen 7', 'ryzen 9', 'm1', 'm2', 'm3'],
                'preferred_keywords': ['workstation', 'creator', 'professional', 'studio'],
                'reject_keywords': ['celeron', 'pentium', 'atom', 'basic'],
                'use_cases': ['ai', 'machine learning', 'deep learning', 'data science']
            },
            
            # Gaming
            'gaming': {
                'min_ram_gb': 8,
                'min_refresh_rate': 120,
                'preferred_keywords': ['rtx', 'gtx', 'radeon', 'snapdragon 8', 'dimensity 9000', 'cooling', 'rgb'],
                'reject_keywords': ['integrated graphics', 'uhd graphics'],
                'use_cases': ['gaming', 'esports', 'streaming']
            },
            
            # Video editing
            'video_editing': {
                'min_ram_gb': 16,
                'min_storage_gb': 512,
                'min_processor_tier': ['i7', 'i9', 'ryzen 7', 'ryzen 9', 'm1 pro', 'm2 pro'],
                'preferred_keywords': ['dedicated gpu', 'rtx', 'color accurate', 'calibrated'],
                'use_cases': ['video editing', '4k editing', 'content creation']
            },
            
            # Photo editing
            'photo_editing': {
                'min_ram_gb': 16,
                'min_storage_gb': 512,
                'preferred_keywords': ['color accurate', 'wide gamut', 'calibrated', 'adobe rgb', 'dci-p3'],
                'use_cases': ['photo editing', 'photography', 'lightroom', 'photoshop']
            },
            
            # Coding/Development
            'coding': {
                'min_ram_gb': 8,
                'min_storage_gb': 256,
                'preferred_keywords': ['ssd', 'backlit keyboard', 'good keyboard'],
                'use_cases': ['coding', 'programming', 'development', 'software engineering']
            }
        }
        
        # Brand knowledge base (infer missing specs)
        self.brand_knowledge = {
            # Laptop brands
            'thinkpad': {
                'keyboard_quality': 'excellent',
                'keyboard_travel_mm': 1.5,
                'build_quality': 'premium',
                'durability': 'excellent',
                'typical_use': 'business',
                'known_for': ['keyboard', 'reliability', 'business']
            },
            'macbook': {
                'keyboard_quality': 'good',
                'keyboard_travel_mm': 1.0,
                'build_quality': 'premium',
                'display_quality': 'excellent',
                'typical_use': 'creative',
                'known_for': ['display', 'build quality', 'battery life']
            },
            'dell xps': {
                'keyboard_quality': 'good',
                'keyboard_travel_mm': 1.3,
                'build_quality': 'premium',
                'display_quality': 'excellent',
                'typical_use': 'professional',
                'known_for': ['display', 'build quality', 'performance']
            },
            'asus zenbook': {
                'keyboard_quality': 'good',
                'keyboard_travel_mm': 1.4,
                'build_quality': 'premium',
                'display_quality': 'excellent',
                'typical_use': 'professional',
                'known_for': ['portability', 'display', 'design']
            },
            'hp pavilion': {
                'keyboard_quality': 'average',
                'keyboard_travel_mm': 1.2,
                'build_quality': 'good',
                'typical_use': 'general',
                'known_for': ['value', 'reliability']
            },
            
            # Gaming laptop brands
            'rog': {
                'gaming_performance': 'flagship',
                'cooling': 'excellent',
                'display_refresh_rate': 144,
                'typical_use': 'gaming',
                'known_for': ['gaming', 'cooling', 'performance']
            },
            'legion': {
                'gaming_performance': 'flagship',
                'cooling': 'excellent',
                'display_refresh_rate': 165,
                'typical_use': 'gaming',
                'known_for': ['gaming', 'value', 'performance']
            },
            'predator': {
                'gaming_performance': 'flagship',
                'cooling': 'excellent',
                'typical_use': 'gaming',
                'known_for': ['gaming', 'aggressive design']
            },
            
            # Phone brands
            'rog phone': {
                'bypass_charging': True,
                'cooling': 'excellent',
                'gaming_performance': 'flagship',
                'refresh_rate': 165,
                'typical_use': 'gaming',
                'known_for': ['gaming', 'cooling', 'bypass charging']
            },
            'iphone': {
                'camera_quality': 'excellent',
                'video_recording': 'excellent',
                'build_quality': 'premium',
                'software_updates': 'long-term',
                'typical_use': 'general/creative',
                'known_for': ['camera', 'video', 'ecosystem']
            },
            'pixel': {
                'camera_quality': 'excellent',
                'software_experience': 'clean',
                'ai_features': True,
                'typical_use': 'photography',
                'known_for': ['camera', 'clean android', 'ai']
            },
            'samsung galaxy s': {
                'camera_quality': 'excellent',
                'display_quality': 'excellent',
                'build_quality': 'premium',
                'typical_use': 'flagship',
                'known_for': ['display', 'camera', 'features']
            }
        }
        
        # Semantic equivalents (different ways to say the same thing)
        self.semantic_equivalents = {
            'good_keyboard': ['excellent keyboard', 'great typing', 'comfortable keyboard', 'mechanical keyboard'],
            'bypass_charging': ['direct power', 'passthrough charging', 'battery bypass'],
            'fast_charging': ['quick charge', 'rapid charging', 'fast charge', 'super fast charging'],
            'high_refresh': ['120hz', '144hz', '165hz', 'high refresh rate', 'smooth display'],
            'color_accurate': ['wide gamut', 'color calibrated', 'adobe rgb', 'dci-p3', 'professional display']
        }
    
    def expand_requirements(self, requirements: Dict) -> Dict:
        """
        Expand vague requirements to concrete specs
        
        Example:
            Input: {"use_case": ["ai", "coding"]}
            Output: {"min_ram_gb": 16, "min_processor_tier": ["i7", ...], ...}
        """
        expanded = requirements.copy()
        
        # Get use cases
        use_cases = requirements.get('use_case') or []
        must_have = requirements.get('must_have_features') or []
        
        # Combine for analysis
        all_requirements = ' '.join([str(uc) for uc in use_cases] + [str(mh) for mh in must_have]).lower()
        
        # Detect intents and expand
        detected_intents = []
        
        for intent_key, intent_data in self.intent_mappings.items():
            # Check if any use case matches this intent
            if any(uc in all_requirements for uc in intent_data.get('use_cases', [])):
                detected_intents.append(intent_key)
        
        # Also check for direct keywords
        if 'ai' in all_requirements or 'machine learning' in all_requirements:
            detected_intents.append('ai')
        if 'gaming' in all_requirements or 'gamer' in all_requirements:
            detected_intents.append('gaming')
        if 'video edit' in all_requirements:
            detected_intents.append('video_editing')
        if 'photo edit' in all_requirements or 'photography' in all_requirements:
            detected_intents.append('photo_editing')
        if 'coding' in all_requirements or 'programming' in all_requirements:
            detected_intents.append('coding')
        
        # Expand based on detected intents
        for intent in detected_intents:
            intent_data = self.intent_mappings.get(intent, {})
            
            # Set minimum RAM if not specified
            if 'ram_needed_gb' not in expanded or not expanded['ram_needed_gb']:
                min_ram = intent_data.get('min_ram_gb')
                if min_ram:
                    expanded['ram_needed_gb'] = min_ram
                    expanded['_inferred_ram'] = True
            
            # Set minimum storage if not specified
            if 'storage_needed_gb' not in expanded or not expanded['storage_needed_gb']:
                min_storage = intent_data.get('min_storage_gb')
                if min_storage:
                    expanded['storage_needed_gb'] = min_storage
                    expanded['_inferred_storage'] = True
            
            # Add preferred keywords to must_have
            preferred = intent_data.get('preferred_keywords', [])
            if preferred and 'semantic_keywords' not in expanded:
                expanded['semantic_keywords'] = preferred
            
            # Add reject keywords
            reject = intent_data.get('reject_keywords', [])
            if reject and 'semantic_reject_keywords' not in expanded:
                expanded['semantic_reject_keywords'] = reject
        
        return expanded
    
    def infer_missing_specs(self, product: Dict) -> Dict:
        """
        Infer missing specs from brand/model knowledge
        
        Example:
            Input: {"name": "ThinkPad X1 Carbon"}
            Output: {"keyboard_travel_mm": 1.5, "keyboard_quality": "excellent", ...}
        """
        product_copy = product.copy()
        product_name = product.get('name', '').lower()
        
        # Try to match brand
        matched_brand = None
        for brand_key in self.brand_knowledge.keys():
            if brand_key.lower() in product_name:
                matched_brand = brand_key
                break
        
        if matched_brand:
            brand_data = self.brand_knowledge[matched_brand]
            inferred_specs = {}
            
            for spec_key, spec_value in brand_data.items():
                # Add inferred spec if not already present
                if spec_key not in product_copy:
                    inferred_specs[spec_key] = spec_value
                    product_copy[f'{spec_key}_inferred'] = True
            
            # Add metadata
            product_copy['_inferred_from_brand'] = matched_brand
            product_copy['_inferred_specs'] = inferred_specs
        
        return product_copy
    
    def check_semantic_match(self, product: Dict, requirement: str) -> bool:
        """
        Check if product matches requirement semantically (not just keyword)
        
        Example:
            Requirement: "good keyboard"
            Product: "ThinkPad X1" (no "good keyboard" in name)
            Result: True (ThinkPad known for keyboards)
        """
        product_name = product.get('name', '').lower()
        requirement_lower = requirement.lower()
        
        # Direct keyword match
        if requirement_lower in product_name:
            return True
        
        # Check semantic equivalents
        for semantic_key, equivalents in self.semantic_equivalents.items():
            if requirement_lower in equivalents or semantic_key.replace('_', ' ') in requirement_lower:
                # Check if product has this capability
                if semantic_key == 'good_keyboard':
                    # Check brand knowledge
                    for brand_key, brand_data in self.brand_knowledge.items():
                        if brand_key in product_name:
                            if brand_data.get('keyboard_quality') in ['excellent', 'good']:
                                return True
                
                elif semantic_key == 'bypass_charging':
                    for brand_key, brand_data in self.brand_knowledge.items():
                        if brand_key in product_name:
                            if brand_data.get('bypass_charging'):
                                return True
                
                elif semantic_key == 'high_refresh':
                    # Check for refresh rate in specs
                    specs = product.get('specs', '').lower()
                    if any(rate in specs for rate in ['120hz', '144hz', '165hz']):
                        return True
        
        return False
    
    def validate_capability_claim(self, product: Dict, claimed_capability: str) -> bool:
        """
        Validate if product can actually deliver claimed capability
        
        Example:
            Product: "AI Gaming Beast - ₹15k, 4GB RAM, Celeron"
            Claimed: "AI"
            Result: False (4GB RAM + Celeron can't handle AI workloads)
        """
        product_text = f"{product.get('name', '')} {product.get('specs', '')}".lower()
        claimed_lower = claimed_capability.lower()
        
        # If capability is claimed, verify hardware supports it
        if claimed_lower in product_text:
            # Get intent requirements
            intent_data = None
            for intent_key, data in self.intent_mappings.items():
                if claimed_lower in data.get('use_cases', []):
                    intent_data = data
                    break
            
            if intent_data:
                # Extract actual specs
                ram_match = re.search(r'(\d+)\s*gb\s*ram', product_text)
                actual_ram = int(ram_match.group(1)) if ram_match else 0
                
                # Check minimum requirements
                min_ram = intent_data.get('min_ram_gb', 0)
                if min_ram > 0 and actual_ram < min_ram:
                    return False  # Claim not supported by hardware
                
                # Check for reject keywords
                reject_keywords = intent_data.get('reject_keywords', [])
                if any(keyword in product_text for keyword in reject_keywords):
                    return False  # Has disqualifying components
        
        return True  # Claim is valid or not made
