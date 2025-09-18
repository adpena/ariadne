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
        jxbe control.json annotated.json
        jxbe control.json annotated.json -o helpers.py
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
    parser.add_argument(
        "-o", "--output",
        help="Path to the output file. If not provided, prints to standard output."
    )

    args = parser.parse_args()

    try:
        generated_code = generate_code_from_files(
            args.control_file,
            args.annotated_file
        )

        if args.output:
            with open(args.output, 'w') as f:
                f.write(generated_code)
            print(f"Successfully wrote helpers to {args.output}")
        else:
            print(generated_code)

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
