import os, sys, joblib, numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

CATEGORICAL_COLS = ["gender", "PhoneService", "InternetService", "Contract"]
TARGET = "Churn"
MODEL_DIR = os.environ.get("MODEL_DIR", os.path.join(os.path.dirname(__file__), "..", "models"))

def train(dataset_path: str):
    os.makedirs(MODEL_DIR, exist_ok=True)
    df = pd.read_csv(dataset_path)
    df.columns = df.columns.str.strip().str.replace(" ", "_")
    df_enc = pd.get_dummies(df, columns=CATEGORICAL_COLS, drop_first=True)
    features = [c for c in df_enc.columns if c != TARGET]
    X, y = df_enc[features].values, df_enc[TARGET].values
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    scaler = StandardScaler()
    X_tr = scaler.fit_transform(X_tr)
    X_te = scaler.transform(X_te)
    try:
        from imblearn.over_sampling import SMOTE
        X_tr, y_tr = SMOTE(random_state=42).fit_resample(X_tr, y_tr)
    except ImportError:
        pass
    model = XGBClassifier(n_estimators=300, max_depth=5, learning_rate=0.05,
                          subsample=0.8, colsample_bytree=0.8,
                          eval_metric="logloss", random_state=42)
    model.fit(X_tr, y_tr)
    joblib.dump(model,    os.path.join(MODEL_DIR, "model.pkl"))
    joblib.dump(scaler,   os.path.join(MODEL_DIR, "scaler.pkl"))
    joblib.dump(features, os.path.join(MODEL_DIR, "features.pkl"))
    print(f"Saved model/scaler/features to {MODEL_DIR}")
    return model, scaler, features

if __name__ == "__main__":
    data = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "data", "churn.csv")
    train(data)
