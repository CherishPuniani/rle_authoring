import os
from pathlib import Path

from daytona import Daytona
from dotenv import load_dotenv


def main():
    load_dotenv(Path(__file__).resolve().parent / ".env")

    if not os.environ.get("DAYTONA_API_KEY"):
        raise RuntimeError("DAYTONA_API_KEY is not configured")

    daytona = Daytona()
    sandbox = daytona.create()

    print(f"Created sandbox: {sandbox.id}")

    try:
        response = sandbox.process.exec(
            "python3 -c 'print(2 + 3)'",
            timeout=10,
        )

        if response.exit_code != 0:
            raise RuntimeError("Sandbox command failed")

        if response.result.strip() != "5":
            raise RuntimeError("Sandbox returned an unexpected result")

        print("PASS: remote Python execution returned 5")
    finally:
        daytona.delete(sandbox, wait=True)
        print("Sandbox deleted")


if __name__ == "__main__":
    main()