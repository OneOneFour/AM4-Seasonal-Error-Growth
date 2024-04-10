
import os 
import re
import sys 

import xarray as xr
import numpy as np
from glob import glob

FILE_LUT = {
    'jan':'DJF',
    'apr':"MAM",
    'jul':'JJA',
    'oct':'SON',
}
file = sys.argv[1]
name = FILE_LUT[file]
base_dir = os.path.expandvars(f"$SCRATCH/am4_error_growth_full/{file}")

full_memberlist = sorted(glob(os.path.join(base_dir,'**','atmos_4xdaily.nc')),key=lambda x: int(re.search(r'\w+\/(\d+)\/\w+.nc',x).group(1)))
full_members =  xr.open_mfdataset(full_memberlist,combine='nested',concat_dim='members',chunks={'time':10,'pfull':'auto','grid_yt':'auto'}).isel(time=slice(250))
rmse_member = []
for i in range(len(full_memberlist)):
    ref = full_members.isel(members=0)
    members = full_members.drop_isel(members=0)
    # Calculate RMSE
    square_residual = (members - ref) ** 2
    rmse_member.append(np.sqrt(square_residual.mean(dim='members')))
rmse = xr.concat(rmse_member,dim='members')
rmse.mean(dim='members').to_netcdf(os.path.expandvars(f"$SCRATCH/am4_error_growth_full/{name}_rmse.nc"))
