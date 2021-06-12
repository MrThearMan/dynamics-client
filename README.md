# Dynamics Web API Client
```
pip install dynamics-client
```
Client for making Web API request from a Microsoft Dynamics 365 Database.

You should also read the [Dynamics Web API Reference Docs](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/query-data-web-api):

## Basic usage:
1. Init the client:     
```python
from dynamics import DynamicsClient

client = DynamicsClient(...)
client = DynamicsClient.from_environment()
```  
2. Set the table:
```python
client.table = "..."
```
3. Set row (Required for PATCH and DELETE, otherwese optional):
```python
client.row_id = "..."
```
4. Set query options (optional):
```python
client.select = [...]
client.expand = {...}
client.filter = [...]
...
```
5. Set headers (optional):
```
client[...] = ...
```

---

Make a GET request:
```python
result = client.GET()
```
Make a POST request:
```python
result = client.POST(data={...})
```
Make a PATCH request:
```python
result = client.PATCH(data={...})
```
Make a DELETE request:
```python
result = client.DELETE()
```

Remember to reset between queries:
```python
client.reset_query()
```

Query straight after client init to get a list of tables in the database.

---

##  Documentation:

### Client class methods an properties:

```python
from dynamics import DynamicsClient
```

#### *DynamicsClient(...)*

- api_url: str - Url in form: 'https://[Organization URI]/api/data/v{api_version}'
- token_url: str - Url in form: 'https://[Dynamics Token URI]/path/to/token'
- client_id: str - Client id (e.g. UUID).
- client_secret: str - Client secret (e.g. OAuth password).
- scope: List[str] - List of urls in form: 'https://[Organization URI]/scope'. Defines the database records that the API connection has access to.

Create a Dynamics client from the given arguments.

---

#### *DynamicsClient.from_environment()*

Create a Dynamics client from environment variables:

1. DYNAMICS_BASE_URL → api_url
2. DYNAMICS_TOKEN_URL → token_url
3. DYNAMICS_CLIENT_ID → client_id
4. DYNAMICS_CLIENT_SECRET → client_secret
5. DYNAMICS_SCOPE → scope

---

#### *DynamicsClient.request_counter: int*

How many request have been made by the client so far.

---

### Client instance methods and properties:

```python
client = DynamicsClient(...)
```

---

#### *client.GET(...) → List[Dict[str, Any]]*

- not_found_ok: bool = False - No entities found should not raise NotFound error, 
  but return empty list instead.
- next_link: Optional[str] = None - Request the next set of records from this link instead.

Make a GET request to the Dataverse API with currently added query options.

**Error Simplification Available**: This and the other HTTP-method -functions are decorated with a decorator, 
that can take some extra options: 'simplify_errors' (if set 'True' will simplify all errors occurring
during the excecution of the function to just a single DynamicsException with a default 
error message) and 'raise_separately' (A list Exception types to exclude from the simplification,
if 'simplify_errors' is True, so that they can be handled separately). These are useful when you want to
hide implementation details recieved in errors from frontend users.

---

#### *client.POST(...) → Dict[str, Any]*

- data: Dict[str, Any] - POST data.

Create new row in a table or execute an API action or function. 
Must have 'table' query option set.

**Error Simplification Available**: See client.GET()

---

#### *client.PATCH(...) → Dict[str, Any]*

- data: Dict[str, Any] - PATCH data.

Update row in a table. Must have 'table' and 'row_id' query option set.

**Error Simplification Available**: See client.GET()

---

#### *client.DELETE() → Dict[str, Any]*

Delete row in a table. Must have 'table' and 'row_id' query option set.

**Error Simplification Available**: See client.GET()

---

#### *client.fetch_schema(...) → Optional[str]*

- to_file: bool = False - Save to a file instead of returning as string.

XML representation of the relational ascpects of the data.

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

#### *client.set_default_headers(...) → None*

- method: Literal["get", "post", "patch", "delete"]

Sets per method default headers. Applied automatically on each request. 
Does not override user added headers.

---

#### *client.table: str → str*

Set the table to search in.

---

#### *client.action: str → str*

Set the Dynamics Web API action or function to use.
It is recommended to read the 
[API Function Reference](https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/functions)
and how to [Use Web API Functions](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/use-web-api-functions), 
as well as the 
[API Action Reference](https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/actions)
and how to [Use Web API Actions](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/use-web-api-actions).
You can input the action/function as a string, or use the included `act` and `fnc` objects construct it.

---

#### *client.row_id: str → str*

Search only from the table row with this id.
If the table has an alternate key defined, you can use
`'foo=bar'` or `'foo=bar,fizz=buzz'` to retrive a single row.
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

Note that query options cannot be used and will not be added
to the query if this property is set.

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
- expand_keys = Literal["select", "filter", "top", "orderby", "expand"]
- expand_values = Union[List[str], Set[str], int, orderby_type, Dict]
- expand_type = Dict[str, Dict[expand_keys, expand_values]]

