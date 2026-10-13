import json
import shlex
from pathlib import Path


def grade_remote_workspace(sandbox, remote_workspace, evidence):
    project = Path(__file__).resolve().parent
    verifier_source = project / "support-issue" / "environment"
    remote_verifier = "/tmp/rle-verifier"
    remote_output = "/tmp/rle-evaluation"

    setup = sandbox.process.exec(
        f"test ! -e {remote_verifier} && "
        f"test ! -e {remote_output} && "
        f"mkdir -p {remote_verifier}",
        timeout=10,
    )
    if setup.exit_code != 0:
        raise RuntimeError("Could not prepare remote grading")

    for filename in (
        "grade.py",
        "test_ticket_report.py",
        "observe_public.py",
    ):
        sandbox.fs.upload_file(
            (verifier_source / filename).read_bytes(),
            f"{remote_verifier}/{filename}",
        )

    response = sandbox.process.exec(
        "python3 grade.py"
        f" --workspace {shlex.quote(remote_workspace)}"
        f" --output {shlex.quote(remote_output)}",
        cwd=remote_verifier,
        timeout=60,
    )

    (evidence / "grading-execution.json").write_text(
        json.dumps(
            {
                "exit_code": response.exit_code,
                "output": response.result,
            },
            indent=2,
        ) + "\n"
    )

    if response.exit_code != 0:
        raise RuntimeError("Remote grader failed to produce results")

    result_bytes = sandbox.fs.download_file(
        f"{remote_output}/result.json"
    )
    reward_bytes = sandbox.fs.download_file(
        f"{remote_output}/reward.txt"
    )
    (evidence / "result.json").write_bytes(result_bytes)
    (evidence / "reward.txt").write_bytes(reward_bytes)

    if reward_bytes not in (b"0", b"1"):
        raise ValueError("Remote reward must be exactly 0 or 1")

    return json.loads(result_bytes), int(reward_bytes)
