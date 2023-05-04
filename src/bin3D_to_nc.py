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
BIN3D2NC = Path(f"{CONFIG['root']}/{CONFIG['case']}/{CONFIG['bin3D2nc']}")
DEST = Path(f"{CONFIG['output']}")

# Use TMPDIR for Torque jobs
# Otherwise use destination directory
f_tmp = True
try:
    TMPDIR = Path(os.environ["tmp"])
except KeyError:
    f_tmp = False
    TMPDIR = DEST

def _xopen(target):
    """
    Helper function for xarray.open_dataset()
    """
    if target.suffix == ".nc":
        ds = xr.open_dataset(target)
    elif target.suffix == ".zarr":
        ds = xr.open_zarr(target)
    else:
        raise TypeError("Dataset type not recognized")

    return ds


def bin3D_to_nc(key, target=4, flag=1, print_stdout=False):
    if f_tmp:
        bin3D2nc = TMPDIR / BIN3D2NC.name
        _key = TMPDIR / 'tmp.bin3D'

        shutil.copy(BIN3D2NC, bin3D2nc)
        shutil.copy(key, _key)
    else:
        bin3D2nc = BIN3D2NC
        _key = TMPDIR / key

    nc_name = TMPDIR / Path(_key).with_suffix('.nc').name

    try:
        result = sp.run([bin3D2nc, _key], check=True, capture_output=True,)

        if f_tmp:
            os.rename(Path(_key).with_suffix('.nc'), nc_name)
    except sp.CalledProcessError as e:
        print(f"Error translating {key}\n", e.output)

        # Open and mark file incomplete
        update_dict(key, target=target, flag=flag)
        raise

    if f_tmp:
        bin3D2nc.unlink()

    if print_stdout:
        print(result.stdout)

    # When all operations are complete
    update_dict(key, flag=2)


def nc_to_zarr(key):
    _key = TMPDIR / Path(key).with_suffix(".nc")
    exc_list = find_exclusion_list(_key.name)

    with _xopen(_key) as ds_nc:
        try:
            ds_nc = ds_nc.squeeze("time").drop(exc_list)
        except Exception:
            raise ValueError

        try:
            zr_path = _key.with_suffix(".zarr")
            with zr.NestedDirectoryStore(f"{zr_path}") as store:
                ds_nc.to_zarr(store, mode="w")

            # Mark Zarr conversion complete
            update_dict(key, flag=3)

            # Validate Zarr output against netCDF
            validate_zarr(key)
        except ValueError:
            print(Path(key))
            print("! Duplicate found. Check leftover zarr folder. \n")


def validate_zarr(key):
    nc_path = TMPDIR / Path(key).with_suffix(".nc")
    zr_path = TMPDIR / Path(key).with_suffix(".zarr")

    exc_list = find_exclusion_list(nc_path.name)

    with _xopen(nc_path) as d_nc, _xopen(zr_path) as d_za:
        try:
            d_nc = d_nc.squeeze("time").drop(exc_list)
            flag = d_nc.equals(d_za)

            if flag is False:
                raise ValueError
        except ValueError:
            print("Translated Zarr dataset does not match .nc file")
            raise

    # Unlink intermediary files
    Path(nc_path).with_suffix(".bin3D").unlink()
    Path(nc_path).unlink()

    if f_tmp:
        # Clean up tmp directory
        # Move Zarr output file
        zr_output = DEST / Path(key).with_suffix(".zarr")

        if zr_output.exists():
            zr_output.unlink()
        shutil.move(zr_path, zr_output.as_posix())

        # Unlink temporary files
        for item in TMPDIR.glob("*"):
            item.unlink()

    # Mark Zarr validation complete
    update_dict(key, flag=4)
