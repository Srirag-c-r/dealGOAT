"""
Laptop Resale Price Prediction - Random Forest Model Trainer
This script trains the ML model and saves it for production use
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

def train_laptop_model():
    """Train the laptop price prediction model"""
    print("=" * 80)
    print("LAPTOP RESALE PRICE PREDICTION - MODEL TRAINING")
    print("=" * 80)
    
    # Load dataset
    print("\n📁 Loading dataset...")
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'dataset', 'laptop.csv')
    
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")
    
    df = pd.read_csv(dataset_path)
    print(f"✅ Dataset loaded: {df.shape[0]:,} samples, {df.shape[1]} features")
    
    # Data preprocessing
    print("\n🔧 Preprocessing data...")
    df_processed = df.copy()
    
    # Check if resale_price exists
    if 'resale_price' not in df_processed.columns:
        raise ValueError("Target column 'resale_price' not found!")
    
    # Identify column types
    numeric_cols = df_processed.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df_processed.select_dtypes(include=['object']).columns.tolist()
    
    # Remove target from numeric columns
    if 'resale_price' in numeric_cols:
        numeric_cols.remove('resale_price')
    
    # Handle missing values
    print("  - Handling missing values...")
    for col in numeric_cols:
        if df_processed[col].isnull().sum() > 0:
            median_value = df_processed[col].median()
            df_processed[col].fillna(median_value if not pd.isna(median_value) else 0, inplace=True)
    
    for col in categorical_cols:
        if df_processed[col].isnull().sum() > 0:
            mode_value = df_processed[col].mode()
            df_processed[col].fillna(mode_value[0] if len(mode_value) > 0 else 'Unknown', inplace=True)
    
    # Handle target variable missing values
    if df_processed['resale_price'].isnull().sum() > 0:
        df_processed['resale_price'].fillna(df_processed['resale_price'].median(), inplace=True)
    
    # Feature Engineering
    print("  - Feature engineering...")
    
    # Device age
    if 'device_age_years' not in df_processed.columns and 'launch_year' in df_processed.columns:
        current_year = 2025
        df_processed['device_age_years'] = current_year - df_processed['launch_year']
        df_processed['device_age_years'].fillna(0, inplace=True)
    
    # Depreciation percentage
    if 'launch_price' in df_processed.columns:
        df_processed['depreciation_pct'] = np.where(
            df_processed['launch_price'] > 0,
            ((df_processed['launch_price'] - df_processed['resale_price']) /
             df_processed['launch_price'] * 100),
            0
        )
    
    # RAM category
    if 'ram' in df_processed.columns:
        df_processed['ram_category'] = pd.cut(df_processed['ram'],
                                               bins=[0, 4, 8, 16, 32, 100],
                                               labels=['Low', 'Medium', 'High', 'Very_High', 'Ultra'])
        df_processed['ram_category'] = df_processed['ram_category'].cat.add_categories(['Unknown'])
        df_processed['ram_category'].fillna('Unknown', inplace=True)
    
    # Storage category
    if 'storage_size' in df_processed.columns:
        df_processed['storage_category'] = pd.cut(df_processed['storage_size'],
                                                   bins=[0, 256, 512, 1024, 2048, 10000],
                                                   labels=['Small', 'Medium', 'Large', 'Very_Large', 'Ultra'])
        df_processed['storage_category'] = df_processed['storage_category'].cat.add_categories(['Unknown'])
        df_processed['storage_category'].fillna('Unknown', inplace=True)
    
    # Separate features and target
    y = df_processed['resale_price'].copy()
    X = df_processed.drop('resale_price', axis=1)
    
    # Encode categorical variables
    print("  - Encoding categorical variables...")
    label_encoders = {}
    categorical_features = X.select_dtypes(include=['object', 'category']).columns
    
    for col in categorical_features:
        le = LabelEncoder()
        X[col] = X[col].astype(str).replace('nan', 'Unknown')
        X[col] = le.fit_transform(X[col])
        label_encoders[col] = le
    
    # Final data cleaning
    X = X.apply(pd.to_numeric, errors='coerce')
    X = X.replace([np.inf, -np.inf], np.nan)
    
    for col in X.columns:
        if X[col].isnull().sum() > 0:
            median_val = X[col].median()
            X[col].fillna(median_val if not pd.isna(median_val) else 0, inplace=True)
    
    # Handle outliers by capping
    print("  - Handling outliers...")
    Q1 = y.quantile(0.25)
    Q3 = y.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    y_capped = y.copy()
    y_capped = np.where(y_capped < lower_bound, lower_bound, y_capped)
    y_capped = np.where(y_capped > upper_bound, upper_bound, y_capped)
    y = pd.Series(y_capped, index=y.index)
    
    print(f"✅ Preprocessing complete: {X.shape[0]:,} samples, {X.shape[1]} features")
    
    # Feature Scaling
    print("\n📏 Scaling features...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
    
    # Train-test split
    print("\n✂️ Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    print(f"Training: {X_train.shape[0]:,} samples, Testing: {X_test.shape[0]:,} samples")
    
    # Train Random Forest model
    print("\n🤖 Training Random Forest model...")
    rf_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        random_state=42,
        n_jobs=-1,
        verbose=0
    )
    
    rf_model.fit(X_train, y_train)
    print("✅ Model training complete!")
    
    # Evaluate model
    print("\n📊 Evaluating model...")
    y_pred = rf_model.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    accuracy = np.mean(np.abs((y_test - y_pred) / np.where(y_test != 0, y_test, 1)) <= 0.10) * 100
    
    print(f"  R² Score:          {r2:.6f}")
    print(f"  Accuracy (±10%):   {accuracy:.2f}%")
    print(f"  MAE:               ₹{mae:,.2f}")
    print(f"  RMSE:              ₹{rmse:,.2f}")
    
    # Save model and artifacts
    print("\n💾 Saving model and artifacts...")
    models_dir = os.path.join(os.path.dirname(__file__), 'ml_models')
    os.makedirs(models_dir, exist_ok=True)
    
    # Save model
    model_path = os.path.join(models_dir, 'laptop_price_model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(rf_model, f)
    
    # Save scaler
    scaler_path = os.path.join(models_dir, 'laptop_scaler.pkl')
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    
    # Save label encoders
    encoders_path = os.path.join(models_dir, 'laptop_label_encoders.pkl')
    with open(encoders_path, 'wb') as f:
        pickle.dump(label_encoders, f)
    
    # Save feature names
    features_path = os.path.join(models_dir, 'laptop_feature_names.pkl')
    with open(features_path, 'wb') as f:
        pickle.dump(list(X.columns), f)
    
    # Save metadata
    metadata = {
        'r2_score': r2,
        'accuracy': accuracy,
        'mae': mae,
        'rmse': rmse,
        'n_features': X.shape[1],
        'n_samples': X.shape[0],
        'feature_names': list(X.columns)
    }
    metadata_path = os.path.join(models_dir, 'laptop_model_metadata.pkl')
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    
    print(f"✅ Model saved to: {model_path}")
    print(f"✅ Scaler saved to: {scaler_path}")
    print(f"✅ Encoders saved to: {encoders_path}")
    print(f"✅ Features saved to: {features_path}")
    print(f"✅ Metadata saved to: {metadata_path}")
    
    print("\n" + "=" * 80)
    print("🎉 MODEL TRAINING COMPLETE!")
    print("=" * 80)
    
    return rf_model, scaler, label_encoders, metadata


if __name__ == '__main__':
    train_laptop_model()

