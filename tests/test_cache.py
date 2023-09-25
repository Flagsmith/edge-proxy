import requests

from src.cache import CacheService
from src.settings import Settings

settings = Settings(
    api_url="http://127.0.0.1:8000/api/v1",
    environment_key_pairs=[
        {"server_side_key": "ser.key1", "client_side_key": "test_env_key_1"},
        {"server_side_key": "ser.key2", "client_side_key": "test_env_key_2"},
    ],
)


def test_refresh_makes_correct_http_call(mocker):
    # Given
    mocked_session = mocker.patch("src.cache.requests.Session")
    mocked_datetime = mocker.patch("src.cache.datetime")
    cache_service = CacheService(settings)

    # When
    cache_service.refresh()
    # Then
    mocked_session.return_value.get.assert_has_calls(
        [
            mocker.call(
                f"{settings.api_url}/environment-document/",
                headers={
                    "X-Environment-Key": settings.environment_key_pairs[
                        0
                    ].server_side_key
                },
            )
        ],
        [
            mocker.call(
                f"{settings.api_url}/environment-document/",
                headers={
                    "X-Environment-Key": settings.environment_key_pairs[
                        1
                    ].server_side_key
                },
            )
        ],
    )
    assert cache_service.last_updated_at == mocked_datetime.now.return_value


def test_refresh_does_not_update_last_updated_at_if_any_request_fails(mocker):
    # Given
    mocked_session = mocker.patch("src.cache.requests.Session")
    mocked_session.return_value.get.side_effect = [
        mocker.MagicMock(),
        requests.exceptions.HTTPError(),
    ]
    cache_service = CacheService(settings)

    # When
    cache_service.refresh()

    # Then
    assert cache_service.last_updated_at is None


def test_get_environment_works_correctly(mocker):
    # Given
    cache_service = CacheService(settings)
    doc_1 = {"key1": "value1"}
    doc_2 = {"key2": "value2"}

    # patch the _fetch_document to populate the cache
    mocked_fetch_document = mocker.patch.object(
        cache_service, "fetch_document", side_effect=[doc_1, doc_2]
    )

    # When
    cache_service.refresh()

    # Next, test that get environment return correct document
    assert (
        cache_service.get_environment(settings.environment_key_pairs[0].client_side_key)
        == doc_1
    )
    assert (
        cache_service.get_environment(settings.environment_key_pairs[1].client_side_key)
        == doc_2
    )
    assert mocked_fetch_document.call_count == 2

    # Next, let's verify that any additional call to get_environment does not call fetch document
    cache_service.get_environment(settings.environment_key_pairs[0].client_side_key)
    cache_service.get_environment(settings.environment_key_pairs[1].client_side_key)
    assert mocked_fetch_document.call_count == 2
