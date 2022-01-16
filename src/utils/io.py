import json


def read_json(file_path: str) -> dict:
    """Reads json file and return a dict
    """
    with open(file_path) as f:
        return json.load(f)


def read_file(file_path: str) -> str:
    """Reads file and return the content
    """
    with open(file_path) as f:
        return f.read()
