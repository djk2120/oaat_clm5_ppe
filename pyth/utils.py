import xarray as xr
import pandas as pd
import numpy as np
import glob


def get_exp(exp,tape='h0',dvs=[],yy=[]):
    
    oaats=['AF1855','AF2095','C285','C867','NDEP','CTL2010']
    if exp in oaats:
        key='/glade/campaign/asp/djk2120/PPEn11/csvs/surviving.csv'
        top='/glade/campaign/cgd/tss/projects/PPE/PPEn11_OAAT/'
        code='OAAT'
        yy=()
        minmax=True
        files,appends,dims=oaatfiles(exp,tape,code=code,yy=yy,top=top,key=key,minmax=minmax)
    else:
        files,appends,dims=lhcfiles(yy[0],yy[1],tape=tape)
        
    ds=get_ds(files,dims,dvs=dvs,appends=appends)
    
    return ds

def amean(da):
    #annual mean of monthly data
    m  = da['time.daysinmonth']
    cf = 1/365
    xa = cf*(m*da).groupby('time.year').sum().compute()
    xa.name=da.name
    xa.attrs=da.attrs
    return xa

def gmean(da,la):
    if 'gridcell' in da.dims:
        dim='gridcell'
    else:
        dim=['lat','lon']
    x=(da*la).sum(dim=dim)/la.sum()
    return x.compute()

def get_map(da,sgmap=None,file='sgmap.nc'):
    if not sgmap:
        sgmap=xr.open_dataset(file)
    return da.sel(gridcell=sgmap.cclass).where(sgmap.notnan).compute()

def rank_plot(da,nx,ax=None,sortby='delta'):
    x = top_n(da,nx,sortby=sortby)
    xdef = da.sel(param='default',minmax='min')
    
    if x.dims[0]=='minmax':
        x=x.T
    
    if not ax:
        fig=plt.figure()
        ax=fig.add_subplot()
    
    ax.plot([xdef,xdef],[0,nx-1],'k:',label='default')
    ax.scatter(x.sel(minmax='min'),range(nx),marker='o',facecolors='none', edgecolors='r',label='low-val')
    ax.plot(x.sel(minmax='max'),range(nx),'ro',label='high-val')

    i=-1
    for xmin,xmax in x:
        i+=1
        ax.plot([xmin,xmax],[i,i],'r')
    ax.set_yticks(range(nx))
    ax.set_yticklabels([p[:15] for p in x.param.values]) #[:15] shortens param names to 15 characters max
    
def top_n(da,nx,sortby='delta'):
    ''' return top_n sorted by param effect or min-val or maxval '''
    flip={'max':1,'min':-1}
    if sortby=='delta':
        dx=abs(da.sel(minmax='max')-da.sel(minmax='min'))
    elif sortby=='max':
        dx=da.max(dim='minmax')
    else:
        dx=-da.min(dim='minmax')
    ix=dx.argsort()[-nx:].values
    x=da.isel(param=ix)
    return x

def get_ds(files,dims,dvs=[],appends={}):
    if dvs:
        def preprocess(ds):
            return ds[dvs]
    else:
        def preprocess(ds):
            return ds

    ds = xr.open_mfdataset(files,combine='nested',concat_dim=dims,
                           parallel=True,
                           preprocess=preprocess)
    f=np.array(files).ravel()[0]
    htape=f.split('clm2')[1][1:3]

    #add extra variables
    tmp = xr.open_dataset(f)
    
    #fix up time dimension, swap pft
    if (htape=='h0')|(htape=='h1'):
        ds=fix_time(ds)
    if (htape=='h1'):
        ds['pft']=tmp.pfts1d_itype_veg
        
    
    for append in appends:
        ds[append]=appends[append]
        
             
    return ds

def lhcfiles(yr0,yr1,tape='h0',dropdef=False):
    fs=[]
    for x in ['transient','ssp370v2']:
        d='/glade/campaign/asp/djk2120/PPEn11/'+x+'/hist/'
        fs=[*fs,*sorted(glob.glob(d+'*LHC*'+tape+'*'))]
    
    #discern year
    fs =np.array(fs)
    yrs=np.array([int(f.split(tape)[1][1:5]) for f in fs])

    #bump back yr0, if needed
    uyrs=np.unique(yrs)
    yr0=uyrs[(uyrs/yr0)<=1][-1]

    #find index to subset files by year
    ix    = (yrs>=yr0)&(yrs<=yr1)
    fs    = fs[ix] 

    #reorganize files
    mems=np.array(['LHC'+f.split('LHC')[1][:4] for f in fs])
    files=[list(fs[mems==mem]) for mem in np.unique(mems)]
    
    #collect parameter info
    key='/glade/campaign/asp/djk2120/PPEn11/csvs/lhc220926.txt'
    df=pd.read_csv(key)
    params=[p for p in df]
    params.remove('member')
    if dropdef:
        defp=[]
        files=files[1:]
    else:
        defp=[np.nan]
    appends={p:xr.DataArray([*defp,*df[p].values],dims='ens') for p in params}
    appends['param']=xr.DataArray(params,dims='param')
    
    #collect some forcing info
    singles=['FSDS','RAIN','SNOW']
    tmp=get_ds(files[0],dims=['time'])
    for v in singles:
        appends[v]=tmp[v]
    appends['PREC']=appends['RAIN']+appends['SNOW']
    
    #add in gridcell info
    tmp=xr.open_dataset(files[0][0])
    singles=['grid1d_lat','grid1d_lon']
    for v in singles:
        appends[v]=tmp[v]
    
    dims=['ens','time']
    
    return files,appends,dims

