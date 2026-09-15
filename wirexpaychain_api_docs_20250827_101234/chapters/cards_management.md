# Cards/Management

The **Card Management APIs** facilitate key lifecycle operations, including activation, status modifications (enable, disable, close) and spending limit management.

## PUT /api/v1/cards/{cardId}/block

**Summary:** Block card

**Description:** Blocks selected card making it impossible to use it for any transactions.

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| cardId | path | string | ✓ | Id of the card on which the action should be performed |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

## PUT /api/v1/cards/{cardId}/close

**Summary:** Close card

**Description:** Closes the card. This action cannot be undone and the card will be permanently closed.

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| cardId | path | string | ✓ | Id of the card on which the action should be performed |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

## PUT /api/v1/cards/{cardId}/limit

**Summary:** Change card limit

**Description:** Updates maximum amount that can be spent using the card within a day

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

## PUT /api/v1/cards/{cardId}/name

**Summary:** Change card name

**Description:** Updates the display name of the card

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

## PUT /api/v1/cards/{cardId}/unblock

**Summary:** Unblock card

**Description:** Unblocks selected card allowing it to be used for transactions once again.

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| cardId | path | string | ✓ | Id of the card on which the action should be performed |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