#### *client.expand(...) → expand_type*

- items: expand_type - What linked tables (a.k.a. naviagation properties) to expand and 
                       what statements to apply inside the expanded tables.
                       If items-dict value is set to an empty dict, no query options are used.
                       Otherwise, valid keys for the items-dict are 'select', 'filter', 'top', 'orderby', and 'expand'.
                       Values under these keys should be constructed in the same manner as they are
                       when outside the expand statement, e.g. 'select' takes a List[str], 'top' an int, etc.

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

Set `$filter` statement. Sets the criteria for which entities will be returned.
It is recommended to read the 
[API Query Function Reference](https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/queryfunctions)
and how to [Query data using the Web API](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/query-data-web-api).
You can input the filters as strings, or use the included `ftr` object to construct them.

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

#### *client.pagesize: int*

Specify the number of tables to return in a page. 
By default, this is set to 1000. Maximum is 5000.

---

### Exceptions:

```python
from dynamics.exceptions import *
```

Exceptions subclass APIException from the 
[Django REST framework](https://www.django-rest-framework.org/) library, if installed.
Otherwise they work like regular exceptions.

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

### API Query Functions:

```python
from dynamics import ftr
```

Object that holds filter query string construction convenience methods. 
It is recommended to read the 
[API Query Function Reference](https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/queryfunctions)
and how to [Query data using the Web API](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/query-data-web-api).

---

### API Functions:

```python
from dynamics import fnc
```

Object that holds API function string construction convenience methods.
It is recommended to read the 
[API Function Reference](https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/functions)
and how to [Use Web API Functions](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/use-web-api-functions).

---

### API Actions:

```python
from dynamics import act
```

Object that holds API action string construction convenience methods.
[API Action Reference](https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/actions)
and how to [Use Web API Actions](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/use-web-api-actions).

---

### Normalizers:

```python
from dynamics.normalizers import *
```

Included normalizers can be used to process the returned values to quarantee wanted types.
The most common case is missing data in the Dynamics database, in which case None would be returned.
Normalizer can be used to convert this to, e.g., an empty string, or any other default value.
They can also be used to specify numeric data as float or int.

#### *as_int(...) → int*

- value: Any - Value to normalize.
- default: int - Default to return if casting value to int fails. Default is 0.

#### *as_float(...) → float*

- value: Any - Value to normalize.
- default: int - Default to return if casting value to float fails. Default is 0.0.

#### *as_str(...) → str*

- value: Any - Value to normalize.
- default: int - Default to return if casting value to string fails. Default is an empty string.

#### *as_bool(...) → bool*

- value: Any - Value to normalize.
- default: int - Default to return if casting value to bool fails. Default is False.


---

### Utils:

```python
from dynamics.utils import *
```

This library includes a number of helpful utilities.


#### *to_dynamics_date_format(...) → str*

- date: datetime - Datetime object to convert.
- from_timezone: str - Name of the timezone, from 'pytz.all_timezones', the date is in. Optional.

Convert a datetime-object to Dynamics compatible ISO formatted date string.

---

#### *from_dynamics_date_format(...) → datetime*

- date: str - ISO datestring from Dynamics database, in form: YYYY-mm-ddTHH:MM:SSZ.
- to_timezone: str - Name of the timezone, from 'pytz.all_timezones', to convert the date to. 
                     This won't add 'tzinfo', instead the actual time part will be changed from UTC
                     to what the time is at 'to_timezone'. Default is "UTC".
  
Convert a ISO datestring from Dynamics database to a datetime-object.

---

#### *DateRange(...)*

- start: str - Range start date in dynamics ISO string from. Optional.
- end: str - Range end date in dynamics ISO string from. Optional.
- start_key - Which dynamics table column has the start date. Only needed is start defined.
- end_key - Which dynamics table column has the end date. Only needed is end defined.

Class that can be used to create start and end dates from dynamics acceptable ISO datestrings
and compile an appropriate dynamics 
'[OnOrBefore](https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/onorbefore?view=dynamics-ce-odata-9)' 
and '[OnOrAfter](https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/onorafter?view=dynamics-ce-odata-9)' 
-filters. The class also includes a membership test, that can be used to test
if a (start, end) Dynamics ISO datestring tuple falls in the defined range.

```python
from dynamics import DynamicsClient
from dynamics.utils import DateRange

client = DynamicsClient(...)

start = "2020-01-01T00:00:00Z"
end = "2020-12-31T23:59:59Z"

daterange = DateRange(start=start, end=end, start_key="begin_date", end_key="end_date")

client.filter = daterange.filter_range

...

start = "2019-08-04T07:10:00Z"
end = "2020-02-01T18:00:00Z"

if (start, end) in daterange:
    ...
```

---
