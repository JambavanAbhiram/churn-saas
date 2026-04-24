from pydantic import BaseModel, EmailStr
from typing import Optional

class SignupRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class PredictRequest(BaseModel):
    gender: str
    SeniorCitizen: int
    PhoneService: str
    InternetService: str
    Contract: str
    tenure: int
    MonthlyCharges: float
    TotalCharges: float

class PredictResponse(BaseModel):
    churn: int
    probability: float
