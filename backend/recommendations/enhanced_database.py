import os
import json
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote
from datetime import datetime, timedelta
import threading
import pickle


class EnhancedProductDatabase:
    """Enhanced product database with caching and real-time updates"""

    def __init__(self):
        self.cache_file = 'product_cache.pkl'
        self.cache_duration = timedelta(hours=24)  # Cache for 24 hours
        self.product_database = self.load_or_create_database()
        self.lock = threading.Lock()

    def load_or_create_database(self):
        """Load cached database or create new one"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    if datetime.now() - cache_data['timestamp'] < self.cache_duration:
                        print("Loading products from cache...")
                        return cache_data['database']
            except Exception as e:
                print(f"Cache load failed: {e}")

        print("Creating fresh product database...")
        return self.create_enhanced_database()

    def save_cache(self):
        """Save database to cache"""
        try:
            cache_data = {
                'timestamp': datetime.now(),
                'database': self.product_database
            }
            with open(self.cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
        except Exception as e:
            print(f"Cache save failed: {e}")

    def create_enhanced_database(self):
        """Create comprehensive product database"""
        return {
            'laptop': [
                # Budget Laptops (under 50k)
                {'name': 'Lenovo IdeaPad 1 AMD Ryzen 3', 'brand': 'Lenovo', 'price': 32999, 'rating': 3.9, 'reviews_count': 156, 'specs': 'AMD Ryzen 3, 8GB RAM, 256GB SSD, 15.6" HD display, laptop, budget'},
                {'name': 'ASUS VivoBook Go 14 Intel Celeron', 'brand': 'ASUS', 'price': 28999, 'rating': 3.7, 'reviews_count': 98, 'specs': 'Intel Celeron, 4GB RAM, 128GB SSD, 14" HD display, laptop, budget'},
                {'name': 'HP 15s Intel Core i3', 'brand': 'HP', 'price': 38999, 'rating': 3.9, 'reviews_count': 234, 'specs': 'Intel Core i3, 8GB RAM, 512GB SSD, 15.6" FHD display, laptop, budget'},
                {'name': 'Dell Inspiron 15 3000 i3', 'brand': 'Dell', 'price': 35999, 'rating': 3.8, 'reviews_count': 187, 'specs': 'Intel Core i3, 8GB RAM, 256GB SSD, 15.6" HD display, laptop, budget'},
                {'name': 'Acer Aspire 3 Intel Core i3', 'brand': 'Acer', 'price': 31999, 'rating': 3.6, 'reviews_count': 145, 'specs': 'Intel Core i3, 4GB RAM, 256GB SSD, 15.6" HD display, laptop, budget'},

                # Mid-Range Laptops (50k-80k)
                {'name': 'ASUS VivoBook 15 Intel Core i5 12th Gen', 'brand': 'ASUS', 'price': 65999, 'rating': 4.2, 'reviews_count': 245, 'specs': 'Intel Core i5 12th Gen, 8GB RAM, 512GB SSD, 15.6" FHD display, laptop, notebook'},
                {'name': 'Lenovo IdeaPad 3 Intel Core i7 12th Gen', 'brand': 'Lenovo', 'price': 72500, 'rating': 4.3, 'reviews_count': 189, 'specs': 'Intel Core i7 12th Gen, 8GB RAM, 512GB SSD, 15.6" FHD display, laptop'},
                {'name': 'HP Pavilion 15 Intel Core i5', 'brand': 'HP', 'price': 66999, 'rating': 4.0, 'reviews_count': 267, 'specs': 'Intel Core i5, 8GB RAM, 512GB SSD, 15.6" FHD, Windows 11, laptop'},
                {'name': 'Dell Inspiron 15 5000 Series i5', 'brand': 'Dell', 'price': 68500, 'rating': 4.4, 'reviews_count': 278, 'specs': 'Intel Core i5, 8GB RAM, 512GB SSD, 15.6" FHD display, laptop'},
                {'name': 'Acer Aspire 5 Intel Core i5', 'brand': 'Acer', 'price': 57999, 'rating': 4.1, 'reviews_count': 198, 'specs': 'Intel Core i5, 8GB RAM, 512GB SSD, 15.6" FHD display, laptop'},

                # Gaming Laptops (70k-120k)
                {'name': 'HP Pavilion 15 Gaming Laptop RTX 3050', 'brand': 'HP', 'price': 78999, 'rating': 4.1, 'reviews_count': 312, 'specs': 'Intel Core i7, 16GB RAM, 512GB SSD, NVIDIA RTX 3050, 15.6" FHD, laptop, gaming'},
                {'name': 'Acer Nitro 5 Gaming Laptop RTX 4050', 'brand': 'Acer', 'price': 79999, 'rating': 4.5, 'reviews_count': 421, 'specs': 'Intel Core i7, 16GB RAM, 512GB SSD, NVIDIA RTX 4050, 15.6" gaming display, laptop'},
                {'name': 'MSI GF63 Thin 12th Gen Gaming Laptop', 'brand': 'MSI', 'price': 74999, 'rating': 4.0, 'reviews_count': 156, 'specs': 'Intel Core i7, 16GB RAM, 512GB SSD, NVIDIA RTX 3050, 15.6" IPS, laptop, gaming'},
                {'name': 'ASUS TUF Gaming F15 12th Gen', 'brand': 'ASUS', 'price': 82500, 'rating': 4.6, 'reviews_count': 389, 'specs': 'Intel Core i7, 16GB RAM, 1TB SSD, NVIDIA RTX 4060, 15.6" FHD, laptop, gaming'},
                {'name': 'Lenovo Legion 5 Gaming Laptop', 'brand': 'Lenovo', 'price': 94999, 'rating': 4.7, 'reviews_count': 412, 'specs': 'Intel Core i7, 16GB RAM, 1TB SSD, NVIDIA RTX 4070, 15.6" FHD display, laptop, gaming'},
                {'name': 'HP Omen 16 Gaming Laptop', 'brand': 'HP', 'price': 119999, 'rating': 4.4, 'reviews_count': 345, 'specs': 'Intel Core i7, 16GB RAM, 1TB SSD, NVIDIA RTX 4060, 16.1" FHD, laptop, gaming'},
                {'name': 'Acer Predator Helios 300', 'brand': 'Acer', 'price': 109999, 'rating': 4.3, 'reviews_count': 412, 'specs': 'Intel Core i7, 16GB RAM, 512GB SSD, NVIDIA RTX 4060, 15.6" FHD, laptop, gaming'},

                # Productivity Laptops (AMD Ryzen)
                {'name': 'ASUS VivoBook 15 AMD Ryzen 7 5700U', 'brand': 'ASUS', 'price': 89999, 'rating': 4.4, 'reviews_count': 356, 'specs': 'AMD Ryzen 7 5700U, 16GB RAM, 512GB SSD, 15.6" FHD display, laptop'},
                {'name': 'Lenovo IdeaPad 5 Pro Ryzen 7 5700U', 'brand': 'Lenovo', 'price': 85999, 'rating': 4.5, 'reviews_count': 423, 'specs': 'AMD Ryzen 7 5700U, 16GB RAM, 512GB SSD, 15.6" IPS display, laptop'},
                {'name': 'HP Pavilion Gaming 15 Ryzen 7', 'brand': 'HP', 'price': 88999, 'rating': 4.3, 'reviews_count': 289, 'specs': 'AMD Ryzen 7, 16GB RAM, 512GB SSD, NVIDIA RTX 3050 Ti, 15.6" display, laptop'},
                {'name': 'Dell G15 Gaming Ryzen 7 RTX 4060', 'brand': 'Dell', 'price': 87999, 'rating': 4.4, 'reviews_count': 334, 'specs': 'AMD Ryzen 7, 16GB RAM, 512GB SSD, NVIDIA RTX 4060, 15.6" FHD, laptop'},

                # Premium & Ultrabook Laptops (100k+)
                {'name': 'ASUS ROG Zephyrus G15 RTX 4080', 'brand': 'ASUS', 'price': 189999, 'rating': 4.8, 'reviews_count': 267, 'specs': 'Intel Core i9, 32GB RAM, 1TB SSD, NVIDIA RTX 4080, 15.6" 240Hz, laptop, gaming'},
                {'name': 'Alienware x15 R2 Gaming Laptop', 'brand': 'Dell', 'price': 179999, 'rating': 4.9, 'reviews_count': 189, 'specs': 'Intel Core i9, 32GB RAM, 1TB SSD, NVIDIA RTX 4090, 15.6" 360Hz, laptop, gaming'},
                {'name': 'ASUS Zephyrus G14 Ultra Gaming', 'brand': 'ASUS', 'price': 134999, 'rating': 4.7, 'reviews_count': 298, 'specs': 'Intel Core i9, 16GB RAM, 1TB SSD, NVIDIA RTX 4070, 14" FHD, ultrabook, laptop'},
                {'name': 'MacBook Air M2 256GB', 'brand': 'Apple', 'price': 99999, 'rating': 4.8, 'reviews_count': 512, 'specs': 'Apple M2, 8GB RAM, 256GB SSD, 13.6" Retina display, ultrabook, laptop'},
                {'name': 'ASUS Zenbook 14 OLED', 'brand': 'ASUS', 'price': 89999, 'rating': 4.6, 'reviews_count': 456, 'specs': 'Intel Core i7, 16GB RAM, 512GB SSD, 14" OLED display, ultrabook, laptop'},
                {'name': 'Dell XPS 13 Plus', 'brand': 'Dell', 'price': 99999, 'rating': 4.7, 'reviews_count': 567, 'specs': 'Intel Core i7, 16GB RAM, 512GB SSD, 13.3" FHD display, ultrabook, laptop'},
                {'name': 'Lenovo ThinkPad X1 Carbon', 'brand': 'Lenovo', 'price': 94999, 'rating': 4.5, 'reviews_count': 345, 'specs': 'Intel Core i7, 16GB RAM, 512GB SSD, 14" FHD display, ultrabook, laptop'},
                {'name': 'Dell XPS 15 OLED', 'brand': 'Dell', 'price': 149999, 'rating': 4.6, 'reviews_count': 387, 'specs': 'Intel Core i7, 16GB RAM, 512GB SSD, 15.6" OLED display, laptop, productivity'},
                {'name': 'ASUS ProArt StudioBook 16 OLED', 'brand': 'ASUS', 'price': 159999, 'rating': 4.7, 'reviews_count': 298, 'specs': 'Intel Core i7, 32GB RAM, 1TB SSD, 16" OLED display, laptop, creative'},
                {'name': 'Lenovo ThinkPad P16 Gen 1', 'brand': 'Lenovo', 'price': 169999, 'rating': 4.5, 'reviews_count': 234, 'specs': 'Intel Core i7, 32GB RAM, 1TB SSD, 16" display, laptop, workstation'},
            ],
            'phone': [
                # Budget Phones (under 15k)
                {'name': 'Samsung Galaxy A13 64GB', 'brand': 'Samsung', 'price': 15999, 'rating': 3.8, 'reviews_count': 1203, 'specs': '6.6" FHD, 5000mAh, 13MP camera, smartphone'},
                {'name': 'Realme 10 128GB', 'brand': 'Realme', 'price': 16999, 'rating': 4.1, 'reviews_count': 945, 'specs': '6.4" AMOLED, 5000mAh, 50MP smartphone'},
                {'name': 'Samsung Galaxy M14 64GB', 'brand': 'Samsung', 'price': 14999, 'rating': 4.0, 'reviews_count': 834, 'specs': '6.5" IPS, 5000mAh, 50MP, 5G mobile'},
                {'name': 'Nokia G42 5G', 'brand': 'Nokia', 'price': 13999, 'rating': 3.9, 'reviews_count': 567, 'specs': '6.5" IPS, 5000mAh, 50MP, 5G phone'},
                {'name': 'Motorola Moto G62 5G', 'brand': 'Motorola', 'price': 15999, 'rating': 4.0, 'reviews_count': 723, 'specs': '6.5" IPS, 5000mAh, 50MP, 5G smartphone'},

                # Mid-Range Phones (15k-30k)
                {'name': 'Xiaomi Redmi Note 12 128GB', 'brand': 'Xiaomi', 'price': 18999, 'rating': 4.3, 'reviews_count': 2134, 'specs': '6.7" AMOLED, 5000mAh, 48MP, 5G phone'},
                {'name': 'OnePlus Nord CE 3 Lite 5G', 'brand': 'OnePlus', 'price': 21999, 'rating': 4.2, 'reviews_count': 1567, 'specs': '6.7" IPS, 5000mAh, 108MP, 5G smartphone'},
                {'name': 'Samsung Galaxy A54 128GB', 'brand': 'Samsung', 'price': 43999, 'rating': 4.3, 'reviews_count': 1267, 'specs': '6.4" AMOLED, 5000mAh, 50MP, 5G mobile'},
                {'name': 'Poco X4 Pro 5G', 'brand': 'Poco', 'price': 32999, 'rating': 4.2, 'reviews_count': 678, 'specs': '6.6" AMOLED, 5000mAh, 108MP, 5G, 120Hz display'},
                {'name': 'Motorola Edge 40 Pro 256GB', 'brand': 'Motorola', 'price': 39999, 'rating': 4.4, 'reviews_count': 523, 'specs': '6.7" AMOLED, 4500mAh, 50MP, 5G phone'},
                {'name': 'Realme 11 Pro+ 5G', 'brand': 'Realme', 'price': 29999, 'rating': 4.3, 'reviews_count': 892, 'specs': '6.7" AMOLED, 5000mAh, 200MP, 5G smartphone'},
                {'name': 'Infinix Zero 30 5G', 'brand': 'Infinix', 'price': 24999, 'rating': 4.1, 'reviews_count': 445, 'specs': '6.8" IPS, 5000mAh, 108MP, 5G phone'},
                {'name': 'Tecno Camon 20 Pro 5G', 'brand': 'Tecno', 'price': 19999, 'rating': 4.0, 'reviews_count': 334, 'specs': '6.7" AMOLED, 5000mAh, 64MP, 5G smartphone'},

                # Premium Phones (30k-60k)
                {'name': 'Apple iPhone SE (2022) 128GB', 'brand': 'Apple', 'price': 39999, 'rating': 4.5, 'reviews_count': 2876, 'specs': '4.7" Retina, 2018mAh, 12MP, 5G, compact, video recording, long-term updates, smooth performance'},
                {'name': 'Apple iPhone 12 128GB', 'brand': 'Apple', 'price': 45999, 'rating': 4.6, 'reviews_count': 4123, 'specs': '6.1" Super Retina, 2815mAh, 12MP, 5G, clean UI, video recording, long-term updates'},
                {'name': 'OnePlus 11 5G 256GB', 'brand': 'OnePlus', 'price': 42999, 'rating': 4.5, 'reviews_count': 876, 'specs': '6.7" AMOLED, 5000mAh, 108MP, 5G mobile, clean UI'},
                {'name': 'Apple iPhone 13 128GB', 'brand': 'Apple', 'price': 52999, 'rating': 4.7, 'reviews_count': 3456, 'specs': '6.1" Super Retina, 3240mAh, 12MP, 5G, clean UI, video recording, long-term updates'},
                {'name': 'Samsung Galaxy S23 256GB', 'brand': 'Samsung', 'price': 74999, 'rating': 4.6, 'reviews_count': 1823, 'specs': '6.1" AMOLED, 4000mAh, 50MP, 5G, compact design'},
                {'name': 'Apple iPhone 14 128GB', 'brand': 'Apple', 'price': 64999, 'rating': 4.6, 'reviews_count': 3421, 'specs': '6.1" Super Retina, 3240mAh, 12MP, 5G, clean UI'},
                {'name': 'Google Pixel 7a', 'brand': 'Google', 'price': 43999, 'rating': 4.4, 'reviews_count': 1234, 'specs': '6.1" OLED, 4385mAh, 64MP, 5G, clean Android'},
                {'name': 'Nothing Phone 2', 'brand': 'Nothing', 'price': 44999, 'rating': 4.3, 'reviews_count': 987, 'specs': '6.7" AMOLED, 4700mAh, 50MP, 5G, unique design'},
                {'name': 'Asus Zenfone 10', 'brand': 'ASUS', 'price': 54999, 'rating': 4.4, 'reviews_count': 456, 'specs': '5.9" AMOLED, 4300mAh, 50MP, 5G, compact flagship'},

                # Compact Phones (under 6.5 inch)
                {'name': 'iPhone 13 Mini 256GB', 'brand': 'Apple', 'price': 72999, 'rating': 4.7, 'reviews_count': 2134, 'specs': '5.4" OLED, 3240mAh, 12MP, compact phone, clean UI'},
                {'name': 'Samsung Galaxy S23 256GB', 'brand': 'Samsung', 'price': 74999, 'rating': 4.6, 'reviews_count': 1823, 'specs': '6.1" AMOLED, 4000mAh, 50MP, 5G, compact design'},
                {'name': 'Apple iPhone 14 128GB', 'brand': 'Apple', 'price': 64999, 'rating': 4.6, 'reviews_count': 3421, 'specs': '6.1" Super Retina, 3240mAh, 12MP, 5G, clean UI'},
                {'name': 'Google Pixel 7', 'brand': 'Google', 'price': 59999, 'rating': 4.5, 'reviews_count': 1567, 'specs': '6.3" OLED, 4270mAh, 50MP, 5G, clean Android'},
                {'name': 'Sony Xperia 5 IV', 'brand': 'Sony', 'price': 79999, 'rating': 4.3, 'reviews_count': 345, 'specs': '6.1" OLED, 5000mAh, 12MP, 5G, camera focused'},

                # Gaming Phones
                {'name': 'OnePlus 11 Pro 512GB', 'brand': 'OnePlus', 'price': 54999, 'rating': 4.7, 'reviews_count': 1245, 'specs': '6.7" AMOLED, 5000mAh, 108MP, 5G, gaming performance, 120Hz'},
                {'name': 'Samsung Galaxy S23 Ultra 512GB', 'brand': 'Samsung', 'price': 124999, 'rating': 4.7, 'reviews_count': 2189, 'specs': '6.8" AMOLED, 5000mAh, 200MP, 5G, gaming phone, 120Hz'},
                {'name': 'ROG Phone 6 Pro 512GB', 'brand': 'ASUS', 'price': 89999, 'rating': 4.8, 'reviews_count': 567, 'specs': '6.78" AMOLED, 6000mAh, 50MP, 5G, gaming, 165Hz, cooling'},
                {'name': 'Xiaomi Poco F4 GT', 'brand': 'Poco', 'price': 49999, 'rating': 4.4, 'reviews_count': 834, 'specs': '6.67" AMOLED, 4700mAh, 64MP, 5G, gaming, 120Hz'},
                {'name': 'Red Magic 8 Pro', 'brand': 'Red Magic', 'price': 59999, 'rating': 4.5, 'reviews_count': 678, 'specs': '6.8" AMOLED, 6000mAh, 50MP, gaming, 165Hz, shoulder triggers'},
                {'name': 'Nubia Red Magic 8', 'brand': 'Nubia', 'price': 47999, 'rating': 4.3, 'reviews_count': 456, 'specs': '6.8" AMOLED, 6500mAh, 64MP, gaming, 165Hz, cooling'},
            ],
            'tablet': [
                {'name': 'Samsung Galaxy Tab S9', 'brand': 'Samsung', 'price': 75999, 'rating': 4.5, 'reviews_count': 234, 'specs': '11" AMOLED, 8GB RAM, 128GB, S Pen, Android tablet'},
                {'name': 'Apple iPad Pro 12.9"', 'brand': 'Apple', 'price': 119999, 'rating': 4.8, 'reviews_count': 456, 'specs': '12.9" Liquid Retina, 8GB RAM, 128GB, M2 chip, iPadOS'},
                {'name': 'Lenovo Tab P12 Pro', 'brand': 'Lenovo', 'price': 64999, 'rating': 4.3, 'reviews_count': 189, 'specs': '12.6" IPS, 8GB RAM, 256GB, Android tablet'},
                {'name': 'Microsoft Surface Pro 9', 'brand': 'Microsoft', 'price': 129999, 'rating': 4.6, 'reviews_count': 345, 'specs': '13" PixelSense, 8GB RAM, 256GB, Intel i5, Windows tablet'},
                {'name': 'Amazon Fire HD 10', 'brand': 'Amazon', 'price': 14999, 'rating': 4.0, 'reviews_count': 1234, 'specs': '10.1" IPS, 3GB RAM, 32GB, Fire OS, budget tablet'},
            ]
        }

    def update_prices_from_web(self):
        """Update prices from web sources (to be implemented)"""
        # This would scrape current prices from Amazon/Flipkart
        # For now, we'll keep the static database
        pass

    def get_products_by_category(self, category, filters=None):
        """Get products by category with optional filters"""
        products = self.product_database.get(category, [])

        if filters:
            filtered = []
            for product in products:
                match = True
                if 'budget_max' in filters and product['price'] > filters['budget_max']:
                    match = False
                if 'brand' in filters and product['brand'].lower() != filters['brand'].lower():
                    match = False
                if match:
                    filtered.append(product)
            return filtered

        return products

    def search_similar_products(self, query, category='laptop', limit=10):
        """Search for products similar to query"""
        products = self.product_database.get(category, [])
        query_lower = query.lower()

        # Simple text matching for now
        matches = []
        for product in products:
            name_lower = product['name'].lower()
            specs_lower = product.get('specs', '').lower()
            if any(word in name_lower or word in specs_lower for word in query_lower.split()):
                matches.append(product)

        return matches[:limit] if matches else products[:limit]