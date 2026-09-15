# Cards/Issuance

The **Card Issuance API** enables the seamless issuance and management of both virtual and physical cards. Virtual cards can be generated
instantly and are ideal for secure online transactions. Physical cards are produced and securely shipped to end-users, with measures in
place to ensure safety during transit. One such measure is activation upon delivery, which prevents unauthorized use or fraudulent spending
while the card is in transit.

## POST /api/v1/cards/plastic

**Summary:** Issue plastic card

**Description:** Issues a plastic card for the specified user and sends it to the provided address.

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string | ✓ | Body data |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

## POST /api/v1/cards/virtual

**Summary:** Issue virtual card

**Description:** Issues a virtual card for the specified user

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string | ✓ | Body data |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

## PUT /api/v1/cards/{cardId}/activate

**Summary:** Activate card

**Description:** Activates a card that has been issues to a user and is currently in **NotActivated** state. </br> **Note:** This endpoint is needed only for physical cards to provide additional layer of security in case the card is stolen during delivery.

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string | ✓ | Body data |
| cardId | path | string | ✓ | Id of the card on which the action should be performed |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

