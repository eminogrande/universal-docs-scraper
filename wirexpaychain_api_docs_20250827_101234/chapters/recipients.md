# Recipients

The **Recipient APIs** provides a powerful interface for managing recipients and their payment details within a corporate environment. It enables seamless integration between fiat and crypto payout infrastructures, ensuring precise and compliant value transfers.

### Key Features:

- **Unified Recipient Management**:
    - Create and maintain recipient profiles for individuals and businesses with full support for KYC-aligned data structures.
    - Associate multiple payment methods per recipient to support complex disbursement needs.

- **Multi-Rail Payment Details Support**:
    - Add, update, and manage multiple payment methods per recipient, including SEPA, SWIFT, ACH, Faster Payments, cards, and crypto addresses.
    - Enforces field requirements dynamically based on payment method and recipient type.

- **Searchable & Scalable**:
    - Query recipients by name, currency, type, or catalog ID.
    - Optimized for high-volume use cases such as payroll, treasury, affiliate, and reward payouts.

- **Built-in Format & Compliance Checks**:
    - Enforces formatting and structure rules for IBANs, BICs, sort codes, routing numbers, PANs, and more.
    - Reduces manual QA and ensures readiness for downstream processing.

---

The Recipient API is designed for fintech platforms that require precision, speed, and flexibility in managing payees. Whether you're sending funds on-chain or off-chain, this section ensures your recipients are always payout-ready.

## GET /api/v1/recipients

**Summary:** Get recipients

**Description:** Retrieves all recipients sorted by the full name

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

## POST /api/v1/recipients

**Summary:** Create recipient

**Description:** Creates a new recipient with provided personal information

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

## GET /api/v1/recipients/filter/catalog

**Summary:** Get by catalog

**Description:** Retrieves recipients filtered by the catalog index. Catalog index is the first letter of the full name, so basically filtering by catalog index provides you with pretty much old yellow pages experience.

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| catalog_index | query | string | ✓ | First letter in the recipient full name. You can treat this parameter as a phone book index |
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

## GET /api/v1/recipients/filter/currency

**Summary:** Get by currency

**Description:** Retrieves recipients filtered by the availability of the requested currency among existing recipient payment details.

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| currency | query | string | ✓ | Currency in which the recipient should have details |
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

## GET /api/v1/recipients/filter/name

**Summary:** Get by name

**Description:** Retrieves recipients filtered by the presence of passed name substring in the full name of the recipient.

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| name | query | string | ✓ | String containing part of the recipient name that should be used to search for the recipient |
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

## GET /api/v1/recipients/filter/type

**Summary:** Get by type

**Description:** Retrieves recipients filtered by availability of the payment details of the passed type.

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| page_number | query | string |  | PageNumber number |
| page_size | query | string |  | Size of the page. If no page size is provided, default page size is used (25). |
| type | query | string | ✓ | Type of the details recipient should have |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

## DELETE /api/v1/recipients/{recipientId}

**Summary:** Delete recipient

**Description:** Deletes selected recipient

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| recipientId | path | string | ✓ | Unique identifier of the recipient on which the operation is to be performed |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

## GET /api/v1/recipients/{recipientId}

**Summary:** Get by catalog

**Description:** Retrieves single recipient by its id.

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| recipientId | path | string | ✓ | Unique identifier of the recipient on which the operation is to be performed |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

## PUT /api/v1/recipients/{recipientId}

**Summary:** Update recipient

**Description:** Updates recipient with provided personal information

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string | ✓ | Body data |
| recipientId | path | string | ✓ | Unique identifier of the recipient on which the operation is to be performed |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

## POST /api/v1/recipients/{recipientId}/payment_details

**Summary:** Create payment details

**Description:** Creates new payment details for existing recipient

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string | ✓ | Body data |
| recipientId | path | string | ✓ | Unique identifier of the recipient on which the operation is to be performed |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

## DELETE /api/v1/recipients/{recipientId}/payment_details/{paymentDetailsId}

**Summary:** Delete payment details

**Description:** Deletes payment details from existing recipient

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| paymentDetailsId | path | string | ✓ | Unique identifier of the payment details on which the operation is to be performed |
| recipientId | path | string | ✓ | Unique identifier of the recipient on which the operation is to be performed |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

## PUT /api/v1/recipients/{recipientId}/payment_details/{paymentDetailsId}

**Summary:** Update payment details

**Description:** Updates existing payment details for existing recipient

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string | ✓ | Body data |
| paymentDetailsId | path | string | ✓ | Unique identifier of the payment details on which the operation is to be performed |
| recipientId | path | string | ✓ | Unique identifier of the recipient on which the operation is to be performed |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

## POST /api/v1/recipients/{recipientId}/usage

**Summary:** Increment recipient usage

**Description:** Increments usage index on specified recipient. Usage index is later used to determine recipient's priority in the list of recipients.

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| recipientId | path | string | ✓ | Unique identifier of the recipient on which the operation is to be performed |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

