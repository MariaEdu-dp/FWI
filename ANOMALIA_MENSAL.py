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

shapefile = gpd.read_file("D:/FACULDADE/FWI/CLUSTER_RECORTADO.gpkg").to_crs(4674)

# Definir as dimensões espaciais e o CRS no NetCDF
ds = dt.rio.set_spatial_dims(x_dim="longitude", y_dim="latitude", inplace=True)
ds = ds.rio.write_crs(f"epsg:4674", inplace=True)

# Recortar o NetCDF para a área da ecorregião
dt = ds.rio.clip(shapefile.geometry.apply(mapping), drop=True)

# Calcular a média mensal dos dados diários
monthly_mean = dt.resample(valid_time="MS").mean(dim="valid_time")

# Calcular a climatologia mensal (média de cada mês ao longo de todo o período)
climatological_mean = monthly_mean.groupby("valid_time.month").mean(dim="valid_time")

# Calcular as anomalias mensais
monthly_anomaly = monthly_mean.groupby("valid_time.month") - climatological_mean

# Criar um diretório para salvar os arquivos de saída
os.makedirs("datasets/ANOMALIAS/MENSAIS", exist_ok=True)

# Criar intervalos de 10 anos
bins = np.arange(1940, 2030, 10)  # De 1940 até 2029, em passos de 10 anos

# Salvar os dados em blocos de décadas
for start_year in bins[:-1]:  # Ignora o último valor (2030)
    end_year = start_year + 9  # Último ano da década
    decade_anomaly = monthly_anomaly.sel(valid_time=slice(f"{start_year}-01-01", f"{end_year}-12-31"))

    # Agora, fazer a média para cada mês dentro dessa década
    decade_anomaly_mean = decade_anomaly.groupby("valid_time.month").mean(dim="valid_time")

    # Salvar o arquivo NetCDF
    output_path = f"datasets/ANOMALIAS/MENSAIS/ANOMALIA_MENSAL_{start_year}-{end_year}.nc"
    decade_anomaly_mean.to_netcdf(output_path)
    print(f"Anomalia mensal para a década {start_year}-{end_year} salva.")

