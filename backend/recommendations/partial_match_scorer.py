"""
Partial Match Scorer - Scores products by % of requirements met

Solves "Zero-Match Error" by:
1. Scoring products by percentage of requirements met (not binary pass/fail)
2. Showing 75% matches with clear explanation of what's missing
3. Tiered results: Perfect (100%) → High (75-99%) → Partial (60-74%)
"""

from typing import Dict, List, Tuple
import re


class PartialMatchScorer:
    """Calculates match percentage and determines if product should be shown"""
    
    def __init__(self):
        # Requirement weights (how important each type is)
        self.requirement_weights = {
            'budget': 100,  # Hard constraint - must be 100%
            'negative_constraints': 100,  # Hard constraint - must be 100%
            'must_have_features': 60,  # Important but can be partial
            'nice_to_have': 30,  # Least important
            'specs': 50,  # RAM, storage, processor
        }
    
    def calculate_match_score(self, product: Dict, requirements: Dict, semantic_matcher=None) -> Dict:
        """
        Calculate comprehensive match score
        
        Returns:
            {
                'overall_percentage': 85,
                'tier': 'high_match',  # perfect/high/partial/low
                'met_requirements': [...],
                'missing_requirements': [...],
                'partial_matches': [...],
                'should_show': True,
                'match_explanation': "Matches 4 of 5 requirements..."
            }
        """
        result = {
            'met_requirements': [],
            'missing_requirements': [],
            'partial_matches': [],
            'requirement_scores': {},
            'should_show': False,
            'tier': 'low_match'
        }
        
        total_weight = 0
        achieved_weight = 0
        
        # 1. Budget (HARD CONSTRAINT)
        budget_score, budget_met = self._check_budget(product, requirements)
        if not budget_met:
            # Budget violation - immediate rejection
            result['overall_percentage'] = 0
            result['should_show'] = False
            result['match_explanation'] = "Exceeds budget limit"
            result['missing_requirements'].append('budget')
            return result
        
        result['met_requirements'].append('budget')
        result['requirement_scores']['budget'] = 100
        total_weight += self.requirement_weights['budget']
        achieved_weight += self.requirement_weights['budget']
        
        # 2. Negative Constraints (HARD CONSTRAINT)
        negative_score, negative_met = self._check_negative_constraints(product, requirements)
        if not negative_met:
            # Constraint violation - immediate rejection
            result['overall_percentage'] = 0
            result['should_show'] = False
            result['match_explanation'] = "Violates negative constraints"
            result['missing_requirements'].append('negative_constraints')
            return result
        
        if requirements.get('negative_constraints'):
            result['met_requirements'].append('negative_constraints')
            result['requirement_scores']['negative_constraints'] = 100
            total_weight += self.requirement_weights['negative_constraints']
            achieved_weight += self.requirement_weights['negative_constraints']
        
        # 3. Must-Have Features (SOFT - can be partial)
        must_have_score, must_have_details = self._check_must_have_features(
            product, requirements, semantic_matcher
        )
        result['requirement_scores']['must_have_features'] = must_have_score
        total_weight += self.requirement_weights['must_have_features']
        achieved_weight += (must_have_score / 100) * self.requirement_weights['must_have_features']
        
        if must_have_score == 100:
            result['met_requirements'].append('must_have_features')
        elif must_have_score >= 50:
            result['partial_matches'].append(f"must_have_features ({must_have_score}%)")
        else:
            result['missing_requirements'].append('must_have_features')
        
        result['must_have_details'] = must_have_details
        
        # 4. Nice-to-Have Features (SOFT - can be partial)
        nice_to_have_score, nice_details = self._check_nice_to_have(
            product, requirements, semantic_matcher
        )
        result['requirement_scores']['nice_to_have'] = nice_to_have_score
        total_weight += self.requirement_weights['nice_to_have']
        achieved_weight += (nice_to_have_score / 100) * self.requirement_weights['nice_to_have']
        
        if nice_to_have_score >= 50:
            result['partial_matches'].append(f"nice_to_have ({nice_to_have_score}%)")
        
        result['nice_to_have_details'] = nice_details
        
        # 5. Spec Requirements (SOFT - can be partial)
        spec_score, spec_details = self._check_spec_requirements(product, requirements)
        result['requirement_scores']['specs'] = spec_score
        total_weight += self.requirement_weights['specs']
        achieved_weight += (spec_score / 100) * self.requirement_weights['specs']
        
        if spec_score == 100:
            result['met_requirements'].append('specs')
        elif spec_score >= 50:
            result['partial_matches'].append(f"specs ({spec_score}%)")
        else:
            result['missing_requirements'].append('specs')
        
        result['spec_details'] = spec_details
        
        # Calculate overall percentage
        if total_weight > 0:
            overall_percentage = (achieved_weight / total_weight) * 100
        else:
            overall_percentage = 100  # No requirements = perfect match
        
        result['overall_percentage'] = round(overall_percentage, 1)
        
        # Determine tier and if should show
        if overall_percentage >= 95:
            result['tier'] = 'perfect_match'
            result['should_show'] = True
        elif overall_percentage >= 75:
            result['tier'] = 'high_match'
            result['should_show'] = True
        elif overall_percentage >= 60:
            result['tier'] = 'partial_match'
            result['should_show'] = True  # Show if not enough high matches
        else:
            result['tier'] = 'low_match'
            result['should_show'] = False
        
        # Generate explanation
        result['match_explanation'] = self._generate_explanation(result)
        
        return result
    
    def _check_budget(self, product: Dict, requirements: Dict) -> Tuple[float, bool]:
        """Check budget constraint (HARD)"""
        budget_max = requirements.get('budget_max')
        if not budget_max:
            return 100, True
        
        price = product.get('price', 0)
        if isinstance(price, str):
            try:
                price = int(float(price.replace(',', '').replace('₹', '')))
            except:
                price = 0
        
        if price <= budget_max:
            return 100, True
        else:
            return 0, False
    
    def _check_negative_constraints(self, product: Dict, requirements: Dict) -> Tuple[float, bool]:
        """Check negative constraints (HARD)"""
        negative_constraints = requirements.get('negative_constraints') or []
        if not negative_constraints:
            return 100, True
        
        product_text = f"{product.get('name', '')} {product.get('specs', '')}".lower()
        
        # Simplified check (full check done by ConstraintValidator)
        for constraint in negative_constraints:
            if constraint in product_text:
                return 0, False
        
        return 100, True
    
    def _check_must_have_features(self, product: Dict, requirements: Dict, semantic_matcher) -> Tuple[float, Dict]:
        """Check must-have features (SOFT - can be partial)"""
        must_have = requirements.get('must_have_features') or []
        if not must_have:
            return 100, {'total': 0, 'met': 0, 'missing': []}
        
        product_text = f"{product.get('name', '')} {product.get('specs', '')}".lower()
        
        met_count = 0
        missing = []
        
        for feature in must_have:
            feature_lower = str(feature).lower()
            
            # Direct match
            if feature_lower in product_text:
                met_count += 1
            # Semantic match (if semantic_matcher available)
            elif semantic_matcher and semantic_matcher.check_semantic_match(product, feature):
                met_count += 1
            else:
                missing.append(feature)
        
        score = (met_count / len(must_have)) * 100 if must_have else 100
        
        return score, {
            'total': len(must_have),
            'met': met_count,
            'missing': missing
        }
    
    def _check_nice_to_have(self, product: Dict, requirements: Dict, semantic_matcher) -> Tuple[float, Dict]:
        """Check nice-to-have features (SOFT - can be partial)"""
        nice_to_have = requirements.get('nice_to_have') or []
        if not nice_to_have:
            return 100, {'total': 0, 'met': 0}
        
        product_text = f"{product.get('name', '')} {product.get('specs', '')}".lower()
        
        met_count = 0
        
        for feature in nice_to_have:
            feature_lower = str(feature).lower()
            
            if feature_lower in product_text:
                met_count += 1
            elif semantic_matcher and semantic_matcher.check_semantic_match(product, feature):
                met_count += 1
        
        score = (met_count / len(nice_to_have)) * 100 if nice_to_have else 100
        
        return score, {
            'total': len(nice_to_have),
            'met': met_count
        }
    
    def _check_spec_requirements(self, product: Dict, requirements: Dict) -> Tuple[float, Dict]:
        """Check spec requirements like RAM, storage, processor (SOFT)"""
        product_text = f"{product.get('name', '')} {product.get('specs', '')}".lower()
        
        checks = []
        met = []
        missing = []
        
        # RAM check
        required_ram = requirements.get('ram_needed_gb')
        if required_ram:
            checks.append('ram')
            ram_match = re.search(r'(\d+)\s*gb\s*ram', product_text)
            actual_ram = int(ram_match.group(1)) if ram_match else 0
            
            if actual_ram >= required_ram:
                met.append('ram')
            else:
                missing.append(f"ram ({actual_ram}GB < {required_ram}GB required)")
        
        # Storage check
        required_storage = requirements.get('storage_needed_gb')
        if required_storage:
            checks.append('storage')
            storage_match = re.search(r'(\d+)\s*(gb|tb)\s*(ssd|storage)', product_text)
            if storage_match:
                size = int(storage_match.group(1))
                unit = storage_match.group(2)
                if unit == 'tb':
                    size *= 1024
                
                if size >= required_storage:
                    met.append('storage')
                else:
                    missing.append(f"storage ({size}GB < {required_storage}GB required)")
            else:
                missing.append('storage (not found)')
        
        # Processor check
        required_processor = requirements.get('processor_min')
        if required_processor:
            checks.append('processor')
            if str(required_processor).lower() in product_text:
                met.append('processor')
            else:
                missing.append(f"processor ({required_processor} not found)")
        
        if not checks:
            return 100, {'total': 0, 'met': 0, 'missing': []}
        
        score = (len(met) / len(checks)) * 100
        
        return score, {
            'total': len(checks),
            'met': len(met),
            'missing': missing
        }
    
    def _generate_explanation(self, result: Dict) -> str:
        """Generate human-readable explanation"""
        percentage = result['overall_percentage']
        tier = result['tier']
        
        if tier == 'perfect_match':
            return f"Perfect match ({percentage}%) - Meets all requirements"
        elif tier == 'high_match':
            missing = result.get('missing_requirements', [])
            if missing:
                return f"High match ({percentage}%) - Missing: {', '.join(missing)}"
            else:
                partial = result.get('partial_matches', [])
                return f"High match ({percentage}%) - Partial: {', '.join(partial[:2])}"
        elif tier == 'partial_match':
            missing = result.get('missing_requirements', [])
            return f"Partial match ({percentage}%) - Missing: {', '.join(missing[:2])}"
        else:
            return f"Low match ({percentage}%) - Does not meet minimum requirements"
    
    def filter_by_tier(self, scored_products: List[Dict], min_tier: str = 'partial_match') -> List[Dict]:
        """
        Filter products by minimum tier
        
        Tiers (in order): perfect_match > high_match > partial_match > low_match
        """
        tier_order = ['perfect_match', 'high_match', 'partial_match', 'low_match']
        min_tier_index = tier_order.index(min_tier) if min_tier in tier_order else 2
        
        filtered = []
        for product in scored_products:
            match_info = product.get('match_info', {})
            tier = match_info.get('tier', 'low_match')
            tier_index = tier_order.index(tier) if tier in tier_order else 3
            
            if tier_index <= min_tier_index:
                filtered.append(product)
        
        return filtered
