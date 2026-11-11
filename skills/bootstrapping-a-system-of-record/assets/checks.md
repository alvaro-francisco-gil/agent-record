# The three checks: specification and acceptance tests

**Specification version:** 1.4.0 (the system-of-record plugin)

The bootstrap installs three small checks in the adopting repo. This plugin does not ship
them as code. **You write each one from this file, run every acceptance test listed for it,
and do not make the repo's first commit until all of them pass.**

| Check | Path in the adopting repo | Default language | Installed |
|---|---|---|---|
| record-check | `scripts/record-check.py` | Python 3, standard library only | always |
| agenda | `scripts/agenda.py` | Python 3, standard library only | only if the record has dated obligations |
| perimeter hook | `.githooks/pre-commit` | POSIX `sh`, calling only `git`, `grep` (with `-E`, `-q` and `-I`, which GNU and BSD grep both have), `wc`, `mktemp`, `rm` | always |

Keep those paths and names even if you write a check in another language (then drop the
`.py` and say in the agents file how to run it). Agents files, habits and this plugin's
other instructions name them.

**What this costs, said plainly.** Two repos that adopt this convention will not have
byte-identical checkers: each was written by a different agent from the same text. What
they share is this specification and these tests. A behaviour the tests do not pin down may
differ between them. When you find such a gap, the fix belongs here, as a new test, not
only in one repo's copy.

## How to run the acceptance tests

- Work in a **scratch directory outside the repo being bootstrapped**, for example under
  the system temp directory. Never in the record itself, and never with real material.
- Copy the check you wrote into the scratch directory at the same relative path it will
  have in the repo, and run it exactly as the scenario says. **Run every command from that
  scratch directory**, which holds the check at `scripts/<name>` or `.githooks/pre-commit`
  and is also the `--root` the record-check scenarios name.
- "Run with" appends to the scenario's default command. A flag given there replaces the
  default command's value for that flag rather than repeating it.
- For the hook tests, isolate git from the machine: a fresh `git init` per scenario, and
  `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_SYSTEM=/dev/null` plus a throwaway author and
  committer name and email in the environment. Do **not** set `core.hooksPath` in a
  scenario unless it says so, so the setup commits are not run through the hook under test.
- "Output contains `X`" means standard output contains the text `X` anywhere. "Output has
  the line `X`" means one whole line of standard output is exactly `X`, leading spaces
  included. "Output is" means the whole of standard output, line by line. "No output" means
  standard output is empty. "Same result as" means the same standard output and exit code.
- **Every scenario must pass.** A scenario that cannot be run as written is a defect in this
  file: run the closest honest equivalent, say so to the human, and report it upstream.
- You may keep the scenarios as an automated test file in the repo, or not. Either way,
  re-run them whenever a check is edited later.
- Put a comment at the top of each check naming this file and the specification version at
  its top, so a later reader knows which specification to compare it against.

---

## 1. record-check

**What it is for.** The generic half of enforcement. It lints the syntax of the two
uncertainty markers, lists every open marker as the worklist, and verifies that the agents
file carries both anchors. It never reads content for sensitivity, so it cannot fire on a
healthy record. Unresolved markers are the worklist, not a failure.

### Command line

```text
python3 scripts/record-check.py [--root DIR] [--agents-file NAME]
    [--inferred-marker WORD] [--unknown-marker WORD] [--glob PATTERN]... [--list]
```

| Flag | Default | Meaning |
|---|---|---|
| `--root` | `.` | The directory to check. |
| `--agents-file` | `AGENTS.md` | The agents file's name, relative to the root. |
| `--inferred-marker` | `inferred` | The word in the bare marker, `[inferred]`. |
| `--unknown-marker` | `unknown` | The word in the question marker, `[unknown: ...]`. |
| `--glob` | `*.md` | A file-name pattern to sweep. Repeatable. **Giving it replaces the default**, so a repo that keeps Markdown and a ledger passes `--glob '*.md' --glob '*.beancount'`. |
| `--list` | off | Print the worklist and errors, and always exit 0. |

Below, `U` is the unknown word and `I` the inferred word. Matching is literal and
case-sensitive.

### Behaviour

1. **Anchors.** If `<root>/<agents-file>` does not exist, that is the error
   `<agents-file>: missing`. Otherwise its text must contain, anywhere, the exact strings
   `<!-- record:perimeter -->` and `<!-- record:routing -->`. Each one absent is the error
   `<agents-file>: missing the <!-- record:perimeter --> anchor` (or `record:routing`).
