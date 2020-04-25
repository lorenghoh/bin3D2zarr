"""
Run this script in the main folder
Now supports multiple processes
"""
import sys
import json
import subprocess as sp

import xarray as xr
import zarr as zr

from pathlib import Path

from lib.config import read_config
from lib.handler import update_dict, find_exclusion_list

config = read_config()
bin3D2nc = f"{config['root']}/{config['bin3D2nc']}"


def bin3D_to_nc(key, target=0, flag=1, print_stdout=False):
    try:
        result = sp.run([bin3D2nc, key], check=True, capture_output=True,)
    except sp.CalledProcessError as e:
        print(f"Error translating {key}\n", e.output)

        # Open and mark file incomplete
        update_dict(key, target=target, flag=flag)
        raise
    finally:
        if print_stdout:
            print(sys.stdout.buffer.write(result.stdout))

    # When all operations are complete
    update_dict(key, flag=2)


def nc_to_zarr(key):
    file_name = Path(key).with_suffix(".nc")

    exc_list = find_exclusion_list(file_name.name)

    with xr.open_dataset(file_name) as ds:
        try:
            ds = ds.squeeze("time").drop(exc_list)
        except Exception:
            raise ValueError

        try:
            # Define compressor
            # Turned off for now (only gives 3 GB -> 2.7 GB)
            # comp = {'compressor': zr.Blosc(cname='zstd')}
            # encoding = {var: comp for var in variables}

            zarr_name = file_name.with_suffix(".zarr")
            ds.to_zarr(f"{zarr_name}")
        except ValueError:
            print(file_name.name)
            print("! Duplicate found. Check leftover zarr folder. \n")

    # Mark nc -> zarr conversion complete
    update_dict(key, flag=3)


def validate_zarr(key):
    nc_path = Path(key).with_suffix(".nc")
    zr_path = Path(key).with_suffix(".zarr")

    exc_list = find_exclusion_list(nc_path.name)

    nc_file = nc_path.as_posix()
    zr_file = zr_path.as_posix()
    with xr.open_dataset(nc_file) as d_nc, xr.open_zarr(zr_file) as d_za:
        try:
            d_nc = d_nc.squeeze("time").drop(exc_list)

            if d_nc.equals(d_za):
                Path(key).with_suffix(".bin3D").unlink()
                Path(key).with_suffix(".nc").unlink()
            else:
                raise ValueError
        except Exception:
            raise Exception

    # Mark Zarr validation complete
    update_dict(key, flag=4)

