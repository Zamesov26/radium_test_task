import asyncio
import json
import tempfile

from app import get_list_files
from app import RepoDownloader
from app import generate_contents_url
from app import build_sha256_dict_report

if __name__ == '__main__':
    with tempfile.TemporaryDirectory() as temp_dir:
        repository_name = 'radium/project-configuration'
        url = generate_contents_url(repository_name, ref='HEAD')

        repo_downloader = RepoDownloader(
            repo_url=url,
            destination_folder=temp_dir,
            max_concurrent_tasks=10,
        )
        loop = asyncio.get_event_loop()
        loop.run_until_complete(repo_downloader.download())
        loop.close()

        file_list = get_list_files(temp_dir)

        dictionary_of_caches = build_sha256_dict_report(file_list, temp_dir)

        with open('reports/report.json', 'w') as result_file:
            json.dump(dictionary_of_caches, result_file, indent=4)
