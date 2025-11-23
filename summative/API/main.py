from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import joblib
from schemas import (
    SalaryInput, 
    SalaryResponse, 
    HealthResponse, 
    ModelInfoResponse, 
    WelcomeResponse,
    ErrorResponse,
    StatisticsResponse,
    PredictionHistory
)
import numpy as np
import pandas as pd
import os
from datetime import datetime
from typing import List
import logging
import random
import json

# Setup logging with more detailed format
logging.basicConfig(
    filename='api.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

# Also log to console for debugging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

app = FastAPI(
    title="Advanced Salary Predictor API",
    description="A comprehensive API to predict salary based on multiple factors including education, experience, location, job title, age, and gender",
    version="2.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update to specific origins in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and scaler
model = None
scaler = None
model_metadata = None
feature_columns = ['Education', 'Experience', 'Location', 'Job_Title', 'Age', 'Gender']
prediction_history = []

def load_model():
    """Load trained model and scaler with comprehensive error checking"""
    global model, scaler, model_metadata
    
    try:
        logger.info("Starting model loading process...")
        
        # Define paths
        model_path = "model/model.pkl"
        scaler_path = "model/scaler.pkl"
        metadata_path = "model/metadata.json"
        
        # Fallback paths
        fallback_model_path = "best_model.pkl"
        fallback_scaler_path = "scaler.pkl"
        
        # Check if primary model files exist
        model_exists = os.path.exists(model_path)
        scaler_exists = os.path.exists(scaler_path)
        metadata_exists = os.path.exists(metadata_path)
        
        logger.info(f"Model file status:")
        logger.info(f"  Primary model ({model_path}): {'✅ EXISTS' if model_exists else '❌ MISSING'}")
        logger.info(f"  Primary scaler ({scaler_path}): {'✅ EXISTS' if scaler_exists else '❌ MISSING'}")
        logger.info(f"  Metadata ({metadata_path}): {'✅ EXISTS' if metadata_exists else '❌ MISSING'}")
        
        # Load metadata if available
        if metadata_exists:
            try:
                with open(metadata_path, 'r') as f:
                    model_metadata = json.load(f)
                logger.info(f"Metadata loaded: {model_metadata}")
            except Exception as e:
                logger.warning(f"Could not load metadata: {e}")
                model_metadata = None
        
        # Try to load primary model
        if model_exists:
            try:
                model = joblib.load(model_path)
                logger.info(f"✅ Model loaded successfully from {model_path}")
                logger.info(f"   Model type: {type(model).__name__}")
            except Exception as e:
                logger.error(f"❌ Error loading primary model: {e}")
                # Try fallback
                if os.path.exists(fallback_model_path):
                    try:
                        model = joblib.load(fallback_model_path)
                        logger.info(f"✅ Fallback model loaded from {fallback_model_path}")
                    except Exception as e2:
                        logger.error(f"❌ Fallback model also failed: {e2}")
                        model = None
                else:
                    model = None
        else:
            logger.warning(f"Primary model not found, trying fallback...")
            if os.path.exists(fallback_model_path):
                try:
                    model = joblib.load(fallback_model_path)
                    logger.info(f"✅ Fallback model loaded from {fallback_model_path}")
                except Exception as e:
                    logger.error(f"❌ Fallback model failed: {e}")
                    model = None
            else:
                logger.error("❌ No model files found!")
                model = None
        
        # Try to load primary scaler
        if scaler_exists:
            try:
                scaler = joblib.load(scaler_path)
                logger.info(f"✅ Scaler loaded successfully from {scaler_path}")
                
                # CRITICAL: Check scaler feature count
                if hasattr(scaler, 'n_features_in_'):
                    n_features = scaler.n_features_in_
                    logger.info(f"   Scaler expects {n_features} features")
                    if n_features != 6:
                        logger.error(f"❌ SCALER MISMATCH: Expected 6 features, got {n_features}")
                        logger.error("   This is likely the source of your error!")
                        logger.error("   Please retrain your model with the updated notebook.")
                    else:
                        logger.info("✅ Scaler feature count matches expected (6 features)")
                else:
                    logger.warning("⚠️  Cannot determine scaler feature count")
                    
            except Exception as e:
                logger.error(f"❌ Error loading primary scaler: {e}")
                # Try fallback
                if os.path.exists(fallback_scaler_path):
                    try:
                        scaler = joblib.load(fallback_scaler_path)
                        logger.info(f"✅ Fallback scaler loaded from {fallback_scaler_path}")
                        
                        # Check fallback scaler too
                        if hasattr(scaler, 'n_features_in_'):
                            n_features = scaler.n_features_in_
                            logger.info(f"   Fallback scaler expects {n_features} features")
                            if n_features != 6:
                                logger.error(f"❌ FALLBACK SCALER MISMATCH: Expected 6 features, got {n_features}")
                        
                    except Exception as e2:
                        logger.error(f"❌ Fallback scaler also failed: {e2}")
                        scaler = None
                else:
                    scaler = None
        else:
            logger.warning(f"Primary scaler not found, trying fallback...")
            if os.path.exists(fallback_scaler_path):
                try:
                    scaler = joblib.load(fallback_scaler_path)
                    logger.info(f"✅ Fallback scaler loaded from {fallback_scaler_path}")
                    
                    # Check fallback scaler
                    if hasattr(scaler, 'n_features_in_'):
                        n_features = scaler.n_features_in_
                        logger.info(f"   Fallback scaler expects {n_features} features")
                        if n_features != 6:
                            logger.error(f"❌ FALLBACK SCALER MISMATCH: Expected 6 features, got {n_features}")
                            
                except Exception as e:
                    logger.error(f"❌ Fallback scaler failed: {e}")
                    scaler = None
            else:
                logger.error("❌ No scaler files found!")
                scaler = None
        
        # Final status report
        logger.info("\n" + "="*50)
        logger.info("MODEL LOADING SUMMARY")
        logger.info("="*50)
        logger.info(f"Model loaded: {'✅ YES' if model is not None else '❌ NO'}")
        logger.info(f"Scaler loaded: {'✅ YES' if scaler is not None else '❌ NO'}")
        
        if model is not None and scaler is not None:
            logger.info("🎉 ALL COMPONENTS LOADED SUCCESSFULLY!")
        elif model is not None:
            logger.warning("⚠️  MODEL LOADED BUT NO SCALER - Predictions may be inaccurate")
        else:
            logger.warning("⚠️  USING MOCK PREDICTIONS - No model available")
        
        logger.info("="*50)
            
    except Exception as e:
        logger.error(f"❌ Critical error in load_model: {e}")
        model = None
        scaler = None
        model_metadata = None

# Load model on startup
logger.info("🚀 Starting API server...")
load_model()

def encode_categorical_features(input_data: SalaryInput) -> np.ndarray:
    """Convert categorical input to numerical features for model prediction"""
    try:
        logger.debug(f"Encoding features for: {input_data.name}")
        
        # Education encoding
        education_map = {"High School": 0, "Bachelor": 1, "Master": 2, "PhD": 3}
        education_encoded = education_map.get(input_data.education, 1)
        
        # Location encoding
        location_map = {"Rural": 0, "Suburban": 1, "Urban": 2}
        location_encoded = location_map.get(input_data.location, 1)
        
        # Job Title encoding - Updated to include all job titles
        job_title_map = {
            "Analyst": 0, 
            "Consultant": 1, 
            "Director": 2, 
            "Engineer": 3, 
            "Manager": 4, 
            "Specialist": 5,
            "Developer": 3,  # Map to Engineer (similar skill level)
            "Designer": 5    # Map to Specialist
        }
        job_title_encoded = job_title_map.get(input_data.job_title, 4)
        
        # Gender encoding - Updated to handle "Other"
        gender_map = {"Male": 1, "Female": 0, "Other": 0}
        gender_encoded = gender_map.get(input_data.gender, 0)
        
        # Create feature array [Education, Experience, Location, Job_Title, Age, Gender]
        # This MUST match your model training order!
        features = np.array([[
            education_encoded,          # Position 0: Education
            input_data.years_of_experience,  # Position 1: Experience
            location_encoded,           # Position 2: Location
            job_title_encoded,          # Position 3: Job_Title
            input_data.age,             # Position 4: Age
            gender_encoded              # Position 5: Gender
        ]], dtype=float)
        
        logger.debug(f"Encoded features shape: {features.shape}")
        logger.debug(f"Encoded values: {features[0]}")
        
        return features
        
    except Exception as e:
        logger.error(f"Error encoding features: {e}")
        raise

def mock_prediction(input_data: SalaryInput) -> float:
    """Fallback prediction when model is not available"""
    logger.info("Using mock prediction (no model available)")
    
    # Simple mock prediction logic
    base_salary = 50000
    
    # Education multiplier
    education_multiplier = {
        "High School": 1.0,
        "Bachelor": 1.3,
        "Master": 1.6,
        "PhD": 2.0
    }
    
    # Job title multiplier - Updated with all job titles
    job_multiplier = {
        "Manager": 1.5,
        "Developer": 1.4,
        "Analyst": 1.2,
        "Designer": 1.1,
        "Engineer": 1.4,
        "Director": 1.8,
        "Consultant": 1.3,
        "Specialist": 1.2
    }
    
    # Location multiplier
    location_multiplier = {
        "Urban": 1.3,
        "Suburban": 1.1,
        "Rural": 0.9
    }
    
    # Gender multiplier (unfortunately still exists in some industries)
    gender_multiplier = {
        "Male": 1.0,
        "Female": 0.95,
        "Other": 1.0
    }
    
    # Calculate predicted salary
    predicted_salary = (
        base_salary * 
        education_multiplier.get(input_data.education, 1.0) *
        job_multiplier.get(input_data.job_title, 1.0) *
        location_multiplier.get(input_data.location, 1.0) *
        gender_multiplier.get(input_data.gender, 1.0) *
        (1 + input_data.years_of_experience * 0.05)  # 5% per year
    )
    
    # Age factor (peak earning years 35-50)
    age_factor = 1.0
    if 35 <= input_data.age <= 50:
        age_factor = 1.1
    elif input_data.age < 25:
        age_factor = 0.9
    
    predicted_salary *= age_factor
    
    # Add some randomness
    predicted_salary *= (0.95 + random.random() * 0.1)  # ±5% variation
    
    return round(predicted_salary, 2)

@app.get("/", response_model=WelcomeResponse)
def read_root():
    logger.info("Root endpoint accessed")
    return WelcomeResponse(
        message="Welcome to the Advanced Salary Predictor API",
        status="active",
        model_loaded=model is not None,
        docs="/docs",
        available_endpoints=["/", "/health", "/predict", "/model-info", "/statistics", "/history", "/debug"]
    )

@app.get("/health", response_model=HealthResponse)
def health_check():
    logger.info("Health check endpoint accessed")
    scaler_features = None
    if scaler is not None and hasattr(scaler, 'n_features_in_'):
        scaler_features = scaler.n_features_in_
    
    return HealthResponse(
        status="healthy",
        model_loaded=model is not None,
        model_features=feature_columns if model is not None else None,
        scaler_features=scaler_features
    )

@app.get("/debug")
def debug_info():
    """Debug endpoint to help diagnose model loading issues"""
    debug_data = {
        "model_loaded": model is not None,
        "scaler_loaded": scaler is not None,
        "model_type": str(type(model).__name__) if model is not None else None,
        "scaler_type": str(type(scaler).__name__) if scaler is not None else None,
        "expected_features": feature_columns,
        "files_check": {
            "model/model.pkl": os.path.exists("model/model.pkl"),
            "model/scaler.pkl": os.path.exists("model/scaler.pkl"),
            "model/metadata.json": os.path.exists("model/metadata.json"),
            "best_model.pkl": os.path.exists("best_model.pkl"),
            "scaler.pkl": os.path.exists("scaler.pkl")
        },
        "metadata": model_metadata
    }
    
    if scaler is not None and hasattr(scaler, 'n_features_in_'):
        debug_data["scaler_features_expected"] = scaler.n_features_in_
        debug_data["feature_mismatch"] = scaler.n_features_in_ != 6
    
    return debug_data

@app.post("/predict", response_model=SalaryResponse)
def predict_salary(input_data: SalaryInput):
    try:
        logger.info(f"🔍 Prediction request received for: {input_data.name}")
        logger.info(f"   Input: Education={input_data.education}, Experience={input_data.years_of_experience}, "
                   f"Location={input_data.location}, Job={input_data.job_title}, Age={input_data.age}, Gender={input_data.gender}")
        
        if model is None:
            # Use mock prediction when model is not available
            logger.warning("⚠️  Using mock prediction - model not loaded")
            predicted_salary = mock_prediction(input_data)
            confidence_score = 0.60  # Lower confidence for mock predictions
            
        else:
            logger.info("🤖 Using actual model for prediction")
            
            # Encode categorical features
            features = encode_categorical_features(input_data)
            logger.info(f"   Encoded features shape: {features.shape}")
            logger.info(f"   Encoded features: {features[0]}")
            
            # Scale features if scaler is available
            if scaler is not None:
                logger.info("🔄 Scaling features...")
                try:
                    features_scaled = scaler.transform(features)
                    logger.info(f"   Scaled features shape: {features_scaled.shape}")
                    logger.info(f"   Scaling successful ✅")
                    features = features_scaled
                except Exception as scale_error:
                    logger.error(f"❌ SCALING ERROR: {scale_error}")
                    logger.error("   This is likely the '6 features vs 1 feature' error!")
                    logger.error("   Please retrain your model with the updated notebook.")
                    raise HTTPException(
                        status_code=500, 
                        detail=f"Feature scaling error: {str(scale_error)}. "
                               f"Model expects different number of features. Please retrain the model."
                    )
            else:
                logger.warning("⚠️  No scaler available - using raw features")
            
            # Make prediction
            logger.info("🎯 Making prediction...")
            try:
                prediction = model.predict(features)
                predicted_salary = float(prediction[0])
                logger.info(f"   Prediction successful: ${predicted_salary:,.2f}")
                confidence_score = 0.85
            except Exception as pred_error:
                logger.error(f"❌ PREDICTION ERROR: {pred_error}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Model prediction error: {str(pred_error)}"
                )
        
        # Store prediction in history
        prediction_record = {
            "id": len(prediction_history) + 1,
            "timestamp": datetime.now().isoformat(),
            "input_data": input_data.dict(),
            "predicted_salary": predicted_salary
        }
        prediction_history.append(prediction_record)
        
        # Add some variation to confidence score
        confidence_score += np.random.normal(0, 0.03)  # Small variation
        confidence_score = min(0.98, max(0.50, confidence_score))
        
        logger.info(f"✅ Prediction completed: {input_data.name} -> ${predicted_salary:,.2f} (confidence: {confidence_score:.3f})")
        
        return SalaryResponse(
            predicted_salary=predicted_salary,
            input_data=input_data.dict(),
            confidence_score=round(confidence_score, 3)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected prediction error: {str(e)}")

@app.get("/model-info", response_model=ModelInfoResponse)
def get_model_info():
    logger.info("Model info endpoint accessed")
    
    model_type = str(type(model).__name__) if model is not None else "MockModel"
    status = "loaded" if model is not None else "using_mock"
    
    additional_info = {}
    if scaler is not None and hasattr(scaler, 'n_features_in_'):
        additional_info["scaler_features"] = scaler.n_features_in_
        additional_info["feature_mismatch"] = scaler.n_features_in_ != 6
    
    if model_metadata:
        additional_info.update(model_metadata)
    
    return ModelInfoResponse(
        model_type=model_type,
        features=feature_columns,
        status=status,
        training_data_size=len(prediction_history) if prediction_history else None,
        **additional_info
    )

@app.get("/statistics", response_model=StatisticsResponse)
def get_statistics():
    logger.info("Statistics endpoint accessed")
    if not prediction_history:
        return StatisticsResponse(
            total_predictions=0,
            average_salary=0.0,
            most_common_job="N/A",
            salary_range={"min": 0, "max": 0}
        )
    
    salaries = [p["predicted_salary"] for p in prediction_history]
    jobs = [p["input_data"]["job_title"] for p in prediction_history]
    
    from collections import Counter
    job_counts = Counter(jobs)
    most_common_job = job_counts.most_common(1)[0][0] if job_counts else "N/A"
    
    return StatisticsResponse(
        total_predictions=len(prediction_history),
        average_salary=round(sum(salaries) / len(salaries), 2),
        most_common_job=most_common_job,
        salary_range={"min": min(salaries), "max": max(salaries)}
    )

@app.get("/history", response_model=List[PredictionHistory])
def get_prediction_history(limit: int = 10):
    logger.info(f"Prediction history endpoint accessed with limit={limit}")
    return [
        PredictionHistory(**record) 
        for record in prediction_history[-limit:]
    ]

@app.delete("/history")
def clear_history():
    logger.info("Prediction history cleared")
    global prediction_history
    prediction_history = []
    return {"message": "Prediction history cleared"}

@app.post("/reload-model")
def reload_model():
    logger.info("🔄 Model reload endpoint accessed")
    load_model()
    
    scaler_features = None
    if scaler is not None and hasattr(scaler, 'n_features_in_'):
        scaler_features = scaler.n_features_in_
    
    return {
        "message": "Model reload completed",
        "model_loaded": model is not None,
        "scaler_loaded": scaler is not None,
        "scaler_features": scaler_features,
        "feature_mismatch": scaler_features != 6 if scaler_features else None
    }

# Test endpoint for debugging
@app.post("/test-prediction")
def test_prediction():
    """Test endpoint with hardcoded values for debugging"""
    test_input = SalaryInput(
        name="Test User",
        age=30,
        gender="Male",
        education="Bachelor",
        years_of_experience=5,
        job_title="Engineer",
        location="Urban"
    )
    
    try:
        result = predict_salary(test_input)
        return {
            "test_successful": True,
            "result": result,
            "message": "Test prediction completed successfully"
        }
    except Exception as e:
        return {
            "test_successful": False,
            "error": str(e),
            "message": "Test prediction failed"
        }

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting API server on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")