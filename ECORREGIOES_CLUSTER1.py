import geopandas as gpd
import matplotlib.pyplot as plt
import rioxarray
from shapely.geometry import mapping
import xarray as xr
import numpy as np

plt.rc("font", family="Arial")
plt.style.use('bmh')

# Carregar o shapefile com clusters e ecorregiões
eco = gpd.read_file("ecorregioes/ecorregiões_cluster/CLUSTER_RECORTADO.gpkg", engine='pyogrio')

# Agrupar as feições pela coluna CLUSTER_ID
clusters = eco.groupby('CLUSTER_ID')

cluster = eco.dissolve("CLUSTER_ID")

# Carregar o dataset NetCDF
dt = xr.open_dataset(r"datasets/media_anual.nc")
dt = dt.drop_vars("time_bnds")
dt1 = dt.sel(lat=slice(-60, 15), lon=slice(-90, -25), time=slice("2002-01-01", "2022-12-31"))

# Loop para cada cluster (CLUSTER_ID)
for cluster_id, cluster_group in clusters:
    print(f"Processando Cluster {cluster_id}...")

    # Configurar a figura para este cluster
    fig, ax = plt.subplots(figsize=(10, 6))

    # Iterar sobre as ecorregiões (LEVEL3) dentro do cluster
    for level3_id, ecorregiao in cluster_group.groupby('LEVEL3'):
        geom_ecorregiao = ecorregiao.unary_union  # Combina as geometrias da ecorregião

        # Definir as dimensões espaciais e o CRS no NetCDF
        ds = dt1.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
        ds = ds.rio.write_crs(f"epsg:4326", inplace=True)

        try:
            # Recortar o NetCDF para a área da ecorregião
            clipped_ds = ds.rio.clip([mapping(geom_ecorregiao)], drop=True)

            # Calcular a média ao longo de lat e lon
            clipped_mean = clipped_ds.mean(dim=("lat", "lon"))

            # Plotar os dados para a ecorregião
            ax.plot(clipped_mean["time"], clipped_mean["fwi"], marker=".", label=f'Ecorregião {level3_id}')

        except rioxarray.exceptions.NoDataInBounds:
            print(f"Nenhum dado encontrado para a ecorregião {level3_id} no Cluster {cluster_id}.")

    # Configurações do gráfico para o cluster
    ax.set_title(f"FWI para o Cluster {cluster_id}")
    ax.set_xlabel("Tempo")
    ax.set_ylabel("FWI Médio")
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)
    ax.margins(x=0)

    # Exibir o gráfico para este cluster
    plt.tight_layout()
    plt.show()
