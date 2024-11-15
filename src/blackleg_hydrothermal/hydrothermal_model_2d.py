"""
Bondad JJ, Whish JPM, Sprague SJ, Van de Wuow AP, Barry KM and Harrison MT (2024) ‘Modelling crop management and environmental effects on the development of Leptosphaeria maculans pseudothecia’, European Journal of Plant Pathology, doi:10.1007/s10658-024-02961-7.


"""

# SporacleEzy model parameters
import numpy as np
from blackleg_hydrothermal.thermal_time import gdd_sinusoidal_2d

TT_REQUIRED = 196


# def hydrothermal_FMP(rainfall, tmax, tmin, evaporation):
#     if rainfall < evaporation:
#         return 0
#     else:
#         return gdd_sinusoidal(tmax, tmin, tt_x = [5, 22, 22],tt_y = [0, 22, 0])


# def hydrothermal_run(df):
#     assert all([c in df.columns for c in ['rainfall', 'air_tmax', 'air_tmin', 'evap_comb']]), "weather data columns missing, designed to match weatherOz/silo"
#     df['FPM'] = df.apply(lambda row: hydrothermal_FMP(row['rainfall'], row['air_tmax'], row['air_tmin'], row['evap_comb']), axis=1)
#     df['FPM_cumsum'] = df['FPM'].cumsum()
#     pm_date = df.loc[(df['FPM_cumsum'] <= TT_REQUIRED), "date"].iloc[-1]
#     print("pseudothecial maturation date", pm_date)
#     return df, pm_date

# %%											 |


def hydrothermal_FPM(rainfall, tmax, tmin, evaporation):
    tt = gdd_sinusoidal_2d(tmax, tmin, tt_x = [5, 22, 22],tt_y = [0, 22, 0])
    conditions = (np.array(rainfall) >= np.array(evaporation))
    return conditions.astype(int) * tt


def hydrothermal_FPM_cumulative(rainfall, tmax, tmin, evaporation):
    assert rainfall.shape == tmax.shape == tmin.shape == evaporation.shape, "Input arrays must have the same shape"

    fpm = hydrothermal_FPM(rainfall, tmax, tmin, evaporation)
    fpm_cumsum = fpm.cumsum(axis=0)
    # current_pm = fpm_cumsum[-1]
    return fpm_cumsum

def get_pm_date_hydrothermal(rainfall, tmax, tmin, evaporation, date_sequence):
    assert len(rainfall) == len(tmax) == len(tmin) == len(evaporation) == len(date_sequence), "All input arrays must have the same length"
    fpm_cumsum = hydrothermal_FPM_cumulative(rainfall, tmax, tmin, evaporation)

    idx = np.where(fpm_cumsum >= TT_REQUIRED)[0][0]

    # idx = np.argmax(fpm_cumsum >= TT_REQUIRED, axis=0)
    pm_date = np.vectorize(lambda x: date_sequence[x])(idx)
    return pm_date