import re
import subprocess
import warnings
from dataclasses import dataclass
from shutil import which

from poem_plugins.config.git import (
    GitProviderSettings, GitVersionFormatEnum, VersionSegmentBumpEnum,
)
from poem_plugins.general.version import Version
from poem_plugins.general.version.drivers import IVersionDriver


GIT_BIN = which("git")
WARNING_TEXT = (
    '"git" binary was not found, this plugin this will not work properly'
)
if GIT_BIN is None:
    warnings.warn(WARNING_TEXT)


@dataclass
class GitVersionDriver(IVersionDriver):
    settings: GitProviderSettings

    VERSION_TEMPLATE: str = (
        "# THIS FILE WAS GENERATED AUTOMATICALLY\n"
        "# BY: {whoami}\n"
        "# NEVER EDIT THIS FILE MANUALLY\n"
        "\n"
        "version_info = ({major}, {minor}, {patch})\n"
        '__version__ = "{version}"\n'
    )

    def _get_version_pep_440(self, raw_version: str) -> Version:
        if raw_version.startswith(self.settings.version_prefix):
            raw_version = raw_version.removeprefix(self.settings.version_prefix)
        else:
            raise RuntimeError(
                f"Version tag must start with '{self.settings.version_prefix}' "
                f"as defined in the plugin's config (or by default).",
            )
        regex = (
            r"^((?P<epoch>\d+)!)?(?P<release>\d+(\.\d+)*)"
            r"(?P<pre>(a|b|rc)\d+)?(\.post(?P<post>\d+))?(\.dev(?P<dev>\d+))?"
            r"-(?P<commit_count>\d+)-(?P<commit>\S+)$"
        )
        match = re.match(regex, raw_version)
        if not match:
            raise RuntimeError(
                f"Failed to parse git version: '{raw_version}' must conform to "
                f"PEP 440",
            )
        groups = match.groupdict()
        epoch = groups["epoch"]
        pre, post, dev = groups["pre"], groups["post"], groups["dev"]
        commit_count = int(groups["commit_count"])
        commit = groups["commit"]
        release = list(map(int, groups["release"].split(".")))
        if len(release) < 3:
            release += [0] * (3 - len(release))

        segments = {
            "epoch": int(epoch) if epoch is not None else None,
            "pre": pre,
            "post": int(post) if post is not None else None,
            "dev": int(dev) if dev is not None else None,
            "commit": commit,
        }

        if commit_count:
            bump_segment = self.settings.bump_segment
            if bump_segment == VersionSegmentBumpEnum.RELEASE:
                print(release)
                release[-1] += commit_count
            else:
                segments[bump_segment.value] = segments[bump_segment.value] or 0
                segments[bump_segment.value] += commit_count  # type: ignore

        segments["release"] = tuple(release)

        if self.settings.format == GitVersionFormatEnum.SHORT:
            segments["commit"] = None

        return Version(**segments)  # type: ignore

    def _git_describe(self) -> str:
        if GIT_BIN is None:
            raise RuntimeError(WARNING_TEXT)

        result = subprocess.run(
            [GIT_BIN, "describe", "--long"],
            stdout=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError("Failed to find git version tag")
        return result.stdout.strip()

    def get_version(self) -> Version:
        raw_version = self._git_describe()
        return self._get_version_pep_440(raw_version)

    def render_version_file(
        self,
        version: Version,
    ) -> str:
        return self.VERSION_TEMPLATE.format(
            whoami='poem-plugins "git" plugin',
            major=version.release[0],
            minor=version.release[1],
            patch=version.release[2],
            version=str(version),
        )
