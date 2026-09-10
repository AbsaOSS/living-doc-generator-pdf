import pytest

from generator.utils.version_compat import (
    CompatibilityWarning,
    VersionCompatibilityError,
    check_schema_version,
)


@pytest.mark.parametrize("value", [None, "", "   ", "\t\n"])
def test_absent_or_blank_returns_empty(value) -> None:
    assert check_schema_version(value) == []


@pytest.mark.parametrize(
    "value",
    ["generator-ready-v1.0.0", "coverage-matrix-v1.0.0", "1.0", "1.2.3"],
)
def test_in_range_returns_empty(value) -> None:
    assert check_schema_version(value) == []


@pytest.mark.parametrize("value", ["generator-ready-v2.0.0", "thing-v0.9.0"])
def test_out_of_range_returns_single_warning(value) -> None:
    warnings = check_schema_version(value)
    assert len(warnings) == 1
    warning = warnings[0]
    assert isinstance(warning, CompatibilityWarning)
    assert warning.code == "schema_version_out_of_range"
    assert warning.context == value


@pytest.mark.parametrize("value", ["generator-ready", "abc", "v-nope"])
def test_unparseable_raises_value_error(value) -> None:
    with pytest.raises(VersionCompatibilityError) as exc_info:
        check_schema_version(value)
    assert isinstance(exc_info.value, ValueError)
    assert "schema_version" in str(exc_info.value)


def test_compatibility_warning_to_dict_shape() -> None:
    warning = CompatibilityWarning(code="c", message="m", context="ctx")
    assert warning.to_dict() == {"code": "c", "message": "m", "context": "ctx"}
