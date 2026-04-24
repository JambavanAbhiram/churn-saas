import os, joblib, numpy as np, pandas as pd
from typing import Optional

MODEL_DIR = os.environ.get("MODEL_DIR", os.path.join(os.path.dirname(__file__), "..", "models"))
CATEGORICAL_COLS = ["gender", "PhoneService", "InternetService", "Contract"]

_model = _scaler = _features = None

def _load():
    global _model, _scaler, _features
    mp = os.path.join(MODEL_DIR, "model.pkl")
    if not os.path.exists(mp):
        from ml.train import train
        data = os.environ.get("TRAIN_DATA", os.path.join(os.path.dirname(__file__), "..", "data", "churn.csv"))
        train(data)
    _model    = joblib.load(os.path.join(MODEL_DIR, "model.pkl"))
    _scaler   = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
    _features = joblib.load(os.path.join(MODEL_DIR, "features.pkl"))

def get_artifacts():
    if _model is None:
        _load()
    return _model, _scaler, _features

def preprocess_df(df: pd.DataFrame) -> np.ndarray:
    _, scaler, features = get_artifacts()
    df = df.copy()
    df.columns = df.columns.str.strip().str.replace(" ", "_")
    df_enc = pd.get_dummies(df, columns=[c for c in CATEGORICAL_COLS if c in df.columns], drop_first=True)
    for col in features:
        if col not in df_enc.columns:
            df_enc[col] = 0
    return scaler.transform(df_enc[features])

def predict_single(row: dict) -> dict:
    model, _, _ = get_artifacts()
    df = pd.DataFrame([row])
    X = preprocess_df(df)
    prob = float(model.predict_proba(X)[0, 1])
    return {"churn": int(prob >= 0.5), "probability": round(prob, 4)}

def predict_batch(df: pd.DataFrame) -> pd.DataFrame:
    model, _, _ = get_artifacts()
    X = preprocess_df(df)
    probs = model.predict_proba(X)[:, 1]
    df = df.copy()
    df["churn_probability"] = probs.round(4)
    df["churn_prediction"] = (probs >= 0.5).astype(int)
    return df
