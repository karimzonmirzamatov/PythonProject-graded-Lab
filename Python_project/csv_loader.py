import csv
import os

from validator import validate_row, to_record


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    messages: list[str] = []
    seen: set[tuple[str, str]] = set()

    for path in paths:
        name = os.path.basename(path)
        with open(path, encoding="utf-8", newline="") as fh:
            for lineno, line in enumerate(fh, start=1):
                if lineno == 1:          # header line, skip without validating
                    continue
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue

                raw = line.rstrip("\r\n")
                fields = next(csv.reader([raw]))

                reason = validate_row(fields, airports)
                if reason is None:
                    rec = to_record(fields)
                    key = (rec["flight_id"], rec["departure_datetime"])
                    if key not in seen:
                        seen.add(key)
                        records.append(rec)
                        continue
                    reason = "DUPLICATE_FLIGHT"

                messages.append(f"{name}:{lineno}: {reason} | {raw}")

    return records, messages