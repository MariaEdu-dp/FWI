import xarray as xr

"""
Você pode trocar esse dataset pelo maior, de 10GB, que tem todos os dados do FWI, se necessário.
Para isso, copie e cole o arquivo para a pasta "datasets", clique nele com o botão direito e clique em "Copy Path/Reference".
Clique em "Path from Content Root, apague o link do xr.open_dataset() e, entre aspas, coloque o link novo.
"""

data = "datasets/FWI_mensal.nc"

dataset_xr = xr.open_dataset(data)
print(dataset_xr)

# Selecione a área de estudo e a variável de interesse
area = dataset_xr["fwi"].sel(lat=slice(-60, 15), lon=slice(-90, -24))

from cdo import Cdo

# Inicialize a interface CDO
cdo = Cdo()

# Caminho para o arquivo de saída
output_file = 'tendencia_fwi.nc'

# Execute o operador regres para calcular a tendência
cdo.regres(input=area, output=output_file)

print(f"Tendência calculada e salva em {output_file}")
output_file = xr.open_dataset(output_file)

print(output_file)
