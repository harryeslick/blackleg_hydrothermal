# Welcome to Blackleg Hydro-thermal

This package is a python implementation three published models for prediction of Blackleg (*Leptosphaeria maculans*) Pseudothecia maturation date based on weather observations. 
The three models are: 

* Blackleg sporacle (Salam et al., 2007)
* SporacleEzy (Salam et al., 2007)
* Blackleg hydrothermal (Bondad et al., 2024)

Each model has two implementations to run the model using 1) a single point location, 2) a raster grid. 
The 2D raster grid implementation can be used for a single point as well, however the code is harder to follow, therefore the 1D model has been retained.

Each model calculates the cumulative pseudothecia maturation index, based on the number of suitable days since harvest. Blackleg hydrothermal accumulates thermal time, rather than simply the number of days. The models calculate the cummulative pseudothecia maturation index and the expected date on the first spore shower. 

Further translation of results into agronomic advice / risk analysis is not included. 

## Bibliography

Bondad JJ, Whish JPM, Sprague SJ, Van de Wuow AP, Barry KM and Harrison MT (2024) ‘Modelling crop management and environmental effects on the development of Leptosphaeria maculans pseudothecia’, European Journal of Plant Pathology, doi:10.1007/s10658-024-02961-7.

Salam MU, Fitt BDL, Aubertot J-N, Diggle AJ, Huang YJ, Barbetti MJ, Gladders P, Jȩdryczka M, Khangura RK, Wratten N, Fernando WGD, Penaud A, Pinochet X and Sivasithamparam K (2007) ‘Two weather-based models for predicting the onset of seasonal release of ascospores of Leptosphaeria maculans or L. biglobosa’, Plant Pathology, 56(3):412–423, doi:10.1111/j.1365-3059.2006.01551.x.
