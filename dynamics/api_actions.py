"""
Actions available in the web API.
Reference:
https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/actions
Documentation:
https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/use-web-api-actions
"""

from typing import List, Dict, Literal, Any, TYPE_CHECKING
from .enums import QuoteState

if TYPE_CHECKING:
    from .client import DynamicsClient


__all__ = ["Actions"]


class Actions:
    """Predefined Dynamics API actions."""

    def __init__(self, client: "DynamicsClient"):
        self.client = client

    def send_email_from_template(
        self,
        template_id: str,
        context_table: str,
        context_row_id: str,
        sender_id: str,
        to_recipient_ids: List[str],
        cc_recipient_ids: List[str] = None,
        bcc_recipient_ids: List[str] = None,
        **kwargs,
    ):
        """Construct POST data to use in SendEmailFromTemplate action.

        https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/sendemailfromtemplate

        :param template_id: Dynamics template GUID to use.
        :param context_table: What table to use in the context of the email.
        :param context_row_id: What row to select from the context table. This row's data can be used in
                               dynamically in the body of the email template.
        :param sender_id: Dynamics systemuser GUID that sends the email. Must have 'send-as' privilegde.
        :param to_recipient_ids: List of Dynamics contact GUIDS to add as to recipients.
        :param cc_recipient_ids: List of Dynamics contact GUIDS to add as cc recipients.
        :param bcc_recipient_ids: List of Dynamics contact GUIDS to add as bcc recipients.
        :return: Tuple of the action name and POST data to send.
        """

        def add_parties(parties_list: List[str], party_type: Literal[1, 2, 3, 4]):
            # Party Types:
            # Sender	        1	Specifies the sender.
            # ToRecipient	    2	Specifies the recipient in the To field.
            # CCRecipient	    3	Specifies the recipient in the Cc field.
            # BccRecipient	    4	Specifies the recipient in the Bcc field.
            return [
                {"partyid_systemuser@odata.bind": f"/contacts({contact})", "participationtypemask": party_type}
                for contact in parties_list
            ]

        parties = add_parties([sender_id], party_type=1)
        parties += add_parties(to_recipient_ids, party_type=2)
        if cc_recipient_ids:
            parties += add_parties(cc_recipient_ids, party_type=3)
        if bcc_recipient_ids:
            parties += add_parties(bcc_recipient_ids, party_type=4)

        self.client.reset_query()
        self.client.action = "SendEmailFromTemplate"

        data = {
            "TemplateId": template_id,
            "Regarding": {"contactid": context_row_id, "@odata.type": f"Microsoft.Dynamics.CRM.{context_table}"},
            "Target": {
                "regardingobjectid_contact@odata.bind": f"/contacts({context_row_id})",
                "email_activity_parties": parties,
                "@odata.type": "Microsoft.Dynamics.CRM.email",
            },
        }

        return self.client.POST(
            data=data,
            simplify_errors=kwargs.pop("simplify_errors", False),
            raise_separately=kwargs.pop("raise_separately", []),
        )

    def convert_quote_to_order(self, quote_id: str, select: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Converts quote to salesorder.

        :param quote_id: Quote to convert to an order.
        :param select: Attributes to retrieve from the new salesorder.
        :return: New salesorder.
        """

        self.client.reset_query()
        self.client.action = "ConvertQuoteToSalesOrder"

        data = {"QuoteId": quote_id, "ColumnSet": {"AllColumns": True}}

        if select:
            data["ColumnSet"] = {"AllColumns": False, "Columns": select}

        return self.client.POST(
            data=data,
            simplify_errors=kwargs.pop("simplify_errors", False),
            raise_separately=kwargs.pop("raise_separately", []),
        )

    def activate_quote(self, quote_id: str, select: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Change the state of the quote to active so it can be converted to a salesorder.

        :param quote_id: Quote to activate.
        :param select: Attributes to retrieve from the quote.
        :return: Activated quote.
        """

        self.client.reset_query()
        self.client.table = "quotes"
        self.client.row_id = quote_id
        if select:
            self.client.select = select

        return self.client.PATCH(
            data={"statecode": QuoteState.Active.value},
            simplify_errors=kwargs.pop("simplify_errors", False),
            raise_separately=kwargs.pop("raise_separately", []),
        )

    def win_quote(self, quote_id: str, **kwargs) -> None:
        """Win a quote, so it can be converted to a salesorder. Quote must be in the 'Active' state.

        :param quote_id: Quote to change to Won state.
        """

        self.client.reset_query()
        self.client.action = "WinQuote"

        data = {
            "QuoteClose": {
                "quoteid@odata.bind": f"/quotes({quote_id})",
                "@odata.type": "Microsoft.Dynamics.CRM.quoteclose",
            },
            "Status": -1,
        }

        self.client.POST(
            data=data,
            simplify_errors=kwargs.pop("simplify_errors", False),
            raise_separately=kwargs.pop("raise_separately", []),
        )

    def close_quote(self, quote_id: str, **kwargs) -> None:
        """Close quote as cancelled.

        :param quote_id: Quote to change to 'Canceled' state.
        """

        self.client.reset_query()
        self.client.action = "CancelSalesOrder"

        data = {
            "QuoteClose": {
                "quoteid@odata.bind": f"/quotes({quote_id})",
                "@odata.type": "Microsoft.Dynamics.CRM.quoteclose",
            },
            "Status": -1,
        }

        self.client.POST(
            data=data,
            simplify_errors=kwargs.pop("simplify_errors", False),
            raise_separately=kwargs.pop("raise_separately", []),
        )

    def revise_quote(self, quote_id: str, select: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Change quote back to draft state.

        :param quote_id: Quote to change to 'Draft' state.
        :param select: Attributes to retrieve in the revised quote.
        """

        self.client.reset_query()
        self.client.action = "ReviseQuote"

        data = {"QuoteId": quote_id}
        if select:
            data["ColumnSet"] = select

        return self.client.POST(
            data=data,
            simplify_errors=kwargs.pop("simplify_errors", False),
            raise_separately=kwargs.pop("raise_separately", []),
        )

    def delete_quote(self, quote_id: str, **kwargs) -> None:
        """Delete a quote.

        :param quote_id: Quote to delete.
        """

        self.client.reset_query()
        self.client.table = "quotes"
        self.client.row_id = quote_id
        self.client.DELETE(
            simplify_errors=kwargs.pop("simplify_errors", False),
            raise_separately=kwargs.pop("raise_separately", []),
        )

    def cancel_order(self, order_id: str, reason: int = None, **kwargs) -> None:
        """Construct POST data to use in 'CancelSalesOrder' action

        :param order_id: Order to cancel.
        :param reason: Reason to close salesorder. Default means 'No Money'.
        """

        self.client.reset_query()
        self.client.action = "CancelSalesOrder"

        if reason is None:
            reason = 4  # No Money

        data = {
            "OrderClose": {
                "salesorderid@odata.bind": f"/salesorders({order_id})",
                "@odata.type": "Microsoft.Dynamics.CRM.orderclose",
            },
            "Status": reason,
        }

        self.client.POST(
            data=data,
            simplify_errors=kwargs.pop("simplify_errors", False),
            raise_separately=kwargs.pop("raise_separately", []),
        )

    def delete_order(self, order_id: str, **kwargs) -> None:
        """Delete an order.

        :param order_id: Order to delete.
        """

        self.client.reset_query()
        self.client.table = "salesorders"
        self.client.row_id = order_id
        self.client.DELETE(
            simplify_errors=kwargs.pop("simplify_errors", False),
            raise_separately=kwargs.pop("raise_separately", []),
        )

    def calculate_quote_price(self, quote_id: str, **kwargs) -> None:
        """Calculate the price of a quote.

        :param quote_id: Quote to calculate the price for.
        """

        self.client.reset_query()
        self.client.action = "CalculatePrice"

        data = {
            "Target": {
                "quoteid": quote_id,
                "@odata.type": "Microsoft.Dynamics.CRM.quote",
            },
        }

        self.client.POST(
            data=data,
            simplify_errors=kwargs.pop("simplify_errors", False),
            raise_separately=kwargs.pop("raise_separately", []),
        )
