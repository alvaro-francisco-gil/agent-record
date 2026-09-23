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


# --- 1.0.3: the question decides, not the backticks. 1.0.2 erased every marker
# inside a code span, which silenced a repo whose house style is to backtick
# its markers - a checker reporting a clean record on a repo with dozens of
# open questions, the same failure seen from the other side. ---


def test_a_real_question_inside_a_code_span_is_still_a_marker(tmp_path):
    # The 1.0.2 regression. A question written in backticks is an open
    # question; backticks are typography, not quotation.
    root = _repo(tmp_path, **{"note.md": "Cost `[unknown: what did it come to?]`\n"})
    errors, worklist = record_check.check(root)
    assert errors == []
    assert any("what did it come to?" in w for w in worklist)


def test_a_bare_inferred_inside_a_code_span_is_still_a_marker(tmp_path):
    # `[inferred]` is a complete marker on its own, so inside backticks it is
    # still a use. The cost is that a prose mention of it counts too - a
    # worklist line, never an error, and a fenced block is the way to quote it.
    root = _repo(tmp_path, **{"note.md": "Expect EUR 400-900/yr `[inferred]`\n"})
    errors, worklist = record_check.check(root)
    assert errors == []
    assert any("note.md:1" in w for w in worklist)


def test_an_empty_question_inside_a_code_span_is_a_mention_not_an_error(tmp_path):
    # It cannot be a real open question - there is no question in it - so in a
    # code span it is the name of the marker, written in prose about markers.
    root = _repo(tmp_path, **{"doc.md": "Unconfirmed facts carry `[unknown:]`.\n"})
    errors, worklist = record_check.check(root)
    assert errors == []
    assert worklist == []


def test_an_empty_question_outside_a_code_span_is_still_an_error(tmp_path):
    root = _repo(tmp_path, **{"note.md": "Revenue [unknown:]\n"})
    errors, _ = record_check.check(root)
    assert any("empty question" in e for e in errors)


def test_a_placeholder_question_is_a_template_not_a_marker(tmp_path):
    # <question> is the shape the template and every skill doc writes. It is
    # never an open question, wherever it appears.
    root = _repo(tmp_path, **{"doc.md": "Write [unknown: <question>] to ask.\n"})
    errors, worklist = record_check.check(root)
    assert errors == []
    assert worklist == []


def test_a_question_may_wrap_across_lines(tmp_path):
    root = _repo(tmp_path, **{"note.md": "- [unknown: can the ayuntamiento be a\n  beneficiary under this call?]\n"})
    errors, worklist = record_check.check(root)
    assert errors == []
    assert any("note.md:1" in w and "beneficiary under this call?" in w for w in worklist)


def test_a_wrapped_question_is_reported_on_one_line_as_one_marker(tmp_path):
    root = _repo(tmp_path, **{"note.md": "- [unknown: first\n  second]\n"})
    _, worklist = record_check.check(root)
    assert len(worklist) == 1
    assert "\n" not in worklist[0]


def test_an_unterminated_question_is_an_error_not_a_swallowed_document(tmp_path):
    # Without this it matches nothing and disappears, which is the worst of the
    # three outcomes: a malformed marker that reads as a clean record.
    root = _repo(tmp_path, **{"note.md": "Revenue [unknown: what did Q3 close at\n\nNext paragraph.\n"})
    errors, worklist = record_check.check(root)
    assert any("note.md:1" in e and "unterminated" in e for e in errors)
    assert worklist == []


def test_one_word_for_both_markers_reads_the_bare_form_as_inferred(tmp_path):
    # A repo may run a single marker in two forms: bare means unverified, and
    # with a question means here is the question. Declaring the same word twice
    # says so, and the bare form is then a worklist item rather than an error.
    root = _repo(tmp_path, **{"nota.md": (
        'tipo: "[[confirmar]]"\n'
        "El plazo [[confirmar: cierra en junio o en julio?]]\n"
    )})
    errors, worklist = record_check.check(root, inferred="confirmar", unknown="confirmar")
    assert errors == []
    assert any("nota.md:1" in w for w in worklist)
    assert any("cierra en junio o en julio?" in w for w in worklist)


