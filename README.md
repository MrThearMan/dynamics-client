# Dynamics Web API Client
Client for making Web API request from a Microsoft Dynamics 365 Database.

API Reference Docs:
https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/query-data-web-api

### How to use:
1. Init the client:     
```python
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
client.select = [...], client.expand = {...}, etc.
```
5. Set headers (optional):
```
client.headers = {...} or client[...] = ...
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

Query with no table nor query options set to get a list of tables in the database.
Use `fetch_schema` for an xml representation of the relational ascpects of the data.