2. **Which files are swept.** Every regular file under the root, at any depth, whose file
   name matches at least one glob (shell-style, matched against the name). A file matching
   two globs is swept once. Symlinked directories are not descended into; a symlink to a
   file is read as that file, under its own name (so a swept target is listed twice). All the skip rules look only at the path **relative to the
   root**, so a root that itself sits under a dot-directory is still swept. Skipped:
   - any path with a component named `.git`, `node_modules`, `.venv`, `venv` or
     `__pycache__`;
   - any file inside a directory below the root whose name starts with `.`, at any depth
     (tooling, transcripts and agent scratch live there; a record layer does not). A file
     whose own name starts with `.` is not skipped for that;
   - every file whose name equals the last path component of `--agents-file`, at any depth.
     The root one was read for its anchors; none is swept, because that is where the markers
     are defined.

   Files are processed in sorted path order. Paths in output are relative to the root,
   with `/` separators.
3. **Decoding and lines.** Read every file as UTF-8, replacing undecodable bytes. A file
   that is not UTF-8 is never a crash and never an error by itself. Lines are separated by
   `\n` only (a trailing `\r` is whitespace); line numbers are 1-based.
4. **Fenced blocks are ignored.** A line that is optional whitespace followed by three
   backticks or three tildes toggles "inside a fence"; either kind closes either kind, a
   deliberate simplification. The fence lines and every line between them are blanked
   before matching. Line numbers still count them. A fence never closed blanks the rest of
   the file.
5. **Code spans.** A code span is a backtick, then zero or more characters other than a
   backtick or a newline, then a backtick, on one line. Backticks pair left to right. A marker is *quoted* when its matched text
   overlaps a code span. Quoting only matters where the rules below say so.
6. **The question marker.** `[U:` then optional spaces, then the question, then `]`. The
   question is any text without `]`. It may wrap onto following lines, but a blank line
   (empty, or only spaces and tabs) or the end of the file ends it. Normalise the question
   by collapsing every run of whitespace to one space and trimming.
   - Non-empty question: a worklist item `<path>:<line>: <question>`, where `<line>` is the
     line the marker starts on.
   - Question is exactly `<` + text (possibly empty) without `<` or `>` + `>`, such as
     `<question>`: a
     template placeholder. Neither listed nor an error, quoted or not.
   - Empty question: the error `<path>:<line>: [U:] has an empty question`, unless quoted,
     in which case it is prose about markers and ignored.
7. **Unterminated.** Scan for question markers left to right; after a match, scanning
   resumes after its `]`. Every occurrence of `[U:` that is not the start of a matched
   marker is the error `<path>:<line>: [U: is unterminated`, unless quoted. That includes a
   `[U:` with no `]` before a blank line or the end of the file, and a `[U:` sitting inside
   another marker's question (most often the first one is missing its `]`). It must never
   swallow the rest of the document.
8. **The bare form `[U]`.** An error, `<path>:<line>: [U] carries no question`, unless
   quoted. Exception: when `I` and `U` are the same word, the repo runs one marker in two
   forms, and the bare form means "unverified": it is then the inferred marker of rule 9,
   never an error.
9. **The inferred marker `[I]`.** Every occurrence, quoted or not, is a worklist item
   `<path>:<line>: [I] <that line's text, trimmed, first 90 characters>`.
10. **Only the declared words are markers.** Once a repo declares its own pair, the
    English defaults are ordinary prose.

### Output and exit code

- **Order.** Worklist: files in sorted path order; within a file, question-marker items in
  position order, then inferred items in position order. Errors: anchor errors first, then
  per file in sorted path order: empty-question errors, then unterminated, then bare-marker
  errors, each in position order.
- If `--list` was given or the worklist is not empty: the line
  `worklist - <N> open marker(s)`, then each item on its own line indented two spaces.
- If there are errors: the line `FAIL`, then each error as `  - <error>`.
- With `--list`: exit 0, always, and no `OK` line. It is the health check the agents file
  installs, run by habit, so it never fails, and it still prints every error.
- Without `--list`: exit 1 if there is any error. Otherwise print
  `OK - no malformed markers, anchors present (<N> open marker(s))` and exit 0.
- Reading the output through a pipe that closes early (`... --list | head`) prints no
  traceback or error to standard error. The exit code stays the honest one.
- No dependency outside the language's standard library.

### What it does not cover

