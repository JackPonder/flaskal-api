from pydantic import AfterValidator
from typing import Annotated


def validate_not_empty(value: str) -> str:
    value = value.strip()
    if not len(value):
        raise ValueError("Value must not be blank")
    
    return value


NonEmptyString = Annotated[str, AfterValidator(validate_not_empty)]
