# New Features Added

## 1. **User Authentication (Sign Up / Sign In)**

### How It Works:
- Users must **Sign Up** or **Login** before accessing the dashboard
- Accounts are stored securely with hashed passwords
- Each login generates a unique authentication token

### How to Use:

**Sign Up (New User):**
1. Click the **Login** button in the top-right of the navbar
2. Click "Sign Up" link
3. Enter Username, Email, and Password
4. Click **Sign Up**
5. Dashboard loads automatically

**Login (Existing User):**
1. Click the **Login** button in the top-right
2. Enter Username and Password
3. Click **Login**
4. Dashboard loads automatically

**Logout:**
- Click the **Logout** button in the top-right (visible when logged in)

---

## 2. **Light/Dark Mode Toggle**

### How It Works:
- Toggle between light mode and dark mode
- Theme preference is saved in browser storage
- All UI elements adjust colors automatically

### How to Use:
1. Click the **Moon/Sun icon** (☀️/🌙) in the navbar
2. The theme switches immediately
3. Your preference is saved for next time

---

## 3. **Upload Custom Data for Forecasting**

### How It Works:
- Users can upload their own CSV file with sales data
- The system retrains the models with the new data
- Generates 90-day forecasts based on uploaded data

### CSV File Requirements:
- **Must contain at least two columns:**
  - `Date` - the date of the sales (any standard date format)
  - `Sales` - the sales amount (numeric value)

### Example CSV Format:
```
Date,Sales
2023-01-01,1500
2023-01-02,1620
2023-01-03,1480
2023-01-04,2100
...
```

### How to Use:
1. **Click the upload area** in the "Upload Custom Data" section
   - OR drag and drop a CSV file onto it
2. Select your CSV file from your computer
3. Wait for the file to be processed (30-60 seconds)
4. Success message appears and dashboard updates with new data
5. Charts and metrics update with your data

---

## 4. **Two Ways to Load Data**

### Option A: Initialize with Demo Data
- Click **"Initialize System"** button
- Uses synthetic sales data for demonstration
- Great for testing the forecasting features

### Option B: Upload Your Own Data
- Use the **"Upload Custom Data"** area
- Drag and drop (or click to select) your CSV file
- System trains models on your actual data
- Perfect for real-world forecasting

---

## Backend Changes

### New API Endpoints:

**Authentication Endpoints:**
- `POST /api/auth/signup` - Create new account
- `POST /api/auth/login` - Login with credentials
- `POST /api/auth/logout` - Logout (requires token)

**Data Upload:**
- `POST /api/upload-csv` - Upload CSV for custom forecasting (requires token)

**All existing endpoints now require authentication:**
- Requests must include header: `Authorization: Bearer <token>`

### User Storage:
- User accounts saved in `users.json` file
- Passwords hashed with SHA-256
- Tokens generated for secure session management

---

## Frontend Changes

### New UI Components:
- **Login/Signup Modal** - Professional authentication form
- **Theme Toggle** - Moon/Sun icon in navbar
- **File Upload Area** - Drag-and-drop file upload zone
- **User Display** - Shows logged-in username
- **Logout Button** - Appears when logged in

### CSS Enhancements:
- **Dark Mode** - Complete dark theme with CSS variables
- **Responsive Design** - Works on mobile and desktop
- **Dark Mode Persistence** - Saves theme preference

---

## How to Run the Updated Application

### Step 1: Install Dependencies
```bash
pip install flask flask-cors numpy pandas matplotlib seaborn scikit-learn statsmodels
```

### Step 2: Start Backend
```bash
cd backend
python app.py
```
(Runs on http://localhost:5000)

### Step 3: Start Frontend
```bash
cd frontend
python -m http.server 3000
```
(Runs on http://localhost:3000)

### Step 4: Open Dashboard
- Go to http://localhost:3000
- Sign up for a new account (or use any username/password for demo)
- Choose to Initialize System or Upload Custom Data
- View forecasts and insights

---

## Test Accounts

Since the app is demo-only, you can create any account:

**Example:**
- Username: `demo`
- Password: `demo123`
- Email: `demo@example.com`

(Or use any other credentials you prefer)

---

## Features Summary

| Feature | Status | Details |
|---------|--------|---------|
| User Authentication | ✅ Real Sign Up/Login | Secure JWT-based tokens |
| Dark Mode | ✅ Working | Toggle anytime, saves preference |
| CSV Upload | ✅ Working | Upload Date + Sales columns |
| Demo Data | ✅ Working | Initialize with synthetic data |
| Sales Forecasting | ✅ Working | 90-day predictions with confidence intervals |
| Model Comparison | ✅ Working | Random Forest vs SARIMA |
| Business Insights | ✅ Working | Recommendations based on data |
| Responsive Design | ✅ Working | Mobile and desktop friendly |

---

## API Documentation

### User Registration
**Endpoint:** `POST /api/auth/signup`

**Request:**
```json
{
  "username": "newuser",
  "password": "securepassword",
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "status": "success",
  "token": "generated_auth_token",
  "username": "newuser"
}
```

### User Login
**Endpoint:** `POST /api/auth/login`

**Request:**
```json
{
  "username": "newuser",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "status": "success",
  "token": "generated_auth_token",
  "username": "newuser"
}
```

### File Upload
**Endpoint:** `POST /api/upload-csv`

**Headers:**
```
Authorization: Bearer <your_token>
```

**Request:**
- Multipart form data with file
- File must be CSV format

**Response:**
```json
{
  "status": "success",
  "message": "Data uploaded and models trained successfully",
  "data_shape": [365, 12],
  "date_range": ["2023-01-01", "2023-12-31"]
}
```

---

## Troubleshooting

**Login not working?**
- Make sure backend is running on port 5000
- Check browser console for errors

**File upload fails?**
- Ensure CSV has "Date" and "Sales" columns
- Make sure you're logged in

**Dark mode not saving?**
- Check if browser allows localStorage
- Try clearing browser cache

**Forecasts not showing?**
- Click "Initialize System" or upload data first
- Wait for processing to complete (30-60 seconds)

---

## Notes

- All user data is stored locally in `backend/users.json`
- This is a demo app - suitable for testing and learning
- For production use, consider: database storage, JWT expiration, password requirements
- Token-based authentication prevents unauthorized API access