- Only the declared globs. A marker in a format nobody declared is invisible.
- Fenced blocks and code spans are Markdown notions, applied to every swept file, so a stray
  backtick in a non-Markdown source can hide a *malformed* marker. It can never hide a real
  question, because a quoted question still counts.
- A marker written in an agents file is never listed. Put facts in sources.
- A prose mention of `[I]` in backticks is counted, because nothing distinguishes it from a
  use. Quote the convention in a fenced block to keep it out of the worklist.
- Nothing here can check the evidence rule. A pass is not evidence that a document is
  honest.

### Acceptance tests

Unless a scenario says otherwise: the scratch root holds `AGENTS.md` whose text is
`# AGENTS.md`, `<!-- record:perimeter -->` and `<!-- record:routing -->` on three lines,
the command is `python3 scripts/record-check.py --root <scratch root>`, and `note.md` is
a file in the root. `\n` in file contents means a line break.

- **RC1.** `note.md`: `Revenue [unknown: what did Q3 close at?]`. Expect: exit 0; output contains `OK - no malformed markers, anchors present (1 open marker(s))` and has the line `  note.md:1: what did Q3 close at?`; no `FAIL`.
- **RC2.** `note.md`: `Revenue [unknown:]`. Expect: exit 1; output contains `FAIL` and `  - note.md:1: [unknown:] has an empty question`.
- **RC3.** `note.md`: `Revenue [unknown]`. Expect: exit 1; output contains `note.md:1: [unknown] carries no question`.
- **RC4.** `note.md`: `Founded in 2011 [inferred]`. Expect: exit 0; output has the line `  note.md:1: [inferred] Founded in 2011 [inferred]`.
- **RC5.** `AGENTS.md` holds only `<!-- record:routing -->`. Expect: exit 1; output contains `AGENTS.md: missing the <!-- record:perimeter --> anchor`.
- **RC6.** `AGENTS.md` holds only `<!-- record:perimeter -->`. Expect: exit 1; output contains `AGENTS.md: missing the <!-- record:routing --> anchor`.
- **RC7.** no `AGENTS.md`; `note.md`: `nothing to see`. Expect: exit 1; the only error line is `  - AGENTS.md: missing`.
- **RC8.** `nota.md`: `Ingresos [desconocido:]\nFundada en 2011 [inferido]\nFounded in 2011 [inferred], revenue [unknown] and [unknown: how much?]`. Run with: `--inferred-marker inferido --unknown-marker desconocido`. Expect: exit 1; output contains `nota.md:1: [desconocido:] has an empty question` and `nota.md:2: [inferido]`; no line mentions `nota.md:3`.
- **RC9.** `nota.md`: `Fundada en 2011 [inferido]`. Run with: `--inferred-marker inferido --unknown-marker desconocido`. Expect: exit 0; output contains `[inferido]`.
- **RC10.** no `AGENTS.md`; `CLAUDE.md` with the two anchors. Run with: `--agents-file CLAUDE.md`. Expect: exit 0; output contains `anchors present`.
- **RC11.** `AGENTS.md` also holds the lines ``- `[inferred]` means derived.`` and ``- `[unknown: <question>]` means ask.``. Run with: `--list`. Expect: exit 0; output has the line `worklist - 0 open marker(s)`; no `FAIL`; no line starting `OK`.
- **RC12.** `project/AGENTS.md`: `Unconfirmed values carry [unknown: <question>] or [inferred].`. Run with: `--list`. Expect: exit 0; `worklist - 0 open marker(s)` (an agents file at any depth is skipped).
- **RC13.** `recibo.md` holds the Latin-1 bytes of `Café [unknown: what did it cost?]`, e.g. `printf 'Caf\351 [unknown: what did it cost?]\n' > recibo.md`. Expect: exit 0; output contains `recibo.md:1: what did it cost?`; nothing on standard error.
- **RC14.** `note.txt`: `Revenue [unknown]`. Expect: exit 0; `(0 open marker(s))` (only `*.md` by default).
- **RC15.** `note.md`: `Revenue [unknown] and [unknown: how much?]`. Run with: `--list`. Expect: **exit 0**; output contains `how much?`, `FAIL` and `note.md:1: [unknown] carries no question`.
- **RC16.** `note.md`: `ordinary`. Run with: `--list`. Expect: exit 0; output has the line `worklist - 0 open marker(s)`; no `FAIL`; no line starting `OK`.
- **RC17.** `doc.md`: ``Open questions use `[unknown:]` markers.``. Expect: exit 0; `(0 open marker(s))`.
- **RC18.** `doc.md`: `Syntax:\n\n` then a fence of three backticks, `[unknown: what did Q3 close at?]`, `[inferred]`, `[unknown]`, `[unknown:`, the closing fence; then the same four lines again between `  ~~~` fences. Expect: exit 0; `(0 open marker(s))`.
- **RC19.** `doc.md`: ``Use `[unknown:]` like this: [unknown: what rate?]``. Expect: exit 0; `(1 open marker(s))`; output contains `what rate?`.
- **RC20.** `note.md`: ``Cost `[unknown: what did it come to?]` ``. Expect: exit 0; output contains `note.md:1: what did it come to?` (a real question in backticks still counts).
- **RC21.** `note.md`: ``Expect 400-900 a year `[inferred]` ``. Expect: exit 0; output contains `note.md:1: [inferred]`.
- **RC22.** `note.md`: ``Never write a bare `[unknown]`.``. Expect: exit 0; `(0 open marker(s))`.
- **RC23.** `doc.md`: `Write [unknown: <question>] to ask.`. Expect: exit 0; `(0 open marker(s))`.
- **RC24.** `note.md`: `- [unknown: can the council be a\n  beneficiary under this call?]`. Expect: exit 0; `(1 open marker(s))`; the item is the single line `  note.md:1: can the council be a beneficiary under this call?`.
- **RC25.** `note.md`: `Revenue [unknown: what did Q3 close at\n\nNext paragraph.`. Expect: exit 1; output contains `note.md:1: [unknown: is unterminated`; no `worklist` line.
- **RC26.** `note.md`: `First line.\nRevenue [unknown: still open` with a final line break and nothing after. Expect: exit 1; output contains `note.md:2: [unknown: is unterminated`.
- **RC27.** `nota.md`: `tipo: "[[confirmar]]"\nEl plazo [[confirmar: cierra en junio o en julio?]]`. Run with: `--inferred-marker confirmar --unknown-marker confirmar`. Expect: exit 0; worklist has an item starting `nota.md:1: [confirmar]` and the item `nota.md:2: cierra en junio o en julio?`; no `FAIL`.
- **RC28.** `.tooling/report.md` and `.a/b/deep.md` and `node_modules/x.md`, each: `Revenue [unknown: what did Q3 close at?] and [unknown]`. Expect: exit 0; `(0 open marker(s))`.
- **RC29.** `note.md`: 5000 lines, line n `Item n [unknown: what is item n?]`. Run as `python3 scripts/record-check.py --root . --list 2>err.txt | head -1` from the scratch root. Expect: `err.txt` is empty (no traceback on a closed pipe).
- **RC30.** `libro.beancount`: `  justificante: "[unknown: is there a receipt?]"`. Expect: exit 0; `(0 open marker(s))`.
- **RC31.** `libro.beancount` as RC30; `registro.yml`: `  alta: [inferred]`. Run with: `--glob '*.md' --glob '*.beancount' --glob '*.yml'`. Expect: exit 0; output contains `libro.beancount:1: is there a receipt?` and `registro.yml:1: [inferred]`.
- **RC32.** `note.md`: `Revenue [unknown: what did Q3 close at?]`. Run with: `--glob '*.md' --glob 'note.md'`. Expect: exit 0; `(1 open marker(s))` (swept once).
- **RC33.** `notes/sub/a.md`: three-backtick fence, `x`, closing fence, then `[unknown: which year?]`. Expect: exit 0; output has the line `  notes/sub/a.md:4: which year?` (path relative to the root; blanked fence lines still counted).
- **RC34.** `note.md`: `Revenue [unknown: what did Q3 close at?]`. Run as `python3 -I -S scripts/record-check.py ...` with the usual arguments. Expect: same result as RC1 (no third-party module needed).
- **RC35.** `doc.md`: three backticks, then `~~~`, then `[unknown: after the fence?]`, on three lines with nothing between them. Expect: exit 0; output contains `doc.md:3: after the fence?` (either fence kind closes either).
- **RC36.** `note.md`: `Cost [unknown: first [unknown: second]`. Expect: exit 1; output has the line `  note.md:1: first [unknown: second` and contains `note.md:1: [unknown: is unterminated` (the inner opener, a sign the outer `]` is missing).

