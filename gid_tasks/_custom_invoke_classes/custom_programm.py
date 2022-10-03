"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
import invoke

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class GidTaskProgramm(invoke.Program):

    def __init__(self,
                 version=...,
                 namespace=...,
                 name=...,
                 binary=...,
                 loader_class=...,
                 executor_class=...,
                 config_class=...,
                 binary_names=...) -> None:
        super().__init__(version, namespace, name, binary, loader_class, executor_class, config_class, binary_names)


# region[Main_Exec]

if __name__ == '__main__':
    pass

# endregion[Main_Exec]
