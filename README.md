# Dynamics Web API Client

```
pip install dynamics-client
```

Client for making Web API request from a Microsoft Dynamics 365 Database.

You should also read the [Dynamics Web API Reference Docs](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/query-data-web-api):

## Basic usage:

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

result = client.GET()

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

result = client.POST(data=data)

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

result = client.PATCH(data=data)

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

client.DELETE()
```

> Tip: Query straight after client initialization for a list of tables in the database.

---

##  Documentation:

### Client class methods and properties:

```python
from dynamics import DynamicsClient
```

#### *[DynamicsClient(...)](dynamics/client.py#L129)*

- api_url: str - Url in form: 'https://[Organization URI]/api/data/v{api_version}'
- token_url: str - Url in form: 'https://[Dynamics Token URI]/path/to/token'
- client_id: str - Client id (e.g. UUID).
- client_secret: str - Client secret (e.g. OAuth password).
- scope: List[str] - List of urls in form: 'https://[Organization URI]/scope'. Defines the database records that the API connection has access to.

Establish a Microsoft Dynamics 365 Dataverse API client connection
using OAuth 2.0 Client Credentials Flow. Client Credentials require an application user to be
created in Dynamics, and granting it an appropriate security role.

---

#### *[DynamicsClient.from_environment()](dynamics/client.py#L181)*

Create a Dynamics client from environment variables:

1. DYNAMICS_API_URL
2. DYNAMICS_TOKEN_URL
3. DYNAMICS_CLIENT_ID
4. DYNAMICS_CLIENT_SECRET
5. DYNAMICS_SCOPE

---

#### *[DynamicsClient.request_counter](dynamics/client.py#L115): int → int*

How many request have been made by the client so far.

---

### Client instance methods and properties:

```python
client = DynamicsClient(...)
```

---

#### *[client.GET(...)](dynamics/client.py#L298) → List[Dict[str, Any]]*

- not_found_ok: bool = False - No entities found should not raise NotFound error, 
  but return empty list instead.
- next_link: Optional[str] = None - Request the next set of records from this link instead.

Make a GET request to the Dataverse API with currently added query options.

[**Error Simplification Available**](dynamics/client.py#L84): 
This and the other HTTP-method -functions are decorated with a decorator, 
that can take some extra options: `simplify_errors` (If set `True`, will simplify all errors occurring
during the excecution of the function to just a single DynamicsException with a default 
error message) and `raise_separately` (A list exception types to exclude from the simplification,
if `simplify_errors=True`, so that they can be handled separately). These are useful when you want to
hide implementation details recieved in errors from frontend users.

---

#### *[client.POST(...)](dynamics/client.py#L362) → Dict[str, Any]*

- data: Dict[str, Any] - POST data.

Create new row in a table or execute an API action or function. 
Must have 'table' query option set.

[**Error Simplification Available**](dynamics/client.py#L84): See client.GET()

---

#### *[client.PATCH(...)](dynamics/client.py#L387) → Dict[str, Any]*

- data: Dict[str, Any] - PATCH data.

Update row in a table. Must have 'table' and 'row_id' query option set.

[**Error Simplification Available**](dynamics/client.py#L84): See client.GET()

---

#### *[client.DELETE()](dynamics/client.py#L413) → None*

Delete row in a table. Must have 'table' and 'row_id' query option set.

[**Error Simplification Available**](dynamics/client.py#L84): See client.GET()

---

#### *[client.current_query()](dynamics/client.py#L202) → str*

Current compiled query string.

---

#### *[client.headers](dynamics/client.py#L242) → Dict[str, str]*

Note: Read only. To set headers, use `client[name] = value`.
Similarly, you can get headers with `client[name]`.

Currently set request headers. Doesn't include per method default headers.

---

#### *[client.reset_query()](dynamics/client.py#L246) → None*

Resets all client options and headers.

---

#### *[client.set_default_headers(...)](dynamics/client.py#L264) → None*

- method: Literal["get", "post", "patch", "delete"]

Sets per method default headers. Applied automatically on each request. 
Does not override user added headers.

___

#### *[client.actions](dynamics/client.py#L152): [Actions](dynamics/api_actions.py)*

Injected instance of predefined Dynamics actions. Calling methods under this property execute the actions 
without needing to use the POST, PATCH, or DELETE methods. It is recommended to read the 
[API Action Reference](https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/actions)
and how to [Use Web API Actions](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/use-web-api-actions).

___

#### *[client.functions](dynamics/client.py#L154): [Functions](dynamics/api_functions.py)*

Injected instance of predefined Dynamics functions. Calling methods under this property run the functions 
without needing to use the GET method. It is recommended to read the 
[API Function Reference](https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/functions)
and how to [Use Web API Functions](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/use-web-api-functions).

---

#### *[client.table](dynamics/client.py#L433): str → str*

Set the table to search in.

---

#### *[client.action](dynamics/client.py#L442): str → str*

Set the Dynamics Web API action or function to use. Most of the time you don't need to set this, 
since you can use the `.actions` and `.functions` attributes to make these queries.

---

#### *[client.row_id](dynamics/client.py#L467): str → str*

Search only from the table row with this id.
If the table has an alternate key defined, you can use
`'foo=bar'` or `'foo=bar,fizz=buzz'` to retrive a single row.
Alternate keys are not enabled by default in Dynamics, so those might not work at all.

---

#### *[client.add_ref_to_property](dynamics/client.py#L481): str → str*

Add reference for this navigation property. This indicates,
that POST data will contain the API url to a matching row id
in the table this navigation property is meant to link to,
like this: `"@odata.id": "<API URI>/<table>(<id>)"`.

This should only be used to link existing rows. Adding references
for new rows can be done on create with this in POST data:
`"<nav_property>@odata.bind": "/<table>(<id>)"`.

---

#### *[client.pre_expand](dynamics/client.py#L498): str → str*

Expand/navigate to some linked table in this table
before taking any query options into account.
This will save you having to use the expand statement itself,
if all you are looking for is under this table anyway.

---

#### *[client.show_annotations](dynamics/client.py#L511): bool → bool*

Show annotations for returned data, e.g. enum values, GUID names, etc
by setting `Prefer: odata.include-annotations="*"` header.
Helpful for development and debugging.

---

#### *[client.select(...)](dynamics/client.py#L526) → List[str]*

- items: List[str] - Columns to select.

Set `$select` statement. Limits the properties returned from the current table.

---

#### *[client.expand(...)](dynamics/client.py#L542) → Dict[str, Optional[ExpandType]]*

- items: Dict[str, Optional[ExpandType]] - 
    What linked tables (a.k.a. naviagation properties) to expand and 
    what queries to make inside the expanded tables.
    Refer to the `ExpandType` TypedDict below on what queries are available,
    and what values they expect. Queries can be an empty dict or None,
    in which case no query Options are used.

```python
from typing import List, Dict, TypedDict, Union, Set, Literal

