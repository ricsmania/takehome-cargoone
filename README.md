# cargo.one take-home: rate sheets in, offers out

Airlines send us rate sheets. Build a small gRPC service that ingests them
and quotes shipments. cargo.one is a marketplace for air cargo: forwarders
search, compare and book capacity across airlines. Rates come in from
airlines in many shapes, offers go out to forwarders, and this exercise is
the smallest honest version of that loop.

Budget: about 4 focused hours, spread over a 7 day window as you like.

## The brief

Implement the 2 RPCs in `proto/quote.proto`:

- `IngestRateSheet` loads one airline's rate sheet (CSV content, header
  included).
- `GetQuote` returns one offer per airline that has a valid, applicable rate
  for the shipment. No applicable rate means no offer for that airline. That
  is not an error.

### Rate sheets

One CSV per airline, in `rate_sheets/`. One row per lane and validity window:

```
airline,origin,destination,currency,valid_from,valid_to,min_charge,rate_normal,rate_45,rate_100,rate_300,rate_500
LH,FRA,JFK,EUR,2026-01-01,2026-03-31,90.00,4.10,3.80,3.40,2.95,2.60
```

- `rate_*` columns are prices per kg at each weight break: `normal` is
  under 45 kg, then 45, 100, 300 and 500 kg and up.
- `min_charge` is the lowest total price the airline will accept.
- `valid_from` and `valid_to` are inclusive dates.

`rate_sheets/malformed/XX.csv` is deliberately broken. Decide what your
ingestion does with it.

### Domain rules

1. Chargeable weight = max(actual weight, volumetric weight), where
   volumetric weight in kg = length x width x height in cm / 6000.
2. Weight break: the applicable break is the highest one at or below the
   chargeable weight. But a higher break may be cheaper (rate it as if the
   shipment weighed the break's minimum). If so, use it. This is called
   as-agreed rating.
3. Minimum charge: total price is never below `min_charge`.
4. Validity: a rate sheet row applies only if `shipping_date` falls inside
   its window.
5. No applicable rate for an airline means no offer for that airline.

The sample data has rough edges on purpose. Where these rules do not settle a
case, decide, and write the decision in `SPEC.md`.

### Worked example

Shipment FRA to JFK, 80 kg, 120 x 80 x 60 cm, shipping 2026-02-10.

Volumetric weight is 120 x 80 x 60 / 6000 = 96 kg, so chargeable weight is
96 kg. For LH (first row above): the 45 break gives 96 x 3.80 = 364.80 EUR,
but the 100 break gives 100 x 3.40 = 340.00 EUR, which is cheaper. Offer:
LH, 340.00 EUR, break 100.

With all 4 sample sheets ingested, the same request yields 4 offers:

| Airline | Total  | Currency | Break |
|---------|--------|----------|-------|
| LH      | 340.00 | EUR      | 100   |
| AF      | 365.00 | EUR      | 100   |
| EK      | 320.00 | USD      | 100   |
| QR      | 360.00 | USD      | 100   |

A 5 kg, 20 x 20 x 20 cm shipment on the same lane and date would rate at
5 x 4.10 = 20.50 EUR for LH, so the offer is the 90.00 EUR minimum charge.

### Scope

- Both RPCs implementing the rules above, with input validation and
  sensible gRPC status codes.
- Storage kept simple. In-memory or SQLite is fine. What we look for is a
  clean seam: real persistence should be swappable in later without touching
  the rating logic.
- Tests where they earn their keep. The rating logic above all.
- Runs with one documented command.

A 4 hour version is the rating logic with tests, ingestion that loads the
sample sheets, and a spec that says what you decided and what you cut.
Validation, persistence and the awkward edge cases are where extra hours
go. Cutting them with a note is fine. Unfinished but specced beats gold
plated but late.

## What you hand in

A branch `firstname-lastname` and a pull request into `main` in this
repository, with the PR description as your summary. On the branch:

- `SPEC.md`, filled in before you write code. What it says matters more
  than when it landed: your reading of the fuzzy rules, acceptance criteria
  we could paste into a test, and what you cut.
- The code and the tests.
- `AI_NOTES.md`, honest and short. AI tools are allowed and encouraged, not
  required. We build with Claude Code day to day and are happy to see you
  use it or an equivalent, and just as happy if you write this one by hand.
  Either way, say how you worked and what you have tried with these tools
  elsewhere. "It one-shotted everything" is not a credible log.
- This README updated with how to run your version, and how long you
  actually spent.

We read `SPEC.md` and the tests as closely as the code. The rating logic,
the data model and the seam between them carry the grade. `AI_NOTES.md`
tells us how you work; it differentiates, it does not filter. We hire on
engineering judgement and teach the workflow.

### Language

The scaffold is Python and that is our stack. If you are stronger in
another language, implement the same `proto/quote.proto` in that language
instead: keep the 2 RPCs and the request fields, listen on port 50051, and
document the run command here. We grade the design and the rating logic,
not the language.

## Running the scaffold

Needs Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```
make install   # create the venv and install dependencies
make test      # runs the one smoke test
make run       # starts the server on :50051 (both RPCs answer UNIMPLEMENTED)
make lint      # ruff
make protos    # regenerate proto/*_pb2* after editing quote.proto
```

A small client is included for manual poking, in a second terminal:

```
uv run python -m quote_service.client ingest rate_sheets/*.csv
uv run python -m quote_service.client quote FRA JFK 80 120x80x60 2026-02-10
```

Everything in this scaffold is yours to change, including the layout, the
build tool and the client.

```
proto/quote.proto       service and message definitions (+ generated code)
quote_service/server.py gRPC server with stubbed RPCs
quote_service/client.py CLI client for manual testing
rate_sheets/            sample data, one CSV per airline, one malformed
tests/                  pytest with an in-process server fixture
SPEC.md                 your spec (fill in first)
AI_NOTES.md             your notes on how you worked
```

## What happens next

We grade every submission against the same rubric within 3 working days of
your pull request. If it passes, there is 1 technical interview of 75 minutes with one
of our tech leads: you defend your submission and its data model with tools
closed, extend it live the way you normally work (agent, editor, your
call), then scale the design on a whiteboard. Have your environment ready
on your branch for that call. There is no other technical round.
