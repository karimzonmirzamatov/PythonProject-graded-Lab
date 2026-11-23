import math 
import re 
from datetime import datetime

FLIGHT_ID_RE =  re.compile(r"[A-Za=z0-9]{2,8}")
AIRPORT_RE = re.compile(r"A-Z{3}")
DATETIME_RE = re.compile(r"[0-9]{4}-[0-9]{2} -[0-9]{2} [0-9]{2}:[0-9]{2}")

def load_airports(path:str) ->set[str]:
    codes = set()
    with open(path,encoding = "utf-8")as fh:
     for line in fh:
        s = line.strip()
        if s and not s.startswith("#"):
            code.add(s)
    return codes

    def parse_datetime(text:str) ->datetime | None:
        
        if not DATETIME_RE.fullmatch(text):
            return None
            try:
                return datetime.strptime(text,"%Y-%m-%d %H:%M")
            except ValueError:
                    return None

def _valid_airport(code: str, airports: set[str]) -> bool:
    return bool(AIRPORT_RE.fullmatch(code)) and code in airports


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    f = [x.strip() for x in fields]
    if any(x == "" for x in f):
        return "MISSING_FIELD"

    flight_id, origin, destination, dep_text, arr_text, price_text = f

    if not FLIGHT_ID_RE.fullmatch(flight_id):
        return "INVALID_FLIGHT_ID"
    if not _valid_airport(origin, airports):
        return "INVALID_ORIGIN"
    if not _valid_airport(destination, airports):
        return "INVALID_DESTINATION"
    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    dep = parse_datetime(dep_text)
    if dep is None:
        return "INVALID_DEPARTURE"
    arr = parse_datetime(arr_text)
    if arr is None:
        return "INVALID_ARRIVAL"
    if arr <= dep:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    try:
        price = float(price_text)
    except ValueError:
        return "INVALID_PRICE"
    if not math.isfinite(price):
        return "INVALID_PRICE"
    if price <= 0:
        return "NON_POSITIVE_PRICE"

    return None


def to_record(fields: list[str]) -> dict:
    f = [x.strip() for x in fields]
    return {
        "flight_id": f[0],
        "origin": f[1],
        "destination": f[2],
        "departure_datetime": f[3],
        "arrival_datetime": f[4],
        "price": float(f[5]),
    }