class ExpandType(TypedDict):
    select: List[str]
    filter: Union[Set[str], List[str]]
    top: int
    orderby: Dict[str, Literal["asc", "desc"]]
    expand: Dict[str, "ExpandType"]
```

Set `$expand` statement, with possible nested statements.
Controls what data from related entities is returned.

Nested expand statement limitations (WEB API v9.1):

1. Nested expand statements can *only* be applied to **many-to-one/single-valued** relationships.
This means nested expands for collections do not work!

2. Each request can include a maximum of 10 expand statements.
This applies to non-nested statements as well! There is no limit on the depth of nested
expand statements, so long as the total is 10.

---

#### *[client.filter(...)](dynamics/client.py#L603) → Union[Set[str], List[str]]*

- items: Union[Set[str], List[str]] - If a list-object, 'and' the items. If a set-object, 'or' the items.

Set `$filter` statement. Sets the criteria for which entities will be returned. It is recommended to read the 
[API Query Function Reference](https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/queryfunctions)
and how to [Query data using the Web API](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/query-data-web-api).
You can input the filters as strings, or use the included `ftr` object to construct them.

---

#### *[client.apply(...)](dynamics/client.py#L658) → str*

- statement: str - aggregate, groupby, or filter apply-string.

Set the `$apply` statement. Aggregates or groups results. It is recommended to read 
[Aggregate and grouping results](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/query-data-web-api#aggregate-and-grouping-results)
and the [FetchXML aggregation documentation](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/use-fetchxml-aggregation)
You can input the apply-statement as a string, or use the included `apl`-object to construct it.

---

#### *[client.top(...)](dynamics/client.py#L686) → int*

- number: int - Maximum number of results to return.

Set `$top` statement. Limits the number of results returned.
Default is to get the alphabetically first items, but `client.orderby(...)` can be used change this.

Note: You should not use `client.top(...)` and `client.count(...)` in the same query.
Also, using `$top` will override `Prefer: odata.maxpagesize=...` header preference setting.

---

#### *[client.orderby(...)](dynamics/client.py#L704) → Dict[str, Literal["asc", "desc"]]*

- items: Dict[str, Literal["asc", "desc"]] - Key indicates the column to order, and value indicates
  ascending (asc) or descending (desc) order respectively.

Set `$orderby` statement. Specifies the order in which items are returned.

---

#### *[client.count(...)](dynamics/client.py#L729) → bool*

- value: bool - If True, include the count (otherwise not included by default).

Set to True to include a `$count` statement. This adds the count of entities that match the 
filter criteria in the results. Count will be the first item in the list of results.

Note: You should not use `client.count(...)` and `client.top(...)` in the same query.

---

#### *[client.pagesize](dynamics/client.py#L748): int → int*

Specify the number of tables to return in a page. 
By default, this is set to 5000, which is the maximum.

---

### [Exceptions](dynamics/exceptions.py):

```python
from dynamics.exceptions import *
```

If [Django REST framework](https://www.django-rest-framework.org/) is installed, 
exceptions subclass from rest_framework.exceptions.APIException, 
otherwise a similar class is created and used instead.

* [DynamicsException](dynamics/exceptions.py#L43) - Dynamics Web API call failed
* [ParseError](dynamics/exceptions.py#L52) - Malformed request
* [AuthenticationFailed](dynamics/exceptions.py#L58) - Incorrect authentication credentials
* [PermissionDenied](dynamics/exceptions.py#L64) - You do not have permission to perform this action
* [NotFound](dynamics/exceptions.py#L70) - Not found
* [MethodNotAllowed](dynamics/exceptions.py#L76) - Method x not allowed
* [DuplicateRecordError](dynamics/exceptions.py#L87) - Trying to save a duplicate record
* [PayloadTooLarge](dynamics/exceptions.py#L94) - Request length is too large
* [APILimitsExceeded](dynamics/exceptions.py#L100) - Dynamics Web API limits were exceeded
* [OperationNotImplemented](dynamics/exceptions.py#L120) - Requested operation isn't implemented
* [WebAPIUnavailable](dynamics/exceptions.py#L126) - Web API service isn't available

---

### [API Query Functions](dynamics/query_functions.py):

```python
from dynamics import ftr
```

Object that holds `$filter` query string construction convenience methods. It is recommended to read the 
[API Query Function Reference](https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/queryfunctions)
and how to [Query data using the Web API](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/query-data-web-api).

### Comparison operations:

#### *[ftr.eq(...)](dynamics/query_functions.py#L171) → str*
#### *[ftr.ne(...)](dynamics/query_functions.py#L183) → str*
#### *[ftr.gt(...)](dynamics/query_functions.py#L195) → str*
#### *[ftr.ge(...)](dynamics/query_functions.py#L207) → str*
#### *[ftr.lt(...)](dynamics/query_functions.py#L219) → str*
#### *[ftr.le(...)](dynamics/query_functions.py#L231) → str*
- column: str - Column to apply the operation to.
- value: Union[str, int, float, bool, None] - Value to compare against.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation, 
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

### Logical operations:

#### *[ftr.and_(...)](dynamics/query_functions.py#L245) → str*
#### *[ftr.or_(...)](dynamics/query_functions.py#L254) → str*
- **args*: str - Other filter operation strings to and/or together.
- ***kwargs*: If has `group=True` - Group the operation inside parentheses.

#### *[ftr.not_(...)](dynamics/query_functions.py#L263) → str*
- operation: str - Invert this operation. Only works on standard operators!
- group : bool = False - Group the operation inside parentheses.

### Standard query functions:

#### *[ftr.contains(...)](dynamics/query_functions.py#L270) → str*
#### *[ftr.endswith(...)](dynamics/query_functions.py#L282) → str*
#### *[ftr.startswith(...)](dynamics/query_functions.py#L294) → str*
- column: str - Column to apply the operation to.
- value: Union[str, int, float, bool, None] - Value to compare against.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation, 
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

### Lambda operations:

#### *[ftr.any_(...)](dynamics/query_functions.py#L308) → str*
#### *[ftr.all_(...)](query_functions.py#L330) → str*
- collection: str - Name of the collection-valued navigation property for some table, 
  for the members of which the given operation is evaluated.
- indicator: str - Item indicator to use inside the statement, typically a single letter.
  The same indicator should be given to the operation(s) evaluated inside this operation.
- operation: str = None - Operation(s) evaluated inside this operation.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

### Special query functions:

#### *[ftr.in_(...)](dynamics/query_functions.py#L353) → str*
#### *[ftr.not_in(...)](dynamics/query_functions.py#L358) → str*
- column: str - Column to check.
- values: List[Union[str, int, float, bool, None]] - Values to evaluate against.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluate whether the value in the given column exists/doesn't exist in a list of values.

#### *[ftr.between(...)](dynamics/query_functions.py#L363) → str*
#### *[ftr.not_between(...)](dynamics/query_functions.py#L370) → str*
- column: str - Column to check.
- values: Tuple[Union[str, int, float], Union[str, int, float]] - Values that define the range.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluate whether the value in the given column is/is not between two values.

#### *[ftr.contain_values(...)](dynamics/query_functions.py#L377) → str*
#### *[ftr.not_contain_values(...)](dynamics/query_functions.py#L382) → str*
- column: str - Column to check.
- values: List[Union[str, int, float, bool, None]] - Values that the column may contain.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluate whether the value in the given column contains/doesn't contain the listed values.

#### *[ftr.above(...)](dynamics/query_functions.py#L391) → str*
#### *[ftr.above_or_equal(...)](dynamics/query_functions.py#L396) → str*
#### *[ftr.under(...)](dynamics/query_functions.py#L401) → str*
#### *[ftr.under_or_equal(...)](dynamics/query_functions.py#L406) → str*
#### *[ftr.not_under(...)](dynamics/query_functions.py#L411) → str*
- column: str - Column to check.
- ref: Union[str, int, float, bool, None] - Referenced
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluates whether the value in column is 
above/above or equal/under/under or equal/not under ref in the hierarchy.

#### *[ftr.today(...)](dynamics/query_functions.py#L418) → str*
#### *[ftr.tomorrow(...)](dynamics/query_functions.py#L418) → str*
#### *[ftr.yesterday(...)](dynamics/query_functions.py#L418) → str*
- column: str - Column to check.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluates whether the value in the given column equals today's/tomorrow's/yesterday’s date.

#### *[ftr.on(...)](dynamics/query_functions.py#L435) → str*
#### *[ftr.on_or_after(...)](dynamics/query_functions.py#L440) → str*
#### *[ftr.on_or_before(...)](dynamics/query_functions.py#L445) → str*
- column: str - Column to check.
- date: str - ISO date string (format: YYYY-mm-ddTHH:MM:SSZ) to evaluate against.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluates whether the date in the given column is on/on or after/on or before the specified date.

#### *[ftr.this_month(...)](dynamics/query_functions.py#L522) → str*
#### *[ftr.this_week(...)](dynamics/query_functions.py#L527) → str*
#### *[ftr.this_year(...)](dynamics/query_functions.py#L532) → str*
#### *[ftr.last_month(...)](dynamics/query_functions.py#L554) → str*
#### *[ftr.last_week(...)](dynamics/query_functions.py#L559) → str*
#### *[ftr.last_year(...)](dynamics/query_functions.py#L564) → str*
#### *[ftr.next_month(...)](dynamics/query_functions.py#L581) → str*
#### *[ftr.next_week(...)](dynamics/query_functions.py#L586) → str*
#### *[ftr.next_year(...)](dynamics/query_functions.py#L591) → str*
- column: str - Column to check.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluates whether the date in the given column is within the current/last/next month/week/year.

#### *[ftr.last_7_days(...)](dynamics/query_functions.py#L539) → str*
- column: str - Column to check.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluates whether the date in the given column in the last 7 days.

#### *[ftr.last_x_days(...)](dynamics/query_functions.py#L598) → str*
#### *[ftr.last_x_hours(...)](dynamics/query_functions.py#L613) → str*
#### *[ftr.last_x_months(...)](dynamics/query_functions.py#L618) → str*
#### *[ftr.last_x_weeks(...)](dynamics/query_functions.py#L623) → str*
#### *[ftr.last_x_years(...)](dynamics/query_functions.py#L628) → str*
#### *[ftr.next_x_days(...)](dynamics/query_functions.py#L635) → str*
#### *[ftr.next_x_hours(...)](dynamics/query_functions.py#L650) → str*
#### *[ftr.next_x_months(...)](dynamics/query_functions.py#L655) → str*
#### *[ftr.next_x_weeks(...)](dynamics/query_functions.py#L660) → str*
#### *[ftr.next_x_years(...)](dynamics/query_functions.py#L665) → str*
#### *[ftr.older_than_x_days(...)](dynamics/query_functions.py#L672) → str*
#### *[ftr.older_than_x_hours(...)](dynamics/query_functions.py#L677) → str*
#### *[ftr.older_than_x_minutes(...)](dynamics/query_functions.py#L682) → str*
#### *[ftr.older_than_x_months(...)](dynamics/query_functions.py#L687) → str*
#### *[ftr.older_than_x_weeks(...)](dynamics/query_functions.py#L692) → str*
#### *[ftr.older_than_x_years(...)](dynamics/query_functions.py#L697) → str*
- column: str - Column to check.
- x: int - How many of the specified unit to check for.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluates whether the date in the given column in the last x/in the next x/is older than x specified units.

#### *[ftr.in_fiscal_period(...)](dynamics/query_functions.py#L452) → str*
#### *[ftr.in_fiscal_period_and_year(...)](dynamics/query_functions.py#L457) → str*
#### *[ftr.in_fiscal_year(...)](dynamics/query_functions.py#L473) → str*
#### *[ftr.in_or_after_fiscal_period_and_year(...)](dynamics/query_functions.py#L478) → str*
#### *[ftr.in_or_before_fiscal_period_and_year(...)](dynamics/query_functions.py#L494) → str*
#### *[ftr.this_fiscal_period(...)](dynamics/query_functions.py#L512) → str*
#### *[ftr.this_fiscal_year(...)](dynamics/query_functions.py#L517) → str*
#### *[ftr.last_fiscal_period(...)](dynamics/query_functions.py#L544) → str*
#### *[ftr.last_fiscal_year(...)](dynamics/query_functions.py#L549) → str*
#### *[ftr.next_fiscal_period(...)](dynamics/query_functions.py#L571) → str*
#### *[ftr.next_fiscal_year(...)](dynamics/query_functions.py#L576) → str*
#### *[ftr.last_x_fiscal_periods(...)](dynamics/query_functions.py#L603) → str*
#### *[ftr.last_x_fiscal_years(...)](dynamics/query_functions.py#L608) → str*
#### *[ftr.next_x_fiscal_periods(...)](dynamics/query_functions.py#L640) → str*
#### *[ftr.next_x_fiscal_periods(...)](dynamics/query_functions.py#L645) → str*
- column: str - Column to check.
- Needed based on function:
  - period: int - Fiscal period to evaluate against.
  - year: int - Fiscal year to evaluate against.
  - x: int - How many of the specified unit to check for.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluates value in the given column against specified fiscal period(s) and/or year(s).

#### *[ftr.equal_business_id(...)](dynamics/query_functions.py#L704) → str*
#### *[ftr.not_business_id(...)](dynamics/query_functions.py#L709) → str*
- column: str - Column to check.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluates whether the value in the given column is equal/not equal to the specified business ID.

#### *[ftr.equal_user_id(...)](dynamics/query_functions.py#L716) → str*
#### *[ftr.not_user_id(...)](dynamics/query_functions.py#L721) → str*
- column: str - Column to check.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluates whether the value in the given column is equal/not equal to the ID of the user.

#### *[ftr.equal_user_language(...)](dynamics/query_functions.py#L728) → str*
#### *[ftr.equal_user_or_user_hierarchy(...)](dynamics/query_functions.py#L733) → str*
#### *[ftr.equal_user_or_user_hierarchy_and_teams(...)](dynamics/query_functions.py#L738) → str*
#### *[ftr.equal_user_or_user_teams(...)](dynamics/query_functions.py#L744) → str*
#### *[ftr.equal_user_teams(...)](dynamics/query_functions.py#L749) → str*

Evaluates whether the value in the given column is equal to the what's asked.

---

### [API Apply Functions](dynamics/apply_functions.py):

```python
from dynamics import apl
```

Object that holds `$apply` string construction convenience methods. It is recommended to read 
[Aggregate and grouping results](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/query-data-web-api#aggregate-and-grouping-results)
and the [FetchXML aggregation documentation](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/use-fetchxml-aggregation)

#### *[apl.groupby(...)](dynamics/apply_functions.py#L21) → str*
- columns: List[str] - Columns to group by.
- aggregate: str = None - Aggregate grouped results by this `apl.aggregate`-function.

Group results by columns, optionally aggregate.

#### *[apl.aggregate(...)](dynamics/apply_functions.py#L31) → str*
- col_: str - Column to aggregate over.
- with_: Literal["average", "sum", "min", "max", "count"] - How to aggregate the columns.
- as_: str - Aggregate result alias.

Aggregate column with some aggregation function, and alias the result under some name.

#### *[apl.filter(...)](dynamics/apply_functions.py#L41) → str*
- by: filter_type - Filter results by this filter string before applying grouping.
  Use the `ftr`-object to construct this.
- group_by_columns: List[str] - Columns to group by.

Group filtered values by columns.

---

### [Normalizers](dynamics/normalizers.py):

```python
from dynamics.normalizers import *
```

Included normalizers can be used to process the returned values to quarantee wanted types.
The most common case is missing data in the Dynamics database, in which case None would be returned.
Normalizer can be used to convert this to, e.g., an empty string, or any other default value.
They can also be used to specify numeric data as float or int.

#### *[as_int(...)](dynamics/normalizers.py#L21) → int*

- value: Any - Value to normalize.
- default: int = 0 - Default to return if casting value to int fails.

#### *[as_float(...)](dynamics/normalizers.py#L30) → float*

- value: Any - Value to normalize.
- default: int = 0.0 - Default to return if casting value to float fails.

#### *[as_str(...)](dynamics/normalizers.py#L39) → str*

- value: Any - Value to normalize.
- default: int = "" - Default to return if casting value to string fails.

#### *[as_bool(...)](dynamics/normalizers.py#L48) → bool*

- value: Any - Value to normalize.
- default: int = False - Default to return if casting value to bool fails.

#### *[str_as_datetime(...)](dynamics/normalizers.py#L55) → datetime*

- value: str - Value to normalize.
- default: Any = None - Default to return if casting value to datetime fails.


---

### [Utils](dynamics/utils.py):

```python
from dynamics.utils import *
```

This library includes a number of helpful utilities.


#### *[to_dynamics_date_format(...)](dynamics/utils.py#L29) → str*

- date: datetime - Datetime object to convert.
- from_timezone: str = None - Name of the timezone, from 'pytz.all_timezones', the date is in.

Convert a datetime-object to Dynamics compatible ISO formatted date string.

---

#### *[from_dynamics_date_format(...)](dynamics/utils.py#L47) → datetime*

- date: str - ISO datestring from Dynamics database, in form: YYYY-mm-ddTHH:MM:SSZ.
- to_timezone: str = "UCT" - Name of the timezone, from 'pytz.all_timezones', to convert the date to. 
                             This won't add 'tzinfo', instead the actual time part will be changed from UCT
                             to what the time is at 'to_timezone'.
  
Convert a ISO datestring from Dynamics database to a datetime-object.

---

#### *[cache](dynamics/utils.py#L129) → [SQLiteCache:](dynamics/utils.py#L91)*

Instance of a SQLite based cache that the client uses to store the auth token so that it can be
reused between client instances. Django's cache is prefered to this, if it is installed.

---
