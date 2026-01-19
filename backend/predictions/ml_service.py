"""
ML Prediction Service
Handles loading models and making predictions
"""

import os
import pickle

import numpy as np
import pandas as pd


class LaptopPricePredictor:
    """Service class for laptop price predictions."""

    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoders = None
        self.feature_names = None
        self.metadata = None
        self.models_dir = os.path.join(os.path.dirname(__file__), "ml_models")
        self.load_models()

    def load_models(self):
        """Load trained models and artifacts."""
        try:
            # Model + scaler
            with open(os.path.join(self.models_dir, "laptop_price_model.pkl"), "rb") as f:
                self.model = pickle.load(f)
            with open(os.path.join(self.models_dir, "laptop_scaler.pkl"), "rb") as f:
                self.scaler = pickle.load(f)

            # Encoders, features, metadata
            with open(os.path.join(self.models_dir, "laptop_label_encoders.pkl"), "rb") as f:
                self.label_encoders = pickle.load(f)
            with open(os.path.join(self.models_dir, "laptop_feature_names.pkl"), "rb") as f:
                self.feature_names = pickle.load(f)
            with open(os.path.join(self.models_dir, "laptop_model_metadata.pkl"), "rb") as f:
                self.metadata = pickle.load(f)

            print("✅ Laptop models loaded successfully")
        except FileNotFoundError as exc:
            print(f"⚠️  Warning: Laptop model not found: {exc}")
            print("   ML predictions will not be available until models are trained")
            # Don't raise - allow Django to start without models

    def preprocess_input(self, data):
        """Preprocess input data for prediction."""
        processed_data = {
            "launch_year": data.get("launch_year", 2020),
            "launch_price": data.get("launch_price", 50000),
            "ram": data.get("ram", 8),
            "storage_size": data.get("storage_size", 512),
            "screen_size": data.get("screen_size", 15.6),
            "warranty_remaining": data.get("warranty_remaining", 0),
            "battery_cycle_count": data.get("battery_cycle_count", 100),
        }

        current_year = 2025
        processed_data["device_age_years"] = current_year - processed_data["launch_year"]
        processed_data["depreciation_pct"] = 0

        brand = data.get("brand", "Unknown")
        processor = data.get("processor", "Unknown")
        storage_type = data.get("storage_type", "SSD")
        gpu = data.get("gpu", "Unknown")
        condition = data.get("condition", "Good")
        seller_location = data.get("seller_location", "Unknown")
        model_name = data.get("model", "Unknown")

        ram_value = processed_data["ram"]
        if ram_value <= 4:
            ram_category = "Low"
        elif ram_value <= 8:
            ram_category = "Medium"
        elif ram_value <= 16:
            ram_category = "High"
        elif ram_value <= 32:
            ram_category = "Very_High"
        else:
            ram_category = "Ultra"

        storage_value = processed_data["storage_size"]
        if storage_value <= 256:
            storage_category = "Small"
        elif storage_value <= 512:
            storage_category = "Medium"
        elif storage_value <= 1024:
            storage_category = "Large"
        elif storage_value <= 2048:
            storage_category = "Very_Large"
        else:
            storage_category = "Ultra"

        df = pd.DataFrame([processed_data])
        df["brand"] = brand
        df["processor"] = processor
        df["storage_type"] = storage_type
        df["gpu"] = gpu
        df["condition"] = condition
        df["seller_location"] = seller_location
        df["model"] = model_name
        df["ram_category"] = ram_category
        df["storage_category"] = storage_category

        for feature in self.feature_names:
            if feature not in df.columns:
                df[feature] = 0

        for col in df.select_dtypes(include=["object"]).columns:
            if col in self.label_encoders:
                le = self.label_encoders[col]
                df[col] = df[col].apply(lambda x: le.transform([x])[0] if x in le.classes_ else -1)
            else:
                df[col] = 0

        df = df[self.feature_names]
        return df

    def predict(self, data):
        """Make a price prediction."""
        if self.model is None:
            raise ValueError("Laptop model not loaded. Please train the model first.")

        processed_data = self.preprocess_input(data)
        scaled_data = self.scaler.transform(processed_data)
        model_price = max(0, float(self.model.predict(scaled_data)[0]))

        # ------------------------------------------------------------------
        # Business-rule floor to avoid clearly unrealistic underpricing
        # ------------------------------------------------------------------
        # Use launch/original price as the anchor for a minimum resale value.
        price_numeric = float(data.get("launch_price") or data.get("original_price") or 0)

        # Derive approximate device age from launch_year
        current_year = 2025
        launch_year = data.get("launch_year") or current_year
        try:
            launch_year = int(launch_year)
        except (TypeError, ValueError):
            launch_year = current_year
        device_age_years = max(0, current_year - launch_year)

        # Base minimum resale percentage by age
        if device_age_years <= 1:
            base_floor_pct = 0.80
        elif device_age_years <= 2:
            base_floor_pct = 0.70
        elif device_age_years <= 3:
            base_floor_pct = 0.60
        elif device_age_years <= 5:
            base_floor_pct = 0.50
        else:
            base_floor_pct = 0.40

        # Adjust by condition (Excellent, Good, Average, Poor)
        condition = str(data.get("condition", "Good"))
        if condition == "Excellent":
            cond_mult = 1.05
        elif condition == "Good":
            cond_mult = 1.0
        elif condition == "Average":
            cond_mult = 0.85
        else:  # Poor or anything else
            cond_mult = 0.70

        floor_pct = base_floor_pct * cond_mult
        floor_pct = max(0.25, min(floor_pct, 0.85))  # keep within reasonable bounds

        floor_price = price_numeric * floor_pct if price_numeric > 0 else 0.0

        # Final price is at least the floor_price
        predicted_price = max(model_price, floor_price)

        confidence = min(95, self.metadata.get("accuracy", 90))
        price_min = predicted_price * 0.95
        price_max = predicted_price * 1.05

        return {
            "predicted_price": round(predicted_price, 2),
            "confidence_score": round(confidence, 2),
            "price_range": {
                "min": round(price_min, 2),
                "max": round(price_max, 2),
            },
            "model_metrics": {
                "r2_score": self.metadata.get("r2_score"),
                "accuracy": self.metadata.get("accuracy"),
                "mae": self.metadata.get("mae"),
            },
        }

    def get_model_info(self):
        if self.metadata is None:
            return None
        return {
            "r2_score": self.metadata.get("r2_score"),
            "accuracy": self.metadata.get("accuracy"),
            "mae": self.metadata.get("mae"),
            "rmse": self.metadata.get("rmse"),
            "n_features": self.metadata.get("n_features"),
            "n_samples": self.metadata.get("n_samples"),
        }


