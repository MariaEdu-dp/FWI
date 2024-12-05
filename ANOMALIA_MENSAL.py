import xarray as xr
import geopandas as gpd
import rioxarray
from shapely.geometry import mapping
import os

# Abrir o dataset e selecionar a variável e o intervalo de datas desejado
dt = xr.open_mfdataset("datasets/FWI/*.nc")["fwinx"].sel(valid_time=slice("1940-01-01", "2023-12-31"))
# Ajustar longitudes se necessário (de 0-360 para -180 a 180)
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

# Calcular a média anual dos dados diários
monthly_mean = dt.resample(valid_time="ME").mean(dim="valid_time")
print("REAMOSTRAGEM MENSAL FEITA.")

# Calcular a média climatológica do período
climatological_mean = monthly_mean(dim="valid_time")
print("CLIMATOLOGIA MENSAL CALCULADA.")

# Calcular as anomalias anuais
monthly_anomaly = monthly_mean - climatological_mean
print("ANOMALIA MENSAL CALCULADA", _anomaly)


# Criar um diretório para salvar os arquivos de saída
output_dir = "anomalia_mensal"
os.makedirs(output_dir, exist_ok=True)

# Salvar cada ano de anomalia como um arquivo NetCDF separado
for year in annual_anomaly.valid_time.dt.month.values:
    # Selecionar a anomalia para o ano atual
    anomaly_year = annual_anomaly.sel(valid_time=str(year))
    anomaly_year.to_netcdf(f"anomalia/ANOMALIA_{year}.nc")

    print(f"Anomalia para o ano {year} salva.")