def test_a_hidden_directory_is_not_the_record(tmp_path):
    # Tooling, transcripts and agent scratch live in dot-directories. A record
    # layer never does, and sweeping them buries the real worklist in noise.
    (tmp_path / ".superpowers").mkdir()
    (tmp_path / ".superpowers" / "report.md").write_text(
        "Revenue [unknown: what did Q3 close at?] and [unknown]\n", encoding="utf-8")
    root = _repo(tmp_path)
    errors, worklist = record_check.check(root)
    assert errors == []
    assert worklist == []


def test_every_agents_file_is_skipped_not_only_the_root_one(tmp_path):
    # A nested agents file documents the convention for its subtree, so it
    # matches the markers it defines for exactly the reason the root one does.
    (tmp_path / "project").mkdir()
    (tmp_path / "project" / "AGENTS.md").write_text(
        "Unconfirmed values carry [unknown: <question>] or [inferred].\n", encoding="utf-8")
    root = _repo(tmp_path)
    errors, worklist = record_check.check(root)
    assert errors == []
    assert worklist == []


def test_a_marker_inside_a_fenced_block_is_still_not_a_marker(tmp_path):
    # Fences stay the way to quote the convention, including a real question.
    root = _repo(tmp_path, **{"doc.md": "Syntax:\n\n```\n[unknown: what did Q3 close at?]\n```\n"})
    errors, worklist = record_check.check(root)
    assert errors == []
    assert worklist == []


def test_a_closed_pipe_is_not_a_traceback(tmp_path):
    # `record-check.py --list | head` is how anyone reads a long worklist, and
    # a traceback there reads as a broken tool. Driven end to end because the
    # failure is in the pipe, not in any function.
    import subprocess
    root = _repo(tmp_path, **{"note.md": "".join(
        f"Item {n} [unknown: what is item {n}?]\n" for n in range(5000))})
    reader = subprocess.Popen(["head", "-1"], stdin=subprocess.PIPE,
                              stdout=subprocess.DEVNULL)
    writer = subprocess.Popen([sys.executable, str(ASSET), "--root", str(root), "--list"],
                              stdout=reader.stdin, stderr=subprocess.PIPE)
    reader.stdin.close()
    stderr = writer.communicate()[1].decode()
    reader.wait()
    assert "Traceback" not in stderr, stderr
    assert "BrokenPipeError" not in stderr, stderr


# --- 1.2.0: the record is not always Markdown. An association's accounts keep
# theirs in a beancount ledger and a YAML registry: 534 markers outside .md
# against 44 inside it, so a Markdown-only sweep saw 4% of the record. ---


def test_the_sweep_is_markdown_only_until_the_repo_says_otherwise(tmp_path):
    root = _repo(tmp_path)
    (tmp_path / "libro.beancount").write_text('  justificante: "[unknown: is there a receipt?]"\n', encoding="utf-8")
    errors, worklist = record_check.check(root)
    assert errors == []
    assert worklist == []


def test_a_declared_glob_widens_the_sweep(tmp_path):
    root = _repo(tmp_path)
    (tmp_path / "libro.beancount").write_text('  justificante: "[unknown: is there a receipt?]"\n', encoding="utf-8")
    (tmp_path / "registro.yml").write_text("  alta: [inferred]\n", encoding="utf-8")
    errors, worklist = record_check.check(root, globs=("*.md", "*.beancount", "*.yml"))
    assert errors == []
    assert any("is there a receipt?" in w for w in worklist)
    assert any("registro.yml" in w for w in worklist)


def test_a_file_matching_two_globs_is_swept_once(tmp_path):
    root = _repo(tmp_path, **{"note.md": "Revenue [unknown: what did Q3 close at?]\n"})
    _, worklist = record_check.check(root, globs=("*.md", "note.md"))
    assert len(worklist) == 1


def test_main_honours_repeated_glob_flags(tmp_path, capsys, monkeypatch):
    root = _repo(tmp_path)
    (tmp_path / "libro.beancount").write_text('  ; [unknown: which activity?]\n', encoding="utf-8")
    assert _run(monkeypatch, root, "--glob", "*.md", "--glob", "*.beancount") == 0
    assert "which activity?" in capsys.readouterr().out
