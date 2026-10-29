from dataclasses import asdict

from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

from models import (
    BookDataclass,
    BookFrozen,
    BookPydantic,
    BookPydanticDataclass,
    BookPydanticStrict,
)
app = FastAPI(title="Library Book API: Dataclass vs Pydantic")

@app.post("/dataclass/books")
def create_dataclass_book(data: dict):
    # FastAPI gives us a raw dict; the dataclass does no type checking
    try:
        book = BookDataclass(**data)
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    result = asdict(book)
    result["price_type"] = type(book.price).__name__
    return result
@app.post("/pydantic/books", status_code=201)
def create_pydantic_book(book: BookPydantic):
    # FastAPI validates the body with Pydantic before this runs
    result = book.model_dump()
    result["price_type"] = type(book.price).__name__
    return result
@app.post("/pydantic-strict/books", status_code=201)
def create_strict_book(book: BookPydanticStrict):
    return book.model_dump()

@app.post("/pydantic-dataclass/books", status_code=201)
def create_pydantic_dataclass_book(book: BookPydanticDataclass):
    result = asdict(book)
    result["price_type"] = type(book.price).__name__
    return result

def _try(model, data):
    try:
        obj = model(**data)
        values = obj.model_dump() if hasattr(obj, "model_dump") else asdict(obj)
        return {"accepted": True, "price_type": type(obj.price).__name__, "data": values}
    except (ValidationError, TypeError, ValueError) as e:
        errors = e.errors() if isinstance(e, ValidationError) else str(e)
        return {"accepted": False, "errors": errors}


@app.post("/compare")
def compare(data: dict):
    # Same input, three model types, side by side
    return {
        "dataclass": _try(BookDataclass, data),
        "pydantic": _try(BookPydantic, data),
        "pydantic_strict": _try(BookPydanticStrict, data),
        "pydantic_dataclass": _try(BookPydanticDataclass, data),
    }
@app.post("/frozen-demo")
def frozen_demo(book: BookFrozen):
    try:
        book.price = 1.0
        return {"changed": True}
    except ValidationError as e:
        return {"changed": False, "error": e.errors()[0]["type"]}