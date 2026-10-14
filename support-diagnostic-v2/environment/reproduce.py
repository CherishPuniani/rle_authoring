import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


def main():
    workspace = Path(__file__).resolve().parent

    expected = {
        "ticket_count": 2,
        "by_status": {
            "open": 1,
            "closed": 0,
            "pending": 1,
        },
    }

    with TemporaryDirectory() as directory:
        output = Path(directory) / "public"

        process = subprocess.run(
            [
                sys.executable,
                str(workspace / "ticket_report.py"),
                "--input",
                str(workspace / "data" / "tickets.json"),
                "--output",
                str(output),
            ],
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if process.returncode != 0:
            print(process.stderr, file=sys.stderr)
            return 1

        actual = json.loads((output / "report.json").read_text())

    print("Actual:", json.dumps(actual))
    print("Expected:", json.dumps(expected))

    if actual != expected:
        subprocess.run(
            [sys.executable, "/usr/local/lib/report-diagnostic.py"],
            check=True,
            timeout=10,
        )
        return 1

    print("Sample report is correct")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())