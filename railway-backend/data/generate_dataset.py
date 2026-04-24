"""Run once to generate a synthetic churn dataset for initial training."""
import os, numpy as np, pandas as pd

np.random.seed(42)
N = 2000
df = pd.DataFrame({
    "gender":          np.random.choice(["Male","Female"], N),
    "SeniorCitizen":   np.random.choice([0,1], N, p=[0.84,0.16]),
    "PhoneService":    np.random.choice(["Yes","No"], N, p=[0.9,0.1]),
    "InternetService": np.random.choice(["DSL","Fiber optic","No"], N),
    "Contract":        np.random.choice(["Month-to-month","One year","Two year"], N, p=[0.55,0.25,0.20]),
    "tenure":          np.random.randint(0,73,N),
    "MonthlyCharges":  np.random.uniform(20,110,N).round(2),
    "TotalCharges":    np.random.uniform(100,8000,N).round(2),
})
# synthetic churn label correlated with features
churn_prob = (0.5 - df["tenure"]/150 +
              (df["Contract"]=="Month-to-month").astype(float)*0.25 +
              df["MonthlyCharges"]/400).clip(0.05,0.95)
df["Churn"] = (np.random.rand(N) < churn_prob).astype(int)
out = os.path.join(os.path.dirname(__file__), "churn.csv")
df.to_csv(out, index=False)
print(f"Saved {N} rows to {out}  (churn rate {df.Churn.mean():.1%})")
