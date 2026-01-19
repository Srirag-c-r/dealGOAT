"""
Spec Verification Engine - Detects keyword stuffing and validates hardware claims

This module:
1. Calculates credibility scores for products
2. Detects impossible hardware combinations
3. Identifies SEO spam and keyword stuffing
4. Validates claimed specs against known hardware reality
"""

from typing import Dict, List, Tuple
import re


class SpecVerifier:
    """Verifies product specifications and detects spam"""
    
    def __init__(self):
        # Known impossible/suspicious combinations
        self.impossible_combos = {
            # Low RAM + High-end claims
            ('4gb ram', 'ai'): {'spam_score': 40, 'reason': '4GB RAM insufficient for AI workloads'},
            ('4gb ram', 'gaming'): {'spam_score': 35, 'reason': '4GB RAM insufficient for modern gaming'},
            ('4gb ram', 'video editing'): {'spam_score': 45, 'reason': '4GB RAM insufficient for video editing'},
            ('2gb ram', 'professional'): {'spam_score': 50, 'reason': '2GB RAM insufficient for professional work'},
            
            # Low-end processors + High-end claims
            ('celeron', 'gaming'): {'spam_score': 40, 'reason': 'Celeron not suitable for gaming'},
            ('celeron', 'video editing'): {'spam_score': 45, 'reason': 'Celeron not suitable for video editing'},
            ('pentium', 'ai'): {'spam_score': 40, 'reason': 'Pentium not suitable for AI workloads'},
            ('atom', 'professional'): {'spam_score': 45, 'reason': 'Atom not suitable for professional work'},
            
            # Storage + Claims mismatches
            ('64gb storage', 'video editing'): {'spam_score': 40, 'reason': '64GB storage insufficient for video editing'},
            ('128gb storage', 'gaming'): {'spam_score': 30, 'reason': '128GB storage insufficient for modern games'},
            
            # Budget phones + Premium claims
            ('₹6000', 'flagship'): {'spam_score': 45, 'reason': 'Price too low for flagship specs'},
            ('₹8000', 'premium'): {'spam_score': 40, 'reason': 'Price too low for premium features'},
        }
        
        # Marketing buzzwords (high frequency = spam)
        self.buzzwords = [
            'ai', 'ultra', 'pro', 'max', 'premium', 'flagship', 'beast', 'monster',
            'killer', 'ultimate', 'extreme', 'revolutionary', 'next-gen', 'advanced',
            'professional', 'studio', 'creator', 'powerhouse', 'performance', 'gaming'
        ]
        
        # Actual spec keywords (presence indicates real specs)
        self.real_spec_keywords = [
            'gb ram', 'gb storage', 'ssd', 'hdd', 'ghz', 'cores', 'threads',
            'mah', 'mp camera', 'inch display', 'hz', 'resolution', 'nits'
        ]
    
    def verify_product(self, product: Dict) -> Dict:
        """
        Comprehensive product verification
        
        Returns:
            {
                'credibility_score': 0-100 (100 = highly credible),
                'spam_score': 0-100 (0 = not spam, 100 = definitely spam),
                'red_flags': [...],
                'is_credible': bool (credibility_score >= 60)
            }
        """
        product_text = f"{product.get('name', '')} {product.get('specs', '')}".lower()
        price = product.get('price', 0)
        
        # Calculate individual scores
        keyword_spam_score = self._calculate_keyword_spam_score(product_text)
        impossible_combo_score = self._check_impossible_combos(product_text, price)
        spec_density_score = self._calculate_spec_density(product_text)
        
        # Red flags
        red_flags = []
        
        if keyword_spam_score > 40:
            red_flags.append(f"High keyword stuffing detected (score: {keyword_spam_score})")
        
        if impossible_combo_score > 0:
            red_flags.append(f"Impossible hardware combination detected")
        
        if spec_density_score < 30:
            red_flags.append("Low actual spec density (mostly marketing fluff)")
        
        # Calculate final spam score (0-100, higher = more spam)
        spam_score = (
            keyword_spam_score * 0.4 +
            impossible_combo_score * 0.4 +
            (100 - spec_density_score) * 0.2
        )
        
        # Credibility is inverse of spam
        credibility_score = max(0, 100 - spam_score)
        
        return {
            'credibility_score': round(credibility_score, 1),
            'spam_score': round(spam_score, 1),
            'red_flags': red_flags,
            'is_credible': credibility_score >= 60,
            'breakdown': {
                'keyword_spam': keyword_spam_score,
                'impossible_combos': impossible_combo_score,
                'spec_density': spec_density_score
            }
        }
    
    def _calculate_keyword_spam_score(self, product_text: str) -> float:
        """
        Detect keyword stuffing by counting buzzwords vs real specs
        
        Returns: 0-100 (higher = more spam)
        """
        # Count buzzwords
        buzzword_count = sum(1 for word in self.buzzwords if word in product_text)
        
        # Count real specs
        real_spec_count = sum(1 for spec in self.real_spec_keywords if spec in product_text)
        
        # If more buzzwords than specs, likely spam
        if real_spec_count == 0:
            return 80  # No real specs = high spam
        
        buzzword_ratio = buzzword_count / max(real_spec_count, 1)
        
        # Ratio > 2 means 2x more buzzwords than specs
        if buzzword_ratio > 3:
            return 70
        elif buzzword_ratio > 2:
            return 50
        elif buzzword_ratio > 1:
            return 30
        else:
            return 10
    
    def _check_impossible_combos(self, product_text: str, price: int) -> float:
        """
        Check for hardware combinations that violate physical/economic reality
        
        Returns: 0-100 (higher = more suspicious)
        """
        max_spam_score = 0
        
        for (spec1, spec2), combo_data in self.impossible_combos.items():
            if spec1 in product_text and spec2 in product_text:
                max_spam_score = max(max_spam_score, combo_data['spam_score'])
        
        # Price-based checks
        if price > 0:
            # Flagship claims at budget prices
            if price < 10000 and any(word in product_text for word in ['flagship', 'premium', 'pro max']):
                max_spam_score = max(max_spam_score, 50)
            
            # Professional claims at ultra-budget prices
            if price < 15000 and 'professional' in product_text and 'video editing' in product_text:
                max_spam_score = max(max_spam_score, 45)
        
        return max_spam_score
    
    def _calculate_spec_density(self, product_text: str) -> float:
        """
        Calculate ratio of real specs to total words
        
        Returns: 0-100 (higher = more real specs)
        """
        # Count total meaningful words (exclude common words)
        words = product_text.split()
        meaningful_words = [w for w in words if len(w) > 3]
        
        if not meaningful_words:
            return 0
        
        # Count spec mentions
        spec_mentions = sum(1 for spec in self.real_spec_keywords if spec in product_text)
        
        # Density = specs per 10 words
        density = (spec_mentions / len(meaningful_words)) * 100
        
        return min(100, density * 10)  # Scale up for better distribution
    
    def get_credibility_tier(self, credibility_score: float) -> str:
        """Convert credibility score to human-readable tier"""
        if credibility_score >= 80:
            return "Highly Credible"
        elif credibility_score >= 60:
            return "Credible"
        elif credibility_score >= 40:
            return "Questionable"
        else:
            return "Likely Spam"
    
    def extract_real_specs(self, product: Dict) -> Dict:
        """
        Extract verifiable specs from product
        
        Returns: {ram_gb, storage_gb, processor, display, etc.}
        """
        text = f"{product.get('name', '')} {product.get('specs', '')}".lower()
        
        specs = {}
        
        # RAM
        ram_match = re.search(r'(\d+)\s*gb\s*ram', text)
        if ram_match:
            specs['ram_gb'] = int(ram_match.group(1))
        
        # Storage
        storage_match = re.search(r'(\d+)\s*(gb|tb)\s*(ssd|storage)', text)
        if storage_match:
            size = int(storage_match.group(1))
            unit = storage_match.group(2)
            if unit == 'tb':
                size *= 1024
            specs['storage_gb'] = size
            specs['storage_type'] = 'ssd' if 'ssd' in text else 'hdd'
        
        # Processor
        processor_patterns = [
            r'(intel\s+core\s+i[3579])',
            r'(ryzen\s+[3579])',
            r'(snapdragon\s+\d+)',
            r'(m[123]\s+chip)',
            r'(celeron|pentium|atom)',
        ]
        for pattern in processor_patterns:
            match = re.search(pattern, text)
            if match:
                specs['processor'] = match.group(1)
                break
        
        # Display size
        display_match = re.search(r'(\d+\.?\d*)\s*(?:inch|")', text)
        if display_match:
            specs['display_inches'] = float(display_match.group(1))
        
        # Refresh rate
        refresh_match = re.search(r'(\d+)\s*hz', text)
        if refresh_match:
            specs['refresh_rate_hz'] = int(refresh_match.group(1))
        
        # Battery
        battery_match = re.search(r'(\d+)\s*mah', text)
        if battery_match:
            specs['battery_mah'] = int(battery_match.group(1))
        
        return specs
