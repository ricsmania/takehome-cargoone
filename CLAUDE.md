# CLAUDE.md

gRPC service for the cargo.one take-home: it ingests airline rate sheets and quotes air cargo
shipments.

## Where things are decided

- `README.md`: the brief, the domain rules and the worked examples.
- `SPEC.md`: the author's decisions on everything the README leaves open, and the acceptance
  criteria. Read it before changing behaviour.
- `proto/quote.proto`: the API contract. Its header comment says what may change.

When the code and these files disagree, stop and ask. When a new ambiguity comes up, propose a
decision to the author instead of burying it in code.

## Commands

Run `make lint` and `make test` before calling any change done. CI runs both. After editing the
proto, run `make protos`; never hand-edit the generated files.

## Constraints

- Rating logic must not import storage or gRPC. Storage stays behind an interface so another store
  can replace it without touching rating.
- Use `Decimal` for weights and money inside the service. Convert to and from `double` only at the
  gRPC boundary.
- Don't add dependencies without asking.

## Code and tests

- Follow the existing style: type hints, module docstrings, few comments, ruff at 100 characters.
- Tests use given/when/then comments. `tests/conftest.py` provides a `stub` fixture backed by an
  in-process server.
- Test each rule with unit tests of the module that applies it. API tests cover only wiring, status
  codes and a few end-to-end examples. `tests/test_smoke.py` only proves the server boots.
- Every acceptance criterion in SPEC.md has a test.

## Working with the author

The author has to walk interviewers through this code without AI tools, so:

- Don't write or edit `AI_NOTES.md` or `SPEC.md`. If there are inconsistensies, tell the author.
- Prefer plain, explicit code over clever abstractions. Make small changes and explain the reasoning
  for each one.
- When in doubt, ask instead of making assumptions.
- Don't commit or push unless asked. Work goes on the `ricardo-smania` branch and a PR into `main`.
