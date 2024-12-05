import geopandas as gpd
import matplotlib.pyplot as plt
import rioxarray
from shapely.geometry import mapping
import xarray as xr
from colorama import Fore
import pandas as pd
from matplotlib.colors import ListedColormap
import math

plt.rc("font", family="Arial")
plt.style.use('seaborn-v0_8-whitegrid')

# Paleta de 20 cores variadas, misturando tons aleatórios de diferentes matizes
from matplotlib.colors import ListedColormap

pastel_colors = ListedColormap([
    "#A8D5E2",  # Azul suave claro
    "#B2A4D3",  # Azul arroxeado escuro
    "#F9C49A",  # Pêssego suave claro
    "#C1D9CE",  # Verde menta suave escuro
    "#B2D3A8",  # Verde suave claro
    "#D5B8E6",  # Roxo claro escuro
    "#F2B5C4",  # Rosa suave claro
    "#B9C0D1",  # Cinza azulado suave escuro
    "#EAD1DC",  # Lilás suave claro
    "#DAD0F5",  # Lavanda suave escuro
    "#D1E2A8",  # Verde amarelado suave claro
    "#F4CEC5",  # Coral claro escuro
    "#FFD1A9",  # Laranja pálido claro
    "#B0E0E6",  # Azul claro escuro
    "#C1D1B2",  # Verde oliva claro
    "#E6B0AA",  # Salmão suave escuro
    "#FFE4B5",  # Amarelo suave claro
    "#C7E3B5",  # Verde suave claro escuro
    "#F0C7A5",  # Pêssego escuro claro
    "#F3DAC9"   # Bege suave escuro
])


# Carregar e transformar o shapefile da América do Sul
sa = gpd.read_file(r"america_do_sul/Lim_america_do_sul_2021.shp", engine='pyogrio')
sa = sa.to_crs(4674)

# Carregar e transformar o shapefile com clusters e ecorregiões
eco = gpd.read_file(r"ecorregioes/ecorregiões_cluster/CLUSTER_RECORTADO.gpkg", engine='pyogrio')
eco = eco.to_crs(4674)

# Realizar o recorte
eco = gpd.clip(eco, sa)

# Dissolver as ecorregiões por LEVEL3 para unir polígonos com o mesmo valor
eco_dissolved = eco.dissolve(by="LEVEL3")

# Agrupar as feições dissolvidas pela coluna CLUSTER_ID
clusters = eco_dissolved.groupby('CLUSTER_ID')

# Carregar o dataset NetCDF
dt = xr.open_mfdataset(r"datasets/FWI/*.nc")
# Filtrar o período desejado
dt1 = dt.sel(valid_time=slice("1940-01-01", "2023-12-31")).resample(valid_time="ME").mean()

# Ajustar longitudes se necessário (de 0-360 para -180 a 180)
dt1.coords["longitude"] = (dt1.coords["longitude"] + 180) % 360 - 180
dt1 = dt1.sortby(dt1.longitude)
ds = dt1.rio.set_spatial_dims(x_dim="longitude", y_dim="latitude", inplace=True)
ds = ds.rio.write_crs("epsg:4674", inplace=True)


# Função para plotar até 4 ecorregiões por figura, combinando ecorregiões quando necessário
def plot_ecorregioes_combinadas(ecorregioes, cluster_id):
    n_ecorregioes = len(ecorregioes)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=True, sharey=True)
    axes = axes.flatten()

    # Definir a quantidade de ecorregiões por eixo para acomodar até 4 eixos
    ecorregioes_por_eixo = math.ceil(n_ecorregioes / 4)

    for idx, ax in enumerate(axes):
        ecorregioes_lote = ecorregioes[idx * ecorregioes_por_eixo: (idx + 1) * ecorregioes_por_eixo]

        handles, labels = [], []  # Lista para armazenar handles e labels de legenda para o eixo atual

        # Plotar cada ecorregião no eixo atual
        for e_idx, ecorregiao in enumerate(ecorregioes_lote):
            geom_ecorregiao = ecorregiao.geometry
            try:
                # Recortar o NetCDF para a área da ecorregião
                clipped_ds = ds.rio.clip([mapping(geom_ecorregiao)], drop=True)
                clipped_mean = clipped_ds.mean(("latitude", "longitude"))

                # Obter valores de tempo e fwi para a ecorregião
                time_values = clipped_mean["valid_time"].values
                fwi_values = clipped_mean["fwinx"].values  # Certifique-se que 'fwi' é o nome correto da variável

                # Plotar os dados para a ecorregião individualmente
                line, = ax.plot(
                    time_values,
                    fwi_values,
                    color=pastel_colors((idx * ecorregioes_por_eixo + e_idx) % 20),
                    linewidth=1,
                    label=f'Ecorregião {ecorregiao.name}'
                )
                handles.append(line)  # Armazena o handle para a legenda
                labels.append(f'Ecorregião {ecorregiao.name}')
            except rioxarray.exceptions.NoDataInBounds:
                print(f"Nenhum dado encontrado para a ecorregião {ecorregiao.name} no cluster {cluster_id}.")

        ax.set_title(f"Ecorregião {ecorregiao.name}")
        ax.set_xlabel("Tempo")
        ax.set_ylabel("FWI Médio")

        # Adicionar a legenda individual acima de cada subplot
        ax.legend(handles=handles, labels=labels, loc="upper center", ncol=4, frameon=False) #bbox_to_anchor=(0.5, 1.15)am m

    # Ajustar layout e título para o cluster
    fig.suptitle(f"FWI para o Cluster {cluster_id}", fontsize=16)
    plt.show()


# Loop para cada cluster
for cluster_id, cluster_group in clusters:
    print(f"Processando Cluster {cluster_id}...")
    ecorregioes = [e[1] for e in cluster_group.iterrows()]
    plot_ecorregioes_combinadas(ecorregioes, cluster_id)
