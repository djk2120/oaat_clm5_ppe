import xarray as xr
import numpy as np
import pandas as pd
import sys

def fix_time(ds):
    yr0=str(ds['time.year'][0].values)
    nt=len(ds.time)
    ds['time'] = xr.cftime_range(yr0,periods=nt,freq='MS',calendar='noleap') #fix time bug
    return ds

def amean(da):
    #annual mean of monthly data
    m  = da['time.daysinmonth']
    cf = 1/365
    xa = cf*(m*da).groupby('time.year').sum().compute()
    return xa

def gmean(da,la):
    if 'gridcell' in da.dims:
        dim='gridcell'
    else:
        dim=['lat','lon']
    x=(da*la).sum(dim=dim)/la.sum()

    return x.compute()

def bmean(da,la,biome):
    x=1/la.groupby(biome).sum()*(da*la).groupby(biome).sum()
    return x.compute()

def pmean(da,lapft):
    x=1/lapft.groupby(da.pft).sum()*(da*lapft).groupby('pft').sum()
    return x.compute()

def cpds(ds1,ds2,suff):
    for v in ds1.data_vars:
        ds2[v+suff]=ds1[v]
    return ds2

def crunch(ds,op,domain,la=[],biome=[],lapft=[]):
    xx=[]
    if op=='mean':
        x=amean(ds).mean(dim='year')
    elif op=='std':
        x=amean(ds).std(dim='year')
    elif op=='amp':
        x=(ds.groupby('time.year').max()-ds.groupby('time.year').min()).mean(dim='year')
          
    if domain=='global':
        xx=gmean(x,la)
    elif domain=='biome':
        xx=bmean(x,la,biome)
    elif domain=='pft':
        xx=pmean(x,lapft)
        
    for v in ds.data_vars:
        xx[v].attrs=ds[v].attrs
    
    return xx
            
def postp(exp,key):
    dsout=xr.Dataset()
    f0='/glade/campaign/cgd/tss/projects/PPE/PPEn11_OAAT/{}/hist/PPEn11_{}_{}.clm2.{}.2005-02-01-00000.nc'
    f=f0.format(exp,exp,key,'h0')
    dvs=['GPP','TLAI']
    ds=fix_time(xr.open_dataset(f))[dvs]
    for op in ['mean','std','amp']:
        for domain in ['global','biome']:
            x=crunch(ds,op,domain,la,biome,lapft)
            dsout=cpds(x,dsout,'_'+domain+'_'+op)

    f=f0.format(exp,exp,key,'h1')
    dvs=['GPP','TLAI']
    ds=fix_time(xr.open_dataset(f))[dvs]
    pft=xr.open_dataset(f)['pfts1d_itype_veg']
    ds['pft']=pft
    domain='pft'
    for op in ['mean','std','amp']:
        x=crunch(ds,op,domain,la,biome,lapft)
        dsout=cpds(x,dsout,'_'+domain+'_'+op)
        
    return dsout


p=int(sys.argv[1])

la=xr.open_dataset('sparsegrid_landarea.nc').landarea
lapft=xr.open_dataset('sparsegrid_landarea.nc').landarea_pft
biome=xr.open_dataset('whitkey.nc').biome
key='/glade/campaign/cgd/tss/projects/PPE/PPEn11_OAAT/helpers/surviving.csv'
df=pd.read_csv(key)


exps=['CTL2010','AF1855','AF2095','NDEP','C285','C867']
minmax=['min','max']
keys=[df[m][p] for m in minmax]

ds=xr.concat([xr.concat([postp(exp,key) for key in keys],dim='minmax') for exp in exps],dim='exp')
ds['minmax']=minmax
ds['exp']=exps
ds['key']=xr.DataArray(keys,dims='minmax')

fout='/glade/scratch/djk2120/postp/oaat/oaat.param{}.nc'.format(str(p).zfill(3))
ds.to_netcdf(fout)
