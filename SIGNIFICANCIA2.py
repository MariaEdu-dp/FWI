import xarray as xr
import numpy as np
from scipy.stats import t

# Abrir o dataset e selecionar a variável e o intervalo de datas desejado
dt = xr.open_mfdataset("datasets/FWI/*.nc", chunks={"latitude": 10, "longitude": 10})["fwinx"].sel(valid_time=slice("1940-01-01", "2023-12-31"))

# Corrigir a longitude para o intervalo [-180, 180]
dt.coords["longitude"] = (dt.coords["longitude"] + 180) % 360 - 180
dt = dt.sortby(dt.longitude)

# Supondo que dt é o seu DataArray com dimensões ("valid_time", "latitude", "longitude")
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

# Valores previstos pela regressão
y_pred = alpha + beta * time

# Resíduos da regressão
residuals = dt - y_pred

# Graus de liberdade (número de observações - 2)
n = dt.sizes["valid_time"]
dof = n - 2

# Soma dos quadrados dos resíduos
rss = (residuals ** 2).sum(dim="valid_time")

# Variância residual
residual_variance = rss / dof

# Erro padrão do coeficiente beta
std_error_beta = np.sqrt(residual_variance / var_time)

# Estatística t para o coeficiente beta
t_stat_beta = beta / std_error_beta

# p-value para cada ponto espacial (habilitando processamento com Dask)
p_value = xr.apply_ufunc(
    t.cdf,
    np.abs(t_stat_beta),
    input_core_dims=[[]],
    kwargs={"df": dof},
    dask="parallelized",
    output_dtypes=[float]
)

# Converter o p-value para a forma de duas caudas
p_value = 2 * (1 - p_value)

p_value.to_netcdf("p-value.nc")
