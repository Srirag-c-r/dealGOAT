# DealGoat Project Guide

## 1. Project Overview
**DealGoat** is an intelligent e-commerce assistant application designed to help users find and evaluate electronic devices (Smartphones and Laptops). It combines a modern React frontend with a powerful Django backend that leverages Machine Learning (XGBoost) for price predictions and Large Language Models (Groq LLM) for natural language product recommendations.

## 2. Technology Stack

### Frontend
- **Framework:** React 18 (via Vite 5.0)
- **Styling:** Tailwind CSS 3.3, Vanilla CSS
- **Animations:** Framer Motion
- **Routing:** React Router DOM 6
- **HTTP Client:** Axios

### Backend
- **Framework:** Django 4.2.7
- **API:** Django REST Framework 3.14
- **Database:** PostgreSQL (Primary), SQLite (Legacy/Reference)
- **Machine Learning:** 
    - XGBoost, Scikit-learn, Pandas, NumPy (Price Prediction)
    - Groq API (LLM for Smart Product Finder)
- **Scraping/Data:** BeautifulSoup4, Selenium
- **Authentication:** Custom User Model, OTP (Email)
- **Configuration:** python-decouple (Environment Variables)

## 3. Project Structure

```
DealGoat/
├── backend/                    # Django Backend
│   ├── dealgoat/               # Project Settings (urls.py, settings.py)
│   ├── users/                  # App: User Authentication & Management
│   ├── predictions/            # App: Price Prediction Models & IMEI Service
│   │   ├── ml_models/          # Saved ML models (.pkl, .json)
│   │   ├── imei_service.py     # IMEI Lookup Service (In Progress)
│   │   └── ml_service.py       # Core prediction logic
│   ├── recommendations/        # App: Smart Product Finder & Recommendations
│   │   ├── llm_service.py      # Groq LLM integration
│   │   ├── scrapers.py         # Product data access/scraping
│   │   └── sidba_engine.py     # Ranking engine
│   ├── chatbot/                # App: Chatbot (Placeholder/Future)
│   ├── manage.py               # Django management script
│   └── requirements.txt        # Python dependencies
│
├── src/                        # React Frontend
│   ├── components/             # Reusable UI components
│   ├── pages/                  # Application views/routes
│   ├── services/               # API service layers
│   ├── App.jsx                 # Main component
│   └── main.jsx                # Entry point
│
├── public/                     # Static assets
└── package.json                # Frontend dependencies
```

## 4. Key Modules & Features

### A. Authentication (App: `users`)
- **Custom User Model**: Extends Django's AbstractUser.
- **OTP Verification**: Email-based OTP for secure actions.
- **Tokens**: DRF Token Authentication.

### B. Price Prediction (App: `predictions`)
- **Models**: Uses trained XGBoost models to predict device prices based on specs (RAM, Storage, Condition, etc.).
- **Smartphones & Laptops**: Separate models for different device categories.
- **IMEI Integration**: Currently implementing `imei_service.py` to fetch device details automatically via IMEI.

### C. Smart Product Finder (App: `recommendations`)
- **Natural Language Search**: Users can ask "Find me a gaming laptop under 70k".
- **LLM Processing**: Uses **Groq** to parse user intent (budget, usage, features).
- **Ranking Engine**: The "SIDBA" engine (and `ml_ranker.py`) scores products based on relevance to the parsed requirements.
- **Data Source**: Currently uses a curated list of products in `scrapers.py`.

### D. Brand Filtering & Dynamic Updates
- **Brand Awareness**: The system can filter recommendations by brand preferences.
- **Dynamic Updates**: Mechanisms to update product data (stubbed in `dynamic_product_manager.py`).

## 5. Setup & Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL

### Backend Setup
1. Additional Environment Setup:
   Ensure `backend/.env` is configured with:
   ```env
   SECRET_KEY=...
   DEBUG=True
   DB_NAME=dealgoat_db
   DB_USER=postgres
   DB_PASSWORD=...
   GROQ_API_KEY=...
   ```

2. Install Dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Database Migration:
   ```bash
   python manage.py migrate
   ```

4. Run Server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup
1. Install Dependencies:
   ```bash
   npm install
   ```

2. Run Development Server:
   ```bash
   npm run dev
   ```

## 6. Access Points
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin

## 7. Current Status & Known Issues
- **IMEI Service**: `backend/predictions/imei_service.py` is being worked on. Requires api integration.
- **Chatbot**: The `chatbot` directory is currently empty.
- **Database**: The project recently switched to PostgreSQL for better performance.
