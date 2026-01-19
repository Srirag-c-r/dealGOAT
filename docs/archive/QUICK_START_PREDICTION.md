# ⚡ Quick Start - Laptop Prediction

## 🚀 3-Step Setup

### Step 1: Install ML Libraries (2 minutes)
```bash
cd C:\SEM4PROJECT\DealGoat\backend
.\venv\Scripts\activate
pip install pandas numpy scikit-learn
```

### Step 2: Train Model (5 minutes)
```bash
python predictions/train_laptop_model.py
```
**Wait for:**
```
🎉 MODEL TRAINING COMPLETE!
```

### Step 3: Run Migrations (1 minute)
```bash
python manage.py makemigrations predictions
python manage.py migrate
```

---

## 🏃 Run the Application

### Terminal 1 - Backend:
```bash
cd C:\SEM4PROJECT\DealGoat\backend
python manage.py runserver
```
**Wait for:** `✅ Laptop models loaded successfully`

### Terminal 2 - Frontend:
```bash
cd C:\SEM4PROJECT\DealGoat
npm run dev
```

---

## 🧪 Test It!

1. Open: `http://localhost:5173`
2. Login
3. Go to: `http://localhost:5173/predictions/laptop`
4. Fill form
5. Get prediction! 🎉

---

## 📝 Sample Test Data

```
Brand: HP
Model: Pavilion 15
Launch Year: 2022
Launch Price: ₹65000
Processor: Intel Core i5
GPU: NVIDIA GeForce GTX 1650
RAM: 16 GB
Storage Type: SSD
Storage Size: 512 GB
Screen Size: 15.6"
Condition: Good
Warranty: 12 months
Battery Cycles: 150
Location: Mumbai
```

**Expected:** ₹40,000-45,000

---

## ✅ Checklist

- [ ] Installed ML libraries
- [ ] Trained model (ml_models folder created)
- [ ] Ran migrations
- [ ] Backend running on :8000
- [ ] Frontend running on :5173
- [ ] Can access prediction form
- [ ] Can get prediction results

---

## 🐛 Quick Fixes

**Model not found?**
```bash
python predictions/train_laptop_model.py
```

**Table doesn't exist?**
```bash
python manage.py migrate predictions
```

**Dependencies missing?**
```bash
pip install pandas numpy scikit-learn
```

---

**That's it! You're ready to predict laptop prices!** 🎉

