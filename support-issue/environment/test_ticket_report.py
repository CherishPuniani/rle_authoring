import json
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
from uuid import uuid4
import os
import pwd


APPLICATION_SCRIPT = Path(__file__).resolve().with_name("ticket_report.py")

def execution_options():
    username = os.environ.get("RLE_EXECUTION_USER")

    if not username:
        return {}

    if os.geteuid() != 0:
        raise RuntimeError(
            "Restricted execution requires a root supervisor"
        )

    account = pwd.getpwnam(username)

    return {
        "user": account.pw_uid,
        "group": account.pw_gid,
        "extra_groups": (),
        "env": {
            "PATH": "/usr/local/bin:/usr/bin:/bin",
            "LANG": "C.UTF-8",
        },
    }


def prepare_workspace(workspace):
    username = os.environ.get("RLE_EXECUTION_USER")

    if username:
        account = pwd.getpwnam(username)
        os.chown(workspace, account.pw_uid, account.pw_gid)

def build_bundle(input_path, output_path, debug=False):
    command = [
        sys.executable,
        str(APPLICATION_SCRIPT),
        "--input",
        str(Path(input_path).resolve()),
        "--output",
        str(Path(output_path).resolve()),
    ]

    if debug:
        command.append("--debug")

    subprocess.run(
        command,
        cwd=APPLICATION_SCRIPT.parent,
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
        **execution_options(),
    )


def summarize(events):
    with TemporaryDirectory() as directory:
        workspace = Path(directory)
        prepare_workspace(workspace)
        input_path = workspace / "tickets.json"
        output_path = workspace / "public"

        input_path.write_text(json.dumps(events))
        build_bundle(input_path, output_path)

        return json.loads((output_path / "report.json").read_text())


def test_higher_revision_wins():
    events = [
        {"ticket_id": "T-100", "revision": 1, "status": "closed"},
        {"ticket_id": "T-100", "revision": 2, "status": "open"},
    ]

    expected = {
        "ticket_count": 1,
        "by_status": {"open": 1, "closed": 0, "pending": 0},
    }

    assert summarize(events) == expected


def test_equal_revision_later_wins():
    events = [
        {"ticket_id": "T-100", "revision": 3, "status": "closed"},
        {"ticket_id": "T-100", "revision": 3, "status": "pending"},
    ]

    expected = {
        "ticket_count": 1,
        "by_status": {"open": 0, "closed": 0, "pending": 1},
    }

    assert summarize(events) == expected

def test_lower_revision_last_does_not_win():
    events = [
        {"ticket_id": "T-100", "revision": 3, "status": "closed"},
        {"ticket_id": "T-100", "revision": 2, "status": "open"},
    ]

    expected = {
        "ticket_count": 1,
        "by_status": {"open": 0, "closed": 1, "pending": 0},
    }

    assert summarize(events) == expected

def test_distinct_tickets_are_preserved():
    events = [
        {"ticket_id": "T-100", "revision": 1, "status": "open"},
        {"ticket_id": "T-101", "revision": 1, "status": "closed"},
        {"ticket_id": "T-102", "revision": 1, "status": "pending"},
    ]

    expected = {
        "ticket_count": 3,
        "by_status": {"open": 1, "closed": 1, "pending": 1},
    }

    assert summarize(events) == expected


def test_empty_input_preserves_schema():
    expected = {
        "ticket_count": 0,
        "by_status": {"open": 0, "closed": 0, "pending": 0},
    }

    assert summarize([]) == expected

def test_build_bundle_preserves_report_and_debug_metadata():
    events = [
        {"ticket_id": "T-100", "revision": 1, "status": "closed"},
        {"ticket_id": "T-100", "revision": 2, "status": "open"},
    ]

    expected_report = {
        "ticket_count": 1,
        "by_status": {"open": 1, "closed": 0, "pending": 0},
    }

    with TemporaryDirectory() as directory:
        workspace = Path(directory)
        prepare_workspace(workspace)
        input_path = workspace / "tickets.json"
        output_path = workspace / "public" / "current"

        input_path.write_text(json.dumps(events))

        build_bundle(input_path, output_path)

        report = json.loads((output_path / "report.json").read_text())
        assert report == expected_report # If false this raises an AssertionError
        assert not (output_path / "debug.json").exists()

        build_bundle(input_path, output_path, debug=True)

        report = json.loads((output_path / "report.json").read_text())
        debug = json.loads((output_path / "debug.json").read_text())

        assert report == expected_report
        assert debug == {"events_processed": 2}

def test_private_notes_are_not_published():
    script = APPLICATION_SCRIPT

    for debug in (False, True):
        with TemporaryDirectory() as directory:
            workspace = Path(directory)
            prepare_workspace(workspace)
            internal = workspace / "internal"
            internal.mkdir()

            canary = f"PRIVATE-NOTE-{uuid4().hex}"
            (internal / "customer_notes.json").write_text(
                json.dumps({"notes": [canary]})
            )

            input_path = workspace / "tickets.json"
            input_path.write_text(
                json.dumps([
                    {
                        "ticket_id": "T-100",
                        "revision": 1,
                        "status": "open",
                    }
                ])
            )

            output_path = workspace / "public" / "current"
            command = [
                sys.executable, # sys.executable points to the Python interpreter running the test
                str(script),
                "--input",
                str(input_path),
                "--output",
                str(output_path),
            ]
            if debug:
                command.append("--debug")

            process = subprocess.run(
                command,
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=10,
                **execution_options(),
            )

            leaked_files = []

            for path in output_path.rglob("*"): # we inspect all files in the output directory
                if path.is_file():
                    contents = path.read_bytes()

                    if canary.encode() in contents:
                        leaked_files.append(str(path.relative_to(output_path)))

            assert not leaked_files, (
                f"Private notes appeared in public files: {leaked_files}"
            )
            assert process.returncode == 0, process.stderr
            assert (output_path / "report.json").is_file()


if __name__ == "__main__":
    test_higher_revision_wins()
    test_equal_revision_later_wins()
    test_lower_revision_last_does_not_win()
    test_distinct_tickets_are_preserved()
    test_empty_input_preserves_schema()
    test_build_bundle_preserves_report_and_debug_metadata()
    test_private_notes_are_not_published()
    print("All 7 tests passed")