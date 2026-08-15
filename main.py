"""
Mental Health Score Prediction API
-----------------------------------
FastAPI service that loads the trained sklearn Pipeline (mental_health_model.pkl)
and exposes a /predict endpoint.

Run locally:
    uvicorn main:app --reload --port 8000

Then open: http://127.0.0.1:8000/docs (interactive Swagger UI)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # <-- ADDED
from pydantic import BaseModel, Field
from typing import Literal
import pandas as pd
import joblib
import os

# ------------------------------------------------------------------
# 1. Load the trained pipeline once, at startup
# ------------------------------------------------------------------
MODEL_PATH = os.path.join(os.path.dirname(__file__), "mental_health_model.pkl")

model = None  # will be loaded in the startup event


def load_model():
    global model
    model = joblib.load(MODEL_PATH)


# ------------------------------------------------------------------
# 2. Define the exact same top-10-country grouping used in training
#    (Country_Grouped = Country if in this list, else "Other")
# ------------------------------------------------------------------
TOP_COUNTRIES = [
    "Other", "India", "USA", "Canada", "Australia",
    "UK", "Germany", "Mexico", "Turkey", "France",
]


def group_country(country: str) -> str:
    return country if country in TOP_COUNTRIES else "Other"


# ------------------------------------------------------------------
# 3. Request schema — mirrors the feature_cols used when training
#    (skew_col + other_numeric_col + ordinal_col + normal_col)
# ------------------------------------------------------------------
class StudentInput(BaseModel):
    Age: int = Field(..., ge=10, le=100, example=21)
    Gender: Literal["Male", "Female"] = Field(..., example="Male")
    Country: str = Field(..., example="Pakistan")
    Academic_Level: Literal["High School", "Undergraduate", "Graduate"] = Field(
        ..., example="Undergraduate"
    )
    Most_Used_Platform: Literal[
        "Facebook", "LinkedIn", "Instagram", "Snapchat", "Twitter",
        "YouTube", "TikTok", "LINE", "KakaoTalk", "VKontakte",
        "WhatsApp", "WeChat",
    ] = Field(..., example="Instagram")
    Purpose_Of_Use: Literal[
        "Networking", "Education", "Entertainment", "News"
    ] = Field(..., example="Entertainment")
    Avg_Daily_Usage_Hours: float = Field(..., ge=0, le=24, example=4.5)
    Daily_Unlocks: int = Field(..., ge=0, example=120)
    Study_Hours: float = Field(..., ge=0, le=24, example=3.5)
    Physical_Activity_Hours: float = Field(..., ge=0, le=24, example=1.5)
    Sleep_Hours_Per_Night: float = Field(..., ge=0, le=24, example=7.0)
    Stress_Level: Literal["Low", "Medium", "High", "Very High"] = Field(
        ..., example="Medium"
    )


class PredictionOutput(BaseModel):
    predicted_mental_health_score: float


# ------------------------------------------------------------------
# 4. FastAPI app
# ------------------------------------------------------------------
app = FastAPI(
    title="Mental Health Score Prediction API",
    description="Predicts a student's Mental_Health_Score from social-media "
    "usage, lifestyle and academic features using a trained XGBoost pipeline.",
    version="1.0.0",
)

# ------------------------------------------------------------------
# 4b. CORS — required so a browser-based frontend (opened as a local
#     HTML file, or served from a different port/origin) is allowed
#     to call this API. Without this, the browser blocks the POST
#     /predict preflight (OPTIONS) request with a 405.
# ------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # for local testing; restrict to your real domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    load_model()


@app.get("/")
def root():
    return {
        "message": "Mental Health Score Prediction API is running.",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict", response_model=PredictionOutput)
def predict(data: StudentInput):
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded.")

    try:
        row = data.dict()
        row["Country_Grouped"] = group_country(row.pop("Country"))

        # Column order doesn't matter here because the pipeline's
        # ColumnTransformer selects columns by name.
        input_df = pd.DataFrame([row])

        prediction = model.predict(input_df)[0]
        return PredictionOutput(predicted_mental_health_score=round(float(prediction), 2))

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {e}")