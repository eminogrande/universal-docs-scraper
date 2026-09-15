# Transactions

The **Transaction APIs** offers functionality to read card transactions.

### Important:

This API is **deprecated** and should no longer be used.  
Please use the [Activity Feed](#tag/Activity-Feed) section instead, which provides improved capabilities for accessing and managing transaction data.

## GET /api/v1/transactions/card

**Summary:** Get card transactions

**Description:** Reads a page of card transactions associated with user

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| page_number | query | string |  | PageNumber number |
| page_size | query | string |  | Size of the page. If no page size is provided, default page size is used (25). |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

