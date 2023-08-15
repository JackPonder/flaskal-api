from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelCaseSchema(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        alias_generator=to_camel,
        populate_by_name=True
    )
