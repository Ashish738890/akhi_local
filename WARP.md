# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a full-stack agricultural application for crop recommendation and pest detection. The system uses machine learning models to predict optimal crops based on soil and environmental conditions, and identify pests from images.

**Tech Stack:**
- **Frontend**: React (with React Router, TailwindCSS, Framer Motion, Recharts)
- **Backend**: Node.js/Express with MongoDB
- **ML Service**: Flask (Python) with scikit-learn and TensorFlow/Keras

## Architecture

### Three-Tier Architecture

1. **Frontend (React SPA)** - Runs on port 3000 (dev)
   - Handles UI/UX for crop recommendations, weather info, and advisory services
   - Uses Axios to communicate with backend API
   - Environment variable: `REACT_APP_API_URL` (defaults to http://localhost:5000)

2. **Backend (Node.js/Express)** - Runs on port 5000
   - Acts as API gateway between frontend and ML services
   - Handles prediction persistence to MongoDB
   - Routes:
     - `/api/predict` - Crop prediction (calls Python predict.py via child_process)
     - `/api/advisory/pest-detect` - Pest detection (proxies to Flask API)
   - Environment variables in `backend/.env`:
     - `MONGO_URI` - MongoDB connection string
     - `PORT` - Server port (default: 5000)

3. **ML Service (Flask)** - Runs on port 5001
   - Serves two ML models:
     - **Crop Model**: RandomForest classifier (scikit-learn) - predicts crops from soil/weather data
     - **Pest Model**: CNN (TensorFlow/Keras) - classifies pest images
   - Endpoints:
     - `/predict` - Crop recommendation (JSON input: N, P, K, temperature, humidity, ph, rainfall)
     - `/predict-pest` - Pest detection (multipart/form-data image upload)
     - `/health` - Health check
   - Environment variables (optional):
     - `PORT` (default: 5001)
     - `MODEL_PATH` (default: models/crop_model.pkl)
     - `PEST_MODEL_PATH` (default: models/pest_cnn_model.h5)
     - `PEST_DATA_DIR` (default: data/pest_dataset)
     - `PestCNNEnabled` (default: true)

### Data Flow

**Crop Prediction:**
Frontend → Backend `/api/predict` → Python script via spawn → ML prediction → MongoDB save → Response

**Pest Detection:**
Frontend → Backend `/api/advisory/pest-detect` → Flask `/predict-pest` → CNN inference → Response

### Key Directories

- `frontend/src/pages/` - Page components (Home, CropRecommendation, Weather, Advisory, CropDetails)
- `frontend/src/components/` - Reusable UI components (Navbar, Footer, Form)
- `frontend/src/api/` - API client configuration
- `backend/routes/` - Express route handlers
- `backend/models/` - MongoDB schemas (Prediction)
- `backend/controllers/` - Business logic controllers
- `ml-model/` - ML training scripts and Flask API
- `ml-model/models/` - Trained model artifacts (.pkl, .h5)
- `ml-model/data/` - Training datasets

## Development Commands

### Initial Setup

```powershell
# Install frontend dependencies
cd frontend
npm install

# Install backend dependencies
cd backend
npm install

# Setup Python virtual environment (from project root)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install Python dependencies (manually for now - no requirements.txt exists)
pip install flask flask-cors numpy pandas scikit-learn tensorflow pillow
```

### Running the Application

**Start all three services in separate terminals:**

```powershell
# Terminal 1: Start Flask ML service
.\venv\Scripts\Activate.ps1
cd ml-model
python app.py
# Runs on http://localhost:5001

# Terminal 2: Start Node.js backend
cd backend
npm run dev
# Runs on http://localhost:5000

# Terminal 3: Start React frontend
cd frontend
npm start
# Runs on http://localhost:3000
```

### Building

```powershell
# Build frontend for production
cd frontend
npm run build
# Creates optimized build in frontend/build/
```

### Training ML Models

```powershell
# Activate virtual environment first
.\venv\Scripts\Activate.ps1
cd ml-model

# Train crop recommendation model
python train_model.py
# Outputs: models/crop_model.pkl

# Train pest detection CNN
python cnn_pest_model.py
# Requires: data/pest_dataset/ with subdirectories for each pest class
# Outputs: models/pest_cnn_model.h5
```

### Testing

Frontend tests (React Testing Library/Jest):
```powershell
cd frontend
npm test
```

*Note: No backend or ML service tests are currently configured.*

## Development Notes

### MongoDB Connection
The backend requires a MongoDB instance. Ensure `MONGO_URI` is set in `backend/.env` before starting the backend service.

### Python Environment
The project uses a virtual environment located at `venv/`. Always activate it before running ML-related scripts or the Flask service. On Windows with PowerShell: `.\venv\Scripts\Activate.ps1`

### Model Dependencies
- Crop model requires `Crop_recommendation.csv` in `ml-model/data/`
- Pest CNN requires image dataset in `ml-model/data/pest_dataset/` organized as subdirectories per class

### Backend-ML Communication
The backend uses two different methods to communicate with ML services:
1. **Crop prediction**: Spawns Python subprocess (predict.py) directly
2. **Pest detection**: Makes HTTP request to Flask API via axios

### Frontend API Configuration
The frontend API base URL is configurable via `REACT_APP_API_URL` environment variable (in `frontend/.env`). Defaults to http://localhost:5000.

### File Uploads
Pest detection accepts image uploads via multipart/form-data. Backend uses multer to handle uploads (temporary storage in `backend/uploads/`), then forwards to Flask API.

## Common Patterns

### Adding a New ML Model
1. Create training script in `ml-model/`
2. Save trained model to `ml-model/models/`
3. Add prediction endpoint in `ml-model/app.py`
4. Create route in `backend/routes/` to proxy or call the model
5. Add frontend service function in `frontend/src/api/api.js`
6. Update relevant page component

### Adding a New Page
1. Create page component in `frontend/src/pages/`
2. Add route in `frontend/src/App.jsx`
3. Update navigation in `frontend/src/components/Navbar.jsx`

### MongoDB Models
All Mongoose schemas are in `backend/models/`. Use ES6 module syntax (import/export) since `package.json` has `"type": "module"`.
