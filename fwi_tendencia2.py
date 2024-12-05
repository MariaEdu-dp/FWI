import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
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
fwi = dt["fwi"].mean(("lat", "lon"))
fwi_anomalia = dt2["fwi"].mean(("lat", "lon"))

# Create the figure and axes
fig, ax = plt.subplots(2, sharex=True, figsize=(10, 8))

# Plot FWI data
ax[0].plot(fwi["time"], fwi.values, marker='o', label="FWI", color='Firebrick')

# Calculate and plot the trend line for FWI
z_fwi = np.polyfit(fwi["time"].values.astype(np.int64), fwi.values, 1)
p_fwi = np.poly1d(z_fwi)
ax[0].plot(fwi["time"], p_fwi(fwi["time"].values.astype(np.int64)), linestyle='--', color='black', lw=0.8, label='Annual anomalia')

ax[0].set_title("FWI")
ax[0].legend()
ax[0].margins(x=0)

# Plot FWI anomalia data
ax[1].plot(fwi.time, fwi_anomalia.values, marker='o', color='olivedrab', label='Anomalia anual')

# Calculate and plot the trend line for FWI anomalia
z_anomalia = np.polyfit(fwi["time"].values.astype(np.int64), fwi_anomalia.values, 1)
p_anomalia = np.poly1d(z_anomalia)
# ax[1].plot(fwi["time"], p_anomalia(fwi["time"].values.astype(np.int64)), linestyle='--', color='r', label='Tendência anomalia')

ax[1].set_title("Annual FWI anomalia")
# ax[1].legend()
ax[1].margins(x=0)

# Formatting
plt.xlabel("Time")
plt.xticks(rotation=45)
plt.tight_layout()

# Show the plot
plt.show()
