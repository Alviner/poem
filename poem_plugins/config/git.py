from dataclasses import dataclass
from enum import unique
from types import MappingProxyType

from poem_plugins.config.base import BaseConfig
from poem_plugins.general.strenum import StrEnum


@unique
class GitVersionFormatEnum(StrEnum):
    LONG = "long"
    SHORT = "short"


@unique
class VersionSegmentBumpEnum(StrEnum):
    RELEASE = "release"
    POST_RELEASE = "post"
    DEV = "dev"


@dataclass
class GitProviderSettings(BaseConfig):
    MAPPERS = MappingProxyType(
        {
            "format": GitVersionFormatEnum,
            "version_prefix": str,
            "bump_segment": VersionSegmentBumpEnum,
        },
    )

    format: GitVersionFormatEnum = GitVersionFormatEnum.SHORT
    version_prefix: str = "v"
    bump_segment: VersionSegmentBumpEnum = VersionSegmentBumpEnum.RELEASE