def oaatfiles(exp,tape,code='OAAT',yy=(),top='/glade/campaign/cgd/tss/projects/PPE/PPEn11_OAAT/',key='/glade/campaign/asp/djk2120/PPEn11/csvs/surviving.csv',minmax=True):

    df=pd.read_csv(key)
    allfiles=all_files(exp,tape=tape,code=code,yy=yy,top=top)
    appends={}

    if minmax==True:
        dims=['param','minmax','time']
        mm=['min','max']
        files=[]
        for p in df.param:
            f=[]
            for m in mm:
                k=df[m][df.param==p].values[0]
                fk=allfiles[k]
                if len(fk)==1:
                    dims=['param','minmax']
                    fk=fk[0]
                f.append(fk)
            files.append(f)
            
        tmp=xr.open_dataset(np.array(files).ravel()[0])
        appends['param']=df.param.values
        appends['minmax']=mm

    
    singles=['grid1d_lat','grid1d_lon','FSDS','RAIN','SNOW','TSA','RH2M','WIND']
    if tape=='h1':
        singles.append('pfts1d_lat')
        singles.append('pfts1d_lon')
        
    for v in singles:
        if 'time' in tmp[v].dims:
            da=fix_time(tmp[v])
        else:
            da=tmp[v]
        appends[v]=tmp[v]
    appends['PREC']=appends['RAIN']+appends['SNOW']
    vpd,vp=calc_vpd(appends['TSA'],appends['RH2M'])
    appends['VPD']=vpd
    appends['VP']=vp
    
        
    return files,appends,dims


def all_files(exp,tape='h0',code='OAAT',yy=(),top='/glade/campaign/cgd/tss/projects/PPE/PPEn11_OAAT/'):
    d=top+exp+'/hist/'
    
    files=np.array(sorted(glob.glob(d+'*'+code+'*'+tape+'*')))
    yrs=np.array([f.split(tape)[1][1:5] for f in files]).astype(int)

    #subset files by year, if desired
    if yy:
        yr0,yr1=yy

        uyrs=np.unique(yrs)
        yr0=max(yr0,uyrs.min())
        if len(uyrs)>1:
            yr0=uyrs[(uyrs/yr0)<=1][-1]  #bump back yr0, if needed
            ix=(yrs>=yr0)&(yrs<=yr1)
            files=files[ix]
            yrs=yrs[ix]

    #index by key
    keys=np.array([f.split('.clm2.')[0].split('_')[-1] for f in files])
    ny0=(keys==keys[0]).sum()
    out={}
    for key in keys:
        ix=keys==key
        out[key]=list(files[ix])
        if ix.sum()!=ny0:
            raise Exception("Unequal number of files per key: "+key)

    return out

def fix_time(ds):
    yr0=str(ds['time.year'][0].values)
    nt=len(ds.time)
    ds['time'] = xr.cftime_range(yr0,periods=nt,freq='MS',calendar='noleap') #fix time bug
    return ds

def calc_vpd(tsa,rh2m):
    t=tsa-273.15
    rh=rh2m/100
    es=0.61094*np.exp(17.625*t/(t+234.04))
    vpd=((1-rh)*es).compute()
    vpd.attrs={'long_name':'vapor pressure deficit','units':'kPa'}
    vp=(rh*es).compute()
    vp.attrs={'long_name':'vapor pressure','units':'kPa'}
    
    return vpd,vp

def brown_green():
    '''
    returns a colormap based on colorbrewer diverging brown->green
    '''

    # colorbrewer colormap, diverging, brown->green
    cmap = np.zeros([11,3]);
    cmap[0,:] = 84,48,5
    cmap[1,:] = 140,81,10
    cmap[2,:] = 191,129,45
    cmap[3,:] = 223,194,125
    cmap[4,:] = 246,232,195
    cmap[5,:] = 245,245,245
    cmap[6,:] = 199,234,229
    cmap[7,:] = 128,205,193
    cmap[8,:] = 53,151,143
    cmap[9,:] = 1,102,94
    cmap[10,:] = 0,60,48
    cmap = matplotlib.colors.ListedColormap(cmap/256)
    
    return cmap