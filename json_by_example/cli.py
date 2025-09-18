import argparse
from .mapper import generate_code_from_files

def main():
    """
    Command-line interface for the JSON by Example tool.
    """
    parser = argparse.ArgumentParser(
        description="Generate Python helper functions to access data in a JSON object.",
        epilog="""
        Example Usage:
        jxbe control.json annotated.json > helpers.py
        """
    )
    parser.add_argument(
        "control_file",
        help="Path to the control JSON file (the original response)."
    )
    parser.add_argument(
        "annotated_file",
        help="Path to the annotated JSON file (with '__want__:' placeholders)."
    )

    args = parser.parse_args()

    try:
        generated_code = generate_code_from_files(
            args.control_file,
            args.annotated_file
        )
        print(generated_code)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
