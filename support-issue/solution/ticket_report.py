"""Generate a client-facing snapshot from support ticket events."""
import argparse
import json
from pathlib import Path


def summarize(events):
    latest = {}

    for event in events:
        ticket_id = event["ticket_id"]
        if (
            ticket_id not in latest
            or event["revision"] >= latest[ticket_id]["revision"]
        ):
            latest[ticket_id] = event

    counts = {"open": 0, "closed": 0, "pending": 0}
    for event in latest.values():
        counts[event["status"]] += 1

    return {
        "ticket_count": len(latest),
        "by_status": counts,
    }


def build_bundle(input_path, output_path, debug=False):
    events = json.loads(Path(input_path).read_text())
    output = Path(output_path)
    output.mkdir(parents=True, exist_ok=True)
    (output / "report.json").write_text(json.dumps(summarize(events), indent=2) + "\n")
    if debug:
        (output / "debug.json").write_text(json.dumps({"events_processed": len(events)}) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    build_bundle(args.input, args.output, args.debug)
