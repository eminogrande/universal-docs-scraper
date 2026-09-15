# Statements

## POST /api/v1/statements

**Summary:** Get financial statement

**Description:** Retrieves financial statement for given period. Returns statement_id in case statement is pending to generate, otherwise returns full object. Upon statement generation ws server will notify with id and owner

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string | ✓ | Body data |

### Responses

#### 200

OK

#### 202

Accepted

#### 400

Bad Request

#### 500

Internal Server Error

---

