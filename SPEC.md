# SPEC

## Problem understanding

The service should provide quotes for air shipments based on chargeable weight
(max of actual weight and H x W x L / 6000), origin, and destination, on
specific date. The airline has a rate sheet with rows per origin, destination,
and weight breaks. Chargeable weight break can be:

- normal: weight < 45 kg
- 45: 45 kg <= weight < 100 kg
- 100: 100 kg <= weight < 300 kg
- 300: 300 kg <= weight < 500 kg
- 500: weight >= 500 kg

A higher break can be cheaper, but it should be checked against the break's
minimum weight and not the chargeable weight. The total price can never be
lower than min_charge. The weight break should also be returned per line, and
can be different for each offer. The service should return one row per airline
that has a matching offer. The offers can have different currencies.

The rate sheets are provided by the airline, and include origin/destination
combinations, validity dates, currency, and the rates.

Fuzzy rules:

- One of the example rate sheets has overlapping validity windows and there's
  no mention of what to do in this case. It does say "one row per lane and
  validity window" which technically makes the sheet correct because they are
  different validity windows. It's not clear how to handle this though, for
  example if we should reject the rate sheet for that lane, use the narrowest
  window (which would also be tricky and have lots of edge cases), assume the
  lowest or highest price, etc.
- It's not clear what would happen if a new rate sheet is sent for the same
  airline. It could mean that we completely replace the rates, and if there
  are date ranges not covered by the new sheet we reject the offers. Or it
  could mean that if there are date gaps, we still look into the previous
  sheets.
- The offers result order is not mentioned. From the 2 examples in the README,
  it seems like the results are ordered by currency (alphabetical) and Total
  (increasing). But that's an assumption based on a very limited set of
  examples.
- All the examples and documentation have integer for weight in kg and
  dimensions in cm, but the proto types are double, and it's not clear whether
  we should use decimals and if there is any kind of rounding. It's also not
  clear whether zero-value weights and dimensions should be accepted.
- It's not clear whether all the weight breaks should always be informed on
  the rate sheets, or if there can be some missing, and what to do in that
  case. The malformed CSV, for example, doesn't have the 500 break, and it's
  not clear whether we should completely reject it, or use the 300 as the last
  break.
- I consider the date handling fuzzy, because in a real-world application the
  time zone would be important and cause a quote to fall on different validity
  windows.
- No upper limit for the 500 break is clear, but there's no mention of a
  maximum weight, which would be reasonable to avoid input errors.
- There's no mention of what format the airport field has in the README. But
  in the proto file it's more specific: // IATA airport code, e.g. FRA
- There's also no mention of which currency codes the service should accept.
- All the examples have one airline per CSV, but it's not clear if this is
  always the case

## Design decisions

- I decided to use Python even though I'm not proficient in it to use the
  opportunity to practice and learn more
- All the calculations are split into specific files with pure functions, and
  the service has the glue code to connect it to the gRPC handlers
- When ingesting the rates, multiple errors are returned instead of stopping
  on the first, except if the header itself is invalid
- No extra dependencies were added, for example for validation
- `Decimal` and `date` types are used inside the service, and converted at the
  gRPC boundary
- Storage is in-memory but with a clear boundary and an interface so it can be
  easily replaced
- The rule to check which rates match the shipment date was done in the
  repository, because in a real application there will potentially be
  thousands of different rates, and already filtering on the database would be
  faster and save memory

## Acceptance criteria

- Given the README worked examples (FRA-JFK on 2026-02-10, all 4 sample
  sheets), the offers match the README tables exactly
- Given a 100 kg shipment FRA-JFK on 2026-02-10, LH quotes 340.00 EUR at the
  100 break (a weight on a break minimum belongs to that break)
- Given a 96 kg chargeable shipment CDG-JFK on 2026-03-01, AF quotes 300.00
  EUR at the 100 break (when validity windows overlap the cheapest one wins)
