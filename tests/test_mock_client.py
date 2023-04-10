import pytest


def test_mock_client__next_exception_before_exceptions_set(dynamics_client):
    with pytest.raises(TypeError, match="Cannot call 'next_exception' without setting exceptions first"):
        dynamics_client.next_exception


def test_mock_client__lengths_dont_match(dynamics_client):
    with pytest.raises(ValueError, match="Mismatching number of arguments given for MockResponse"):
        dynamics_client.with_responses(None).with_status_codes(100, 100)


def test_mock_client__too_few_responses(dynamics_client):
    dynamics_client.with_responses(None)
    dynamics_client.delete()

    with pytest.raises(ValueError, match="Ran out of responses on the MockClient"):
        dynamics_client.delete()


def test_mock_client__too_few_status_codes(dynamics_client):
    dynamics_client.internal.with_status_codes(204)
    dynamics_client.delete()

    with pytest.raises(ValueError, match="Ran out of status codes on the MockClient"):
        dynamics_client.delete()
