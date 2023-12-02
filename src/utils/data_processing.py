from typing import List


def read_objects_from_file(file_path: str) -> List[str]:
    """
    Reads objects from a file and returns them as a list.

    Args:
        file_path (str): Path to the file containing objects.

    Returns:
        List[str]: A list of objects read from the file.
    """
    with open(file_path, "r") as file:
        return [line.strip() for line in file.readlines() if line.strip()]
