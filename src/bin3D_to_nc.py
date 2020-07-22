"""
Run this script in the main folder
Now supports multiple processes
"""
import os
import shutil

import subprocess as sp

import xarray as xr
import zarr as zr

from pathlib import Path

from lib.config import read_config
from lib.handler import update_dict, find_exclusion_list

CONFIG = read_config()
BIN3D2NC = Path(f"{CONFIG['root']}/{CONFIG['bin3D2nc']}")
TMPDIR = Path(os.environ["TMPDIR"])


def bin3D_to_nc(key, target=4, flag=1, print_stdout=False):
    # Ensure target files are in $TMPDIR
    bin3D2nc = TMPDIR / BIN3D2NC.name
    tmp_key = TMPDIR / Path(key).name
    shutil.copy(BIN3D2NC, bin3D2nc)
    shutil.copy(key, tmp_key)

    try:
        result = sp.run([bin3D2nc, tmp_key], check=True, capture_output=True,)
    except sp.CalledProcessError as e:
        print(f"Error translating {key}\n", e.output)

        # Open and mark file incomplete
        update_dict(key, target=target, flag=flag)
        raise

    bin3D2nc.unlink()

    if print_stdout:
        print(result.stdout)

    # When all operations are complete
    update_dict(key, flag=2)


def nc_to_zarr(key):
    tmp_key = TMPDIR / Path(key).with_suffix(".nc").name
    exc_list = find_exclusion_list(tmp_key.name)

    with xr.open_dataset(tmp_key) as ds_nc:
        try:
            ds_nc = ds_nc.squeeze("time").drop(exc_list)
        except Exception:
            raise ValueError

        try:
            # Define compressor
            # Turned off for now (only gives 3 GB -> 2.7 GB)
            # comp = {'compressor': zr.Blosc(cname='zstd')}
            # encoding = {var: comp for var in variables}

            # Use $TMPDIR for Zarr output
            zr_path = tmp_key.with_suffix(".zarr.zip")
            with zr.ZipStore(f"{zr_path}") as store:
                ds_nc.to_zarr(store, mode="w")

            # Mark Zarr conversion complete
            update_dict(key, flag=3)

            # Validate Zarr output against netCDF
            validate_zarr(key)
        except ValueError:
            print(Path(key.name))
            print("! Duplicate found. Check leftover zarr folder. \n")


def validate_zarr(key):
    nc_path = TMPDIR / Path(key).with_suffix(".nc").name
    zr_path = TMPDIR / Path(key).with_suffix(".zarr.zip").name

    exc_list = find_exclusion_list(nc_path.name)

    # Since I do not care for Windows
    nc_str = nc_path.as_posix()
    zr_str = zr_path.as_posix()
    with xr.open_dataset(nc_str) as d_nc, xr.open_zarr(zr.ZipStore(zr_str)) as d_za:
        try:
            d_nc = d_nc.squeeze("time").drop(exc_list)

            flag = d_nc.equals(d_za)

            if flag is False:
                raise ValueError
        except ValueError:
            print("Translated Zarr dataset does not match .nc file")
            raise

    # Move Zarr output
    # Odd error with shutil.move that throws an error with Path
    # But this will be fixed in Python 3.9 (i.e. update later)
    zr_output = Path(key).with_suffix(".zarr.zip")

    if zr_output.exists():
        shutil.rmtree(zr_output)
    shutil.move(zr_str, zr_output.as_posix())

    # Unlink leftover files
    Path(key).with_suffix(".bin3D").unlink()

    for item in TMPDIR.glob("*"):
        item.unlink()

    # Mark Zarr validation complete
    update_dict(key, flag=4)