---

## 2. agenda

**What it is for.** Lists what the obligations register says is overdue, then what closes
soon, so a session raises dates before the task at hand. Installed only when the interview
surfaced a dated obligation.

### Command line

```text
python3 scripts/agenda.py [--register PATH] [--within N] [--check] [--today YYYY-MM-DD]
```

| Flag | Default | Meaning |
|---|---|---|
| `--register` | `obligations.md` | The register file, relative to the working directory. |
| `--within` | `45` | Days ahead to list. |
| `--check` | off | Validate the register only. |
| `--today` | the local date | The date to compute against. Exists so the tests below are fixed; nobody passes it day to day. |

### The register

The register is the Markdown table in `obligations.md` (copied from this skill's
`assets/obligations.md`). It is Markdown so a person can read and edit it without tooling,
and so the check needs no parser beyond the standard library.

1. **Finding the table.** The header is the first line that starts (after optional
   whitespace) with `|` and whose cells, lowercased, are exactly
   `id`, `what`, `opens`, `closes`, `if missed`, `explained in`, `done`, in that order. None:
   the error `<path>: no table with the columns id | what | opens | closes | if missed | explained in | done`,
   where `<path>` is the value given to `--register`.
2. **Cells.** Trim the line; drop one leading `|`; drop one trailing `|` unless it is
   escaped as `\|`; split on every `|` not preceded by a backslash; trim each cell; turn
   `\|` into `|`.
