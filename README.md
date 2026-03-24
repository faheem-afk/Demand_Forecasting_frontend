<h1 align="center">📊 Demand Forecasting Dashboard (Live)</h1>

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?size=22&duration=3000&color=36BCF7&center=true&vCenter=true&width=650&lines=Real-Time+Demand+Forecasting+Dashboard;12-Week+Predictions+Across+Cities;Built+for+Fast%2C+Scalable+Access" />
</p>

<p align="center">
  <a href="https://demandforecastt.streamlit.app">
    <img src="https://img.shields.io/badge/Live-Demo-brightgreen?style=for-the-badge&logo=streamlit" />
  </a>
  <img src="https://img.shields.io/badge/Deployment-Cloud-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Database-Neon%20Postgres-orange?style=for-the-badge" />
</p>

---

## 📌 Overview

This is the **live deployment** of a production-style demand forecasting system.

An interactive dashboard that provides **real-time access to multi-week forecasts**,  
built with a clear separation between model development and deployment.

👉 Not just predictions — a system designed for **fast, reliable decision access**

---

## 🧠 What the App Does

- Forecasts demand up to **12 weeks ahead**  
- Enables interactive exploration across **cities & meals**  
- Queries predictions in **real-time**  
- Displays insights through a clean, intuitive dashboard  

---

## ⚙️ Architecture

Streamlit (Frontend)
↓
Neon Postgres (Database)
↓
Precomputed Forecasts (XGBoost models)

### Key Components

- **Streamlit** → Interactive frontend  
- **Neon (Serverless Postgres)** → Scalable cloud database  
- **ML Pipeline (offline)** → Generates and uploads forecasts  

---

## 📊 Model Highlights

- Multi-horizon forecasting using **12 XGBoost models**  
- Trained on:
  - ~320,000 rows  
  - 32 engineered features  

Time-series features include:
- Lag variables  
- Rolling statistics  

👉 Predictions are **precomputed** and stored → fast retrieval

---

## 🔍 Interpretability (SHAP)

Used SHAP to understand model behavior.

📈 Key drivers:
- `num_orders` (historical demand)  
- `num_orders_rolling_16_week`  

👉 Demand patterns are driven by **recent + smoothed history**

---

## ⚡ Performance & Design

- Precomputed predictions → **low-latency experience**  
- Efficient querying via Streamlit DB connection  
- Serverless Postgres → **scalable by design**  
- Secure access via parameterized queries  

---

## 🖥️ How It Works

1. ML pipeline generates forecasts (offline)  
2. Predictions are uploaded to Neon Postgres  
3. Streamlit app queries data in real-time  
4. Users explore insights through dashboards  

---

## 🔐 Notes

- Production uses **Neon (not local PostgreSQL)**  
- No Docker in production (dev-only)  
- Credentials managed securely via environment/secrets  

---

## 💡 Key Takeaways

- Production ML ≠ just models  
- Separation of concerns → better scalability  
- Cloud-native databases simplify deployment  
- Precomputing → fast, responsive dashboards  

---

## 🌐 Live App

👉 https://demandforecastt.streamlit.app

---

## 📫 Connect

- LinkedIn: https://www.linkedin.com/in/faheem-bht  
- Email: adahm7114@gmail.com  

---

<p align="center">
  ⭐ If you found this useful, consider starring the repo!
</p>


⸻
