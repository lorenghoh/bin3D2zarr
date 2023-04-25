import glob
import json

from pathlib import Path
from collections import defaultdict as dd

import lib.config

config = lib.config.read_config()
pwd = config["pwd"]


def main():
    bin3D_dir = f"{config['root']}/{config['case']}/OUT_3D/"

    print(f"Target directory is: \n\t {bin3D_dir} \n")

    file_list = sorted(glob.glob(f"{bin3D_dir}/{config['case']}_*.bin3D"))
    file_dict = dd(int)
    for item in file_list:
        file_dict[Path(item).name] = 0

    for item in file_list[:8]:
        print(Path(item).name)

    with open(f"{pwd}/bin3D_list.json", "w") as jf:
        jf.write(json.dumps(file_dict, indent=4))


if __name__ == "__main__":
    main()
