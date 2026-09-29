"""Comprehensive unit tests for the easy_date_formatter module."""

import datetime as dt
from datetime import timezone
import re
from unittest.mock import patch
import pytest

from py_simple_package.src import py_simple as pkg_root
from py_simple_package.src.py_simple import easy_date_formatter
from py_simple_package.src.py_simple.easy_date_formatter import (
    _FORMATS,
    _format_date,
    _get_future_date,
    _get_past_date,
    dd_mm_yyyy,
    future_dd_mm_yyyy,
    future_iso_8601,
    future_mm_dd_yyyy,
    future_slash_dd_mm_yyyy,
    future_slash_mm_dd_yyyy,
    get_future_pretty_date,
    get_past_pretty_date,
    get_pretty_date,
    iso_8601,
    list_available_formats,
    mm_dd_yyyy,
    past_dd_mm_yyyy,
    past_iso_8601,
    past_mm_dd_yyyy,
    past_slash_dd_mm_yyyy,
    past_slash_mm_dd_yyyy,
    slash_dd_mm_yyyy,
    slash_mm_dd_yyyy,
)

FROZEN_NOW = dt.datetime(2026, 4, 9, 14, 30, 45)
FROZEN_UTC_NOW = dt.datetime(2026, 4, 9, 14, 30, 45, tzinfo=timezone.utc)


class TestFormatRegistry:
    """Tests for format registry and internal formatting helpers."""

    def test_list_available_formats_returns_list(self):
        formats = list_available_formats()
        assert isinstance(formats, list)
        assert len(formats) == len(_FORMATS)

    def test_list_available_formats_contains_all_registered_keys(self):
        expected_keys = {
            "pretty",
            "dd-mm-yyyy",
            "mm-dd-yyyy",
            "dd/mm/yyyy",
            "mm/dd/yyyy",
            "ISO-8601",
        }
        assert set(list_available_formats()) == expected_keys

    def test_list_available_formats_returns_new_list_copy(self):
        formats = list_available_formats()
        formats.append("custom-format")
        assert "custom-format" not in _FORMATS
        assert "custom-format" not in list_available_formats()

    @pytest.mark.parametrize(
        ("fmt_key", "expected_str"),
        [
            ("pretty", "Thursday, April 09, 2026"),
            ("dd-mm-yyyy", "09-04-2026"),
            ("mm-dd-yyyy", "04-09-2026"),
            ("dd/mm/yyyy", "09/04/2026"),
            ("mm/dd/yyyy", "04/09/2026"),
            ("ISO-8601", "2026-04-09T14:30:45Z"),
        ],
    )
    def test_format_date_valid_keys(self, fmt_key, expected_str):
        sample_dt = dt.datetime(2026, 4, 9, 14, 30, 45)
        assert _format_date(sample_dt, fmt_key) == expected_str

    def test_format_date_invalid_key_raises_key_error(self):
        sample_dt = dt.datetime(2026, 4, 9, 14, 30, 45)
        with pytest.raises(KeyError):
            _format_date(sample_dt, "nonexistent-format-key")


