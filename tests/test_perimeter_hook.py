"""Tests for the generated pre-commit perimeter hook.

The hook is the only shipped asset that guards something irreversible, and it
was the only one with no automated test: every defect it has carried was found
by a human hand-building a throwaway repo, and none of them could fail a build
afterwards. So these build the throwaway repo instead.

Each test fills the two placeholders with fabricated patterns, stages something,
and runs the hook exactly as the skill's verification recipe does - `sh
.githooks/pre-commit`, from the repo root. Nothing here resembles real material:
the probe values are invented prefixes that match nothing outside this file.

`core.hooksPath` is deliberately NOT set, so the fixture's own setup commit is
not run through the hook under test.
"""
import os
import pathlib
import shutil
import subprocess

import pytest

ASSET = pathlib.Path(__file__).resolve().parent.parent / (
    "skills/bootstrapping-a-system-of-record/assets/pre-commit-perimeter.sh"
)

# Fabricated, and chosen so no real document could match them.
FORBIDDEN_PATHS = 'private/*|*private/*|"personal notes/"*|*.fakekey'
CONTENT_PATTERN = "FAKEACCT-[0-9]{8}|zzsecret_[A-Za-z0-9]{6}"
PROBE_SECRET = "FAKEACCT-00000001"

# Long on purpose, and the rename test depends on it. git's rename detection
# only reports R once the pair clears a similarity threshold (50% by default);
# a one-line file plus a one-line edit scored R055, five points of margin, and
# below the threshold git reports D+A - which the buggy --diff-filter=ACM does
# list, so the regression test would have passed against the unfixed hook. At
# forty lines a move plus one appended line scores in the high nineties, the
# way the real defect did.
ORDINARY_BODY = "".join(
    f"- an ordinary line, number {n}, with nothing in it.\n" for n in range(1, 41)
)

pytestmark = pytest.mark.skipif(
    shutil.which("git") is None or shutil.which("sh") is None,
    reason="the perimeter hook tests need git and sh on PATH",
)


class Repo:
    """A throwaway git repo with the hook installed but not wired to git."""

    def __init__(self, path, forbidden=FORBIDDEN_PATHS, content=CONTENT_PATTERN):
        self.path = path
        (self.path / ".githooks").mkdir(parents=True)
        # Never inherit the machine's git identity, hooks, templates or aliases.
        self.env = dict(os.environ)
        self.env.update(
            HOME=str(path),
            XDG_CONFIG_HOME=str(path / ".config"),
            GIT_CONFIG_GLOBAL=os.devnull,
            GIT_CONFIG_SYSTEM=os.devnull,
            GIT_AUTHOR_NAME="Perimeter Test",
            GIT_AUTHOR_EMAIL="perimeter-test@example.invalid",
            GIT_COMMITTER_NAME="Perimeter Test",
            GIT_COMMITTER_EMAIL="perimeter-test@example.invalid",
        )
        self.git("-c", "init.defaultBranch=main", "init", "-q", ".")
        self.git("config", "user.name", "Perimeter Test")
        self.git("config", "user.email", "perimeter-test@example.invalid")
        self.git("config", "commit.gpgsign", "false")

        hook = ASSET.read_text(encoding="utf-8")
        assert "<FORBIDDEN_PATTERNS>" in hook and "<CONTENT_PATTERNS>" in hook
        hook = hook.replace("<FORBIDDEN_PATTERNS>", forbidden)
        hook = hook.replace("<CONTENT_PATTERNS>", content)
        (self.path / ".githooks/pre-commit").write_text(hook, encoding="utf-8")

    def git(self, *args, check=True):
        return subprocess.run(
            ["git", *args], cwd=self.path, env=self.env, check=check,
            capture_output=True, text=True,
        )

    def write(self, rel, text):
        p = self.path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def run_hook(self):
        return subprocess.run(
            ["sh", ".githooks/pre-commit"], cwd=self.path, env=self.env,
            capture_output=True, text=True,
        )


@pytest.fixture
def repo(tmp_path):
    r = Repo(tmp_path / "record")
    r.write("notes/ordinary.md", ORDINARY_BODY)
    r.git("add", "-A")
    r.git("commit", "-qm", "initial")
    return r


def test_the_hook_runs_and_passes_an_ordinary_file(repo):
    repo.write("notes/second.md", "Another ordinary line.\n")
    repo.git("add", "notes/second.md")
    r = repo.run_hook()
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout == ""


def test_a_forbidden_path_containing_a_space_is_blocked(repo):
    # Received documents are named like this, and word-splitting used to lose them.
    repo.write("private/Contract Signed 2024.md", "placeholder\n")
    repo.git("add", "-f", "private/Contract Signed 2024.md")
    r = repo.run_hook()
    assert r.returncode == 1, r.stdout + r.stderr
    assert "private/Contract Signed 2024.md is outside the perimeter" in r.stdout


