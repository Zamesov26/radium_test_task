import asyncio
import os
from http import HTTPStatus
from typing import Dict, List, Union

import aiohttp

from .utils import (
    async_download_file,
    create_folder_if_not_exist,
    get_unfinished_tasks,
)


class RepoDownloader(object):
    def __init__(
        self: 'RepoDownloader',
        repo_url: str,
        destination_folder: str,
        max_concurrent_tasks: int,
    ) -> None:
        """Return."""
        self.destination_folder = destination_folder

        self.file_queue = asyncio.Queue()
        self.dir_queue = asyncio.Queue()
        self.dir_queue.put_nowait({'url': repo_url})

        self.tasks = set()

        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.session: Union[aiohttp.ClientSession, None] = None

    async def create_task(self: 'RepoDownloader') -> None:
        """
        Create task from "file_queue" or "dir_queue".

        This function checks two queues, one for downloading files and another
        for downloading directories(file list). If there is data in either
        queue, it creates a single task with priority given to files,
        to download the available items from the queues.
        """
        if not self.file_queue.empty():
            file_info = await self.file_queue.get()
            await self.semaphore.acquire()
            task = asyncio.create_task(self.download_file(file_info))
            task.add_done_callback(lambda res: self.semaphore.release())
            self.tasks.add(task)

        elif not self.dir_queue.empty():
            file_info = await self.dir_queue.get()
            await self.semaphore.acquire()
            task = asyncio.create_task(self.get_file_list_from_dir(file_info))
            task.add_done_callback(lambda res: self.semaphore.release())
            self.tasks.add(task)

    async def download(self: 'RepoDownloader') -> None:
        self.session = aiohttp.ClientSession()
        await self.create_task()
        while self.tasks:
            await self.create_task()
            self.tasks = get_unfinished_tasks(self.tasks)
            await asyncio.sleep(0)

        await self.session.close()

    async def get_file_list_from_dir(
        self: 'RepoDownloader',
        file_info: Dict,
    ) -> List[Dict]:
        url = file_info.get('url')
        if not url:
            return []
        async with self.session.get(url) as response:
            if response.status != HTTPStatus.OK:
                return []
            res = await response.json()
        await self.adding_to_queues(res)

    async def download_file(self: 'RepoDownloader', file_info: Dict) -> None:
        url = file_info.get('url')
        if not url:
            return
        file_path = file_info.get('path')
        if not file_path:
            return
        full_path_file = os.path.join(self.destination_folder, file_path)
        await async_download_file(self.session, url, full_path_file)

    async def adding_to_queues(
        self: 'RepoDownloader',
        files_info: List[Dict],
    ) -> None:
        for file_info in files_info:
            if file_info.get('type') == 'dir':
                create_folder_if_not_exist(
                    self.destination_folder,
                    file_info.get('path'),
                )
                await self.dir_queue.put(file_info)
            elif file_info.get('type') == 'file':
                await self.file_queue.put(file_info)
