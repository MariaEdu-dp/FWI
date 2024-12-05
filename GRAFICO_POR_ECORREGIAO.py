import geopandas as gpd
import matplotlib.pyplot as plt
import rioxarray
from shapely.geometry import mapping
import xarray as xr
import pandas as pd
import numpy as np

plt.rc("font", family="Arial")
plt.style.use('bmh')

# Carregar o shapefile com clusters e ecorregiões
eco = r"ecorregioes/ecorregiões_cluster/CLUSTER_RECORTADO.gpkg"
eco = gpd.read_file(eco, engine='pyogrio')
eco = eco.to_crs(4674)

# Agrupar as feições pela coluna LEVEL3
ecorregioes = eco.groupby('LEVEL3')

# Load datasets
dt = xr.open_dataset(r"datasets/media_anual.nc")
print(dt)
dt = dt.drop_vars("time_bnds")
dt1 = dt.sel(time=slice("2001-01-01", "2022-12-31"))
print(dt)

# Loop para cada ecorregião (LEVEL3)
for level3_id, ecorregiao_group in ecorregioes:
    # print(level3_id)
    print(f"Processando Ecorregião {level3_id}...")

    # Unir todas as geometrias associadas a essa ecorregião (se necessário)
    geom_ecorregiao = ecorregiao_group.union_all(method="unary")

    # Definir as dimensões espaciais e o CRS no NetCDF
    ds = dt1.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
    ds = ds.rio.write_crs(f"epsg:4674", inplace=True)

    try:
        # Recortar o NetCDF para a área da ecorregião
        clipped_ds = ds.rio.clip([mapping(geom_ecorregiao)], drop=True)
        clipped_ds.to_netcdf("TESTE_RECORTE_ECORREGIAO.nc")

        # Calcular a média ao longo de lat e lon
        clipped_mean = clipped_ds.mean(("lat", "lon"))
        print(clipped_mean)

        # Configurar a figura para esta ecorregião
        fig, ax = plt.subplots(figsize=(10, 6))

        # Iterar sobre os clusters associados a essa ecorregião
        for cluster_id, cluster_row in ecorregiao_group.groupby('CLUSTER_ID'):
            time_values = clipped_mean["time"].values
            fwi_values = clipped_mean.values

            # Plotar os dados para o cluster
            #time_values = pd.date_range(start="1940-01-03", end="2023-12-31", freq="D")
            ax.plot(time_values, clipped_mean["fwi"], marker='o', label=f'Cluster {cluster_id}')

        # Configurações do gráfico para a ecorregião
        ax.set_title(f"FWI para a Ecorregião {level3_id}")
        ax.set_xlabel("Tempo")
        ax.set_ylabel("FWI Médio")
        ax.legend()

        # Exibir o gráfico para esta ecorregião
        plt.tight_layout()
        plt.show()

    except rioxarray.exceptions.NoDataInBounds:
        print(f"Nenhum dado encontrado para a ecorregião {level3_id}.")
