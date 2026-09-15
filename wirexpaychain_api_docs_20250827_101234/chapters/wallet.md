# Wallet

The **Wallet APIs** provide you with an ability to read details of your on-chain AA wallet including its address and balances

## GET /api/v1/wallet

**Summary:** Get wallets

**Description:** Retrieves user wallet along with its balances. By wallet this API suggests a valid Account Abstraction wallet that was linked during the registration.

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

