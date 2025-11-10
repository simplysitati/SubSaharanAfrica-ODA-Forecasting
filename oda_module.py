"""

Module for loading ODA data, aggregating into subregions,
fitting ARIMA and Holt models, and producing forecasts.

Public functions:
- load_worldbank_style(csv_path) -> DataFrame (Country, Year, ODA)
- prepare_subregion_timeseries(df_long) -> pivot DataFrame (index=Year, cols=subregions)
- fit_and_forecast(series, ...) -> dict with train/test/predictions/metrics/forecast
- build_all_subregion_models(csv_path) -> (subregion_wide, models)
- create_dash_app(subregion_wide, models, config) -> Dash app instance

"""

import io
import base64
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_absolute_error, mean_squared_error
from datetime import timedelta

# -----------------------
# Configurable subregion map (edit if needed)
# -----------------------
SUBREGION_MAP = {
    "East Africa": [
        "Burundi", "Comoros", "Djibouti", "Eritrea", "Ethiopia", "Kenya",
        "Madagascar", "Malawi", "Mauritius", "Mozambique", "Rwanda",
        "Seychelles", "Somalia", "South Sudan", "Uganda", "Tanzania", "Zambia", "Zimbabwe"
    ],
    "West Africa": [
        "Benin", "Burkina Faso", "Cabo Verde", "Côte d'Ivoire", "Gambia, The", "Gambia",
        "Ghana", "Guinea", "Guinea-Bissau", "Liberia", "Mali", "Mauritania",
        "Niger", "Nigeria", "Saint Helena", "Senegal", "Sierra Leone", "Togo"
    ],
    "Central Africa": [
        "Angola", "Cameroon", "Central African Republic", "Chad", "Congo, Dem. Rep.", "Congo, Rep.",
        "Equatorial Guinea", "Gabon", "Sao Tome and Principe"
    ],
    "Southern Africa": [
        "Botswana", "Eswatini", "Lesotho", "Namibia", "South Africa"
    ]
}


# -----------------------
# Data loading helpers
# -----------------------
def load_worldbank_style(csv_path):
    """
    Load a World Bank wide-format CSV (skiprows=4) if present, else try long format.
    Returns a DataFrame with columns: ['Country','ISO3'(optional),'Year','ODA'].
    """
    # Try wide format first (skiprows=4)
    try:
        df = pd.read_csv(csv_path, skiprows=4)
        year_cols = [c for c in df.columns if str(c).isdigit()]
        if len(year_cols) >= 10:
            df_long = df.melt(id_vars=[c for c in ["Country Name", "Country Code"] if c in df.columns],
                              value_vars=year_cols, var_name="Year", value_name="ODA")
            # normalize column names
            colmap = {}
            if "Country Name" in df_long.columns:
                colmap["Country Name"] = "Country"
            if "Country Code" in df_long.columns:
                colmap["Country Code"] = "ISO3"
            df_long = df_long.rename(columns=colmap)
            df_long = df_long.dropna(subset=["ODA"])
            df_long["Year"] = df_long["Year"].astype(int)
            return df_long.rename(columns={"ODA": "ODA"})
    except Exception:
        pass

    # Attempt reading as long format CSV
    df2 = pd.read_csv(csv_path)
    # try to detect columns
    cols_lower = [c.lower() for c in df2.columns]
    country_col = next((c for c in df2.columns if "country" in c.lower()), None)
    year_col = next((c for c in df2.columns if c.lower() == "year"), None)
    value_col = next((c for c in df2.columns if any(k in c.lower() for k in ["oda","value","amount","official"])), None)
    if country_col and year_col and value_col:
        out = df2[[country_col, year_col, value_col]].rename(columns={country_col: "Country", year_col: "Year", value_col: "ODA"})
        out = out.dropna(subset=["ODA"])
        out["Year"] = out["Year"].astype(int)
        return out

    raise ValueError("Unable to parse CSV: check file format. Expected World Bank wide CSV or a long-format CSV with country/year/value.")


# -----------------------
# Subregion assignment helper
# -----------------------
def assign_subregion(country_name, subregion_map=SUBREGION_MAP):
    """
    Return the subregion name for a country; else None.
    Uses exact and simple normalized matching.
    """
    if pd.isna(country_name):
        return None
    cn = country_name.strip().lower().replace('.', '').replace(',', '')
    for subregion, members in subregion_map.items():
        for m in members:
            mm = m.strip().lower().replace('.', '').replace(',', '')
            if cn == mm:
                return subregion
            # some fuzzy matches: shorten common prefixes
            if cn.startswith(mm) or mm.startswith(cn):
                return subregion
    return None


def prepare_subregion_timeseries(df_long, subregion_map=SUBREGION_MAP):
    """
    Convert df_long (Country, Year, ODA) -> pivot Year x Subregion with summed ODA.
    Missing subregions become zero columns.
    """
    df = df_long.copy()
    df['ODA'] = pd.to_numeric(df['ODA'], errors='coerce')
    df = df.dropna(subset=['ODA'])
    df['Subregion'] = df['Country'].apply(lambda c: assign_subregion(c, subregion_map))
    df_sub = df.dropna(subset=['Subregion'])
    grouped = df_sub.groupby(['Subregion', 'Year'])['ODA'].sum().reset_index()
    pivot = grouped.pivot(index='Year', columns='Subregion', values='ODA').fillna(0)
    # ensure columns exist
    for s in subregion_map.keys():
        if s not in pivot.columns:
            pivot[s] = 0.0
    pivot = pivot.sort_index()
    return pivot


