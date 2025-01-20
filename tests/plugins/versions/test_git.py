from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any, Mapping

import pytest
from cleo.io.buffered_io import BufferedIO
from poetry.console.commands.build import BuildCommand
from poetry.console.commands.lock import LockCommand
from poetry.poetry import Poetry

from poem_plugins.config import VersionProviderEnum
from poem_plugins.config.git import GitVersionFormatEnum
from poem_plugins.general.version import Version


@pytest.fixture
def version_config() -> Mapping[str, Any]:
    return dict(
        provider=VersionProviderEnum.GIT,
        update_pyproject=True,
        write_version_file=True,
        git=dict(
            format=GitVersionFormatEnum.SHORT,
        ),
    )


def test_skip_non_build(poetry_io: BufferedIO, run_command) -> None:
    run_command(LockCommand)
    assert "poem-plugins" not in poetry_io.fetch_output()


def test_output_version(poetry_io: BufferedIO, run_command) -> None:
    run_command(BuildCommand)
    expected = "poem-plugins: Setting version to: 1.2.0\n"
    assert poetry_io.fetch_output().startswith(expected)


def test_file_version(
    simple_project: Path,
    expected_version: Version,
    run_command,
) -> None:
    run_command(BuildCommand)
    version_path = simple_project / "simple_project" / "version.py"
    spec = spec_from_file_location(
        "simple_project.version",
        version_path,
    )
    assert spec
    version_module = module_from_spec(spec)
    spec.loader.exec_module(version_module)
    assert version_module.__version__ == str(expected_version)
    assert version_module.version_info == expected_version.release[:3]


def test_pyproject_version(
    expected_version: Version,
    run_command,
    poetry: Poetry,
) -> None:
    run_command(BuildCommand)
    content = poetry.file.read()
    poetry_content = content["tool"]["poetry"]
    assert poetry_content["version"] == str(expected_version)
