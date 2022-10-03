"""
WiP.

Soon.
"""

# region [Imports]

# * Typing Imports --------------------------------------------------------------------------------------->
from typing import Optional, TypeAlias, Union, Callable
from hashlib import blake2b, md5

# * Standard Library Imports ---------------------------------------------------------------------------->
import shutil
import subprocess
from pathlib import Path
from contextlib import contextmanager
import os
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()
GIT_EXE = shutil.which('git.exe')
# endregion[Constants]
PATH_TYPE: TypeAlias = Union[str, os.PathLike[str], Path]


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


@contextmanager
def change_cwd(target_cwd: "PATH_TYPE"):
    old_cwd = Path.cwd()
    new_cwd = Path(target_cwd)
    if new_cwd.is_dir() is False:
        raise FileNotFoundError(f"The target_cwd({new_cwd.as_posix()!r}) either does not exist or is a file and not a directory.")
    os.chdir(new_cwd)
    yield
    os.chdir(old_cwd)


FILE_HASH_INCREMENTAL_THRESHOLD: int = 52428800  # 50mb


def file_hash(in_file: "PATH_TYPE", hash_algo: Callable = blake2b) -> str:
    in_file = Path(in_file)
    if not in_file.is_file():
        raise OSError(f"The path {in_file.as_posix()!r} either does not exist or is a Folder.")
    if in_file.stat().st_size > FILE_HASH_INCREMENTAL_THRESHOLD:
        _hash = hash_algo(usedforsecurity=False)
        with in_file.open("rb", buffering=FILE_HASH_INCREMENTAL_THRESHOLD // 4) as f:
            for chunk in f:
                _hash.update(chunk)
        return _hash.hexdigest()

    return hash_algo(in_file.read_bytes(), usedforsecurity=False).hexdigest()


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
