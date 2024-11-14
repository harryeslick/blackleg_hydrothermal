import logging
from rasterio.plot import show
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
all_grids.keys()


layers = all_grids["daily_rain"].shape[0]

for i in range(layers):
    fmp = sporacleEzy_FMP(rainfall=all_grids["daily_rain"][i],
                tmax=all_grids["max_temp"][i],
                tmin= all_grids["min_temp"][i]
                )


# %%											 |

# SporacleEzy model parameters
SAR_ON = 18
RAIN_THRESHOLD = 1.0
T_LOWER_THRESHOLD = 6
T_UPPER_THRESHOLD = 22

def sporacleEzy_FMP(rainfall, tmax, tmin):
    tmean = (tmax + tmin) /2
    conditions = [
        rainfall >= RAIN_THRESHOLD,
        tmean >= T_LOWER_THRESHOLD,
        tmean <= T_UPPER_THRESHOLD
    ]
    conditions = np.array(conditions)
    return conditions.all(axis=0).astype(int)


def blackleg_sporacleEzy_run(df):

    df['FPM'] = df.apply(lambda row: sporacleEzy_FMP(row['rainfall'], row['air_tmax'], row['air_tmin']), axis=1)
    df['FPM_cumsum'] = df['FPM'].cumsum()
    pm_date = df.loc[(df['FPM_cumsum'] <= SAR_ON), "date"].iloc[-1]
    print("pseudothecial maturation date", pm_date)
    return df, pm_date