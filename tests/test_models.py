from src.models import IdentityWithTraits


def test_identity_with_traits_str():
    # Given
    identifier = "foo"
    traits = [
        {"trait_key": "foo", "trait_value": "bar"},
        {"trait_key": "age", "trait_value": 21},
        {"trait_key": "is_cool", "trait_value": True},
    ]

    expected = "identifier:foo|traits:foo=bar,age=21,is_cool=True"

    # When
    identity_with_traits = IdentityWithTraits.parse_obj(
        {"identifier": identifier, "traits": traits}
    )

    # Then
    assert str(identity_with_traits) == expected


def test_identity_with_traits_hash():
    # Given
    identifier = "foo"
    traits = [
        {"trait_key": "foo", "trait_value": "bar"},
        {"trait_key": "age", "trait_value": 21},
        {"trait_key": "is_cool", "trait_value": True},
    ]

    expected = hash("identifier:foo|traits:foo=bar,age=21,is_cool=True")

    # When
    identity_with_traits = IdentityWithTraits.parse_obj(
        {"identifier": identifier, "traits": traits}
    )

    # Then
    assert hash(identity_with_traits) == expected
