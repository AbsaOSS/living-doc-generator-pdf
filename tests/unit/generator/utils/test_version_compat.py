import pytest

from generator.utils.version_compat import (
    MISSING,
    CompatibilityWarning,
    VersionCompatibilityError,
    check_schema_version,
)


def test_absent_key_raises_value_error() -> None:
    with pytest.raises(VersionCompatibilityError) as exc_info:
        check_schema_version(MISSING)
    assert "absent" in str(exc_info.value)


def test_default_arg_is_missing() -> None:
    with pytest.raises(VersionCompatibilityError):
        check_schema_version()


def test_explicit_null_raises_value_error() -> None:
    with pytest.raises(VersionCompatibilityError) as exc_info:
        check_schema_version(None)
    assert "null" in str(exc_info.value)


@pytest.mark.parametrize("value", ["", "   ", "\t\n"])
def test_blank_declared_raises_value_error(value) -> None:
    with pytest.raises(VersionCompatibilityError) as exc_info:
        check_schema_version(value)
    assert "schema_version" in str(exc_info.value)


@pytest.mark.parametrize(
    "value",
    [
        "generator-ready-v1.0.0",
        "coverage-matrix-v1.0.0",
        "1.0",
        "1.2.3",
        "generator-ready-v1.5.0-rc.1",
        "1.0.0-rc.1",
        "1.0.0+build.7",
        "generator-ready-v1.2.3-rc.1+build.7",
    ],
)
def test_in_range_returns_empty(value) -> None:
    assert check_schema_version(value) == []


@pytest.mark.parametrize("value", ["generator-ready-v2.0.0", "thing-v0.9.0", "2.0.0-rc.1"])
def test_out_of_range_returns_single_warning(value) -> None:
    warnings = check_schema_version(value)
    assert len(warnings) == 1
    warning = warnings[0]
    assert isinstance(warning, CompatibilityWarning)
    assert warning.code == "schema_version_out_of_range"
    assert warning.context == value


@pytest.mark.parametrize(
    "value", ["generator-ready", "abc", "v-nope", "1.0.0-", "1.2.3.4"]
)
def test_unparseable_raises_value_error(value) -> None:
    with pytest.raises(VersionCompatibilityError) as exc_info:
        check_schema_version(value)
    assert isinstance(exc_info.value, ValueError)
    assert "schema_version" in str(exc_info.value)


@pytest.mark.parametrize("value", [1.0, 2, 0, True, ["1.0.0"], {"v": "1.0.0"}])
def test_non_string_raises_value_error(value) -> None:
    with pytest.raises(VersionCompatibilityError) as exc_info:
        check_schema_version(value)
    assert isinstance(exc_info.value, ValueError)
    assert "must be a string" in str(exc_info.value)


def test_compatibility_warning_to_dict_shape() -> None:
    warning = CompatibilityWarning(code="c", message="m", context="ctx")
    assert warning.to_dict() == {"code": "c", "message": "m", "context": "ctx"}
