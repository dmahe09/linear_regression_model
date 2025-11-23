from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum

class EducationLevel(str, Enum):
    HIGH_SCHOOL = "High School"
    BACHELOR = "Bachelor"
    MASTER = "Master"
    PHD = "PhD"

class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"  # Added to match Flutter app

class Location(str, Enum):
    URBAN = "Urban"
    SUBURBAN = "Suburban"
    RURAL = "Rural"

class JobTitle(str, Enum):
    MANAGER = "Manager"
    DIRECTOR = "Director"
    ANALYST = "Analyst"
    ENGINEER = "Engineer"
    CONSULTANT = "Consultant"
    SPECIALIST = "Specialist"
    DEVELOPER = "Developer"  # Added to match Flutter app
    DESIGNER = "Designer"    # Added to match Flutter app

class SalaryInput(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Person's full name")
    education: EducationLevel = Field(..., description="Education level")
    years_of_experience: float = Field(..., ge=0, le=50, description="Years of experience (0-50)")
    location: Location = Field(..., description="Work location type")
    job_title: JobTitle = Field(..., description="Job title/position")
    age: int = Field(..., ge=18, le=100, description="Age (18-100)")  # Increased max age to match Flutter validation
    gender: Gender = Field(..., description="Gender")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "education": "Bachelor",
                "years_of_experience": 5.0,
                "location": "Urban",
                "job_title": "Manager",
                "age": 30,
                "gender": "Male"
            }
        }

class SalaryResponse(BaseModel):
    predicted_salary: float = Field(..., description="Predicted salary in USD")
    input_data: dict = Field(..., description="Input data used for prediction")
    confidence_score: Optional[float] = Field(None, description="Prediction confidence (if available)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "predicted_salary": 75000.0,
                "input_data": {
                    "name": "John Doe",
                    "education": "Bachelor",
                    "years_of_experience": 5.0,
                    "location": "Urban",
                    "job_title": "Manager",
                    "age": 30,
                    "gender": "Male"
                },
                "confidence_score": 0.85
            }
        }

class PredictionHistory(BaseModel):
    id: int = Field(..., description="Prediction ID")
    timestamp: str = Field(..., description="Prediction timestamp")
    input_data: dict = Field(..., description="Input data used")
    predicted_salary: float = Field(..., description="Predicted salary")

class HealthResponse(BaseModel):
    status: str = Field(..., description="API health status")
    model_loaded: bool = Field(..., description="Whether the ML model is loaded")
    model_features: Optional[list[str]] = Field(None, description="Model feature names")

class ModelInfoResponse(BaseModel):
    model_type: str = Field(..., description="Type of ML model")
    features: list[str] = Field(..., description="List of model features")
    status: str = Field(..., description="Model loading status")
    training_data_size: Optional[int] = Field(None, description="Size of training dataset")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    
class WelcomeResponse(BaseModel):
    message: str = Field(..., description="Welcome message")
    status: str = Field(..., description="API status")
    model_loaded: bool = Field(..., description="Whether the ML model is loaded")
    docs: str = Field(..., description="API documentation URL")
    available_endpoints: list[str] = Field(..., description="Available API endpoints")

class StatisticsResponse(BaseModel):
    total_predictions: int = Field(..., description="Total number of predictions made")
    average_salary: float = Field(..., description="Average predicted salary")
    most_common_job: str = Field(..., description="Most frequently predicted job title")
    salary_range: dict = Field(..., description="Min and max predicted salaries")