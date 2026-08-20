import os
import pickle
from contextlib import asynccontextmanager
from typing import Any, Dict

import numpy as np
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Global model container
ml_models: Dict[str, Any] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Try loading RF.pkl or model.pkl
    base_dir = os.path.dirname(__file__)
    model_paths = [
        os.path.join(base_dir, "RF.pkl"),
        os.path.join(base_dir, "model.pkl"),
        os.path.join(base_dir, "RandomForest.pkl"),
    ]
    
    loaded = False
    for path in model_paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    ml_models["crop_model"] = pickle.load(f)
                print(f"Loaded model successfully from: {path}")
                loaded = True
                break
            except Exception as e:
                print(f"Error loading {path}: {e}")
                
    if not loaded:
        print("Warning: No model .pkl file found. Run train_model.py first.")
        ml_models["crop_model"] = None
        
    yield
    ml_models.clear()

app = FastAPI(
    title="AgriSens - Crop Recommendation API",
    lifespan=lifespan
)

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CropInput(BaseModel):
    nitrogen: float = Field(..., ge=0, le=300, description="Nitrogen ratio in soil (N)")
    phosphorus: float = Field(..., ge=0, le=300, description="Phosphorus ratio in soil (P)")
    potassium: float = Field(..., ge=0, le=300, description="Potassium ratio in soil (K)")
    temperature: float = Field(..., ge=-10, le=60, description="Temperature in °C")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity in %")
    ph: float = Field(..., ge=0, le=14, description="pH value of the soil")
    rainfall: float = Field(..., ge=0, le=1000, description="Rainfall in mm")

    model_config = {
        "json_schema_extra": {
            "example": {
                "nitrogen": 90.0,
                "phosphorus": 42.0,
                "potassium": 43.0,
                "temperature": 20.87,
                "humidity": 82.00,
                "ph": 6.50,
                "rainfall": 202.93
            }
        }
    }

class CropPredictionResponse(BaseModel):
    crop: str
    confidence: float
    status: str

@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "message": "AgriSens Backend API is running.",
        "model_loaded": ml_models.get("crop_model") is not None
    }

# Fixes the 404 on /api/options
@app.get("/api/options", tags=["Options"])
def get_options():
    crops = [
        "apple", "banana", "blackgram", "chickpea", "coconut", "coffee",
        "cotton", "grapes", "jute", "kidneybeans", "lentil", "maize",
        "mango", "mothbeans", "mungbean", "muskmelon", "orange", "papaya",
        "pigeonpeas", "pomegranate", "rice", "watermelon"
    ]
    return {
        "status": "success",
        "crops": crops,
        "parameters": {
            "nitrogen": {"min": 0, "max": 140, "default": 90},
            "phosphorus": {"min": 0, "max": 145, "default": 42},
            "potassium": {"min": 0, "max": 205, "default": 43},
            "temperature": {"min": 0, "max": 50, "default": 25.0},
            "humidity": {"min": 0, "max": 100, "default": 80.0},
            "ph": {"min": 0, "max": 14, "default": 6.5},
            "rainfall": {"min": 0, "max": 300, "default": 200.0}
        }
    }

@app.post(
    "/predict",
    response_model=CropPredictionResponse,
    status_code=status.HTTP_200_OK,
    tags=["Prediction"]
)
def predict_crop(data: CropInput):
    model = ml_models.get("crop_model")
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded. Make sure a trained .pkl file exists in the backend directory."
        )

    features = np.array([[
        data.nitrogen,
        data.phosphorus,
        data.potassium,
        data.temperature,
        data.humidity,
        data.ph,
        data.rainfall
    ]])

    prediction = model.predict(features)[0]
    
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(features)[0]
        confidence = round(float(np.max(probabilities) * 100), 2)
    else:
        confidence = 100.0

    return CropPredictionResponse(
        crop=str(prediction).capitalize(),
        confidence=confidence,
        status="success"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)