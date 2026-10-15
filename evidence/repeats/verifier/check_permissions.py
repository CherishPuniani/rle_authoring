import json
import os
from pathlib import Path
import subprocess
import sys

from test_ticket_report import execution_options, run_application


def main():
    if os.geteuid() != 0:
        raise RuntimeError("Permission probe requires a root supervisor")

    if not os.environ.get("RLE_EXECUTION_USER"):
        raise RuntimeError("Restricted execution user is not configured")

    options = execution_options()

    code = """
import json
import os
import resource
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

limits = {name: resource.getrlimit(getattr(resource, name)) for name in ("RLIMIT_CPU", "RLIMIT_FSIZE", "RLIMIT_NOFILE", "RLIMIT_CORE", "RLIMIT_AS", "RLIMIT_NPROC")}
print(json.dumps({
    "limits": limits,
    "uid": os.geteuid(),
    "gid": os.getegid(),
    "groups": os.getgroups(),
    "blocked": blocked,
}))
"""

    process = run_application([sys.executable, "-c", code], "/app")
    process.check_returncode()

    result = json.loads(process.stdout)

    Path("/logs/verifier/permissions.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )

    assert result["limits"]["RLIMIT_CPU"] == [5, 5]
    assert result["limits"]["RLIMIT_FSIZE"] == [2097152, 2097152]
    assert result["limits"]["RLIMIT_NOFILE"] == [64, 64]
    assert result["limits"]["RLIMIT_CORE"] == [0, 0]
    assert result["limits"]["RLIMIT_AS"] == [268435456, 268435456]
    assert result["limits"]["RLIMIT_NPROC"] == [32, 32]
    assert result["uid"] == options["user"]
    assert result["gid"] == options["group"]
    assert result["groups"] == []
    assert all(result["blocked"].values()), result

    print("PASS: restricted process cannot write protected directories")


if __name__ == "__main__":
    main()