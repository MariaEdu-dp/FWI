import xarray as xr
import os

# Load your dataset
dt = xr.open_mfdataset(r"D:/FACULDADE/FWI/*.nc").fillna(0)

# Adjust longitude from 0-360 to -180 - 180
dt.coords["longitude"] = (dt.coords["longitude"] + 180) % 360 - 180
dt = dt.sortby(dt.longitude)

# Resample to monthly mean if not already done
dt_monthly = dt.resample(valid_time="ME").mean()

# Define your time periods (adjust as needed)
time_periods = [
    ("1940-01-01", "1949-12-31"),
    ("1950-01-01", "1959-12-31"),
    ("1960-01-01", "1969-12-31"),
    ("1970-01-01", "1979-12-31")
    # Add more periods as needed
]

# List of statistical operations and their output names
stats = [('mean', 'hmean_month'), ('std', 'hstd_month')]

for start_date, end_date in time_periods:
    # Select the time period
    period_data = dt_monthly.sel(valid_time=slice(start_date, end_date))

    for stat, var_name in stats:
        # Group by month and compute statistic (mean or std)
        monthly_stat = period_data.groupby('valid_time.month').__getattribute__(stat)()

        # Find month with highest value for each pixel
        hmonth = monthly_stat['fwinx'].argmax(dim='month') + 1  # +1 for 1-based months

        # Convert to dataset and add metadata
        result_ds = hmonth.to_dataset(name=var_name)
        result_ds.attrs['description'] = f"Month with highest {stat} FWI {start_date[:4]}-{end_date[:4]}"
        result_ds.attrs['month_values'] = "1=Jan, 2=Feb, ..., 12=Dec"

        # Save to NetCDF (create directories if needed)
        output_dir = f"MES_DO_ANO/{'MEDIA' if stat == 'mean' else 'DESVIO_PADRAO'}"
        os.makedirs(output_dir, exist_ok=True)
        result_ds.to_netcdf(f"{output_dir}/MESES_{start_date[:4]}_{end_date[:4]}.nc")
        print(f"Saved {stat} results for {start_date[:4]}-{end_date[:4]} to {output_dir}")
