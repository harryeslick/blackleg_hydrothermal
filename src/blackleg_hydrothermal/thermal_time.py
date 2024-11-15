import pandas as pd
import numpy as np


# Define function to calculate GDD for a row
def gdd_basic(air_tmax, air_tmin, Tbase=0):
    """
    calculate growing degree days (GDD) using basic method
    mean temperature subtract base temperature

    Args:
        air_tmax: daily max air temperature
        air_tmin: daily min air temperature
        Tbase: low temperature threshold Defaults to 0.

    Returns:
        Thermal time accumulation: float

    Examples:
    >>> gdd_basic(5, 15, 18)
    8
    >>> gdd_basic(20, 30, 18)
    0
    >>> gdd_basic(18, 20, 18)
    1
    """
    average_temp = (air_tmax + air_tmin) / 2
    gdd = average_temp - Tbase
    if gdd < 0:
        gdd = 0
    return gdd


def gdd_cardinal(air_tmax, air_tmin, tt_x = [0, 26, 34], tt_y = [0, 26, 0]):
    """
    _summary_

    https://www.apsim.info/wp-content/uploads/2019/09/WheatDocumentation.pdf

    Args:
        air_tmax: daily max air temperature
        air_tmin: daily min air temperature
        tt_x: temperature range[min, optimum, max]. Defaults to [0, 26, 34] (wheat).
        tt_y: tt accumulation at each value of tt_x Defaults to [0, 26, 0] (wheat).

    Returns:
        Thermal time accumulation: float

    Examples:
    >>> gdd_cardinal(10,10, tt_x = [0, 10, 30], tt_y = [0, 10, 0])
    10

    # apply to df
    >>> df["gdd_basic"] = df.apply(lambda row: gdd_basic(row['air_tmax'], row['air_tmin']), axis=1)

    """

    mean_t = (air_tmax + air_tmin) / 2
    tt = np.interp(mean_t, tt_x, tt_y)
    return tt

def get_diurnal_fraction(n_segments=8):
    hours_seq = np.linspace(12/n_segments/2, 12-12/n_segments/2, n_segments)
    # Create a sine sequence that starts from a peak and ends at a trough
    sin_y = np.sin((np.pi / 12) * (hours_seq + 6))
    # normalise  to range from 0 to 1
    sin_y = (sin_y+1)/2
    df = pd.DataFrame({'hour': hours_seq, 'frac': sin_y}).round(4)
    return df

def gdd_sinusoidal(air_tmax, air_tmin,n_time_steps=24, tt_x = [0, 26, 34], tt_y = [0, 26, 0]):
    """
    interpolate temperature sequence between daily min and max using sinusoidal approximation
    accumulate tt for each time period using cardinal temperatures
    Advantages over daily average: allows gdd accumulation for partial days when average temp outside of cardinal range

    https://www.apsim.info/wp-content/uploads/2019/09/WheatDocumentation.pdf
    https://builds.apsim.info/api/nextgen/docs/lifecycle.pdf

    Args:
        air_tmax: daily max air temperature
        air_tmin: daily min air temperature
        n_time_steps: The number of steps to divide a day into Defaults to 24 (hourly).
        tt_x: temperature range[min, optimum, max]. Defaults to [0, 26, 34] (wheat).
        tt_y: tt accumulation at each value of tt_x Defaults to [0, 26, 0] (wheat).

    Returns:
        Thermal time accumulation: float

    Examples:
    >>> df["gdd_sinusoidal"] = df.apply(lambda row: gdd_sinusoidal(row['air_tmax'], row['air_tmin']), axis=1)

    """
    assert air_tmax >= air_tmin, "air_tmax must be greater than air_tmin"
    assert tt_x == sorted(tt_x), "tt_x must be in ascending order"

    df = get_diurnal_fraction(n_segments=n_time_steps)

    # interpolate temperature sequence between daily min and max
    temp_seq = np.interp(df.frac, [0,1], [air_tmin, air_tmax])
    # get tt for each time period using cardinal temperatures
    tt_seq = np.interp(temp_seq, tt_x, tt_y)
    tt = tt_seq.mean()
    return tt


def gdd_sinusoidal_2d(air_tmax, air_tmin,n_time_steps=24, tt_x = [0, 26, 34], tt_y = [0, 26, 0]):
    """
    interpolate temperature sequence between daily min and max using sinusoidal approximation
    accumulate tt for each time period using cardinal temperatures
    Advantages over daily average: allows gdd accumulation for partial days when average temp outside of cardinal range

    https://www.apsim.info/wp-content/uploads/2019/09/WheatDocumentation.pdf
    https://builds.apsim.info/api/nextgen/docs/lifecycle.pdf

    Args:
        air_tmax: daily max air temperature
        air_tmin: daily min air temperature
        n_time_steps: The number of steps to divide a day into Defaults to 24 (hourly).
        tt_x: temperature range[min, optimum, max]. Defaults to [0, 26, 34] (wheat).
        tt_y: tt accumulation at each value of tt_x Defaults to [0, 26, 0] (wheat).

    Returns:
        Thermal time accumulation: float

    Examples:
    >>> df["gdd_sinusoidal"] = df.apply(lambda row: gdd_sinusoidal(row['air_tmax'], row['air_tmin']), axis=1)

    """
    assert all(air_tmax >= air_tmin), "air_tmax must be greater than air_tmin"
    assert tt_x == sorted(tt_x), "tt_x must be in ascending order"

    df = get_diurnal_fraction(n_segments=n_time_steps)
    dfrac = df.frac.to_numpy()

    # interpolate temperature sequence between daily min and max
    air_tmin = np.array(air_tmin)[:, None]
    air_tmax = np.array(air_tmax)[:, None]
    temp_seq = air_tmin + (air_tmax - air_tmin) * dfrac[None,:]


    # get tt for each time period using cardinal temperatures
    tt_seq = np.interp(temp_seq, tt_x, tt_y)
    # take the mean to give a single tt value for each day
    tt = tt_seq.mean(axis=-1)
    return tt