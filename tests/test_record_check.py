import importlib.util, pathlib

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
    root = _repo(tmp_path, **{"nota.md": "Fundada en 2011 [desconocido:]\n"})
    errors, _ = record_check.check(root, inferred="inferido", unknown="desconocido")
    assert any("empty question" in e for e in errors)
