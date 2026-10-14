# AI notes

## How you worked

I used Claude Code with Opus 5.5.

I spent roughly 1 hour reading through the documentation and writing the
first version of the SPEC, paying special attention to the fuzzy rules
and edge cases. I added some basic acceptance criteria.
Then, I created a first draft of the structure of the
project by hand, with the different services and layers.

I like to do TDD in some cases, so then I added a couple tests by hand
validating real behavior.

Then I started working with Claude. I asked it to write a CLAUDE.md file
with some rules, for example never to touch SPEC.md. I didn't create or
use any skills.

Then I asked it to validate what I wrote in SPEC against the examples,
README, and the tests.

After the basic structure was in place, I started asking it to turn some
of the acceptance criteria into test cases. Once that was done, I asked
it to actually start implementing the business logic. I started with the
pure functions for calculating the prices, and then started iterating
on creating more tests, validating the SPEC, and writing code that actually
passed the tests. Towards the end, I started doing some refactoring rounds,
for example moving functions to more specific files, improving types
by using Decimal instead of float, etc.

At the end I asked it to do a final check and see if everything made sense
according to the SPEC, if there were acceptance criteria that weren't being
tested.

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

When I asked it to create a CLAUDE.md file, it was very long and didn't
follow their own best practices. A second attempt added very specific
decisions that were already documented on SPEC.md, and I had to add that
that was the source of truth, and I didn't want to have duplicate info.

## What you kept without fully understanding

When writing the function to calculate the chargeable weight it wrote this:
`return max(weight_kg, volumetric).quantize(Decimal(1), rounding=ROUND_CEILING)`

The tests passed and I didn't think much of it. But then I understood that quantize is just the rounding function.

## What you have tried on your own

Whether or not you used an agent for this exercise: what have you tried with
Claude Code or a similar tool on real code, at work or on the side, and what
did it get wrong? One concrete story is worth more than a list of tools.
