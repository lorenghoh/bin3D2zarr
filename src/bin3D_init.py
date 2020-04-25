import glob
import json

from collections import defaultdict as dd

import lib.config

config = lib.config.read_config()


def main():
    fdir = f"{config['root']}/{config['src']}"

    file_list = sorted(glob.glob(f"{fdir}/{config['casename']}_*.bin3D"))
    file_dict = dd(int)
    for item in file_list:
        file_dict[item] = 0

    with open("bin3D_list.json", "w") as jf:
        jf.write(json.dumps(file_dict, indent=4))


if __name__ == "__main__":
    main()