class TestDateCalculationHelpers:
    """Tests for _get_past_date and _get_future_date internal helpers."""

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_get_past_date_zero_days(self, mock_dt):
        mock_dt.now.return_value = FROZEN_NOW
        assert _get_past_date(0) == FROZEN_NOW

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    @pytest.mark.parametrize(
        ("days", "expected_dt"),
        [
            (1, dt.datetime(2026, 4, 8, 14, 30, 45)),
            (9, dt.datetime(2026, 3, 31, 14, 30, 45)),
            (100, dt.datetime(2025, 12, 30, 14, 30, 45)),
        ],
    )
    def test_get_past_date_various_days(self, mock_dt, days, expected_dt):
        mock_dt.now.return_value = FROZEN_NOW
        assert _get_past_date(days) == expected_dt

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_get_future_date_zero_days(self, mock_dt):
        mock_dt.now.return_value = FROZEN_NOW
        assert _get_future_date(0) == FROZEN_NOW

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    @pytest.mark.parametrize(
        ("days", "expected_dt"),
        [
            (1, dt.datetime(2026, 4, 10, 14, 30, 45)),
            (22, dt.datetime(2026, 5, 1, 14, 30, 45)),
            (365, dt.datetime(2027, 4, 9, 14, 30, 45)),
        ],
    )
    def test_get_future_date_various_days(self, mock_dt, days, expected_dt):
        mock_dt.now.return_value = FROZEN_NOW
        assert _get_future_date(days) == expected_dt

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_past_future_symmetry_with_negative_days(self, mock_dt):
        mock_dt.now.return_value = FROZEN_NOW
        assert _get_past_date(-10) == _get_future_date(10)
        assert _get_future_date(-10) == _get_past_date(10)

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_leap_year_rollover(self, mock_dt):
        mock_dt.now.return_value = dt.datetime(2024, 3, 1, 12, 0, 0)
        assert _get_past_date(1) == dt.datetime(2024, 2, 29, 12, 0, 0)

        mock_dt.now.return_value = dt.datetime(2024, 2, 28, 12, 0, 0)
        assert _get_future_date(1) == dt.datetime(2024, 2, 29, 12, 0, 0)


class TestPrettyDates:
    """Tests for get_pretty_date, get_past_pretty_date, and get_future_pretty_date."""

    def test_get_pretty_date_format_unmocked(self):
        result = get_pretty_date()
        assert isinstance(result, str)
        assert re.match(r"^[A-Z][a-z]+, [A-Z][a-z]+ \d{1,2}, \d{4}$", result)

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_get_pretty_date_mocked(self, mock_dt):
        mock_dt.now.return_value = FROZEN_NOW
        assert get_pretty_date() == "Thursday, April 09, 2026"

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_get_past_pretty_date_zero_days(self, mock_dt):
        mock_dt.now.return_value = FROZEN_NOW
        assert get_past_pretty_date(0) == get_pretty_date()

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    @pytest.mark.parametrize(
        ("days", "expected"),
        [
            (1, "Wednesday, April 08, 2026"),
            (7, "Thursday, April 02, 2026"),
            (9, "Tuesday, March 31, 2026"),
            (100, "Tuesday, December 30, 2025"),
        ],
    )
    def test_get_past_pretty_date_mocked(self, mock_dt, days, expected):
        mock_dt.now.return_value = FROZEN_NOW
        assert get_past_pretty_date(days) == expected

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_get_future_pretty_date_zero_days(self, mock_dt):
        mock_dt.now.return_value = FROZEN_NOW
        assert get_future_pretty_date(0) == get_pretty_date()

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    @pytest.mark.parametrize(
        ("days", "expected"),
        [
            (1, "Friday, April 10, 2026"),
            (7, "Thursday, April 16, 2026"),
            (22, "Friday, May 01, 2026"),
            (365, "Friday, April 09, 2027"),
        ],
    )
    def test_get_future_pretty_date_mocked(self, mock_dt, days, expected):
        mock_dt.now.return_value = FROZEN_NOW
        assert get_future_pretty_date(days) == expected

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_pretty_dates_negative_symmetry(self, mock_dt):
        mock_dt.now.return_value = FROZEN_NOW
        assert get_past_pretty_date(-7) == get_future_pretty_date(7)
        assert get_future_pretty_date(-7) == get_past_pretty_date(7)


