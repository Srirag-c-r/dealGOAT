"""
Smartphone Resale Price Prediction - XGBoost Model Trainer
Adapts the provided Colab notebook so it can run inside this project.
"""

from pathlib import Path
import pickle
import warnings

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBRegressor

warnings.filterwarnings("ignore")


def train_smartphone_model():
    """Train the smartphone price prediction model and persist artifacts."""
    print("=" * 90)
    print("SMARTPHONE RESALE PRICE PREDICTION - MODEL TRAINING")
    print("=" * 90)

    # ------------------------------------------------------------------
    # Load dataset
    # ------------------------------------------------------------------
    dataset_path = Path(__file__).resolve().parents[2] / "dataset" / "mobile.csv"
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    print(f"\n[INFO] Loading dataset from {dataset_path}")
    df = pd.read_csv(dataset_path)
    print(f"[INFO] Dataset loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")

    # ------------------------------------------------------------------
    # Data cleaning
    # ------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("DATA CLEANING")
    print("=" * 90)

    df_clean = df.copy()

    columns_to_drop = ['Title', 'price_raw', 'garbage', 'condition_note', 'Price(INR)']
    df_clean.drop(columns=[c for c in columns_to_drop if c in df_clean.columns], inplace=True, errors='ignore')

    if 'resale_price' not in df_clean.columns:
        raise ValueError("Target column 'resale_price' not found in dataset.")

    initial_count = len(df_clean)
    df_clean = df_clean.dropna(subset=['resale_price'])
    q1 = df_clean['resale_price'].quantile(0.01)
    q99 = df_clean['resale_price'].quantile(0.99)
    df_clean = df_clean[(df_clean['resale_price'] >= q1) & (df_clean['resale_price'] <= q99)]
    print(f"[INFO] Removed {initial_count - len(df_clean):,} outlier rows")
    print(f"[INFO] Dataset after cleaning: {len(df_clean):,} rows")

    # ------------------------------------------------------------------
    # Feature engineering helpers
    # ------------------------------------------------------------------
    condition_map = {
        'Like New': 10, 'Good': 8, 'Fair': 6, 'Average': 5,
        'Used': 5, 'Refurbished': 7, 'Screen Damage': 2, 'No Box': 6
    }
    premium_brands = ['Apple', 'Samsung', 'Google', 'Oneplus', 'Nothing']
    seller_map = {'Store': 3, 'Refurbisher': 2, 'Individual': 1}

    def convert_warranty(val):
        if pd.isna(val):
            return 0
        if isinstance(val, (int, float)):
            return float(val)
        val_str = str(val).strip().lower()
        if 'under warranty' in val_str or 'yes' in val_str:
            return 12
        if val_str in ['0', 'no', 'none', '']:
            return 0
        try:
            return float(val_str)
        except ValueError:
            return 0

    def score_accessories(acc):
        if pd.isna(acc):
            return 0
        acc_str = str(acc).lower()
        score = 0
        if 'charger' in acc_str:
            score += 2
        if 'earphone' in acc_str or 'headphone' in acc_str:
            score += 2
        if 'box' in acc_str:
            score += 2
        if 'bill' in acc_str:
            score += 1
        return score

    # ------------------------------------------------------------------
    # Feature engineering
    # ------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("FEATURE ENGINEERING")
    print("=" * 90)

    if 'brand' in df_clean.columns:
        df_clean['brand'] = df_clean['brand'].astype(str).str.strip().str.title()

    numerical_cols = [
        'storage_GB', 'RAM_GB', 'Battery %', 'battery_health', 'camera_rear_mp',
        'camera_front_mp', 'display_size_inch', 'launch_year', 'price_numeric',
        'screen_cracked', 'body_damage', 'supports_5g'
    ]

    for col in numerical_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            df_clean[col].fillna(df_clean[col].median(), inplace=True)

    if 'warranty' in df_clean.columns:
        df_clean['warranty'] = df_clean['warranty'].apply(convert_warranty)

    binary_cols = ['supports_5g', 'screen_cracked', 'body_damage']
    for col in binary_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0)

    categorical_cols = [
        'brand', 'ModelName', 'processor', 'display_type',
        'condition', 'seller_type', 'seller_location', 'accessories'
    ]
    for col in categorical_cols:
        if col in df_clean.columns:
            df_clean[col].fillna('Unknown', inplace=True)

    current_year = pd.Timestamp.now().year
    if 'purchase_date' in df_clean.columns:
        df_clean['purchase_date'] = pd.to_datetime(df_clean['purchase_date'], errors='coerce')
        df_clean['device_age_years'] = (pd.Timestamp.now() - df_clean['purchase_date']).dt.days / 365.25
        df_clean['device_age_years'].fillna(df_clean['device_age_years'].median(), inplace=True)
    elif 'launch_year' in df_clean.columns:
        df_clean['device_age_years'] = current_year - df_clean['launch_year']
        # Clip the age to be between 0 and 15. This is crucial to prevent the scaler
        # from creating extreme negative values for new phones, which was the root cause
        # of the underprediction bug.
        df_clean['device_age_years'] = df_clean['device_age_years'].clip(0, 15)

    if 'price_numeric' in df_clean.columns:
        df_clean['price_numeric'].fillna(df_clean['price_numeric'].median(), inplace=True)
        df_clean['log_price'] = np.log1p(df_clean['price_numeric'])
        df_clean['depreciation_rate'] = df_clean['price_numeric'] / (df_clean['device_age_years'] + 1)
        df_clean['expected_value'] = df_clean['price_numeric'] * (0.85 ** df_clean['device_age_years'])

    if {'storage_GB', 'RAM_GB'}.issubset(df_clean.columns):
        df_clean['total_memory_score'] = df_clean['storage_GB'] + (df_clean['RAM_GB'] * 8)
        df_clean['memory_ratio'] = df_clean['storage_GB'] / (df_clean['RAM_GB'] + 1)
        df_clean['is_high_memory'] = ((df_clean['storage_GB'] >= 128) & (df_clean['RAM_GB'] >= 6)).astype(int)

    if {'camera_rear_mp', 'camera_front_mp'}.issubset(df_clean.columns):
        df_clean['total_camera'] = df_clean['camera_rear_mp'] + df_clean['camera_front_mp']
        df_clean['camera_quality'] = df_clean['camera_rear_mp'] / (df_clean['camera_front_mp'] + 1)
        df_clean['is_good_camera'] = (df_clean['camera_rear_mp'] >= 48).astype(int)

    if {'Battery %', 'battery_health'}.issubset(df_clean.columns):
        df_clean['battery_avg'] = (df_clean['Battery %'] + df_clean['battery_health']) / 2
        df_clean['battery_score'] = df_clean['battery_avg'] * np.exp(-0.05 * df_clean['device_age_years'])

    if 'condition' in df_clean.columns:
        df_clean['condition_score'] = df_clean['condition'].map(condition_map).fillna(5)

    df_clean['damage_penalty'] = 0
    if 'screen_cracked' in df_clean.columns:
        df_clean['damage_penalty'] += df_clean['screen_cracked'] * 5
    if 'body_damage' in df_clean.columns:
        df_clean['damage_penalty'] += df_clean['body_damage'] * 2

    df_clean['device_quality'] = (
        df_clean.get('condition_score', 5) * 3 +
        df_clean.get('battery_score', 80) / 10 +
        df_clean.get('warranty', 0) / 2 -
        df_clean.get('damage_penalty', 0)
    )

    if 'brand' in df_clean.columns:
        df_clean['is_premium_brand'] = df_clean['brand'].isin(premium_brands).astype(int)

    if 'launch_year' in df_clean.columns:
        df_clean['is_modern'] = (df_clean['launch_year'] >= 2020).astype(int)
        df_clean['year_squared'] = df_clean['launch_year'] ** 2

    if 'display_size_inch' in df_clean.columns:
        df_clean['is_large_display'] = (df_clean['display_size_inch'] >= 6.5).astype(int)

    if 'supports_5g' in df_clean.columns:
        df_clean['5g_premium'] = df_clean['supports_5g'] * df_clean.get('is_modern', 1)

    if 'accessories' in df_clean.columns:
        df_clean['accessories_value'] = df_clean['accessories'].apply(score_accessories)

    if 'seller_type' in df_clean.columns:
        df_clean['seller_reliability'] = df_clean['seller_type'].map(seller_map).fillna(2)

    df_clean['model_popularity'] = 1
    df_clean['model_avg_resale'] = df_clean['resale_price'].median()
    if 'ModelName' in df_clean.columns:
        model_counts = df_clean['ModelName'].value_counts()
        df_clean['model_popularity'] = df_clean['ModelName'].map(model_counts).fillna(1)
        model_mean_price = df_clean.groupby('ModelName')['resale_price'].mean()
        df_clean['model_avg_resale'] = df_clean['ModelName'].map(model_mean_price).fillna(df_clean['resale_price'].median())
    else:
        model_counts = pd.Series(dtype=int)
        model_mean_price = pd.Series(dtype=float)

    if 'price_numeric' in df_clean.columns:
        df_clean['price_age_interaction'] = df_clean['price_numeric'] * np.exp(-0.1 * df_clean['device_age_years'])
        df_clean['price_condition_interaction'] = df_clean['price_numeric'] * (df_clean.get('condition_score', 5) / 10)

    created_features = len([c for c in df_clean.columns if c not in df.columns])
    print(f"[INFO] Created {created_features} engineered features")

    # ------------------------------------------------------------------
    # Encoding
    # ------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("ENCODING CATEGORICAL FEATURES")
    print("=" * 90)

    categorical_to_encode = ['brand', 'processor', 'display_type', 'seller_type', 'seller_location']
    label_encoders = {}
    for col in categorical_to_encode:
        if col in df_clean.columns:
            le = LabelEncoder()
            df_clean[f'{col}_encoded'] = le.fit_transform(df_clean[col].astype(str))
            label_encoders[col] = le
            print(f"[INFO] Encoded {col} ({len(le.classes_)} categories)")

    # ------------------------------------------------------------------
    # Feature selection
    # ------------------------------------------------------------------
    features_to_use = [
        'storage_GB', 'RAM_GB', 'Battery %', 'battery_health',
        'camera_rear_mp', 'camera_front_mp', 'display_size_inch',
        'supports_5g', 'launch_year', 'screen_cracked', 'body_damage', 'warranty',
        'price_numeric', 'log_price', 'device_age_years', 'depreciation_rate',
        'expected_value', 'total_memory_score', 'memory_ratio', 'is_high_memory',
        'total_camera', 'camera_quality', 'is_good_camera', 'battery_avg',
        'battery_score', 'condition_score', 'damage_penalty', 'device_quality',
        'is_premium_brand', 'is_modern', 'year_squared', 'is_large_display',
        '5g_premium', 'accessories_value', 'seller_reliability',
        'model_popularity', 'model_avg_resale', 'price_age_interaction',
        'price_condition_interaction', 'brand_encoded', 'processor_encoded',
        'display_type_encoded', 'seller_type_encoded', 'seller_location_encoded'
    ]

    features_to_use = [f for f in features_to_use if f in df_clean.columns]
    print(f"[INFO] Total features selected: {len(features_to_use)}")

    X = df_clean[features_to_use].copy()
    y = np.log1p(df_clean['resale_price'].copy())

    X = X.apply(pd.to_numeric, errors='coerce')
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median())

    # ------------------------------------------------------------------
    # Scale features
    # ------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("SCALING FEATURES")
    print("=" * 90)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X = pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
    print("[INFO] Features scaled using StandardScaler")

    y = y.fillna(y.median())

    # ------------------------------------------------------------------
    # Train-test split
    # ------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("TRAIN-TEST SPLIT")
    print("=" * 90)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, shuffle=True
    )

    print(f"Training samples: {X_train.shape[0]:,}")
    print(f"Testing samples:  {X_test.shape[0]:,}")

    # ------------------------------------------------------------------
    # Cross-validation
    # ------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("5-FOLD CROSS-VALIDATION")
    print("=" * 90)

    cv_model = XGBRegressor(
        n_estimators=800,
        learning_rate=0.03,
        max_depth=10,
        min_child_weight=1,
        subsample=0.8,
        colsample_bytree=0.8,
        gamma=0.1,
        reg_alpha=0.3,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
        verbosity=0
    )

    cv_scores = cross_val_score(cv_model, X_train, y_train, cv=5, scoring='r2', n_jobs=-1)
    print(f"   CV R² Scores: {[f'{score:.4f}' for score in cv_scores]}")
    print(f"   Mean CV R²:  {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    # ------------------------------------------------------------------
    # Train final model
    # ------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("TRAINING FINAL XGBOOST MODEL")
    print("=" * 90)

    final_model = XGBRegressor(
        n_estimators=1000,
        learning_rate=0.03,
        max_depth=10,
        min_child_weight=1,
        subsample=0.8,
        colsample_bytree=0.8,
        gamma=0.1,
        reg_alpha=0.3,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
        verbosity=0
    )

    final_model.fit(X_train, y_train)
    print("[INFO] Training completed")

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("MODEL EVALUATION")
    print("=" * 90)

    # Get log-predictions
    y_pred_train_log = final_model.predict(X_train)
    y_pred_test_log = final_model.predict(X_test)

    # Invert log-transform to get actual prices
    y_train_orig = np.expm1(y_train)
    y_test_orig = np.expm1(y_test)
    y_pred_train_orig = np.expm1(y_pred_train_log)
    y_pred_test_orig = np.expm1(y_pred_test_log)

    # Evaluate on original scale
    train_r2 = r2_score(y_train_orig, y_pred_train_orig)
    test_r2 = r2_score(y_test_orig, y_pred_test_orig)
    test_mae = mean_absolute_error(y_test_orig, y_pred_test_orig)
    test_rmse = np.sqrt(mean_squared_error(y_test_orig, y_pred_test_orig))
    
    # Filter out zero values in y_test_orig for MAPE calculation to avoid division by zero
    non_zero_mask = y_test_orig > 0
    test_mape = np.mean(np.abs((y_test_orig[non_zero_mask] - y_pred_test_orig[non_zero_mask]) / y_test_orig[non_zero_mask])) * 100

    print(f"   Train R²: {train_r2:.4f}")
    print(f"   Test  R²: {test_r2:.4f}")
    print(f"   Test Accuracy: {test_r2 * 100:.2f}%")
    print(f"   MAE:  ₹{test_mae:,.2f}")
    print(f"   RMSE: ₹{test_rmse:,.2f}")
    print(f"   MAPE: {test_mape:.2f}%")

    overfitting = train_r2 - test_r2
    if overfitting < 0.05:
        print("[INFO] Model is well-generalized.")
    elif overfitting < 0.10:
        print("[WARN] Slight overfitting detected.")
    else:
        print("[WARN] Model may be overfitting.")

    error_percentages = np.abs((y_test_orig[non_zero_mask] - y_pred_test_orig[non_zero_mask]) / y_test_orig[non_zero_mask]) * 100
    within_5 = (error_percentages <= 5).mean() * 100
    within_10 = (error_percentages <= 10).mean() * 100
    print(f"   Predictions within 5%:  {within_5:.2f}%")
    print(f"   Predictions within 10%: {within_10:.2f}%")

    # ------------------------------------------------------------------
    # Persist artifacts
    # ------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("SAVING MODEL ARTIFACTS")
    print("=" * 90)

    models_dir = Path(__file__).resolve().parent / "ml_models"
    models_dir.mkdir(parents=True, exist_ok=True)

    with open(models_dir / "smartphone_price_model.pkl", "wb") as f:
        pickle.dump(final_model, f)

    with open(models_dir / "smartphone_feature_names.pkl", "wb") as f:
        pickle.dump(features_to_use, f)

    with open(models_dir / "smartphone_label_encoders.pkl", "wb") as f:
        pickle.dump(label_encoders, f)

    with open(models_dir / "smartphone_scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)

    metadata = {
        'r2_score': float(test_r2),
        'accuracy': float(test_r2 * 100),
        'mae': float(test_mae),
        'rmse': float(test_rmse),
        'mape': float(test_mape),
        'cv_mean': float(cv_scores.mean()),
        'cv_std': float(cv_scores.std()),
        'n_features': len(features_to_use),
        'n_samples': len(df_clean),
        'median_resale_price': float(df_clean['resale_price'].median())
    }
    with open(models_dir / "smartphone_model_metadata.pkl", "wb") as f:
        pickle.dump(metadata, f)

    stats_payload = {
        'model_popularity': model_counts.to_dict() if 'model_counts' in locals() else {},
        'model_avg_resale': model_mean_price.to_dict() if 'model_mean_price' in locals() else {},
    }
    with open(models_dir / "smartphone_model_stats.pkl", "wb") as f:
        pickle.dump(stats_payload, f)

    print("[INFO] Artifacts saved to backend/predictions/ml_models/")
    print("\n" + "=" * 90)
    print("SMARTPHONE MODEL TRAINING COMPLETE!")
    print("=" * 90)

    return final_model, metadata


if __name__ == "__main__":
    train_smartphone_model()

