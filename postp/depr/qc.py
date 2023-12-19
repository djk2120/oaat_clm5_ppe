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

files=sorted(glob.glob(d+'*.h0.*'))
f=d+'PPEn11_C285_OAAT0222.clm2.h0.2005-02-01-00000.nc'
ds=xr.open_dataset(f)

cf=24*60*60

k='OAAT'+f.split('OAAT')[2].split('.')[0]
print(k,ds.GPP.equals(ds0.GPP),ds.GPP.equals(ds1.GPP))
print(k,np.round(cf*gmean(ds.GPP).mean(dim='time').values,3),
      np.round(cf*gmean(ds0.GPP).mean(dim='time').values,3),
               np.round(cf*gmean(ds1.GPP).mean(dim='time').values,3))