class SmartphonePricePredictor:
    """Service class for smartphone price predictions."""

    condition_map = {
        "Like New": 10, "Good": 8, "Fair": 6, "Average": 5,
        "Used": 5, "Refurbished": 7, "Screen Damage": 2, "No Box": 6
    }
    premium_brands = {'Apple', 'Samsung', 'Google', 'Oneplus', 'Nothing'}
    seller_map = {'Store': 3, 'Refurbisher': 2, 'Individual': 1}

    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.label_encoders = {}
        self.metadata = {}
        self.stats = {"model_popularity": {}, "model_avg_resale": {}}
        self.models_dir = os.path.join(os.path.dirname(__file__), "ml_models")
        self.load_models()

    def load_models(self):
        """Load trained smartphone artifacts."""
        try:
            with open(os.path.join(self.models_dir, "smartphone_price_model.pkl"), "rb") as f:
                self.model = pickle.load(f)
            with open(os.path.join(self.models_dir, "smartphone_feature_names.pkl"), "rb") as f:
                self.feature_names = pickle.load(f)
            with open(os.path.join(self.models_dir, "smartphone_label_encoders.pkl"), "rb") as f:
                self.label_encoders = pickle.load(f)
            with open(os.path.join(self.models_dir, "smartphone_model_metadata.pkl"), "rb") as f:
                self.metadata = pickle.load(f)
            scaler_path = os.path.join(self.models_dir, "smartphone_scaler.pkl")
            if os.path.exists(scaler_path):
                with open(scaler_path, "rb") as f:
                    self.scaler = pickle.load(f)
                print("\n[SUCCESS] Scaler found. The new, corrected smartphone model pipeline is active.\n")
            stats_path = os.path.join(self.models_dir, "smartphone_model_stats.pkl")
            if os.path.exists(stats_path):
                with open(stats_path, "rb") as f:
                    self.stats = pickle.load(f)
            print("✅ Smartphone model loaded successfully")
        except FileNotFoundError as exc:
            print(f"⚠️  Warning: Smartphone model not found: {exc}")
            print("   ML predictions will not be available until models are trained")
            # Don't raise - allow Django to start without models

    def _score_accessories(self, accessories: str) -> int:
        if not accessories:
            return 0
        acc = accessories.lower()
        score = 0
        if "charger" in acc:
            score += 2
        if "earphone" in acc or "headphone" in acc:
            score += 2
        if "box" in acc:
            score += 2
        if "bill" in acc:
            score += 1
        return score

    def _encode_category(self, col, value):
        encoder = self.label_encoders.get(col)
        if not encoder:
            return 0
        value = str(value)
        if value in encoder.classes_:
            return int(encoder.transform([value])[0])
        return -1

    def preprocess_input(self, data):
        """Apply the same feature engineering used during training."""
        current_year = pd.Timestamp.now().year

        storage = float(data.get("storage_gb", 128) or 128)
        ram = float(data.get("ram_gb", 6) or 6)
        battery_pct = float(data.get("battery_percentage", 85) or 85)
        battery_health = float(data.get("battery_health", 85) or 85)
        camera_rear = float(data.get("camera_rear_mp", 48) or 48)
        camera_front = float(data.get("camera_front_mp", 16) or 16)
        display_size = float(data.get("display_size_inch", 6.5) or 6.5)
        supports_5g = 1 if data.get("supports_5g", False) else 0
        launch_year = int(data.get("launch_year", current_year))
        screen_cracked = 1 if data.get("screen_cracked", False) else 0
        body_damage = 1 if data.get("body_damage", False) else 0
        warranty = float(data.get("warranty_months", 0) or 0)
        price_numeric = float(data.get("launch_price", data.get("original_price", 20000)) or 20000)
        condition = data.get("condition", "Good")
        accessories = data.get("accessories", "")
        seller_type = data.get("seller_type", "Store")

        device_age_years = max(0, current_year - launch_year)
        log_price = np.log1p(price_numeric)
        depreciation_rate = price_numeric / (device_age_years + 1)
        expected_value = price_numeric * (0.85 ** device_age_years)

        total_memory_score = storage + (ram * 8)
        memory_ratio = storage / (ram + 1)
        is_high_memory = int(storage >= 128 and ram >= 6)

        total_camera = camera_rear + camera_front
        camera_quality = camera_rear / (camera_front + 1)
        is_good_camera = int(camera_rear >= 48)

        battery_avg = (battery_pct + battery_health) / 2
        battery_score = battery_avg * np.exp(-0.05 * device_age_years)

        condition_score = self.condition_map.get(condition, 5)
        damage_penalty = screen_cracked * 5 + body_damage * 2
        device_quality = condition_score * 3 + battery_score / 10 + warranty / 2 - damage_penalty

        brand = str(data.get("brand", "Unknown")).title()
        is_premium_brand = int(brand in self.premium_brands)
        is_modern = int(launch_year >= 2020)
        year_squared = launch_year ** 2
        is_large_display = int(display_size >= 6.5)
        g5_premium = supports_5g * is_modern

        accessories_value = self._score_accessories(accessories)
        seller_reliability = self.seller_map.get(seller_type, 2)

        model_name = data.get("model_name") or data.get("model") or "Unknown"
        model_popularity = self.stats.get("model_popularity", {}).get(model_name, 1)
        # If the model name is unknown, fall back to a value based on its own launch
        # price, not the global median. This is critical for new/premium phones.
        model_avg_resale = self.stats.get("model_avg_resale", {}).get(model_name, price_numeric * 0.6)

        price_age_interaction = price_numeric * np.exp(-0.1 * device_age_years)
        price_condition_interaction = price_numeric * (condition_score / 10)

        processed = {
            "storage_GB": storage,
            "RAM_GB": ram,
            "Battery %": battery_pct,
            "battery_health": battery_health,
            "camera_rear_mp": camera_rear,
            "camera_front_mp": camera_front,
            "display_size_inch": display_size,
            "supports_5g": supports_5g,
            "launch_year": launch_year,
            "screen_cracked": screen_cracked,
            "body_damage": body_damage,
            "warranty": warranty,
            "price_numeric": price_numeric,
            "log_price": log_price,
            "device_age_years": device_age_years,
            "depreciation_rate": depreciation_rate,
            "expected_value": expected_value,
            "total_memory_score": total_memory_score,
            "memory_ratio": memory_ratio,
            "is_high_memory": is_high_memory,
            "total_camera": total_camera,
            "camera_quality": camera_quality,
            "is_good_camera": is_good_camera,
            "battery_avg": battery_avg,
            "battery_score": battery_score,
            "condition_score": condition_score,
            "damage_penalty": damage_penalty,
            "device_quality": device_quality,
            "is_premium_brand": is_premium_brand,
            "is_modern": is_modern,
            "year_squared": year_squared,
            "is_large_display": is_large_display,
            "5g_premium": g5_premium,
            "accessories_value": accessories_value,
            "seller_reliability": seller_reliability,
            "model_popularity": model_popularity,
            "model_avg_resale": model_avg_resale,
            "price_age_interaction": price_age_interaction,
            "price_condition_interaction": price_condition_interaction,
            "brand_encoded": self._encode_category("brand", brand),
            "processor_encoded": self._encode_category("processor", data.get("processor", "Unknown")),
            "display_type_encoded": self._encode_category("display_type", data.get("display_type", "LCD")),
            "seller_type_encoded": self._encode_category("seller_type", seller_type),
            "seller_location_encoded": self._encode_category("seller_location", data.get("seller_location", "Unknown")),
        }

        df = pd.DataFrame([processed])
        for feature in self.feature_names:
            if feature not in df.columns:
                df[feature] = 0
        df = df[self.feature_names]
        df = df.replace([np.inf, -np.inf], 0)
        df = df.fillna(0)

        # Scale the features if a scaler is available
        if self.scaler:
            df_scaled = self.scaler.transform(df)
            df = pd.DataFrame(df_scaled, columns=df.columns, index=df.index)

        return df

    def predict(self, data):
        if self.model is None:
            raise ValueError("Smartphone model not loaded. Please train the model first.")

        processed = self.preprocess_input(data)
        # Predict the log-transformed price
        predicted_log_price = self.model.predict(processed)[0]

        # Inverse transform to get the actual price from the model
        model_price = float(max(0, np.expm1(predicted_log_price)))

        # Business-rule floor to avoid clearly unrealistic underpricing
        price_numeric = float(data.get("launch_price") or data.get("original_price") or 0)

        # Derive approximate device age from launch_year
        current_year = pd.Timestamp.now().year
        launch_year = int(data.get("launch_year", current_year) or current_year)
        device_age_years = max(0, current_year - launch_year)

        # Base minimum resale percentage by age (very rough but safe bounds)
        if device_age_years <= 1:
            base_floor_pct = 0.80
        elif device_age_years <= 2:
            base_floor_pct = 0.70
        elif device_age_years <= 3:
            base_floor_pct = 0.60
        else:
            base_floor_pct = 0.45

        # Adjust by condition
        condition = str(data.get("condition", "Good"))
        if condition == "Like New":
            cond_mult = 1.05
        elif condition == "Good":
            cond_mult = 1.0
        elif condition in {"Fair", "Average"}:
            cond_mult = 0.9
        else:  # Used, Refurbished, Screen Damage, No Box
            cond_mult = 0.8

        # Slight boost for premium brands
        brand = str(data.get("brand", "")).title()
        is_premium = brand in self.premium_brands
        premium_mult = 1.05 if is_premium else 1.0

        floor_pct = base_floor_pct * cond_mult * premium_mult
        floor_pct = max(0.30, min(floor_pct, 0.90))  # keep within reasonable bounds

        floor_price = price_numeric * floor_pct if price_numeric > 0 else 0.0

        # Final price is at least the floor_price
        predicted_price = max(model_price, floor_price)

        confidence = min(95, self.metadata.get("accuracy", 90))
        price_min = predicted_price * 0.93
        price_max = predicted_price * 1.07

        return {
            "predicted_price": round(predicted_price, 2),
            "confidence_score": round(confidence, 2),
            "price_range": {
                "min": round(price_min, 2),
                "max": round(price_max, 2),
            },
            "model_metrics": {
                "r2_score": self.metadata.get("r2_score"),
                "accuracy": self.metadata.get("accuracy"),
                "mae": self.metadata.get("mae"),
                "rmse": self.metadata.get("rmse"),
            },
        }

    def get_model_info(self):
        if not self.metadata:
            return None
        return {
            "r2_score": self.metadata.get("r2_score"),
            "accuracy": self.metadata.get("accuracy"),
            "mae": self.metadata.get("mae"),
            "rmse": self.metadata.get("rmse"),
            "n_features": self.metadata.get("n_features"),
            "n_samples": self.metadata.get("n_samples"),
        }


try:
    laptop_predictor = LaptopPricePredictor()
except FileNotFoundError:
    laptop_predictor = None

try:
    smartphone_predictor = SmartphonePricePredictor()
except FileNotFoundError:
    smartphone_predictor = None

