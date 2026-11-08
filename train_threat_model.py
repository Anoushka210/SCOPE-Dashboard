import os
import json
import pickle
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, precision_recall_fscore_support
from sklearn.utils.class_weight import compute_sample_weight
import xgboost as xgb
import lightgbm as lgb
import shap

from utils.feature_engineering import fit_feature_encoders, transform_feature_matrix

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
PROCESSED_DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'processed', 'illicit_networks.csv')
ENCODER_PATH = os.path.join(MODELS_DIR, 'feature_encoders.pkl')

def train_and_evaluate_models():
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    if not os.path.exists(PROCESSED_DATA_PATH):
        raise FileNotFoundError(f"Processed dataset not found at {PROCESSED_DATA_PATH}")
        
    print("Loading illicit_networks.csv...")
    df = pd.read_csv(PROCESSED_DATA_PATH, low_memory=False)
    print(f"Total dataset records: {len(df):,}")

    # Time-based split: Train < 2024, Test >= 2024
    cutoff_year = 2024
    train_df = df[df['year'] < cutoff_year].copy()
    test_df = df[df['year'] >= cutoff_year].copy()
    print(f"Time-based split: Train < {cutoff_year} ({len(train_df):,} samples), Test >= {cutoff_year} ({len(test_df):,} samples)")

    # 1. Fit encoders ONLY on training split (no future leakage)
    print("Fitting feature encoders on training split ONLY...")
    encoders = fit_feature_encoders(train_df)
    with open(ENCODER_PATH, 'wb') as f:
        pickle.dump(encoders, f)
    print(f"Encoders saved to {ENCODER_PATH}")

    # 2. Transform train and test matrices
    print("Transforming feature matrices (without target leakage)...")
    X_train, y_train = transform_feature_matrix(train_df, encoders)
    X_test, y_test = transform_feature_matrix(test_df, encoders)
    print(f"Train set shape: {X_train.shape}, Test set shape: {X_test.shape}")
    print("Feature columns:", X_train.columns.tolist())

    models = {
        'RandomForest': RandomForestClassifier(
            n_estimators=100, 
            max_depth=12,
            class_weight='balanced', 
            random_state=42, 
            n_jobs=-1
        ),
        'XGBoost': xgb.XGBClassifier(
            n_estimators=100, 
            max_depth=6,
            learning_rate=0.1,
            random_state=42, 
            eval_metric='mlogloss',
            n_jobs=-1
        ),
        'LightGBM': lgb.LGBMClassifier(
            n_estimators=100, 
            max_depth=6,
            class_weight='balanced', 
            random_state=42, 
            verbose=-1,
            n_jobs=-1
        )
    }

    results = {}
    fitted_models = {}
    class_names = ['Low (0)', 'Medium (1)', 'High (2)', 'Critical (3)']

    for name, model in models.items():
        print(f"\n--- Training {name} ---")
        if name == 'XGBoost':
            sample_weights = compute_sample_weight('balanced', y_train)
            model.fit(X_train, y_train, sample_weight=sample_weights)
        else:
            model.fit(X_train, y_train)
            
        preds = model.predict(X_test)
        
        acc = float(accuracy_score(y_test, preds))
        macro_f1 = float(f1_score(y_test, preds, average='macro'))
        prec, rec, f1, sup = precision_recall_fscore_support(y_test, preds)
        cm = confusion_matrix(y_test, preds).tolist()
        
        per_class_metrics = {}
        for idx, c_name in enumerate(class_names):
            per_class_metrics[c_name] = {
                'precision': round(float(prec[idx]), 4),
                'recall': round(float(rec[idx]), 4),
                'f1': round(float(f1[idx]), 4),
                'support': int(sup[idx])
            }
            
        print(f"{name} Results -> Accuracy: {acc:.4f}, Macro F1: {macro_f1:.4f}")
        for idx, c_name in enumerate(class_names):
            print(f"  {c_name} -> Precision: {prec[idx]:.4f}, Recall: {rec[idx]:.4f}, F1: {f1[idx]:.4f}, Support: {sup[idx]:,}")
        
        results[name] = {
            'accuracy': round(acc, 4),
            'macro_f1': round(macro_f1, 4),
            'per_class_f1': [round(float(x), 4) for x in f1],
            'per_class_metrics': per_class_metrics,
            'confusion_matrix': cm
        }
        fitted_models[name] = model

    best_model_name = max(results, key=lambda k: results[k]['macro_f1'])
    best_model = fitted_models[best_model_name]
    print(f"\n🏆 Winning Model selected by Macro F1: {best_model_name} (Macro F1 = {results[best_model_name]['macro_f1']:.4f})")

    # Save winning model
    model_save_path = os.path.join(MODELS_DIR, 'incident_prediction.pkl')
    with open(model_save_path, 'wb') as f:
        pickle.dump(best_model, f)
    print(f"Serialized winning model saved to {model_save_path}")

    # Save extended honest metrics for ALL models
    metrics_path = os.path.join(MODELS_DIR, 'metrics.json')
    metrics_payload = {
        'winning_model': best_model_name,
        'cutoff_year': cutoff_year,
        'train_samples': int(len(X_train)),
        'test_samples': int(len(X_test)),
        'leakage_status': 'REMOVED - Trained strictly on pre-incident operational indicators (fatalities, nkill, nwound, and EVENTS removed)',
        'critical_class_summary': {
            'test_support': results[best_model_name]['per_class_metrics']['Critical (3)']['support'],
            'precision': results[best_model_name]['per_class_metrics']['Critical (3)']['precision'],
            'recall': results[best_model_name]['per_class_metrics']['Critical (3)']['recall'],
            'f1': results[best_model_name]['per_class_metrics']['Critical (3)']['f1'],
            'assessment': f"Leakage-free evaluation across {len(X_test):,} held-out test events (2024+). Macro F1: {results[best_model_name]['macro_f1']:.4f}."
        },
        'models': results
    }
    with open(metrics_path, 'w') as f:
        json.dump(metrics_payload, f, indent=2)
    print(f"Extended metrics saved to {metrics_path}")

    # Generate SHAP summary plot for winning model
    print("Generating SHAP summary plot for winning model...")
    try:
        sample_size = min(500, len(X_test))
        X_sample = X_test.sample(n=sample_size, random_state=42)
        
        explainer = shap.TreeExplainer(best_model)
        shap_values = explainer.shap_values(X_sample)
        
        plt.figure(figsize=(10, 6), facecolor='#FFFFFF')
        if isinstance(shap_values, list):
            shap.summary_plot(shap_values[1] if len(shap_values) > 1 else shap_values[0], X_sample, show=False)
        elif len(np.shape(shap_values)) == 3:
            shap.summary_plot(shap_values[:, :, 1] if np.shape(shap_values)[2] > 1 else shap_values[:, :, 0], X_sample, show=False)
        else:
            shap.summary_plot(shap_values, X_sample, show=False)
            
        plt.tight_layout()
        shap_img_path = os.path.join(MODELS_DIR, 'shap_summary.png')
        plt.savefig(shap_img_path, dpi=200, bbox_inches='tight')
        plt.close()
        print(f"SHAP summary plot saved to {shap_img_path}")
    except Exception as e:
        print(f"Warning: Error generating SHAP plot: {e}")

if __name__ == '__main__':
    train_and_evaluate_models()
