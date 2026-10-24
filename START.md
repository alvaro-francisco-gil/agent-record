# Start here

*[Leer en español](START.es.md)*

You don't need to know how to program. This sets up a private record of something in
your life (a vehicle, a new business, your career, a project) that an AI assistant keeps
up to date with you: the important facts, the papers and the deadlines.

**You need:** [Claude Code](https://claude.com/claude-code) installed and signed in to
your own Claude account, and a free [GitHub](https://github.com/signup) account.

**Then:** open Claude Code, copy the message below (the copy button is at its top
right), paste it, and answer its questions. It asks one at a time, and nothing is saved
until you've agreed what must never go in. Your record stays private unless you choose
otherwise.

```text
I'd like you to keep a private record of something in my life — what it is, everything
important about it, its papers and its deadlines — and keep it up to date with me from
now on. I don't program: do the technical steps yourself, explain each one in plain
words, and ask me before anything that can't be undone. Talk to me in my language.

1. Start by interviewing me, one question at a time: what this record is about, what I
   want it to do for me, who I ever send documents to, and which dates cost me if I miss
   them. Don't assume; if I'm vague, give me examples and let me pick.
2. Check that git, Python 3 and the GitHub CLI (gh) are installed. Install what's missing,
   or tell me exactly what to click. If gh isn't logged in, have me run `gh auth login`
   myself. Never ask me for a password or a token.
3. Install the plugin that knows how to build this:
   claude plugin install system-of-record --marketplace alvaro-francisco-gil/agent-record
   (version 1.3.0 or later). If its skills don't appear, tell me to restart Claude and
   paste this message again; you'll pick up where we left off.
4. Then use its bootstrapping-a-system-of-record skill, in a new folder under my home
   directory named after what we're recording. Follow it exactly, reusing what I already
   told you: nothing is saved to history until we've agreed what must never go in, it
   only adds the tools my answers justify, and the GitHub repo is private unless I say
   otherwise.
5. Never invent a date, an amount or a fact. Mark it as unknown and ask me.
6. When you finish, tell me in three short lines: where the record lives, how to ask you
   to add something, and what's coming up on my agenda.
```

What it builds and why is in the [README](README.md).
