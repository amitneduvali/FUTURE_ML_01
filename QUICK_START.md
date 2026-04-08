# QUICK START GUIDE - Commands to Run

## Step 1: Install Dependencies (Run ONCE)
```bash
pip install flask flask-cors numpy pandas matplotlib seaborn scikit-learn statsmodels
```

## Step 2: Start the Backend (Terminal 1)
```bash
cd c:\Users\AMITH\OneDrive\Desktop\FutureIntern\backend
python app.py
```

You should see:
```
Starting Sales Forecasting API...
API will be available at: http://localhost:5000
WARNING in app.rtypes: "The Flask Development Server is not suitable for production...
 * Running on http://0.0.0.0:5000
```

## Step 3: Start the Frontend (Terminal 2)
```bash
cd c:\Users\AMITH\OneDrive\Desktop\FutureIntern\frontend
python -m http.server 3000
```

You should see:
```
Serving HTTP on 0.0.0.0 port 3000 (http://0.0.0.0:3000/)
```

## Step 4: Open Dashboard in Browser

Open your web browser and go to:
```
http://localhost:3000
```

## Step 5: Use the Dashboard

1. Click "Initialize System" button
2. Wait for data to load (30-60 seconds)
3. View charts, metrics, and insights automatically

---

## DETAILED INSTRUCTIONS

### First Time Setup

1. **Install all packages** (one time only):
```bash
pip install flask flask-cors numpy pandas matplotlib seaborn scikit-learn statsmodels
```

2. **Verify installation**:
```bash
python -c "import flask, pandas, sklearn, statsmodels; print('All packages installed!')"
```

### Running the Application

#### OPTION A: Automatic (Windows Batch File)
Simply double-click:
```
run_app.bat
```
This will automatically start both servers.

#### OPTION B: Manual (Recommended for Development)

**Terminal 1 - Backend**:
```bash
cd c:\Users\AMITH\OneDrive\Desktop\FutureIntern\backend
python app.py
```

**Terminal 2 - Frontend** (Open new terminal):
```bash
cd c:\Users\AMITH\OneDrive\Desktop\FutureIntern\frontend
python -m http.server 3000
```

**Terminal 3 - Open Browser** (Optional):
```bash
start http://localhost:3000
```

### Dashboard Usage (NO INPUTS NEEDED)

1. **Navigate to**: http://localhost:3000
2. **Click**: "Initialize System" button
   - This loads synthetic data
   - Trains both models
   - Generates forecast
3. **View automatically**:
   - Sales trends chart
   - Seasonal performance
   - Model metrics (MAE, RMSE)
   - Business insights
   - Recommendations

### Troubleshooting

**Problem**: "Can't reach server"
**Solution**: Check if both terminals are running

**Problem**: Port 5000 already in use
**Solution**: 
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Problem**: Module not found error
**Solution**: 
```bash
pip install <module_name>
```

**Problem**: Python not recognized
**Solution**: 
```bash
python --version
```

### What Each Terminal Does

| Terminal | Command | Purpose | URL |
|----------|---------|---------|-----|
| 1 | `python app.py` | Backend API Server | http://localhost:5000 |
| 2 | `python -m http.server 3000` | Frontend Dashboard | http://localhost:3000 |
| 3 | Open Browser | View Dashboard | http://localhost:3000 |

### API Endpoints (For Reference)

```
POST   http://localhost:5000/api/initialize        - Load data & train models
GET    http://localhost:5000/api/health            - Check if API is running
GET    http://localhost:5000/api/historical-data   - Get historical sales
GET    http://localhost:5000/api/forecast          - Get 90-day forecast
GET    http://localhost:5000/api/metrics           - Get model performance
GET    http://localhost:5000/api/business-insights - Get insights & recommendations
GET    http://localhost:5000/api/chart/<type>      - Get charts (sales_trend, seasonal, forecast)
```

### Example API Test

```bash
# Test if backend is running
curl http://localhost:5000/api/health

# Should return:
# {"status":"healthy","message":"Sales Forecasting API is running"}
```

---

## COMPLETE WORKFLOW

1. **Install** (do once):
   ```bash
   pip install flask flask-cors numpy pandas matplotlib seaborn scikit-learn statsmodels
   ```

2. **Terminal 1**:
   ```bash
   cd c:\Users\AMITH\OneDrive\Desktop\FutureIntern\backend
   python app.py
   ```

3. **Terminal 2**:
   ```bash
   cd c:\Users\AMITH\OneDrive\Desktop\FutureIntern\frontend
   python -m http.server 3000
   ```

4. **Browser**:
   Open http://localhost:3000

5. **Click**: "Initialize System"

6. **Wait**: 30-60 seconds for models to train

7. **Explore**: Charts, metrics, and insights appear automatically

---

## NO USER INPUT REQUIRED AFTER INITIALIZATION

The dashboard is fully automated. Just click "Initialize" and all data, models, and visualizations are generated automatically.