class TestHyphenatedDates:
    """Tests for dd-mm-yyyy and mm-dd-yyyy formats."""

    def test_dd_mm_yyyy_format_unmocked(self):
        result = dd_mm_yyyy()
        assert isinstance(result, str)
        assert re.match(r"^\d{2}-\d{2}-\d{4}$", result)

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_dd_mm_yyyy_mocked(self, mock_dt):
        mock_dt.now.return_value = FROZEN_NOW
        assert dd_mm_yyyy() == "09-04-2026"

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_past_dd_mm_yyyy_zero_days(self, mock_dt):
        mock_dt.now.return_value = FROZEN_NOW
        assert past_dd_mm_yyyy(0) == dd_mm_yyyy()

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    @pytest.mark.parametrize(
        ("days", "expected"),
        [
            (1, "08-04-2026"),
            (9, "31-03-2026"),
            (100, "30-12-2025"),
        ],
    )
    def test_past_dd_mm_yyyy_mocked(self, mock_dt, days, expected):
        mock_dt.now.return_value = FROZEN_NOW
        assert past_dd_mm_yyyy(days) == expected

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_future_dd_mm_yyyy_zero_days(self, mock_dt):
        mock_dt.now.return_value = FROZEN_NOW
        assert future_dd_mm_yyyy(0) == dd_mm_yyyy()

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    @pytest.mark.parametrize(
        ("days", "expected"),
        [
            (1, "10-04-2026"),
            (22, "01-05-2026"),
            (365, "09-04-2027"),
        ],
    )
    def test_future_dd_mm_yyyy_mocked(self, mock_dt, days, expected):
        mock_dt.now.return_value = FROZEN_NOW
        assert future_dd_mm_yyyy(days) == expected

    def test_mm_dd_yyyy_format_unmocked(self):
        result = mm_dd_yyyy()
        assert isinstance(result, str)
        assert re.match(r"^\d{2}-\d{2}-\d{4}$", result)

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_mm_dd_yyyy_mocked(self, mock_dt):
        mock_dt.now.return_value = FROZEN_NOW
        assert mm_dd_yyyy() == "04-09-2026"

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_past_mm_dd_yyyy_zero_days(self, mock_dt):
        mock_dt.now.return_value = FROZEN_NOW
        assert past_mm_dd_yyyy(0) == mm_dd_yyyy()

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    @pytest.mark.parametrize(
        ("days", "expected"),
        [
            (1, "04-08-2026"),
            (9, "03-31-2026"),
            (100, "12-30-2025"),
        ],
    )
    def test_past_mm_dd_yyyy_mocked(self, mock_dt, days, expected):
        mock_dt.now.return_value = FROZEN_NOW
        assert past_mm_dd_yyyy(days) == expected

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_future_mm_dd_yyyy_zero_days(self, mock_dt):
        mock_dt.now.return_value = FROZEN_NOW
        assert future_mm_dd_yyyy(0) == mm_dd_yyyy()

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    @pytest.mark.parametrize(
        ("days", "expected"),
        [
            (1, "04-10-2026"),
            (22, "05-01-2026"),
            (365, "04-09-2027"),
        ],
    )
    def test_future_mm_dd_yyyy_mocked(self, mock_dt, days, expected):
        mock_dt.now.return_value = FROZEN_NOW
        assert future_mm_dd_yyyy(days) == expected

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_hyphenated_order_difference(self, mock_dt):
        mock_dt.now.return_value = FROZEN_NOW
        d_m_y = dd_mm_yyyy()
        m_d_y = mm_dd_yyyy()
        assert d_m_y == "09-04-2026"
        assert m_d_y == "04-09-2026"
        assert d_m_y != m_d_y

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_hyphenated_negative_symmetry(self, mock_dt):
        mock_dt.now.return_value = FROZEN_NOW
        assert past_dd_mm_yyyy(-7) == future_dd_mm_yyyy(7)
        assert future_dd_mm_yyyy(-7) == past_dd_mm_yyyy(7)
        assert past_mm_dd_yyyy(-7) == future_mm_dd_yyyy(7)
        assert future_mm_dd_yyyy(-7) == past_mm_dd_yyyy(7)


