import datetime as dt, pathlib, types

# Executed from source, like record-check.py in test_record_check.py: the asset
# has no importable name, and a stale bytecode cache must never be what passes.
ASSET = (pathlib.Path(__file__).resolve().parent.parent
         / "skills/bootstrapping-a-system-of-record/assets/agenda.py")
agenda = types.ModuleType("agenda")
agenda.__file__ = str(ASSET)
exec(compile(ASSET.read_text(encoding="utf-8"), str(ASSET), "exec"), agenda.__dict__)

TEMPLATE = (ASSET.parent / "obligations.md").read_text(encoding="utf-8")
TODAY = dt.date(2027, 3, 10)


def _register(tmp_path, *rows):
    path = tmp_path / "obligations.md"
    path.write_text(TEMPLATE + "".join(r + "\n" for r in rows), encoding="utf-8")
    return path


def _run(path, *args, capsys):
    code = agenda.main(["--register", str(path), *args], today=TODAY)
    return code, capsys.readouterr().out


def test_shipped_template_is_a_valid_empty_register(tmp_path, capsys):
    code, out = _run(_register(tmp_path), capsys=capsys)
    assert code == 0
    assert "Nothing overdue" in out


def test_upcoming_row_is_listed_and_exits_zero(tmp_path, capsys):
    path = _register(tmp_path, "| insurance-2027 | Renew insurance | - | 2027-03-31 | uninsured | - | |")
    code, out = _run(path, capsys=capsys)
    assert code == 0
    assert "Renew insurance" in out and "closes in 21 days" in out


def test_overdue_row_exits_one(tmp_path, capsys):
    path = _register(tmp_path, "| inspection-2027 | Pass the inspection | 2027-01-01 | 2027-03-01 | fine | - | |")
    code, out = _run(path, capsys=capsys)
    assert code == 1
    assert "OVERDUE" in out and "9 days overdue" in out


def test_done_row_is_off_the_agenda(tmp_path, capsys):
    path = _register(tmp_path, "| inspection-2027 | Pass the inspection | - | 2027-03-01 | fine | - | inspections/2027-02-20.md |")
    code, out = _run(path, capsys=capsys)
    assert code == 0
    assert "Pass the inspection" not in out


def test_beyond_the_horizon_is_not_listed_until_widened(tmp_path, capsys):
    path = _register(tmp_path, "| filing-q2 | File the return | - | 2027-07-20 | surcharge | - | |")
    assert "File the return" not in _run(path, capsys=capsys)[1]
    assert "File the return" in _run(path, "--within", "200", capsys=capsys)[1]


def test_bad_date_is_an_error(tmp_path, capsys):
    path = _register(tmp_path, "| x | Something | - | 2027-02-30 | cost | - | |")
    code, out = _run(path, capsys=capsys)
    assert code == 1
    assert "not a real YYYY-MM-DD date" in out


def test_duplicate_id_and_missing_cost_are_errors(tmp_path, capsys):
    path = _register(tmp_path,
                     "| x | One | - | 2027-04-01 | cost | - | |",
                     "| x | Two | - | 2027-04-02 |  | - | |")
    code, out = _run(path, "--check", capsys=capsys)
    assert code == 1
    assert "duplicate id" in out and "empty 'if missed'" in out


def test_opens_after_closes_is_an_error(tmp_path, capsys):
    path = _register(tmp_path, "| x | One | 2027-05-01 | 2027-04-01 | cost | - | |")
    assert "opens after it closes" in _run(path, capsys=capsys)[1]


def test_wrong_cell_count_is_an_error(tmp_path, capsys):
    path = _register(tmp_path, "| x | One | 2027-04-01 | cost |")
    code, out = _run(path, capsys=capsys)
    assert code == 1
    assert "expected 7" in out


def test_escaped_pipe_stays_in_its_cell(tmp_path, capsys):
    path = _register(tmp_path, "| x | Pay A \\| B | - | 2027-03-20 | cost | - | |")
    code, out = _run(path, capsys=capsys)
    assert code == 0
    assert "Pay A | B" in out


def test_missing_table_is_an_error(tmp_path, capsys):
    path = tmp_path / "obligations.md"
    path.write_text("# Obligations\n\nNothing here yet.\n", encoding="utf-8")
    code, out = _run(path, capsys=capsys)
    assert code == 1
    assert "no table" in out


def test_missing_register_is_an_error(tmp_path, capsys):
    code, out = _run(tmp_path / "nope.md", capsys=capsys)
    assert code == 1
