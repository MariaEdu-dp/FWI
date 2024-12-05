import xarray as xr
import os
import rioxarray
from shapely.geometry import mapping
import geopandas as gpd

from ANOMALIA_ANUAL import output_dir

# Abrir o dataset e selecionar a variável e o intervalo de datas desejado
dt = xr.open_mfdataset("datasets/FWI/*.nc")["fwinx"].sel(valid_time=slice("1940-01-01", "2023-12-31"))

dt.coords["longitude"] = (dt.coords["longitude"] + 180) % 360 - 180
dt = dt.sortby(dt.longitude)

shapefile = gpd.read_file("CLUSTER_ID/CLUSTER_ID.shp").to_crs(4674)
geom_sa = shapefile.geometry
print(geom_sa)

# Definir as dimensões espaciais e o CRS no NetCDF
ds = dt.rio.set_spatial_dims(x_dim="longitude", y_dim="latitude", inplace=True)
ds = ds.rio.write_crs(f"epsg:4674", inplace=True)
# Recortar o NetCDF para a área da ecorregião
dt = ds.rio.clip(shapefile.geometry.apply(mapping), drop=True)

# Calcular a média sazonal dos dados diários, começando o verão em novembro
seasonal_mean = dt.resample(valid_time="QS-NOV").mean(dim="valid_time")

# Calcular a média climatológica para cada estação ao longo do período
climatological_seasonal_mean = seasonal_mean.groupby("valid_time.season").mean(dim="valid_time")

# Calcular as anomalias sazonais subtraindo a média climatológica de cada estação
seasonal_anomaly = seasonal_mean.groupby("valid_time.season") - climatological_seasonal_mean

# Calcular a anomalia sazonal total (média das anomalias sazonais ao longo dos anos)
seasonal_anomaly_total = seasonal_anomaly.groupby("valid_time.season").mean(dim="valid_time")

# Salvar cada estação de cada ano como um arquivo NetCDF separado
for time in seasonal_anomaly.valid_time:
    # Extrair o ano e a estação atual
    year = time.dt.year
    season = time.dt.season

    # Selecionar os dados de anomalia para este período
    anomaly_season = seasonal_anomaly.sel(valid_time=time)

    # Salvar o arquivo NetCDF
    anomaly_season.to_netcdf(f"anomalia_sazonal/ANOMALIA_SAZONAL_{season}_{year}.nc")
    print(f"Anomalia sazonal para {season} {year} salva.")
