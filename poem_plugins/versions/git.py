import abc
from dataclasses import dataclass

from cleo.events.console_command_event import ConsoleCommandEvent
from cleo.events.console_events import COMMAND
from cleo.events.event_dispatcher import EventDispatcher
from poetry.console.application import Application
from poetry.console.commands.build import BuildCommand
from poetry.core.utils.helpers import module_name
from poetry.poetry import Poetry
from tomlkit.toml_document import TOMLDocument

from poem_plugins.base import BasePlugin
from poem_plugins.config import Config, VersionEnum
from poem_plugins.general.versions import Version
from poem_plugins.general.versions.drivers import IVervsionDriver
from poem_plugins.general.versions.drivers.git import GitLongVersionDriver


class IVersionPlugin(abc.ABC):
    @abc.abstractmethod
    def _should_be_used(self, config: Config) -> bool:
        raise NotImplementedError


class BaseVersionPlugin(BasePlugin, IVersionPlugin, abc.ABC):
    driver: IVervsionDriver

    VERSION_TEMPLATE = (
        "# THIS FILE WAS GENERATED BY \"{whoami}\"\n"
        "# NEWER EDIT THIS FILE MANUALLY\n"
        "\n"
        "version_info = ({major}, {minor}, {patch})\n"
        "__version__ = \"{version}\"\n"
    )

    def _write_pyproject(
        self, poetry: Poetry, version: Version, config: Config,
    ) -> None:
        if not config.update_pyproject:
            return
        content: TOMLDocument = poetry.file.read()
        poetry_content = content["tool"]["poetry"]  # type: ignore
        poetry_content["version"] = str(version)  # type: ignore
        poetry.file.write(content)

    def _write_module(
        self, poetry: Poetry, version: Version, config: Config,
    ) -> None:
        if not config.update_pyproject:
            return
        package_name = module_name(poetry.package.name)
        with open(f"{package_name}/version.py", "w+") as file:
            file.write(
                self.VERSION_TEMPLATE.format(
                    whoami=".".join((
                        self.__class__.__module__,
                        self.__class__.__name__,
                    )),
                    major=version.major,
                    minor=version.minor,
                    patch=version.patch,
                    version=str(version),
                ),
            )
    def activate(self, application: Application) -> None:
        if not application.event_dispatcher:
            return
        application.event_dispatcher.add_listener(
            COMMAND, self._set_version,
        )

    def _set_version(self, event: ConsoleCommandEvent, event_name: str, dispatcher: EventDispatcher) -> None:
        command = event.command
        if not isinstance(command, BuildCommand):
            return
        io = event.io
        poetry = command.poetry
        config: Config = self.get_config(poetry)
        if not self._should_be_used(config):
            return
        try:
            version = self.driver.get_version(config.git_version_prefix)
        except Exception as exc:
            io.write_error_line(f"<b>poem-plugins</b>: {exc}")
            raise exc

        io.write_line(
            f"<b>poem-plugins</b>: Setting version to: {version}",
        )
        poetry.package.version = str(version)  # type: ignore

        self._write_pyproject(poetry, version, config)
        self._write_module(poetry, version, config)


@dataclass
class GitLongVersionPlugin(BaseVersionPlugin):
    driver: IVervsionDriver = GitLongVersionDriver()

    def _should_be_used(self, config: Config) -> bool:
        return config.version_plugin == VersionEnum.GIT_LONG
