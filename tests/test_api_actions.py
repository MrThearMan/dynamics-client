import json
from unittest import mock

import pytest

from dynamics.api_actions import Actions
from dynamics.enums import QuoteState
from dynamics.test import ResponseMock, dynamics_client_response, dynamics_client_response_mirror
from dynamics.typing import Any, Dict, List, Optional


@pytest.mark.parametrize("cc,bcc", [[["cc1"], ["bcc1"]], [None, None]])
def test_api_actions__send_email_from_template(dynamics_client, cc: Optional[List[str]], bcc: Optional[List[str]]):
    api_functions = Actions(client=dynamics_client)

    with dynamics_client_response_mirror(dynamics_client, method="post"):
        result = api_functions.send_email_from_template(
            template_id="template_id",
            context_table="table",
            context_row_id="row_id",
            sender_id="sender_id",
            to_recipient_ids=["recipient1"],
            cc_recipient_ids=cc,
            bcc_recipient_ids=bcc,
        )

    expected_results = {
        "TemplateId": "template_id",
        "Regarding": {"contactid": "row_id", "@odata.type": "Microsoft.Dynamics.CRM.table"},
        "Target": {
            "regardingobjectid_contact@odata.bind": "/contacts(row_id)",
            "email_activity_parties": [
                {
                    "partyid_systemuser@odata.bind": "/contacts(sender_id)",
                    "participationtypemask": 1,
                },
                {
                    "partyid_systemuser@odata.bind": "/contacts(recipient1)",
                    "participationtypemask": 2,
                },
            ],
            "@odata.type": "Microsoft.Dynamics.CRM.email",
        },
    }

    if cc:
        expected_results["Target"]["email_activity_parties"].append(
            {
                "partyid_systemuser@odata.bind": "/contacts(cc1)",
                "participationtypemask": 3,
            },
        )

    if bcc:
        expected_results["Target"]["email_activity_parties"].append(
            {
                "partyid_systemuser@odata.bind": "/contacts(bcc1)",
                "participationtypemask": 4,
            },
        )

    assert dynamics_client.action == "SendEmailFromTemplate"
    assert result == expected_results


@pytest.mark.parametrize("select", [["select", "it"], None])
def test_api_actions__convert_quote_to_order(dynamics_client, select: Optional[List[str]]):
    api_functions = Actions(client=dynamics_client)

    with dynamics_client_response_mirror(dynamics_client, method="post"):
        result = api_functions.convert_quote_to_order(quote_id="quote_id", select=select)

    if select:
        expected_result = {"QuoteId": "quote_id", "ColumnSet": {"AllColumns": False, "Columns": select}}
    else:
        expected_result = {"QuoteId": "quote_id", "ColumnSet": {"AllColumns": True}}

    assert dynamics_client.action == "ConvertQuoteToSalesOrder"
    assert result == expected_result


@pytest.mark.parametrize("select", [["select", "it"], None])
def test_api_actions__activate_quote(dynamics_client, select: Optional[List[str]]):
    api_functions = Actions(client=dynamics_client)

    with dynamics_client_response_mirror(dynamics_client, method="patch"):
        result = api_functions.activate_quote(quote_id="quote_id", select=select)

    assert dynamics_client.table == "quotes"
    assert dynamics_client.row_id == "quote_id"
    if select:
        assert dynamics_client.select == select

    assert result == {"statecode": QuoteState.ACTIVE.value}


def test_api_actions__win_quote(dynamics_client):
    api_functions = Actions(client=dynamics_client)
    result: bytes = b""

    def capture_data(url: str, data: bytes, headers: Dict[str, Any]) -> ResponseMock:
        nonlocal result
        result = json.loads(data.decode())
        return ResponseMock(data=result, status_code=204)

    with mock.patch(
        "requests_oauthlib.oauth2_session.OAuth2Session.post",
        mock.MagicMock(side_effect=capture_data),
    ):
        api_functions.win_quote(quote_id="quote_id")

    assert dynamics_client.action == "WinQuote"
    assert result == {
        "QuoteClose": {
            "quoteid@odata.bind": "/quotes(quote_id)",
            "@odata.type": "Microsoft.Dynamics.CRM.quoteclose",
        },
        "Status": -1,
    }


