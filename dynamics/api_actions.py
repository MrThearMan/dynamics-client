"""
Actions available in the web API.
Reference:
https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/actions
Documentation:
https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/use-web-api-actions
"""

from typing import List, Literal, Tuple, Dict, Any


__all__ = [
    "act",
]


class Actions:
    @staticmethod
    def send_email_from_template(
        template_id: str,
        context_table: str,
        context_row_id: str,
        sender_id: str,
        to_recipient_ids: List[str],
        cc_recipient_ids: List[str] = None,
        bcc_recipient_ids: List[str] = None,
    ) -> Tuple[str, Dict[str, Any]]:
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

        data = {
            "TemplateId": template_id,
            "Regarding": {"contactid": context_row_id, "@odata.type": f"Microsoft.Dynamics.CRM.{context_table}"},
            "Target": {
                # "regardingobjectid_contact@odata.bind": f"/contacts({contactid})",
                "email_activity_parties": parties,
                "@odata.type": "Microsoft.Dynamics.CRM.email",
            },
        }

        return "SendEmailFromTemplate", data

    @staticmethod
    def convert_quote_to_order(quote_id: str, select: List[str] = None) -> Tuple[str, Dict[str, Any]]:
        """Construct POST data to use in 'ConvertQuoteToSalesOrder' action

        :param quote_id: Quote to convert to an order.
        :param select: Attributes to retrieve from the new salesorder..
        :return: Tuple of the action name and POST data to send.
        """

        data = {
            "QuoteId": quote_id,
        }
        if select:
            data["ColumnSet"] = {"AllColumns": False, "Columns": select}
        else:
            data["ColumnSet"] = {"AllColumns": True}

        return "ConvertQuoteToSalesOrder", data

    @staticmethod
    def win_quote(quote_id: str) -> Tuple[str, Dict[str, Any]]:
        """Construct POST data to use in 'WinQuote' action

        :param quote_id: Quote to change to Won state.
        :return: Tuple of the action name and POST data to send.
        """

        data = {
            "QuoteClose": {
                "quoteid@odata.bind": f"/quotes({quote_id})",
                "@odata.type": "Microsoft.Dynamics.CRM.quoteclose",
            },
            "Status": -1,
        }

        return "WinQuote", data

    @staticmethod
    def close_quote(quote_id: str) -> Tuple[str, Dict[str, Any]]:
        """Construct POST data to use in 'CloseQuote' action

        :param quote_id: Quote to change to Canceled state.
        :return: Tuple of the action name and POST data to send.
        """

        data = {
            "QuoteClose": {
                "quoteid@odata.bind": f"/quotes({quote_id})",
                "@odata.type": "Microsoft.Dynamics.CRM.quoteclose",
            },
            "Status": -1,
        }

        return "CloseQuote", data

    @staticmethod
    def revise_quote(quote_id: str, select: List[str] = None) -> Tuple[str, Dict[str, Any]]:
        """Construct POST data to use in 'ReviseQuote' action

        :param quote_id: Quote to change to Draft state.
        :param select: Attributes to retrieve in the revised quote.
        :return: Tuple of the action name and POST data to send.
        """

        data = {"QuoteId": quote_id}

        if select:
            data["ColumnSet"] = select

        return "ReviseQuote", data

    @staticmethod
    def cancel_order(order_id: str) -> Tuple[str, Dict[str, Any]]:
        """Construct POST data to use in 'CancelSalesOrder' action

        :param order_id: Order to cancel.
        :return: Tuple of the action name and POST data to send.
        """

        data = {
            "OrderClose": {
                "salesorderid@odata.bind": f"/salesorders({order_id})",
                "@odata.type": "Microsoft.Dynamics.CRM.orderclose",
            },
            "Status": 4,  # No Money
        }

        return "CancelSalesOrder", data


act = Actions()
