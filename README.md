# cargo.one take-home: rate sheets in, offers out

Airlines send us rate sheets. Build a Python gRPC service that ingests them
and quotes shipments.

This mirrors the job. cargo.one is a marketplace for air cargo: forwarders
search, compare and book capacity across airlines. Rates come in from
airlines in many shapes; offers go out to forwarders. This challenge is the
smallest honest version of that loop.

Budget: about **4 focused hours**, spread over a **7-day window** as you like.

## Ground rules

- **Use an AI coding agent. We encourage Claude Code.** It is what we ship
  with day to day, and the follow-up interview assumes an agentic tool. An
  equivalent agent is fine if that is your real workflow. We will discuss
  *how* you used it as seriously as *what* you built.
- **Spec first.** Fill in `SPEC.md` before you write code, and commit it
  before the code. The commit history should show that order.
- **Keep an AI log** in `AI_NOTES.md`: which tools, where the model was wrong
  or you overrode it, what you would set up differently. "It one-shotted
  everything" is not a credible log.
- **Respect the timebox.** Unfinished but specced beats gold-plated but late.
  Note what you cut and why, and tell us how long you actually spent.
- **Deliver as a branch and merge request** on this repository. Branch
  `firstname-lastname`, target `main`. Use the MR description as your
  summary.

## The brief

Implement the two RPCs in `proto/quote.proto`:

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

- `rate_*` columns are prices per kg at each **weight break**: `normal` is
  under 45 kg, then 45, 100, 300 and 500 kg and up.
- `min_charge` is the lowest total price the airline will accept.
- `valid_from` and `valid_to` are inclusive dates.

`rate_sheets/malformed/XX.csv` is deliberately broken. Decide what your
ingestion does with it.

### Domain rules

1. **Chargeable weight** = max(actual weight, volumetric weight), where
   volumetric weight in kg = length × width × height in cm / 6000.
2. **Weight break**: the applicable break is the highest one at or below the
   chargeable weight. But a higher break may be cheaper (rate it as if the
   shipment weighed the break's minimum). If so, use it. This is called
   as-agreed rating.
3. **Minimum charge**: total price is never below `min_charge`.
4. **Validity**: a rate sheet row applies only if `shipping_date` falls inside
   its window.
5. No applicable rate for an airline means no offer for that airline.

The sample data has rough edges on purpose. Where these rules do not settle a
case, decide, and write the decision in `SPEC.md`.

### Worked example

Shipment FRA → JFK, 80 kg, 120 × 80 × 60 cm, shipping 2026-02-10.

Volumetric weight is 120 × 80 × 60 / 6000 = 96 kg, so chargeable weight is
96 kg. For LH (first row above): the 45 break gives 96 × 3.80 = 364.80 EUR,
but the 100 break gives 100 × 3.40 = 340.00 EUR, which is cheaper. Offer:
**LH, 340.00 EUR, break 100**.

With all four sample sheets ingested, the same request yields four offers:

| Airline | Total  | Currency | Break |
|---------|--------|----------|-------|
| LH      | 340.00 | EUR      | 100   |
| AF      | 365.00 | EUR      | 100   |
| EK      | 320.00 | USD      | 100   |
| QR      | 360.00 | USD      | 100   |

A 5 kg, 20 × 20 × 20 cm shipment on the same lane and date would rate at
5 × 4.10 = 20.50 EUR for LH, so the offer is the 90.00 EUR minimum charge.

### Scope

- `IngestRateSheet` and `GetQuote` implementing the rules above, with input
  validation and sensible gRPC status codes.
- Storage kept simple. SQLite or in-memory is fine. What we look for is a
  clean seam: real persistence should be swappable in later without touching
  the rating logic.
- Tests where they earn their keep. The rating logic above all.
- Runs with one documented command.

### Deliverables

`SPEC.md` (committed before the code), the code, tests, `AI_NOTES.md`, and
this README updated with how to run your version.

### What we look for

We read `SPEC.md`, the tests and `AI_NOTES.md` as closely as the code.

### What happens next

We grade every submission against the same rubric within 3 working days
of your MR. If it passes, there is 1 technical interview of 75 minutes
with one of our tech leads. In it you defend your submission with AI
tools closed, extend it live with your own agent, and then scale the
design on a whiteboard. Please have your environment and your agent ready
on your branch for that call. There is no other technical round.

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

## Layout

```
proto/quote.proto       service and message definitions (+ generated code)
quote_service/server.py gRPC server with stubbed RPCs
quote_service/client.py CLI client for manual testing
rate_sheets/            sample data, one CSV per airline, one malformed
tests/                  pytest with an in-process server fixture
SPEC.md                 your spec (fill in first)
AI_NOTES.md             your AI log
```