3. **Rows.** The line after the header (the separator) is skipped. Every following line
   that starts, after optional whitespace, with `|` is a row; the first line that does not
   (a blank line, prose) ends the table. A row's line number is its 1-based line in the file.
4. **Validation.** Errors are prefixed `line <n> (<id, or ? if empty>): `.
   - A row with a cell count other than 7: `line <n>: <k> cells, expected 7` (this error
     has no id in its prefix), and the row is otherwise ignored.
   - `empty id`; `duplicate id` (second and later occurrences); `empty what`;
     `empty 'if missed'`.
   - `opens` may be empty or `-`. Otherwise `opens`, and always `closes`, must be a real
     calendar date written exactly `YYYY-MM-DD`; if not:
     `<opens|closes> '<value>' is not a real YYYY-MM-DD date`. So `2027-02-30`, `2027-3-1`
     and an `[unknown: ...]` marker all fail.
   - Both dates present and `opens` later than `closes`: `opens after it closes`.
   - Rows that are done are validated too.

### Behaviour

- Register file absent: print `no register at <path>`, exit 1.
- Any error, in either mode: print `<path>: <k> problem(s)`, then each error as
  `  - <error>`, exit 1.
- `--check` and valid: print `<path>: <n> row(s), valid`, exit 0.
- Otherwise, the agenda. A row whose `done` cell is non-empty is off the agenda. An open row
  is **overdue** when `closes` is before today, and **upcoming** when `closes` is from today
  to today plus `--within` days, inclusive. Each group is sorted by `closes`; rows with the
  same `closes` keep their order in the file. A group with no rows prints no heading.
  - Overdue rows under the line `OVERDUE`, then upcoming rows under the line
    `Closing in the next <N> days`. Neither: the line
    `Nothing overdue, nothing closing in the next <N> days.`
  - Each row is the line
    `  <closes>  <what>  (<when><opens>; if missed: <if missed>)  [<id>]`, with two spaces
    between fields as shown. `<when>` is `<d> days overdue`, `closes today` or
    `closes in <d> days`. `<opens>` is `, opens <opens>` only when `opens` is a date after
    today, else empty. The wording is literal, `1 days` included.
  - Exit 1 if anything is overdue, so a hook or CI job can use it; exit 0 otherwise,
    including when nothing is due.
- No dependency outside the language's standard library.

### What it does not cover

- It reads one file. A date written anywhere else in the record is invisible; the register
  exists so that dates are written nowhere else.
- It reaches nobody. It runs when someone runs it.
- It trusts `done`. A row marked done with a wrong path is off the agenda.

### Acceptance tests

Unless a scenario says otherwise: `obligations.md` is this skill's `assets/obligations.md`
copied unchanged with the given rows appended, one per line, directly under the table; the
command is `python3 scripts/agenda.py --register obligations.md --today 2027-03-10`.

