import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from mpl_toolkits.basemap import Basemap
from matplotlib_scalebar.scalebar import ScaleBar

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
fig, axs = plt.subplots(nrows=2, ncols=5, figsize=(20, 10), subplot_kw={'projection': ccrs.PlateCarree()})

# Flatten axs for easy indexing
axs = axs.flatten()

for i, time in enumerate(fwi['time']):
    if i >= len(axs):  # Prevent accessing axes beyond available
        break

    # Select the data for the current timestep
    data = fwi.sel(time=time)
    data1 = fwi_anomalia.sel(time=time)

    # Plot the data (NetCDF variable)
    contour = axs[i].contourf(data1['lon'], data1['lat'], data1, cmap="RdYlGn_r", levels=11, transform=ccrs.PlateCarree())

    # Set title using the year from time.values
    year = time.dt.year.values.item()  # Extract the year as an integer
    axs[i].set_title(f'{year}')
    data1.to_netcdf(f"anomalia/Anomalia_{year}.nc")

    axs[i].set_xlabel('Longitude')
    axs[i].set_ylabel('Latitude')
    # Add features for countries and oceans
    axs[i].add_feature(cfeature.BORDERS, linewidth=0.5)
    axs[i].add_feature(cfeature.COASTLINE, linewidth=1)
    axs[i].add_feature(cfeature.LAND, edgecolor='black')
    axs[i].add_feature(cfeature.OCEAN, color="lightblue")
    axs[i].add_feature(cfeature.LAKES, edgecolor='black')

    # Add gridlines only for labels
    gl = axs[i].gridlines(draw_labels=True, xlocs=np.arange(-90, -25, 20), ylocs=np.arange(-60, 20, 20), color='none')
    gl.xlabels_top = False  # Disable top labels
    gl.ylabels_right = False  # Disable right labels
    gl.xlabel_style = {'size': 10}  # Customize x-label style
    gl.ylabel_style = {'size': 10}  # Customize y-label style
    # Base definitions
    scalebar = ScaleBar(20000, location='lower right', rotation="horizontal", dimension="si-length",
                        length_fraction=0.30, frameon=True)
    # Add scalebar and North arrow
    axs[i].add_artist(scalebar)
    # Put north arrow
    x, y, arrow_length = 0.06, 0.09, 0.06
    #axs[i].annotate('N', xy=(x, y), xytext=(x, y - arrow_length), arrowprops=dict(facecolor='black', width=5, headwidth=15),
                # ha='center', va='center', fontsize=16, xycoords=axs[i].transAxes)

    # Add colorbar to the current subplot
    cbar = plt.colorbar(contour, ax=axs[i], orientation='vertical', pad=0.02, label='FWI Value')
plt.show()
