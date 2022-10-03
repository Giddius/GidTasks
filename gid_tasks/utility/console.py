"""
WiP.

Soon.
"""

# region [Imports]

# * Typing Imports --------------------------------------------------------------------------------------->
from typing import TYPE_CHECKING, Any, Union

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
from rich.rule import Rule
from rich.style import Style
from rich.console import Group
from rich.console import Console as RichConsole

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from rich.text import TextType
    from rich.align import AlignMethod

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class DefaultRuleSettings:

    def __init__(self, characters: str, style: Union[str, Style], align: "AlignMethod") -> None:
        self.characters = characters
        self.style = style
        self.align = align

    @classmethod
    def from_kwargs(cls, kwargs: dict[str, Any]) -> "DefaultRuleSettings":
        characters = kwargs.pop("default_rule_characters", "-")
        style = kwargs.pop("default_rule_style", "rule.line")
        align = kwargs.pop("default_rule_align", "center")
        return cls(characters=characters, style=style, align=align)

    def as_dict(self) -> dict[str, Any]:
        return {"characters": self.characters,
                "style": self.style,
                "align": self.align}


class GidTaskConsole(RichConsole):

    def __init__(self, **kwargs) -> None:
        self.default_rule_settings = DefaultRuleSettings.from_kwargs(kwargs)
        super().__init__(**kwargs)

    def rule(self, title: "TextType" = None, *, characters: str = None, style: Union[str, Style] = None, align: "AlignMethod" = None) -> None:
        title = title or ""
        style = style or "rule.line"
        align = align or "center"
        characters = characters or self.default_rule_settings.characters
        return super().rule(title=title, characters=characters, style=style, align=align)

    def big_rule(self, title: "TextType" = None, *, characters: str = None, style: Union[str, Style] = None, align: "AlignMethod" = None) -> None:
        characters = characters or self.default_rule_settings.characters
        style = style or "rule.line"
        align = align or "center"
        title = title or ""
        top_bottom = Rule(title="", characters=characters, style=style, align=align)
        middle = Rule(title=title, characters=characters, style=style, align=align)
        self.print(Group(top_bottom, middle, top_bottom))

    def end_message(self):
        ...

    def start_message(self):
        ...


def make_console():
    kwargs = {"soft_wrap": True}
    return GidTaskConsole(**kwargs)


# region[Main_Exec]
if __name__ == '__main__':
    c = make_console()
    c.big_rule("[red]tt")

# endregion[Main_Exec]
