from typing import Any
from flag_engine.engine import ContextValue
from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError


class IdentityWithTraits(BaseModel):
    identifier: str
    traits: dict[str, ContextValue] = Field(default_factory=dict)

    @field_validator("traits", mode="before")
    @classmethod
    def convert_traits_list_to_dict(cls, v: Any) -> dict[str, ContextValue]:
        """Convert legacy list format to dict."""
        if isinstance(v, list):
            return {trait["trait_key"]: trait["trait_value"] for trait in v}
        return v

    @field_validator("traits")
    @classmethod
    def validate_trait_value_length(
        cls, v: dict[str, ContextValue]
    ) -> dict[str, ContextValue]:
        """Enforce 2000 char limit on trait values."""
        for key, value in v.items():
            if isinstance(value, str) and len(value) > 2000:
                raise PydanticCustomError(
                    "string_too_long",
                    "String should have at most 2000 characters",
                    {"max_length": 2000, "actual_length": len(value)},
                )
        return v

    def __str__(self):
        return "identifier:%s|traits:%s" % (
            self.identifier,
            ",".join([f"{k}={str(v)}" for k, v in self.traits.items()]),
        )

    def __hash__(self):
        return hash(str(self))
