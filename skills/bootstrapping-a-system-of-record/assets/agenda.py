#!/usr/bin/env python3
# The agenda of a system-of-record repo, from its obligations register.
#
#   python3 scripts/agenda.py               # overdue, then what closes in 45 days
#   python3 scripts/agenda.py --within 90   # look further ahead
#   python3 scripts/agenda.py --check       # validate the register only
#
# Exit 1 when the register is malformed or something is overdue, so a hook or a
# CI job can use it. Exit 0 otherwise, including when nothing is due.
#
# The register is the Markdown table in obligations.md, so a person can read and
# edit it without tooling and this script needs nothing beyond Python 3.
#
# What it does not cover, so nobody reads a quiet agenda as more than it is:
#   - It reads one file. A date written anywhere else in the record is invisible
#     here; the register exists so that dates are written nowhere else.
#   - It reaches nobody. It runs when someone runs it. An agenda nobody opens is
#     a date nobody reads.
#   - It trusts `done`. A row marked done with a wrong path is off the agenda.
import argparse, datetime as dt, pathlib, re, sys

COLUMNS = ("id", "what", "opens", "closes", "if missed", "explained in", "done")
DATE = re.compile(r"\A\d{4}-\d{2}-\d{2}\Z")


def _cells(line):
    """The cells of one Markdown table row. A `\\|` is a literal pipe."""
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", body)]


def load(path):
    """(rows, errors). Each row is a dict keyed by COLUMNS, plus its line number."""
    lines = path.read_text(encoding="utf-8").splitlines()
    header_at = None
    for i, line in enumerate(lines):
        if line.lstrip().startswith("|") and [c.lower() for c in _cells(line)] == list(COLUMNS):
            header_at = i
            break
    if header_at is None:
        return [], [f"{path.name}: no table with the columns {' | '.join(COLUMNS)}"]

    rows, errors = [], []
    for n, line in enumerate(lines[header_at + 2:], start=header_at + 3):
        if not line.lstrip().startswith("|"):
            break
        cells = _cells(line)
        if len(cells) != len(COLUMNS):
            errors.append(f"line {n}: {len(cells)} cells, expected {len(COLUMNS)}")
            continue
        row = dict(zip(COLUMNS, cells))
        row["line"] = n
        rows.append(row)
    return rows, errors


def check(rows):
    """Every problem in the rows, as strings. Empty means valid."""
    errors, seen = [], set()
    for r in rows:
        where = f"line {r['line']} ({r['id'] or '?'})"
        if not r["id"]:
            errors.append(f"{where}: empty id")
        elif r["id"] in seen:
            errors.append(f"{where}: duplicate id")
        seen.add(r["id"])
        if not r["what"]:
            errors.append(f"{where}: empty what")
        dates = {}
        for key in ("opens", "closes"):
            value = r[key]
            if key == "opens" and value in ("", "-"):
                continue
            try:
                if not DATE.match(value):
                    raise ValueError
                dates[key] = dt.date.fromisoformat(value)
            except ValueError:
                errors.append(f"{where}: {key} '{value}' is not a real YYYY-MM-DD date")
        if "opens" in dates and "closes" in dates and dates["opens"] > dates["closes"]:
            errors.append(f"{where}: opens after it closes")
        if not r["if missed"]:
            errors.append(f"{where}: empty 'if missed'")
    return errors


def agenda(rows, today, within):
    """(overdue, upcoming): open rows, each sorted by closing date."""
    horizon = today + dt.timedelta(days=within)
    overdue, upcoming = [], []
    for r in rows:
        if r["done"]:
            continue
        closes = dt.date.fromisoformat(r["closes"])
        if closes < today:
            overdue.append(r)
        elif closes <= horizon:
            upcoming.append(r)
    key = lambda r: r["closes"]
    return sorted(overdue, key=key), sorted(upcoming, key=key)


def _line(r, today):
    days = (dt.date.fromisoformat(r["closes"]) - today).days
    when = (f"{-days} days overdue" if days < 0 else
            "closes today" if days == 0 else
            f"closes in {days} days")
    opens = ""
    if r["opens"] not in ("", "-") and dt.date.fromisoformat(r["opens"]) > today:
        opens = f", opens {r['opens']}"
    return f"  {r['closes']}  {r['what']}  ({when}{opens}; if missed: {r['if missed']})  [{r['id']}]"


def main(argv=None, today=None):
    ap = argparse.ArgumentParser(description="The agenda from a system-of-record's obligations register.")
    ap.add_argument("--register", default="obligations.md")
    ap.add_argument("--within", type=int, default=45, help="days ahead to list (default 45)")
    ap.add_argument("--check", action="store_true", help="validate the register and exit")
    args = ap.parse_args(argv)
    today = today or dt.date.today()

    path = pathlib.Path(args.register)
    if not path.is_file():
        print(f"no register at {path}")
        return 1
    rows, errors = load(path)
    errors += check(rows)
    if errors:
        print(f"{path}: {len(errors)} problem(s)")
        for e in errors:
            print(f"  - {e}")
        return 1
    if args.check:
        print(f"{path}: {len(rows)} row(s), valid")
        return 0

    overdue, upcoming = agenda(rows, today, args.within)
    if overdue:
        print("OVERDUE")
        for r in overdue:
            print(_line(r, today))
    if upcoming:
        print(f"Closing in the next {args.within} days")
        for r in upcoming:
            print(_line(r, today))
    if not overdue and not upcoming:
        print(f"Nothing overdue, nothing closing in the next {args.within} days.")
    return 1 if overdue else 0


if __name__ == "__main__":
    sys.exit(main())
