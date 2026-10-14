import json
import os
from pathlib import Path
import subprocess
import sys

from test_ticket_report import execution_options


def main():
    if os.geteuid() != 0:
        raise RuntimeError("Permission probe requires a root supervisor")

    if not os.environ.get("RLE_EXECUTION_USER"):
        raise RuntimeError("Restricted execution user is not configured")

    options = execution_options()

    code = """
import json
import os
from pathlib import Path

blocked = {}

for directory in ("/tests", "/grading", "/logs/verifier"):
    path = Path(directory) / ".permission-probe"

    try:
        path.write_text("unauthorized write")
    except PermissionError:
        blocked[directory] = True
    else:
        blocked[directory] = False

print(json.dumps({
    "uid": os.geteuid(),
    "gid": os.getegid(),
    "groups": os.getgroups(),
    "blocked": blocked,
}))
"""

    process = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
        **options,
    )

    result = json.loads(process.stdout)

    Path("/logs/verifier/permissions.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )

    assert result["uid"] == options["user"]
    assert result["gid"] == options["group"]
    assert result["groups"] == []
    assert all(result["blocked"].values()), result

    print("PASS: restricted process cannot write protected directories")


if __name__ == "__main__":
    main()