- **AG1.** none. Expect: exit 0; output is `Nothing overdue, nothing closing in the next 45 days.`.
- **AG2.** none. Run with: `--check`. Expect: exit 0; output is `obligations.md: 0 row(s), valid`.
- **AG3.** `| insurance-2027 | Renew insurance | - | 2027-03-31 | uninsured | - | |`. Expect: exit 0; output is `Closing in the next 45 days` then `  2027-03-31  Renew insurance  (closes in 21 days; if missed: uninsured)  [insurance-2027]`.
- **AG4.** `| inspection-2027 | Pass the inspection | 2027-01-01 | 2027-03-01 | fine | - | |`. Expect: exit 1; output contains `OVERDUE` and `9 days overdue`.
- **AG5.** `| inspection-2027 | Pass the inspection | - | 2027-03-01 | fine | - | inspections/2027-02-20.md |`. Expect: exit 0; output does not contain `Pass the inspection`.
- **AG6.** `| filing-q2 | File the return | - | 2027-07-20 | surcharge | - | |`. Run with: none, then `--within 200`. Expect: first run does not list `File the return`; second run lists it; both exit 0.
- **AG7.** `| x | Something | - | 2027-02-30 | cost | - | |`. Expect: exit 1; output contains `closes '2027-02-30' is not a real YYYY-MM-DD date`.
- **AG8.** `| x | Something | - | 2027-3-1 | cost | - | |`. Run with: `--check`. Expect: exit 1; output contains `is not a real YYYY-MM-DD date`.
- **AG9.** `| x | One | - | 2027-04-01 | cost | - | |` and `| x | Two | - | 2027-04-02 |  | - | |`. Run with: `--check`. Expect: exit 1; output contains `duplicate id` and `empty 'if missed'`.
- **AG10.** `| x | One | 2027-05-01 | 2027-04-01 | cost | - | |`. Expect: exit 1; output contains `opens after it closes`.
- **AG11.** `| x | One | 2027-04-01 | cost |`. Expect: exit 1; output contains `4 cells, expected 7`.
- **AG12.** `| x | Pay A \| B | - | 2027-03-20 | cost | - | |` (a backslash before the middle pipe). Expect: exit 0; output contains `Pay A | B` (the escaped pipe stays in its cell).
- **AG13.** `| renewal | Renew the policy | - | [unknown: when does it renew?] | lapse | - | |`. Run with: `--check`. Expect: exit 1; output contains `not a real YYYY-MM-DD date` (an unknown date is never a tracked date).
- **AG14.** `| late | File late one | 2027-04-01 | 2027-04-20 | fee | - | |` then `| now | Pay today | - | 2027-03-10 | fee | - | |`. Expect: exit 0; `now` (with `closes today`) is listed before `late`, and the `late` line contains `, opens 2027-04-01`.
- **AG15.** `| ok | Fine | - | 2027-04-01 | fee | - | |`, then a blank line, then `| broken |`. Run with: `--check`. Expect: exit 0; `1 row(s), valid` (the blank line ends the table).
- **AG16.** file contains only `# Obligations\n\nNothing here yet.`. Expect: exit 1; output contains `no table`.
- **AG17.** no file. Run with: `--register nope.md`. Expect: exit 1; output contains `no register at`.
- **AG18.** as AG3. Run as `python3 -I -S scripts/agenda.py ...` with the usual arguments. Expect: same result as AG3.

---

## 3. The perimeter hook

**What it is for.** The repo-specific half of enforcement. Before each commit it refuses
oversized files, forbidden paths and forbidden content in what is about to enter permanent
history. It is generated per repo because every rule depends on a layout only that repo
has. It catches the careless case, not a determined one.

### Settings

Two values, filled from interview question 3, written once near the top of the hook so a
person can find and change them:

- **Forbidden path patterns:** shell `case` patterns joined by `|`, matched against the
  whole staged path, for example `private/*|*private/*|*.key`. `private/*` misses
  `a/private/x`; `*private/*` catches both. A pattern containing a space is quoted:
  `"personal notes/"*`. No path rules at all: the single pattern
  `.perimeter-no-path-rules`, which matches no real file, and the agents file says so.
- **Forbidden content pattern:** one POSIX extended regular expression, for example an
  account-number shape or a key prefix. ERE has no `\d`, `\w` or `\s`: write `[0-9]`,
  `[A-Za-z0-9_]`, `[[:space:]]`. No content rules at all: the empty string, which turns the
  content rule off.

How the settings sit in the file matters, because the obvious ways are wrong:

- The path patterns must act as `case` syntax, where `|` separates alternatives and quotes
  group a pattern with a space. A variable expanded into a `case` pattern does neither: its
  `|` is a literal character, and the rule silently matches nothing. Write the patterns into
  the `case` arm itself, or evaluate the setting as `case` syntax.
