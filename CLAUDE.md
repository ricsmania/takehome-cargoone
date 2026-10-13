# CLAUDE.md

gRPC service for the cargo.one take-home. It ingests airline rate sheets (CSV) and quotes air cargo
shipments. `README.md` is the brief. `SPEC.md` holds the decisions on every rule the README leaves
open. When the code and SPEC.md disagree, stop and ask. Don't silently pick one.

## Commands

Run `make lint` and `make test` before calling any change done. CI runs both.

## Hard constraints

- `proto/quote.proto` is a fixed contract. The graders' client is built from the original file.
  You may add new fields and messages. Never remove, rename, renumber or retype an existing RPC or
  field. To use a better money type, add a field next to the `double` and fill both.
- Don't hand-edit `proto/*_pb2*.py` or `*.pyi`. Change `quote.proto` and run `make protos`.
- The rating logic must not import storage or gRPC. It takes rate rows and a shipment and returns
  offers. Keep storage behind an interface so SQLite or another store can replace the in-memory one
  without touching rating. The rubric weighs this separation, the rating logic and the data model
  most heavily.
- Use `Decimal` for weights and money inside the service. Convert to and from `double` only at the
  gRPC boundary. Floats make boundary tests (45, 100, 300, 500 kg) flaky.
- Don't add dependencies without asking.

## Domain rules (README, settled)

- Chargeable weight = max(actual kg, L x W x H cm / 6000).
- The break is chosen by chargeable weight. Each break is named after its minimum:
  `normal` < 45 kg; `45`: 45 <= w < 100; `100`: 100 <= w < 300; `300`: 300 <= w < 500;
  `500`: w >= 500.
- As-agreed rating: start with the break that contains the weight, then price each higher break at
  its own minimum weight and take the cheapest total.
- The total is never below `min_charge`.
- `valid_from` and `valid_to` are inclusive. A row applies only if `shipping_date` falls inside its
  window.
- One offer per airline that has an applicable rate. No applicable rate means no offer, not an error.
  Offers keep the sheet's currency and are never converted.

Turn the README worked examples into tests.

## Project decisions (SPEC.md)

Read SPEC.md before changing behaviour. In summary:

- Overlapping validity windows for one airline and lane (AF CDG-JFK in March): price every matching
  row and return the cheapest.
- Re-ingesting an airline replaces all of that airline's rates.
- Every rate column is required. A missing break rejects the sheet.
- Currencies and airport codes are checked against allowlists.
- A weight of 0 is valid and gets `min_charge`. A negative weight is rejected.
- `rate_sheets/malformed/XX.csv` must fail ingestion with line-numbered errors (see the acceptance
  criteria in SPEC.md). Its header also lacks `rate_500`.

If a new ambiguity comes up, propose a decision and add it to SPEC.md. Don't bury it in code.

## Code and tests

- Python 3.12, ruff, 100-character lines. Follow the scaffold style: type hints, module docstrings,
  and few comments.
- Tests use given/when/then comments (see `tests/test_smoke.py`). `tests/conftest.py` provides a
  `stub` fixture backed by an in-process server. Unit-test rating as pure functions first, then
  cover the RPCs through `stub`.
- Turn each SPEC.md acceptance criterion into a test. Test the edges of every break.
- gRPC errors: invalid input → `INVALID_ARGUMENT` with a readable message (line number and field for
  CSV errors). No offers → an empty response with status OK.

## Working with the author

The author has to walk interviewers through this code without AI tools, so:

- Don't write or edit `AI_NOTES.md` or the `SPEC.md`. If there are changes that should be made in SPEC.md, tell the author so they do it.
- Prefer plain, explicit code over clever abstractions. Make small changes and explain the reasoning
  for each one.
- When in doubt, ask instead of making assumptions.
- Don't commit or push unless asked. Work goes on a `ricardo-smania` branch and a PR into `main`.
