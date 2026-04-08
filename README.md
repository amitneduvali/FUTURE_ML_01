# Sales & Demand Forecasting - Full Stack Application

A comprehensive sales forecasting system with both backend API and frontend dashboard.

## Project Structure

```
sales-forecasting-project/
├── backend/                 # Flask API backend
│   ├── app.py              # Main Flask application
│   └── requirements.txt    # Python dependencies
├── frontend/               # Web dashboard frontend
│   ├── index.html         # Main HTML page
│   └── app.js             # Frontend JavaScript logic
├── sales_forecasting.py    # Standalone Python script
├── synthetic_sales_data.csv # Generated dataset
├── dashboard_sales_forecast.csv # Forecast data for BI
└── dashboard_metrics.csv   # Key metrics for BI
```

## Features

### Backend API
- **Data Generation**: Synthetic retail sales data generation
- **Model Training**: Random Forest and SARIMA models
- **Forecasting**: 90-day sales predictions with confidence intervals
- **Metrics**: Model performance evaluation (MAE, RMSE)
- **Business Insights**: Key findings and recommendations

### Frontend Dashboard
- **Interactive Charts**: Sales trends, forecasts, and seasonal analysis
- **Real-time Metrics**: Key performance indicators
- **Model Comparison**: Performance metrics for both models
- **Business Insights**: Actionable recommendations

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js (optional, for serving frontend)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Flask API:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Serve the frontend (using Python's built-in server):
```bash
python -m http.server 3000
```

Or use any static file server. The frontend will be available at `http://localhost:3000`

## Usage

1. **Start the Backend**: Run the Flask API first
2. **Start the Frontend**: Open the dashboard in your browser
3. **Initialize System**: Click "Initialize System" to load data and train models
4. **Explore Dashboard**: View charts, metrics, and insights

## API Endpoints

### Core Endpoints
- `GET /api/health` - Health check
- `POST /api/initialize` - Initialize data and train models
- `GET /api/historical-data` - Get historical sales data
- `GET /api/forecast` - Get sales forecast
- `GET /api/metrics` - Get model performance metrics
- `GET /api/business-insights` - Get business insights

### Chart Endpoints
- `GET /api/chart/sales_trend` - Sales trend chart
- `GET /api/chart/seasonal` - Seasonal performance chart
- `GET /api/chart/forecast` - Forecast visualization

## Models Used

### Random Forest Regressor
- **Purpose**: Predict sales based on features (price, product, store, time)
- **Features**: Price, product/store dummies, time-based features
- **Use Case**: Product-specific or store-specific predictions

### SARIMA (Seasonal ARIMA)
- **Purpose**: Time series forecasting
- **Components**: Trend, seasonality, autoregression
- **Use Case**: Overall sales forecasting with seasonal patterns

## Business Insights

The system provides:
- **Seasonal Analysis**: Peak and low seasons
- **Performance Metrics**: Best products and stores
- **Demand Patterns**: Weekend vs weekday analysis
- **Inventory Recommendations**: When to stock up
- **Staffing Suggestions**: When to schedule more employees

## Data Description

### Synthetic Dataset
- **Time Period**: 2 years (2022-2023)
- **Products**: 5 different products
- **Stores**: 3 store locations
- **Features**: Date, Product, Store, Price, Demand, Sales
- **Records**: ~10,950 daily records

### Generated Features
- Time-based: Year, Month, Day, Weekday, Is_Weekend, Quarter, Season
- Categorical: Product/Store/Season dummies
- Derived: Seasonal factors, weekly patterns

## Deployment

### Local Development
1. Follow the setup instructions above
2. Both backend and frontend run locally

### Production Deployment
- **Backend**: Deploy Flask app to Heroku, AWS, or similar
- **Frontend**: Deploy static files to Netlify, Vercel, or similar
- **Database**: For production, consider PostgreSQL instead of in-memory data

## Technologies Used

### Backend
- **Flask**: Web framework
- **pandas**: Data manipulation
- **scikit-learn**: Machine learning
- **statsmodels**: Time series analysis
- **matplotlib/seaborn**: Visualization

### Frontend
- **HTML5/CSS3**: Structure and styling
- **Bootstrap**: UI framework
- **Chart.js**: Interactive charts
- **Vanilla JavaScript**: API communication

## Future Enhancements

- **Database Integration**: PostgreSQL for data persistence
- **User Authentication**: Login system for multiple users
- **Real-time Updates**: WebSocket for live data updates
- **Advanced Models**: LSTM, Prophet for better forecasting
- **External Data**: Weather, holidays, economic indicators
- **API Documentation**: Swagger/OpenAPI specs
- **Testing**: Unit and integration tests
- **Docker**: Containerization for easy deployment

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For questions or issues, please open an issue on the GitHub repository.