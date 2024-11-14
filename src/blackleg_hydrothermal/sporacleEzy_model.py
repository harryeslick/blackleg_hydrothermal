"""
Table 4: Values of parameters used in the SporacleEzy model: (Salam et al. 2007)

| Parameter         | Definition                                                                            | Unit | Value                                                      |
|-------------------|---------------------------------------------------------------------------------------|------|------------------------------------------------------------|
| SAR-on            | No. of days favourable for pseudothecial maturation before onset of ascospore release | days | Australia, Canada, France, UK: 18; Poland: 18              |
| Rain-threshold    | Lower limit of daily rain favourable for pseudothecial maturation                     | mm   | Australia, Canada, France, UK: 1.0; Poland: 1.25           |
| T-lower-threshold | Lower limit of mean daily temperature favourable for pseudothecial maturation         | °C   | 6                                                          |
| T-upper-threshold | Upper limit of mean daily temperature favourable for pseudothecial maturation         | °C   | Australia, Canada, France, UK: 22; Poland: 24              |
"""

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
    return int(all(conditions))


def blackleg_sporacleEzy_run(df):

    df['FPM'] = df.apply(lambda row: sporacleEzy_FMP(row['rainfall'], row['air_tmax'], row['air_tmin']), axis=1)
    df['FPM_cumsum'] = df['FPM'].cumsum()
    pm_date = df.loc[(df['FPM_cumsum'] <= SAR_ON), "date"].iloc[-1]
    print("pseudothecial maturation date", pm_date)
    return df, pm_date