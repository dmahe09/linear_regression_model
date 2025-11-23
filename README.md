# linear_regression_model

## Mission & Problem
Predict employee salaries based on education, experience, job title, location, age, and gender using regression analysis. The goal is to support fair compensation decisions.

## Dataset
- Source: [Kaggle Salary Dataset](https://www.kaggle.com/) (or specify your actual source)
- Rich in volume and variety, includes relevant features for regression.
- Visualizations: Correlation heatmap and feature distributions (see `summative/linear_regression/multivariate.ipynb`).

## Model Development
- Data preprocessing: Feature engineering, numeric conversion, standardization.
- Models: Linear Regression, Decision Tree, Random Forest (scikit-learn).
- Optimization: Gradient descent for linear regression.
- Evaluation: Loss curves for train/test, scatter plots before/after fitting.
- Best model saved for deployment.

## API
- Built with FastAPI, Pydantic, Uvicorn.
- POST `/predict` endpoint with strict data types and range constraints.
- CORS middleware enabled.
- Hosted on Render (insert your public URL here):  
  [Swagger UI](http://0.0.0.0:8000)

## Flutter App
- Single-page mobile app for salary prediction.
- Inputs match model features.
- "Predict" button calls API and displays result or error.
- Organized, user-friendly layout.

## How to Run

### 1. Backend API (Local)
```powershell
cd summative/API
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Test: Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Flutter App (Windows Desktop)
```powershell
cd summative/FlutterApp
flutter clean
flutter pub get
flutter run -d windows

### 3. Flutter App (Android Emulator)
- Move project out of OneDrive if you get Gradle errors.
- Use: `flutter run -d emulator-5554`

## Video Demo
- [YouTube Demo Link](https://youtu.be/n41gKacRQ6w)
- Shows mobile app prediction, API Swagger UI, model performance, and justification.

## Repo Structure
```
linear_regression_model/
├── summative/
│   ├── linear_regression/
│   │   └── multivariate.ipynb
│   ├── API/
│   │   ├── main.py
│   │   ├── prediction.py
│   │   ├── requirements.txt
│   ├── FlutterApp/
│   │   └── lib/
│   │       └── main.dart
```
## Notes
- For public API, use the Render URL in the Flutter app.
- All code, models, and instructions included for reproducibility.

## Clone the repository
git clone https://github.com/dmahe09/linear_regression_model.git
```
cd linear_regression_model/summative/API
```
cd cd linear_regression_model/summative/FlutterApp
```
cd linear_regression_model/summative/linear_regression
```
