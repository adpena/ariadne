import pytest
import subprocess
from pathlib import Path

# Define paths to the fixture files
FIXTURE_DIR = Path(__file__).parent / "fixtures"
CONTROL_JSON_PATH = str(FIXTURE_DIR / "actblue_control.json")
ANNOTATED_JSON_PATH = str(FIXTURE_DIR / "actblue_annotated.json")

def test_cli_prints_to_stdout(capsys):
    """
    Tests that the CLI prints to stdout by default.
    """
    # The 'ariadne' command is installed as a script via pyproject.toml
    result = subprocess.run(
        ["ariadne", CONTROL_JSON_PATH, ANNOTATED_JSON_PATH],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "def get_contribution_id(obj: Union[Dict, List]) -> Any:" in result.stdout
    assert "def get_ip_address(obj: Union[Dict, List]) -> Any:" in result.stdout

def test_cli_writes_to_output_file(tmp_path):
    """
    Tests that the CLI writes to a file when the --output flag is used.
    """
    output_file = tmp_path / "helpers.py"

    result = subprocess.run(
        ["ariadne", CONTROL_JSON_PATH, ANNOTATED_JSON_PATH, "--output", str(output_file)],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert output_file.exists()

    content = output_file.read_text()
    assert "def get_contribution_id(obj: Union[Dict, List]) -> Any:" in content
    assert "def get_ip_address(obj: Union[Dict, List]) -> Any:" in content

    # Check that the confirmation message is printed to stdout
    assert f"Successfully wrote helpers to {output_file}" in result.stdout