- Given the QR sheet, a FRA-JFK quote returns a QR offer on 2026-01-15 and
  2026-02-28, and no offer on 2026-03-01 (both window ends are inclusive)
- Given a 96 kg chargeable shipment CDG-JFK on 2027-01-01, an empty response
  with status OK is returned
- Given a 5 kg, 20 x 20 x 20 cm shipment FRA-JFK on 2026-02-10, LH quotes its
  min_charge of 90.00 EUR (the total is never below min_charge)
- Given all 4 sample sheets, a 96 kg chargeable shipment FRA-JFK on 2026-03-01
  gets offers from LH, AF and EK, and none from QR (QR has no rate for this
  date)
- Given rate_sheets/malformed/XX.csv, ingestion fails with INVALID_ARGUMENT
  and "header - missing columns: rate_500". With rate_500 added, it fails
  with:
  - line 3 - invalid origin: FRANKFURT
  - line 4 - valid_to must be >= valid_from
  - line 5 - rate_normal must be > 0
  - line 6 - rate_45 is required
- Given a 0 kg shipment FRA-JFK on 2026-02-10, LH quotes its min_charge of
  90.00 EUR
- Given a -10 kg, the quote fails with INVALID_ARGUMENT and "weight must be >=
  0"

## Edge cases

- The sample data for AF has an overlap in the validity windows. I have
  decided to calculate both and return the lowest calculated price, but it
  could also be the case that we would choose the innermost range always, or
  reject the rate sheet.
- Weight is double in the proto but all the examples are whole numbers. I
  decided to round the weight up to the next whole kg, also when calculating
  the chargeable weight. I left the type as Decimal so that it can be easily
  changed.
- Dimensions are also double and the examples are whole numbers. I decided to
  round it up to the nearest whole cm. I left the type as Decimal so that it
  can be easily changed.
- The rate sheets only have examples for USD and EUR, so I allow those and
  reject everything else
- If a rate is missing, do we assume the lower rate, higher rate, or reject?
  Line 6 has rate_45 missing, and it's not clear whether this means it's the
  same as normal, or if it's a mistake. I decided to require all rates to be
  passed. To consider a lower rating we would need to find the first break
  before the first one that has a rate, and also consider what to do if the
  normal break has no rate. So validating seems reasonable, but possibly
  doesn't reflect real world usage.
- There is no mention of 0 kg weight and/or dimensions. If the chargeable
  weight is 0, I decided to accept it and apply the minimum charge.
- I order the results by currency and then total because it matches the
  examples in the README, but that's not mentioned.
- If multiple breaks have the same final price, I return the lowest one.

## Cut scope

- I always replace the rate sheets with the latest version. In a real
  application, I would keep all rates, also past ones marked as inactive, so
  that the data can be used for logging and debugging purposes in case there
  is an issue with a past request. I cut it because it wasn't mentioned, and
  the rules around rate sheets are fuzzy.
- Probably it would make sense to get the currency on the request, and convert
  to the consumer's currency, so they can directly compare prices. Then there
  would be other things to consider such as VAT. I cut it because it wasn't
  mentioned.
- For validating the airport code I only check if it has 3 uppercase
  characters, but of course in a real application it would make sense to store
  the full list. I cut it because I don't know if the service should return
  rates for all airports, or if there should be an allow list.
- For the currencies I only check if it's EUR or USD. I don't know which
  currencies the service should support.
- I didn't add any kind of type validation such as with Pydantic, because I
  felt this would be overkill for a challenge.
- Defining the weight breaks as an array/list rather than named "rate_x"
  fields could make the calculations potentially simpler
- The server assumes one CSV per airline, and I didn't add validation to check
  because the rule is fuzzy
- I didn't add any kind of database. My first idea was to use Postgres and
  Docker Compose for local testing, but it would add too much complexity.

## Time spent

Around 5 hours. Since I haven't used Python in a while, I also took the chance
to practice but that also made me less productive than usual.
