import xarray as xr
import numpy as np
import glob


f='/glade/campaign/cgd/tss/projects/PPE/PPEn11_OAAT/helpers/sparsegrid_landarea.nc'
la=xr.open_dataset(f).landarea
lasum=la.sum().compute()

def gmean(da):
    return 1/lasum*(da*la).sum(dim='gridcell')

d='/glade/campaign/cgd/tss/projects/PPE/PPEn11_OAAT/C285/hist/'

f0=d+'PPEn11_C285_OAAT0000.clm2.h0.2005-02-01-00000.nc'
f1=d+'PPEn11_C285_OAAT0221.clm2.h0.2005-02-01-00000.nc'


ds0=xr.open_dataset(f0)
ds1=xr.open_dataset(f1)

for v in ds0.data_vars:
    if not ds0[v].equals(ds1[v]):
        print(v)
