# 🎯 Smart Product Finder - Complete Setup Guide

## ✅ What Was Implemented

The **Smart Product Finder** feature is now fully integrated into your DealGoat project! It's an AI-powered product recommendation system that:

- **Accepts detailed requirements** from users (battery life, gaming capability, budget, etc.)
- **Uses LLM (GROQ API)** to understand and parse requirements
- **Web scrapes** Amazon.in and Flipkart.com for real products
- **Ranks products** using AI based on user needs
- **Returns direct product links** with prices and ratings
- **Stores search history** for users

---

## 🚀 QUICK START (5 Steps)

### **Step 1: Get GROQ API Key (2 minutes)**

1. Go to: https://console.groq.com/keys
2. Sign up with Google/GitHub (FREE)
3. Copy your API key
4. Update `backend/.env`:
   ```
   GROQ_API_KEY=paste_your_key_here
   ```

### **Step 2: Install Python Dependencies (2 minutes)**

```bash
cd backend
pip install -r requirements.txt
```

**New packages added:**
- `groq==0.4.0` - LLM API client
- `beautifulsoup4==4.12.0` - Web scraping
- `requests==2.31.0` - HTTP requests
- `selenium==4.13.0` - Dynamic scraping

### **Step 3: Run Django Migrations (1 minute)**

```bash
cd backend
python manage.py makemigrations recommendations
python manage.py migrate
```

### **Step 4: Start Django Backend**

```bash
cd backend
python manage.py runserver
```

Expected output:
```
Starting development server at http://127.0.0.1:8000/
```

### **Step 5: Start React Frontend**

```bash
cd DealGoat (root folder)
npm start
```

---

## 🎨 Features Added

### **1. Smart Product Finder Page**
- **Route:** `/smart-finder`
- **Location:** `src/pages/SmartProductFinder.jsx`
- **Features:**
  - Detailed text input for requirements
  - AI parsing of requirements
  - Web scraping from Amazon & Flipkart
  - Top 5 product recommendations
  - Match score visualization
  - Direct "Buy Now" links
  - Search history sidebar

### **2. Updated UserHomePage**
- **New card:** "Smart Product Finder" feature
- **New quick action button:** "Find Best Products"
- **Color:** Yellow/Orange gradient

### **3. Backend API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/recommendations/find-products/` | POST | Find products based on requirements |
| `/api/recommendations/query-history/` | GET | Get user's search history |
| `/api/recommendations/query-detail/<id>/` | GET | Get details of a specific search |

---

## 📊 Database Models

### **RequirementQuery**
```python
- id (Primary Key)
- user (Foreign Key)
- requirements_text (TextField)
- parsed_requirements (JSONField)
- results (JSONField)
- created_at (DateTime)
- updated_at (DateTime)
```

### **ProductResult**
```python
- id (Primary Key)
- query (Foreign Key to RequirementQuery)
- rank (IntegerField)
- product_name (CharField)
- brand (CharField)
- price (IntegerField)
- amazon_link (URLField)
- flipkart_link (URLField)
- product_image (URLField)
- match_score (FloatField)
- match_reasons (JSONField)
- rating (FloatField)
- reviews_count (IntegerField)
```

---

## 🔧 How It Works

### **User Flow:**

```
1. User enters requirements:
   "I need laptop with best battery, gaming, ₹80k budget, lightweight"
   
   ↓
   
2. LLM (GROQ) parses requirements:
   {
     "device_type": "laptop",
     "budget_max": 80000,
     "must_have_features": ["gaming", "battery"],
     "performance_tier": "mid"
   }
   
   ↓
   
3. Generate search queries:
   - "best gaming laptop battery 80000"
   - "lightweight gaming laptop"
   - "gaming laptop 80k budget"
   
   ↓
   
4. Web scraper searches:
   - Amazon.in results
   - Flipkart.com results
   
   ↓
   
5. LLM ranks products based on match score
   
   ↓
   
6. Return top 5 with:
   - Product name & price
   - Amazon/Flipkart links
   - Match reasons
   - Customer ratings
```

---

## 🐛 Troubleshooting

### **Issue: GROQ API Key Error**
```
Error: GROQ_API_KEY environment variable not set
```
**Solution:**
1. Get API key from https://console.groq.com/keys
2. Add to `backend/.env`: `GROQ_API_KEY=your_key`
3. Restart Django

### **Issue: 404 on `/smart-finder` page**
```
Page not found
```
**Solution:**
1. Make sure `App.jsx` has the route
2. Restart React frontend

