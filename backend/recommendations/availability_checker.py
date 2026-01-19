"""
Product Availability Checker - Verifies products can actually be purchased

This module:
1. Checks if product URLs are live and accessible
2. Detects "Out of Stock", "Pre-order", "Coming Soon" status
3. Verifies "Add to Cart" functionality exists
4. Filters out ghost/phantom products
"""

from typing import Dict, Tuple, Optional
import requests
from bs4 import BeautifulSoup
import time
import random


class AvailabilityChecker:
    """Verifies product availability on retailer websites"""
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        ]
        
        # Patterns indicating unavailability
        self.unavailable_patterns = {
            'out_of_stock': [
                'out of stock', 'currently unavailable', 'not available',
                'sold out', 'stock out', 'unavailable'
            ],
            'pre_order': [
                'pre-order', 'preorder', 'pre order', 'coming soon',
                'available soon', 'notify me'
            ],
            'discontinued': [
                'discontinued', 'no longer available', 'product retired'
            ]
        }
        
        # Patterns indicating availability
        self.available_patterns = [
            'add to cart', 'buy now', 'add to bag', 'in stock',
            'available', 'buy this product'
        ]
    
    def check_product_availability(self, product: Dict) -> Dict:
        """
        Check if product is actually available for purchase
        
        Returns:
            {
                'is_available': bool,
                'status': 'in_stock' | 'out_of_stock' | 'pre_order' | 'unknown',
                'checked_source': 'amazon' | 'flipkart' | 'none',
                'confidence': 0-100
            }
        """
        amazon_link = product.get('amazon_link', '')
        flipkart_link = product.get('flipkart_link', '')
        
        # Try Amazon first
        if amazon_link and 'amazon' in amazon_link.lower():
            result = self._check_amazon_availability(amazon_link)
            if result['status'] != 'unknown':
                return result
        
        # Try Flipkart
        if flipkart_link and 'flipkart' in flipkart_link.lower():
            result = self._check_flipkart_availability(flipkart_link)
            if result['status'] != 'unknown':
                return result
        
        # If we have a link but couldn't verify, assume available with low confidence
        if amazon_link or flipkart_link:
            return {
                'is_available': True,
                'status': 'unknown',
                'checked_source': 'none',
                'confidence': 40  # Low confidence
            }
        
        # No links at all - likely mock/fallback product
        return {
            'is_available': False,
            'status': 'no_link',
            'checked_source': 'none',
            'confidence': 100
        }
    
    def _check_amazon_availability(self, url: str) -> Dict:
        """Check Amazon product availability"""
        try:
            headers = {'User-Agent': random.choice(self.user_agents)}
            
            # Quick HEAD request first to check if URL exists
            head_response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
            
            if head_response.status_code == 404:
                return {
                    'is_available': False,
                    'status': 'not_found',
                    'checked_source': 'amazon',
                    'confidence': 100
                }
            
            # If URL exists, do lightweight GET (don't parse full page)
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return {'is_available': False, 'status': 'error', 'checked_source': 'amazon', 'confidence': 80}
            
            # Quick text search (faster than BeautifulSoup)
            page_text = response.text.lower()
            
            # Check for unavailability indicators
            for status_type, patterns in self.unavailable_patterns.items():
                for pattern in patterns:
                    if pattern in page_text:
                        return {
                            'is_available': False,
                            'status': status_type,
                            'checked_source': 'amazon',
                            'confidence': 90
                        }
            
            # Check for availability indicators
            for pattern in self.available_patterns:
                if pattern in page_text:
                    return {
                        'is_available': True,
                        'status': 'in_stock',
                        'checked_source': 'amazon',
                        'confidence': 85
                    }
            
            # Ambiguous - assume available with low confidence
            return {
                'is_available': True,
                'status': 'unknown',
                'checked_source': 'amazon',
                'confidence': 50
            }
            
        except requests.Timeout:
            return {'is_available': True, 'status': 'timeout', 'checked_source': 'amazon', 'confidence': 30}
        except Exception as e:
            print(f"[AVAILABILITY] Amazon check error: {e}")
            return {'is_available': True, 'status': 'error', 'checked_source': 'amazon', 'confidence': 30}
    
    def _check_flipkart_availability(self, url: str) -> Dict:
        """Check Flipkart product availability"""
        try:
            headers = {'User-Agent': random.choice(self.user_agents)}
            
            # Quick HEAD request
            head_response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
            
            if head_response.status_code == 404:
                return {
                    'is_available': False,
                    'status': 'not_found',
                    'checked_source': 'flipkart',
                    'confidence': 100
                }
            
            # Lightweight GET
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return {'is_available': False, 'status': 'error', 'checked_source': 'flipkart', 'confidence': 80}
            
            page_text = response.text.lower()
            
            # Check unavailability
            for status_type, patterns in self.unavailable_patterns.items():
                for pattern in patterns:
                    if pattern in page_text:
                        return {
                            'is_available': False,
                            'status': status_type,
                            'checked_source': 'flipkart',
                            'confidence': 90
                        }
            
            # Check availability
            for pattern in self.available_patterns:
                if pattern in page_text:
                    return {
                        'is_available': True,
                        'status': 'in_stock',
                        'checked_source': 'flipkart',
                        'confidence': 85
                    }
            
            return {
                'is_available': True,
                'status': 'unknown',
                'checked_source': 'flipkart',
                'confidence': 50
            }
            
        except requests.Timeout:
            return {'is_available': True, 'status': 'timeout', 'checked_source': 'flipkart', 'confidence': 30}
        except Exception as e:
            print(f"[AVAILABILITY] Flipkart check error: {e}")
            return {'is_available': True, 'status': 'error', 'checked_source': 'flipkart', 'confidence': 30}
    
    def batch_check_availability(self, products: list, max_checks: int = 5) -> list:
        """
        Check availability for multiple products (with rate limiting)
        
        Args:
            products: List of product dicts
            max_checks: Maximum number of products to actually verify (to avoid rate limiting)
        
        Returns:
            List of products with 'availability_info' added
        """
        enhanced_products = []
        checks_done = 0
        
        for product in products:
            # Skip availability checks for fallback/manual products
            # These are curated products from our database, not live-scraped
            if product.get('source') == 'manual':
                availability_info = {
                    'is_available': True,
                    'status': 'curated',
                    'checked_source': 'fallback_db',
                    'confidence': 100  # High confidence - curated products
                }
                product_copy = product.copy()
                product_copy['availability_info'] = availability_info
                enhanced_products.append(product_copy)
                continue
            
            # Only do deep checks for top products
            if checks_done < max_checks:
                availability_info = self.check_product_availability(product)
                checks_done += 1
                time.sleep(random.uniform(1, 2))  # Rate limiting
            else:
                # For remaining products, do quick link check only
                availability_info = self._quick_link_check(product)
            
            product_copy = product.copy()
            product_copy['availability_info'] = availability_info
            enhanced_products.append(product_copy)
        
        return enhanced_products
    
    def _quick_link_check(self, product: Dict) -> Dict:
        """Quick check if product has valid links (no HTTP request)"""
        amazon_link = product.get('amazon_link', '')
        flipkart_link = product.get('flipkart_link', '')
        
        has_valid_link = (
            (amazon_link and 'amazon' in amazon_link.lower()) or
            (flipkart_link and 'flipkart' in flipkart_link.lower())
        )
        
        if has_valid_link:
            return {
                'is_available': True,
                'status': 'not_checked',
                'checked_source': 'none',
                'confidence': 60  # Moderate confidence
            }
        else:
            return {
                'is_available': False,
                'status': 'no_link',
                'checked_source': 'none',
                'confidence': 100
            }
    
    def filter_unavailable_products(self, products: list) -> list:
        """
        Remove products that are definitely unavailable
        
        Only removes products with high-confidence unavailability
        """
        filtered = []
        
        for product in products:
            availability = product.get('availability_info', {})
            
            # Keep if available OR if we're not confident it's unavailable
            if availability.get('is_available', True) or availability.get('confidence', 0) < 70:
                filtered.append(product)
        
        return filtered
