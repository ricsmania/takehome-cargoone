.PHONY: install protos run test lint

install:
	uv sync

protos:
	uv run python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. --pyi_out=. proto/quote.proto

run:
	uv run python -m quote_service.server

test:
	uv run pytest

lint:
	uv run ruff check .
