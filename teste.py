import xarray as xr
import matplotlib.pyplot as plt

dt = xr.open_dataset(r"datasets/media_anual.nc")
dt2 = xr.open_dataset(r"datasets/anomalia_anual.nc")
print(dt)

fwi = dt["fwi"].mean(("lat", "lon"))
fwi_anomalia = dt2["fwi"].mean(("lat", "lon"))

fig, ax = plt.subplots(2, sharex=True)

ax[0].plot(fwi.time, fwi)
ax[1].plot(fwi.time, fwi_anomalia)

plt.show()
