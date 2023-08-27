# Documentation

## Client class methods and properties

```python
from dynamics import DynamicsClient
```

#### *DynamicsClient(...)*

- api_url: str - Url in form: 'https://[Organization URI]/api/data/v{api_version}'
- token_url: str - Url in form: 'https://[Dynamics Token URI]/path/to/token'
- client_id: str - Client id (e.g. UUID).
- client_secret: str - Client secret (e.g. OAuth password).


- *scope: Optional[str | List[str]] - Url or list of urls in form: 'https://[Organization URI]/scope'. Defines the database records that the API connection has access to.*
- *resource: Optional[str] - Url in form: 'https://[Organization URI]'. Defines the database records that the API connection has access to.*

*NOTE: at least one of `scope` or `resource` must be provided.*

Establish a Microsoft Dynamics 365 Dataverse API client connection
using OAuth 2.0 Client Credentials Flow. Client Credentials require an application user to be
created in Dynamics, and granting it an appropriate security role.

*If you are experiencing auth errors, inspect the returned auth token's `aud`
and see whether it resolves to `00000002-0000-0000-c000-000000000000` instead of your CRM url.*

*If so, you may want to specify the resource URL using the optional
`resource=` parameter.*

---

#### *DynamicsClient.from_environment()*

Create a Dynamics client from environment variables:

1. DYNAMICS_API_URL
2. DYNAMICS_TOKEN_URL
3. DYNAMICS_CLIENT_ID
4. DYNAMICS_CLIENT_SECRET


5. *DYNAMICS_SCOPE (Optional)*
6. *DYNAMICS_RESOURCE (Optional)*

*NOTE: at least one of `DYNAMICS_SCOPE` or `DYNAMICS_RESOURCE` must be provided.*

*If you are experiencing auth errors, inspect the returned auth token's `aud`
and see whether it resolves to `00000002-0000-0000-c000-000000000000` instead of your CRM url.*

*If so, you may want to specify the resource URL using the optional
`DYNAMICS_RESOURCE` environment variable.*


---

#### *DynamicsClient.request_counter: int → int*

How many request have been made by the client so far.

---

## Client instance methods and properties

```python
client = DynamicsClient(...)
```

---

#### *client.get(...) → List[Dict[str, Any]]*

- not_found_ok: bool = False - No entities found should not raise NotFound error,
  but return empty list instead.
- query: Optional[str] = None - Use this url instead of building it from current query parameters.

Make a GET request to the Dataverse API with currently added query options.

**Error Simplification Available**:
This and the other HTTP-methods are decorated with a decorator,
that can take some extra options: `simplify_errors` (If set `True`, will simplify all errors occurring
during the execution of the function to just a single DynamicsException with a default
error message) and `raise_separately` (A list exception types to exclude from the simplification,
if `simplify_errors=True`, so that they can be handled separately). These are useful when you want to
hide implementation details received in errors from frontend users.

---

#### *client.post(...) → Dict[str, Any]*

- data: Dict[str, Any] - POST data.
- query: Optional[str] = None - Use this url instead of building it from current query parameters.

Create new row in a table or execute an API action or function.
Must have 'table' query option set.

**Error Simplification Available**: See client.get()

---

#### *client.patch(...) → Dict[str, Any]*

- data: Dict[str, Any] - PATCH data.
- query: Optional[str] = None - Use this url instead of building it from current query parameters.

Update row in a table. Must have 'table' and 'row_id' query option set.

**Error Simplification Available**: See client.get()

---

#### *client.delete() → None*

- query: Optional[str] = None - Use this url instead of building it from current query parameters.

Delete row in a table. Must have 'table' and 'row_id' query option set.

**Error Simplification Available**: See client.get()

---

#### *client.create_task(...) -> asyncio.Task*

- method: Callable[P, T] - Client method to create task for.
- args & kwargs: Any - Arguments passed to the method.

