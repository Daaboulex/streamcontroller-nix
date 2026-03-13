"""Output formatting utilities for human and JSON modes."""

import json
import sys


class OutputFormatter:
    """Handles output formatting for both human-readable and JSON modes."""

    def __init__(self, json_mode: bool = False):
        self.json_mode = json_mode

    def print_result(self, data, human_formatter=None):
        """Print data in JSON or human-readable format.

        Args:
            data: Dictionary or list to output.
            human_formatter: Optional callable(data) -> str for human output.
        """
        if self.json_mode:
            json.dump(data, sys.stdout, indent=2, default=str)
            sys.stdout.write("\n")
        elif human_formatter:
            print(human_formatter(data))
        else:
            # Default human format: simple key-value
            if isinstance(data, dict):
                for k, v in data.items():
                    print(f"  {k}: {v}")
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            print(f"  {k}: {v}")
                        print()
                    else:
                        print(f"  {item}")

    def print_error(self, message: str, details: dict = None):
        """Print an error message."""
        if self.json_mode:
            err = {"error": message}
            if details:
                err["details"] = details
            json.dump(err, sys.stderr, indent=2, default=str)
            sys.stderr.write("\n")
        else:
            print(f"Error: {message}", file=sys.stderr)
            if details:
                for k, v in details.items():
                    print(f"  {k}: {v}", file=sys.stderr)

    def print_success(self, message: str, data: dict = None):
        """Print a success message."""
        if self.json_mode:
            result = {"status": "ok", "message": message}
            if data:
                result.update(data)
            json.dump(result, sys.stdout, indent=2, default=str)
            sys.stdout.write("\n")
        else:
            print(message)

    def print_table(self, headers: list, rows: list):
        """Print a simple table."""
        if self.json_mode:
            result = []
            for row in rows:
                result.append(dict(zip(headers, row)))
            json.dump(result, sys.stdout, indent=2, default=str)
            sys.stdout.write("\n")
            return

        if not rows:
            print("  (none)")
            return

        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))

        header_line = "  ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
        print(header_line)
        print("  ".join("-" * w for w in col_widths))
        for row in rows:
            line = "  ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
            print(line)
