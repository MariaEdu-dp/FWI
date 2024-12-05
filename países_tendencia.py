import geopandas as gpd
import matplotlib.pyplot as plt
import rioxarray
from shapely.geometry import mapping
import xarray as xr
import numpy as np

plt.rc("font", family="Arial")
plt.style.use('bmh')


# Open South America shapefile
SA = r"america_do_sul/Lim_america_do_sul_2021.shp"
SA = gpd.read_file(SA, engine='pyogrio')
SA = SA.to_crs(4326)
print(SA)

# Load datasets
dt = xr.open_dataset(r"datasets/media_anual.nc")
dt = dt.drop_vars("time_bnds")
dt1 = dt.sel(lat=slice(-60, 15), lon=slice(-90, -25), time=slice("2002-01-01", "2022-12-31"))
print(dt)

# Lista para armazenar os datasets recortados e os nomes
recortes = []
nomes = []

# Loop para recorte
for idx, row in SA.iterrows():
    geom = row.geometry

    # Definir as dimensões espaciais e o CRS no NetCDF
    ds = dt1.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
    ds = ds.rio.write_crs(f"epsg:4326", inplace=True)

    print(f"Recortando para a geometria {idx}...")

    try:
        # Recortar usando a geometria atual
        clipped_ds = ds.rio.clip([mapping(geom)], drop=True)

        # Nomear e salvar o nome da geometria
        name = row["nome"]
        recortes.append(clipped_ds.mean(("lat", "lon")))  # Armazena o recorte médio
        nomes.append(name)  # Armazena o nome da geometria

    except rioxarray.exceptions.NoDataInBounds:
        print(f"Nenhum dado encontrado na área correspondente a {row['nome']}.")

# Configuração da grade de subplots (7 linhas, 2 colunas) e compartilhamento do eixo y
fig, axes = plt.subplots(nrows=7, ncols=2, figsize=(14, 20), sharey=True)
axes = axes.flatten()  # Flatten a grid para iterar facilmente sobre os eixos

# Loop para plotar os dados de cada recorte
for idx, clipped in enumerate(recortes):
    ax = axes[idx]  # Seleciona o eixo correspondente

    # Certifique-se de que você está acessando os valores corretamente
    time_values = clipped["time"].values  # Converta para int64
    time = len(time_values)
    fwi_values = clipped["fwi"]

    # Calcular a tendência (polinômio de grau 1 - linha reta)
    z_fwi = np.polyfit(time, fwi_values, 1)
    p_fwi = np.poly1d(z_fwi)

    # Plotar o FWI e a linha de tendência
    ax.plot(clipped["time"], clipped["fwi"], color="firebrick", label=f'{nomes[idx]}', linestyle='-')
    ax.plot(time_values, p_fwi(time_values.astype(np.int64)), linestyle='--', lw=0.8)

    # Definir título e legendas para cada eixo
    ax.set_title(f"Tendência FWI - {nomes[idx]}")
    ax.set_xlabel("Tempo")
    if idx % 2 == 0:
        ax.set_ylabel("FWI Médio")
    ax.legend()
    ax.margins(x=0)

# Remover subplots vazios (se houver menos de 14 países)
for i in range(len(recortes), len(axes)):
    fig.delaxes(axes[i])

# Ajustar o layout para evitar sobreposição dos gráficos
plt.tight_layout()
plt.show()
