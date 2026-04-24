import os
import streamlit as st
import requests
import pandas as pd
import io

API_URL = os.environ.get("API_URL", "http://backend:8000")

st.set_page_config(page_title="ChurnSaaS", page_icon="📉")

# ── Session state ──────────────────────────────────────────────────────────────
if "token" not in st.session_state:
    st.session_state.token = None

def headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

# ── Auth helpers ───────────────────────────────────────────────────────────────
def login(email, password):
    r = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
    if r.ok:
        st.session_state.token = r.json()["access_token"]
        return True
    st.error(r.json().get("detail", "Login failed"))
    return False

def signup(email, password):
    r = requests.post(f"{API_URL}/auth/signup", json={"email": email, "password": password})
    if r.ok:
        st.session_state.token = r.json()["access_token"]
        return True
    st.error(r.json().get("detail", "Signup failed"))
    return False

# ── Login / Signup page ────────────────────────────────────────────────────────
if not st.session_state.token:
    st.title("📉 ChurnSaaS")
    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])
    with tab_login:
        e = st.text_input("Email", key="le")
        p = st.text_input("Password", type="password", key="lp")
        if st.button("Login"):
            login(e, p)
            st.rerun()
    with tab_signup:
        e2 = st.text_input("Email", key="se")
        p2 = st.text_input("Password", type="password", key="sp")
        if st.button("Sign Up"):
            signup(e2, p2)
            st.rerun()
    st.stop()

# ── Main app ───────────────────────────────────────────────────────────────────
st.sidebar.title("📉 ChurnSaaS")
if st.sidebar.button("Logout"):
    st.session_state.token = None
    st.rerun()

page = st.sidebar.radio("Navigate", ["Single Predict", "Batch Predict"])

if page == "Single Predict":
    st.title("Single Customer Prediction")
    col1, col2 = st.columns(2)
    with col1:
        gender       = st.selectbox("Gender", ["Male", "Female"])
        senior       = st.selectbox("Senior Citizen", [0, 1])
        phone        = st.selectbox("Phone Service", ["Yes", "No"])
        internet     = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
    with col2:
        contract     = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
        tenure       = st.slider("Tenure (months)", 0, 72, 12)
        monthly      = st.number_input("Monthly Charges", 0.0, 200.0, 65.0)
        total        = st.number_input("Total Charges", 0.0, 10000.0, tenure * monthly)

    if st.button("Predict Churn"):
        payload = {"gender": gender, "SeniorCitizen": senior, "PhoneService": phone,
                   "InternetService": internet, "Contract": contract,
                   "tenure": tenure, "MonthlyCharges": monthly, "TotalCharges": total}
        r = requests.post(f"{API_URL}/predict", json=payload, headers=headers())
        if r.ok:
            res = r.json()
            prob = res["probability"]
            color = "🔴" if res["churn"] else "🟢"
            st.metric("Churn Risk", f"{prob:.1%}", delta=None)
            st.write(f"{color} **{'Will Churn' if res['churn'] else 'Will NOT Churn'}**")
            st.progress(prob)
        else:
            st.error(r.json().get("detail", "Prediction failed"))

elif page == "Batch Predict":
    st.title("Batch Prediction (CSV Upload)")
    st.info("Upload a CSV with columns: gender, SeniorCitizen, PhoneService, InternetService, Contract, tenure, MonthlyCharges, TotalCharges")
    uploaded = st.file_uploader("Choose CSV", type="csv")
    if uploaded and st.button("Run Batch Predict"):
        r = requests.post(f"{API_URL}/batch_predict",
                          files={"file": (uploaded.name, uploaded.getvalue(), "text/csv")},
                          headers=headers())
        if r.ok:
            df = pd.read_csv(io.StringIO(r.text))
            st.success(f"Done! {len(df)} predictions.")
            st.dataframe(df.tail(20))
            st.download_button("Download Results CSV", r.content,
                               file_name="churn_results.csv", mime="text/csv")
        else:
            st.error(r.json().get("detail", "Batch prediction failed"))
