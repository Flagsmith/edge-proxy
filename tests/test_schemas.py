import pytest
from marshmallow import ValidationError

from src.constants import TRAIT_STRING_VALUE_MAX_LENGTH
from src.schemas import APITraitSchema


@pytest.mark.parametrize("trait_value", (1, "some string", 12.34))
def test_api_trait_schema_valid_data(trait_value):
    # Given
    schema = APITraitSchema()
    data = {"trait_key": "foo", "trait_value": trait_value}

    # When
    trait_model = schema.load(data)

    # Then
    # no exception is raised
    assert trait_model.trait_key == data["trait_key"]
    assert trait_model.trait_value == data["trait_value"]


def test_api_trait_schema_invalid_data():
    # Given
    schema = APITraitSchema()
    data = {
        "trait_key": "foo",
        "trait_value": "a" * (TRAIT_STRING_VALUE_MAX_LENGTH + 1),
    }

    # When
    with pytest.raises(ValidationError):
        # Then validation error is raised
        schema.load(data)
