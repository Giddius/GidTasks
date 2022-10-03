from typing import Optional, Union
import pytest
from pytest import param
from gid_tasks.version_handling.version_item import Version


version_as_string_params = [param(0, 0, 1, None, "0.0.1", id="simple no extra"),
                            param(1, 2, 3, 4, "1.2.3.4", id="simple int extra"),
                            param(1, 2, 3, "post1", "1.2.3.post1", id="simple str extra")]


@pytest.mark.parametrize(["major", "minor", "patch", "extra", "result"], version_as_string_params,)
def test_version_as_string(major: int, minor: int, patch: int, extra: Optional[Union[int, str]], result: str):
    version_object = Version(major=major, minor=minor, patch=patch, extra=extra)
    assert version_object.major == major
    assert version_object.minor == minor
    assert version_object.patch == patch
    assert version_object.extra == extra

    assert str(version_object) == result


version_increment_params = [param(Version(0, 0, 1), "increment_patch", {"major": 0, "minor": 0, "patch": 2, "extra": None}, id="simple no extra increment patch"),
                            param(Version(0, 0, 1), "increment_minor", {"major": 0, "minor": 1, "patch": 0, "extra": None}, id="simple no extra increment minor"),
                            param(Version(0, 0, 1), "increment_major", {"major": 1, "minor": 0, "patch": 0, "extra": None}, id="simple no extra increment major"),
                            param(Version(0, 0, 1, "post1"), "increment_major", {"major": 1, "minor": 0, "patch": 0, "extra": None}, id="simple str extra increment major"),
                            param(Version(0, 14, 3), "increment_major", {"major": 1, "minor": 0, "patch": 0, "extra": None}, id="advanced no extra increment major"),
                            param(Version(1, 2, 3), "increment_minor", {"major": 1, "minor": 3, "patch": 0, "extra": None}, id="advanced no extra increment minor"),
                            param(Version(1, 2, 3), "increment_patch", {"major": 1, "minor": 2, "patch": 4, "extra": None}, id="advanced no extra increment patch")]


@pytest.mark.parametrize(["version_obj", "value_to_increment", "new_values"], version_increment_params)
def test_version_increment(version_obj: Version, value_to_increment: str, new_values: dict[str, Union[str, int]]):
    new_version_obj = getattr(version_obj, value_to_increment)()
    assert new_version_obj is not version_obj
    assert new_version_obj != version_obj

    assert new_version_obj > version_obj

    for k, v in new_values.items():
        assert getattr(new_version_obj, k) == v
