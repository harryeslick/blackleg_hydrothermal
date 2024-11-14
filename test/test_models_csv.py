
from blackleg_hydrothermal.blackleg_sporacle_model import blackleg_sporacle_run
from blackleg_hydrothermal.sporacleEzy_model import blackleg_sporacleEzy_run
import pandas as pd


df = pd.read_csv("../data/northam_NO__2022-06-20.csv")

out, dt = blackleg_sporacleEzy_run(df)

out, dt = blackleg_sporacle_run(df)

# %%
