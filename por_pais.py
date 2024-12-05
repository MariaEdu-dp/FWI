import geopandas as gpd
import matplotlib.pyplot as plt
import rioxarray
from shapely.geometry import mapping
import xarray as xr
import pandas as pd
import numpy as np

plt.rc("font", family="Arial")
plt.style.use('bmh')


# Open South America shapefile
SA = r"america_do_sul/Lim_america_do_sul_2021.shp"
SA = gpd.read_file(SA, engine='pyogrio')
SA = SA.to_crs(4674)
print(SA)

# Load datasets
dt = xr.open_mfdataset(r"datasets/FWI/*nc")
print(dt)
# dt = dt.drop_vars("time_bnds")
dt1 = dt.sel(valid_time=slice("1940-01-03", "2023-12-31"))
print(dt)

# Lista para armazenar os datasets recortados e os nomes
recortes = []
nomes = []

# Loop para recorte
for idx, row in SA.iterrows():
