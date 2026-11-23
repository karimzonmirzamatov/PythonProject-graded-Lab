from validator import parse_datetime

ALLOWED_KEYS = {
    "flight_id", "origin", "destination", "departure_datetime",
    "arrival_datetime", "price", "min_price", "sort_by", "order", "limit",
}
RECORD_KEYS = {
    "flight_id", "origin", "destination", "departure_datetime",
    "arrival_datetime", "price",
}


def _is_number(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _is_valid_query(q) -> bool:
    if not isinstance(q, dict):
        return False
    if any(k not in ALLOWED_KEYS for k in q):
        return False

    for k in ("flight_id", "origin", "destination"):
        if k in q and not isinstance(q[k], str):
            return False

    for k in ("departure_datetime", "arrival_datetime"):
        if k in q and (not isinstance(q[k], str) or parse_datetime(q[k]) is None):
            return False

    for k in ("price", "min_price"):
        if k in q and not _is_number(q[k]):
            return False

    if "sort_by" in q and (not isinstance(q["sort_by"], str) or q["sort_by"] not in RECORD_KEYS):
        return False

    if "order" in q:
        if "sort_by" not in q or q["order"] not in ("asc", "desc"):
            return False

    if "limit" in q:
        lim = q["limit"]
        if not isinstance(lim, int) or isinstance(lim, bool) or lim < 0:
            return False

    return True


def _matches(rec: dict, q: dict) -> bool:
    for k in ("flight_id", "origin", "destination"):
        if k in q and rec[k] != q[k]:
            return False
    # Datetimes are zero-padded "YYYY-MM-DD HH:MM", so string comparison works.
    if "departure_datetime" in q and rec["departure_datetime"] < q["departure_datetime"]:
        return False
    if "arrival_datetime" in q and rec["arrival_datetime"] > q["arrival_datetime"]:
        return False
    if "price" in q and rec["price"] > q["price"]:
        return False
    if "min_price" in q and rec["price"] < q["min_price"]:
        return False
    return True


def run_query(db: list[dict], query: dict) -> dict:
    if not _is_valid_query(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    matches = [rec for rec in db if _matches(rec, query)]

    if "sort_by" in query:
        reverse = query.get("order", "asc") == "desc"
        matches = sorted(matches, key=lambda r: r[query["sort_by"]], reverse=reverse)

    if "limit" in query:
        matches = matches[: query["limit"]]

    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries) -> list[dict]:
    if isinstance(queries, dict):
        queries = [queries]
    return [run_query(db, q) for q in queries]