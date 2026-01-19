import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
import os
from datetime import datetime


class MLProductRanker:
    """Machine Learning-based product ranking system"""

    def __init__(self):
        self.model = None
        self.scaler = None
        self.model_file = 'product_ranker_model.pkl'
        self.load_or_train_model()

    def load_or_train_model(self):
        """Load existing model or train new one"""
        if os.path.exists(self.model_file):
            try:
                with open(self.model_file, 'rb') as f:
                    data = pickle.load(f)
                    self.model = data['model']
                    self.scaler = data['scaler']
                    print("Loaded existing ML ranking model")
                    return
            except Exception as e:
                print(f"Model loading failed: {e}")

        print("Training new ML ranking model...")
        self.train_model()

    def create_training_data(self):
        """Create synthetic training data for product ranking"""
        # This simulates user preferences and product features
        np.random.seed(42)

        # Generate synthetic product data
        n_samples = 1000

        data = {
            'price': np.random.uniform(15000, 200000, n_samples),
            'rating': np.random.uniform(3.0, 5.0, n_samples),
            'ram_gb': np.random.choice([4, 8, 16, 32, 64], n_samples),
            'storage_gb': np.random.choice([128, 256, 512, 1024, 2048], n_samples),
            'screen_size': np.random.uniform(13, 17, n_samples),
            'has_ssd': np.random.choice([0, 1], n_samples, p=[0.1, 0.9]),
            'processor_tier': np.random.choice([1, 2, 3, 4, 5], n_samples),  # 1=low, 5=high-end
            'brand_premium': np.random.choice([0, 1, 2, 3], n_samples),  # Apple=3, Gaming brands=2, etc.
            'battery_hours': np.random.uniform(4, 12, n_samples),
            'weight_kg': np.random.uniform(1.2, 3.5, n_samples),
            'has_dedicated_gpu': np.random.choice([0, 1], n_samples),
            'refresh_rate': np.random.choice([60, 90, 120, 144, 240], n_samples),
        }

        df = pd.DataFrame(data)

        # Create target variable (user satisfaction score)
        # This is a simulated score based on product features
        df['user_satisfaction'] = (
            df['rating'] * 0.3 +
            (df['ram_gb'] / 64) * 0.15 +
            (df['storage_gb'] / 2048) * 0.1 +
            (df['processor_tier'] / 5) * 0.2 +
            df['has_ssd'] * 0.05 +
            (df['brand_premium'] / 3) * 0.1 +
            (df['battery_hours'] / 12) * 0.05 +
            df['has_dedicated_gpu'] * 0.05
        )

        # Add some noise and normalize
        df['user_satisfaction'] += np.random.normal(0, 0.1, n_samples)
        df['user_satisfaction'] = np.clip(df['user_satisfaction'], 0, 1)

        return df

    def train_model(self):
        """Train the ML model"""
        df = self.create_training_data()

        # Features for training
        features = [
            'price', 'rating', 'ram_gb', 'storage_gb', 'screen_size',
            'has_ssd', 'processor_tier', 'brand_premium', 'battery_hours',
            'weight_kg', 'has_dedicated_gpu', 'refresh_rate'
        ]

        X = df[features]
        y = df['user_satisfaction']

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train model
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )

        self.model.fit(X_train_scaled, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        print(f"Model trained - MAE: {mae:.3f}, R²: {r2:.3f}")
        # Save model
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'features': features,
            'trained_at': datetime.now()
        }

        with open(self.model_file, 'wb') as f:
            pickle.dump(model_data, f)

        print("ML ranking model trained and saved")

    def predict_product_score(self, product_features):
        """Predict user satisfaction score for a product"""
        if not self.model or not self.scaler:
            return 0.5  # Default score

        try:
            # Convert product features to array
            features = [
                product_features.get('price', 50000),
                product_features.get('rating', 4.0),
                product_features.get('ram_gb', 8),
                product_features.get('storage_gb', 512),
                product_features.get('screen_size', 15.6),
                1 if 'ssd' in product_features.get('storage_type', '').lower() else 0,
                self._get_processor_tier(product_features.get('processor', '')),
                self._get_brand_premium(product_features.get('brand', '')),
                product_features.get('battery_hours', 6),
                product_features.get('weight_kg', 2.0),
                1 if product_features.get('has_gpu', False) else 0,
                product_features.get('refresh_rate', 60)
            ]

            # Scale features
            features_scaled = self.scaler.transform([features])

            # Predict
            score = self.model.predict(features_scaled)[0]

            # Convert to 0-100 scale
            return max(0, min(100, score * 100))

        except Exception as e:
            print(f"ML prediction error: {e}")
            return 50  # Fallback score

    def _get_processor_tier(self, processor):
        """Convert processor string to tier"""
        proc_lower = str(processor).lower()

        if any(x in proc_lower for x in ['i9', 'ryzen 9', 'm2', 'm3']):
            return 5  # High-end
        elif any(x in proc_lower for x in ['i7', 'ryzen 7', 'i8']):
            return 4  # Mid-high
        elif any(x in proc_lower for x in ['i5', 'ryzen 5']):
            return 3  # Mid-range
        elif any(x in proc_lower for x in ['i3', 'ryzen 3', 'celeron']):
            return 2  # Entry-level
        else:
            return 1  # Unknown/low

    def _get_brand_premium(self, brand):
        """Convert brand to premium score"""
        brand_lower = str(brand).lower()

        premium_brands = ['apple', 'dell', 'asus', 'msi', 'alienware', 'razer']
        mid_premium = ['lenovo', 'hp', 'acer', 'samsung', 'oneplus', 'google']

        if any(b in brand_lower for b in premium_brands):
            return 3
        elif any(b in brand_lower for b in mid_premium):
            return 2
        else:
            return 1


