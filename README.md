# Crop Recommendation & Pest Detection Application

A full-stack agricultural application using ML for crop recommendations and pest detection.

## Prerequisites

- Node.js (for frontend & backend)
- Python 3.x (for ML service)
- MongoDB (local or cloud instance)

## Setup

### 1. Install Dependencies

```powershell
# Frontend
cd frontend
npm install

# Backend
cd backend
npm install

# Python ML Service
cd ml-model
pip install flask flask-cors numpy pandas scikit-learn tensorflow pillow
```

### 2. Configure Environment Variables

**Backend** (`backend/.env`):
```
MONGO_URI=your_mongodb_connection_string
PORT=5000
```

**Frontend** (`frontend/.env`):
```
REACT_APP_API_URL=http://localhost:5000
```

## Running the Application

You need to run **3 services** in separate terminals:

### Terminal 1: ML Service (Flask) - Port 5001

```powershell
cd ml-model
..\venv\Scripts\Activate.ps1
python app.py
```

Or use the startup script:
```powershell
cd ml-model
.\start-ml-service.ps1
```

### Terminal 2: Backend (Express) - Port 5000

```powershell
cd backend
npm run dev
```

### Terminal 3: Frontend (React) - Port 3000

```powershell
cd frontend
npm start
```

## Accessing the Application

Once all services are running:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- ML Service: http://localhost:5001

## Features

- **Crop Recommendation**: Input soil parameters (N, P, K) and environmental data (temperature, humidity, pH, rainfall) to get crop recommendations
- **Pest Detection**: Upload images of tomato leaves to detect diseases
- **Weather Information**: View weather data for agricultural planning
- **Advisory Services**: Get farming advice and pest management tips

## Troubleshooting

### Pest Detection Not Working?

Make sure:
1. Flask ML service is running on port 5001
2. Check the terminal running Flask for error messages
3. Ensure the model file exists: `ml-model/models/pest_cnn_model.h5`
4. Pest dataset exists: `ml-model/data/pest_dataset/`

### Backend Connection Issues?

1. Verify MongoDB is running and `MONGO_URI` is correct
2. Check that port 5000 is not in use by another application

## Tech Stack

- **Frontend**: React, TailwindCSS, React Router, Framer Motion, Recharts
- **Backend**: Node.js, Express, MongoDB, Mongoose
- **ML Service**: Flask, scikit-learn, TensorFlow/Keras
