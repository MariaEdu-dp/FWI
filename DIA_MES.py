import xarray as xr
import matplotlib.pyplot as plt

# Abrir o dataset e selecionar a variável e o intervalo de datas desejado
dt = xr.open_mfdataset("datasets/FWI/*.nc")["fwinx"].sel(valid_time=slice("2001-01-01", "2022-12-31"))

# Agrupar os dados por dia do ano (ignorando o ano) e calcular a média para cada dia
daily_mean = dt.groupby("valid_time.dayofyear").mean(dim="valid_time")

# Plotar um histograma das médias diárias
plt.figure(figsize=(12, 6))
plt.hist(daily_mean.values, bins=30, edgecolor="black", alpha=0.7)
plt.title("Distribuição das Médias Diárias de FWI")
plt.xlabel("Valor Médio Diário de FWI")
plt.ylabel("Frequência")
plt.show()
