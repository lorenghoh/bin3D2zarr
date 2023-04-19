import glob
import json

from collections import defaultdict as dd

import lib.config

config = lib.config.read_config()
pwd = config["pwd"]


def main():
    bin3D_dir = f"{config['root']}/{config['casename']}/OUT_3D/"
    print(bin3D_dir)

    file_list = sorted(glob.glob(f"{bin3D_dir}/{config['casename']}_*.bin3D"))
    file_dict = dd(int)
    for item in file_list:
        file_dict[item] = 0

    for item in file_list[:12]:
        print(item)

    with open(f"{pwd}/bin3D_list.json", "w") as jf:
        jf.write(json.dumps(file_dict, indent=4))


if __name__ == "__main__":
    main()
