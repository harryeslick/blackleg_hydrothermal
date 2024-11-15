import logging
from rasterio.plot import show
import numpy as np
import matplotlib.pyplot as plt
import rasterio
from rasterio.features import geometry_window
from shapely.geometry import Point, box
import tempfile
import datetime
import matplotlib.animation as animation

# %%	Silo weather variables										 |

# base instruction on data access here:
# https://www.longpaddock.qld.gov.au/silo/gridded-data/

# Idex of all available NetCDF products is available here:
# https://s3-ap-southeast-2.amazonaws.com/silo-open-data/Official/annual/index.html


variables =[
    "daily_rain",
    "evap_pan",
    "max_temp",
    "min_temp",
    ]

def create_cog_url(variable, date: datetime.date):
    base_url = "https://s3-ap-southeast-2.amazonaws.com/silo-open-data/Official/daily/"
    product_suffix = f"{variable}/{date.year}/{date.strftime("%Y%m%d")}.{variable}.tif"
    cog_url = base_url+product_suffix
    return cog_url

def read_cog(cog_url, aoi):
    with rasterio.open(cog_url) as src:
        profile = src.profile
        assert profile["crs"].to_string() == 'EPSG:4326', 'The CRS is not EPSG:4326'
        window = geometry_window(src, [aoi])

        # Read the data including the nodata mask
        data = src.read(1, masked=True, window=window)

        # Calculate the new affine transformation
        window_transform = src.window_transform(window)
        profile.update(width=window.width,
                        height=window.height,
                        transform=window_transform
                        )
    return data, profile


# %%	Download data										 |
# SW WA
aoi = box(*Point(118.0, -31.2).buffer(4).bounds)

startdate = datetime.date(2023, 1, 1)
enddate = datetime.date(2023, 2, 28)
date_sequence = [startdate + datetime.timedelta(days=x) for x in range((enddate - startdate).days + 1)]

all_grids = {}
for variable in variables:
    logging.info(f"Downloading {variable}")
    grids = []
    for date in date_sequence:
        cog_url = create_cog_url(variable, date)
        data, profile = read_cog(cog_url, aoi)
        data = data.filled(np.nan)
        grids.append(data)

    # Create a 3D array from the list of grids
    grid_array = np.array(grids)
    all_grids[variable] = grid_array
# %%


# %%	vectorised										 |
rainfall = all_grids["daily_rain"]
tmax = all_grids["max_temp"]
tmin = all_grids["min_temp"]

fpm = sporacleEzy_FPM(rainfall, tmax, tmin)
fpm.sum()
fpm_cumsum = fpm.cumsum(axis=0)
fpm_sum = fpm_cumsum[-1]
show(fpm_sum)
fpm_sum.shape


# %%											 |

# SporacleEzy model parameters
SAR_ON = 18
RAIN_THRESHOLD = 1.0
T_LOWER_THRESHOLD = 6
T_UPPER_THRESHOLD = 22


def sporacleEzy_FPM(rainfall, tmax, tmin):
    tmean = (tmax + tmin) / 2
    conditions = (rainfall >= RAIN_THRESHOLD) & (tmean >= T_LOWER_THRESHOLD) & (tmean <= T_UPPER_THRESHOLD)
    return conditions.astype(int)


def sporacleEzy_FPM_cumulative(rainfall, tmax, tmin):
    assert rainfall.shape == tmax.shape == tmin.shape, "Input arrays must have the same shape"

    fpm = sporacleEzy_FPM(rainfall, tmax, tmin)
    fpm_cumsum = fpm.cumsum(axis=0)
    # current_pm = fpm_cumsum[-1]
    return fpm_cumsum


def get_pm_date_sporacleEzy(rainfall, tmax, tmin, date_sequence):
    assert len(rainfall) == len(tmax) == len(tmin) == len(date_sequence), "All input arrays must have the same length"
    fpm = sporacleEzy_FPM_cumulative(rainfall, tmax, tmin)
    idx = np.argmax(fpm >= SAR_ON, axis=0)
    pm_date = np.vectorize(lambda x: date_sequence[x])(idx)
    return pm_date



# %%											 |

pred_dates = []
for i, row in df.iterrows():
    # break
    station_code = station_map[row.Location]
    weather_data = wd.loc[(wd.station_code == station_code) & (wd.year == row.Year)].copy().reset_index(drop=True)
    ddf, date = blackleg_sporacleEzy_run(weather_data)
    dt = datetime.datetime.strptime(date, "%Y-%m-%d")
    pred_dates.append(dt)

df['sporacleEzy_o2'] = pred_dates

pred_dates = []
for i, row in df.iterrows():
    station_code = station_map[row.Location]
    weather_data = wd.loc[(wd.station_code == station_code) & (wd.year == row.Year)].copy().reset_index(drop=True)
    dt = get_pm_date_sporacleEzy(rainfall=weather_data.rainfall, tmax=weather_data.air_tmax, tmin=weather_data.air_tmin, date_sequence=weather_data.date)
    pred_dates.append(dt)

df['sporacleEzy_v'] = pred_dates
# %%

weather_data.date