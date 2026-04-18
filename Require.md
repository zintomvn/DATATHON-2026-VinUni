# Datathon 2026 - The Gridbreakers

## Professional Data Science Project Template

---

# 📌 1. Project Overview

This project aims to solve a real-world business problem:

> **Revenue Forecasting for an E-commerce Fashion Company in Vietnam**

The competition consists of three parts:

1. Multiple-choice questions (data querying)
2. Exploratory Data Analysis (EDA) & Visualization
3. Sales Forecasting (Time Series)

---

# 📊 2. Dataset Overview

The dataset simulates e-commerce operations (2012–2022), including:

### Master Data

- products.csv
- customers.csv
- promotions.csv
- geography.csv

### Transaction Data

- orders.csv
- order_items.csv
- payments.csv
- shipments.csv
- returns.csv
- reviews.csv

### Analytical Data

- sales.csv (train)
- sales_test.csv (test)

### Operational Data

- inventory.csv
- web_traffic.csv

---

# 🎯 3. Objectives

- Perform deep exploratory data analysis
- Generate business insights with storytelling
- Build a robust revenue forecasting model
- Ensure reproducibility and no data leakage

---

# 📁 4. Project Structure

```bash
datathon-2026-the-gridbreakers/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
│
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_modeling.ipynb
│   └── 04_evaluation.ipynb
│
├── src/
│   ├── data/
│   │   ├── load_data.py
│   │   └── preprocess.py
│   │
│   ├── features/
│   │   └── build_features.py
│   │
│   ├── models/
│   │   ├── train.py
│   │   └── predict.py
│   │
│   └── utils/
│       └── metrics.py
│
├── outputs/
│   ├── figures/
│   ├── models/
│   └── submissions/


Raw Data
   ↓
Data Cleaning
   ↓
EDA
   ↓
Feature Engineering
   ↓
Model Training
   ↓
Evaluation
   ↓
Submission


01_eda.ipynb
# 1. Introduction
- Define objective
- Business context

# 2. Data Loading
- Load all CSV files
- Show shape and schema

# 3. Data Cleaning
- Missing values
- Data types
- Outliers

# 4. Univariate Analysis
- Revenue distribution
- Customer behavior
- Product categories

# 5. Bivariate / Multivariate Analysis
- Revenue vs category
- Returns vs size
- Traffic vs conversion

# 6. Visualization
- Time series plots
- Heatmaps
- Bar charts

# 7. Business Insights
- Key findings (bullet points)
- Supported by data

# 8. Summary


02_feature_engineering.ipynb
# 1. Feature Engineering Strategy
- Time features (year, month, day)
- Customer features
- Product features
- Promotion features

# 2. Time Series Features
- Lag features
- Rolling mean
- Seasonality indicators

# 3. Data Merging
- Join all tables correctly
- Avoid leakage

# 4. Final Dataset
- Train/test split (time-based)


03_modeling.ipynb
# 1. Problem Definition
- Forecast Revenue

# 2. Model Selection
- Linear Regression
- Random Forest
- XGBoost / LightGBM

# 3. Training Strategy
- Time-series cross-validation

# 4. Model Training
- Train multiple models
- Save models

# 5. Feature Importance
- Plot and analyze


04_evaluation.ipynb

# 1. Evaluation Metrics
- MAE
- RMSE
- R²

# 2. Model Comparison
- Compare all models

# 3. Error Analysis
- Identify failure cases

# 4. Final Model Selection

# 5. Generate Submission
- Match sample_submission format



```
