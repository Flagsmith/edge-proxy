from flag_engine.identities.models import TraitModel
from pydantic import BaseModel, Field


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
