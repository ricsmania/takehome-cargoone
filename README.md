# cargo.one take-home: rate sheets in, offers out

Airlines send us rate sheets. Build a small gRPC service that ingests them
and quotes shipments. cargo.one is a marketplace for air cargo: forwarders
search, compare and book capacity across airlines. Rates come in from
airlines in many shapes, offers go out to forwarders, and this exercise is
a small version of that loop.

Budget: about 4 focused hours, spread over a 7 day window as you like.

## The brief

Implement the 2 RPCs in `proto/quote.proto`:

- `IngestRateSheet` loads one airline's rate sheet (CSV content, header
  included).
- `GetQuote` returns one offer per airline that has a valid, applicable rate
  for the shipment. No applicable rate means no offer for that airline. That
  is not an error.

`proto/quote.proto` is the contract. We test your service with our own
client, built from that file as it is in this repository. You may add
fields and messages. Do not remove, rename, renumber or retype the 2 RPCs
or any existing field, in the requests or in the responses. If you want a
better type for money than a double, add a new field next to the existing
one and fill both.

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
2. Weight break: each break starts at its own minimum weight and ends just
   below the next break's minimum. `normal` is under 45 kg, `45` is 45 kg up
   to but not including 100 kg, and so on. `500` has no upper limit. Start
   with the break that contains the chargeable weight.
   A higher break can still be cheaper. To compare, price the higher break
   at its own minimum weight, not at the chargeable weight. If that total is
   lower, use the higher break. This is called as-agreed rating.
3. Minimum charge: total price is never below `min_charge`.
4. Validity: a rate sheet row applies only if `shipping_date` falls inside
   its window.
5. No applicable rate for an airline means no offer for that airline.

The sample data has rough edges on purpose. Where these rules do not settle a
case, decide, and write the decision in `SPEC.md`.

### Worked example

Shipment FRA to JFK, 80 kg, 120 x 80 x 60 cm, shipping 2026-02-10.

Volumetric weight is 120 x 80 x 60 / 6000 = 96 kg, so chargeable weight is
96 kg. Take the LH row from the CSV sample under "Rate sheets" above. 96 kg
falls in the 45 break: 96 kg x 3.80 = 364.80 EUR. The 100 break, priced at
its minimum weight, is 100 kg x 3.40 = 340.00 EUR, which is cheaper. Offer:
LH, 340.00 EUR, break 100.

With all 4 sample sheets ingested, the same request yields 4 offers:

| Airline | Total  | Currency | Break |
|---------|--------|----------|-------|
| LH      | 340.00 | EUR      | 100   |
| AF      | 365.00 | EUR      | 100   |
| EK      | 320.00 | USD      | 100   |
| QR      | 360.00 | USD      | 100   |

A second shipment on the same lane and date, 75 kg, 10 x 10 x 10 cm
(chargeable weight 75 kg), does not land on the same break for every
airline:

| Airline | Total  | Currency | Break | Why                                   |
|---------|--------|----------|-------|---------------------------------------|
| LH      | 285.00 | EUR      | 45    | 75 x 3.80 = 285.00, the 100 break is 340.00 |
| AF      | 303.75 | EUR      | 45    | 75 x 4.05 = 303.75, the 100 break is 365.00 |
| EK      | 320.00 | USD      | 100   | 75 x 4.60 = 345.00, the 100 break is 100 x 3.20 = 320.00 |
| QR      | 322.50 | USD      | 45    | 75 x 4.30 = 322.50, the 100 break is 360.00 |

Minimum charge: a 5 kg, 20 x 20 x 20 cm shipment on the same lane and date
has a chargeable weight of 5 kg. For LH that is 5 kg x 4.10 (the `normal`
rate) = 20.50 EUR, which is below LH's `min_charge` of 90.00 EUR. The offer
is 90.00 EUR.

### Scope

- Both RPCs implementing the rules above, with input validation and
  sensible gRPC status codes.
- Storage kept simple. In-memory or SQLite is fine. What we look for is a
  clean seam: real persistence should be swappable in later without touching
  the rating logic.
- Tests for the parts that matter most. Start with the rating logic.
- The gRPC server starts with 1 documented command. The scaffold uses
  `make run`.

A 4 hour version is the rating logic with tests, ingestion that loads the
sample sheets, and a spec that says what you decided and what you cut.
Validation, persistence and the awkward edge cases are where extra hours
go. Cutting them with a note is fine. We prefer an unfinished submission
with a clear spec over a polished one that took 3 times the budget.

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

We read `SPEC.md` and the tests as closely as the code. Most of the grade
comes from 3 things: the rating logic, the data model, and how cleanly
storage is separated from rating. `AI_NOTES.md` is not a pass or fail item.
It tells us how you work. You do not need AI experience to pass.

### Language

The scaffold is Python and that is our stack. If you are stronger in
another language, implement the same `proto/quote.proto` in that language
instead: keep the 2 RPCs and every existing field, listen on port 50051,
and document the run command here. We grade the design and the rating logic,
not the language.

## Running the service

Needs Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```
make install   # create the venv and install dependencies
make test      # unit tests and gRPC tests
make run       # starts the server on :50051 (rates are kept in memory)
make lint      # ruff
make protos    # regenerate proto/*_pb2* after editing quote.proto
```

With the server running, the client in a second terminal loads the sample sheets and quotes the
README example:

```
uv run python -m quote_service.client ingest rate_sheets/*.csv
uv run python -m quote_service.client quote FRA JFK 80 120x80x60 2026-02-10
```

```
proto/quote.proto                          service and message definitions (+ generated code)
quote_service/server.py                    gRPC server: converts proto messages to and from the domain
quote_service/service.py                   ingest and quote use cases, input validation
quote_service/rates/rate.py                Rate: one rate sheet row
quote_service/rates/rate_sheet.py          CSV parsing and validation
quote_service/rates/rate_repository.py     storage interface and the in-memory store
quote_service/pricing/shipment.py          Shipment, Dimensions and Offer
quote_service/pricing/chargeable_weight.py chargeable weight
quote_service/pricing/offers.py            weight breaks, as-agreed rating, min charge
quote_service/client.py                    CLI client for manual testing
rate_sheets/                               sample data, one CSV per airline, one malformed
tests/                                     pytest, unit tests and an in-process server fixture
SPEC.md                                    decisions, acceptance criteria and cut scope
AI_NOTES.md                                notes on how I worked
```

Time spent: around 5 hours (see SPEC.md).

## What happens next

We grade every submission against the same rubric within 3 working days of
your pull request. If it passes, there is 1 technical interview of 75 minutes with one
of our tech leads. It has 3 parts. First you walk us through your submission
and its data model, and we ask questions. No AI tools in this part. Then you
extend it live the way you normally work (agent, editor, your call). Then we
discuss how the design would scale, again without AI tools. Have your
environment ready on your branch for that call. There is no other technical
round.
