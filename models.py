from dataclasses import dataclass, field

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.dataclasses import dataclass as pydantic_dataclass


# 1. Standard dataclass: no automatic validation or type conversion
@dataclass
class BookDataclass:
    title: str
    author: str
    isbn: str
    price: float
    year: int
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        # Only checks we write by hand are enforced
        if len(self.isbn) != 13:
            raise ValueError("isbn must be 13 characters")

# 2. Pydantic BaseModel: automatic validation and type conversion
class BookPydantic(BaseModel):
    title: str = Field(min_length=1)
    author: str
    isbn: str = Field(min_length=13, max_length=13)
    price: float = Field(gt=0, le=500)
    year: int = Field(ge=1450, le=2026)
    tags: list[str] = Field(default_factory=list)

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        return value.strip().title()
# Same model in strict mode: no type conversion allowed
class BookPydanticStrict(BookPydantic):
    model_config = ConfigDict(strict=True)

# Frozen model: fields cannot be changed after creation
class BookFrozen(BookPydantic):
    model_config = ConfigDict(frozen=True)

# 3. Pydantic dataclass: dataclass syntax with Pydantic validation
@pydantic_dataclass
class BookPydanticDataclass:
    title: str
    author: str
    isbn: str = Field(min_length=13, max_length=13)
    price: float = Field(gt=0)
    year: int = Field(ge=1450, le=2026)
    tags: list[str] = Field(default_factory=list)