- The content pattern must reach `grep` byte for byte, whatever quotes it contains (HK12,
  HK13). A pattern pasted inside double or single quotes breaks on the first quote of the
  same kind; a quoted here-document read with `IFS= read -r` does not.
- **The hook holds its own content pattern, and the hook is committed.** A pattern with no
  regular-expression syntax in it, such as a literal company prefix, matches its own text,
  and the hook then blocks the commit that adds it. Write such a pattern so it cannot match
  itself (`ACME[-]INTERNAL`, not `ACME-INTERNAL`); HK17 proves it.

Write the hook first with the two settings as the literal text `<FORBIDDEN_PATTERNS>` and
`<CONTENT_PATTERNS>`, run HK1, then fill them in.

### Behaviour

1. **The staged list.** The files to check are exactly what
   `git -c core.quotePath=false diff --cached --no-renames --name-only --diff-filter=ACMRT`
   lists. Each part is load-bearing:
   - `--no-renames` with `R` and `T` in the filter. With rename detection on and only
     `ACM`, `git mv notes/x.md private/x.md` plus an edit in the same commit lists
     *nothing*, and the file dragged into the wrong directory, the very case the hook
     exists for, enters history in silence. `--no-renames` reports the move as the add it
     really is. `T` (typechange: a tracked symlink replaced by a real file) is the only
     thing that keeps that new blob in scope.
   - `core.quotePath=false`, so a non-ASCII name such as `Contrato Firmado Año.pdf` is
     listed as itself rather than C-quoted into a string that matches no pattern.
2. **One path per line, no word-splitting, no pipe into the loop.** Read the list one whole
   line at a time, so a path with spaces stays one path. Feed the loop from a temporary file
   (removed on exit), not from a pipe, so the "something failed" flag is not lost in a
   subshell.
3. **The staged blob, never the working tree.** Every content and size check reads the
   staged version (`git show ":0:<path>"`). The index is what enters history; a file edited
   clean after `git add` still carries what was staged.
4. **Rule 1, size.** A staged blob over 1048576 bytes:
   `perimeter: <path> is <size in KiB, rounded down> KiB - over the 1 MiB limit`.
5. **Rule 2, path.** A staged path matching a forbidden pattern:
   `perimeter: <path> is outside the perimeter`.
6. **Rule 3, content.** Unless the content pattern is empty: a staged blob that is text and
   matches it: `perimeter: <path> matches a forbidden content pattern`. Binary blobs are
   not searched; binary means what `grep -I` treats as binary. Every character of the pattern reaches the matcher unchanged, including
   `"` and `'`.
7. **Submodule entries** have no blob here. Size and content checks pass over them silently
   (no error output); what they point at is governed by that repo's own perimeter.
8. **All rules run over all files**, so one run reports every problem. Messages go to
   standard output. Exit 1 if anything fired; otherwise exit 0 with no output.
9. **Never silently match nothing.** If either setting still holds its placeholder, or the
   path setting is empty, the hook exits non-zero on every run, with a message naming the
   setting. (A path placeholder written literally into a `case` arm is a syntax error and
   fails anyway; a content placeholder is valid shell and would run and match nothing.)
10. **Installed and live:** executable bit set, and `git config core.hooksPath .githooks`.
    Git skips a non-executable hook without a word.

### What it does not cover

- `--no-verify` skips it, and a fresh clone has no hook until `core.hooksPath` is set there:
  local config is never committed.
- Git quotes a path containing a newline, a double quote or a backslash whatever
  `quotePath` says; such a path is not matched against the rules.
- The content rule only ever applies to text. A UTF-16 document, or a text file carrying a
  pasted binary run, is treated as binary and passes that rule unexamined.
- Pattern lists are never complete, and committing is not the only way material leaves a
  machine.

### Acceptance tests

Unless a scenario says otherwise: a fresh repository with the hook at
`.githooks/pre-commit`, its settings filled with these fabricated test values, which match
nothing real:

- forbidden path patterns: `private/*|*private/*|"personal notes/"*|*.fakekey`
- content pattern: `FAKEACCT-[0-9]{8}|zzsecret_[A-Za-z0-9]{6}`

and one setup commit holding the hook itself and `notes/ordinary.md`, of forty lines (`- an ordinary line, number
<n>, with nothing in it.`). Forty lines matter: git reports a rename only above a
similarity threshold, and a tiny file plus an edit falls below it, which would let HK6 pass
against a hook that is still broken. The command is `sh .githooks/pre-commit` from the repo
root, with `core.hooksPath` unset.

