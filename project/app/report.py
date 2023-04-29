from typing import Dict, List

from .utils import get_sha256_by_file


def build_sha256_dict_report(file_names: List[str], remove_folder='') -> Dict:
    dictionary_of_caches = {}

    for full_name in file_names:
        local_name = full_name.lstrip(remove_folder)
        *dirs, file_name = local_name.lstrip('\\').split('\\')
        destination_folder = dictionary_of_caches
        for dir in dirs:
            next_dir = destination_folder.setdefault(dir, {})
            destination_folder = next_dir
        destination_folder[file_name] = get_sha256_by_file(full_name)
    return dictionary_of_caches
