# Statements

## POST /api/v1/statements

**Get financial statement**

Retrieves financial statement for given period. Returns statement_id in case statement is pending to generate, otherwise returns full object. Upon statement generation ws server will notify with id and owner

---

