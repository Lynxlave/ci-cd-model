import os
from typing import List
import pickle
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

model = None
try:
    with open("models/model.pkl", "rb") as f:
        model = pickle.load(f)
except FileNotFoundError:
    from models.dummy_model import DummyModel
    model = DummyModel(weights=[1.0, 0.5, -0.3], bias=0.1)


class PredictionRequest(BaseModel):
    x: List[float]


class PredictionResponse(BaseModel):
    prediction: float
    confidence: float
    version: str


@app.get("/health")
def health():
    version = os.getenv("MODEL_VERSION", "v1.0.0")
    return {
        "status": "ok",
        "version": version
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    version = os.getenv("MODEL_VERSION", "v1.0.0")
    
    predictions = model.predict([request.x])
    prediction = float(predictions[0])
    
    proba = model.predict_proba([request.x])[0]
    confidence = float(max(proba))
    
    return PredictionResponse(
        prediction=prediction,
        confidence=confidence,
        version=version
    )

