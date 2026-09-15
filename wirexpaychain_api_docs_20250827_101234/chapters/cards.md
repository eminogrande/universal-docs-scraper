# Cards

The **Card API** allows partners to seamlessly issue and manage virtual or plastic cards for retail users via a non-custodial wallet infrastructure. It supports the full card lifecycle, from issuance and activation to spending controls and secure card data access—all designed for scalable partner integration.

### Key Features:

- **Retail Card Issuance**:
  - Instantly issue virtual or plastic cards for retail users.
  - Support for user-defined card names and physical delivery with address and courier preferences.
  - Designed for smooth partner onboarding and activation flows.

- **Lifecycle Management**:
  - Activate cards securely using last four digits and expiry date confirmation.
  - Enable, disable, or deactivate cards via API to maintain full control.

- **Spending Limit Configuration**:
  - Provide user with spending controls to limit the amount that can be withdrawn from the account in one day.

- **Wallet-Based Payments**:
  - All issued cards are linked to a user's smart wallet for non-custodial, on-chain payment support.

- **Secure Card Data Access**:
  - Retrieve sensitive card information using secure, permissioned API flows backed by user confirmation and smart contract validation.

---

## GET /api/v1/cards

**Summary:** Get cards

**Description:** Retrieves list of cards that belong to the user

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

