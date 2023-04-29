"""
pytest fixtures for the project.

Fixtures:
    downloader: A queue fixture to simulate the queue of files to download

    semaphore: A fixture to provide an `asyncio` semaphore for
        controlling concurrent tasks

    add_file_to_queue: A fixture that takes a `downloader` object and returns
        a function for adding a file_info to the `file_queue` fixture

    add_dir_to_queue: A fixture that takes a `downloader` object and returns
        a function for adding a dir_info to the `dir_queue` fixture

    clear_dir_queue: A fixture that takes a `downloader` object and returns
        a function for clearing the `dir_queue` fixture
"""

import asyncio
from typing import Callable, Dict

import pytest
import pytest_mock

from project.app.download import RepoDownloader


@pytest.fixture()
def async_semaphore(mocker: pytest_mock.MockFixture) -> asyncio.Semaphore:
    semaphore = asyncio.Semaphore(3)
    mocker.patch.object(semaphore, 'acquire', return_value=None)
    mocker.patch.object(semaphore, 'release', return_value=None)
    return semaphore


@pytest.mark.parametrize('semaphore', [async_semaphore])
@pytest.fixture()
def repo_downloader(semaphore: asyncio.Semaphore) -> RepoDownloader:
    downloader = RepoDownloader('https://example.com/', '', 3)
    downloader.semaphore = semaphore
    return downloader


@pytest.mark.parametrize('downloader', [repo_downloader])
@pytest.fixture()
def add_file_to_queue(downloader: 'RepoDownloader'):
    def _add_file_to_queue(file_info):  # noqa: WPS430
        downloader.file_queue.put_nowait(file_info)

    return _add_file_to_queue


@pytest.fixture()
def add_dir_to_queue(repo_downloader) -> Callable[[Dict], None]:
    def _add_dir_to_queue(file_info):
        repo_downloader.dir_queue.put_nowait(file_info)

    return _add_dir_to_queue


@pytest.fixture()
def clear_dir_queue(repo_downloader) -> Callable[[], None]:
    def _clear_dir_queue():
        repo_downloader.dir_queue._queue.clear()

    return _clear_dir_queue
