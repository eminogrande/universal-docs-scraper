# Cards/Fees

The **Card Fees APIs** provide comprehensive details about card issuance fees incurred by the company to process a card order.  
This includes a breakdown of costs, applicable currencies, and any dynamic pricing rules configured for the account.

> **Note:** This section is applicable only if your account manager has advised you to incorporate card fee handling as part of your integration process.

## GET /api/v1/cards/{type}/fees/{country}

**Summary:** Get order fees

**Description:** Retrieves estimation of fees that should be paid for the card order</br> > **Note:** This method is applicable only if your account manager has advised you to incorporate card fee handling as part of your integration process.

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| country | path | string | ✓ | Country in which the card will be issued (ISO 3166-1 alpha-2) |
| type | path | string | ✓ | Format of the card the fees should be calculated for |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

## POST /api/v1/cards/{type}/fees/{country}/payment

**Summary:** Create order fees invoice

**Description:** Creates an invoice for payment of the card order fees.</br> > **Note:** This method is applicable only if your account manager has advised you to incorporate card fee handling as part of your integration process.

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| country | path | string | ✓ | Country in which the card will be issued (ISO 3166-1 alpha-2) |
| type | path | string | ✓ | Format of the card the fees should be calculated for |
| bodyData | body | string | ✓ | Body data |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

