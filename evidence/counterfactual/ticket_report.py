"""Generate a client-facing snapshot from support ticket events."""
import argparse
import json
from pathlib import Path


def summarize(events):
    # Deduplicate: for each ticket_id, keep the event with highest revision.
    # If revisions tie, keep the later one (higher index in original list).
    latest = {}
    for idx, event in enumerate(events):
        tid = event["ticket_id"]
        rev = event["revision"]
        if tid not in latest:
            latest[tid] = (rev, idx, event)
        else:
            cur_rev, cur_idx, _ = latest[tid]
            if rev > cur_rev or (rev == cur_rev and idx > cur_idx):
                latest[tid] = (rev, idx, event)
    selected_events = [v[2] for v in latest.values()]
    
    counts = {"open": 0, "closed": 0, "pending": 0}
    for event in selected_events:
        counts[event["status"]] += 1
    
    return {
        "ticket_count": len(selected_events),
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
