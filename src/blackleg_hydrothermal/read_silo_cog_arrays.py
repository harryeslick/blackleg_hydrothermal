

import datetime
import logging

import numpy as np
import rasterio
from rasterio.features import geometry_window


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


def create_cog_url(variable, date: datetime.date):
    base_url = "https://s3-ap-southeast-2.amazonaws.com/silo-open-data/Official/daily/"
    product_suffix = f"{variable}/{date.year}/{date.strftime("%Y%m%d")}.{variable}.tif"
    cog_url = base_url+product_suffix
    return cog_url


def read_cog_arrays(startdate,
                    enddate,
                    aoi,
                    variables =[
                        "daily_rain",
                        "max_temp",
                        "min_temp",
                        "evap_pan",
                        ],
                    ):
    """
    Read a sequence of COG weather files from SILO for a given date range and list of variables

    Args:
        startdate: datetime.date
        enddate: datetime.date
        variables: list of SILO variable strings eg variables =["daily_rain","evap_pan","max_temp","min_temp",]
        aoi: shapely.geometry.Polygon only reads data within the AOI

    Returns:
        dict of numpy arrays, keys == variables
    """
    date_sequence = [startdate + datetime.timedelta(days=x) for x in range((enddate - startdate).days + 1)]
    assert len(date_sequence) <365, "More than 365 days requested, are you sure?"


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
    return all_grids