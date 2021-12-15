from typing import Any, List

from pydantic import BaseModel


class Traits(BaseModel):
    trait_key: str
    trait_value: Any


class IdentityWithTraits(BaseModel):
    identifier: str
    traits: List[Traits] = []
