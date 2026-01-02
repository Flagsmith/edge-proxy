from typing import Union

from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError


TraitValue = Union[str, int, float, bool, None]


class TraitModel(BaseModel):
    trait_key: str
    trait_value: TraitValue = None

    @field_validator("trait_value")
    @classmethod
    def validate_trait_value_length(cls, v: TraitValue) -> TraitValue:
        if isinstance(v, str) and len(v) > 2000:
            raise PydanticCustomError(
                "string_too_long",
                "String should have at most 2000 characters",
                {"max_length": 2000, "actual_length": len(v)},
            )
        return v


class IdentityWithTraits(BaseModel):
    identifier: str
    traits: list[TraitModel] = Field(default_factory=list)

    def __str__(self):
        return "identifier:%s|traits:%s" % (
            self.identifier,
            ",".join([f"{t.trait_key}={str(t.trait_value)}" for t in self.traits]),
        )

    def __hash__(self):
        return hash(str(self))
