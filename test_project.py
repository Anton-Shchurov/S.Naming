"""
Unit tests for url_connect, create_phase_stage_name and field_generator.

All network calls are mocked – the Excel file is created in memory,
so no tokens, passwords or corporate links are required.
"""
import pytest
import pandas as pd
from io import BytesIO
import requests

# --- Prepare mock data -------------------------------------------------------

# Demonstration table that will be "downloaded"
DATA = {
    "Project Name": ["Project1", "Project1", "Project2"],
    "Short Name":   ["P1", "P1", "P2"],
    "Phase":        ["1.0", "2.0", "3.0"],
    "Stage":        ["1", "2", "3"],
    "Building":     ["B1", "B2", "B3"],
}
DF_DEMO = pd.DataFrame(DATA)

def make_excel_bytes(df: pd.DataFrame, sheet_name: str = "Summary Table") -> bytes:
    """Serialize a DataFrame to an in‑memory Excel file and return its bytes."""
    buffer = BytesIO()
    df.to_excel(buffer, index=False, sheet_name=sheet_name)
    buffer.seek(0)
    return buffer.read()

EXCEL_BYTES = make_excel_bytes(DF_DEMO)

# --- Mock requests.get -------------------------------------------------------

def mock_requests_get(url, *args, **kwargs):
    """Return a Response containing the Excel bytes, ignoring the actual URL."""
    response = requests.Response()
    response.status_code = 200
    response._content = EXCEL_BYTES
    return response

# Patch the method in the requests library
requests.get = mock_requests_get

# --- Import the functions under test ----------------------------------------
# Import occurs *after* mocking so that url_connect uses the patched version.
import constants as ct
import project

from project import url_connect, create_phase_stage_name, field_generator

# Provide a dummy URL so the function signature is satisfied
ct.URL = "https://example.com/demo.xlsx"

# --- Tests -------------------------------------------------------------------

def test_url_connect():
    df = url_connect(ct.URL)
    assert isinstance(df, pd.DataFrame)
    assert df.equals(DF_DEMO)        # must match the mock table exactly
    assert list(df.columns) == list(DF_DEMO.columns)

def test_create_phase_stage_name():
    assert create_phase_stage_name("1.0", ["1", "2"]) == ["1.1", "1.2"]
    assert create_phase_stage_name("nan", ["1", "2"])  == "00"
    assert create_phase_stage_name("1.0", ["nan", "-"]) == ["1"]

@pytest.mark.parametrize(
    "inp, expected",
    [
        (["1.1", "1.3", "1.5"],                     "1.1#1.3#1.5"),
        (["1", "2", "3", "4", "5"],                 "1-5"),
        (["1.1", "1.2", "1.3", "1.4", "1.5"],       "1.1-1.5"),
        (["1.1", "1.2"],                            "1.1#1.2"),
        (["1", "2", "5"],                           "1#2#5"),
        (
            [
                "1.1", "1.2", "1.3", "1.5", "2", "3",
                "4", "5.1", "5.2", "5.3", "6", "7", "8", "9", "12",
            ],
            "1.1-1.3#1.5#2-4#5.1-5.3#6-9#12",
        ),
        (["3.1 Паркинг", "3.2 Паркинг", "5.5", "6.6"],
            "5.5#6.6#3.1 Паркинг#3.2 Паркинг",
        ),
        (["1.1", "2.2", "3.3", "1.1 Паркинг", "1.2 Паркинг"],
            "1.1#2.2#3.3#1.1 Паркинг#1.2 Паркинг",
        ),
    ],
)
def test_field_generator(inp, expected):
    assert field_generator(inp) == expected
