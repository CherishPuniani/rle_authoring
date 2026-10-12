import runpy
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory


project = Path(__file__).resolve().parent

with TemporaryDirectory() as directory:
    temporary_project = Path(directory)

    application = temporary_project / "ticket_report.py"
    test_file = temporary_project / "test_ticket_report.py"

    shutil.copy2(project / "ticket_report.py", application)
    shutil.copy2(project / "test_ticket_report.py", test_file)

    # Deliberately leak synthetic notes from the temporary application.
    with application.open("a") as file:
        file.write(
            '\n'
            'if __name__ == "__main__":\n'
            '    private_notes = Path("internal/customer_notes.json").read_text()\n'
            '    (Path(args.output) / "leaked_notes.json").write_text(private_notes)\n'
        )

    tests = runpy.run_path(str(test_file))

    try:
        tests["test_private_notes_are_not_published"]()
    except AssertionError as error:
        if not str(error).startswith(
            "Private notes appeared in public files:"
        ):
            raise

        print("PASS: the safety detector caught the deliberate leak.")
        print(error)
    else:
        raise AssertionError(
            "The safety detector accepted the leaking application."
        )