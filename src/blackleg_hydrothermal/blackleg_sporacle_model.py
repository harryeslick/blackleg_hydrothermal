
PM_BEGIN = 43
RAIN_THRESHOLD = 4
RAIN_THRESHOLD_DAYS = 7
T_LOWER_THRESHOLD = 3
T_UPPER_THRESHOLD = 22
T_THRESHOLD_DAYS = 10


def blackleg_sporacle_FPM(rainfall, tmax, tmin):
    """
    Determines favourable_pseudothecial_maturity (FPM) for each day

    Args:
        rainfall: mm rain in a day
        tmax: daily max temperature
        tmin: daily min temperature

    Returns:
        int 1 or 0
    """
    conditions = [
        rainfall >= RAIN_THRESHOLD,
        tmin >= T_LOWER_THRESHOLD,
        tmax <= T_UPPER_THRESHOLD
    ]
    return int(all(conditions))


def blackleg_sporacle_run(df):
    # rolling sum method results in nan values for the first 3 days  / 10 for temp.
    # this results in loss of fpm values where summer rainfall was observed, eg 1999 Mount Barker
    # as a result, the 2d model performs worse than the 1d model,agaist the data
    # however, the 2d model is a more correct representation of the model in the literature
    df["rain7"] = df["rainfall"].rolling(window=RAIN_THRESHOLD_DAYS).sum()
    df["air_tmean"] = (df["air_tmax"] + df["air_tmin"])/2
    df["air_tmean10"] = df["air_tmean"].rolling(window=T_THRESHOLD_DAYS).mean()

    df['FPM'] = df.apply(lambda row: blackleg_sporacle_FPM(row['rain7'], row['air_tmean10'], row['air_tmean']), axis=1)
    df['FPM_cumsum'] = df['FPM'].cumsum()

    pm_date = df.loc[(df['FPM_cumsum'] <= PM_BEGIN), "date"].iloc[-1]
    print("pseudothecial maturation date", pm_date)
    return df, pm_date