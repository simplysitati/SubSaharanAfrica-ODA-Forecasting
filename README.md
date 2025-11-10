# 🌍 Sub-Saharan Africa ODA Forecasting (1960–2030)

## 📖 Project Overview
This project analyzes and forecasts **Official Development Assistance (ODA)** to **Sub-Saharan Africa** between **1960 and 2030**, using historical data from the **OECD** and **World Bank**.  
It was developed as part of my coursework in **STA3050 – Time Series Analysis & Forecasting** at the **United States International University–Africa (USIU-A)**.

The analysis combines **time series modeling** with an **interactive data visualization dashboard**, allowing exploration of long-term aid trends across four subregions:  
**East**, **West**, **Central**, and **Southern Africa**.

---

## 🧠 Objectives
- Examine historical trends in ODA inflows (1960–2023).
- Apply **ARIMA (1,1,1)** and **Holt’s Linear Trend** models for forecasting.
- Evaluate model performance using **MAE** and **RMSE** metrics.
- Forecast regional aid flows to **2030**.
- Develop an **interactive Plotly Dash dashboard** for subregional exploration.

---

## 🧮 Dataset
**Source:** [World Bank Data – Net Official Development Assistance (current US$)](https://data.worldbank.org/indicator/DT.ODA.ALLD.CD?locations=ZG)  
**Coverage:** 1960–2023  
**Geographic scope:** Sub-Saharan Africa (aggregate of 48 countries)  
**Units:** Current US dollars  

Each country was mapped to one of four analytical subregions:
- **East Africa**
- **West Africa**
- **Central Africa**
- **Southern Africa**

---

## ⚙️ Methodology
The project workflow follows these steps:

1. **Data Preprocessing**
   - Load World Bank CSV data and transform from wide to long format.
   - Aggregate annual ODA by subregion (1960–2023).

2. **Modeling**
   - Split dataset into training (1960–2018) and test (2019–2023).
   - Fit ARIMA(1,1,1) and Holt’s Linear Trend models.
   - Compute evaluation metrics (MAE, RMSE).

3. **Forecasting**
   - Extend both models to forecast ODA to 2030.
   - Compare projections and accuracy.

4. **Visualization**
   - Build an interactive dashboard using Plotly Dash.
   - Enable subregion selection, visual metrics, and downloadable CSV forecasts.

---

## 📊 Model Evaluation Summary

| Model | MAE (USD) | RMSE (USD) | Notes |
|--------|------------|------------|--------|
| **ARIMA (1,1,1)** | 3.85 Billion | 4.45 Billion | Captures dynamics, but less stable |
| **Holt’s Linear Trend** | 2.16 Billion | 2.94 Billion | Smoother and more reliable |

**Interpretation:**  
Holt’s Linear Trend model produced lower error margins, making it a better fit for ODA data characterized by long-run structural trends rather than cyclical patterns.

---

## 🧩 Key Insights
- ODA to Sub-Saharan Africa shows **steady long-term growth** with periodic global shocks (1980s debt crises, 2008 recession, 2020 pandemic).  
- **East and West Africa** remain dominant recipients due to diversified economies and donor priorities.  
- **Central and Southern Africa** exhibit flatter growth trends.  
- **Forecasts suggest decelerating growth through 2030**, reflecting potential aid fatigue and economic reallocation.

---

## ⚠️ Contextual Caveat
While the statistical models performed strongly, they assume **historical continuity**.  
Recent real-world developments contradict this assumption:

> According to the *OECD Policy Brief (June 2025)*, *“Cuts in Official Development Assistance: OECD Projections for 2025 and the Near Term”*,  
> global ODA is projected to **drop by 9–17% in 2025**, following a **9% reduction in 2024** — the sharpest contraction in 30 years.  
>  
> Major donors including the United States, France, Germany, and the United Kingdom have all announced consecutive cuts, with Sub-Saharan Africa expected to face a **16–28% decline** in bilateral aid.

**Implication:**  
> The models represent *structural trends*, not current fiscal realities.  
> Forecasts serve as a baseline for “business-as-usual” scenarios, not as definitive projections amid donor retrenchment.

---

## 💻 Running the Project Locally

### 🔸 Prerequisites
Make sure you have Python 3.10+ and Git installed.

### 🔸 Installation
Clone the repository:
```bash
git clone https://github.com/simplysitati/SubSaharanAfrica-ODA-Forecasting.git
cd SubSaharanAfrica-ODA-Forecasting
