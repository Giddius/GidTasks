"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
import re
from typing import TYPE_CHECKING
from pathlib import Path

# * Gid Imports ----------------------------------------------------------------------------------------->
from gid_tasks.errors import VersionNotFoundError
from gid_tasks.utility.enums import PipManager
from gid_tasks.version_handling.version_item import Version, get_specific_version

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from gid_tasks.project_info.project import MainModule

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()


# endregion[Constants]

VERSION_EXTRA_PARTS = r'|'.join([r"(post/d*)", r"(build/d*)", r"(alpha)"])

VERSION_PARTS_REGEX_PATTERN = rf"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>[\drc]+)\.?(?P<extra>{VERSION_EXTRA_PARTS})?"


VERSION_REGEXES = {PipManager.FLIT: re.compile(r"^\_\_version\_\_\s?\=\s?" + "[\'\"]?" + VERSION_PARTS_REGEX_PATTERN + "[\'\"]?", re.MULTILINE)}


class VersionFinder:

    def __init__(self, pip_manager: "PipManager", main_module: "MainModule") -> None:
        self.pip_manager = pip_manager
        self.regex = VERSION_REGEXES[self.pip_manager]
        self.main_module = main_module
        self.version: Version = None

    def _search_file(self, in_file: Path) -> bool:
        with in_file.open('r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, start=1):
                if version_match := self.regex.match(line.strip()):

                    self.version = get_specific_version(pip_manager=self.pip_manager, **version_match.groupdict(), file=in_file, line_number=line_num)
                    return True
        return False

    def find_version(self, force: bool = False) -> "Version":
        if self.version is not None and force is False:
            return self.version
        for file in self.main_module.get_all_python_files():
            if self._search_file(file) is True:
                return self.version
        raise VersionNotFoundError(f"Unable to find a file with the specific Version indicator for {self.pip_manager.name!r}.")

# region[Main_Exec]


if __name__ == '__main__':
    print(os.getenv("TESTING_SITE_CUSTOMIZE", "0"))


# endregion[Main_Exec]
