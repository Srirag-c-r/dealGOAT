import os
import json
from groq import Groq
from decouple import config as decouple_config


class LLMService:
    def __init__(self):
        # Try to get API key from decouple config (reads from .env), fall back to os.getenv
        api_key = decouple_config('GROQ_API_KEY', default=None)
        if not api_key:
            api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set. Please add it to .env file")
        self.client = Groq(api_key=api_key)
        # Using llama-3.3-70b-versatile (current latest available)
        # Alternative: llama-3.1-8b-instant (faster, smaller)
        self.model = "llama-3.3-70b-versatile"
    
    def parse_requirements(self, user_text):
        """Convert user text to structured requirements with intelligent fallback"""
        # Defensive input validation
        if not user_text or not isinstance(user_text, str) or not str(user_text).strip():
            print("[PARSE ERROR] user_text is None, empty, or not a string")
            return {
                "device_type": "laptop",
                "budget_min": None,
                "budget_max": 100000,
                "must_have_features": ["High performance"],
                "nice_to_have": [],
                "use_case": ["general"],
                "performance_tier": "mid",
                "processor_min": None,
                "ram_needed_gb": None,
                "storage_needed_gb": None,
                "screen_size_min": None,
                "screen_size_max": None,
                "os_required": None,
                "priority": "performance"
            }
        # Always work with a clean string
        user_text = str(user_text).strip()
        
        prompt = f"""You are a product requirement parser. Extract specifications from user input.

User Input: "{user_text}"

=== CRITICAL RULES ===

1. BUDGET IS A HARD LIMIT (NOT A PREFERENCE):
   - If user says "under ₹50,000" → budget_max = 50000 (ABSOLUTE MAXIMUM)
   - If user says "₹1.5L" or "1.5 lakh" → budget_max = 150000
   - NEVER treat budget as "around" or "approximately"
   - Budget is a WALL, not a guideline

2. EXTRACT NEGATIVE CONSTRAINTS:
   - "no curved screen" → negative_constraints: ["curved_screen"]
   - "flat display only" → negative_constraints: ["curved_screen"]
   - "not for gaming" → negative_constraints: ["gaming"]
   - "avoid touchscreen" → negative_constraints: ["touchscreen"]
   - "no convertible" → negative_constraints: ["convertible"]

3. DEVICE TYPE DETECTION:
   - PHONE: "phone", "smartphone", "mobile", "BGMI", "gaming phone", "120Hz", "AMOLED"
   - LAPTOP: "laptop", "notebook", "computer", "ultrabook", "coding", "i7", "RTX"
   - TABLET: "tablet", "iPad", "ipad pro"

4. EXTRACT EXACT VALUES:
   - Budget: ₹ or rupee amounts (CRITICAL: This is MAXIMUM, not target)
   - Processor: i3/i5/i7/i9 or Ryzen 3/5/7/9
   - RAM: GB amounts (e.g., 16GB)
   - Storage: GB/TB amounts (e.g., 512GB)
   - Screen: inch amounts or refresh rate

5. BRAND PREFERENCE:
   - Extract: ASUS, Lenovo, HP, Dell, Apple, Samsung, Xiaomi, OnePlus, etc.
   - Multiple brands: Return as list
   - No preference: Return empty list []

Return ONLY this JSON format (NO markdown, NO explanation):

{{
  "device_type": "laptop",
  "brand_preference": ["ASUS", "Dell"],
  "budget_min": null,
  "budget_max": 75000,
  "must_have_features": ["high resolution display", "powerful processor"],
  "nice_to_have": ["4K display", "HDR support"],
  "use_case": ["video editing", "photo editing"],
  "negative_constraints": ["curved_screen", "gaming"],
  "performance_tier": "high",
  "processor_min": "i7",
  "ram_needed_gb": 16,
  "storage_needed_gb": 512,
  "screen_size_min": 15,
  "screen_size_max": 17,
  "os_required": null,
  "priority": "display_quality",
  "original_text": "{user_text}"
}}

REMEMBER: budget_max is an ABSOLUTE CEILING. negative_constraints are VETO conditions."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=600
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Clean up markdown/code blocks
            if "```" in response_text:
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            response_text = response_text.strip()
            
            print(f"[PARSE DEBUG] Raw response: {response_text[:200]}")
            parsed = json.loads(response_text)
            print(f"[PARSE DEBUG] Parsed successfully: {parsed}")
            
            # Validate that parsed result has required fields
            if not parsed or not isinstance(parsed, dict) or not parsed.get('device_type'):
                print(f"[PARSE DEBUG] Invalid parsed result, using fallback parsing")
                raise ValueError("Empty or invalid JSON response")
            
            return parsed
            
        except Exception as e:
            print(f"[PARSE ERROR] {str(e)}")
            print(f"[PARSE ERROR] Response text: {response_text if 'response_text' in locals() else 'N/A'}")
            
            # Smart fallback: extract key info manually
            # Ensure user_text is valid for fallback
            if not user_text or not isinstance(user_text, str):
                user_text = ""
            text_lower = str(user_text).lower()
            
            # ============================================================
            # STEP 1: DETECT DEVICE TYPE FIRST (CRITICAL!)
            # ============================================================
            device_type = "laptop"  # default
            
            # Phone detection keywords - COMPREHENSIVE LIST
            phone_keywords = [
                # Direct device names
                'phone', 'smartphone', 'mobile', 'iphone', 'android phone',
                # Gaming indicators
                'bgmi', 'call of duty', 'gaming phone', 'games', 'pubg',
                # Display specifications
                'refresh rate', '120hz', '144hz', '90hz', 'amoled', 'oled', '5g',
                # Phone specs
                'cooling', 'thermal', 'vapor chamber', 'display', 'camera',
                # Phone brands
                'snapdragon', 'xiaomi', 'redmi', 'samsung', 'oneplus', 'poco',
                'realme', 'vivo', 'oppo', 'motorola', 'nokia', 'honor',
                # Phone-specific features
                'compact', 'inch', 'screen size', '6.', '6.2', '6.5', '6.7',
                # Indicators
                'under 6', 'below 6', 'compact phone', 'slim', 'pocket'
            ]
            
            # Tablet detection keywords
            tablet_keywords = ['tablet', 'ipad', 'ipad pro']
            
            # Laptop detection keywords
            laptop_keywords = ['laptop', 'notebook', 'computer', 'ultrabook', 'coding', 'vs code', 
                             'python', 'development', 'programming', 'macbook', 'dell', 'hp', 'asus', 
                             'lenovo', 'acer', 'screen 15', 'screen 16', 'inch screen']
            
            # Determine device type by checking keywords
            has_phone_keywords = any(keyword in text_lower for keyword in phone_keywords)
            has_tablet_keywords = any(keyword in text_lower for keyword in tablet_keywords)
            has_laptop_keywords = any(keyword in text_lower for keyword in laptop_keywords)
            
            # Priority-based decision
            if has_phone_keywords:
                device_type = "phone"
                print(f"[PARSE DEBUG] Device type DETECTED: PHONE")
            elif has_tablet_keywords:
                device_type = "tablet"
                print(f"[PARSE DEBUG] Device type DETECTED: TABLET")
            elif has_laptop_keywords:
                device_type = "laptop"
                print(f"[PARSE DEBUG] Device type DETECTED: LAPTOP")
            else:
                device_type = "laptop"
                print(f"[PARSE DEBUG] Device type: DEFAULT to LAPTOP")
            
            # ============================================================
            # STEP 2: EXTRACT OTHER SPECIFICATIONS
            # ============================================================
            
            # Extract budget with better handling for content creation needs
            budget_max = 100000
            if '₹' in user_text or 'rs' in user_text.lower() or 'rupees' in user_text.lower() or 'rs.' in user_text.lower():
                import re
                # Match various price formats: ₹75,000, 75k, 75000, etc.
                budget_matches = re.findall(r'(?:₹|rs\.?\s*|inr\s*)?(\d+[,\d]*(?:\.\d+)?)(?:\s*(?:k|thousand))?', user_text, re.IGNORECASE)
                if budget_matches:
                    try:
                        # Take the highest mentioned price
                        max_price = 0
                        for match in budget_matches:
                            price_str = match[0].replace(',', '')
                            # If 'k' is present, multiply by 1000
                            if match[1] and match[1].lower() == 'k':
                                price = float(price_str) * 1000
                            else:
                                price = float(price_str)
                            max_price = max(max_price, price)
                        
                        if max_price > 0:
                            budget_max = int(max_price)
                            print(f"[BUDGET DETECTED] Set budget to ₹{budget_max:,}")
                    except Exception as e:
                        print(f"[BUDGET PARSE ERROR] {str(e)}")
                        # Default to 75k for content creation if parsing fails
                        budget_max = 75000
            
            # Detect processor (only for laptops)
            processor = None
            if device_type == "laptop":
                if 'i7' in text_lower or 'intel i7' in text_lower:
                    processor = 'i7'
                elif 'ryzen 7' in text_lower or 'ryzen7' in text_lower:
                    processor = 'Ryzen 7'
                elif 'i9' in text_lower:
                    processor = 'i9'
            
            # Extract RAM
            ram_gb = None
            if '16gb' in text_lower or '16 gb' in text_lower:
                ram_gb = 16
            elif '8gb' in text_lower or '8 gb' in text_lower:
                ram_gb = 8
            
            # Extract storage
            storage_gb = None
            if '512gb' in text_lower or '512 gb' in text_lower:
                storage_gb = 512
            elif '1tb' in text_lower or '1 tb' in text_lower:
                storage_gb = 1024
            
            # Extract screen size (for laptops)
            screen_min = None
            screen_max = None
            if device_type == "laptop":
                if '15' in text_lower and '16' in text_lower:
                    screen_min = '15'
                    screen_max = '16'
                elif '15"' in user_text:
                    screen_min = '15'
                elif '16"' in user_text:
                    screen_min = '16'
            
            # ============================================================
            # STEP 3: BUILD FEATURES LIST
            # ============================================================
            features = []
            use_cases = []
            performance_tier = "mid"
            priority = "performance"
            
            if device_type == "phone":
                # Phone-specific features
                if '120hz' in text_lower or '144hz' in text_lower or '90hz' in text_lower:
                    features.append("High refresh rate display")
                if 'amoled' in text_lower or 'oled' in text_lower:
                    features.append("AMOLED/OLED display")
                if '5g' in text_lower:
                    features.append("5G support")
                if 'clean ui' in text_lower or 'clean interface' in text_lower:
                    features.append("Clean UI")
                if ram_gb:
                    features.append(f"{ram_gb}GB RAM")
                if 'cooling' in text_lower or 'thermal' in text_lower or 'vapor' in text_lower:
                    features.append("Good cooling system")
                if 'battery' in text_lower or 'battery life' in text_lower:
                    features.append("Good battery life")
                if 'gaming' in text_lower:
                    features.append("Gaming performance")
                    use_cases.append("gaming")
                    performance_tier = "high"
                    priority = "gaming"
                if 'camera' in text_lower or 'photography' in text_lower:
                    features.append("Good camera")
                    use_cases.append("photography")
                if 'calling' in text_lower or 'calls' in text_lower:
                    features.append("Clear calling quality")
                    use_cases.append("calling")
                if 'internet' in text_lower or 'browsing' in text_lower:
                    features.append("Good for browsing")
                    use_cases.append("internet")
                if 'compact' in text_lower or 'small' in text_lower or 'mini' in text_lower:
                    features.append("Compact size")
                    priority = "compact"
                
            elif device_type == "laptop":
                # Laptop-specific features
                if processor:
                    features.append(f"{processor} processor")
                if ram_gb:
                    features.append(f"{ram_gb}GB RAM")
                if storage_gb:
                    features.append(f"{storage_gb}GB SSD")
                if screen_min:
                    if screen_max:
                        features.append(f"{screen_min}-{screen_max}\" screen")
                    else:
                        features.append(f"{screen_min}\" screen")
                if 'windows' in text_lower:
                    features.append("Windows OS")
                if 'gaming' in text_lower:
                    features.append("Gaming capable")
                    use_cases.append("gaming")
                if 'coding' in text_lower:
                    features.append("Good for coding")
                    use_cases.append("coding")
                if 'lightweight' in text_lower or 'portable' in text_lower or 'ultrabook' in text_lower:
                    features.append("Lightweight/Portable")
                if 'battery' in text_lower:
                    features.append("Long battery life")
            
            # Build use_cases if not already set
            if not use_cases:
                if 'gaming' in text_lower:
                    use_cases.append("gaming")
                if 'coding' in text_lower:
                    use_cases.append("coding")
                if 'work' in text_lower or 'office' in text_lower:
                    use_cases.append("work")
            
            # ============================================================
            # STEP 4: EXTRACT BRAND PREFERENCE (NEW!)
            # ============================================================
            brand_preference = []
            all_brands = {
                'ASUS': ['asus', 'asus rog', 'rog'],
                'Lenovo': ['lenovo', 'thinkpad', 'legion', 'ideapad'],
                'HP': ['hp ', 'hewlett packard', 'pavilion'],
                'Dell': ['dell', 'alienware', 'xps'],
                'Acer': ['acer', 'nitro'],
                'MSI': ['msi '],
                'Apple': ['apple', 'macbook', 'iphone', 'ipad'],
                'Samsung': ['samsung', 'galaxy'],
                'Xiaomi': ['xiaomi', 'redmi', 'poco'],
                'OnePlus': ['oneplus', 'one plus'],
                'Motorola': ['motorola', 'moto'],
                'Realme': ['realme'],
                'VIVO': ['vivo'],
                'OPPO': ['oppo'],
                'Google': ['google', 'pixel'],
                'Microsoft': ['microsoft', 'surface']
            }
            
            for official_brand, keywords in all_brands.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        if official_brand not in brand_preference:
                            brand_preference.append(official_brand)
                            print(f"[PARSE DEBUG] Brand detected: {official_brand}")
            
            # Extract negative constraints
            negative_constraints = []
            if 'no curved' in text_lower or 'flat screen' in text_lower or 'flat display' in text_lower:
                negative_constraints.append('curved_screen')
            if 'no gaming' in text_lower or 'not for gaming' in text_lower:
                negative_constraints.append('gaming')
            if 'no touchscreen' in text_lower:
                negative_constraints.append('touchscreen')
            if 'no convertible' in text_lower or 'not 2-in-1' in text_lower:
                negative_constraints.append('convertible')
            
            return {
                "device_type": device_type,
                "brand_preference": brand_preference,
                "budget_min": None,
                "budget_max": budget_max,
                "must_have_features": features if features else ["High performance", "Good build quality"],
                "nice_to_have": [],
                "use_case": use_cases if use_cases else ["general"],
                "negative_constraints": negative_constraints,
                "performance_tier": performance_tier,
                "processor_min": processor if device_type == "laptop" else None,
                "ram_needed_gb": ram_gb,
                "storage_needed_gb": storage_gb if device_type == "laptop" else None,
                "screen_size_min": screen_min if device_type == "laptop" else None,
                "screen_size_max": screen_max if device_type == "laptop" else None,
                "os_required": "Windows" if (device_type == "laptop" and "windows" in text_lower) else None,
                "priority": priority,
                "original_text": user_text
            }
    
    def generate_search_queries(self, parsed_requirements):
        """Generate optimized search queries"""
        prompt = f"""
        Based on these requirements:
        {json.dumps(parsed_requirements, indent=2)}
        
        Generate 5 specific, optimized search queries to find products on Amazon.in and Flipkart.com.
        Include specific model names, specs, and price ranges where applicable.
        
        Return ONLY a JSON array of strings (no markdown):
        ["query1", "query2", "query3", "query4", "query5"]
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=300
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Clean up markdown if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            response_text = response_text.strip()
            
            queries = json.loads(response_text)
            return queries if isinstance(queries, list) else [response_text]
        except Exception as e:
            print(f"Error generating queries: {e}")
            device = parsed_requirements.get('device_type') or 'laptop'
            budget = parsed_requirements.get('budget_max') or ''
            features = " ".join((parsed_requirements.get('must_have_features') or []))
            
            return [
                f"best {device} under {budget}",
                f"{device} with {features}",
                f"premium {device} {budget}",
                f"gaming {device}",
                f"{device} with long battery"
            ]
    
    def rank_products(self, requirements, products):
        """Rank products using enhanced ML + rule-based scoring"""
        if not products:
            print("[RANK DEBUG] No products provided!")
            return []
        
        print(f"\n[RENHANCED RANKING] Starting enhanced ranking with {len(products)} products")
        
        # Use enhanced ranker
        try:
            from .ml_ranker import EnhancedRanker
            ranker = EnhancedRanker()
            ranked_products = ranker.rank_products_enhanced(requirements, products)
            print(f"[ENHANCED RANKING] Successfully ranked {len(ranked_products)} products")
            return ranked_products
        except Exception as e:
            print(f"[RANKING ERROR] Using fallback ranking: {str(e)}")
            # Fallback to basic ranking if enhanced ranking fails
            ranked_products = []
            for product in products:
                score = 50  # Base score
                match_reasons = []
                
                # Basic info
                name = str(product.get('name', '')).lower()
                price = float(product.get('price', 0) or 0)
                brand = str(product.get('brand', '')).lower()
                
                # Skip if no price or name
                if not name or price <= 0:
                    continue
            
            # Content creation specific checks
            display_quality = 0
            color_accuracy = 0
            performance = 0
            
            # Check display specifications (critical for content creation)
            display_specs = []
            if 'display' in product:
                display_specs.append(str(product['display']).lower())
            if 'screen' in product:
                display_specs.append(str(product['screen']).lower())
            
            # Rate display quality based on specifications
            display_text = ' '.join(display_specs)
            if any(term in display_text for term in ['4k', 'uhd', '3840', '4096']):
                display_quality += 40  # 4K is excellent for content creation
                match_reasons.append('4K/UHD display')
            elif any(term in display_text for term in ['qhd', '2k', '2560', '1440p']):
                display_quality += 30  # QHD is good
                match_reasons.append('QHD/2K display')
            elif 'fhd' in display_text or 'full hd' in display_text or '1920' in display_text:
                display_quality += 20  # FHD is acceptable
                match_reasons.append('Full HD display')
            
            # Check color accuracy features
            if any(term in display_text for term in ['100% srgb', '100% srgb', 'dci-p3', 'adobe rgb', 'pantone', 'color accurate', 'color-accurate']):
                color_accuracy += 30
                match_reasons.append('Color-accurate display')
            
            # Check for HDR support
            if 'hdr' in display_text:
                display_quality += 10
                match_reasons.append('HDR support')
            
            # Check for high refresh rate (less important for content creation)
            if any(term in display_text for term in ['144hz', '120hz', '240hz']):
                display_quality += 5
                match_reasons.append('High refresh rate display')
            
            # Budget check (30% weight, reduced from 50% to prioritize quality)
            if price <= budget_max:
                budget_ratio = (budget_max - price) / budget_max
                score += 15 * budget_ratio  # Reduced from 25 to 15 points max
                match_reasons.append(f'Within budget (₹{price:,})')
            else:
                # Less penalty for going over budget for content creation
                overage_ratio = (price - budget_max) / budget_max
                score -= min(20, 20 * overage_ratio)  # Reduced from 30 to 20 point max penalty
                match_reasons.append(f'Over budget by ₹{price - budget_max:,}')
            
            # Must-have features (25% weight, reduced from 30%)
            must_have = requirements.get('must_have_features') or []
            must_have_matches = 0
            for feature in must_have:
                if (feature in name or 
                    any(feature in str(v).lower() for v in product.values()) or
                    (feature in ['high resolution', '4k', 'uhd'] and display_quality >= 30)):
                    must_have_matches += 1
                    match_reasons.append(f'Has {feature}')
            
            if must_have:
                must_have_score = 25 * (must_have_matches / len(must_have))
                score += must_have_score
            
            # Nice-to-have features (15% weight)
            nice_to_have = requirements.get('nice_to_have') or []
            nice_have_matches = 0
            for feature in nice_to_have:
                if (feature in name or 
                    any(feature in str(v).lower() for v in product.values()) or
                    (feature in ['hdr', 'color accurate'] and color_accuracy > 0)):
                    nice_have_matches += 1
                    match_reasons.append(f'Has {feature} (nice-to-have)')
            
            if nice_to_have:
                nice_have_score = 15 * (nice_have_matches / len(nice_to_have))
                score += nice_have_score
            
            # Brand preference (5% weight)
            brand_pref = [str(b).lower() for b in (requirements.get('brand_preference') or []) if b]
            if brand_pref and brand in brand_pref:
                score += 5
                match_reasons.append(f'Preferred brand: {brand}')
            
            # Add display quality and color accuracy to score (25% weight total)
            score += (display_quality * 0.15)  # 15% for display quality
            score += (color_accuracy * 0.10)   # 10% for color accuracy
            
            # Don't filter by score threshold - include all products, just rank them
            # This ensures we always return products even if they don't match perfectly
            product_copy['match_score'] = max(score, 50)  # Minimum 50% score
            product_copy['match_reasons'] = reasons if reasons else ["Matches requirements"]
            ranked_products.append(product_copy)
        
        ranked_products.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        return ranked_products[:5] if ranked_products else []
