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
    expected_placeholders = find_all_placeholders(annotated_data)
    assert len(mappings) == len(expected_placeholders)
    assert mappings["__want__:contribution_id"] == ('contribution', 'id')

def test_generate_helpers_structure(control_data, annotated_data):
    """
    Tests the new structure of the generated Python helper functions.
    """
    mappings = map_placeholders(control_data, annotated_data)
    helpers_code = generate_helpers(mappings)

    assert "class JSONPathNotFoundError(KeyError):" in helpers_code
    assert "def _get_data(data: Union[Dict, List], path: tuple, friendly_name: str) -> Any:" in helpers_code
    assert "raise JSONPathNotFoundError(" in helpers_code
    assert "return _get_data(obj, ('contribution', 'id'), 'contribution_id')" in helpers_code

def test_generated_helpers_raise_exception(control_data, annotated_data):
    """
    Tests that the generated helpers correctly raise JSONPathNotFoundError.
    """
    mappings = map_placeholders(control_data, annotated_data)
    helpers_code = generate_helpers(mappings)

    # Execute the generated code to define the functions in a local scope.
    # Using the same dict for globals and locals ensures the functions can find each other.
    local_scope = {}
    exec(helpers_code, local_scope)

    # Get the generated exception and a helper function from the scope
    JSONPathNotFoundError = local_scope['JSONPathNotFoundError']
    get_contribution_id = local_scope['get_contribution_id']

    # Test that calling the function with invalid data raises the custom exception
    with pytest.raises(JSONPathNotFoundError, match="Could not find 'contribution_id'"):
        get_contribution_id({})

def test_generate_helpers_writes_to_file(tmp_path, control_data, annotated_data):
    """
    Tests that generate_helpers writes to a file when the output_file arg is used.
    """
    output_file = tmp_path / "helpers.py"
    mappings = map_placeholders(control_data, annotated_data)

    # Call the function with the output_file argument
    generate_helpers(mappings, output_file=str(output_file))

    assert output_file.exists()
    content = output_file.read_text()
    assert "class JSONPathNotFoundError(KeyError):" in content
    assert "def get_ip_address(obj: Union[Dict, List]) -> Any:" in content
