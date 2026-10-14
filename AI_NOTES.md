# AI notes

How you worked, and how you work with AI tools in general. Short is fine.
Delete these prompts as you fill the sections in.

## How you worked

Which agent and model, if any, and what you gave it (rules file, system
prompt, skills). If you wrote this by hand, say so and why.

I used Claude Code with Opus 5.5. After reading and understanding the
problem, I asked it to write a CLAUDE.md file with some rules, for
example never to touch SPEC.md. I didn't create or use any skills.

## Where it went wrong and what you changed

It got very picky about the language. For example, it insisted that we
should only compare the price with the break immediately higher, because
since the docs say "A higher break can still be cheaper" it said that this
is singular so we shouldn't look at all the higher breaks.

In several occations it also ignored the decisions I made in the SPEC, and
insisted that I wasn't following the README when there were fuzzy rules.
For example, it said we shouldn't use any kind of rounding because the
README doesn't mention it, even though I had already written on the SPEC
that I have decided it.

When I asked it to create a test covering the overlapping date windows,
it added a smoke test rather than a unit test. I asked why, and it said
I was right to question it, and moved it to a unit test.

If you used an agent: concrete cases where it was wrong (a bad assumption,
a subtle bug, an invented API, a weak test), how you caught each one, and
what you rewrote. If you did not use one: skip this section.

## What you kept without fully understanding

Be honest. A little is normal. We will ask about it.

## What you have tried on your own

Whether or not you used an agent for this exercise: what have you tried with
Claude Code or a similar tool on real code, at work or on the side, and what
did it get wrong? One concrete story is worth more than a list of tools.
