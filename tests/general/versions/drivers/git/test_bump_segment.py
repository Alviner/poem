import pytest

from poem_plugins.config.git import (
    GitProviderSettings, GitVersionFormatEnum, VersionSegmentBumpEnum,
)
from poem_plugins.general.version import Version


@pytest.fixture
def git_settings() -> GitProviderSettings:
    return GitProviderSettings(format=GitVersionFormatEnum.SHORT)


@pytest.mark.parametrize(
    "describe,segment,expected", (
        (
            "1",
            VersionSegmentBumpEnum.RELEASE,
            Version(release=(1, 0, 10)),
        ),
        (
            "1.2",
            VersionSegmentBumpEnum.RELEASE,
            Version(release=(1, 2, 10)),
        ),
        (
            "1.2.3",
            VersionSegmentBumpEnum.RELEASE,
            Version(release=(1, 2, 13)),
        ),
        (
            "1.2.3.4",
            VersionSegmentBumpEnum.RELEASE,
            Version(release=(1, 2, 3, 14)),
        ),
        (
            "1.2.post3",
            VersionSegmentBumpEnum.POST_RELEASE,
            Version(release=(1, 2, 0), post=13),
        ),
        (
            "1.2.dev3",
            VersionSegmentBumpEnum.DEV,
            Version(release=(1, 2, 0), dev=13),
        ),
    ),
)
def test_pep_440(
    get_mocked_git_version_driver, describe, segment, expected,
) -> None:
    describe = "v" + describe + "-10-g3c3e199"

    git_settings = GitProviderSettings(bump_segment=segment)
    driver = get_mocked_git_version_driver(describe=describe, git_settings=git_settings)
    assert driver.get_version() == expected


@pytest.mark.parametrize(
    "describe,segment,expected", (
        (
            "1.2.3.4",
            VersionSegmentBumpEnum.RELEASE,
            Version(release=(1, 2, 3, 4)),
        ),
        (
            "1.2",
            VersionSegmentBumpEnum.POST_RELEASE,
            Version(release=(1, 2, 0)),
        ),
        (
            "1.2",
            VersionSegmentBumpEnum.DEV,
            Version(release=(1, 2, 0)),
        ),
    ),
)
def test_pep_440_zero_commits(
    get_mocked_git_version_driver, describe, segment, expected,
) -> None:
    describe = "v" + describe + "-0-g3c3e199"

    git_settings = GitProviderSettings(bump_segment=segment)
    driver = get_mocked_git_version_driver(describe=describe, git_settings=git_settings)
    assert driver.get_version() == expected
