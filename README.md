# Ariadne

A small utility to find your way through complex JSON objects by providing an example.

When interacting with APIs, you often get back large, deeply-nested JSON responses. Finding the correct path to the specific data you need can feel like navigating a labyrinth. `ariadne` helps by generating simple, robust Python helper functions to access that data, giving you a thread to follow.

## Installation

To install `ariadne`, navigate to the project's root directory (the one containing `pyproject.toml`) and run:

```bash
# It is highly recommended to use a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install in editable mode
pip install -e .
```

## Quick Start

This repository includes an `examples/` directory to get you started.

1.  **`examples/control.json`** contains a sample JSON object:
    ```json
    {
      "user": { "id": 123, "name": "Alice", ... },
      "posts": [ { "id": "post-1", ... }, { "id": "post-2", ... } ]
    }
    ```

2.  **`examples/annotated.json`** is a copy where we've marked the data we want with `__want__:` placeholders:
    ```json
    {
      "user": { "email": "__want__:user_email", ... },
      "posts": [ ..., { "title": "__want__:second_post_title" } ]
    }
    ```

3.  **Run `ariadne`** from your terminal to generate the helper functions and save them to a file:
    ```bash
    ariadne examples/control.json examples/annotated.json -o helpers.py
    ```

4.  **Check the output** in `helpers.py`. You now have ready-to-use Python functions!

## Usage

### Command-Line Usage

The `ariadne` command is the quickest way to generate helper functions.

```bash
# Print helpers to the console
ariadne <control_file.json> <annotated_file.json>

# Save helpers to a specific file
ariadne <control_file.json> <annotated_file.json> --output helpers.py
```

### Library Usage

You can also use `ariadne` programmatically within your own Python scripts.

```python
import json
from ariadne.mapper import map_placeholders, generate_helpers

# 1. Load your JSON data
with open('examples/control.json') as f:
    control_data = json.load(f)
with open('examples/annotated.json') as f:
    annotated_data = json.load(f)

# 2. Find the placeholder mappings
mappings = map_placeholders(control_data, annotated_data)

# 3. Generate the helper code
# You can get it as a string...
code_string = generate_helpers(mappings)
print(code_string)

# ...or save it directly to a file
generate_helpers(mappings, output_file="my_helpers.py")
```

## Example Generated Code

Running `ariadne` on the `examples/` files will produce the following code in `helpers.py`:

```python
from typing import Any, Dict, List, Union

class JSONPathNotFoundError(KeyError):
    """Custom exception raised when a path is not found in the data."""
    pass

def _get_data(data: Union[Dict, List], path: tuple, friendly_name: str) -> Any:
    """Safely access nested data, raising a custom error on failure."""
    for key in path:
        try:
            data = data[key]
        except (KeyError, IndexError, TypeError):
            raise JSONPathNotFoundError(
                f"Could not find '{friendly_name}'. The path {path} was not found in the object."
            )
    return data

def get_second_post_title(obj: Union[Dict, List]) -> Any:
    """Gets data for 'second_post_title' from path: obj['posts'][1]['title']"""
    # JSONPath equivalent: $.posts[1].title
    return _get_data(obj, ('posts', 1, 'title'), 'second_post_title')

def get_sms_enabled(obj: Union[Dict, List]) -> Any:
    """Gets data for 'sms_enabled' from path: obj['user']['prefs']['notifications']['sms']"""
    # JSONPath equivalent: $.user.prefs.notifications.sms
    return _get_data(obj, ('user', 'prefs', 'notifications', 'sms'), 'sms_enabled')

def get_user_email(obj: Union[Dict, List]) -> Any:
    """Gets data for 'user_email' from path: obj['user']['email']"""
    # JSONPath equivalent: $.user.email
    return _get_data(obj, ('user', 'email'), 'user_email')
```