class EnhancedRanker:
    """Enhanced ranking system combining ML and rule-based scoring"""

    def __init__(self):
        self.ml_ranker = MLProductRanker()
        self.model_loaded = False

        # Try to load existing model
        try:
            if os.path.exists(self.ml_ranker.model_file):
                with open(self.ml_ranker.model_file, 'rb') as f:
                    model_data = pickle.load(f)
                    self.ml_ranker.model = model_data['model']
                    self.ml_ranker.scaler = data['scaler'] if 'scaler' in locals() else model_data['scaler']
                    # self.ml_ranker.features = model_data['features'] # Might be missing in older models
                    self.model_loaded = True
                    # print('Loaded existing ML ranking model')
            else:
                pass
                # print('No existing ML model found, will use rule-based ranking only')
        except Exception as e:
            # print(f'Could not load ML model: {e}, using rule-based ranking only')
            self.model_loaded = False

    def rank_products_enhanced(self, requirements, products):
        """Rank products using ML + rule-based hybrid approach"""
        try:
            if self.model_loaded and len(products) > 0:
                # Try ML ranking first
                return self._ml_enhanced_ranking(requirements, products)
            else:
                # Fall back to rule-based ranking
                return self._rule_based_ranking(requirements, products)
        except Exception as e:
            print(f'ML ranking failed: {e}, using rule-based ranking')
            return self._rule_based_ranking(requirements, products)

    def _ml_enhanced_ranking(self, requirements, products):
        """Enhanced ranking using ML predictions with rule-based fallback"""
        ranked_products = []

        for product in products:
            try:
                # Get ML score
                ml_score = self.ml_ranker.predict_product_score(self._extract_product_features(product))

                # Get rule-based score
                rule_score, reasons = self._calculate_rule_score(requirements, product)

                # Combine scores (70% ML, 30% rule-based)
                combined_score = (ml_score * 0.7) + (rule_score * 0.3)

                # Add to results
                product_copy = product.copy()
                product_copy['match_score'] = round(combined_score, 1)
                product_copy['ranking_reasons'] = reasons
                product_copy['ml_score'] = round(ml_score, 1)
                product_copy['rule_score'] = round(rule_score, 1)

                ranked_products.append(product_copy)

            except Exception as e:
                product_name = product.get('name', 'Unknown')
                print(f'Error ranking product {product_name}: {e}')
                # Fallback to rule-based only - call local method properly!
                try:
                    rule_score, reasons = self._calculate_rule_score(requirements, product)
                    product_copy = product.copy()
                    product_copy['match_score'] = round(rule_score, 1)
                    product_copy['ranking_reasons'] = reasons
                    product_copy['ml_score'] = 0.0
                    product_copy['rule_score'] = round(rule_score, 1)
                    ranked_products.append(product_copy)
                except Exception as e2:
                    print(f"Double fault ranking {product_name}: {e2}")

        # Sort by combined score
        ranked_products.sort(key=lambda x: x['match_score'], reverse=True)
        return ranked_products

    def _rule_based_ranking(self, requirements, products):
        """Pure rule-based ranking as fallback"""
        ranked_products = []
        
        for product in products:
            try:
                score, reasons = self._calculate_rule_score(requirements, product)
                product_copy = product.copy()
                # Ensure minimum score so products aren't filtered out
                final_score = max(round(score, 1), 50.0)  # Minimum 50% score
                product_copy['match_score'] = final_score
                product_copy['match_reasons'] = reasons if reasons else ['Matches basic requirements']
                product_copy['ml_score'] = 0.0
                product_copy['rule_score'] = round(score, 1)
                ranked_products.append(product_copy)
            except Exception as e:
                print(f"[RANKER DEBUG] Error ranking product {product.get('name', 'Unknown')}: {e}")
                # Still add product with default score
                product_copy = product.copy()
                product_copy['match_score'] = 50.0
                product_copy['match_reasons'] = ['Matches basic requirements']
                product_copy['ml_score'] = 0.0
                product_copy['rule_score'] = 50.0
                ranked_products.append(product_copy)
        
        # Sort by score
        ranked_products.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        # Always return at least top 5, even if scores are low
        return ranked_products[:5] if ranked_products else []

    def _calculate_rule_score(self, requirements, product):
        """Calculate rule-based matching score with persona-aware weighting"""
        score = 0
        reasons = []
        max_score = 100

        name_lower = product.get('name', '').lower()
        specs_lower = product.get('specs', '').lower()
        full_text = f"{name_lower} {specs_lower}".lower()
        
        # SAFE PRICE EXTRACTION
        price = product.get('price')
        if price is None:
             price = 0
        elif isinstance(price, str):
             try: price = int(float(price.replace(',','').replace('₹','')))
             except: price = 0
             
        # SAFE BUDGET EXTRACTION
        budget_max = requirements.get('budget_max')
        if budget_max and isinstance(budget_max, str):
            try: budget_max = int(float(budget_max.replace(',','').replace('₹','')))
            except: budget_max = None
            
        # Get persona weights if available
        persona = requirements.get('persona') or {}
        weight_factors = persona.get('weight_factors') or {}
        
        # Base weights (used if persona weights not available)
        base_weights = {
            'price': 0.2,
            'performance': 0.2,
            'battery': 0.15,
            'gpu': 0.15,
            'build_quality': 0.1,
            'portability': 0.1,
            'display': 0.1
        }
        
        # Use persona weights if available, otherwise use base weights
        weights = weight_factors if weight_factors else base_weights

        # Budget check (soft requirement - don't exclude, just penalize)
        price_weight = weights.get('price', 0.2)
        
        if budget_max:
             if price <= budget_max:
                score += 20 * (1 + price_weight)  # Boost if price is important to persona
                reasons.append(f"Within budget (₹{price} ≤ ₹{budget_max})")
             elif price > budget_max * 1.2:  # Allow 20% over budget
                score -= 10 * (1 + price_weight)  # Penalty but don't exclude
                reasons.append(f"Over budget (₹{price} > ₹{budget_max})")
             else:
                # Slightly over budget
                score += 10
                reasons.append(f"Slightly over budget (₹{price} vs ₹{budget_max})")

        # RAM requirements
        ram_needed = requirements.get('ram_needed_gb', 8)
        if not ram_needed: ram_needed = 0
        
        if f"{ram_needed}gb ram" in full_text or f"{ram_needed} gb ram" in full_text:
            score += 15
            reasons.append(f"Meets RAM requirement ({ram_needed}GB)")
        elif ram_needed <= 8 and '8gb ram' in full_text:
            score += 10
            reasons.append("8GB RAM sufficient")

        # Storage requirements
        storage_needed = requirements.get('storage_needed_gb', 512)
        if storage_needed:
            import re
            storage_match = re.search(r'(\d+)\s*(?:gb|tb)', full_text)
            if storage_match:
                val = int(storage_match.group(1))
                if 'tb' in full_text:
                    val *= 1024
                if val >= storage_needed:
                    score += 10
                    reasons.append(f"{val}GB storage meets requirements")

        # Use case bonuses
        use_cases = requirements.get('use_case') or []
        if use_cases:
            if 'gaming' in [str(u).lower() for u in use_cases]:
                if 'rtx' in full_text or 'gtx' in full_text or 'gaming' in full_text:
                    score += 10
                    reasons.append("Gaming optimized")

            if 'coding' in [str(u).lower() for u in use_cases]:
                if 'ssd' in full_text or 'i5' in full_text or 'i7' in full_text:
                    score += 8
                    reasons.append("Good for coding")

        # Rating bonus
        rating = product.get('rating', 0)
        if rating >= 4.5:
            score += 5
            reasons.append("Highly rated")
        elif rating >= 4.0:
            score += 3
            reasons.append("Well rated")

        return min(score, max_score), reasons if reasons else ["Matches basic criteria"]

    def _extract_product_features(self, product):
        """Extract features from product for ML scoring"""
        name = product.get('name', '').lower()
        specs = product.get('specs', '').lower()

        # Extract RAM
        ram_gb = 8  # default
        import re
        ram_match = re.search(r'(\d+)\s*gb\s*ram', specs)
        if ram_match:
            ram_gb = int(ram_match.group(1))

        # Extract storage
        storage_gb = 512  # default
        storage_match = re.search(r'(\d+)\s*(?:gb|tb)', specs)
        if storage_match:
            val = int(storage_match.group(1))
            if 'tb' in specs:
                storage_gb = val * 1024
            else:
                storage_gb = val

        # Extract screen size
        screen_size = 15.6  # default
        screen_match = re.search(r'(\d+(?:\.\d+)?)\s*["\"]', specs)
        if screen_match:
            screen_size = float(screen_match.group(1))

        # Determine processor tier
        processor = ''
        if 'i9' in specs or 'ryzen 9' in specs:
            processor = 'i9'
        elif 'i7' in specs or 'ryzen 7' in specs:
            processor = 'i7'
        elif 'i5' in specs or 'ryzen 5' in specs:
            processor = 'i5'
        elif 'i3' in specs or 'ryzen 3' in specs:
            processor = 'i3'

        return {
            'price': product.get('price') or 50000,
            'rating': product.get('rating', 4.0),
            'ram_gb': ram_gb,
            'storage_gb': storage_gb,
            'screen_size': screen_size,
            'storage_type': 'ssd' if 'ssd' in specs else 'hdd',
            'processor': processor,
            'brand': product.get('brand', ''),
            'battery_hours': 6,  # Default
            'weight_kg': 2.0,    # Default
            'has_gpu': 'rtx' in specs or 'gtx' in specs or 'gpu' in specs,
            'refresh_rate': 120 if '120hz' in specs else 60
        }
