import importlib.util, pathlib, sys

# The asset has a hyphen in its filename, so it cannot be imported by name.
ASSET = (pathlib.Path(__file__).resolve().parent.parent
         / "skills/bootstrapping-a-system-of-record/assets/record-check.py")
_spec = importlib.util.spec_from_file_location("record_check", ASSET)
record_check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(record_check)

ANCHORED = "# AGENTS.md\n<!-- record:perimeter -->\n<!-- record:routing -->\n"

def _repo(tmp_path, agents=ANCHORED, **files):
    (tmp_path / "AGENTS.md").write_text(agents, encoding="utf-8")
    for name, body in files.items():
        (tmp_path / name).write_text(body, encoding="utf-8")
    return tmp_path

def test_wellformed_unknown_is_worklist_not_error(tmp_path):
    root = _repo(tmp_path, **{"note.md": "Revenue [unknown: what did Q3 close at?]\n"})
    errors, worklist = record_check.check(root)
    assert errors == []
    assert any("what did Q3 close at?" in w for w in worklist)

def test_unknown_without_question_is_an_error(tmp_path):
    root = _repo(tmp_path, **{"note.md": "Revenue [unknown:]\n"})
    errors, _ = record_check.check(root)
    assert any("note.md" in e and "empty question" in e for e in errors)

def test_bare_unknown_token_is_an_error(tmp_path):
    root = _repo(tmp_path, **{"note.md": "Revenue [unknown]\n"})
    errors, _ = record_check.check(root)
    assert any("note.md" in e for e in errors)

def test_inferred_markers_are_listed(tmp_path):
    root = _repo(tmp_path, **{"note.md": "Founded in 2011 [inferred]\n"})
    errors, worklist = record_check.check(root)
    assert errors == []
    assert any("[inferred]" in w for w in worklist)

def test_missing_perimeter_anchor_is_an_error(tmp_path):
    root = _repo(tmp_path, agents="# AGENTS.md\n<!-- record:routing -->\n")
    errors, _ = record_check.check(root)
    assert any("record:perimeter" in e for e in errors)

def test_missing_routing_anchor_is_an_error(tmp_path):
    root = _repo(tmp_path, agents="# AGENTS.md\n<!-- record:perimeter -->\n")
    errors, _ = record_check.check(root)
    assert any("record:routing" in e for e in errors)

def test_custom_marker_words(tmp_path):
    root = _repo(tmp_path, **{"nota.md": (
        "Ingresos [desconocido:]\n"
        "Fundada en 2011 [inferido]\n"
        "Founded in 2011 [inferred], revenue [unknown] and [unknown: how much?]\n"
    )})
    errors, worklist = record_check.check(root, inferred="inferido", unknown="desconocido")
    assert any("nota.md:1" in e and "empty question" in e for e in errors)
    assert any("nota.md:2" in w and "[inferido]" in w for w in worklist)
    # Marker words are per-repo and there are always exactly two. Once a repo
    # declares its own pair, the English defaults are ordinary prose: line 3 is
    # neither an error nor a worklist item.
    assert not any("nota.md:3" in e for e in errors)
    assert not any("nota.md:3" in w for w in worklist)


def test_a_marker_in_the_agents_file_is_not_swept(tmp_path):
    # The agents file is where the two markers are defined, so it matches them.
    # It is read for its anchors and skipped here - otherwise every freshly
    # bootstrapped repo opens its worklist with the template's own definitions.
    root = _repo(tmp_path, agents=ANCHORED + "- `[inferred]` means derived.\n"
                                             "- `[unknown: <question>]` means ask.\n")
    errors, worklist = record_check.check(root)
    assert errors == []
    assert worklist == []


def test_a_non_utf8_source_does_not_raise(tmp_path):
    # A received document need not be UTF-8, and an undecodable byte is not a
    # marker defect. It must never be a traceback in somebody else's repo.
    _repo(tmp_path)
    (tmp_path / "recibo.md").write_bytes("Caf\xe9 [unknown: what did it cost?]\n".encode("latin-1"))
    errors, worklist = record_check.check(tmp_path)
    assert errors == []
    assert any("what did it cost?" in w for w in worklist)


def test_only_markdown_is_scanned(tmp_path):
    # A documented limitation, asserted so it stays a decision rather than a
    # surprise: a marker outside a .md file is invisible to this checker.
    root = _repo(tmp_path)
    (tmp_path / "note.txt").write_text("Revenue [unknown]\n", encoding="utf-8")
    errors, worklist = record_check.check(root)
    assert errors == []
    assert worklist == []


