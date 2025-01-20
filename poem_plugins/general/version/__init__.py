import re
from typing import NamedTuple, Optional, Tuple


_REGEX_PRE = re.compile(r"^(?P<id>(a|b|rc))(?P<val>\d+)$")


class Version(NamedTuple):
    release: Tuple[int, ...]
    epoch: Optional[int] = None
    pre: Optional[str] = None
    post: Optional[int] = None
    dev: Optional[int] = None
    commit: Optional[str] = None

    def __str__(self) -> str:
        epoch = f"{self.epoch}!" if self.epoch is not None else ""
        pre = self.pre or ""
        post = f".post{self.post}" if self.post is not None else ""
        dev = f".dev{self.dev}" if self.dev is not None else ""
        commit = f"+{self.commit}" if self.commit is not None else ""
        version = (
            epoch +
            ".".join(map(str, self.release)) +
            "".join((pre, post, dev, commit))
        )
        return version
