"""
Table 4: Values of parameters used in the SporacleEzy model: (Salam et al. 2007)

| Parameter         | Definition                                                                            | Unit | Value                                                      |
|-------------------|---------------------------------------------------------------------------------------|------|------------------------------------------------------------|
| SAR-on            | No. of days favourable for pseudothecial maturation before onset of ascospore release | days | Australia, Canada, France, UK: 18; Poland: 18              |
| Rain-threshold    | Lower limit of daily rain favourable for pseudothecial maturation                     | mm   | Australia, Canada, France, UK: 1.0; Poland: 1.25           |
| T-lower-threshold | Lower limit of mean daily temperature favourable for pseudothecial maturation         | °C   | 6                                                          |
| T-upper-threshold | Upper limit of mean daily temperature favourable for pseudothecial maturation         | °C   | Australia, Canada, France, UK: 22; Poland: 24              |
"""
import numpy as np

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