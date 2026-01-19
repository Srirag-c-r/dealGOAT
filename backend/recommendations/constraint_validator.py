"""
Hard Constraint Validator - Enforces non-negotiable requirements

This module ensures:
1. Budget limits are NEVER exceeded (hard stop)
2. Negative constraints are respected (e.g., "no curved screen")
3. Minimum specs are met (RAM, storage, processor)
"""

from typing import Dict, List, Tuple, Optional
import re


class ConstraintValidator:
    """Validates products against hard constraints with zero tolerance"""
    
    def __init__(self):
        # Negative constraint patterns
        self.negative_patterns = {
            'curved_screen': [
                'curved', 'curve', 'quad curve', '4d curve', 'edge display',
                'waterfall', 'hyperglow curve', 'curved edge'
            ],
            'gaming': ['gaming', 'gamer', 'game', 'rog', 'legion', 'predator', 'nitro'],
            'heavy': ['heavy', 'bulky', 'thick'],
            'large': ['large', 'big', 'huge', '17 inch', '17"', '18 inch'],
            'small': ['small', 'mini', 'compact', 'tiny'],
            'touchscreen': ['touchscreen', 'touch screen', 'touch display'],
            'convertible': ['convertible', '2-in-1', '2 in 1', 'flip'],
        }
        
        # Minimum viable specs for common use cases
        self.minimum_specs = {
            'video_editing': {'ram_gb': 16, 'storage_gb': 512},
            'photo_editing': {'ram_gb': 16, 'storage_gb': 512},
            'coding': {'ram_gb': 8, 'storage_gb': 256},
            'professional': {'ram_gb': 8, 'storage_gb': 256},
            'ai': {'ram_gb': 16, 'storage_gb': 512},
            'machine_learning': {'ram_gb': 16, 'storage_gb': 512},
        }
                # 'gaming' will be handled dynamically based on device type
    
    def validate_product(self, product: Dict, requirements: Dict) -> Tuple[bool, List[str]]:
        """
        Validate product against ALL hard constraints
        
        Returns:
            (is_valid, violations) - violations list explains why product was rejected
        """
        violations = []
        
        # 1. BUDGET CHECK (HIGHEST PRIORITY - HARD STOP)
        budget_valid, budget_violation = self.validate_budget(product, requirements)
        if not budget_valid:
            violations.append(budget_violation)
            return False, violations  # Immediate rejection
        
        # 2. NEGATIVE CONSTRAINTS
        negative_valid, negative_violations = self.validate_negative_constraints(product, requirements)
        if not negative_valid:
            violations.extend(negative_violations)
            return False, violations  # Immediate rejection
        
        # 3. MINIMUM SPECS
        specs_valid, spec_violations = self.validate_minimum_specs(product, requirements)
        if not specs_valid:
            violations.extend(spec_violations)
            return False, violations
        
        return True, []
    
    def validate_budget(self, product: Dict, requirements: Dict) -> Tuple[bool, Optional[str]]:
        """
        HARD BUDGET ENFORCEMENT - Zero tolerance
        
        Returns:
            (is_valid, violation_message)
        """
        budget_max = requirements.get('budget_max')
        
        # If no budget specified, allow all
        if not budget_max:
            return True, None
        
        # Get product price
        price = product.get('price', 0)
        if isinstance(price, str):
            try:
                price = int(float(price.replace(',', '').replace('₹', '')))
            except:
                price = 0
        
        # HARD STOP: No exceptions, no "close enough"
        if price > budget_max:
            violation = f"Price ₹{price:,} exceeds budget limit ₹{budget_max:,}"
            return False, violation
        
        return True, None
    
    def validate_negative_constraints(self, product: Dict, requirements: Dict) -> Tuple[bool, List[str]]:
        """
        Check if product violates any "NO X" constraints
        
        Examples:
            - "no curved screen" → reject curved displays
            - "not for gaming" → reject gaming laptops
            - "flat display only" → reject curved phones
        """
        violations = []
        
        # Extract negative constraints from requirements
        negative_constraints = requirements.get('negative_constraints', [])
        if not negative_constraints:
            # Try to infer from text
            user_text = requirements.get('original_text', '').lower()
            negative_constraints = self._extract_negative_constraints(user_text)
        
        if not negative_constraints:
            return True, []
        
        # Check product name and specs
        product_text = f"{product.get('name', '')} {product.get('specs', '')}".lower()
        
        for constraint in negative_constraints:
            if constraint in self.negative_patterns:
                patterns = self.negative_patterns[constraint]
                for pattern in patterns:
                    if pattern in product_text:
                        violations.append(f"Violates '{constraint}' constraint (found '{pattern}')")
                        return False, violations
        
        return True, []
    
    def _extract_negative_constraints(self, user_text: str) -> List[str]:
        """Extract negative constraints from natural language"""
        constraints = []
        
        # Pattern: "no X", "not X", "without X", "avoid X"
        negative_phrases = [
            r'no\s+curved',
            r'not\s+curved',
            r'flat\s+screen',
            r'flat\s+display',
            r'no\s+gaming',
            r'not\s+for\s+gaming',
            r'avoid\s+gaming',
            r'no\s+touchscreen',
            r'not\s+touchscreen',
        ]
        
        for phrase in negative_phrases:
            if re.search(phrase, user_text):
                if 'curved' in phrase or 'flat' in phrase:
                    constraints.append('curved_screen')
                elif 'gaming' in phrase:
                    constraints.append('gaming')
                elif 'touchscreen' in phrase:
                    constraints.append('touchscreen')
        
        return constraints
    
    def validate_minimum_specs(self, product: Dict, requirements: Dict) -> Tuple[bool, List[str]]:
        """
        Verify product meets minimum viable specs for intended use case
        
        Example: "Video editing laptop" needs at least 16GB RAM, 512GB storage
        """
        violations = []
        
        # Get use cases
        use_cases = requirements.get('use_case') or []
        if not use_cases:
            return True, []  # No specific use case, skip validation
        
        # Extract product specs
        product_specs = self._extract_specs_from_product(product)
        
        # Check each use case
        for use_case in use_cases:
            use_case_lower = str(use_case).lower()
            
            # Find matching minimum spec requirement
            for spec_key, min_specs in self.minimum_specs.items():
                if spec_key in use_case_lower:
                    # Check RAM
                    if 'ram_gb' in min_specs:
                        required_ram = min_specs['ram_gb']
                        actual_ram = product_specs.get('ram_gb', 0)
                        if actual_ram < required_ram:
                            violations.append(
                                f"{use_case} requires {required_ram}GB RAM, product has {actual_ram}GB"
                            )
                    
                    # Check Storage
                    if 'storage_gb' in min_specs:
                        required_storage = min_specs['storage_gb']
                        actual_storage = product_specs.get('storage_gb', 0)
                        if actual_storage < required_storage:
                            violations.append(
                                f"{use_case} requires {required_storage}GB storage, product has {actual_storage}GB"
                            )
        
        return len(violations) == 0, violations
    
    def _extract_specs_from_product(self, product: Dict) -> Dict:
        """
        Extract numerical specs from product name and specs with smart heuristics
        
        Handles formats like:
        - "16GB RAM" (Explicit)
        - "16GB/512GB" (Implicit/Split)
        - "8GB | 256GB" (Separator)
        """
        text = f"{product.get('name', '')} {product.get('specs', '')}".lower()
        
        specs = {
            'ram_gb': 0,
            'storage_gb': 0,
        }
        
        # 1. Try Explicit RAM Matches first (Strongest signal)
        ram_explicit = re.search(r'(\d+)\s*gb\s*ram', text)
        if ram_explicit:
            specs['ram_gb'] = int(ram_explicit.group(1))
            
        # 2. Try Explicit Storage Matches
        storage_explicit = re.search(r'(\d+)\s*(?:gb|tb)\s*(?:ssd|hdd|storage)', text)
        if storage_explicit:
            val = int(storage_explicit.group(1))
            if 'tb' in storage_explicit.group(0):
                val *= 1024
            specs['storage_gb'] = val
            
        # 3. If missing, use Heuristics on all file size patterns
        # Find all "XX GB" patterns
        all_sizes_matches = re.finditer(r'(\d+)\s*(?:gb|tb|g)(?!\w)', text)
        found_values = []
        
        for m in all_sizes_matches:
            val = int(m.group(1))
            unit_str = m.group(0)
            if 'tb' in unit_str:
                val *= 1024
            found_values.append(val)
            
        # Sort values to process
        # Typically: Small value = RAM, Large value = Storage
        for val in found_values:
            # Heuristic: RAM is usually <= 128GB
            if specs['ram_gb'] == 0 and 4 <= val <= 128:
                # Double check: Is this likely storage? (e.g. "64GB" phone storage)
                # If we already have a larger value that looks like storage, this might be RAM
                # If we have nothing, assume smallest valid RAM-like number is RAM
                specs['ram_gb'] = val
            
            # Heuristic: Storage is usually >= 128GB or explicit TB
            elif specs['storage_gb'] == 0 and val >= 128:
                specs['storage_gb'] = val
                
            # Edge case: If we found another large value, update storage to be the max
            elif val > specs['storage_gb'] and val >= 128:
                specs['storage_gb'] = val
                
        return specs
    
    def get_constraint_summary(self, requirements: Dict) -> Dict:
        """
        Generate human-readable summary of active constraints
        
        Useful for debugging and user feedback
        """
        summary = {
            'budget_limit': requirements.get('budget_max'),
            'negative_constraints': requirements.get('negative_constraints', []),
            'minimum_specs': {},
        }
        
        use_cases = requirements.get('use_case') or []
        for use_case in use_cases:
            use_case_lower = str(use_case).lower()
            for spec_key, min_specs in self.minimum_specs.items():
                if spec_key in use_case_lower:
                    summary['minimum_specs'][use_case] = min_specs
        
        return summary
