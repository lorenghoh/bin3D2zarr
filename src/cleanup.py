import os, glob, json
import subprocess as sp

import xarray as xr
import zarr as zr

from os import path
from pathlib import Path
from tqdm import tqdm

import lib_io, lib_config

c_ = lib_config.read_config()

"""
kwargs:
    f_name: Path object
"""
def cleanup_nc(f_name):
    nc_name = f_name.with_suffix('.nc').as_posix()
    za_name = f_name.with_suffix('.zarr').as_posix()

    # exc_list = ['QI', 'NI', 'QS', 'NS', 'QG', 'NG']
    exc_list = []

    with xr.open_dataset(nc_name) as dnc, xr.open_zarr(za_name) as dza:
        try:
            dnc = dnc.squeeze('time').drop(exc_list)

            if dnc.equals(dza):
                f_name.with_suffix('.nc').unlink()
            else:
                raise
        except FileNotFoundError:
            pass
        except:
            raise

if __name__ == '__main__':
    src = Path(f"{c_['root']}/{c_['src']}")
    
    for item in sorted(src.glob('*.nc')):
        cleanup_nc(item)
        
        