- **HK1.** the hook with the path setting left as `<FORBIDDEN_PATTERNS>`; then, separately, with only the content setting left as `<CONTENT_PATTERNS>`; stage `notes/second.md` each time. Then a third run with the path setting empty, the content setting filled, and `notes/second.md` staged. Expect: each run exits non-zero; the content-placeholder run's output contains `content`, and the empty-path run's output contains `path`.
- **HK2.** `notes/second.md`: `Another ordinary line.`. Expect: exit 0; no output.
- **HK3.** `private/Contract Signed 2024.md`. Expect: exit 1; output contains `perimeter: private/Contract Signed 2024.md is outside the perimeter`.
- **HK4.** `private/Contrato Firmado Año.md`. Expect: exit 1; output contains `perimeter: private/Contrato Firmado Año.md is outside the perimeter`.
- **HK5.** stage `notes/paste.md` holding `- reference FAKEACCT-00000001`, then overwrite the working copy with `- reference removed` without re-staging. Expect: exit 1; output contains `perimeter: notes/paste.md matches a forbidden content pattern`.
- **HK6.** `mkdir private && git mv notes/ordinary.md private/ordinary.md`, append `- reference FAKEACCT-00000001` to it, `git add -A`. First confirm the premise: `git diff --cached --name-status -M` shows an `R` line ending in `private/ordinary.md`; if not, the scenario is broken, not passed. Expect: exit 1; output contains `private/ordinary.md is outside the perimeter` and `private/ordinary.md matches a forbidden content pattern`.
- **HK7.** commit a symlink `notes/link.md` pointing at `ordinary.md`; replace it with a regular file holding `- reference FAKEACCT-00000001`; stage it. Confirm `git diff --cached --name-status` shows a `T` line. Expect: exit 1; output contains `notes/link.md matches a forbidden content pattern`.
- **HK8.** `notes/large.md`: 120000 lines of `filler line` (over 1 MiB). Expect: exit 1; output contains `notes/large.md is` and `over the 1 MiB limit`.
- **HK9.** `notes/allowed-path.md`: `Invoice reference FAKEACCT-00000001.`. Expect: exit 1; output contains `notes/allowed-path.md matches a forbidden content pattern` and not `outside the perimeter`.
- **HK10.** content setting empty; stage `notes/paste.md` holding `- reference FAKEACCT-00000001`. Expect: exit 0; no output (empty switches the content rule off).
- **HK11.** `personal notes/plan.md`, and `archive/private/old.md`, and `keys/test.fakekey`. Expect: exit 1; each of the three paths is reported `outside the perimeter` (quoted pattern with a space, `*private/*` at depth, a suffix at any depth).
- **HK12.** content pattern `key="[A-Z]{4}"`; stage `a.md` holding `key=` alone, run; then `b.md` holding `key="ABCD"`, run. Expect: first run exit 0 with no output; second run exit 1 reporting `b.md` (a `"` in the pattern is literal, never a shell quote).
- **HK13.** content pattern `it's-[0-9]{3}`; stage `c.md` holding `it's-123`. Expect: exit 1 reporting `c.md`.
- **HK14.** a submodule entry: `git update-index --add --cacheinfo 160000,0123456789abcdef0123456789abcdef01234567,vendor/lib` (a commit that does not exist here, as a submodule's usually does not; git accepts the entry). Expect: exit 0; no output and nothing on standard error.
- **HK15.** `git config core.hooksPath .githooks`; `test -x .githooks/pre-commit`; stage `private/probe.md`; run `git commit -m probe`. Expect: `test -x` succeeds; the commit fails; `git log` has no new commit (git itself runs the hook).
- **HK16.** `notes/a.md` holding `zzsecret_ABC123` and `private/b.md` holding nothing secret, staged together. Expect: exit 1; both files reported in one run.
- **HK17.** content pattern `ACME[-]INTERNAL`; change one line of `.githooks/pre-commit` (a comment will do) and stage it. Expect: exit 0; no output (the hook does not block itself). Then stage `d.md` holding `ACME-INTERNAL`: exit 1 reporting `d.md`.

After these pass on the scratch copy, fill the real repo's settings and run the bootstrap
skill's *Verify the hook* steps against the real patterns, with fabricated probe values
built from them.
