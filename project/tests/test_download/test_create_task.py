"""
Test for create_task method in RepoDownloader class.

Test that the method `create_task` creates a task for downloading either
a file or a directorybased on the queue with data and adds
it to the set of tasks.

The test uses `mocker` to mock the methods `download_file` and
`get_file_list_from_dir` to avoid actual downloads. It also uses
`repo_downloader_file_queue` and `asyncio_semaphore`
fixtures to simulate the data queues and a semaphore
for controlling concurrent tasks.

The test first puts a file_info item in the `file_queue` fixture and
then calls the `create_task` method. It asserts that `download_file`
is called with the expected arguments and that
the semaphore is acquired and then released.
Then it clears the set of tasks and repeats the
same process for the `dir_queue` fixture.

Finally, the test asserts that `download_file` and `get_file_list_from_dir`
are both called once and only once with their respective arguments.
"""
from typing import Callable, Dict

import pytest
import pytest_mock

from project.app.download import RepoDownloader


@pytest.mark.asyncio()
async def test_create_task_with_file_queue(
    mocker: pytest_mock.MockFixture,
    repo_downloader,
    add_file_to_queue: Callable[[Dict], None],
):
    file_info = {'file': 'test_file.txt'}
    m_create_task = mocker.patch('asyncio.create_task')
    mock_download_file = mocker.patch.object(
        repo_downloader, 'download_file', return_value=None,
    )

    add_file_to_queue(file_info)
    await repo_downloader.create_task()

    mock_download_file.assert_called_once_with(file_info)
    m_create_task.assert_called_once()
    assert len(repo_downloader.tasks) == 1
    assert repo_downloader.semaphore.acquire.called


@pytest.mark.asyncio()
async def test_create_task_with_dir_queue(
    mocker: pytest_mock.MockFixture,
    repo_downloader,
    clear_dir_queue: Callable[[], None],
    add_dir_to_queue: Callable[[Dict], None],
):
    dir_info = {'dir': 'test_dir'}
    m_create_task = mocker.patch('asyncio.create_task')
    mock_get_file_list_from_dir = mocker.patch.object(
        repo_downloader, 'get_file_list_from_dir', return_value=None,
    )

    clear_dir_queue()
    add_dir_to_queue(dir_info)
    await repo_downloader.create_task()

    mock_get_file_list_from_dir.assert_called_once_with(dir_info)
    m_create_task.assert_called_once()
    assert len(repo_downloader.tasks) == 1
    assert repo_downloader.semaphore.acquire.called


@pytest.mark.asyncio()
async def test_create_task_with_empty_queues(
    repo_downloader, clear_dir_queue: Callable[[], None],
):
    clear_dir_queue()
    await repo_downloader.create_task()

    assert not repo_downloader.tasks
    assert repo_downloader.semaphore.acquire.not_called()
