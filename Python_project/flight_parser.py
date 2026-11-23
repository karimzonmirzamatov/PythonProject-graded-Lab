import argparse
import datetime as dt
import json
import logging
import os
import sys

from csv_loader import parse_files
from query import run_queries
from validator import load_airports

STUDENT_ID = "251ADB092"   
FIRST_NAME = "Karimboyvachcha"
LAST_NAME = "Mirzamatov"


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Validate flight CSVs and query them.")
    p.add_argument("-i", metavar="FILE", help="parse a single CSV file")
    p.add_argument("-d", metavar="FOLDER", help="parse every .csv file in a folder")
    p.add_argument("-j", metavar="FILE", help="load an existing JSON database")
    p.add_argument("-a", metavar="FILE", help="airport list file")
    p.add_argument("-o", metavar="FILE", help="output database path (default db.json)")
    p.add_argument("-q", metavar="FILE", help="JSON query file")
    p.add_argument("-r", metavar="FOLDER", default=".", help="response folder (default .)")
    return p


def _write_database_and_log(db_path: str, records: list[dict], messages: list[str]) -> None:
    with open(db_path, "w", encoding="utf-8") as fh:
        json.dump(records, fh, indent=2)

    log_path = os.path.join(os.path.dirname(os.path.abspath(db_path)), "errors.log")
    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(handler)
    try:
        for msg in messages:
            logger.warning(msg)
    finally:
        logger.removeHandler(handler)
        handler.close()


def _collect_csv_files(folder: str) -> list[str]:
    if not os.path.isdir(folder):
        raise ValueError(f"folder not found: {folder}")
    names = sorted(
        n for n in os.listdir(folder)
        if n.endswith(".csv") and os.path.isfile(os.path.join(folder, n))
    )
    if not names:
        raise ValueError(f"no .csv files in folder: {folder}")
    return [os.path.join(folder, n) for n in names]


def _load_json(path: str):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main(argv: list[str] | None = None) -> int:
    try:
        args = _build_parser().parse_args(argv)
    except SystemExit as exc:          # -h gives 0, bad arguments give 2
        return exc.code if isinstance(exc.code, int) else 2

    sources = [x for x in (args.i, args.d, args.j) if x is not None]
    if len(sources) != 1:
        print("Error: exactly one of -i, -d, -j is required", file=sys.stderr)
        return 2
    if (args.i or args.d) and not args.a:
        print("Error: -a is required with -i and -d", file=sys.stderr)
        return 2
    if args.j and args.o:
        print("Error: -o cannot be used with -j", file=sys.stderr)
        return 2

    try:
        if args.j:
            db = _load_json(args.j)
            if not isinstance(db, list) or not all(isinstance(r, dict) for r in db):
                raise ValueError("database file must contain a JSON array of objects")
        else:
            airports = load_airports(args.a)
            paths = [args.i] if args.i else _collect_csv_files(args.d)
            db, messages = parse_files(paths, airports)
            db_path = args.o or "db.json"
            _write_database_and_log(db_path, db, messages)
            print(f"Valid flights: {len(db)}, invalid rows: {len(messages)}")

        if args.q:
            queries = _load_json(args.q)
            if not isinstance(queries, (dict, list)):
                raise ValueError("query file must contain an object or an array")
            results = run_queries(db, queries)

            now = dt.datetime.now().strftime("%Y%m%d_%H%M")
            name = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{now}.json"
            with open(os.path.join(args.r, name), "w", encoding="utf-8") as fh:
                json.dump(results, fh, indent=2, ensure_ascii=False)

    except (OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())