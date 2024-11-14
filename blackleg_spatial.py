import rioxarray
import xarray as xr



variables =[
    "daily_rain",
    "evap_pan",
    "max_temp",
    "min_temp",
    ]

base_url = "https://s3-ap-southeast-2.amazonaws.com/silo-open-data/daily/"

product = f"{variable}/{year}/{year}{month}{day}.{variable}.tif"



f'https://s3-ap-southeast-2.amazonaws.com/silo-open-data/annual/rh_tmax/2020.rh_tmax.nc'