Can be used to create [asyncio.Tasks](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task),
which will be run using the defined query options before the task was created.
This way, you can queue up many tasks and run them asynchronously, either with
[asyncio.gather](https://docs.python.org/3/library/asyncio-task.html#asyncio.gather),
or from python 3.11, [asyncio.TaskGroups](https://github.com/python/cpython/issues/90908).
To use TaskGroups, just use the DynamicsClient as an async context manager.
The async context manager behaves like a TaskGroup from 3.11 up,
otherwise just instantiates a dynamics client like normal.

```python
async with DynamicsClient.from_environment() as client:
    client.table = "foo"
    client.select = ["bar"]
    task_1 = client.create_task(client.get)

    client.reset_query()  # Remember to call this!

    task_2 = client.create_task(client.actions.win_quote, quote_id="...")

data = task_1.result()

# Can also be used without the context manager
client.table = "foo"
client.select = ["bar"]
task3 = client.create_task(client.post, data={"foo": "bar"})
result = await task3
```

---

#### *client.current_query() → str*

Current compiled query string.

---

#### *client.headers → Dict[str, str]*

Note: Read only. To set headers, use `client[name] = value`.
Similarly, you can get headers with `client[name]`.

Currently set request headers. Doesn't include per method default headers.

---

#### *client.reset_query() → None*

Resets all client options and headers.

---

#### *client.default_headers(...) → Dict[str, str]*

- method: Literal["get", "post", "patch", "delete"]

Get method default headers for given method. Applied automatically on each request.

___

#### *client.actions: Actions*

Injected instance of predefined Dynamics actions. Calling methods under this property execute the actions
without needing to use the POST, PATCH, or DELETE methods. It is recommended to read the
[API Action Reference](https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/actions)
and how to [Use Web API Actions](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/use-web-api-actions).

___

#### *client.functions: Functions*

Injected instance of predefined Dynamics functions. Calling methods under this property run the functions
without needing to use the GET method. It is recommended to read the
[API Function Reference](https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/functions)
and how to [Use Web API Functions](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/use-web-api-functions).

---

#### *client.table: str → str*

Set the table to search in.

---

#### *client.action: str → str*

Set the Dynamics Web API action or function to use. Most of the time you don't need to set this,
since you can use the `.actions` and `.functions` attributes to make these queries.

---

#### *client.row_id: str → str*

Search only from the table row with this id.
If the table has an alternate key defined, you can use
`'foo=bar'` or `'foo=bar,fizz=buzz'` to retrieve a single row.
Alternate keys are not enabled by default in Dynamics, so those might not work at all.

---

#### *client.add_ref_to_property: str → str*

Add reference for this navigation property. This indicates,
that POST data will contain the API url to a matching row id
in the table this navigation property is meant to link to,
like this: `"@odata.id": "<API URI>/<table>(<id>)"`.

This should only be used to link existing rows. Adding references
for new rows can be done on create with this in POST data:
`"<nav_property>@odata.bind": "/<table>(<id>)"`.

---

#### *client.pre_expand: str → str*

Expand/navigate to some linked table in this table
before taking any query options into account.
This will save you having to use the expand statement itself,
if all you are looking for is under this table anyway.

---

#### *client.show_annotations: bool → bool*

Show annotations for returned data, e.g. enum values, GUID names, etc
by setting `Prefer: odata.include-annotations="*"` header.
Helpful for development and debugging.

---

#### *client.select(...) → List[str]*

- items: List[str] - Columns to select.

Set `$select` statement. Limits the properties returned from the current table.

---

#### *client.expand(...) → Dict[str, Optional[ExpandType]]*

- items: Dict[str, Optional[ExpandType]] -
    What linked tables (a.k.a. navigation properties) to expand and
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

#### *client.filter(...) → Union[Set[str], List[str]]*

- items: Union[Set[str], List[str]] - If a list-object, 'and' the items. If a set-object, 'or' the items.

Set `$filter` statement. Sets the criteria for which entities will be returned. It is recommended to read the
[API Query Function Reference](https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/queryfunctions)
and how to [Query data using the Web API](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/query-data-web-api).
You can input the filters as strings, or use the included `ftr` object to construct them.

---

#### *client.apply(...) → str*

- statement: str - aggregate, groupby, or filter apply-string.

Set the `$apply` statement. Aggregates or groups results. It is recommended to read
[Aggregate and grouping results](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/query-data-web-api#aggregate-and-grouping-results)
and the [FetchXML aggregation documentation](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/use-fetchxml-aggregation)
You can input the apply-statement as a string, or use the included `apl`-object to construct it.

---

#### *client.top(...) → int*

- number: int - Maximum number of results to return.

Set `$top` statement. Limits the number of results returned.
Default is to get the alphabetically first items, but `client.orderby(...)` can be used change this.

Note: You should not use `client.top(...)` and `client.count(...)` in the same query.
Also, using `$top` will override `Prefer: odata.maxpagesize=...` header preference setting.

---

#### *client.orderby(...) → Dict[str, Literal["asc", "desc"]]*

- items: Dict[str, Literal["asc", "desc"]] - Key indicates the column to order, and value indicates
  ascending (asc) or descending (desc) order respectively.

Set `$orderby` statement. Specifies the order in which items are returned.

---

#### *client.count(...) → bool*

- value: bool - If True, include the count (otherwise not included by default).

Set to True to include a `$count` statement. This adds the count of entities that match the
filter criteria in the results. Count will be the first item in the list of results.

Note: You should not use `client.count(...)` and `client.top(...)` in the same query.

---

#### *client.pagesize: int → int*

Specify the number of tables to return in a page.
By default, this is set to 5000, which is the maximum.

---

#### *client.fetch_xml: str → str*

Set a query using the FetchXML query language.
Must set table, but cannot set any other query options!
Queries can be constructed with the included `FetchXMLBuilder`.

XML Schema:
[https://docs.microsoft.com/en-us/powerapps/developer/data-platform/fetchxml-schema](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/fetchxml-schema)

How to use:
[https://docs.microsoft.com/en-us/powerapps/developer/data-platform/use-fetchxml-construct-query](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/use-fetchxml-construct-query)

---

## Exceptions

```python
from dynamics.exceptions import *
```

If [Django REST framework](https://www.django-rest-framework.org/) is installed,
exceptions subclass from rest_framework.exceptions.APIException,
otherwise a similar class is created and used instead.

* DynamicsException - Dynamics Web API call failed
* ParseError - Malformed request
* AuthenticationFailed - Incorrect authentication credentials
* PermissionDenied - You do not have permission to perform this action
* NotFound - Not found
* MethodNotAllowed - Method x not allowed
* DuplicateRecordError - Trying to save a duplicate record
* PayloadTooLarge - Request length is too large
* APILimitsExceeded - Dynamics Web API limits were exceeded
* OperationNotImplemented - Requested operation isn't implemented
* WebAPIUnavailable - Web API service isn't available

---

## API Query Functions

```python
from dynamics import ftr
```

Object that holds `$filter` query string construction convenience methods. It is recommended to read the
[API Query Function Reference](https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/queryfunctions)
and how to [Query data using the Web API](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/query-data-web-api).


## Comparison operations

#### *ftr.eq(...) → str*
#### *ftr.ne(...) → str*
#### *ftr.gt(...) → str*
#### *ftr.ge(...) → str*
#### *ftr.lt(...) → str*
#### *ftr.le(...) → str*
- column: str - Column to apply the operation to.
- value: Union[str, int, float, bool, None] - Value to compare against.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.


## Logical operations

#### *ftr.and_(...) → str*
#### *ftr.or_(...) → str*
- **args*: str - Other filter operation strings to and/or together.
- ***kwargs*: If has `group=True` - Group the operation inside parentheses.

#### *ftr.not_(...) → str*
- operation: str - Invert this operation. Only works on standard operators!
- group : bool = False - Group the operation inside parentheses.


## Standard query functions

#### *ftr.contains(...) → str*
#### *ftr.endswith(...) → str*
#### *ftr.startswith(...) → str*
- column: str - Column to apply the operation to.
- value: Union[str, int, float, bool, None] - Value to compare against.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

## Lambda operations

#### *ftr.any_(...) → str*
#### *ftr.all_(...) → str*
- collection: str - Name of the collection-valued navigation property for some table,
  for the members of which the given operation is evaluated.
- indicator: str - Item indicator to use inside the statement, typically a single letter.
  The same indicator should be given to the operation(s) evaluated inside this operation.
- operation: str = None - Operation(s) evaluated inside this operation.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.


## Special query functions

#### *ftr.in_(...) → str*
#### *ftr.not_in(...) → str*
- column: str - Column to check.
- values: List[Union[str, int, float, bool, None]] - Values to evaluate against.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluate whether the value in the given column exists/doesn't exist in a list of values.

#### *ftr.between(...) → str*
#### *ftr.not_between(...) → str*
- column: str - Column to check.
- values: Tuple[Union[str, int, float], Union[str, int, float]] - Values that define the range.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluate whether the value in the given column is/is not between two values.

#### *ftr.contain_values(...) → str*
#### *ftr.not_contain_values(...) → str*
- column: str - Column to check.
- values: List[Union[str, int, float, bool, None]] - Values that the column may contain.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluate whether the value in the given column contains/doesn't contain the listed values.

#### *ftr.above(...) → str*
#### *ftr.above_or_equal(...) → str*
#### *ftr.under(...) → str*
#### *ftr.under_or_equal(...) → str*
#### *ftr.not_under(...) → str*
- column: str - Column to check.
- ref: Union[str, int, float, bool, None] - Referenced
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluates whether the value in column is
above/above or equal/under/under or equal/not under ref in the hierarchy.

#### *ftr.today(...) → str*
#### *ftr.tomorrow(...) → str*
#### *ftr.yesterday(...) → str*
- column: str - Column to check.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluates whether the value in the given column equals today's/tomorrow's/yesterday’s date.

#### *ftr.on(...) → str*
#### *ftr.on_or_after(...) → str*
#### *ftr.on_or_before(...) → str*
- column: str - Column to check.
- date: str - ISO date string (format: YYYY-mm-ddTHH:MM:SSZ) to evaluate against.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluates whether the date in the given column is on/on or after/on or before the specified date.

#### *ftr.this_month(...) → str*
#### *ftr.this_week(...) → str*
#### *ftr.this_year(...) → str*
#### *ftr.last_month(...) → str*
#### *ftr.last_week(...) → str*
#### *ftr.last_year(...) → str*
#### *ftr.next_month(...) → str*
#### *ftr.next_week(...) → str*
#### *ftr.next_year(...) → str*
- column: str - Column to check.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluates whether the date in the given column is within the current/last/next month/week/year.

#### *ftr.last_7_days(...) → str*
- column: str - Column to check.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluates whether the date in the given column in the last 7 days.

#### *ftr.last_x_days(...) → str*
#### *ftr.last_x_hours(...) → str*
#### *ftr.last_x_months(...) → str*
#### *ftr.last_x_weeks(...) → str*
#### *ftr.last_x_years(...) → str*
#### *ftr.next_x_days(...) → str*
#### *ftr.next_x_hours(...) → str*
#### *ftr.next_x_months(...) → str*
#### *ftr.next_x_weeks(...) → str*
#### *ftr.next_x_years(...) → str*
#### *ftr.older_than_x_days(...) → str*
#### *ftr.older_than_x_hours(...) → str*
#### *ftr.older_than_x_minutes(...) → str*
#### *ftr.older_than_x_months(...) → str*
#### *ftr.older_than_x_weeks(...) → str*
#### *ftr.older_than_x_years(...) → str*
- column: str - Column to check.
- x: int - How many of the specified unit to check for.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluates whether the date in the given column in the last x/in the next x/is older than x specified units.

#### *ftr.in_fiscal_period(...) → str*
#### *ftr.in_fiscal_period_and_year(...) → str*
#### *ftr.in_fiscal_year(...) → str*
#### *ftr.in_or_after_fiscal_period_and_year(...) → str*
#### *ftr.in_or_before_fiscal_period_and_year(...) → str*
#### *ftr.this_fiscal_period(...) → str*
#### *ftr.this_fiscal_year(...) → str*
#### *ftr.last_fiscal_period(...) → str*
#### *ftr.last_fiscal_year(...) → str*
#### *ftr.next_fiscal_period(...) → str*
#### *ftr.next_fiscal_year(...) → str*
#### *ftr.last_x_fiscal_periods(...) → str*
#### *ftr.last_x_fiscal_years(...) → str*
#### *ftr.next_x_fiscal_periods(...) → str*
#### *ftr.next_x_fiscal_periods(...) → str*
- column: str - Column to check.
- Needed based on function:
  - period: int - Fiscal period to evaluate against.
  - year: int - Fiscal year to evaluate against.
  - x: int - How many of the specified unit to check for.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluates value in the given column against specified fiscal period(s) and/or year(s).

#### *ftr.equal_business_id(...) → str*
#### *ftr.not_business_id(...) → str*
- column: str - Column to check.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluates whether the value in the given column is equal/not equal to the specified business ID.

#### *ftr.equal_user_id(...) → str*
#### *ftr.not_user_id(...) → str*
- column: str - Column to check.
- lambda_indicator: str = None - If this operation is evaluated inside a lambda operation,
  provide the lambda operations item indicator here.
- group: bool = False - Group the operation inside parentheses.

Evaluates whether the value in the given column is equal/not equal to the ID of the user.

#### *ftr.equal_user_language(...) → str*
#### *ftr.equal_user_or_user_hierarchy(...) → str*
#### *ftr.equal_user_or_user_hierarchy_and_teams(...) → str*
#### *ftr.equal_user_or_user_teams(...) → str*
#### *ftr.equal_user_teams(...) → str*

Evaluates whether the value in the given column is equal to the what's asked.

---

## API Apply Functions

```python
from dynamics import apl
```

Object that holds `$apply` string construction convenience methods. It is recommended to read
[Aggregate and grouping results](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/query-data-web-api#aggregate-and-grouping-results)
and the [FetchXML aggregation documentation](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/use-fetchxml-aggregation)

#### *apl.groupby(...) → str*
- columns: List[str] - Columns to group by.
- aggregate: str = None - Aggregate grouped results by this `apl.aggregate`-function.

Group results by columns, optionally aggregate.

#### *apl.aggregate(...) → str*
- col_: str - Column to aggregate over.
- with_: Literal["average", "sum", "min", "max", "count"] - How to aggregate the columns.
- as_: str - Aggregate result alias.

Aggregate column with some aggregation function, and alias the result under some name.

#### *apl.filter(...) → str*
- by: filter_type - Filter results by this filter string before applying grouping.
  Use the `ftr`-object to construct this.
- group_by_columns: List[str] - Columns to group by.

Group filtered values by columns.

---

## FetchXML Builder

```python
from dynamics.fetchxml import FetchXMLBuilder
```

This builder can be used to build FetchXML queries for the client.
It uses the Builder design pattern. Here is an example:

```python
from dynamics.fetchxml import FetchXMLBuilder

fetch_xml = (
    FetchXMLBuilder(mapping="logical")
    .add_entity(name="account")
    .add_attribute(name="accountid")
    .add_attribute(name="name")
    .add_attribute(name="accountnumber")
    .order(attribute="name")
    .filter()
    .add_condition(attribute="accountnumber", operator="gt", value=1000)
    .add_linked_entity(name="systemuser", to="owninguser")
    .build()
)
```

Refer to the [FetchXML documentation](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/use-fetchxml-construct-query),
and the builder docstrings for more details.


---

## Normalizers

```python
from dynamics.normalizers import *
```

Included normalizers can be used to process the returned values to guarantee wanted types.
The most common case is missing data in the Dynamics database, in which case None would be returned.
Normalizer can be used to convert this to, e.g., an empty string, or any other default value.
They can also be used to specify numeric data as float or int.

#### *as_int(...) → int*

- value: Any - Value to normalize.
- default: int = 0 - Default to return if casting value to int fails.

#### *as_float(...) → float*

- value: Any - Value to normalize.
- default: int = 0.0 - Default to return if casting value to float fails.

#### *as_str(...) → str*

- value: Any - Value to normalize.
- default: int = "" - Default to return if casting value to string fails.

#### *as_bool(...) → bool*

- value: Any - Value to normalize.
- default: int = False - Default to return if casting value to bool fails.

#### *str_as_datetime(...) → datetime*

- value: str - Value to normalize.
- default: Any = None - Default to return if casting value to datetime fails.


---

### Utils

```python
from dynamics.utils import *
```

This library includes a number of helpful utilities.


#### *to_dynamics_date_format(...) → str*

- date: datetime - Datetime object to convert.
- from_timezone: str = None - Name of the timezone, from 'pytz.all_timezones', the date is in.

Convert a datetime-object to Dynamics compatible ISO formatted date string.

---

#### *from_dynamics_date_format(...) → datetime*

- date: str - ISO datestring from Dynamics database, in form: YYYY-mm-ddTHH:MM:SSZ.
- to_timezone: str = "UCT" - Name of the timezone, from 'pytz.all_timezones', to convert the date to.
                             This won't add 'tzinfo', instead the actual time part will be changed from UCT
                             to what the time is at 'to_timezone'.

Convert a ISO datestring from Dynamics database to a datetime-object.

---

#### *cache → SQLiteCache:*

Instance of a SQLite based cache that the client uses to store the auth token so that it can be
reused between client instances. Django's cache is preferred to this, if it is installed.

---

## Testing

The library comes with a testing client and some fixtures for pytest:


### MockClient

Dynamics Client that can be used for testing purposes. It allows mocking the responses from the real
client's HTTP methods, and can even set multiple responses at once:

```python
from dynamics.test import MockClient

expected = [{"foo": "bar"}, {"fizz": "buzz"}]

# MockClient is a builder class, so you can chain the
# setup code or use on a separate line
client = MockClient().with_responses(*expected)

result = client.get()
assert result == expected[0]

result = client.get()
assert result == expected[1]
```

Can be used with `pytest.mark.parametrize`:

```python
@pytest.mark.parametrize(
    "dynamics_client",
    [
        MockClient().with_responses({"foo": "bar"}),
        MockClient().with_responses({"foo": "baz"}),
    ],
    indirect=True,  # important!
)
def test_foo(dynamics_client):
    # Use as-is
    x = dynamics_client.get()

    # ...or patch usage
    with mock.patch("path.to.client.DynamicsClient", return_value=dynamics_client):
        ...

    with mock.patch("path.to.client.DynamicsClient.from_environment", return_value=dynamics_client):
        ...
```

If you need to configure the DynamicsClient instance, you can create a new MockClient
by inheriting from BaseMockClient and your custom DynamicsClient.

```python
from  dynamics import DynamicsClient
from dynamics.test import BaseMockClient

class MyDynamicsClient(DynamicsClient):
    pass

# Order is important, BaseMockClient first!
class MyMockClient(BaseMockClient, MyDynamicsClient):
     pass

client = MyMockClient()
```

---


### Fixtures

#### dynamics_client

An instance of MockClient that can be used to mock responses from the DynamicsClient.
If you use a customized DynamicsClient, you can configure your own `dynamics_client` fixture
like this:

```python
@pytest.fixture
def dynamics_client(request):
    if not hasattr(request, "param"):
        yield MyMockClient()
    else:
        # When used with `pytest.mark.parametrize`
        yield request.param
```


#### dynamics_cache

An instance of the cache used by the client. Can be either an instance of the SQLiteCache
that comes with the library, or Django's cache if it's installed.
