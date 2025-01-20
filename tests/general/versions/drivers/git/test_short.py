import pytest

from poem_plugins.config.git import GitProviderSettings, GitVersionFormatEnum
from poem_plugins.general.version import Version
from poem_plugins.general.version.drivers import IVersionDriver


@pytest.fixture
def git_settings() -> GitProviderSettings:
    return GitProviderSettings(format=GitVersionFormatEnum.SHORT)


def test_get_version(
    git_version_driver: IVersionDriver,
    expected_version: Version,
) -> None:
    assert git_version_driver.get_version() == expected_version


@pytest.mark.parametrize(
    "describe,expected", (
        (
            "1",
            Version(release=(1, 0, 10)),
        ),
        (
            "1.2",
            Version(release=(1, 2, 10)),
        ),
        (
            "1.2.3",
            Version(release=(1, 2, 13)),
        ),
        (
            "1.2.3.0",
            Version(release=(1, 2, 3, 10)),
        ),
        (
            "1.2a1",
            Version(release=(1, 2, 10), pre="a1"),
        ),
        (
            "1.2b1",
            Version(release=(1, 2, 10), pre="b1"),
        ),
        (
            "1.2rc1",
            Version(release=(1, 2, 10), pre="rc1"),
        ),
        (
            "1.2.post1",
            Version(release=(1, 2, 10), post=1),
        ),
        (
            "1.2.dev1",
            Version(release=(1, 2, 10), dev=1),
        ),
        (
            "1!1.2",
            Version(epoch=1, release=(1, 2, 10)),
        ),
        (
            "1!1.2.3a1.post1.dev1",
            Version(
                epoch=1, release=(1, 2, 13), pre="a1", post=1, dev=1,
            ),
        ),
    ),
)
def test_get_version_pep_440(
    get_mocked_git_version_driver, describe, expected,
) -> None:
    describe = "v" + describe + "-10-g3c3e199"
    driver = get_mocked_git_version_driver(describe=describe)
    assert driver.get_version() == expected


def test_get_version_malformed(get_mocked_git_version_driver) -> None:
    describe = "v1post123"
    driver = get_mocked_git_version_driver(describe=describe)
    with pytest.raises(
        RuntimeError,
        match="Failed to parse git version: '1post123' must conform to PEP 440",
    ):
        driver.get_version()


def test_render_version(
    git_version_driver: IVersionDriver,
    expected_version: Version,
) -> None:
    content = git_version_driver.render_version_file(expected_version)
    expected = "\n".join(
        (
            "# THIS FILE WAS GENERATED AUTOMATICALLY",
            '# BY: poem-plugins "git" plugin',
            "# NEVER EDIT THIS FILE MANUALLY",
            "",
            "version_info = (1, 2, 0)",
            '__version__ = "1.2.0"',
            "",
        ),
    )
    assert content == expected


def test_render_version_pep440(git_version_driver: IVersionDriver) -> None:
    version = Version(
        release=(1, 2, 3, 4),
        epoch=1,
        pre="a2",
        post=3,
        dev=4,
        commit=None,
    )
    content = git_version_driver.render_version_file(version)
    expected = "\n".join(
        (
            "# THIS FILE WAS GENERATED AUTOMATICALLY",
            '# BY: poem-plugins "git" plugin',
            "# NEVER EDIT THIS FILE MANUALLY",
            "",
            "version_info = (1, 2, 3)",
            '__version__ = "1!1.2.3.4a2.post3.dev4"',
            "",
        ),
    )
    assert content == expected
