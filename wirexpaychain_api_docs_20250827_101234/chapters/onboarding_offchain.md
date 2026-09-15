# Onboarding/OffChain

Off-chain onboarding handles the **user’s presence in the Wirex backend**, allowing the system to manage non-sensitive metadata, orchestrate KYC flows, and enable services such as card issuance and transaction monitoring.

- Partners can choose between **server-side onboarding using Auth0** or **frontend integration via Privy SDK**.
- This flow includes registering the user in the off-chain system and obtaining authorization tokens for subsequent operations.

---

## Server-Side Onboarding (Auth0-Based)

### Description
This method is ideal for partners with their own backend infrastructure and existing user authentication systems. Partners collect and manage all required user information (e.g., email, wallet address, personal details) and use their **Auth0 server token** to perform onboarding actions via API.

### Key Requirements
  - Partner must have a secure authentication system in place to authorize each individual user.
  - Partner is responsible for collecting user details and ensuring data compliance.

### Typical Flow
  1. Authenticate via Auth0 to obtain a server token (see [Authorization > Auth0](#tag/Authorization/Auth0)).
  2. Register the user by making server-side API call to [Create user](#tag/User/paths/~1api~1v1~1user/post) with necessary data.
```bash
     curl --request POST \
     --url https://api-business.wirexpaychain.tech/api/v1/user \
     --header 'Authorization: Bearer {your_auth0_server_token}' \
     --header 'Content-Type: application/json' \
     --data '{
     "email": "a.grey@wirexpaychain.com",
     "country": "FR",
     "wallet_address": "0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf"
     }'
 ```
  3. Continue the onboarding flow (e.g., KYC, card issuance) using either [Auth0 server token authorization](#tag/Authorization/Auth0) or [Wirex token authorization](#tag/Authorization/Wirex-Pay-Token).

### Best For
Platforms that already manage their own user databases and require full backend control.

---

## Privy SDK

### Description
This method allows partners to offload identity and session management by integrating **Privy SDK** directly into their client application. Wirex provides a dedicated **AppId** that enables Privy to handle login, identity verification, and session persistence on behalf of the partner.

### Key Benefits
  - No need to implement or maintain a custom login flow.
  - Privy handles user authentication and provides tokens required for authorized API calls.
  - Reduced compliance and data handling overhead for the partner.

### Typical Flow
  1. Integrate the Privy SDK using the `AppId` provided by Wirex. For details on integrating SDK please follow [Privy SDK docs](https://docs.privy.io/basics/react/installation)
  2. Onboard the user via Privy to obtain access and identity tokens. **Please note that as a result of onboarding the registered user must have a linked email account and either a linked or an embedded wallet.**
  3. Register the user by making client-side API call to [Create retail user](#tag/User/paths/~1api~1v1~1user~1retail/post) with necessary data.
```bash
     curl --request POST \
     --url https://api-business.wirexpaychain.tech/api/v1/user/retail \
     --header 'Authorization: Bearer {your_privy_access_token}' \
     --header 'Identity: Bearer {your_privy_identity_token}' \
     --header 'Content-Type: application/json' \
     --data '{
     "country": "FR"
     }'
 ```
  4. Exchange Privy tokens for a **Wirex Token** (see [Authorization > Wirex Token](#tag/Authorization/Wirex-Pay-Token)).
  5. Use the Wirex Token to complete onboarding and initiate other user-specific operations (e.g., card activation, transaction initiation).

### Best For
Partners looking for a seamless, secure, and low-maintenance user onboarding experience.

---

By supporting both **backend-driven** and **embedded identity provider** flows, the Wirex BaaS API gives you the flexibility to tailor user onboarding to your product’s architecture—without compromising on security or decentralization.

## POST /api/v1/user

**Summary:** Create user

**Description:** Creates a new user in the Wirex system using server side Auth0 authorization.

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string |  | Body data |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

## POST /api/v1/user/retail

**Summary:** Create retail user

**Description:** Creates a new user in the Wirex system using client side Privy SDK authorization.

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string |  | Body data |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

## POST /api/v1/user/retail/validate

**Summary:** Create retail user

**Description:** Creates a new user in the Wirex system using client side Privy SDK authorization.

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string |  | Body data |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

