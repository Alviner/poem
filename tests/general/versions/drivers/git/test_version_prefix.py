import re

import pytest

from poem_plugins.config.git import GitProviderSettings, GitVersionFormatEnum
from poem_plugins.general.version import Version


@pytest.fixture
def git_settings() -> GitProviderSettings:
    return GitProviderSettings(format=GitVersionFormatEnum.SHORT)


def test_version_prefix_ok(get_mocked_git_version_driver, git_settings) -> None:
    describe = "v1.2.3-10-g3c3e199"
    driver = get_mocked_git_version_driver(describe=describe, git_settings=git_settings)
    assert driver.get_version() == Version(release=(1, 2, 13))


def test_version_prefix_fail(get_mocked_git_version_driver) -> None:
    describe = "1.2.3-10-g3c3e199"
    git_settings = GitProviderSettings(version_prefix="v")
    driver = get_mocked_git_version_driver(describe=describe, git_settings=git_settings)
    with pytest.raises(
        RuntimeError,
        match=re.escape(
            "Version tag must start with 'v' as defined in the plugin's config "
            "(or by default).",
        ),
    ):
        driver.get_version()