def test_api_actions__close_quote(dynamics_client):
    api_functions = Actions(client=dynamics_client)
    result: bytes = b""

    def capture_data(url: str, data: bytes, headers: Dict[str, Any]) -> ResponseMock:
        nonlocal result
        result = json.loads(data.decode())
        return ResponseMock(data=result, status_code=204)

    with mock.patch(
        "requests_oauthlib.oauth2_session.OAuth2Session.post",
        mock.MagicMock(side_effect=capture_data),
    ):
        api_functions.close_quote(quote_id="quote_id")

    assert dynamics_client.action == "CloseQuote"
    assert result == {
        "QuoteClose": {
            "quoteid@odata.bind": f"/quotes(quote_id)",
            "@odata.type": "Microsoft.Dynamics.CRM.quoteclose",
        },
        "Status": -1,
    }


@pytest.mark.parametrize("select", [["select", "it"], None])
def test_api_actions__revise_quote(dynamics_client, select: Optional[List[str]]):
    api_functions = Actions(client=dynamics_client)

    with dynamics_client_response_mirror(dynamics_client, method="post"):
        result = api_functions.revise_quote(quote_id="quote_id", select=select)

    if select:
        expected_result = {"QuoteId": "quote_id", "ColumnSet": select}
    else:
        expected_result = {"QuoteId": "quote_id"}

    assert result == expected_result


def test_api_actions__delete_quote(dynamics_client):
    api_functions = Actions(client=dynamics_client)

    with dynamics_client_response(
        dynamics_client,
        session_response=ResponseMock(data=None, status_code=204),
        method="delete",
        client_response=None,
    ):
        api_functions.delete_quote(quote_id="quote_id")

    assert dynamics_client.table == "quotes"
    assert dynamics_client.row_id == "quote_id"


@pytest.mark.parametrize("reason", [1, None])
def test_api_actions__calculate_quote_price(dynamics_client, reason: int):
    api_functions = Actions(client=dynamics_client)
    result: bytes = b""

    def capture_data(url: str, data: bytes, headers: Dict[str, Any]) -> ResponseMock:
        nonlocal result
        result = json.loads(data.decode())
        return ResponseMock(data=result, status_code=204)

    with mock.patch(
        "requests_oauthlib.oauth2_session.OAuth2Session.post",
        mock.MagicMock(side_effect=capture_data),
    ):
        api_functions.calculate_quote_price(quote_id="quote_id")

    assert dynamics_client.action == "CalculatePrice"
    assert result == {
        "Target": {
            "quoteid": "quote_id",
            "@odata.type": "Microsoft.Dynamics.CRM.quote",
        },
    }


@pytest.mark.parametrize("reason", [1, None])
def test_api_actions__cancel_order(dynamics_client, reason: int):
    api_functions = Actions(client=dynamics_client)
    result: bytes = b""

    def capture_data(url: str, data: bytes, headers: Dict[str, Any]) -> ResponseMock:
        nonlocal result
        result = json.loads(data.decode())
        return ResponseMock(data=result, status_code=204)

    with mock.patch(
        "requests_oauthlib.oauth2_session.OAuth2Session.post",
        mock.MagicMock(side_effect=capture_data),
    ):
        api_functions.cancel_order(order_id="order_id", reason=reason)

    reason = reason if reason else 4

    assert dynamics_client.action == "CancelSalesOrder"
    assert result == {
        "OrderClose": {
            "salesorderid@odata.bind": f"/salesorders(order_id)",
            "@odata.type": "Microsoft.Dynamics.CRM.orderclose",
        },
        "Status": reason,
    }


def test_api_actions__delete_order(dynamics_client):
    api_functions = Actions(client=dynamics_client)

    with dynamics_client_response(
        dynamics_client,
        session_response=ResponseMock(data=None, status_code=204),
        method="delete",
        client_response=None,
    ):
        api_functions.delete_order(order_id="order_id")

    assert dynamics_client.table == "salesorders"
    assert dynamics_client.row_id == "order_id"
