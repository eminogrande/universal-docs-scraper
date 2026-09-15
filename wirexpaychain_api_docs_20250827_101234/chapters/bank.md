# Bank

The **Bank APIs** section bridges traditional Web2 banking with non-custodial Web3 wallets using Account Abstraction (AA).

- **Automatic Account Creation**: All supported accounts would be created automatically upon registration. The user would be able to access their account details and manage their funds through the AA wallet. 

- **Fiat to Crypto**: Users can transfer fiat (EUR/GBP) from a traditional bank account to provided account details. The funds are automatically converted and deposited into their AA wallet as cryptocurrency.

- **Crypto to Fiat**: Users can send crypto from their AA wallet, which is converted and delivered as fiat to a traditional bank account (via IBAN, sort code, etc.).

This allows seamless value transfer between fiat and crypto systems while maintaining full user custody and control via smart contract wallets.

## GET /api/v1/bank/accounts

**Summary:** Get bank accounts

**Description:** Retrieves a list of bank accounts that belong to the user

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

## POST /api/v1/bank/accounts

**Summary:** Create bank account

**Description:** Activates bank account details for the specified account type

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

## POST /api/v1/bank/transfer

**Summary:** Execute bank transfer

**Description:** Executes the bank transfer either according to the estimation made previously or using current market rates.

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

## POST /api/v1/bank/transfer/estimate

**Summary:** Estimate bank transfer

**Description:** Estimates the amounts that would be charged for a bank transfer according to the current market rates.

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

## POST /api/v2/bank/transfer/estimate

**Summary:** Estimate bank transfer

**Description:** Estimates the amounts that would be charged for a bank transfer according to the current market rates.

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

