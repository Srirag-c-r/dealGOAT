import time
import random
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup

class BaseScraper:
    def __init__(self):
        self.options = Options()
        self.options.add_argument('--headless=new')  # Use new headless mode
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--window-size=1920,1080')
        # Add realistic user agent
        self.options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    def get_driver(self):
        try:
            return webdriver.Chrome(options=self.options)
        except Exception as e:
            print(f"Error initializing Chrome driver: {e}")
            return None

class AmazonScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.amazon.in/s"

    def search(self, query, max_results=8):
        print(f"[AMAZON] Starting Selenium search for: {query}")
        driver = self.get_driver()
        if not driver:
            return []
            
        products = []
        try:
            search_url = f"{self.base_url}?k={query.replace(' ', '+')}"
            driver.get(search_url)
            
            # Wait for products to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-component-type='s-search-result']"))
                )
            except TimeoutException:
                print("[AMAZON] Timeout waiting for results")
            
            # Parse with BeautifulSoup for speed after loading
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            results = soup.select("div[data-component-type='s-search-result']")
            print(f"[AMAZON] Found {len(results)} raw results")
            
            for item in results[:max_results]:
                try:
                    product = self.extract_product_data(item)
                    if product and product['price'] > 0:
                        products.append(product)
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"[AMAZON] Search error: {e}")
        finally:
            driver.quit()
            
        print(f"[AMAZON] Extracted {len(products)} valid products")
        return products

    def extract_product_data(self, item):
        try:
            # Name
            name_elem = item.select_one("h2 a span") or item.select_one("h2 span")
            if not name_elem: return None
            name = name_elem.get_text(strip=True)
            
            # Link
            link_elem = item.select_one("h2 a")
            if link_elem:
                link = "https://www.amazon.in" + link_elem['href']
            else:
                 # Fallback to search link if direct link fails
                 link = f"https://www.amazon.in/s?k={name.replace(' ', '+')}"
            
            # Price
            price_elem = item.select_one(".a-price .a-offscreen")
            price = 0
            if price_elem:
                price_text = price_elem.get_text(strip=True).replace('₹', '').replace(',', '')
                try: price = int(float(price_text))
                except: pass
            
            # Rating
            rating_elem = item.select_one("span[aria-label*='stars']") or item.select_one(".a-icon-star-small .a-icon-alt")
            rating = 0.0
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True) or rating_elem.get('aria-label', '')
                try: rating = float(rating_text.split()[0])
                except: pass
                
            # Reviews
            reviews_elem = item.select_one("span[aria-label*='ratings']")
            reviews_count = 0
            if reviews_elem:
                try: reviews_count = int(reviews_elem.get('aria-label', '').replace(',', ''))
                except: pass
            
            # Image
            img_elem = item.select_one(".s-image")
            image = img_elem['src'] if img_elem else ""
            
            return {
                'name': name,
                'brand': name.split()[0],
                'amazon_link': link,
                'price': price,
                'rating': rating,
                'reviews_count': reviews_count,
                'source': 'amazon',
                'image': image,
                'specs': f"{name}"
            }
        except:
            return None

class FlipkartScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.flipkart.com/search"

    def search(self, query):
        print(f"[FLIPKART] Starting Selenium search for: {query}")
        driver = self.get_driver()
        if not driver:
            return []
            
        products = []
        try:
            search_url = f"{self.base_url}?q={query.replace(' ', '+')}"
            driver.get(search_url)
            
            # Wait for any common result container
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: d.find_elements(By.CLASS_NAME, "_1UoZlX") or 
                             d.find_elements(By.CLASS_NAME, "_4ddWXP") or
                             d.find_elements(By.CLASS_NAME, "_2kHMtA")
                )
            except TimeoutException:
                print("[FLIPKART] Timeout waiting for results")

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Try multiple selectors
            items = []
            for selector in ["._2kHMtA", "._1UoZlX", "._4ddWXP", "div[data-id]"]:
                items = soup.select(selector)
                if items: break
                
            print(f"[FLIPKART] Found {len(items)} raw results")
            
            for item in items[:8]:
                try:
                    product = self.extract_product_data(item)
                    if product and product['price'] > 0:
                        products.append(product)
                except: continue
                
        except Exception as e:
            print(f"[FLIPKART] Search error: {e}")
        finally:
            driver.quit()
            
        print(f"[FLIPKART] Extracted {len(products)} valid products")
        return products

    def extract_product_data(self, item):
        try:
            # Name
            name_elem = item.select_one("div._4rR01T") or item.select_one("a.s1Q9rs") or item.select_one("a._2rpwq")
            if not name_elem: return None
            name = name_elem.get_text(strip=True)
            
            # Link
            link_elem = item.select_one("a._1fGeJ5") or item.select_one("a.s1Q9rs") or item.select_one("a._2rpwq") or item.select_one("a.CGtC98") or item.select_one("a")
            if link_elem and link_elem.get('href'):
                href = link_elem.get('href')
                if href.startswith('http'):
                    link = href
                else:
                    link = "https://www.flipkart.com" + href if href.startswith('/') else "https://www.flipkart.com/" + href
            else:
                 link = ""
            
            # Price
            price_elem = item.select_one("div._30jeq3")
            price = 0
            if price_elem:
                try: price = int(price_elem.get_text(strip=True).replace('₹', '').replace(',', ''))
                except: pass
                
            # Rating
            rating_elem = item.select_one("div._3LWZlK")
            rating = 0.0
            if rating_elem:
                try: rating = float(rating_elem.get_text(strip=True))
                except: pass
                
            # Image
            img_elem = item.select_one("img._396cs4")
            image = img_elem['src'] if img_elem else ""
            
            return {
                'name': name,
                'brand': name.split()[0],
                'flipkart_link': link,
                'price': price,
                'rating': rating,
                'reviews_count': 0, # Difficult to extract consistently
                'source': 'flipkart',
                'image': image,
                'specs': f"{name}"
            }
        except:
            return None

