"""Модуль для работы с API сервиса X."""


def generate_contents_url(repo_name: str, **kwargs: str) -> str:
    """Generate a report with sha256 hashes."""
    base_url = 'https://gitea.radium.group/api/v1/repos/'
    repo_url = '{0}{1}/contents'.format(base_url, repo_name)

    if kwargs:
        query_params = '&'.join(['='.join(item) for item in kwargs.items()])
        return '{0}?{1}'.format(repo_url, query_params)
    return repo_url
