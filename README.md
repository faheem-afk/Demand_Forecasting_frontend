🚀 Demand Forecasting Dashboard (Live Deployment)

👉 Live App: https://demandforecastt.streamlit.app

An interactive machine learning-powered dashboard for forecasting meal demand across cities, built using a production-style pipeline and deployed with cloud-native components.

📌 Overview

This application provides real-time access to multi-week demand forecasts, enabling users to explore trends across cities and meals through an intuitive interface.

The system is powered by a multi-horizon forecasting pipeline and designed with a clear separation between model development and deployment.


🧠 What the App Does
	•	Forecasts demand up to 12 weeks ahead
	•	Enables interactive exploration of demand across cities and meals
	•	Provides real-time querying of precomputed predictions
	•	Displays key insights through a clean and user-friendly dashboard


⚙️ Deployment Architecture

Streamlit (Frontend)
        ↓
Neon Postgres (Database)
        ↓
Precomputed Forecasts (XGBoost models)

Key Components:
	•	Streamlit → Interactive frontend dashboard
	•	Neon (Serverless Postgres) → Cloud-hosted database for storing predictions
	•	ML Pipeline (offline) → Generates and uploads forecasts


📊 Model Highlights
	•	Multi-horizon forecasting using 12 XGBoost models
	•	Trained on ~320K rows with 32 engineered features
	•	Time-series features include:
	•	Lag variables
	•	Rolling statistics
	•	Predictions are precomputed and stored in the database for fast retrieval


🔍 Model Interpretability

Used SHAP to analyze feature importance.

Key findings:
	•	Historical demand (num_orders)
	•	16-week rolling average demand

These features consistently contributed most to model predictions.


⚡ Performance & Design
	•	Precomputed predictions → low-latency dashboard experience
	•	Efficient querying using Streamlit’s database connection layer
	•	Scalable architecture using serverless Postgres (Neon)
	•	Secure data access via parameterized queries


🖥️ How It Works
	1.	ML pipeline generates forecasts (offline)
	2.	Predictions are uploaded to Neon Postgres
	3.	Streamlit app queries data in real-time
	4.	Users interact with dashboards and explore insights


🔐 Notes
	•	This deployment uses Neon instead of local PostgreSQL
	•	No Docker is used in production — only in development
	•	Database credentials are securely managed via environment/secrets


💡 Key Takeaways
	•	Production ML systems require more than just models
	•	Separation of training, storage, and visualization improves scalability
	•	Cloud-native databases simplify deployment and access
	•	Precomputing predictions enables fast and responsive dashboards


📬 Contact
	•	LinkedIn: https://www.linkedin.com/in/faheem-bht
	•	Email: adahm7114@gmail.com


⭐ If you find this useful, feel free to share or connect!
