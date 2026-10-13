import shutil
from pathlib import Path
from uuid import uuid4


project = Path(__file__).resolve().parent
template = project / "environment"

episode = project / "runs" / uuid4().hex
workspace = episode / "workspace"
workspace.mkdir(parents=True)

shutil.copy2(
    project / "instruction.md",
    episode / "instruction.md",
)

shutil.copy2(
    template / "ticket_report.py",
    workspace / "ticket_report.py",
)

for directory in ("data", "internal", "docs"):
    shutil.copytree(
        template / directory,
        workspace / directory,
    )

assert not (workspace / "public").exists()
assert not (workspace / "grading-output").exists()
assert not (workspace / "grade.py").exists()
assert not (workspace / "solution").exists()

print(f"Episode: {episode}")
print(f"Agent workspace: {workspace}")