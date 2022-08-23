import typing

from flag_engine.features.models import FeatureStateModel
from flag_engine.features.schemas import FeatureStateSchema
from flag_engine.identities.schemas import TraitSchema
from marshmallow import fields
from marshmallow import validates
from marshmallow import ValidationError

from .constants import ACCEPTED_TRAIT_VALUE_TYPES
from .constants import TRAIT_STRING_VALUE_MAX_LENGTH


class APIFeatureStateSchema(FeatureStateSchema):
    feature_state_value = fields.Method(serialize="serialize_feature_state_value")

    class Meta:
        exclude = (
            "multivariate_feature_state_values",
            "featurestate_uuid",
            "feature_segment",
            "django_id",
        )

    def serialize_feature_state_value(self, instance: FeatureStateModel) -> typing.Any:
        return instance.get_value(identity_id=self.context.get("identity_identifier"))


class APITraitSchema(TraitSchema):
    trait_value = fields.Method(
        serialize="serialize_trait_value", deserialize="deserialize_trait_value"
    )

    def serialize_trait_value(
        self, obj: typing.Any
    ) -> typing.Union[int, str, bool, float]:
        return obj.trait_value

    def deserialize_trait_value(
        self, trait_value: typing.Any
    ) -> typing.Union[int, str, bool, float]:
        if type(trait_value) not in ACCEPTED_TRAIT_VALUE_TYPES:
            trait_value = str(trait_value)
        return trait_value

    @validates("trait_value")
    def validate_trait_value_length(
        self, trait_value: typing.Union[int, str, bool, float]
    ):
        type_ = type(trait_value)
        if type_ == str and len(trait_value) > TRAIT_STRING_VALUE_MAX_LENGTH:
            raise ValidationError(
                f"Value string is too long. Must be less than "
                f"{TRAIT_STRING_VALUE_MAX_LENGTH} character"
            )