class ProductSearcher:
    """Unified product searcher combining Selenium scraping with fallback"""
    
    def __init__(self):
        self.amazon = AmazonScraper()
        self.flipkart = FlipkartScraper()
        
        # Comprehensive fallback database
        self.product_database = {
            'laptop': [
                {'name': 'ASUS TUF Gaming F15', 'brand': 'ASUS', 'price': 54990, 'rating': 4.4, 'specs': 'i5 11th Gen, 16GB, 512GB, RTX 3050'},
                {'name': 'Lenovo IdeaPad Gaming 3', 'brand': 'Lenovo', 'price': 49990, 'rating': 4.2, 'specs': 'Ryzen 5, 8GB, 512GB, GTX 1650'},
                {'name': 'HP Pavilion 15', 'brand': 'HP', 'price': 65000, 'rating': 4.3, 'specs': 'i5 12th Gen, 16GB, 512GB'},
                {'name': 'MacBook Air M1', 'brand': 'Apple', 'price': 69990, 'rating': 4.7, 'specs': 'M1, 8GB, 256GB'},
                {'name': 'Dell G15 Gaming', 'brand': 'Dell', 'price': 72990, 'rating': 4.1, 'specs': 'Ryzen 5, 16GB, 512GB, RTX 3050'}
            ],
            'phone': [
                {'name': 'iPhone 13', 'brand': 'Apple', 'price': 49999, 'rating': 4.6, 'specs': '128GB, A15 Bionic'},
                {'name': 'Samsung Galaxy S23', 'brand': 'Samsung', 'price': 64999, 'rating': 4.5, 'specs': '8GB, 128GB, Snapdragon 8 Gen 2'},
                {'name': 'OnePlus 11R', 'brand': 'OnePlus', 'price': 39999, 'rating': 4.4, 'specs': '8GB, 128GB, Snapdragon 8+ Gen 1'},
                {'name': 'Redmi Note 13 Pro', 'brand': 'Xiaomi', 'price': 25999, 'rating': 4.2, 'specs': '8GB, 256GB'},
                {'name': 'Pixel 7a', 'brand': 'Google', 'price': 39999, 'rating': 4.3, 'specs': '8GB, 128GB, Tensor G2'}
            ]
        }
    
    def search(self, queries, parsed_requirements=None):
        print(f"[SEARCHER] Processing queries: {queries}")
        all_products = []
        
        # Try live scraping
        for query in queries[:2]: # Limit to 2 queries to save time
            try:
                # Selenium is slow, run efficiently
                amz_results = self.amazon.search(query)
                all_products.extend(amz_results)
                
                fk_results = self.flipkart.search(query)
                all_products.extend(fk_results)
                
                if len(all_products) >= 5: break
            except Exception as e:
                print(f"[SEARCHER] Error scraping '{query}': {e}")

        # If scraping returned nothing, use fallback
        if not all_products:
            print("[SEARCHER] No live products found. Using fallback database.")
            all_products = self.get_fallback_products(parsed_requirements)
            
        return self._deduplicate(all_products)

    def get_fallback_products(self, parsed_requirements):
        device_type = 'laptop'
        if parsed_requirements:
            device_type = str(parsed_requirements.get('device_type', 'laptop')).lower()
        
        # Simple mapping
        category = 'laptop'
        if 'phone' in device_type or 'mobile' in device_type:
            category = 'phone'
        
        # Get base products
        products = self.product_database.get(category, self.product_database['laptop'])
        
        # Add mock links/images
        formatted = []
        for p in products:
            formatted.append({
                'name': p['name'],
                'brand': p['brand'],
                'price': p['price'],
                'rating': p['rating'],
                'reviews_count': random.randint(100, 5000),
                'amazon_link': f"https://www.amazon.in/s?k={p['name'].replace(' ', '+')}",
                'flipkart_link': f"https://www.flipkart.com/search?q={p['name'].replace(' ', '+')}",
                'image': f"https://via.placeholder.com/300x200?text={p['name'].replace(' ', '+')}",
                'specs': p['specs'],
                'source': 'manual'
            })
        return formatted

    def _deduplicate(self, products):
        seen = set()
        unique = []
        for p in products:
            name = p['name'].lower().strip()
            if name not in seen:
                seen.add(name)
                unique.append(p)
        return unique
