import os, json, pathlib


def write_template():
    with open("config.json", "w") as f:
        config = {
            "root": "",
            "casename": "",
            "src": "OUT_3D",
            "bin3D2nc": "UTIL/bin3D2nc",
        }
        json.dump(config, f, indent=0)


def read_config():
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        write_template()

        print("Config template generated. Complete config.json \n")
        raise
    return config


if __name__ == "__main__":
    read_config()

    # Confirm config output
    print(read_config())
