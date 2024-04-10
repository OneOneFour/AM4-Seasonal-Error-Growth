import argparse
import os
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir")
    parser.add_argument(
        "--reference", type=int, default=0, help='Run ID to use as "truth"'
    )
    parser.add_argument(
        '--crop-time',type=int,help="crop time to the first N number of points",default=None
    )
    parser.add_argument(
        "--nc-name",
        type=str,
        default="atmos_4xdaily.nc",
        help="Name of file to open as diffs",
    )
    parser.add_argument('--plot',action_store=True,help='Plot intermediate output steps')
    parser.add_argument('--plot-var',type=str,default='ucomp',help='Variable to plot intermediate. Only used if --plot is set.')
    parser.add_argument("--chunks", type=int, default=20)

    args = parser.parse_args()

    ref = xr.open_dataset(
        os.path.join(args.run_dir, args.reference, args.nc_name),
        chunks={"grid_xt": args.chunks, "grid_yt": args.chunks},
    ).isel(time=slice(args.crop_time))
    memberlist = list(
        filter(
            lambda x: x != os.path.join(args.run_dir, args.reference, args.nc_name),
            glob(os.path.join(args.run_dir, "**", args.nc_name)),
        )
    )
    ref = ref.expand_dims({"members": len(memberlist)})
    members = xr.open_mfdataset(
        memberlist,
        chunks={"grid_xt": args.chunks, "grid_yt": args.chunks},
        combine="nested",
        concat_dim="members",
    ).isel(time=slice(args.crop_time))
    square_residual = (members - ref) ** 2
    rmse = square_residual.mean(dim='members')
    if args.plot:
        global_residual = square_residual.mean(dim=("grid_xt", "grid_yt"))
        eq =square_residual[args.plot_var].sel(grid_yt=slice(-10,10)).sel(pfull=850,method='nearest').mean(dim=("grid_xt", "grid_yt"))
        nh_ml =  square_residual[args.plot_var].sel(grid_yt=slice(30,60)).sel(pfull=850,method='nearest').mean(dim=("grid_xt", "grid_yt"))
        nh_polar = square_residual[args.plot_var].sel(grid_yt=slice(60,None)).sel(pfull=850,method='nearest').mean(dim=("grid_xt", "grid_yt"))
        
        fig,(axeq,axml,axpolar) = plt.subplots(nrows=3,ncols=1)
        eq.plot.line(ax=axeq)
        nh_ml.plot.line(ax=axml)
        nh_polar.plot.line(ax=axpolar)
        fig.savefig('member_mean_spread.png')
        plt.close(fig)
    if args.plot:
        fig,ax = plt.subplots()
        rmse[args.plot_var].max(dim='time').plot.pcolormesh(ax=ax)
        fig.savefig('saturation_rmse.png')
        plt.close(fig)
    