def test_a_missing_agents_file_is_an_error(tmp_path):
    (tmp_path / "note.md").write_text("nothing to see\n", encoding="utf-8")
    errors, _ = record_check.check(tmp_path)
    assert errors == ["AGENTS.md: missing"]


# --- the CLI. check() was covered and main() was not, which is how a --list
# that swallowed every error survived three reviews. ---

def _run(monkeypatch, root, *args):
    monkeypatch.setattr(sys, "argv", ["record-check.py", "--root", str(root), *args])
    return record_check.main()


def test_main_exits_zero_and_says_ok_on_a_clean_repo(tmp_path, capsys, monkeypatch):
    root = _repo(tmp_path, **{"note.md": "Revenue [unknown: what did Q3 close at?]\n"})
    assert _run(monkeypatch, root) == 0
    out = capsys.readouterr().out
    assert "OK - no malformed markers, anchors present (1 open marker(s))" in out
    assert "what did Q3 close at?" in out
    assert "FAIL" not in out


def test_main_exits_one_on_a_malformed_marker(tmp_path, capsys, monkeypatch):
    root = _repo(tmp_path, **{"note.md": "Revenue [unknown]\n"})
    assert _run(monkeypatch, root) == 1
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "note.md:1: [unknown] carries no question" in out


def test_main_exits_one_when_the_agents_file_is_missing(tmp_path, capsys, monkeypatch):
    (tmp_path / "note.md").write_text("ordinary\n", encoding="utf-8")
    assert _run(monkeypatch, tmp_path) == 1
    assert "AGENTS.md: missing" in capsys.readouterr().out


def test_main_list_prints_errors_and_still_exits_zero(tmp_path, capsys, monkeypatch):
    # The regression that matters. --list is what the agents-file template
    # installs as the health check, so it must never exit non-zero - and it must
    # never be the one mode that cannot report a defect.
    root = _repo(tmp_path, **{"note.md": "Revenue [unknown] and [unknown: how much?]\n"})
    assert _run(monkeypatch, root, "--list") == 0
    out = capsys.readouterr().out
    assert "how much?" in out
    assert "FAIL" in out
    assert "note.md:1: [unknown] carries no question" in out


def test_main_list_prints_an_empty_worklist_rather_than_nothing(tmp_path, capsys, monkeypatch):
    root = _repo(tmp_path, **{"note.md": "ordinary\n"})
    assert _run(monkeypatch, root, "--list") == 0
    out = capsys.readouterr().out
    assert "worklist - 0 open marker(s)" in out
    assert "FAIL" not in out


def test_main_honours_the_custom_marker_flags(tmp_path, capsys, monkeypatch):
    root = _repo(tmp_path, **{"nota.md": "Fundada en 2011 [inferido]\n"})
    assert _run(monkeypatch, root, "--inferred-marker", "inferido",
                "--unknown-marker", "desconocido") == 0
    assert "[inferido]" in capsys.readouterr().out


def test_main_honours_a_custom_agents_file(tmp_path, capsys, monkeypatch):
    (tmp_path / "CLAUDE.md").write_text(ANCHORED, encoding="utf-8")
    assert _run(monkeypatch, tmp_path, "--agents-file", "CLAUDE.md") == 0
    assert "anchors present" in capsys.readouterr().out


def test_a_marker_inside_a_code_span_is_not_a_marker(tmp_path):
    # Any repo that documents its own convention writes `[unknown:]` in prose.
    # Counting that is a check firing on a healthy record, which is the one
    # thing this checker must never do.
    root = _repo(tmp_path, **{"doc.md": "Open questions use `[unknown:]` markers.\n"})
    errors, worklist = record_check.check(root)
    assert errors == []
    assert worklist == []


def test_a_marker_inside_a_fenced_block_is_not_a_marker(tmp_path):
    root = _repo(tmp_path, **{"doc.md": "Syntax:\n\n```\n[unknown: <question>]\n[inferred]\n```\n"})
    errors, worklist = record_check.check(root)
    assert errors == []
    assert worklist == []


def test_a_real_marker_beside_a_code_span_still_counts(tmp_path):
    root = _repo(tmp_path, **{"doc.md": "Use `[unknown:]` like this: [unknown: what rate?]\n"})
    errors, worklist = record_check.check(root)
    assert errors == []
    assert any("what rate?" in w for w in worklist)
