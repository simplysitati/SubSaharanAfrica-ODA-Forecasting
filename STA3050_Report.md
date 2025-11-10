# Forecasting Official Development Assistance to Sub-Saharan Africa (1960–2030)

## 1. Introduction
This analysis examines trends in **Official Development Assistance (ODA)** to **Sub-Saharan Africa** between 1960 and 2023, using data obtained from the **OECD** and **World Bank**. ODA remains one of the region’s most critical sources of development financing, influencing social programs, infrastructure, and macroeconomic stability.  
Because these inflows evolve gradually over time, **time series forecasting** provides an analytical framework for anticipating future aid levels, evaluating subregional disparities, and informing long-term policy planning.  
This project applies forecasting models to historical ODA data to project likely trajectories up to **2030**, offering both a quantitative and interpretive view of Africa’s development financing landscape.

---

## 2. Data and Methodology
The dataset used is the *“Net Official Development Assistance and Official Aid Received (current US$)”* series (1960–2023), published by the OECD and World Bank.  
Source: [World Bank Data – Net Official Development Assistance (DT.ODA.ALLD.CD)](https://data.worldbank.org/indicator/DT.ODA.ALLD.CD?locations=ZG)

Each Sub-Saharan African country was assigned to one of four analytical zones — **East**, **West**, **Central**, and **Southern Africa** — based on World Bank regional classifications.  
Annual ODA totals were aggregated by subregion to form a multi-series time series dataset with yearly observations from 1960 to 2023.  

Two forecasting methods were implemented:

1. **ARIMA (1,1,1)** — capturing serial dependencies and long-run trend dynamics.  
2. **Holt’s Linear Trend (Exponential Smoothing)** — modeling gradual trend movements without overfitting short-term volatility.  

Both models were trained on data from **1960–2018** and tested on **2019–2023**.  
Model accuracy was evaluated using **Mean Absolute Error (MAE)** and **Root Mean Squared Error (RMSE)** before forecasting forward to **2030**.  

The interactive component was developed using **Plotly Dash**, allowing users to select any of the four subregions and visualize historical data, test-period predictions, and forecasts. Each model’s accuracy metrics and forecast CSVs are dynamically generated within the dashboard.

---

## 3. Results
Across all four subregions, ODA shows a long-term upward trend with intermittent shocks during key global events — the 1980s debt crisis, the 2008 financial downturn, and the 2020 COVID-19 pandemic.  
Evaluation results reveal that **Holt’s Linear Trend** outperformed ARIMA across all regions, delivering lower prediction errors:

| Model | MAE (USD) | RMSE (USD) | Interpretation |
|--------|------------|------------|----------------|
| **ARIMA (1,1,1)** | 3.85 Billion | 4.45 Billion | Overreacted to short-term fluctuations |
| **Holt Linear Trend** | 2.16 Billion | 2.94 Billion | More stable and accurate fit |

This suggests that ODA data is more trend-dominant than autocorrelated — consistent with the nature of multilateral and bilateral aid flows, which evolve gradually rather than cyclically.  
Forecasts to 2030 indicate continued though **slower ODA growth** across the continent, with **East and West Africa** projected to remain dominant recipients. **Central and Southern Africa** show flatter trajectories, reflecting donor concentration patterns and differing absorption capacities.

---

## 4. Discussion
While both forecasting models demonstrate robust statistical performance, they share a common limitation: **they assume the future behaves like the past**.  
Recent developments, however, break this historical pattern. According to the **OECD Policy Brief (June 2025)**, *“Cuts in Official Development Assistance: OECD Projections for 2025 and the Near Term”*, ODA is projected to fall by **9–17% in 2025**, following a **9% drop in 2024** — the sharpest contraction in three decades.  
Major donors including the United States, France, Germany, and the United Kingdom have all announced consecutive ODA cuts for the first time in modern history. The brief projects that by **2027**, global ODA levels could revert to those of **2020**, severely affecting Sub-Saharan Africa and least developed countries, which could experience **16–28% declines** in net bilateral aid.  

These recent shocks mean that **model-based forecasts are now optimistic** relative to current policy realities. Statistical projections like those produced here effectively illustrate the *underlying structural trend* of ODA growth — but not the immediate **market and policy-driven reversals** currently underway.  
The contrast between projected growth and real-world cuts underscores a crucial insight: **forecasting provides a baseline for what should happen if trends continue — not necessarily what will happen when geopolitical or fiscal constraints intervene.**

---

## 5. Conclusion
This study demonstrates the value of **time series forecasting** for analyzing Africa’s external financing trends, while also acknowledging its limits in the face of global economic shocks.  
By combining historical ODA data (1960–2023) with statistical modeling and interactive visualization, it transforms decades of aid data into a dynamic analytical tool.  
The **Holt Linear Trend model** emerges as the most reliable baseline for ODA forecasting under normal conditions, but the **2024–2025 ODA cuts** highlight the need for adaptive models that incorporate *real-time policy and macroeconomic data*.  
Forecasting, therefore, should complement — not replace — policy analysis, ensuring that statistical projections are interpreted within current geopolitical and fiscal realities.

---

## 6. References
- OECD. (2025, June 26). *Cuts in Official Development Assistance: OECD Projections for 2025 and the Near Term.* Organisation for Economic Co-operation and Development.*[https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/06/cuts-in-official-development-assistance_e161f0c5/8c530629-en.pdf](https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/06/cuts-in-official-development-assistance_e161f0c5/8c530629-en.pdf)  
- World Bank. (2024). *Net official development assistance and official aid received (current US$) – Sub-Saharan Africa.* [https://data.worldbank.org/indicator/DT.ODA.ALLD.CD?locations=ZG](https://data.worldbank.org/indicator/DT.ODA.ALLD.CD?locations=ZG)

---

*Author: Wesley Clyde Fenjo Sitati*  
*Course: STA3050 – Time Series Analysis & Forecasting*  
*Semester: Fall 2025*  
*Institution: United States International University – Africa (USIU-A)*  