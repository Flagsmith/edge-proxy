from src.cache import CacheService

api_url = "https://localhost/api/v1"
server_side_keys = ["ser.key1", "ser.key2"]
api_keys = ["test_env_key_1", "test_env_key2"]


def test_refresh_makes_correct_http_call(mocker):
    # Given
    mocked_session = mocker.patch("src.cache.requests.Session")
    cache_service = CacheService(api_url, server_side_keys, api_keys)

    # When
    cache_service.refresh()
    # Then
    mocked_session.return_value.get.assert_has_calls(
        [
            mocker.call(
                f"{api_url}/environment-document/",
                headers={"X-Environment-Key": server_side_keys[0]},
            )
        ],
        [
            mocker.call(
                f"{api_url}/environment-document/",
                headers={"X-Environment-Key": server_side_keys[1]},
            )
        ],
    )


def test_get_environment_works_correctly(mocker):
    # Given
    cache_service = CacheService(api_url, server_side_keys, api_keys)
    doc_1 = {"key1": "value1"}
    doc_2 = {"key2": "value2"}

    # patch the _fetch_document to populate the cache
    mocked_fetch_document = mocker.patch.object(
        cache_service, "_fetch_document", side_effect=[doc_1, doc_2]
    )

    # When
    cache_service.refresh()

    # Next, test that get environment return correct document
    cache_service.get_environment(api_keys[0]) == doc_1
    cache_service.get_environment(api_keys[1]) == doc_2
    assert mocked_fetch_document.call_count == 2

    # Next, let's verify that any additional call to get_environment does not call fetch document
    cache_service.get_environment(api_keys[0])
    cache_service.get_environment(api_keys[1])
    assert mocked_fetch_document.call_count == 2
