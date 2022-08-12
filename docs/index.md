# Dynamics Web API Client

[![Coverage Status][coverage-badge]][coverage]
[![GitHub Workflow Status][status-badge]][status]
[![PyPI][pypi-badge]][pypi]
[![GitHub][licence-badge]][licence]
[![GitHub Last Commit][repo-badge]][repo]
[![GitHub Issues][issues-badge]][issues]
[![Downloads][downloads-badge]][pypi]
[![Python Version][version-badge]][pypi]

```shell
pip install dynamics-client
```

---

**Documentation**: [https://mrthearman.github.io/dynamics-client/](https://mrthearman.github.io/dynamics-client/)

**Source Code**: [https://github.com/MrThearMan/dynamics-client/](https://github.com/MrThearMan/dynamics-client/)

---

## Basic usage

```python
from dynamics import DynamicsClient, ftr

# Init the client:
client = DynamicsClient(...)

### Example GET request:

client.table = "accounts"

# Get only these columns for the account.
client.select = ["accountid", "name"]

# Filter to only the accounts that have been created on or after the
# given ISO date string, AND that have 200 or more employees.
client.filter = [
    ftr.on_or_after("createdon", "2020-01-01T00:00:00Z"),
    ftr.ge("numberofemployees", 200),
]

# Expand to the contacts (collection-values navigation property)
# on the account that have 'gmail.com' in their email address 1 OR 2.
# Get only the 'firstname', 'lastname' and 'mobilephone' columns for these contacts.
# Also expand the primary contact (single-valued navigation property).
# Get only the 'emailaddress1' column for the primary contact.
client.expand = {
    "contact_customer_accounts": {
        "select": ["firstname", "lastname", "mobilephone"],
        "filter": {
            ftr.contains("emailaddress1", "gmail.com"),
            ftr.contains("emailaddress2", "gmail.com"),
        }
    },
    "primarycontactid": {
        "select": ["emailaddress1"],
    },
}

result = client.get()

# [
#     {
#         "accountid": ...,
#         "name": ...,
#         "contact_customer_accounts": [
#             {
#                 "contactid": ...,  # id field is always given
#                 "firstname": ...,
#                 "lastname": ...,
#                 "mobilephone": ...
#             },
#             ...
#         ],
#         "primarycontactid": {
#             "contactid": ...,
#             "emailaddress1": ...
#         }
#     },
#     ...
# ]

### Example POST request

# IMPORTANT!!!
client.reset_query()

client.table = "contacts"

# Get only these columns from the created contact
client.select = ["firstname", "lastname", "emailaddress1"]

# The data to create the contact with. '@odata.bind' is used to link
# the contact to the given navigation property.
accountid = ...
data = {
    "firstname": ...,
    "lastname": ...,
    "emailaddress1": ...,
    "parentcustomerid_account@odata.bind": f"/accounts({accountid})"
}

result = client.post(data=data)

# {
#     "contactid": ...,
#     "firstname": ...,
#     "lastname": ...,
#     "emailaddress1": ...
# }


### Example PATCH request

client.reset_query()

client.table = "contacts"
client.row_id = result["contactid"]

data = {
    "firstname": ...,
    "lastname": ...,
}

result = client.patch(data=data)

# Return all rows on the updated contact,
# since no select statement was given
#
# {
#     ...
#     "contactid": ...,
#     "firstname": ...,
#     "lastname": ...,
#     ...
# }


### Example DELETE request

client.reset_query()

client.table = "contacts"
client.row_id = result["contactid"]

client.delete()
```


[ref-docs]: https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/query-data-web-api

[coverage-badge]: https://coveralls.io/repos/github/MrThearMan/dynamics-client/badge.svg?branch=main
[status-badge]: https://img.shields.io/github/workflow/status/MrThearMan/dynamics-client/Test
[pypi-badge]: https://img.shields.io/pypi/v/dynamics-client
[licence-badge]: https://img.shields.io/github/license/MrThearMan/dynamics-client
[repo-badge]: https://img.shields.io/github/last-commit/MrThearMan/dynamics-client
[issues-badge]: https://img.shields.io/github/issues-raw/MrThearMan/dynamics-client
[version-badge]: https://img.shields.io/pypi/pyversions/dynamics-client
[downloads-badge]: https://img.shields.io/pypi/dm/dynamics-client

[coverage]: https://coveralls.io/github/MrThearMan/dynamics-client?branch=main
[status]: https://github.com/MrThearMan/dynamics-client/actions/workflows/test.yml
[pypi]: https://pypi.org/project/dynamics-client
[licence]: https://github.com/MrThearMan/dynamics-client/blob/main/LICENSE
[repo]: https://github.com/MrThearMan/dynamics-client/commits/main
[issues]: https://github.com/MrThearMan/dynamics-client/issues
