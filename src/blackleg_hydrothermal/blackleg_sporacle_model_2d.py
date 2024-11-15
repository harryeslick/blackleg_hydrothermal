import numpy as np
from scipy.ndimage import convolve1d

PM_BEGIN = 43
RAIN_THRESHOLD = 4
RAIN_THRESHOLD_DAYS = 7
T_LOWER_THRESHOLD = 3
T_UPPER_THRESHOLD = 22
T_THRESHOLD_DAYS = 10


def blackleg_sporacle_FPM(rainfall, t_rolling_mean, t_mean):
    """
    Determines favourable_pseudothecial_maturity (FPM) for each day

    Args:
        rainfall: mm rain in a day
        t_rolling_mean: daily max temperature
        t_mean: daily min temperature

    Returns:
        int 1 or 0
    """
    conditions = (rainfall >= RAIN_THRESHOLD) & (t_mean >= T_LOWER_THRESHOLD) & (t_rolling_mean <= T_UPPER_THRESHOLD)
    return conditions.astype(int)

def blackleg_sporacle_FPM_cumulative(rainfall, tmax, tmin):
    assert rainfall.shape == tmax.shape == tmin.shape, "Input arrays must have the same shape"
    # rolling sum of rainfall
    rainfall7 = convolve1d(rainfall, weights=np.ones(RAIN_THRESHOLD_DAYS),origin=-3, axis=0, mode="constant")
    air_tmean = (tmax + tmin)/2
    # rolling mean of temp (weights are 1/n to give the mean)
    air_tmean10 = convolve1d(air_tmean, weights=np.ones(T_THRESHOLD_DAYS)/T_THRESHOLD_DAYS,origin=-(T_THRESHOLD_DAYS//2), axis=0, mode="reflect")

    fpm = blackleg_sporacle_FPM(rainfall7, air_tmean10, air_tmean)
    fpm_cumsum = fpm.cumsum(axis=0)
    # current_pm = fpm_cumsum[-1]

    # apply original data mask
    mask = np.isnan(rainfall)
    fpm_cumsum = fpm_cumsum.astype(float)
    fpm_cumsum[mask] = np.nan

    return fpm_cumsum


def get_pm_date_blackleg_sporacle(rainfall, tmax, tmin, date_sequence):
    assert len(rainfall) == len(tmax) == len(tmin) == len(date_sequence), "All input arrays must have the same length"
    fpm = blackleg_sporacle_FPM_cumulative(rainfall, tmax, tmin)
    idx = np.argmax(fpm >= PM_BEGIN, axis=0)
    pm_date = np.vectorize(lambda x: date_sequence[x])(idx)
    return pm_date