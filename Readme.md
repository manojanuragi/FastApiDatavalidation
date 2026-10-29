# Library Book API: Dataclass vs Pydantic

A small FastAPI project that sends the same book data to different Python model types and shows how each one behaves. It compares a standard Python **dataclass**, a **Pydantic BaseModel** and a **Pydantic dataclass** on validation, type coercion, immutability and serialization.

## Project Structure

```
library-api/
├── main.py            # FastAPI app and endpoints
├── models.py          # Book model in different forms
├── test_main.py       # 10 pytest tests
├── books.json         # 10 sample records (some deliberately invalid)
├── requirements.txt
└── README.md
```

## Models

| Model | Type | Purpose |
|---|---|---|
| `BookDataclass` | Standard `@dataclass` | No automatic validation; only the ISBN length is checked by hand in `__post_init__` |
| `BookPydantic` | Pydantic `BaseModel` | Automatic validation with `Field()` limits and a `@field_validator` that tidies the title |
| `BookPydanticStrict` | `BaseModel` + `ConfigDict(strict=True)` | Same rules, but no type conversion allowed |
| `BookFrozen` | `BaseModel` + `ConfigDict(frozen=True)` | Fields cannot be changed after creation |
| `BookPydanticDataclass` | `@pydantic.dataclasses.dataclass` | Dataclass syntax with Pydantic validation |

Book fields: `title`, `author`, `isbn` (13 characters), `price` (above 0, up to 10000), `year` (1450 to 2026), `tags` (optional list).

## Setup

Requires Python 3.11 or newer.

```bash
pip install -r requirements.txt
```

## Run the API

```bash
uvicorn main:app --reload
```

Open Swagger UI at **http://127.0.0.1:8000/docs**

## Endpoints

| Method | Path | What it does |
|---|---|---|
| POST | `/dataclass/books` | Creates a book with the standard dataclass |
| POST | `/pydantic/books` | Creates a book with the Pydantic BaseModel |
| POST | `/pydantic-strict/books` | Creates a book with the strict Pydantic model |
| POST | `/pydantic-dataclass/books` | Creates a book with the Pydantic dataclass |
| POST | `/compare` | Sends one input to every model and returns the results side by side |
| POST | `/frozen-demo` | Tries to change a frozen model and returns the error |

## Example Request

`POST /compare`

```json
{
  "title": "clean code",
  "author": "Robert Martin",
  "isbn": "9780132350884",
  "price": "29.99",
  "year": 2008
}
```

Result (shortened):

```json
{
  "dataclass":          { "accepted": true,  "price_type": "str" },
  "pydantic":           { "accepted": true,  "price_type": "float" },
  "pydantic_strict":    { "accepted": false, "errors": ["Input should be a valid number"] },
  "pydantic_dataclass": { "accepted": true,  "price_type": "float" }
}
```

## Comparison of Behaviour

| Behaviour | Dataclass | Pydantic BaseModel | Pydantic dataclass |
|---|---|---|---|
| Type checking at runtime | No | Yes | Yes |
| Price sent as `"29.99"` | Kept as `str` | Converted to `float` (rejected in strict mode) | Converted to `float` |
| Negative price | Accepted | Rejected (422) | Rejected (422) |
| ISBN of wrong length | Rejected (manual check) | Rejected (422) | Rejected (422) |
| Custom rules | Written by hand in `__post_init__` | `Field()` and `@field_validator` | `Field()` |
| Frozen / immutable | `frozen=True` | `ConfigDict(frozen=True)` | `frozen=True` |
| Convert to dict | `asdict()` | `model_dump()` | `asdict()` |
| Schema in Swagger docs | No | Yes | Yes |

## Changing a Rule

Validation rules live in `models.py`. For example, to lower the maximum price, edit this line in `BookPydantic`:

```python
price: float = Field(gt=0, le=10000)   # change 10000 to 500
```

After saving, a price of `600` sent to `/compare` is rejected by the Pydantic BaseModel (and its strict and frozen versions), while the standard dataclass still accepts it, because it has no price check.

## Run the Tests

```bash
pytest -v
```

Expected result: `10 passed`

| Test | What it checks |
|---|---|
| `test_pydantic_accepts_valid_book` | Valid input is accepted and the title is tidied |
| `test_pydantic_converts_string_price` | `"29.99"` becomes a float |
| `test_dataclass_keeps_string_price` | The dataclass keeps `"29.99"` as a string |
| `test_strict_mode_rejects_string_price` | Strict mode returns 422 |
| `test_pydantic_rejects_negative_price` | Pydantic returns 422 for a negative price |
| `test_dataclass_accepts_negative_price` | The dataclass accepts a negative price |
| `test_dataclass_post_init_rejects_short_isbn` | The manual `__post_init__` check works |
| `test_pydantic_dataclass_validates_year` | The Pydantic dataclass rejects a negative year |
| `test_frozen_model_cannot_change` | A frozen model cannot be changed |
| `test_compare_shows_differences` | `/compare` shows all the differences together |

## Key Takeaway

A standard dataclass is a simple data container: it trusts whatever it is given. Pydantic checks and converts data at runtime, which makes it the safer choice for API input. A Pydantic dataclass gives you that validation while keeping the familiar dataclass syntax.

## Tech Stack

Python, FastAPI, Pydantic v2, Uvicorn, Pytest, HTTPX