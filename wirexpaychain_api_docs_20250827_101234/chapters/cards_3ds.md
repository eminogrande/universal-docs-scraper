# Cards/3DS

The **Card 3DS APIs** enable clients to securely manage 3D Secure (3DS) authentication requests initiated during card transactions.

### Key Capabilities

- **Retrieve Active Challenges**: Access pending 3DS requests that require user action.
- **Approve or Reject**: Handle a specific challenge using an action token acquired from the [Confirmation](#tag/Confirmation) section.

### Security

All challenge responses require a valid, signed action token to confirm that the user has explicitly authorized the operation with their
private key.

> This section ensures robust authentication for sensitive card activities, preventing unauthorized use and supporting compliance with 3DS protocols.

## GET /api/v1/cards/3ds/requests

**Summary:** Get active requests

**Description:** Retrieves active 3DS requests that need to be either approved or declined

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

## POST /api/v1/cards/3ds/requests/{transactionId}/approve

**Summary:** Approve request

**Description:** Approves 3DS request allowing the transaction to proceed

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| transactionId | path | string | ✓ | Identifier of transaction for which 3DS decision is made |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

## POST /api/v1/cards/3ds/requests/{transactionId}/decline

**Summary:** Decline request

**Description:** Declines 3DS request blocking the transaction from proceeding

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| transactionId | path | string | ✓ | Identifier of transaction for which 3DS decision is made |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