def test_a_forbidden_path_containing_a_non_ascii_byte_is_blocked(repo):
    # git's default core.quotePath=true would spell this "private/A\303\261o.md",
    # which matches no case pattern and names no file.
    rel = "private/Contrato Firmado Año.md"
    try:
        repo.write(rel, "placeholder\n")
    except (UnicodeEncodeError, OSError):  # pragma: no cover - exotic filesystem
        pytest.skip("this filesystem cannot hold a non-ASCII path")
    repo.git("add", "-f", rel)
    r = repo.run_hook()
    assert r.returncode == 1, r.stdout + r.stderr
    assert f"{rel} is outside the perimeter" in r.stdout


def test_the_staged_blob_is_checked_not_the_worktree(repo):
    # Stage the secret, then tidy the working copy without re-staging it. The
    # index is what enters permanent history, so the hook must still block.
    repo.write("notes/paste.md", f"- reference {PROBE_SECRET}\n")
    repo.git("add", "notes/paste.md")
    repo.write("notes/paste.md", "- reference removed\n")
    r = repo.run_hook()
    assert r.returncode == 1, r.stdout + r.stderr
    assert "notes/paste.md matches a forbidden content pattern" in r.stdout


def test_a_rename_into_a_forbidden_path_is_blocked(repo):
    # The careless case the hook exists for: the file dragged into the wrong
    # directory. git reports it as a rename, and --diff-filter=ACM listed nothing.
    (repo.path / "private").mkdir()
    repo.git("mv", "notes/ordinary.md", "private/ordinary.md")
    with (repo.path / "private/ordinary.md").open("a", encoding="utf-8") as fh:
        fh.write(f"- reference {PROBE_SECRET}\n")
    repo.git("add", "-A")
    # The premise, asserted rather than assumed: git has to be reporting this
    # as a rename for the test to be testing anything. If a future edit to the
    # fixture drops the pair below the similarity threshold, git reports D+A,
    # the old buggy filter lists the add, and this test would go green against
    # an unfixed hook. Fail loudly instead of passing vacuously.
    status = repo.git("diff", "--cached", "--name-status", "-M").stdout
    assert any(
        line.startswith("R") and line.endswith("private/ordinary.md")
        for line in status.splitlines()
    ), f"git did not report a rename, so this test no longer guards C1:\n{status}"
    r = repo.run_hook()
    assert r.returncode == 1, r.stdout + r.stderr
    assert "private/ordinary.md is outside the perimeter" in r.stdout
    # The edit that rode along with the move is caught too.
    assert "private/ordinary.md matches a forbidden content pattern" in r.stdout


def test_a_typechange_into_a_forbidden_blob_is_blocked(repo):
    # A tracked symlink replaced by a real file. git calls that neither an add
    # nor a modification but a typechange, so the T in --diff-filter=ACMRT is
    # the only thing keeping the new blob in scope at all.
    link = repo.path / "notes/link.md"
    try:
        link.symlink_to("ordinary.md")
    except (OSError, NotImplementedError):  # pragma: no cover - no symlinks here
        pytest.skip("this filesystem cannot hold a symlink")
    repo.git("add", "notes/link.md")
    repo.git("commit", "-qm", "a tracked symlink")
    link.unlink()
    repo.write("notes/link.md", f"- reference {PROBE_SECRET}\n")
    repo.git("add", "notes/link.md")
    status = repo.git("diff", "--cached", "--name-status").stdout
    assert any(
        line.startswith("T") for line in status.splitlines()
    ), f"git did not report a typechange, so this test guards nothing:\n{status}"
    r = repo.run_hook()
    assert r.returncode == 1, r.stdout + r.stderr
    assert "notes/link.md matches a forbidden content pattern" in r.stdout


def test_a_file_over_the_size_limit_is_blocked(repo):
    repo.write("notes/large.md", "filler line\n" * 120_000)
    assert (repo.path / "notes/large.md").stat().st_size > 1048576
    repo.git("add", "notes/large.md")
    r = repo.run_hook()
    assert r.returncode == 1, r.stdout + r.stderr
    assert "notes/large.md is" in r.stdout and "over the 1 MiB limit" in r.stdout


def test_a_forbidden_content_pattern_is_blocked(repo):
    repo.write("notes/allowed-path.md", f"Invoice reference {PROBE_SECRET}.\n")
    repo.git("add", "notes/allowed-path.md")
    r = repo.run_hook()
    assert r.returncode == 1, r.stdout + r.stderr
    assert "notes/allowed-path.md matches a forbidden content pattern" in r.stdout
    # The path rule has nothing to say about it; only the content rule fired.
    assert "outside the perimeter" not in r.stdout


def test_an_empty_content_placeholder_switches_the_content_rule_off(tmp_path):
    # Documented behaviour: a repo with no content rules replaces the
    # placeholder with an empty string, and rule 3 stops running.
    r = Repo(tmp_path / "no-content-rules", content="")
    r.write("notes/paste.md", f"- reference {PROBE_SECRET}\n")
    r.git("add", "-A")
    out = r.run_hook()
    assert out.returncode == 0, out.stdout + out.stderr
    assert out.stdout == ""
