# SPEC

Fill this in before you write code. What it says matters more than when it
landed. Delete these prompts as you fill the sections in. Bullets are fine.

## Problem understanding

What the service does, in your own words. Which rules in the README are
sharp, which are fuzzy, and how you read the fuzzy ones.

The service should provide quotes for air shipments based on chargeable weight (max of actual weight and H x W x L / 6000), origin, and destination, on specific date. The airline has a rate sheet with rows per origin, destination, and weight breaks.
Chargeable weight break can be:

- normal: weight < 45 kg
- 45: 45 kg <= weight < 100 kg
- 100: 100 kg <= weight < 300 kg
- 300: 300 kg <= weight < 500 kg
- 500: weight >= 500 kg

A higher break can be cheaper, but it should be checked against the break's minimum weight and not the chargeable weight. The total price can never be lower than min_charge. The weight break should also be returned per line, and can be different for each offer.
The service should return one row per airline that has a matching offer. The offers can have different currencies.

The rate sheets are provided by the airline, and include origin/destination combinations, validity dates, currency, and the rates.

Fuzzy rules:

- One of the example rate sheets has overlapping date ranges, and there's no mention of what to do in this case, for example if we should reject the rate sheet for that origin/destination combination, use the narrowest window, assume the highest price, etc.
- It's not clear what would happen if a new rate sheet is sent for the same airline. It could mean that we completely replace the rates, and if there are date ranges not covered by the new sheet we reject the offers. Or it could mean that if there are date gaps, we still look into the previous sheets.
- It's not clear whether all the weight breaks should always be informed, or if there can be some missing, and what to do in that case.
- I consider the date handling fuzzy, because in a real-world application the time zone would be important and cause a quote to fall on different validity windows.
- There's no mention of validation for airport codes, or even if airport names are also acceptable.
- There's also no mention of currency validation.
- No upper limit for the 500 break is clear, but there's no mention of a maximum weight, which would be reasonable to avoid input errors.

## Design decisions

The choices you made and why: storage, how rating is structured, how errors
are reported, anything you changed in the proto.

## Acceptance criteria

Testable statements. "Given a 96 kg chargeable shipment FRA-JFK on 2026-02-10,
LH quotes 340.00 EUR at the 100 break" is one. "Quoting works" is not.

- Given rate_sheets/malformed/XX.csv, reject the loading with the following errors:
  - line 3 - invalid origin: FRANKFURT
  - Line 4 - valid_to must be >= valid_from
  - Line 5 - rate_normal must be > 0
  - Line 6 - rate_45 is required
- Any quotes with weight <= 0 are rejected

## Edge cases

The awkward cases you found in the rules and in the sample data, and what
you decided for each.

- The rate sheets only have examples for USD and EUR, and it's not clear how to validate
  I decided to have an allowlist of currencies
- Is there a list of airports we accept quotes to and from, and should we always match by airport code? The malformed CSV has a line with FRANKFURT instead of FRA.
  I decided to have an allowlist of airports
- If a rate is missing, do we assume the lower rate, higher rate, or reject? Line 6 has rate_45 missing, and it's not clear whether this means it's the same as normal, or if it's a mistake.
  I decided to require all rates to be passed. To consider a lower rating we would need to find the first break before the first one that has a rate, and also consider what to do if the normal break has no rate. So validating seems reasonable, but possibly doesn't reflect real world usage.

## Cut scope

What you left out on purpose, and why.
I always replace the rate sheets with the latest version. In a real application, I would keep a history, so that the data can be used for logging and debugging purposes.

## Time spent

Honest number of hours, roughly.

## TODO

Validate the date range
Validate airport code
Validate currencies
Validate that rates are positive
