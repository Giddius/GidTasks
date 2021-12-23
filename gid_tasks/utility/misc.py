"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import shutil
import subprocess
from typing import Optional
from pathlib import Path

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()
GIT_EXE = shutil.which('git.exe')
# endregion[Constants]


def main_dir_from_git():
    cmd = subprocess.run([GIT_EXE, "rev-parse", "--show-toplevel"], capture_output=True, text=True, shell=True, check=True)
    main_dir = Path(cmd.stdout.rstrip('\n'))
    if main_dir.is_dir() is False:
        raise FileNotFoundError('Unable to locate main dir of project')
    return main_dir


def find_main_dir_by_pyproject_location():
    def _check(_folder: Path) -> Optional[Path]:
        for item in _folder.iterdir():
            if item.name.casefold() == "pyproject.toml":
                return _folder
        return _check(_folder.parent)
    return _check(Path.cwd())


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
