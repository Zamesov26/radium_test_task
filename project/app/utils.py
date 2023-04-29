import asyncio
import hashlib
import os
from http import HTTPStatus
from typing import Set, List

import aiofiles
import aiohttp


def get_sha256_by_file(filename: str) -> str:
    hasher = hashlib.sha256()
    with open(filename, 'rb') as open_file:
        chunk_size = 4096
        while True:
            chunk = open_file.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def create_folder_if_not_exist(dest_folder: str, local_file_path: str) -> None:
    if not local_file_path:
        return
    full_path = os.path.join(dest_folder, local_file_path)
    if not os.path.exists(full_path):
        os.makedirs(full_path)


def get_unfinished_tasks(tasks: Set[asyncio.Task]) -> Set[asyncio.Task]:
    unfinished_tasks = set()
    for task in tasks:
        if not task.done():
            unfinished_tasks.add(task)
    return unfinished_tasks


async def async_download_file(
    session: aiohttp.ClientSession,
    url: str,
    full_path_file: str,
    chunk_size: int = 1024,
) -> None:
    async with session.get(url) as response:
        if response.status != HTTPStatus.OK:
            return
        async with aiofiles.open(full_path_file, mode='wb') as open_file:
            while True:
                chunk = await response.content.read(chunk_size)
                if not chunk:
                    break
                await open_file.write(chunk)


def get_list_files(path: str) -> List[str]:
    file_list = []
    for root, _dirs, files in os.walk(path):
        for file_name in files:
            file_list.append(os.path.join(root, file_name))
    return file_list
