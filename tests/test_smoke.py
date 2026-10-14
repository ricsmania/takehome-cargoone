"""Proves the server boots and answers."""

from proto import quote_pb2


def test_empty_server_answers_with_no_offers(stub):
    # given a booted server with nothing ingested
    request = quote_pb2.GetQuoteRequest(origin="FRA", destination="JFK", weight_kg=80,
                                        shipping_date="2026-02-10")

    # when a quote is requested
    response = stub.GetQuote(request)

    # then the answer is empty, not an error
    assert list(response.offers) == []
