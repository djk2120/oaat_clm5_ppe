import numpy as np
import xarray as xr
import glob
import sys

def amean(da,cf=1/365):
    #annual mean
    m  = da['time.daysinmonth']
    x = cf*(m*da).groupby('time.year').sum().compute()
    x.name=da.name
    x.attrs=da.attrs
    return x

def gmean(da,la):
    x=1/la.sum()*(la*da).sum(dim='gridcell')
    x.name=da.name
    x.attrs=da.attrs
    return x.compute()

def bmean(da,la,biome):
    x=1/la.groupby(biome).sum()*(da*la).groupby(biome).sum()
    x.name=da.name
    x.attrs=da.attrs
    return x.compute()

def pmean(da,lapft):
    x=1/lapft.groupby(da.pft).sum()*(da*lapft).groupby('pft').sum()
    x.name=da.name
    x.attrs=da.attrs
    return x.compute()

def crunch(ds,ds1,v,dsout):
    xann=amean(ds[v])
    xamp=ds[v].groupby('time.year').max()-ds[v].groupby('time.year').min()
    attrs={'long_name':ds[v].attrs['long_name'],
           'units':ds[v].attrs['units']}

    xglob={'mean':gmean(xann.mean(dim='year'),la),
           'std':gmean(xann.std(dim='year'),la),
           'amp':gmean(xamp.mean(dim='year'),la)}
    xgrid=xann.mean(dim='year')
    xbiom={'mean':bmean(xann.mean(dim='year'),la,biome),
           'std':bmean(xann.std(dim='year'),la,biome),
           'amp':bmean(xamp.mean(dim='year'),la,biome)}

    
    pftvs=['AR','FCEV','FCTR','FSR','GPP','NPP','NPP_NUPTAKE','TLAI','TOTVEGC']
    
    if v in pftvs:
        xann=amean(ds1[v])
        xamp=ds1[v].groupby('time.year').max()-ds1[v].groupby('time.year').min()
        xpft={'mean':pmean(xann.mean(dim='year'),lapft),
              'std':pmean(xann.std(dim='year'),lapft),
              'amp':pmean(xamp.mean(dim='year'),lapft)}
    else:
        xpft=[]


    for d,x in zip(['global','biome','pft'],[xglob,xbiom,xpft]):
        for op in x:
            dsout[v+'_'+d+'_'+op]=x[op]
            dsout[v+'_'+d+'_'+op].attrs=attrs

    dsout[v+'_gridded_mean']=xgrid
    dsout[v+'_gridded_mean'].attrs=attrs
    
    return dsout

def get_files(k,exps,tape):
    files = [glob.glob('/glade/campaign/asp/djk2120/PPEn11/'+exp+'/hist/*'+k+'*.clm2.'+tape+'.*.nc')[0] for exp in exps]
    return files

def fixxer(ds,exps):
    nx=len(ds.time)
    yr0=str(ds['time.year'][0].values)
    ds['time']=xr.cftime_range(yr0,periods=nx,freq='MS',calendar='noleap')
    ds['exp']=exps
    if 'pft' in ds.GPP.dims:
        ds['pft']=ds.pfts1d_itype_veg.isel(exp=0)
    return ds

la=xr.open_dataset('sparsegrid_landarea.nc').landarea
lapft=xr.open_dataset('sparsegrid_landarea.nc').landarea_pft
biome=xr.open_dataset('whitkey.nc').biome

f=sys.argv[1]
with open(f) as file:
    keys=file.read().splitlines()

for k in keys:
    print(k)
    dsout=xr.Dataset()
    exps=['CTL2010','C285','C867','NDEP','AF1855','AF2095']
    files=get_files(k,exps,'h0')
    ds=fixxer(xr.open_mfdataset(files,combine='nested',concat_dim='exp'),exps)
    files=get_files(k,exps,'h1')
    ds1=fixxer(xr.open_mfdataset(files,combine='nested',concat_dim='exp'),exps)

    dvs=['GPP','AR','HR','NPP','NBP','NEP','ER','NPP_NUPTAKE',
         'EFLX_LH_TOT','FCTR','FCEV','FGEV','BTRANMN','FGR','FSH',
         'SOILWATER_10CM','TWS','QRUNOFF','SNOWDP','H2OSNO','FSNO',
         'TLAI','FSR','ALTMAX','TV','TG',
         'FAREA_BURNED','COL_FIRE_CLOSS',
         'TOTVEGC','TOTECOSYSC','TOTSOMC_1m',
         'TOTVEGN','TOTECOSYSN']

    dsout=xr.Dataset()
    for v in dvs:
        dsout=crunch(ds,ds1,v,dsout)

    fout='/glade/scratch/djk2120/postp/oaat/'+k+'.postp.nc'
    dsout.to_netcdf(fout)