class TestSlashedDates:
    """Tests for dd/mm/yyyy and mm/dd/yyyy formats."""

    def test_slash_dd_mm_yyyy_format_unmocked(self):
        result = slash_dd_mm_yyyy()
        assert isinstance(result, str)
        assert re.match(r"^\d{2}/\d{2}/\d{4}$", result)

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_slash_dd_mm_yyyy_mocked(self, mock_dt):
        mock_dt.now.return_value = FROZEN_NOW
        assert slash_dd_mm_yyyy() == "09/04/2026"

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_past_slash_dd_mm_yyyy_zero_days(self, mock_dt):
        mock_dt.now.return_value = FROZEN_NOW
        assert past_slash_dd_mm_yyyy(0) == slash_dd_mm_yyyy()

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    @pytest.mark.parametrize(
        ("days", "expected"),
        [
            (1, "08/04/2026"),
            (9, "31/03/2026"),
            (100, "30/12/2025"),
        ],
    )
    def test_past_slash_dd_mm_yyyy_mocked(self, mock_dt, days, expected):
        mock_dt.now.return_value = FROZEN_NOW
        assert past_slash_dd_mm_yyyy(days) == expected

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_future_slash_dd_mm_yyyy_zero_days(self, mock_dt):
        mock_dt.now.return_value = FROZEN_NOW
        assert future_slash_dd_mm_yyyy(0) == slash_dd_mm_yyyy()

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    @pytest.mark.parametrize(
        ("days", "expected"),
        [
            (1, "10/04/2026"),
            (22, "01/05/2026"),
            (365, "09/04/2027"),
        ],
    )
    def test_future_slash_dd_mm_yyyy_mocked(self, mock_dt, days, expected):
        mock_dt.now.return_value = FROZEN_NOW
        assert future_slash_dd_mm_yyyy(days) == expected

    def test_slash_mm_dd_yyyy_format_unmocked(self):
        result = slash_mm_dd_yyyy()
        assert isinstance(result, str)
        assert re.match(r"^\d{2}/\d{2}/\d{4}$", result)

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_slash_mm_dd_yyyy_mocked(self, mock_dt):
        mock_dt.now.return_value = FROZEN_NOW
        assert slash_mm_dd_yyyy() == "04/09/2026"

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_past_slash_mm_dd_yyyy_zero_days(self, mock_dt):
        mock_dt.now.return_value = FROZEN_NOW
        assert past_slash_mm_dd_yyyy(0) == slash_mm_dd_yyyy()

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    @pytest.mark.parametrize(
        ("days", "expected"),
        [
            (1, "04/08/2026"),
            (9, "03/31/2026"),
            (100, "12/30/2025"),
        ],
    )
    def test_past_slash_mm_dd_yyyy_mocked(self, mock_dt, days, expected):
        mock_dt.now.return_value = FROZEN_NOW
        assert past_slash_mm_dd_yyyy(days) == expected

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_future_slash_mm_dd_yyyy_zero_days(self, mock_dt):
        mock_dt.now.return_value = FROZEN_NOW
        assert future_slash_mm_dd_yyyy(0) == slash_mm_dd_yyyy()

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    @pytest.mark.parametrize(
        ("days", "expected"),
        [
            (1, "04/10/2026"),
            (22, "05/01/2026"),
            (365, "04/09/2027"),
        ],
    )
    def test_future_slash_mm_dd_yyyy_mocked(self, mock_dt, days, expected):
        mock_dt.now.return_value = FROZEN_NOW
        assert future_slash_mm_dd_yyyy(days) == expected

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_slashed_order_difference(self, mock_dt):
        mock_dt.now.return_value = FROZEN_NOW
        d_m_y = slash_dd_mm_yyyy()
        m_d_y = slash_mm_dd_yyyy()
        assert d_m_y == "09/04/2026"
        assert m_d_y == "04/09/2026"
        assert d_m_y != m_d_y

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_slashed_negative_symmetry(self, mock_dt):
        mock_dt.now.return_value = FROZEN_NOW
        assert past_slash_dd_mm_yyyy(-7) == future_slash_dd_mm_yyyy(7)
        assert future_slash_dd_mm_yyyy(-7) == past_slash_dd_mm_yyyy(7)
        assert past_slash_mm_dd_yyyy(-7) == future_slash_mm_dd_yyyy(7)
        assert future_slash_mm_dd_yyyy(-7) == past_slash_mm_dd_yyyy(7)


