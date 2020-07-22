import json

from pathlib import Path

# Resolve file path for project working directory
pwd = Path(__file__).absolute().parents[2]


def write_template():
    with open(f"{pwd}/config.json", "w") as config_file:
        config = {
            "pwd": pwd.as_posix(),
            "root": "",
            "casename": "",
            "output": "",
            "bin3D2nc": "UTIL/bin3D2nc",
        }
        json.dump(config, config_file, indent=0)


def read_config():
    try:
        with open(f"{pwd}/config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        write_template()

        print("Config template generated. Complete config.json \n")
        raise
    return config


def show_config():
    pass


if __name__ == "__main__":
    config = read_config()

    # Confirm config output
    print(config)
