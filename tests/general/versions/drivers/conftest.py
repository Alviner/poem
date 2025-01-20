import pytest

from poem_plugins.config.git import GitProviderSettings
from poem_plugins.general.version.drivers.git import GitVersionDriver


@pytest.fixture
def git_settings() -> GitProviderSettings:
    return GitProviderSettings()


@pytest.fixture
def git_version_driver(git_settings) -> GitVersionDriver:
    return GitVersionDriver(git_settings)


class MockedGitVersionDriver(GitVersionDriver):

    _describe: str

    def __init__(self, *args, describe: str, **kwargs):
        super().__init__(*args, **kwargs)
        self._describe = describe

    def _git_describe(self) -> str:
        return self._describe


@pytest.fixture
def get_mocked_git_version_driver(git_settings):
    return lambda describe, git_settings=git_settings: (
        MockedGitVersionDriver(git_settings, describe=describe)
    )
