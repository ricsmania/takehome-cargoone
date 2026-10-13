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

- One of the example rate sheets has overlapping validity windows and there's no mention of what to do in this case. It does say "one row per lane and vality window" which technically makes the sheet correct because they are different validity windows. It's not clear how to handle this though, for example if we should reject the rate sheet for that lane, use the narrowest window (which would also be tricky and have lots of edge cases), assume the lowest or highest price, etc.
- It's not clear what would happen if a new rate sheet is sent for the same airline. It could mean that we completely replace the rates, and if there are date ranges not covered by the new sheet we reject the offers. Or it could mean that if there are date gaps, we still look into the previous sheets.
- The offers result order is not mentioned. From the 2 examples in the README, it seems like the results are ordered by currency (alphabetical) and Total (increasing). But that's an assumption based on a very limited set of examples.
- All the examples and documentation have integer for weight in kg and dimensions in cm, but the proto types are double, and it's not clear whether we should use decimals and how many.
- It's not clear whether all the weight breaks should always be informed, or if there can be some missing, and what to do in that case.
- I consider the date handling fuzzy, because in a real-world application the time zone would be important and cause a quote to fall on different validity windows.
- No upper limit for the 500 break is clear, but there's no mention of a maximum weight, which would be reasonable to avoid input errors.
- There's no mention of what format the airport field has in the README. But in the proto file it's more specific: // IATA airport code, e.g. FRA
- There's also no mention of currency validation.

## Design decisions

The choices you made and why: storage, how rating is structured, how errors
are reported, anything you changed in the proto.

## Acceptance criteria

Testable statements. "Given a 96 kg chargeable shipment FRA-JFK on 2026-02-10,
LH quotes 340.00 EUR at the 100 break" is one. "Quoting works" is not.

- Given a 96 kg chargeable shipment CDG-JFK on 2026-03-01, AF quotes 300.00 EUR at the 100 break
- Given rate_sheets/malformed/XX.csv, reject the loading with the following errors:
  - line 3 - invalid origin: FRANKFURT
  - Line 4 - valid_to must be >= valid_from
  - Line 5 - rate_normal must be > 0
  - Line 6 - rate_45 is required
- Given a quote with weight -10, reject with the error:
  - weight must be >= 0

## Edge cases

The awkward cases you found in the rules and in the sample data, and what
you decided for each.

- The sample data for AF has an overlap in the validity windows. I have decided to calculate both and return the lowest calculated price, but it could also be the case that we would choose the innermost range always, or reject the rate sheet.
- Weight is double in the proto but all the examples are int. I decided to use one decimal max and round the weight to 0.1 kg, also when calculating the chargeable weight.
- Dimensions are also double and the examples are int. I decided to round it to the nearest whole cm.
- The rate sheets only have examples for USD and EUR, so I allow those and reject everything else
- If a rate is missing, do we assume the lower rate, higher rate, or reject? Line 6 has rate_45 missing, and it's not clear whether this means it's the same as normal, or if it's a mistake.
  I decided to require all rates to be passed. To consider a lower rating we would need to find the first break before the first one that has a rate, and also consider what to do if the normal break has no rate. So validating seems reasonable, but possibly doesn't reflect real world usage.
- There is no mention of 0 kg weight. I assume this is a valid use case (for example a letter that rounds to 0 kg) and consider the minimum charge.
- I order the results by currency and then total because it matches the examples in the README, but that's not mentioned.

## Cut scope

What you left out on purpose, and why.

- I always replace the rate sheets with the latest version. In a real application, I would keep a history, so that the data can be used for logging and debugging purposes in case there is an issue with a past request.
- Probably it would make sense to get the currency on the request, and convert to the consumer's currency, so they can directly compare prices. Then there would be other things to consider such as VAT.
- I would store the airlines and airports on different tables and add FKs to the rates table, so that the data is consistent
- I didn't add any kind of dependency injection
- I didn't add any kind of type validation such as with Pydantic

## Time spent

Honest number of hours, roughly.

## TODO

Validate the date range
Validate airport code
Validate currencies
Validate that rates are positive