# -----------------------
# Modeling helper
# -----------------------
def fit_and_forecast(series, eval_years=5, arima_order=(1, 1, 1), forecast_end_year=2030):
    """
    series: pd.Series indexed by Year (int) with numeric values.
    Returns dict with: train, test, preds (on test), metrics, forecast (annual)
    """
    ser = series.copy().sort_index()

    # ---- Convert integer year index to a DatetimeIndex ending each year (Dec 31)
    # This gives statsmodels a supported index for forecasting.
    # Example: year 1960 -> 1960-12-31 (annual frequency)
    try:
        years = ser.index.astype(int)
    except Exception:
        # if index already datetime-like, try to extract the year
        years = pd.Index([getattr(d, "year", d) for d in ser.index]).astype(int)

    ser.index = pd.to_datetime(years.astype(str) + "-12-31")
    ser.index.freq = "YE-DEC"  # annual frequency (year end)

    # Determine train/test split using the last eval_years (by position)
    if len(ser) < eval_years + 3:
        eval_years = max(1, min(eval_years, len(ser) // 3))

    train = ser.iloc[:-eval_years]
    test = ser.iloc[-eval_years:]

    # Fit ARIMA on train
    try:
        arima_model = ARIMA(train, order=arima_order).fit()
        arima_pred = arima_model.forecast(steps=len(test))
        # ensure same index as test
        arima_pred.index = test.index
    except Exception as e:
        arima_pred = pd.Series([np.nan] * len(test), index=test.index)
        print("ARIMA fit failed:", e)

    # Fit Holt's linear trend (ExponentialSmoothing)
    try:
        hw_model = ExponentialSmoothing(train, trend='add', seasonal=None, initialization_method='estimated').fit()
        hw_pred = hw_model.forecast(len(test))
        hw_pred.index = test.index
    except Exception as e:
        hw_pred = pd.Series([np.nan] * len(test), index=test.index)
        print("Holt fit failed:", e)

    # Metrics: MAE and RMSE (portable)
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    mae_arima = mean_absolute_error(test.values, arima_pred.values)
    rmse_arima = float(np.sqrt(mean_squared_error(test.values, arima_pred.values)))
    mae_holt = mean_absolute_error(test.values, hw_pred.values)
    rmse_holt = float(np.sqrt(mean_squared_error(test.values, hw_pred.values)))

    metrics = {
        'ARIMA_MAE': mae_arima,
        'ARIMA_RMSE': rmse_arima,
        'HOLT_MAE': mae_holt,
        'HOLT_RMSE': rmse_holt
    }

    # Refit on full series and forecast to forecast_end_year
    last_year = ser.index.year.max()
    forecast_years = list(range(last_year + 1, forecast_end_year + 1))
    # create target datetimes for forecast index (year ends)
    fc_dates = pd.to_datetime([f"{y}-12-31" for y in forecast_years])

    try:
        arima_full = ARIMA(ser, order=arima_order).fit()
        arima_fc = arima_full.forecast(steps=len(forecast_years))
        arima_fc.index = fc_dates
    except Exception as e:
        arima_fc = pd.Series([np.nan] * len(forecast_years), index=fc_dates)
        print("ARIMA full fit failed:", e)

    try:
        hw_full = ExponentialSmoothing(ser, trend='add', seasonal=None, initialization_method='estimated').fit()
        hw_fc = hw_full.forecast(len(forecast_years))
        hw_fc.index = fc_dates
    except Exception as e:
        hw_fc = pd.Series([np.nan] * len(forecast_years), index=fc_dates)
        print("Holt full fit failed:", e)

    # Build forecast DataFrame indexed by Year (int) for downstream code
    forecast_df = pd.DataFrame({
        'ARIMA': arima_fc.values,
        'Holt': hw_fc.values
    }, index=[d.year for d in fc_dates])

    # Convert train/test indexes back to integer years for other parts of the code if needed
    train_out = train.copy()
    test_out = test.copy()
    train_out.index = train_out.index.year
    test_out.index = test_out.index.year

    # also ensure pred_test series are indexed by int years
    pred_test_arima = arima_pred.copy()
    pred_test_holt = hw_pred.copy()
    pred_test_arima.index = pred_test_arima.index.year
    pred_test_holt.index = pred_test_holt.index.year

    return {
        'train': train_out,
        'test': test_out,
        'pred_test_arima': pred_test_arima,
        'pred_test_holt': pred_test_holt,
        'metrics': metrics,
        'forecast': forecast_df
    }


# -----------------------
# High-level builder
# -----------------------
def build_all_subregion_models(csv_path, eval_years=5, arima_order=(1,1,1), forecast_end_year=2030, subregion_map=SUBREGION_MAP):
    """Load CSV, prepare subregion series, and fit models for each subregion."""
    long_df = load_worldbank_style(csv_path)
    # Attempt to normalize column names if necessary
    if 'Country' not in long_df.columns:
        if 'Country Name' in long_df.columns:
            long_df = long_df.rename(columns={'Country Name': 'Country'})
    if 'Year' not in long_df.columns and 'year' in long_df.columns:
        long_df = long_df.rename(columns={'year':'Year'})
    if 'ODA' not in long_df.columns:
        valcol = next((c for c in long_df.columns if 'value' in c.lower() or 'oda' in c.lower()), None)
        if valcol:
            long_df = long_df.rename(columns={valcol: 'ODA'})

    subregion_wide = prepare_subregion_timeseries(long_df, subregion_map=subregion_map)
    models = {}
    for sub in subregion_wide.columns:
        s = subregion_wide[sub]
        models[sub] = fit_and_forecast(s, eval_years, arima_order, forecast_end_year)
    return subregion_wide, models