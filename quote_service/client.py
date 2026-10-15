"""Small CLI to poke a running server. Not part of the challenge; change it freely.

uv run python -m quote_service.client ingest rate_sheets/LH.csv
uv run python -m quote_service.client quote FRA JFK 80 120x80x60 2026-02-10
"""

import argparse
import sys
from pathlib import Path

import grpc

from proto import quote_pb2, quote_pb2_grpc


def _stub(target: str) -> quote_pb2_grpc.QuoteServiceStub:
    return quote_pb2_grpc.QuoteServiceStub(grpc.insecure_channel(target))


def ingest(stub: quote_pb2_grpc.QuoteServiceStub, path: Path) -> None:
    response = stub.IngestRateSheet(quote_pb2.IngestRateSheetRequest(csv_content=path.read_text()))
    print(f"{path.name}: {response.rows_ingested} rows ingested")


def quote(
    stub: quote_pb2_grpc.QuoteServiceStub,
    origin: str,
    destination: str,
    weight_kg: float,
    dims: str,
    shipping_date: str,
) -> None:
    length, width, height = (float(x) for x in dims.lower().split("x"))
    response = stub.GetQuote(
        quote_pb2.GetQuoteRequest(
            origin=origin,
            destination=destination,
            weight_kg=weight_kg,
            dimensions=quote_pb2.Dimensions(length_cm=length, width_cm=width, height_cm=height),
            shipping_date=shipping_date,
        )
    )
    if not response.offers:
        print("no offers")
    for offer in response.offers:
        print(
            f"{offer.airline}  {offer.total_price:>10.2f} {offer.currency}  "
            f"chargeable {offer.chargeable_weight_kg:g} kg  "
            f"break {offer.weight_break} @ {offer.rate_per_kg:.2f}/kg"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--target", default="localhost:50051")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ingest = sub.add_parser("ingest", help="ingest one or more rate sheet CSV files")
    p_ingest.add_argument("paths", nargs="+", type=Path)

    p_quote = sub.add_parser("quote", help="quote a shipment")
    p_quote.add_argument("origin")
    p_quote.add_argument("destination")
    p_quote.add_argument("weight_kg", type=float)
    p_quote.add_argument("dims", help="LxWxH in cm, e.g. 120x80x60")
    p_quote.add_argument("shipping_date", help="ISO 8601 date, e.g. 2026-02-10")

    args = parser.parse_args(argv)
    stub = _stub(args.target)
    try:
        if args.command == "ingest":
            for path in args.paths:
                ingest(stub, path)
        else:
            quote(
                stub, args.origin, args.destination, args.weight_kg, args.dims, args.shipping_date
            )
    except grpc.RpcError as err:
        print(f"{err.code().name}: {err.details()}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