### **Issue: Web scraper returns no results**
```
"No products found"
```
**Solution:**
1. Check internet connection
2. Amazon/Flipkart may have changed HTML structure
3. Update selectors in `backend/recommendations/scrapers.py`

### **Issue: CORS Error**
```
Access to XMLHttpRequest blocked by CORS policy
```
**Solution:**
Already configured in `settings.py`, but if issues persist:
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',
    'http://127.0.0.1:3000',
]
```

---

## 📝 API Examples

### **Find Products Request**
```bash
curl -X POST http://localhost:8000/api/recommendations/find-products/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "I need a gaming laptop with 12+ hour battery under ₹80,000"
  }'
```

### **Response**
```json
{
  "success": true,
  "message": "Found best products matching your needs",
  "query": {
    "id": 1,
    "requirements_text": "I need a gaming laptop...",
    "parsed_requirements": {
      "device_type": "laptop",
      "budget_max": 80000,
      "must_have_features": ["gaming", "battery"],
      "performance_tier": "mid"
    },
    "products": [
      {
        "id": 1,
        "rank": 1,
        "product_name": "ASUS TUF Gaming F15",
        "brand": "ASUS",
        "price": 78000,
        "amazon_link": "https://amazon.in/...",
        "flipkart_link": "https://flipkart.com/...",
        "match_score": 87.5,
        "match_reasons": [
          "RTX 3050 Ti for gaming",
          "12.5 hour battery life",
          "Within budget"
        ],
        "rating": 4.5,
        "reviews_count": 245
      }
    ]
  }
}
```

---

## 🚀 Advanced Features (Optional)

### **1. Add Email Notifications**
When a product price drops, email users.

```python
# In recommendations/tasks.py
from celery import shared_task
import requests

@shared_task
def check_price_drops():
    # Periodically check Amazon/Flipkart for price changes
    pass
```

### **2. Add User Preferences**
Save favorite brands/features for personalized recommendations.

### **3. Add Price History Tracking**
Track price changes over time.

### **4. Add ML Model Integration**
Use your existing laptop/phone prediction models to rank products.

---

## 📚 File Structure

```
backend/
├── recommendations/          # NEW APP
│   ├── __init__.py
│   ├── models.py            # Database models
│   ├── views.py             # API endpoints
│   ├── serializers.py       # API serializers
│   ├── llm_service.py       # GROQ LLM integration
│   ├── scrapers.py          # Web scraping logic
│   ├── urls.py              # API routes
│   ├── admin.py             # Django admin
│   ├── apps.py              # App config
│   └── migrations/
│       └── __init__.py

frontend/
src/
├── pages/
│   └── SmartProductFinder.jsx  # NEW PAGE
└── App.jsx                      # UPDATED (new route)
```

---

## ✨ Testing the Feature

### **Test in Frontend:**

1. Go to http://localhost:3000/user-home
2. Click **"Find Best Products"** button
3. Enter: `I need a gaming laptop with best battery, RTX 3050, ₹80,000 budget, under 2kg weight`
4. Click **"Find Best Products"**
5. Wait 10-15 seconds for results
6. You should see top 5 products with Amazon/Flipkart links

### **Test in Django Admin:**

1. Go to http://localhost:8000/admin
2. Login with Django admin credentials
3. Navigate to **Recommendations** > **Requirement Queries**
4. View search history and results

---

## 🔐 Security & Best Practices

### **1. Rate Limiting**
```python
# Add to settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

### **2. Scraper Delays**
- Added 0.5s delay between scraper requests
- User-Agent headers to avoid blocking
- Error handling for failed requests

### **3. GROQ API Limits**
- Free tier: 100 requests/day
- Upgrade to paid for higher limits
- Implement caching for repeated queries

---

## 📞 Support

If you encounter issues:

1. **Check logs:**
   ```bash
   # Django logs
   tail -f backend.log
   
   # Browser console (F12)
   ```

2. **Common fixes:**
   ```bash
   # Clear migrations
   find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
   
   # Fresh database
   python manage.py migrate --run-syncdb
   ```

3. **Test endpoint directly:**
   ```bash
   # Using Python
   import requests
   response = requests.post('http://localhost:8000/api/recommendations/find-products/',
     headers={'Authorization': 'Bearer YOUR_TOKEN'},
     json={'requirements': 'gaming laptop under 80000'}
   )
   print(response.json())
   ```

---

## 🎉 You're All Set!

Your Smart Product Finder is now live! Users can:
- ✅ Enter detailed requirements
- ✅ Get AI-powered recommendations
- ✅ See direct Amazon/Flipkart links
- ✅ View search history
- ✅ Make informed buying decisions

**Happy coding! 🚀**
