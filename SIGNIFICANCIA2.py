import os
import xarray as xr
import numpy as np
from scipy.stats import t
from shapely.geometry import mapping
import geopandas as gpd

# Diretório para salvar resultados
output_dir = "datasets/TENDENCIA/TIFF_OUTPUT"
os.makedirs(output_dir, exist_ok=True)
print(f"Diretório de saída criado: {output_dir}")

# Abrir dataset e selecionar variável e período
dt = xr.open_mfdataset(
    r"D:\USP\DADOS_FWI_portal-nasa\para_compartilhar_com_maria_eduarda\pythonProject1\datasets\FWI\*nc"
)["fwinx"].sel(valid_time=slice("1940-01-01", "2024-12-31"))

# Ajustar longitude para [-180, 180]
dt.coords["longitude"] = (dt.coords["longitude"] + 180) % 360 - 180
dt = dt.sortby(dt.longitude)
print("Dados carregados e longitude ajustada.")

# Ler o shapefile e configurar o CRS
shapefile = gpd.read_file(r"D:\USP\DADOS_FWI_portal-nasa\para_compartilhar_com_maria_eduarda\pythonProject1\CLUSTER_ID\CLUSTER_ID.shp").to_crs(4674)
geom_sa = shapefile.geometry

# Definir as dimensões espaciais e o CRS no NetCDF
ds = dt.rio.set_spatial_dims(x_dim="longitude", y_dim="latitude", inplace=True)
ds = ds.rio.write_crs(f"epsg:4674", inplace=True)

# Recortar o NetCDF para a área da ecorregião
dt = ds.rio.clip(shapefile.geometry.apply(mapping), drop=True)

# Variável de tempo em float (dias desde epoch)
time = dt["valid_time"].astype(float)

time_mean = time.mean(dim="valid_time")
data_mean = dt.mean(dim="valid_time")

cov_time_data = ((time - time_mean) * (dt - data_mean)).sum(dim="valid_time")
var_time = ((time - time_mean) ** 2).sum(dim="valid_time")

beta = cov_time_data / var_time

beta_total = beta * 1e9 * 60 * 60 * 24 * len(dt.valid_time)

alpha = data_mean - beta * time_mean
y_pred = alpha + beta * time
residuals = dt - y_pred

n = dt.sizes["valid_time"]
dof = n - 2
rss = (residuals ** 2).sum(dim="valid_time")
residual_variance = rss / dof

std_error_beta = np.sqrt(residual_variance / var_time)
t_stat_beta = beta / std_error_beta

p_value = xr.apply_ufunc(
    t.cdf,
    np.abs(t_stat_beta),
    input_core_dims=[[]],
    kwargs={"df": dof},
    dask="parallelized",
    output_dtypes=[float],
)
p_value = 2 * (1 - p_value)

significant = p_value < 0.05

# Salvar como GeoTIFF (2D dados) usando rioxarray

beta_total.rio.set_spatial_dims(x_dim="longitude", y_dim="latitude", inplace=True)
beta_total.rio.write_crs("EPSG:4674", inplace=True)  # ajuste EPSG conforme seu dado

significant = significant.astype(np.uint8)  # booleano como 0/1 para TIFF
significant.rio.set_spatial_dims(x_dim="longitude", y_dim="latitude", inplace=True)
significant.rio.write_crs("EPSG:4674", inplace=True)

beta_total.rio.to_raster(os.path.join(output_dir, "tendencia.tif"))
print(f"Tendência total salva como TIFF em {os.path.join(output_dir, 'tendencia.tif')}")

significant.rio.to_raster(os.path.join(output_dir, "p-value.tif"))
print(f"Significância salva como TIFF em {os.path.join(output_dir, 'p-value.tif')}")

print("✅ Salvamento em TIFF concluído.")

