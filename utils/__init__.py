"""
utils package.
"""
import json


def load_json_file(file_path: str) -> dict:
    """
    Load a json file and return dict values from the given file path.
    Args:
        file_path: string of file path.

    Returns:
        dict
    """
    with open(file_path, "r") as file:
        return json.load(file)

