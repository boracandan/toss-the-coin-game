from src.settings import *


def write_dict_to_json(dict, *path):
    fullPath = join(*path)
    try:
        with open(fullPath, "w") as f:
            json.dump(dict, f)
    except FileNotFoundError:
        print(f"File not found: {fullPath}")
    except Exception as e:
        print(f"Error clearing file: {e}")


def clear_file(*path):
    fullPath = join(*path)
    try:
        with open(fullPath, 'w') as file:
            pass
    except FileNotFoundError:
        print(f"File not found: {fullPath}")
    except Exception as e:
        print(f"Error clearing file: {e}")


def pos_int(val):
    integer = int(val)
    if integer <= 0:
        raise ValueError 
    return integer