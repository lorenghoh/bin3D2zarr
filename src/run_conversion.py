from lib.handler import update_dict

import bin3D_to_nc as bin3d


def convert():
    key = update_dict()
    if key is None:
        return False

    try:
        bin3d.bin3D_to_nc(key)
    except Exception:
        raise Exception

    bin3d.nc_to_zarr(key)


if __name__ == "__main__":
    flag = True
    while flag:
        flag = convert()
