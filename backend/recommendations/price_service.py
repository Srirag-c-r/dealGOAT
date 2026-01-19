import requests
from bs4 import BeautifulSoup
import time
import json
import threading
from datetime import datetime, timedelta
import random
from urllib.parse import quote


class PriceUpdateService:
    """Service for updating product prices in real-time"""

    def __init__(self):
        self.price_cache = {}
        self.cache_duration = timedelta(hours=6)  # Cache prices for 6 hours
        self.last_update = {}
        self.update_lock = threading.Lock()

    def get_current_price(self, product_name, brand, source='amazon'):
        """Get current price for a product"""
        cache_key = f"{brand}_{product_name}_{source}"

        # Check cache first
        if cache_key in self.price_cache:
            cached_data = self.price_cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < self.cache_duration:
                return cached_data['price'], cached_data['url']

        # Fetch new price
        price, url = self._fetch_price_from_web(product_name, brand, source)

        if price:
            # Cache the result
            self.price_cache[cache_key] = {
                'price': price,
                'url': url,
                'timestamp': datetime.now()
            }

        return price, url

    def _fetch_price_from_web(self, product_name, brand, source='amazon'):
        """Fetch price from web source"""
        try:
            if source == 'amazon':
                return self._fetch_amazon_price(product_name, brand)
            elif source == 'flipkart':
                return self._fetch_flipkart_price(product_name, brand)
            else:
                return None, None
        except Exception as e:
            print(f"Price fetch error for {product_name}: {e}")
            return None, None

    def _fetch_amazon_price(self, product_name, brand):
        """Fetch price from Amazon"""
        try:
            # Create search query
            query = f"{brand} {product_name}"
            search_url = f"https://www.amazon.in/s?k={quote(query)}"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }

            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find first product result
            product_link = soup.find('a', {'class': 'a-link-normal s-no-outline'})
            if product_link:
                product_url = f"https://www.amazon.in{product_link['href']}"

                # Get price from the product page
                product_response = requests.get(product_url, headers=headers, timeout=10)
                product_soup = BeautifulSoup(product_response.content, 'html.parser')

                # Try different price selectors
                price_selectors = [
                    'span.a-price-whole',
                    '.a-price .a-offscreen',
                    '#priceblock_ourprice',
                    '#priceblock_dealprice'
                ]

                for selector in price_selectors:
                    price_elem = product_soup.select_one(selector)
                    if price_elem:
                        price_text = price_elem.get_text().strip()
                        price = self._parse_price_text(price_text)
                        if price:
                            return price, product_url

            return None, search_url

        except Exception as e:
            print(f"Amazon price fetch error: {e}")
            return None, None

    def _fetch_flipkart_price(self, product_name, brand):
        """Fetch price from Flipkart"""
        try:
            query = f"{brand} {product_name}"
            search_url = f"https://www.flipkart.com/search?q={quote(query)}"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find price
            price_elem = soup.select_one('div._30jeq3')
            if price_elem:
                price_text = price_elem.get_text().strip()
                price = self._parse_price_text(price_text)
                return price, search_url

            return None, search_url

        except Exception as e:
            print(f"Flipkart price fetch error: {e}")
            return None, None

    def _parse_price_text(self, price_text):
        """Parse price text into integer"""
        try:
            # Remove currency symbols and commas
            clean_text = price_text.replace('₹', '').replace(',', '').replace('Rs.', '').strip()

            # Extract first number
            import re
            match = re.search(r'\d+', clean_text)
            if match:
                return int(match.group())
        except:
            pass
        return None

    def update_product_prices(self, products):
        """Update prices for a list of products"""
        updated_products = []

        for product in products:
            # Try Amazon first
            price, url = self.get_current_price(
                product['name'],
                product['brand'],
                'amazon'
            )

            if not price:
                # Try Flipkart as fallback
                price, url = self.get_current_price(
                    product['name'],
                    product['brand'],
                    'flipkart'
                )

            if price:
                updated_product = product.copy()
                updated_product['current_price'] = price
                updated_product['price_updated'] = datetime.now().isoformat()
                updated_product['product_url'] = url
                updated_products.append(updated_product)
            else:
                # Keep original price if update fails
                updated_products.append(product)

            # Rate limiting
            time.sleep(random.uniform(1, 3))

        return updated_products

    def get_price_history(self, product_name, brand, days=30):
        """Get price history for a product (placeholder for future implementation)"""
        # This would store price history in a database
        # For now, return mock data
        return {
            'product': f"{brand} {product_name}",
            'current_price': None,
            'price_history': [],
            'lowest_price': None,
            'highest_price': None,
            'average_price': None
        }


class DealFinder:
    """Find deals and discounts"""

    def __init__(self):
        self.price_service = PriceUpdateService()

    def find_deals(self, products, threshold=0.1):
        """Find products with significant price drops"""
        deals = []

        for product in products:
            original_price = product.get('price', 0)
            current_price, _ = self.price_service.get_current_price(
                product['name'],
                product['brand']
            )

            if current_price and current_price < original_price:
                discount_percent = (original_price - current_price) / original_price

                if discount_percent >= threshold:
                    deal_info = {
                        'product': product,
                        'original_price': original_price,
                        'current_price': current_price,
                        'discount_percent': discount_percent,
                        'savings': original_price - current_price,
                        'deal_type': 'price_drop'
                    }
                    deals.append(deal_info)

        return sorted(deals, key=lambda x: x['discount_percent'], reverse=True)

    def get_seasonal_deals(self, category='laptop'):
        """Get seasonal deals for a category"""
        # This would check for seasonal promotions
        # For now, return mock deals
        mock_deals = [
            {
                'title': 'Back to School Sale',
                'discount': 'Up to 20% off',
                'category': category,
                'valid_until': (datetime.now() + timedelta(days=30)).isoformat()
            },
            {
                'title': 'Gaming Laptop Festival',
                'discount': '₹5000-10000 off',
                'category': category,
                'valid_until': (datetime.now() + timedelta(days=15)).isoformat()
            }
        ]
        return mock_deals


class InventoryChecker:
    """Check product availability"""

    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(hours=1)

    def check_availability(self, product_name, brand):
        """Check if product is in stock"""
        cache_key = f"{brand}_{product_name}"

        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < self.cache_duration:
                return cached_data['available']

        # Mock availability check
        # In production, this would scrape actual inventory
        available = random.choice([True, True, True, False])  # 75% available

        self.cache[cache_key] = {
            'available': available,
            'timestamp': datetime.now()
        }

        return available

    def get_delivery_info(self, product_name, brand, pincode='110001'):
        """Get delivery information"""
        # Mock delivery info
        if self.check_availability(product_name, brand):
            return {
                'available': True,
                'delivery_date': (datetime.now() + timedelta(days=random.randint(2, 7))).strftime('%Y-%m-%d'),
                'delivery_charges': random.choice([0, 40, 60, 80]),
                'fast_delivery': random.choice([True, False])
            }
        else:
            return {
                'available': False,
                'message': 'Currently out of stock'
            }