from src.cache import CacheService

api_url = "https://localhost/api/v1"
api_token = "test_token"
api_keys = ["test_env_key_1", "test_env_key2"]


def test_refresh_makes_correct_http_call(mocker):
    # Given
    mocked_session = mocker.patch("src.cache.requests.Session")
    cache_service = CacheService(api_url, api_token, api_keys)

    # When
    cache_service.refresh()
    # Then
    mocked_session.return_value.get.assert_has_calls(
        [mocker.call(f"{api_url}/environments/{api_keys[0]}/document/")],
        [mocker.call(f"{api_url}/environments/{api_keys[1]}/document/")],
    )


def test_initializing_cache_service_sets_the_authorization_header(mocker):
    # Given
    mocked_session = mocker.MagicMock()
    mocker.patch("src.cache.requests.Session", return_value=mocked_session)

    # When
    CacheService(api_url, api_token, api_keys)
    # Then
    mocked_session.headers.update.assert_called_once_with(
        {"Authorization": f"Token {api_token}"}
    )


def test_get_environment_works_correctly(mocker):
    # Given
    cache_service = CacheService(api_url, api_token, api_keys)
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
