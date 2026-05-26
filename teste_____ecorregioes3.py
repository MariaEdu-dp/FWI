import geopandas as gpd
import matplotlib.pyplot as plt
import rioxarray
from shapely.geometry import mapping
import xarray as xr
import os
from colorama import Fore
import pandas as pd
from matplotlib.colors import ListedColormap
import math

plt.rc("font", family="Arial")
plt.style.use("ggplot")

# Paleta de 20 cores variadas, misturando tons aleatórios de diferentes matizes
from matplotlib.colors import ListedColormap

pastel_colors = ListedColormap([
    "#f77189",  # Rosa avermelhado vibrante
    "#ff8e57",  # Laranja intenso
    "#fecf46",  # Amarelo ouro
    "#a4db48",  # Verde limão brilhante
    "#44c06b",  # Verde esmeralda
    "#2cbbcc",  # Azul turquesa vibrante
    "#2c80d0",  # Azul royal intenso
    "#8064c9",  # Roxo médio vibrante
    "#c76ad3",  # Lilás forte
    "#fc7faa",  # Rosa choque
    "#ff6b67",  # Vermelho alaranjado
    "#ff943e",  # Laranja queimado
    "#fadf4e",  # Amarelo vibrante
    "#a4e347",  # Verde primavera
    "#42cd63",  # Verde bandeira
    "#2ec2d6",  # Azul celeste forte
    "#2f93dc",  # Azul vibrante médio
    "#7c6ad1",  # Roxo azulado
    "#c662cf",  # Magenta forte
    "#f9789c"   # Rosa avermelhado claro
])


# Carregar e transformar o shapefile da América do Sul
sa = gpd.read_file(r"C:/QGIS/World_Continents/World_Continents.shp", engine='pyogrio')
sa = sa.to_crs(4674)

# Carregar e transformar o shapefile com clusters e ecorregiões
eco = gpd.read_file(r"D:/FACULDADE/FWI/CLUSTER_RECORTADO.gpkg", engine='pyogrio')
eco = eco.to_crs(4674)

# Realizar o recorte
eco = gpd.clip(eco, sa)

# Dissolver as ecorregiões por LEVEL3 para unir polígonos com o mesmo valor
eco_dissolved = eco.dissolve(by="LEVEL3")

# Agrupar as feições dissolvidas pela coluna CLUSTER_ID
clusters = eco_dissolved.groupby('CLUSTER_ID')

# Carregar o dataset NetCDF
dt = xr.open_mfdataset(r"D:/FACULDADE/FWI/*.nc")
print(dt)
# Filtrar o período desejado
dt1 = dt.sel(valid_time=slice("1940-01-01", "1979-12-31")).resample(valid_time="YE").mean()

# Ajustar longitudes se necessário (de 0-360 para -180 a 180)
dt1.coords["longitude"] = (dt1.coords["longitude"] + 180) % 360 - 180
dt1 = dt1.sortby(dt1.longitude)
ds = dt1.rio.set_spatial_dims(x_dim="longitude", y_dim="latitude", inplace=True)
ds = ds.rio.write_crs("epsg:4674", inplace=True)


# Função para plotar até 4 ecorregiões por figura, combinando ecorregiões quando necessário
# Loop para cada cluster
for cluster_id, cluster_group in clusters:
    print(f"Processando Cluster {cluster_id}...")
    ecorregioes = [e[1] for e in cluster_group.iterrows()]
    n_ecorregioes = len(ecorregioes)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=True, sharey=True)
    plt.subplots_adjust(left=0.052, bottom=0.046, right=0.975, top=0.9, wspace=0.032, hspace=0.14)
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

        # Adicionar a legenda individual acima de cada subplot
        ax.legend(handles=handles, labels=labels, loc="upper center", ncol=4, frameon=False) #bbox_to_anchor=(0.5, 1.15)am m

    # Ajustar layout e título para o cluster
    fig.suptitle(f"FWI anual para o cluster {cluster_id}", fontsize=16)
    plt.ylim(0, 60)
    fig.supylabel("FWI Médio")
    os.makedirs("FIGURAS/teste___ecorregioes3", exist_ok=True)
    plt.savefig(f"FIGURAS/teste___ecorregioes3/FWI_ANUAL_CLUSTER{cluster_id}.png", dpi=300)
