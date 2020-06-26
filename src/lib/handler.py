import json

from .lock import f_lock
from .config import read_config


config = read_config()

def update_dict(key=None, target=4, flag=1):
    pwd = config["pwd"]
    with f_lock(f"{pwd}/bin3D_list.json") as json_file:
        json_dict = json.load(json_file)

        if key is None:
            for key in json_dict.keys():
                if json_dict[key] != target:
                    break
        json_dict[key] = flag
    
    with open(f"{pwd}/bin3D_list.json", 'w+') as json_file:
        json_file.write(json.dumps(json_dict, indent=4))

    return key


def find_exclusion_list(file_name):
    # Assume file_name is string
    tag = file_name.split('_')[1]

    if tag in ['CORE', 'CLOUD']:
        exc_list = []
    else:
        exc_list = ['QI', 'NI', 'QS', 'NS', 'QG', 'NG']

    return exc_list
