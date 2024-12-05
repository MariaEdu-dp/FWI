import xarray as xr
import geopandas as gpd
import rioxarray
from shapely.geometry import mapping
import os

data = xr.open_mfdataset("datasets/FWI/*.nc")

data.coords["longitude"] = (data.coords["longitude"] + 180) % 360 - 180
data = data.sortby(data.longitude)

shapefile = gpd.read_file("ecorregioes/ecorregiões_cluster/CLUSTER_RECORTADO.gpkg").to_crs(4674)
geom_sa = shapefile.geometry
print(geom_sa)

# Definir as dimensões espaciais e o CRS no NetCDF
ds = data.rio.set_spatial_dims(x_dim="longitude", y_dim="latitude", inplace=True)
ds = ds.rio.write_crs(f"epsg:4674", inplace=True)
# Recortar o NetCDF para a área da ecorregião
data = ds.rio.clip(shapefile.geometry.apply(mapping), drop=True)

#data_1940 = data.sel(valid_time=slice("1940-01-03", "1949-12-31"))
#data_1950 = data.sel(valid_time=slice("1950-01-01", "1959-12-31"))
#data_1960 = data.sel(valid_time=slice("1960-01-01", "1969-12-31"))
#data_1970 = data.sel(valid_time=slice("1970-01-01", "1979-12-31"))
#data_1980 = data.sel(valid_time=slice("1980-01-01", "1989-12-31"))
#data_1990 = data.sel(valid_time=slice("1990-01-01", "1999-12-31"))
#data_2000 = data.sel(valid_time=slice("2000-01-01", "2009-12-31"))
#data_2010 = data.sel(valid_time=slice("2010-01-01", "2019-12-31"))
#data_2020 = data.sel(valid_time=slice("2020-01-01", "2023-12-31"))

# Médias

# data = [data_1940, data_1950, data_1960, data_1970, data_1980, data_1990, data_2000, data_2010, data_2020]

#for dataset in data:
    #ano = dataset.valid_time.dt.year.values[:1]
    #print(ano)

    #polyfit = dataset.polyfit(dim="valid_time", deg=1) * 1e9 * 60 * 60 * 24 * len(dataset.valid_time.values)
    #polyfit.to_netcdf(f"datasets/regressao/tendencia_{ano}.nc")

polyfit_total = data.polyfit(dim="valid_time", deg=1) * 1e9 * 60 * 60 * 24 * len(data.valid_time.values)
polyfit_total.to_netcdf("tendencia_total.nc")
