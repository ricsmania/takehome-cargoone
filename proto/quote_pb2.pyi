from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class IngestRateSheetRequest(_message.Message):
    __slots__ = ("csv_content",)
    CSV_CONTENT_FIELD_NUMBER: _ClassVar[int]
    csv_content: str
    def __init__(self, csv_content: _Optional[str] = ...) -> None: ...

class IngestRateSheetResponse(_message.Message):
    __slots__ = ("rows_ingested",)
    ROWS_INGESTED_FIELD_NUMBER: _ClassVar[int]
    rows_ingested: int
    def __init__(self, rows_ingested: _Optional[int] = ...) -> None: ...

class Dimensions(_message.Message):
    __slots__ = ("length_cm", "width_cm", "height_cm")
    LENGTH_CM_FIELD_NUMBER: _ClassVar[int]
    WIDTH_CM_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_CM_FIELD_NUMBER: _ClassVar[int]
    length_cm: float
    width_cm: float
    height_cm: float
    def __init__(self, length_cm: _Optional[float] = ..., width_cm: _Optional[float] = ..., height_cm: _Optional[float] = ...) -> None: ...

class GetQuoteRequest(_message.Message):
    __slots__ = ("origin", "destination", "weight_kg", "dimensions", "shipping_date")
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_KG_FIELD_NUMBER: _ClassVar[int]
    DIMENSIONS_FIELD_NUMBER: _ClassVar[int]
    SHIPPING_DATE_FIELD_NUMBER: _ClassVar[int]
    origin: str
    destination: str
    weight_kg: float
    dimensions: Dimensions
    shipping_date: str
    def __init__(self, origin: _Optional[str] = ..., destination: _Optional[str] = ..., weight_kg: _Optional[float] = ..., dimensions: _Optional[_Union[Dimensions, _Mapping]] = ..., shipping_date: _Optional[str] = ...) -> None: ...

class Offer(_message.Message):
    __slots__ = ("airline", "currency", "chargeable_weight_kg", "weight_break", "rate_per_kg", "total_price")
    AIRLINE_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    CHARGEABLE_WEIGHT_KG_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_BREAK_FIELD_NUMBER: _ClassVar[int]
    RATE_PER_KG_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PRICE_FIELD_NUMBER: _ClassVar[int]
    airline: str
    currency: str
    chargeable_weight_kg: float
    weight_break: str
    rate_per_kg: float
    total_price: float
    def __init__(self, airline: _Optional[str] = ..., currency: _Optional[str] = ..., chargeable_weight_kg: _Optional[float] = ..., weight_break: _Optional[str] = ..., rate_per_kg: _Optional[float] = ..., total_price: _Optional[float] = ...) -> None: ...

class GetQuoteResponse(_message.Message):
    __slots__ = ("offers",)
    OFFERS_FIELD_NUMBER: _ClassVar[int]
    offers: _containers.RepeatedCompositeFieldContainer[Offer]
    def __init__(self, offers: _Optional[_Iterable[_Union[Offer, _Mapping]]] = ...) -> None: ...
