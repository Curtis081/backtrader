import os


def delete_file_if_exists(file_path):
    """
    If the file exists, delete the file.

    :param file_path: str, target file path
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"file {file_path} deleted")
    else:
        print(f"file {file_path} does not exist, no need to delete")


def write_dict_to_file(file_path, data, header=None):
    """
    Write a dictionary to a file. If the file does not exist, add a header.

    :param file_path: str, target file path
    :param data: dict, need to write dictionary
    :param header: str, optional, file header(only write when file does not exist)
    """
    file_exists = os.path.exists(file_path)

    with open(file_path, "a") as file:
        if not file_exists and header:
            file.write(header + "\n")
            file.write("-" * len(header) + "\n")

        if isinstance(data, dict):
            file.write(f"\n")
            for key, value in data.items():
                file.write(f"{key}: {value}\n")
        elif isinstance(data, str):
            file.write(f"{data}\n")

    print(f"dirctory contents written to {file_path}")
