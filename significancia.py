import xarray as xr
import numpy as np
from scipy.stats import t
from shapely.geometry import mapping
import geopandas as gpd

# Abrir o dataset e selecionar a variável e o intervalo de datas desejado
dt = xr.open_mfdataset("datasets/FWI/*.nc")["fwinx"].sel(valid_time=slice("1940-01-01", "2023-12-31"))

# Corrigir a longitude para o intervalo [-180, 180]
dt.coords["longitude"] = (dt.coords["longitude"] + 180) % 360 - 180
dt = dt.sortby(dt.longitude)

# Ler o shapefile e configurar o CRS
shapefile = gpd.read_file("CLUSTER_ID/CLUSTER_ID.shp").to_crs(4674)
geom_sa = shapefile.geometry

# Definir as dimensões espaciais e o CRS no NetCDF
ds = dt.rio.set_spatial_dims(x_dim="longitude", y_dim="latitude", inplace=True)
ds = ds.rio.write_crs(f"epsg:4674", inplace=True)

# Recortar o NetCDF para a área da ecorregião
dt = ds.rio.clip(shapefile.geometry.apply(mapping), drop=True)


# Supondo que `dt` é o seu DataArray com dimensões ("valid_time", "latitude", "longitude")
# Criar a variável de tempo como a variável independente
time = dt["valid_time"].astype(float)

# Calculando as médias
time_mean = time.mean(dim="valid_time")
data_mean = dt.mean(dim="valid_time")

# Calculando a covariância entre tempo e a variável dependente
cov_time_data = ((time - time_mean) * (dt - data_mean)).sum(dim="valid_time")

# Calculando a variância do tempo
var_time = ((time - time_mean) ** 2).sum(dim="valid_time")

# Coeficiente de regressão (inclinação ou tendência)
beta = cov_time_data / var_time

# Intercepto (ponto onde a reta cruza o eixo y)
alpha = data_mean - beta * time_mean

# Resultado: `beta` contém a tendência em cada ponto espacial
print(beta)

# Adicionando a tendência como uma nova variável ao dataset
dt["trend"] = beta

# Salvar como NetCDF, se necessário
dt["trend"].to_netcdf("trend_results.nc")
