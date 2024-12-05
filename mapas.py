import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import pandas as pd

plt.rc("font", family="Arial")
plt.style.use('bmh')

# Load datasets
dt = xr.open_dataset(r"datasets/media_anual.nc")
dt = dt.sel(lat=slice(-60, 15), lon=slice(-90, -25), time=slice("2002-01-01", "2022-12-01"))
dt2 = xr.open_dataset(r"datasets/anomalia_anual.nc")
dt2 = dt2.sel(lat=slice(-60, 15), lon=slice(-90, -25), time=slice("2002-01-01", "2022-12-01"))

# Print datasets for reference (optional)
print(dt)
print(dt2)

# Compute mean values
fwi = dt["fwi"]
fwi_anomalia = dt2["fwi"]

# Create a figure with subplots
fig, axs = plt.subplots(nrows=2, ncols=4, figsize=(20, 10), subplot_kw={'projection': ccrs.PlateCarree()})

for time in fwi['time']:
    # Select the data for the current timestep
    data = fwi.sel(time=time)
    data1 = fwi_anomalia.sel(time=time)
    # Plot the data (NetCDF variable)
    map1 = plt.contourf(data1['lon'], data1['lat'], data1[:, :], cmap="RdYlGn", levels=9)
    plt.colorbar(label='FWI Value')  # Adjust label to your variable

    # Add titles and labels
    plt.title(f'FWI at {str(time.values)}')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    plt.show()
