"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from enum import Enum, auto, unique
from pathlib import Path

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


@unique
class PipManager(Enum):
    FLIT = auto()
    POETRY = auto()


@unique
class Sentinel(Enum):
    MISSING = auto()

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
