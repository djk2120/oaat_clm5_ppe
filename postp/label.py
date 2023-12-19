import xarray as xr
import pandas as pd

ds=xr.open_dataset('postp.nc')
key='/glade/campaign/cgd/tss/projects/PPE/PPEn11_OAAT/helpers/surviving.csv'
df=pd.read_csv(key)
ds['param']=df.param.values

ds.attrs={'contact':'djk2120@ucar.edu',
          'date':'18-Dec-2023',
          'key':key,
          'source':'/glade/campaign/cgd/tss/projects/PPE/PPEn11_OAAT',
          'script':'/glade/u/home/djk2120/oaat_clm5_ppe/postp/oaat_postp.py'}

ds.to_netcdf('oaat_postp.nc')
