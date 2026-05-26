import xarray as xr
import geopandas as gpd
import rioxarray
from shapely.geometry import mapping
import os
import numpy as np

# Abrir o dataset e selecionar a variável e o intervalo de datas desejado
dt = xr.open_mfdataset("D:/FACULDADE/FWI/*.nc")["fwinx"].sel(valid_time=slice("1940-01-01", "2023-12-31"))

# Ajustar longitudes se necessário (de 0-360 para -180 a 180)
dt.coords["longitude"] = (dt.coords["longitude"] + 180) % 360 - 180
dt = dt.sortby(dt.longitude)

# Abrir shapefile e recortar o NetCDF
shapefile = gpd.read_file("D:/FACULDADE/FWI/CLUSTER_RECORTADO.gpkg").to_crs(4674)
ds = dt.rio.set_spatial_dims(x_dim="longitude", y_dim="latitude", inplace=True)
ds = ds.rio.write_crs(f"epsg:4674", inplace=True)
dt = ds.rio.clip(shapefile.geometry.apply(mapping), drop=True)

# Reamostrar os dados para médias sazonais
seasonal_mean = dt.resample(valid_time="QS-DEC").mean(dim="valid_time")

# Criar a coordenada 'season' manualmente
season_mapping = {12: "DJF", 1: "DJF", 2: "DJF",
                  3: "MAM", 4: "MAM", 5: "MAM",
                  6: "JJA", 7: "JJA", 8: "JJA",
                  9: "SON", 10: "SON", 11: "SON"}

season_labels = [season_mapping[m] for m in seasonal_mean["valid_time"].dt.month.values]
seasonal_mean = seasonal_mean.assign_coords(season=("valid_time", season_labels))

# Calcular a climatologia sazonal
climatological_mean = seasonal_mean.groupby("season").mean(dim="valid_time")

# Calcular as anomalias sazonais
seasonal_anomaly = seasonal_mean.groupby("season") - climatological_mean

# Criar diretório de saída
os.makedirs("datasets/ANOMALIAS/SAZONAIS", exist_ok=True)

# Criar intervalos de décadas
bins = np.arange(1940, 2030, 10)  # De 1940 até 2029, em passos de 10 anos

# Salvar os arquivos por década
for start_year in bins[:-1]:  # Ignora o último valor (2030)
    end_year = start_year + 9
    decade_anomaly = seasonal_anomaly.sel(valid_time=slice(f"{start_year}-01-01", f"{end_year}-12-31"))

    # Fazer a média para cada estação dentro da década
    decade_anomaly_mean = decade_anomaly.groupby("season").mean(dim="valid_time")

    # Salvar o arquivo NetCDF
    output_path = f"datasets/ANOMALIAS/SAZONAIS/ANOMALIA_SAZONAL_{start_year}-{end_year}.nc"
    decade_anomaly_mean.to_netcdf(output_path)
    print(f"Anomalia sazonal para a década {start_year}-{end_year} salva.")
