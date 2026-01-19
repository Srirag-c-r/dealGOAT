"""
Dynamic Product Manager - Handles new product launches, price updates, and discounts

This module provides:
1. Real-time price updates from Amazon/Flipkart
2. New product detection
3. Price change tracking
4. Discount alerts
5. Background update scheduler
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import threading
from datetime import datetime, timedelta
from urllib.parse import quote
import random
from typing import Dict, List, Optional, Tuple


class DynamicProductManager:
    """Manages dynamic product discovery and price updates"""
    
    def __init__(self):
        self.price_cache = {}
        self.product_cache = {}
        self.price_history = {}  # Track price changes
        self.new_products = []  # Track newly discovered products
        self.cache_duration = timedelta(hours=6)  # Cache prices for 6 hours
        self.product_cache_duration = timedelta(days=7)  # Cache product data for 7 days
        self.update_lock = threading.Lock()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
    
    def get_headers(self):
        """Get random headers to avoid detection"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def fetch_live_price(self, product_name: str, brand: str, source: str = 'amazon') -> Tuple[Optional[int], Optional[str]]:
        """
        Fetch live price from Amazon or Flipkart
        
        Returns:
            (price, url) or (None, None) if failed
        """
        cache_key = f"{brand}_{product_name}_{source}"
        
        # Check cache first
        if cache_key in self.price_cache:
            cached = self.price_cache[cache_key]
            if datetime.now() - cached['timestamp'] < self.cache_duration:
                return cached['price'], cached['url']
        
        try:
            if source == 'amazon':
                price, url = self._fetch_amazon_price(product_name, brand)
            elif source == 'flipkart':
                price, url = self._fetch_flipkart_price(product_name, brand)
            else:
                return None, None
            
            # Cache the result
            if price:
                self.price_cache[cache_key] = {
                    'price': price,
                    'url': url,
                    'timestamp': datetime.now()
                }
                
                # Track price history
                self._track_price_change(brand, product_name, price, source)
            
            return price, url
            
        except Exception as e:
            print(f"[PRICE UPDATE] Error fetching price for {product_name}: {e}")
            return None, None
    
    def _fetch_amazon_price(self, product_name: str, brand: str) -> Tuple[Optional[int], Optional[str]]:
        """Fetch price from Amazon.in"""
        try:
            # Build search query
            query = f"{brand} {product_name}"
            search_url = f"https://www.amazon.in/s?k={quote(query)}"
            
            response = requests.get(search_url, headers=self.get_headers(), timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors for price
            price_selectors = [
                '.a-price .a-offscreen',
                '.a-price-whole',
                '.a-color-price',
                '[data-cy="price-recipe"] span'
            ]
            
            for selector in price_selectors:
                price_elem = soup.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price = self._parse_price(price_text)
                    if price:
                        # Get product link
                        link_elem = soup.select_one('h2 a[href*="/dp/"]')
                        link = link_elem['href'] if link_elem else search_url
                        if not link.startswith('http'):
                            link = 'https://www.amazon.in' + link
                        
                        return price, link
            
            return None, None
            
        except Exception as e:
            print(f"[AMAZON] Price fetch error: {e}")
            return None, None
    
    def _fetch_flipkart_price(self, product_name: str, brand: str) -> Tuple[Optional[int], Optional[str]]:
        """Fetch price from Flipkart.com"""
        try:
            query = f"{brand} {product_name}"
            search_url = f"https://www.flipkart.com/search?q={quote(query)}"
            
            response = requests.get(search_url, headers=self.get_headers(), timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors
            price_selectors = [
                'div[data-cy="price-recipe"]',
                'div._30jeq3',
                'div._16Jk6d'
            ]
            
            for selector in price_selectors:
                price_elem = soup.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price = self._parse_price(price_text)
                    if price:
                        # Get product link
                        link_elem = soup.select_one('a[data-cy="title-recipe"]')
                        link = link_elem['href'] if link_elem else search_url
                        if not link.startswith('http'):
                            link = 'https://www.flipkart.com' + link
                        
                        return price, link
            
            return None, None
            
        except Exception as e:
            print(f"[FLIPKART] Price fetch error: {e}")
            return None, None
    
    def _parse_price(self, price_text: str) -> Optional[int]:
        """Parse price text to integer"""
        try:
            # Remove currency symbols and commas
            price_text = price_text.replace('₹', '').replace(',', '').replace('.00', '').strip()
            # Extract first number
            import re
            match = re.search(r'(\d+)', price_text)
            if match:
                return int(match.group(1))
        except:
            pass
        return None
    
    def _track_price_change(self, brand: str, product_name: str, new_price: int, source: str):
        """Track price changes and detect discounts"""
        key = f"{brand}_{product_name}"
        
        if key not in self.price_history:
            self.price_history[key] = {
                'prices': [],
                'sources': {},
                'last_updated': datetime.now()
            }
        
        history = self.price_history[key]
        
        # Add new price
        history['prices'].append({
            'price': new_price,
            'source': source,
            'timestamp': datetime.now()
        })
        
        # Keep only last 30 days
        cutoff = datetime.now() - timedelta(days=30)
        history['prices'] = [p for p in history['prices'] if p['timestamp'] > cutoff]
        
        # Update source price
        history['sources'][source] = {
            'price': new_price,
            'timestamp': datetime.now()
        }
        
        history['last_updated'] = datetime.now()
    
    def detect_discount(self, brand: str, product_name: str, current_price: int) -> Dict:
        """
        Detect if product is on discount
        
        Returns:
            {
                'is_discount': bool,
                'discount_percent': float,
                'original_price': int,
                'savings': int
            }
        """
        key = f"{brand}_{product_name}"
        
        if key not in self.price_history or len(self.price_history[key]['prices']) < 2:
            return {
                'is_discount': False,
                'discount_percent': 0,
                'original_price': current_price,
                'savings': 0
            }
        
        prices = [p['price'] for p in self.price_history[key]['prices']]
        if not prices:
            return {
                'is_discount': False,
                'discount_percent': 0,
                'original_price': current_price,
                'savings': 0
            }
        
        # Get average price (excluding current)
        recent_prices = prices[:-1] if len(prices) > 1 else prices
        avg_price = sum(recent_prices) / len(recent_prices) if recent_prices else current_price
        
        # Consider it a discount if current price is 5%+ lower than average
        if current_price < avg_price * 0.95:
            discount_percent = ((avg_price - current_price) / avg_price) * 100
            return {
                'is_discount': True,
                'discount_percent': round(discount_percent, 1),
                'original_price': int(avg_price),
                'savings': int(avg_price - current_price)
            }
        
        return {
            'is_discount': False,
            'discount_percent': 0,
            'original_price': current_price,
            'savings': 0
        }
    
    def discover_new_products(self, search_query: str, device_type: str = 'laptop', limit: int = 10) -> List[Dict]:
        """
        Discover new products by searching Amazon/Flipkart
        
        Returns list of newly discovered products
        """
        new_products = []
        
        try:
            # Search Amazon
            amazon_products = self._search_amazon_products(search_query, limit)
            new_products.extend(amazon_products)
            
            time.sleep(1)  # Rate limiting
            
            # Search Flipkart
            flipkart_products = self._search_flipkart_products(search_query, limit)
            new_products.extend(flipkart_products)
            
            # Remove duplicates
            seen = set()
            unique_products = []
            for product in new_products:
                key = f"{product.get('brand', '')}_{product.get('name', '')}"
                if key not in seen:
                    seen.add(key)
                    unique_products.append(product)
            
            return unique_products[:limit]
            
        except Exception as e:
            print(f"[DISCOVERY] Error discovering products: {e}")
            return []
    
    def _search_amazon_products(self, query: str, limit: int = 10) -> List[Dict]:
        """Search Amazon for products"""
        try:
            search_url = f"https://www.amazon.in/s?k={quote(query)}"
            response = requests.get(search_url, headers=self.get_headers(), timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Find product containers
            containers = soup.select('div[data-component-type="s-search-result"]')[:limit]
            
            for container in containers:
                try:
                    # Extract product name
                    name_elem = container.select_one('h2 a span')
                    if not name_elem:
                        continue
                    name = name_elem.get_text(strip=True)
                    
                    # Extract brand (first word usually)
                    brand = name.split()[0] if name else "Unknown"
                    
                    # Extract price
                    price_elem = container.select_one('.a-price .a-offscreen')
                    price = 0
                    if price_elem:
                        price = self._parse_price(price_elem.get_text(strip=True)) or 0
                    
                    # Extract link
                    link_elem = container.select_one('h2 a')
                    link = link_elem['href'] if link_elem else ''
                    if link and not link.startswith('http'):
                        link = 'https://www.amazon.in' + link
                    
                    # Extract rating
                    rating = 0
                    rating_elem = container.select_one('.a-icon-star-small .a-icon-alt')
                    if rating_elem:
                        try:
                            rating_text = rating_elem.get_text(strip=True)
                            rating = float(rating_text.split()[0])
                        except:
                            pass
                    
                    if name and price > 0:
                        products.append({
                            'name': name,
                            'brand': brand,
                            'price': price,
                            'amazon_link': link,
                            'rating': rating,
                            'source': 'amazon',
                            'discovered_at': datetime.now().isoformat()
                        })
                except Exception as e:
                    print(f"[AMAZON] Error extracting product: {e}")
                    continue
            
            return products
            
        except Exception as e:
            print(f"[AMAZON] Search error: {e}")
            return []
    
    def _search_flipkart_products(self, query: str, limit: int = 10) -> List[Dict]:
        """Search Flipkart for products"""
        try:
            search_url = f"https://www.flipkart.com/search?q={quote(query)}"
            response = requests.get(search_url, headers=self.get_headers(), timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Find product containers
            containers = soup.find_all('div', {'data-id': True})[:limit]
            
            for container in containers:
                try:
                    # Extract product name
                    name_elem = container.select_one('a[data-cy="title-recipe"]') or container.select_one('div._4rR01T')
                    if not name_elem:
                        continue
                    name = name_elem.get_text(strip=True)
                    
                    # Extract brand
                    brand = name.split()[0] if name else "Unknown"
                    
                    # Extract price
                    price_elem = container.select_one('div[data-cy="price-recipe"]') or container.select_one('div._30jeq3')
                    price = 0
                    if price_elem:
                        price = self._parse_price(price_elem.get_text(strip=True)) or 0
                    
                    # Extract link
                    link_elem = container.select_one('a[data-cy="title-recipe"]')
                    link = link_elem['href'] if link_elem else ''
                    if link and not link.startswith('http'):
                        link = 'https://www.flipkart.com' + link
                    
                    # Extract rating
                    rating = 0
                    rating_elem = container.select_one('div._3LWZlK')
                    if rating_elem:
                        try:
                            rating_text = rating_elem.get_text(strip=True)
                            rating = float(rating_text.split()[0])
                        except:
                            pass
                    
                    if name and price > 0:
                        products.append({
                            'name': name,
                            'brand': brand,
                            'price': price,
                            'flipkart_link': link,
                            'rating': rating,
                            'source': 'flipkart',
                            'discovered_at': datetime.now().isoformat()
                        })
                except Exception as e:
                    print(f"[FLIPKART] Error extracting product: {e}")
                    continue
            
            return products
            
        except Exception as e:
            print(f"[FLIPKART] Search error: {e}")
            return []
    
    def update_product_with_live_data(self, product: Dict) -> Dict:
        """
        Update a product with live price and discount info
        
        Args:
            product: Product dict with name, brand, price, etc.
        
        Returns:
            Updated product dict with live_price, discount_info, etc.
        """
        updated_product = product.copy()
        brand = product.get('brand', '')
        name = product.get('name', '')
        
        # Try to get live price from Amazon
        live_price, amazon_url = self.fetch_live_price(name, brand, 'amazon')
        
        if not live_price:
            # Try Flipkart
            live_price, flipkart_url = self.fetch_live_price(name, brand, 'flipkart')
            if flipkart_url:
                updated_product['flipkart_link'] = flipkart_url
        
        if live_price:
            updated_product['live_price'] = live_price
            updated_product['price_updated_at'] = datetime.now().isoformat()
            
            # Update links if we got new URLs
            if amazon_url:
                updated_product['amazon_link'] = amazon_url
            
            # Check for discount
            discount_info = self.detect_discount(brand, name, live_price)
            updated_product['discount_info'] = discount_info
            
            # Use live price if available
            if live_price != product.get('price', 0):
                updated_product['original_price'] = product.get('price', live_price)
                updated_product['price'] = live_price
                updated_product['price_changed'] = True
        else:
            # Keep original price
            updated_product['live_price'] = product.get('price', 0)
            updated_product['price_updated_at'] = None
            updated_product['discount_info'] = {
                'is_discount': False,
                'discount_percent': 0,
                'original_price': product.get('price', 0),
                'savings': 0
            }
        
        return updated_product
    
    def update_multiple_products(self, products: List[Dict], max_workers: int = 3) -> List[Dict]:
        """
        Update multiple products with live prices (with rate limiting)
        
        Args:
            products: List of product dicts
            max_workers: Number of concurrent updates (keep low to avoid rate limiting)
        
        Returns:
            List of updated products
        """
        updated_products = []
        
        for i, product in enumerate(products):
            try:
                updated = self.update_product_with_live_data(product)
                updated_products.append(updated)
                
                # Rate limiting - wait between requests
                if i < len(products) - 1:  # Don't wait after last product
                    time.sleep(random.uniform(2, 4))  # 2-4 seconds between requests
                    
            except Exception as e:
                print(f"[UPDATE] Error updating product {product.get('name', 'Unknown')}: {e}")
                # Add original product if update fails
                updated_products.append(product)
        
        return updated_products


class ProductDiscoveryService:
    """Service for discovering new products based on search queries"""
    
    def __init__(self):
        self.manager = DynamicProductManager()
        self.discovered_products_cache = {}
    
    def discover_for_query(self, search_queries: List[str], device_type: str = 'laptop') -> List[Dict]:
        """
        Discover new products for given search queries
        
        Args:
            search_queries: List of search query strings
            device_type: Type of device (laptop/phone)
        
        Returns:
            List of newly discovered products
        """
        all_discovered = []
        
        for query in search_queries[:3]:  # Limit to 3 queries to avoid rate limiting
            try:
                products = self.manager.discover_new_products(query, device_type, limit=5)
                all_discovered.extend(products)
                time.sleep(2)  # Rate limiting between queries
            except Exception as e:
                print(f"[DISCOVERY] Error discovering for query '{query}': {e}")
                continue
        
        # Remove duplicates
        seen = set()
        unique_products = []
        for product in all_discovered:
            key = f"{product.get('brand', '')}_{product.get('name', '')}"
            if key not in seen:
                seen.add(key)
                unique_products.append(product)
        
        return unique_products[:10]  # Return top 10 unique products