class TestISO8601Dates:
    """Tests for iso_8601, past_iso_8601, and future_iso_8601 UTC formats."""

    def test_iso_8601_format_unmocked(self):
        result = iso_8601()
        assert isinstance(result, str)
        assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", result)

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_iso_8601_mocked(self, mock_dt):
        mock_dt.now.return_value = FROZEN_UTC_NOW
        result = iso_8601()
        assert result == "2026-04-09T14:30:45Z"
        mock_dt.now.assert_called_with(timezone.utc)

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_past_iso_8601_zero_days(self, mock_dt):
        mock_dt.now.return_value = FROZEN_UTC_NOW
        assert past_iso_8601(0) == "2026-04-09T14:30:45Z"

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    @pytest.mark.parametrize(
        ("days", "expected"),
        [
            (1, "2026-04-08T14:30:45Z"),
            (7, "2026-04-02T14:30:45Z"),
            (9, "2026-03-31T14:30:45Z"),
            (100, "2025-12-30T14:30:45Z"),
        ],
    )
    def test_past_iso_8601_mocked(self, mock_dt, days, expected):
        mock_dt.now.return_value = FROZEN_UTC_NOW
        assert past_iso_8601(days) == expected

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_future_iso_8601_zero_days(self, mock_dt):
        mock_dt.now.return_value = FROZEN_UTC_NOW
        assert future_iso_8601(0) == "2026-04-09T14:30:45Z"

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    @pytest.mark.parametrize(
        ("days", "expected"),
        [
            (1, "2026-04-10T14:30:45Z"),
            (7, "2026-04-16T14:30:45Z"),
            (22, "2026-05-01T14:30:45Z"),
            (365, "2027-04-09T14:30:45Z"),
        ],
    )
    def test_future_iso_8601_mocked(self, mock_dt, days, expected):
        mock_dt.now.return_value = FROZEN_UTC_NOW
        assert future_iso_8601(days) == expected

    @patch("py_simple_package.src.py_simple.easy_date_formatter.datetime")
    def test_iso_8601_negative_symmetry(self, mock_dt):
        mock_dt.now.return_value = FROZEN_UTC_NOW
        assert past_iso_8601(-7) == future_iso_8601(7)
        assert future_iso_8601(-7) == past_iso_8601(7)


class TestDateFormatterReExports:
    """Tests confirming all easy_date_formatter functions are exported at top-level py_simple."""

    @pytest.mark.parametrize(
        "func_name",
        [
            "list_available_formats",
            "get_pretty_date",
            "get_past_pretty_date",
            "get_future_pretty_date",
            "dd_mm_yyyy",
            "past_dd_mm_yyyy",
            "future_dd_mm_yyyy",
            "mm_dd_yyyy",
            "past_mm_dd_yyyy",
            "future_mm_dd_yyyy",
            "slash_dd_mm_yyyy",
            "past_slash_dd_mm_yyyy",
            "future_slash_dd_mm_yyyy",
            "slash_mm_dd_yyyy",
            "past_slash_mm_dd_yyyy",
            "future_slash_mm_dd_yyyy",
            "iso_8601",
            "past_iso_8601",
            "future_iso_8601",
        ],
    )
    def test_exported_from_py_simple(self, func_name):
        top_level_func = getattr(pkg_root, func_name, None)
        module_func = getattr(easy_date_formatter, func_name, None)
        assert top_level_func is not None
        assert top_level_func is module_func
        assert callable(top_level_func)


class TestInputValidation:
    """Tests verifying behavior on invalid day input types."""

    @pytest.mark.parametrize(
        "func",
        [
            get_past_pretty_date,
            get_future_pretty_date,
            past_dd_mm_yyyy,
            future_dd_mm_yyyy,
            past_mm_dd_yyyy,
            future_mm_dd_yyyy,
            past_slash_dd_mm_yyyy,
            future_slash_dd_mm_yyyy,
            past_slash_mm_dd_yyyy,
            future_slash_mm_dd_yyyy,
            past_iso_8601,
            future_iso_8601,
            _get_past_date,
            _get_future_date,
        ],
    )
    def test_functions_raise_type_error_on_string_argument(self, func):
        with pytest.raises(TypeError):
            func("not_a_number")
