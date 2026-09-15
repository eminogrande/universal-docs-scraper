# Test

This API section exists solely for testing purposes. It is not intended to be used in production. Or anywhere else for that matter. If you
see it, pretend it’s a magical unicorn and walk away slowly.

## GET /api/v1/test/{type}

**Summary:** Test api request parsing

**Description:** This one exists only to test that API request parsing works correctly from body, query, path and header

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| status | query | string | ✓ |  |
| type | path | string | ✓ |  |
| X-Aud | header | string | ✓ |  |
| bodyData | body | string | ✓ | Body data |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

