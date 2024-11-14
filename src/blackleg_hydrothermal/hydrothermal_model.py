"""
Bondad JJ, Whish JPM, Sprague SJ, Van de Wuow AP, Barry KM and Harrison MT (2024) ‘Modelling crop management and environmental effects on the development of Leptosphaeria maculans pseudothecia’, European Journal of Plant Pathology, doi:10.1007/s10658-024-02961-7.


"""

# SporacleEzy model parameters
from blackleg_hydrothermal.thermal_time import gdd_sinusoidal

TT_REQUIRED = 196


def hydrothermal_FMP(rainfall, tmax, tmin, evaporation):
    if rainfall < evaporation:
        return 0
    else:
        return gdd_sinusoidal(tmax, tmin, tt_x = [5, 22, 22],tt_y = [0, 22, 0])


def hydrothermal_run(df):
    assert all([c in df.columns for c in ['rainfall', 'air_tmax', 'air_tmin', 'evap_comb']]), "weather data columns missing, designed to match weatherOz/silo"
    df['FPM'] = df.apply(lambda row: hydrothermal_FMP(row['rainfall'], row['air_tmax'], row['air_tmin'], row['evap_comb']), axis=1)
    df['FPM_cumsum'] = df['FPM'].cumsum()
    pm_date = df.loc[(df['FPM_cumsum'] <= TT_REQUIRED), "date"].iloc[-1]
    print("pseudothecial maturation date", pm_date)
    return df, pm_date