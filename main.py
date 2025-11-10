"""
main.py

Entry point for ODA subregional forecasting interactive app.
This file is intentionally small: it imports the module and starts the Dash server.
"""

import os
from oda_module import build_all_subregion_models
from oda_module import SUBREGION_MAP  # optional: to inspect mapping
from oda_module import prepare_subregion_timeseries, load_worldbank_style  # optional helpers

# Dash-specific import and builder function are included here to keep main.py minimal
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import io, base64
import pandas as pd

# ==== Configuration ====
DATA_CSV = "API_DT.ODA.ALLD.CD_DS2_en_csv_v2_6030.csv"  # change if your filename differs
FORECAST_END_YEAR = 2030

# ==== Build models ====
if not os.path.exists(DATA_CSV):
    raise SystemExit(f"Data CSV not found at {DATA_CSV}. Place it in the project folder or change DATA_CSV in main.py.")

print("Building models from:", DATA_CSV)
subregion_wide, models = build_all_subregion_models(DATA_CSV, eval_years=5, arima_order=(1,1,1), forecast_end_year=FORECAST_END_YEAR)
print("Models ready. Years:", subregion_wide.index.min(), "-", subregion_wide.index.max())

# ==== Dash app ====
app = dash.Dash(__name__)
app.title = "ODA Subregions Forecast"

subregions = list(subregion_wide.columns)

app.layout = html.Div([
    html.H2("ODA Forecast — Sub-Saharan Africa (Subregion Selector)"),
    html.Div([
        dcc.Dropdown(id='subregion-dropdown', options=[{'label': s, 'value': s} for s in subregions],
                     value=subregions[0], clearable=False, style={'width':'40%'}),
    ]),
    html.Div(id='metrics-div', style={'marginTop':10}),
    dcc.Graph(id='oda-timeseries-plot'),
    html.Br(),
    html.Div(id='download-link-div')
], style={'marginLeft':30, 'marginRight':30})


@app.callback(
    [Output('oda-timeseries-plot', 'figure'),
     Output('metrics-div', 'children'),
     Output('download-link-div', 'children')],
    [Input('subregion-dropdown', 'value')]
)
def update(selected_sub):
    model_res = models[selected_sub]
    train = model_res['train']
    test = model_res['test']
    forecast = model_res['forecast']  # DataFrame indexed by Year

    # build figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=train.index, y=train.values, mode='lines+markers', name='Train (historical)'))
    fig.add_trace(go.Scatter(x=test.index, y=test.values, mode='markers+lines', name='Test (actual)'))
    fig.add_trace(go.Scatter(x=model_res['pred_test_arima'].index, y=model_res['pred_test_arima'].values,
                             mode='lines+markers', name='ARIMA (test pred)', line=dict(dash='dash')))
    fig.add_trace(go.Scatter(x=model_res['pred_test_holt'].index, y=model_res['pred_test_holt'].values,
                             mode='lines+markers', name='Holt (test pred)', line=dict(dash='dash')))
    fig.add_trace(go.Scatter(x=forecast.index, y=forecast['ARIMA'], mode='lines', name='ARIMA (forecast)', line=dict(width=3)))
    fig.add_trace(go.Scatter(x=forecast.index, y=forecast['Holt'], mode='lines', name='Holt (forecast)', line=dict(width=3, dash='dot')))
    fig.update_layout(title=f"ODA (current US$) — {selected_sub}", xaxis_title='Year', yaxis_title='ODA (current US$)', template='plotly_white')

    metrics = model_res['metrics']
    metrics_div = html.Div([
        html.P(f"Evaluation (last 5 years) — ARIMA MAE: {metrics['ARIMA_MAE']:.2f}, RMSE: {metrics['ARIMA_RMSE']:.2f}"),
        html.P(f"Holt MAE: {metrics['HOLT_MAE']:.2f}, RMSE: {metrics['HOLT_RMSE']:.2f}")
    ])

    # Prepare download link (CSV)
    csv_buffer = io.StringIO()
    out_df = forecast.reset_index().rename(columns={'ARIMA': 'ARIMA_ODA', 'Holt': 'HOLT_ODA'})
    out_df.to_csv(csv_buffer, index=False)
    csv_b64 = base64.b64encode(csv_buffer.getvalue().encode()).decode()
    href_data = f"data:text/csv;base64,{csv_b64}"
    download_link = html.A("Download annual forecast CSV", href=href_data, download=f"{selected_sub}_oda_forecast.csv", target="_blank")

    return fig, metrics_div, download_link


if __name__ == "__main__":
    # When running from PyCharm, run main.py directly.
    print("Starting Dash app at http://127.0.0.1:8050")
    app.run(debug=False)