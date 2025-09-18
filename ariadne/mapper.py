import json
from deepdiff import DeepDiff
from typing import Any, Dict, List, Tuple, Union

Path = Tuple[Union[str, int], ...]
Mappings = Dict[str, Path]

SENTINEL_PREFIX = "__want__:"

def map_placeholders(
    control: Union[Dict, List],
    annotated: Union[Dict, List],
    prefix: str = SENTINEL_PREFIX
) -> Mappings:
    """
    Compare a control and an annotated data structure to find placeholders.

    It identifies values in the 'annotated' structure that start with the
    sentinel prefix and maps them to their corresponding path from the
    original structure.

    Args:
        control: The original, unmodified data structure (e.g., from a real API response).
        annotated: A copy of the control data where target values have been
                   replaced by placeholder strings (e.g., '__want__:my_field').
        prefix: The string prefix used to identify placeholders.

    Returns:
        A dictionary mapping each placeholder tag to its structural path.
        Example: {'__want__:user_id': ('users', 0, 'id')}
    """
    diff = DeepDiff(control, annotated, view='tree')
    mappings: Mappings = {}

    change_types = [
        'values_changed',
        'type_changes',
        'dictionary_item_added',
        'iterable_item_added'
    ]

    def get_value_by_path(data, path):
        for key in path:
            try:
                data = data[key]
            except (KeyError, IndexError, TypeError):
                return None
        return data

    for change_type in change_types:
        for change in diff.get(change_type, []):
            path_list = change.path(output_format='list')

            # Use the path to look up the value in the annotated object.
            # This is more robust than relying on change.t2.
            new_value = get_value_by_path(annotated, path_list)

            if isinstance(new_value, str) and new_value.startswith(prefix):
                mappings[new_value] = tuple(path_list)

    return mappings

def _python_expr_for_path(path: Path, root_name: str = "data") -> str:
    """Generates a Python expression to access data at a given path."""
    expr = root_name
    for part in path:
        if isinstance(part, int):
            expr += f"[{part}]"
        else:
            # Use repr() to handle quotes and special characters in keys
            expr += f"[{repr(part)}]"
    return expr

def _jsonpath_for_path(path: Path) -> str:
    """Generates a JSONPath string for a given path."""
    expr = "$"
    for part in path:
        if isinstance(part, int):
            expr += f"[{part}]"
        elif isinstance(part, str) and part.isidentifier():
            expr += f".{part}"
        else:
            # Use repr() to handle quotes and special characters
            expr += f"[{repr(part)}]"
    return expr

def generate_helpers(
    mappings: Mappings,
    func_prefix: str = "get_",
    output_file: str = None
) -> str:
    """
    Generates a Python script containing helper functions from path mappings.

    This version includes a custom exception for robust error handling and can
    optionally write the output directly to a file.

    Args:
        mappings: A dictionary mapping placeholder tags to their paths.
        func_prefix: The prefix to use for the generated helper functions.
        output_file: Optional. A file path to write the generated code to.

    Returns:
        A string containing the generated Python code.
    """
    code_lines = [
        "from typing import Any, Dict, List, Union",
        "",
        "class JSONPathNotFoundError(KeyError):",
        '    """Custom exception raised when a path is not found in the data."""',
        "    pass",
        "",
        "def _get_data(data: Union[Dict, List], path: tuple, friendly_name: str) -> Any:",
        '    """Safely access nested data, raising a custom error on failure."""',
        "    for key in path:",
        "        try:",
        "            data = data[key]",
        "        except (KeyError, IndexError, TypeError):",
        "            raise JSONPathNotFoundError(",
        "                f\"Could not find '{friendly_name}'. The path {path} was not found in the object.\"",
        "            )",
        "    return data",
        "",
    ]
    for tag, path in sorted(mappings.items()):
        clean_tag = tag.replace(SENTINEL_PREFIX, "", 1)
        func_name = f"{func_prefix}{clean_tag}"
        py_expr_str = _python_expr_for_path(path, "obj")
        jp_expr_str = _jsonpath_for_path(path)

        docstring = f'"""Gets data for \'{clean_tag}\' from path: {py_expr_str}"""'

        func_def = [
            f"def {func_name}(obj: Union[Dict, List]) -> Any:",
            f"    {docstring}",
            f"    # JSONPath equivalent: {jp_expr_str}",
            f"    return _get_data(obj, {path}, '{clean_tag}')",
            "",
        ]
        code_lines.extend(func_def)

    code_string = "\n".join(code_lines)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(code_string)

    return code_string

def generate_code_from_files(control_file: str, annotated_file: str) -> str:
    """
    Loads JSON files and generates helper code.

    Args:
        control_file: Path to the control JSON file.
        annotated_file: Path to the annotated JSON file.

    Returns:
        A string of generated Python code.
    """
    with open(control_file, 'r') as f:
        control_data = json.load(f)

    with open(annotated_file, 'r') as f:
        annotated_data = json.load(f)

    mappings = map_placeholders(control_data, annotated_data)
    return generate_helpers(mappings)
