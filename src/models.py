from flag_engine.identities.models import TraitModel
from pydantic import BaseModel, Field


class IdentityWithTraits(BaseModel):
    identifier: str
    traits: list[TraitModel] = Field(default_factory=list)
