import json
import pytest
from pathlib import Path
from ariadne.mapper import map_placeholders, generate_helpers

# Define the paths to the fixture files
FIXTURE_DIR = Path(__file__).parent / "fixtures"
CONTROL_JSON_PATH = FIXTURE_DIR / "actblue_control.json"
ANNOTATED_JSON_PATH = FIXTURE_DIR / "actblue_annotated.json"

@pytest.fixture
def control_data():
    """Loads the control JSON data."""
    with open(CONTROL_JSON_PATH) as f:
        return json.load(f)

@pytest.fixture
def annotated_data():
    """Loads the annotated JSON data."""
    with open(ANNOTATED_JSON_PATH) as f:
        return json.load(f)

def find_all_placeholders(data, prefix="__want__:"):
    """Helper to find all placeholder strings in a nested structure."""
    placeholders = set()
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, str) and v.startswith(prefix):
                placeholders.add(v)
            else:
                placeholders.update(find_all_placeholders(v, prefix))
    elif isinstance(data, list):
        for item in data:
            placeholders.update(find_all_placeholders(item, prefix))
    return placeholders

def test_map_placeholders(control_data, annotated_data):
    """
    Tests that placeholders are correctly mapped to their paths.
    """
    mappings = map_placeholders(control_data, annotated_data)

    # Check a few key mappings to ensure correctness
    assert mappings["__want__:contribution_id"] == ('contribution', 'id')
    assert mappings["__want__:gross_amount"] == ('contribution', 'amount')
    assert mappings["__want__:donor_email"] == ('contribution', 'donor', 'email')
    assert mappings["__want__:candidate_allocation"] == ('contribution', 'allocations', 0, 'amount')
    assert mappings["__want__:committee_allocation"] == ('contribution', 'allocations', 1, 'amount')
    assert mappings["__want__:ip_address"] == ('contribution', 'metadata', 'device', 'ip')

    # Check the total number of mappings found
    expected_placeholders = find_all_placeholders(annotated_data)
    assert len(mappings) == len(expected_placeholders)

def test_generate_helpers(control_data, annotated_data):
    """
    Tests the generation of Python helper functions.
    """
    mappings = map_placeholders(control_data, annotated_data)
    helpers_code = generate_helpers(mappings)

    # Basic check to ensure the code is a non-empty string
    assert isinstance(helpers_code, str)
    assert len(helpers_code) > 0

    # Check that a few expected function definitions are present
    assert "def get_contribution_id(obj: Union[Dict, List]) -> Any:" in helpers_code
    assert "def get_donor_email(obj: Union[Dict, List]) -> Any:" in helpers_code
    assert "def get_candidate_allocation(obj: Union[Dict, List]) -> Any:" in helpers_code
    assert "def get_ip_address(obj: Union[Dict, List]) -> Any:" in helpers_code

    # Check for the safe accessor and its usage
    assert "def get_data(data: Union[Dict, List], path: tuple, default: Any = None) -> Any:" in helpers_code
    assert "return get_data(obj, ('contribution', 'id'))" in helpers_code

    # Check for a JSONPath comment
    assert "# JSONPath equivalent: $.contribution.donor.email" in helpers_code
