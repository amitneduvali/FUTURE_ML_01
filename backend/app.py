"""
Sales Forecasting API - Backend
Flask-based REST API for sales forecasting functionality
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import json
import os
import hashlib
import secrets
from functools import wraps
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Global variables to store models and data
rf_model = None
sarima_model = None
df = None
daily_sales_ts = None
forecast_df = None
user_data_store = {}
users_file = 'users.json'

# Load users from file
def load_users():
    global user_data_store
    if os.path.exists(users_file):
        try:
            with open(users_file, 'r') as f:
                user_data_store = json.load(f)
        except:
            user_data_store = {}
    return user_data_store

# Save users to file
def save_users():
    with open(users_file, 'w') as f:
        json.dump(user_data_store, f, indent=4)

# Load users on startup
load_users()

# Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Token generation
def generate_token():
    return secrets.token_urlsafe(32)

# Token validation decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'status': 'error', 'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'status': 'error', 'message': 'Token is missing'}), 401
        
        # Check if token exists and is valid
        user_found = False
        for user, data in user_data_store.items():
            if data.get('token') == token:
                request.current_user = user
                user_found = True
                break
        
        if not user_found:
            return jsonify({'status': 'error', 'message': 'Token is invalid'}), 401
        
        return f(*args, **kwargs)
    return decorated

def generate_sales_data(start_date, end_date, num_products=5, num_stores=3):
    """Generate synthetic sales data"""
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    products = [f'Product_{i+1}' for i in range(num_products)]
    stores = [f'Store_{i+1}' for i in range(num_stores)]

    data = []
    for date in dates:
        for product in products:
            for store in stores:
                base_price = np.random.uniform(10, 100)
                month = date.month
                seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * month / 12)
                weekday = date.weekday()
                weekly_factor = 1.2 if weekday >= 5 else 1.0
                demand_noise = np.random.normal(0, 0.1)

                base_demand = np.random.poisson(50)
                demand = int(base_demand * seasonal_factor * weekly_factor * (1 + demand_noise))
                demand = max(0, demand)

                price = base_price * (1 + np.random.normal(0, 0.05))
                sales = min(demand, np.random.poisson(demand * 0.8))

                data.append({
                    'Date': date,
                    'Product': product,
                    'Store': store,
                    'Price': round(price, 2),
                    'Demand': demand,
                    'Sales': sales
                })

    return pd.DataFrame(data)

def preprocess_data(df):
    """Preprocess the data"""
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').reset_index(drop=True)

    # Remove outliers - only for columns that exist
    def remove_outliers(df, column):
        if column not in df.columns:
            return df
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

    df = remove_outliers(df, 'Sales')

    # Time-based features
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    df['Weekday'] = df['Date'].dt.weekday
    df['Is_Weekend'] = df['Weekday'].isin([5, 6]).astype(int)
    df['Quarter'] = df['Date'].dt.quarter

    def get_season(month):
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Fall'

    df['Season'] = df['Month'].apply(get_season)
    return df

def train_models(df):
    """Train both Random Forest and SARIMA models"""
    global rf_model, sarima_model, daily_sales_ts

    # Prepare data for Random Forest
    # Handle case where Product/Store columns may not exist
    columns_to_encode = []
    for col in ['Product', 'Store', 'Season']:
        if col in df.columns:
            columns_to_encode.append(col)
    
    if columns_to_encode:
        df_encoded = pd.get_dummies(df, columns=columns_to_encode, drop_first=True)
    else:
        df_encoded = df.copy()
    
    # Build features list - only include columns that exist
    available_features = ['Year', 'Month', 'Day', 'Weekday', 'Is_Weekend', 'Quarter']
    features = [col for col in available_features if col in df_encoded.columns]
    
    # Add encoded categorical features
    features += [col for col in df_encoded.columns if col.startswith(('Product_', 'Store_', 'Season_'))]

    X = df_encoded[features]
    y = df_encoded['Sales']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train Random Forest
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)

    # Prepare time series data
    daily_sales_ts = df.groupby('Date')['Sales'].sum().reset_index()
    daily_sales_ts.set_index('Date', inplace=True)

    train_size = int(len(daily_sales_ts) * 0.8)
    train_ts = daily_sales_ts[:train_size]

    # Train SARIMA
    sarima_model = SARIMAX(train_ts, order=(1, 1, 1), seasonal_order=(1, 1, 1, 7))
    sarima_model = sarima_model.fit(disp=False)

    return X_test, y_test, train_ts

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User signup endpoint"""
    global user_data_store
    
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email', '')
    
    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Username and password required'}), 400
    
    if username in user_data_store:
        return jsonify({'status': 'error', 'message': 'User already exists'}), 400
    
    # Create new user
    token = generate_token()
    user_data_store[username] = {
        'password': hash_password(password),
        'email': email,
        'token': token,
        'created_at': datetime.now().isoformat()
    }
    
    save_users()
    
    return jsonify({
        'status': 'success',
        'message': 'User created successfully',
        'token': token,
        'username': username
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    global user_data_store
    
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Username and password required'}), 400
    
    if username not in user_data_store:
        return jsonify({'status': 'error', 'message': 'Invalid username or password'}), 401
    
    user = user_data_store[username]
    if user['password'] != hash_password(password):
        return jsonify({'status': 'error', 'message': 'Invalid username or password'}), 401
    
    # Generate new token
    token = generate_token()
    user['token'] = token
    save_users()
    
    return jsonify({
        'status': 'success',
        'message': 'Login successful',
        'token': token,
        'username': username
    }), 200

@app.route('/api/auth/logout', methods=['POST'])
@token_required
def logout():
    """User logout endpoint"""
    global user_data_store
    
    user = request.current_user
    user_data_store[user]['token'] = None
    save_users()
    
    return jsonify({
        'status': 'success',
        'message': 'Logged out successfully'
    }), 200

# ==================== DATA UPLOAD ENDPOINT ====================

@app.route('/api/upload-csv', methods=['POST'])
@token_required
def upload_csv():
    """Upload custom CSV data for forecasting"""
    global df, rf_model, sarima_model, daily_sales_ts, forecast_df
    
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected'}), 400
    
    try:
        # Try reading CSV with multiple encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-16', 'gb2312']
        df = None
        encoding_used = None
        
        for encoding in encodings:
            try:
                file.seek(0)
                df = pd.read_csv(file, encoding=encoding)
                encoding_used = encoding
                break
            except (UnicodeDecodeError, LookupError):
                continue
        
        if df is None:
            return jsonify({
                'status': 'error', 
                'message': 'Could not read CSV file. Try converting to UTF-8 first.'
            }), 400
        
        # Normalize column names
        df.columns = df.columns.str.strip()
        
        # Find Date and Sales columns
        date_col = None
        sales_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if 'date' in col_lower and date_col is None:
                date_col = col
            if 'sales' in col_lower and sales_col is None:
                sales_col = col
        
        if date_col is None or sales_col is None:
            missing = []
            if date_col is None:
                missing.append("Date (or *Date column)")
            if sales_col is None:
                missing.append("Sales")
            return jsonify({
                'status': 'error', 
                'message': f'CSV missing required columns: {", ".join(missing)}'
            }), 400
        
        # Rename columns to standard names
        df.rename(columns={date_col: 'Date', sales_col: 'Sales'}, inplace=True)
        df = df[['Date', 'Sales']].copy()
        
        # Quick preprocessing
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date').reset_index(drop=True)
        
        return jsonify({
            'status': 'success',
            'message': '✅ File uploaded successfully!',
            'data_shape': list(df.shape),
            'date_range': [str(df['Date'].min().date()), str(df['Date'].max().date())],
            'total_records': len(df)
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500

@app.route('/api/generate-forecast', methods=['POST'])
@token_required
def generate_forecast():
    """Generate forecast from uploaded data"""
    global df, rf_model, sarima_model, daily_sales_ts, forecast_df
    
    if df is None or df.empty:
        return jsonify({'status': 'error', 'message': 'No data uploaded yet'}), 400
    
    try:
        # Preprocess
        df_processed = preprocess_data(df.copy())
        
        # Train models
        X_test, y_test, train_ts = train_models(df_processed)
        
        # Generate forecast
        forecast_steps = 90
        forecast = sarima_model.get_forecast(steps=forecast_steps)
        forecast_values = forecast.predicted_mean
        forecast_ci = forecast.conf_int()
        
        last_date = daily_sales_ts.index[-1]
        forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_steps, freq='D')
        
        forecast_df = pd.DataFrame({
            'Date': forecast_dates,
            'Forecasted_Sales': forecast_values.values,
            'Lower_CI': forecast_ci.iloc[:, 0].values,
            'Upper_CI': forecast_ci.iloc[:, 1].values
        })
        
        return jsonify({
            'status': 'success',
            'message': 'Forecast generated successfully!'
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error generating forecast: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Sales Forecasting API is running'})

@app.route('/api/initialize', methods=['POST'])
@token_required
def initialize_data():
    """Initialize the dataset and train models"""
    global df, rf_model, sarima_model, forecast_df

    try:
        # Generate data
        start_date = '2022-01-01'
        end_date = '2023-12-31'
        df = generate_sales_data(start_date, end_date)

        # Preprocess
        df = preprocess_data(df)

        # Train models
        X_test, y_test, train_ts = train_models(df)

        # Generate forecast
        forecast_steps = 90
        forecast = sarima_model.get_forecast(steps=forecast_steps)
        forecast_values = forecast.predicted_mean
        forecast_ci = forecast.conf_int()

        last_date = daily_sales_ts.index[-1]
        forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_steps, freq='D')

        forecast_df = pd.DataFrame({
            'Date': forecast_dates,
            'Forecasted_Sales': forecast_values.values,
            'Lower_CI': forecast_ci.iloc[:, 0].values,
            'Upper_CI': forecast_ci.iloc[:, 1].values
        })

        return jsonify({
            'status': 'success',
            'message': 'Data initialized and models trained',
            'data_shape': df.shape,
            'date_range': [str(df['Date'].min()), str(df['Date'].max())]
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/historical-data', methods=['GET'])
@token_required
def get_historical_data():
    """Get historical sales data"""
    if df is None:
        return jsonify({'status': 'error', 'message': 'Data not initialized'}), 400

    # Aggregate daily sales
    daily_sales = df.groupby('Date')['Sales'].sum().reset_index()
    data = {
        'dates': [str(date) for date in daily_sales['Date']],
        'sales': daily_sales['Sales'].tolist()
    }

    return jsonify({'status': 'success', 'data': data})

@app.route('/api/forecast', methods=['GET'])
@token_required
def get_forecast():
    """Get sales forecast"""
    if forecast_df is None:
        return jsonify({'status': 'error', 'message': 'Forecast not available'}), 400

    data = {
        'dates': [str(date) for date in forecast_df['Date']],
        'forecasted_sales': forecast_df['Forecasted_Sales'].tolist(),
        'lower_ci': forecast_df['Lower_CI'].tolist(),
        'upper_ci': forecast_df['Upper_CI'].tolist()
    }

    return jsonify({'status': 'success', 'data': data})

@app.route('/api/metrics', methods=['GET'])
@token_required
def get_metrics():
    """Get model performance metrics"""
    if rf_model is None or sarima_model is None:
        return jsonify({'status': 'error', 'message': 'Models not trained'}), 400

    try:
        # Calculate metrics
        df_encoded = pd.get_dummies(df, columns=['Product', 'Store', 'Season'], drop_first=True)
        features = ['Price', 'Year', 'Month', 'Day', 'Weekday', 'Is_Weekend', 'Quarter'] + \
                   [col for col in df_encoded.columns if col.startswith(('Product_', 'Store_', 'Season_'))]

        X = df_encoded[features]
        y = df_encoded['Sales']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        rf_predictions = rf_model.predict(X_test)
        rf_mae = mean_absolute_error(y_test, rf_predictions)
        rf_rmse = np.sqrt(mean_squared_error(y_test, rf_predictions))

        # SARIMA metrics
        train_size = int(len(daily_sales_ts) * 0.8)
        test_ts = daily_sales_ts[train_size:]
        sarima_predictions = sarima_model.predict(start=test_ts.index[0], end=test_ts.index[-1])
        sarima_mae = mean_absolute_error(test_ts['Sales'], sarima_predictions)
        sarima_rmse = np.sqrt(mean_squared_error(test_ts['Sales'], sarima_predictions))

        metrics = {
            'random_forest': {
                'mae': round(rf_mae, 2),
                'rmse': round(rf_rmse, 2)
            },
            'sarima': {
                'mae': round(sarima_mae, 2),
                'rmse': round(sarima_rmse, 2)
            }
        }

        return jsonify({'status': 'success', 'metrics': metrics})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/business-insights', methods=['GET'])
@token_required
def get_business_insights():
    """Get business insights"""
    if df is None:
        return jsonify({'status': 'error', 'message': 'Data not initialized'}), 400

    try:
        # Calculate insights
        total_sales = df['Sales'].sum()
        avg_daily_sales = df.groupby('Date')['Sales'].sum().mean()

        seasonal_sales = df.groupby('Season')['Sales'].mean().reindex(['Winter', 'Spring', 'Summer', 'Fall'])
        peak_season = seasonal_sales.idxmax()
        low_season = seasonal_sales.idxmin()

        store_sales = df.groupby('Store')['Sales'].sum()
        product_sales = df.groupby('Product')['Sales'].sum()
        best_store = store_sales.idxmax()
        best_product = product_sales.idxmax()

        weekend_boost = df[df['Is_Weekend'] == 1]['Sales'].mean() / df[df['Is_Weekend'] == 0]['Sales'].mean() - 1

        insights = {
            'total_sales': int(total_sales),
            'avg_daily_sales': round(avg_daily_sales, 2),
            'peak_season': peak_season,
            'low_season': low_season,
            'best_store': best_store,
            'best_product': best_product,
            'weekend_boost': round(weekend_boost * 100, 1)
        }

        return jsonify({'status': 'success', 'insights': insights})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/chart/<chart_type>', methods=['GET'])
@token_required
def get_chart(chart_type):
    """Generate and return chart as base64 image"""
    if df is None:
        return jsonify({'status': 'error', 'message': 'Data not initialized'}), 400

    try:
        plt.figure(figsize=(10, 6))

        if chart_type == 'sales_trend':
            daily_sales = df.groupby('Date')['Sales'].sum().reset_index()
            plt.plot(daily_sales['Date'], daily_sales['Sales'])
            plt.title('Daily Sales Trend')
            plt.xlabel('Date')
            plt.ylabel('Sales')
            plt.xticks(rotation=45)

        elif chart_type == 'seasonal':
            seasonal_sales = df.groupby('Season')['Sales'].mean().reindex(['Winter', 'Spring', 'Summer', 'Fall'])
            seasonal_sales.plot(kind='bar')
            plt.title('Average Sales by Season')
            plt.xlabel('Season')
            plt.ylabel('Average Sales')

        elif chart_type == 'forecast':
            if forecast_df is not None:
                daily_sales = df.groupby('Date')['Sales'].sum().reset_index()
                plt.plot(daily_sales['Date'][-180:], daily_sales['Sales'][-180:], label='Historical')
                plt.plot(forecast_df['Date'], forecast_df['Forecasted_Sales'], label='Forecast', color='red')
                plt.fill_between(forecast_df['Date'], forecast_df['Lower_CI'], forecast_df['Upper_CI'],
                               color='red', alpha=0.2, label='95% CI')
                plt.title('Sales Forecast')
                plt.xlabel('Date')
                plt.ylabel('Sales')
                plt.legend()
                plt.xticks(rotation=45)

        plt.tight_layout()

        # Convert plot to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()

        return jsonify({'status': 'success', 'image': image_base64})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint - returns API info"""
    return jsonify({
        'status': 'success',
        'message': 'Sales Forecasting API is running',
        'endpoints': {
            'health': '/api/health',
            'initialize': '/api/initialize (POST)',
            'history': '/api/historical-data',
            'forecast': '/api/forecast',
            'metrics': '/api/metrics',
            'insights': '/api/business-insights',
            'charts': '/api/chart/<chart_type>'
        }
    })

if __name__ == '__main__':
    print("Starting Sales Forecasting API...")
    print("API will be available at: http://localhost:5000")
    print("Open http://localhost:5000/api/health to test")
    app.run(debug=True, host='0.0.0.0', port=5000)