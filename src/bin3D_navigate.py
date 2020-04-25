import os
import json
import lib.config

c = lib.config.read_config()


def main():
    # Read data storage configuration
    output = f"""
            SAM output storage configuration:
            {c['root']}
	    {c['root']}/{c['src']}
	    {c['root']}/{c['bin3D2nc']}
        """
    print(output)

    with open("bin3D_list.json", "r") as jf:
        jd = json.load(jf)

    _to_nc = 0
    _finished = 0
    for i in jd:
        if jd[i] == 2:
            _finished += 1
        elif jd[i] == 1:
            _to_nc += 1
        else:
            pass

    output = f"""
                {len(jd)} items currently in bin3D_list file
                {_finished} translated to netCDF4 format
                {_to_nc} being processed to netCDF4 format
            """
    print(output)


if __name__ == "__main__":
    main()
