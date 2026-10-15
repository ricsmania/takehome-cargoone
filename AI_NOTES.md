# AI notes

## How you worked

I used Claude Code with Opus 5.5.

I spent roughly 1 hour reading through the documentation and writing the first
version of the SPEC, paying special attention to the fuzzy rules and edge
cases. I added some basic acceptance criteria. Then, I created a first draft
of the structure of the project by hand, with the different services and
layers.

I like to do TDD in some cases, so then I added a couple tests by hand
validating real behavior.

Then I started working with Claude. I asked it to write a CLAUDE.md file with
some rules, for example never to touch SPEC.md. I didn't create or use any
skills.

Then I asked it to validate what I wrote in SPEC against the examples, README,
and the tests.

After the basic structure was in place, I started asking it to turn some of
the acceptance criteria into test cases. Once that was done, I asked it to
actually start implementing the business logic. I started with the pure
functions for calculating the prices, and then started iterating on creating
more tests, validating the SPEC, and writing code that actually passed the
tests. Towards the end, I started doing some refactoring rounds, for example
moving functions to more specific files, improving types by using Decimal
instead of float, etc.

At the end I asked it to do a final check and see if everything made sense
according to the SPEC, if there were acceptance criteria that weren't being
tested.

## Where it went wrong and what you changed

It got very picky about the language. For example, it insisted that we should
only compare the price with the break immediately higher, because since the
docs say "A higher break can still be cheaper" it said that this is singular
so we shouldn't look at all the higher breaks.

In several occasions it also ignored the decisions I made in the SPEC, and
insisted that I wasn't following the README when there were fuzzy rules. For
example, it said we shouldn't use any kind of rounding because the README
doesn't mention it, even though I had already written on the SPEC that I have
decided it.

When I asked it to create a test covering the overlapping date windows, it
added a smoke test rather than a unit test. I asked why, and it said I was
right to question it, and moved it to a unit test.

When creating tests, it added many helper functions with default values,
but I prefer to have explicit values passed, so it's easier to review and
it also lowers the chance of breaking later.

## What you kept without fully understanding

When writing the function to calculate the chargeable weight it wrote this:

```
return max(weight_kg, volumetric).quantize(Decimal(1), rounding=ROUND_CEILING)
```

The tests passed and I didn't think much of it. But then I understood that
quantize is just the rounding function.

Also some of these constructions, mostly because I have limited experience
with Python:

```
    for column, parsed in (("valid_from", valid_from), ("valid_to", valid_to)):
        if values[column] and parsed is None:
            errors.append(f"{column} must be an ISO 8601 date, got {values[column]}")
```

```
    start = max(i for i, (_, minimum_kg, _) in enumerate(breaks) if minimum_kg <= chargeable_weight)
```

## What you have tried on your own

I use Claude Code daily at my job, and also for personal projects. My main
issues for sure are the hallucinations. One of the responsibilities at work is
integrating with a transportation partner. They have their own API, and
neither the API nor the documentation is public. Even checking out the docs
locally, and instructing Claude explicitly to only consider that repository,
it often either checks another API from the same partner that is public, or
downright invents methods that don't exist and probably never existed.

I improved this behavior by adding specific instructions on CLAUDE.md to
always check the private API docs rather than the public one. The newer models
(5+) seem much better at actually following those instructions.

I also use LLMs for a hobby project, which is a game discovery/recommendation
platform, and I use Claude both for writing the code and also on the platform
itself.

There the challenge is more related to costs. I could use the LLMs to
recommend games directly, but that would be extremely expensive, so instead I
use some very light models such as Haiku for tagging games, and then I can
compare games based on those tags. Since it's a lighter model, there are some
quality issues with the output, such as tags that are too specific. For newly
added tags, I use Sonnet to evaluate the quality, and then I do a manual check
to see which ones are worth keeping. I also have some automated tests where I
compare the generated tags with a manually curated list for a few well known
games, and it gives me a score so I can improve the prompt and the tagging
engine.

The platform is also using Jev, a small classifier model from typesafe.ai,
for simple yes/no questions such as flagging spam/offensive content for manual
review.
