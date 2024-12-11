import geopandas as gpd
import rioxarray
from shapely.geometry import mapping
import xarray as xr
import matplotlib.pyplot as plt
import math
import statsmodels.api as sm

# Carregar o shapefile da América do Sul
sa = gpd.read_file(r"america_do_sul/Lim_america_do_sul_2021.shp", engine='pyogrio')
sa = sa.to_crs(4674)

# Carregar o shapefile com clusters
eco = gpd.read_file(r"ecorregioes/ecorregiões_cluster/CLUSTER_RECORTADO.gpkg", engine='pyogrio')
eco = eco.to_crs(4674)

# Realizar o recorte do shapefile dos clusters pela América do Sul
eco = gpd.clip(eco, sa)

# Dissolver as feições por CLUSTER_ID para unir os polígonos
clusters = eco.dissolve(by="CLUSTER_ID")

# Carregar o dataset NetCDF
dt = xr.open_mfdataset(r"datasets/FWI/*.nc")

# Ajustar período e coordenadas
dt = dt.sel(valid_time=slice("1940-01-01", "2023-12-31")).resample(valid_time="ME").mean()
dt.coords["longitude"] = (dt.coords["longitude"] + 180) % 360 - 180
dt = dt.sortby(dt.longitude)
dt = dt.rio.set_spatial_dims(x_dim="longitude", y_dim="latitude", inplace=True)
dt = dt.rio.write_crs("epsg:4674", inplace=True)


# Função para decompor e plotar a série temporal com componentes
def decompor_e_plotar(series, ax, cluster_id):
    # Decomposição sazonal da série temporal
    decomposition = sm.tsa.seasonal_decompose(series, model='additive', period=12)  # Considerando sazonalidade mensal

    # Criar DataArrays com o índice de tempo original
    time_index = series.valid_time

    trend = xr.DataArray(decomposition.trend, coords=[time_index], dims=["valid_time"])
    seasonal = xr.DataArray(decomposition.seasonal, coords=[time_index], dims=["valid_time"])
    resid = xr.DataArray(decomposition.resid, coords=[time_index], dims=["valid_time"])

    # Plotar a série original e os componentes
    ax.plot(series.valid_time, series.values, label="Série Original", color='blue', linewidth=2, linestyle='-')
    ax.plot(trend.valid_time, trend.values, label="Tendência", color='red', linestyle='--')
    ax.plot(seasonal.valid_time, seasonal.values, label="Sazonalidade", color='green', linestyle=':')
    ax.plot(resid.valid_time, resid.values, label="Resíduos", color='orange', linestyle='-.')

    # Adicionar título e legendas
    ax.set_title(f"Decomposição para o Cluster {cluster_id}")
    ax.set_xlabel("Tempo")
    ax.set_ylabel("FWI")
    ax.legend()


# Criar a figura com subplots
fig, axes = plt.subplots(len(clusters), 1, figsize=(10, 6 * len(clusters)))

# Se houver apenas um cluster, a estrutura de axes não será uma lista, então precisamos garantir isso
if len(clusters) == 1:
    axes = [axes]

# Loop para processar cada cluster
for idx, (cluster_id, cluster) in enumerate(clusters.iterrows()):
    print(f"Processando Cluster {cluster_id}...")

    try:
        # Obter a geometria do cluster
        geom_cluster = cluster.geometry

        # Recortar o NetCDF para a área do cluster
        clipped_ds = dt.rio.clip([mapping(geom_cluster)], drop=True)

        # Calcular a média espacial (latitude e longitude) para o cluster
        mean_spatial = clipped_ds.mean(dim=("latitude", "longitude"))

        # Extrair a série temporal de FWI para o cluster
        fwi_series = mean_spatial["fwinx"]

        # Decompor e plotar a série temporal no eixo correspondente
        decompor_e_plotar(fwi_series, axes[idx], cluster_id)

    except rioxarray.exceptions.NoDataInBounds:
        print(f"Nenhum dado encontrado para o cluster {cluster_id}.")

# Ajustar layout e exibir a figura
plt.tight_layout()
plt.show()
