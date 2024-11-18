# %%  [markdown]
# Model Validation

This script compares the predicted pseudothecial maturation dates from the hydrothermal model, sporacleEzy model, and blackleg_sporacle model with the actual pseudothecial maturation dates from Khangura et al. 2007.

Weather data source were source using the WeatherOz (r-package), via SILO patched point data.

Weather data used for the following locations:

| Location      | Stations                 | Code   |
|---------------|--------------------------|--------|
| East Chapman  | Nabawa                   | 008028 |
| Merredin      | Merredin                 | 010092 |
| Mount Barker  | Mount Barker             | 009581 |
| Wongan Hills  | Wongan Hills Res Station | 008138 |


# %%	imports										 |
import pandas as pd
import datetime
import numpy as np

import matplotlib.pyplot as plt
import plotly.express as px
import statsmodels.api as sm

from blackleg_hydrothermal.hydrothermal_model_2d import get_pm_date_hydrothermal
from blackleg_hydrothermal.blackleg_sporacle_model_2d import get_pm_date_blackleg_sporacle
from blackleg_hydrothermal.sporacleEzy_model_2d import get_pm_date_sporacleEzy

from IPython.display import HTML


# %%											 |
df = pd.read_csv("data/Pseudothecia_Maturity_Dates_khangura2007.csv")
# df.loc[:,["Year", "Location"]].drop_duplicates()

wd = pd.read_csv("data/khangura2007_weather_1998-2000.csv")

station_map = {'East Chapman':8028, 'Merredin':10092, 'Mount Barker':9581, 'Wongan Hills':8138}


wd[wd.station_code == station_map['Mount Barker']]

# %%	Run hydrothermal model										 |

pred_dates = []
for i, row in df.iterrows():
    # break
    station_code = station_map[row.Location]
    weather_data = wd.loc[(wd.station_code == station_code) & (wd.year == row.Year)].copy().reset_index(drop=True)
    date = get_pm_date_hydrothermal(weather_data.rainfall, weather_data.air_tmax, weather_data.air_tmin, weather_data.evap_comb, weather_data.date)
    dt = datetime.datetime.strptime(str(date), "%Y-%m-%d")
    day_of_year = dt.timetuple().tm_yday
    pred_dates.append(day_of_year)


df['doy_hydrothermal'] = pred_dates

# %%	Run sporacleEzy										 |

pred_dates = []
for i, row in df.iterrows():
    # break
    station_code = station_map[row.Location]
    weather_data = wd.loc[(wd.station_code == station_code) & (wd.year == row.Year)].copy().reset_index(drop=True)
    date = get_pm_date_sporacleEzy(weather_data.rainfall, weather_data.air_tmax, weather_data.air_tmin, weather_data.date)
    dt = datetime.datetime.strptime(str(date), "%Y-%m-%d")
    day_of_year = dt.timetuple().tm_yday
    pred_dates.append(day_of_year)

df['doy_sporacleEzy'] = pred_dates

# wd.to_csv("khangura2007_weather_1998-2000_incl_FPM.csv", index=False)
# %%	Run blackleg_sporacle										 |

pred_dates = []
for i, row in df.iterrows():
    # break
    station_code = station_map[row.Location]
    weather_data = wd.loc[(wd.station_code == station_code) & (wd.year == row.Year)].copy().reset_index(drop=True)
    date = get_pm_date_blackleg_sporacle(weather_data.rainfall, weather_data.air_tmax, weather_data.air_tmin, weather_data.date)
    dt = datetime.datetime.strptime(str(date), "%Y-%m-%d")
    day_of_year = dt.timetuple().tm_yday
    pred_dates.append(day_of_year)

df['doy_blackleg_sporacle'] = pred_dates


# %%
import plotly.express as px
import statsmodels.api as sm
import numpy as np
from plotly.subplots import make_subplots

def plot_regression(df, x_col, y_col, title):
    fig = px.scatter(df, x=x_col, y=y_col, title=title)

    # Fit regression model
    X = df[x_col]
    y = df[y_col]
    X = sm.add_constant(X)  # Adds a constant term to the predictor
    model = sm.OLS(y, X).fit()
    df['regression_line'] = model.predict(X)

    # Add regression line to plot
    fig.add_trace(px.line(df, x=x_col, y='regression_line').data[0])

    # Calculate RMSE
    rmse = np.sqrt(np.mean((df[y_col] - df['regression_line'])**2))
    fig.add_annotation(x=0.05, y=0.92, text=f'RMSE: {rmse:.2f}', showarrow=False, xref='paper', yref='paper')
    print(f'RMSE: {rmse:.2f}')

    # Calculate correlation
    correlation = np.corrcoef(df[x_col], df[y_col])[0, 1]
    fig.add_annotation(x=0.05, y=0.98, text=f'Correlation: {correlation:.2f}', showarrow=False, xref='paper', yref='paper')
    fig.update_layout(xaxis_title='Day of Year (Observed)', yaxis_title='Day of Year (Predicted)')
    return display(
        HTML(
            fig.to_html(
                # full_html=True,
                # include_plotlyjs="cdn",
                full_html=True,
                include_plotlyjs=True,
            )))


df["doy_mean"] = (df[" doy_max"] + df.doy_min) / 2
# Plot doy_blackleg_sporacle VS actual
plot_regression(df, 'doy_mean', 'doy_blackleg_sporacle', 'blackleg_sporacle VS actual')

# Plot doy_sporacleEzy VS actual
plot_regression(df, 'doy_mean', 'doy_sporacleEzy', 'sporacleEzy VS actual')

# Plot doy_hydrothermal VS actual
plot_regression(df, 'doy_mean', 'doy_hydrothermal', 'hydrothermal VS actual')

# %%
