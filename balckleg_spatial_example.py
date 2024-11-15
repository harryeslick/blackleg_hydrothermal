from blackleg_hydrothermal.sporacleEzy_model import sporacleEzy_FMP
from rasterio.plot import show
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point, box
import datetime
import matplotlib.animation as animation

from blackleg_hydrothermal.read_silo_cog_arrays import read_cog_arrays
from blackleg_hydrothermal.hydrothermal_model_2d import hydrothermal_FPM_cumulative
from blackleg_hydrothermal.sporacleEzy_model_2d import sporacleEzy_FPM_cumulative
from blackleg_hydrothermal.blackleg_sporacle_model_2d import blackleg_sporacle_FPM_cumulative

# %%	Silo weather variables										 |

# base instruction on data access here:
# https://www.longpaddock.qld.gov.au/silo/gridded-data/

# Idex of all available NetCDF products is available here:
# https://s3-ap-southeast-2.amazonaws.com/silo-open-data/Official/annual/index.html

# %%	Download data										 |

variables =[
    "daily_rain",
    "evap_pan",
    "max_temp",
    "min_temp",
    ]

# SW WA
aoi = box(*Point(118.0, -31.2).buffer(4).bounds)

startdate = datetime.date(2023, 1, 1)
enddate = datetime.date(2023, 5, 28)

all_grids = read_cog_arrays(startdate, enddate,  variables, aoi)

rainfall = all_grids["daily_rain"]
tmax = all_grids["max_temp"]
tmin = all_grids["min_temp"]
evaporation = all_grids["evap_pan"]

# %%	vectorised	sporacleEzy_model_2d									 |

fpm_cumsum = sporacleEzy_FPM_cumulative(rainfall, tmax, tmin)


fig, ax = plt.subplots()
cax = ax.imshow(fpm_cumsum[-1], vmax=18)
fig.colorbar(cax, ax=ax, label='maturity index')
ax.set_title(f"sporacleEzy @ {enddate.strftime("%Y-%m-%d")}")
plt.show()

# %%	vectorised	sporacleEzy_model_2d									 |


fpm_cumsum = blackleg_sporacle_FPM_cumulative(rainfall, tmax, tmin)


fpm_cumsum = fpm_cumsum.astype(float)
fpm_cumsum[mask] = np.nan

# show(fpm_cumsum[-1], vmax=43, title="sporacle OG")

fig, ax = plt.subplots()
cax = ax.imshow(fpm_cumsum[-1], vmax=43)
fig.colorbar(cax, ax=ax, label='maturity index')
ax.set_title(f"sporacle OG @ {enddate.strftime("%Y-%m-%d")}")
plt.show()


# %%	vectorised	sporacleEzy_model_2d									 |


fpm_cumsum = hydrothermal_FPM_cumulative(rainfall, tmax, tmin, evaporation)


fpm_cumsum = fpm_cumsum.astype(float)
fpm_cumsum[mask] = np.nan

# show(fpm_cumsum[-1], vmax=196, title="Hydrothermal model")

fig, ax = plt.subplots()
cax = ax.imshow(fpm_cumsum[-1], vmax=196)
fig.colorbar(cax, ax=ax, label='maturity index')
ax.set_title(f"Hydrothermal model @ {enddate.strftime("%Y-%m-%d")}")
plt.show()

# %%
