# Cards/Details

The **Card Details APIs** enable secure access to sensitive card information, including full PAN, CVV, and expiry date.  
Access is strictly controlled, audited, and permitted only through secure, authorized channels in full compliance with PCI DSS standards.

> **Note:** To obtain card details, each request must include a valid **action token** generated through
> the [Confirmation](#tag/Confirmation) process.  
> This mechanism ensures the cardholder has explicitly authorized the operation using their private key.

## POST /api/v1/cards/{cardId}/cvv

**Summary:** Get card CVV

**Description:** Retrieves CVV code for the card using the action confirmation token generated using the **Confirmation** flow

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| cardId | path | string | ✓ | Id of the card on which the action should be performed |
| bodyData | body | string | ✓ | Body data |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

## POST /api/v1/cards/{cardId}/details

**Summary:** Get card details

**Description:** Retrieves card PAN and expiry date using the action confirmation token generated using the **Confirmation** flow

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| cardId | path | string | ✓ | Id of the card on which the action should be performed |
| bodyData | body | string | ✓ | Body data |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

## POST /api/v1/cards/{cardId}/pin

**Summary:** Get card pin

**Description:** Retrieves card Pin code using the action confirmation token generated using the **Confirmation** flow

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| cardId | path | string | ✓ | Id of the card on which the action should be performed |
| bodyData | body | string | ✓ | Body data |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

