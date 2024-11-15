"""
pseudothecial maturation dates sources from Khangura et al. 2007.
Weather data source: WeatherOz, via silo patched point data.

Weather data used for the following locations:
| Location      | Stations                 | Code   |
|---------------|------------------        |--------|
| East Chapman  | Nabawa                   | 008028 |
| Merredin      | Merredin                 | 010092 |
| Mount Barker  | Mount Barker             | 009581 |
| Wongan Hills  | Wongan Hills Res Station | 008138 |

"""

# %%	imports										 |
import pandas as pd
import datetime
from blackleg_hydrothermal.hydrothermal_model import hydrothermal_run
import numpy as np

import matplotlib.pyplot as plt
import plotly.express as px
import statsmodels.api as sm

import blackleg_hydrothermal.hydrothermal_model as se
import blackleg_hydrothermal.hydrothermal_model_2d as se2

# %%											 |
df = pd.read_csv("data/Pseudothecia_Maturity_Dates_khangura2007.csv")
# df.loc[:,["Year", "Location"]].drop_duplicates()

wd = pd.read_csv("data/khangura2007_weather_1998-2000.csv")
wd.columns
df.Location.unique()
wd.station_name.unique()

station_map = {'East Chapman':8028, 'Merredin':10092, 'Mount Barker':9581, 'Wongan Hills':8138}

# %%	Run se										 |

pred_dates = []
for i, row in df.iterrows():
    # break
    station_code = station_map[row.Location]
    weather_data = wd.loc[(wd.station_code == station_code) & (wd.year == row.Year)].copy().reset_index(drop=True)
    ddf, date = se.hydrothermal_run(weather_data)
    dt = datetime.datetime.strptime(date, "%Y-%m-%d")
    day_of_year = dt.timetuple().tm_yday
    pred_dates.append(day_of_year)

df['se'] = pred_dates

# %%	run se2										 |


pred_dates = []
for i, row in df.iterrows():
    # if i==10:
    #     break
    # break
    station_code = station_map[row.Location]
    weather_data = wd.loc[(wd.station_code == station_code) & (wd.year == row.Year)].copy().reset_index(drop=True)
    date = se2.get_pm_date_hydrothermal(weather_data.rainfall, weather_data.air_tmax, weather_data.air_tmin, weather_data.evap_comb, weather_data.date)
    # date = datetime.date.fromisoformat(str(date))
    dt = datetime.datetime.strptime(str(date), "%Y-%m-%d")
    day_of_year = dt.timetuple().tm_yday
    pred_dates.append(day_of_year)

df['se2'] = pred_dates

rainfall = weather_data.rainfall
air_tmax = tmax = weather_data.air_tmax
air_tmin = tmin = weather_data.air_tmin
date_sequence = weather_data.date
evaporation = weather_data.evap_comb

row = df.loc[(df.se2 -df.se) != 0]

# %%											 |
dfrac = df.frac.to_numpy()
dfrac.shape
air_tmax.shape
temp_seq = np.interp(df.frac, [0, 1], [air_tmin[0], air_tmax[0]])

# Interpolate along the new axis, broadcasting dfrac for each grid point
air_tmin = np.array(air_tmin)[:, None]
air_tmax = np.array(air_tmax)[:, None]
temp_seq = air_tmin + (air_tmax - air_tmin) * dfrac[None,:]

temp_seq[0]

np.isclose(temp_seq[0], np.interp(df.frac, [0, 1], [air_tmin[0][0], air_tmax[0][0]]))


# Verify the shape
print(temp_seq.shape)  # Expected shape: (10, 4, 5, 5)


# %%	compare outliers										 |
# row = row.loc[10]
# df = pd.DataFrame({'rainfall':rainfall, 'air_tmax':tmax, 'air_tmin':tmin, 'date_sequence':date_sequence})

# np.isclose(df["rain7"], rainfall7)
# np.isclose(df["air_tmean"], air_tmean)
# np.isclose(df["air_tmean10"], air_tmean10)
# np.isclose(df['FPM'], fpm)

# fpm[:13]
# df['FPM'][:13]
# df["air_tmean10"][:13]
# air_tmean10[:13]

# df["air_tmean"][:13]
# air_tmean[:13]

# df["rainfall"][:13]
# rainfall7[:13]
# # wd.to_csv("khangura2007_weather_1998-2000_incl_FPM.csv", index=False)
# %%	plot										 |
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
    fig.update_layout(xaxis_title='Day of Year (Min)', yaxis_title='Day of Year (Max)')
    fig.show()


# Plot doy_hydrothermal VS actual
plot_regression(df, 'se', 'se2', 'se VS se2 (vectorised)')

# %%
