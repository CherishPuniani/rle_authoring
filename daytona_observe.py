import json
import shlex
from pathlib import Path


def observe_remote_public(sandbox, remote_workspace, evidence):
    project = Path(__file__).resolve().parent
    observer_source = (
        project
        / "support-issue"
        / "environment"
        / "observe_public.py"
    ).read_text()

    code = (
        "import json\n"
        "namespace = {'__name__': 'remote_observer'}\n"
        f"exec({observer_source!r}, namespace)\n"
        f"result = namespace['observe_public']("
        f"{remote_workspace + '/public/current'!r})\n"
        "print(json.dumps(result))\n"
    )

    response = sandbox.process.exec(
        "python3 -c " + shlex.quote(code),
        timeout=10,
    )

    (evidence / "safety-execution.json").write_text(
        json.dumps(
            {
                "exit_code": response.exit_code,
                "output": response.result,
            },
            indent=2,
        ) + "\n"
    )

    if response.exit_code != 0:
        raise RuntimeError("Remote safety observation failed")

    result = json.loads(response.result)
    (evidence / "safety.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )

    return result