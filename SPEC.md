# SPEC

Write this before the code. Commit it before the code too; we read the history.

Delete these prompts as you fill the sections in. Bullets are fine.

## Problem understanding

What the service does, in your own words. Which rules in the README are
sharp, which are fuzzy, and how you read the fuzzy ones.

## Design decisions

The choices you made and why. Storage, how rating is structured, where the
persistence seam is, how errors map to gRPC status codes, anything you changed
in the proto.

## Acceptance criteria

Testable statements. "Given a 96 kg chargeable shipment FRA-JFK on 2026-02-10,
LH quotes 340.00 EUR at the 100 break" is one. "Quoting works" is not.

## Edge cases

The awkward ones: volumetric vs actual weight, a higher break being cheaper,
the min charge, validity boundaries, overlapping windows, bad input.

## Cut scope

What you left out on purpose, and why.

## Time spent

Honest number of hours, roughly.
