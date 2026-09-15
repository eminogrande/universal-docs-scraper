# Wirex BaaS API - Complete Documentation
**Version:** 1.0
**Base URL:** `https://api-business.wirexpaychain.tech`
**Generated:** 2025-08-27T10:17:49.554525

## Overview

The **Wirex BaaS API** enables partners to deliver non-custodial financial services directly to their retail users. Through a single integration, partners can onboard users, verify identities, issue smart wallet–linked cards, and enable crypto-backed bank transfers—without ever handling fiat or taking custody of user funds.
All transactions are powered by **user-owned smart wallets**, ensuring security, transparency, and full user control. Wirex acts as the infrastructure provider, so you can focus on building exceptional user experiences while we handle the heavy lifting.

## Abstract

The Wirex BaaS API enables partners to offer non-custodial cards and crypto-backed bank accounts to their retail users—directly from their own platforms. Powered by Wirex, this API provides secure infrastructure for onboarding users, managing wallets, and processing transactions, all while maintaining full user ownership of assets.

### Key Features:

**Embedded Financial Services:**
- Offer non-custodial card issuance and crypto-backed account functionality through your app or service.
- Enable retail users to spend, send, and receive funds without relinquishing control of their assets.

**Decentralized by Design:**
- Every user operates with a dedicated smart wallet—no custodial risk or pooled funds.
- Transactions are executed on-chain, ensuring full transparency and traceability.

**Seamless Integration:**
- Plug-and-play endpoints designed for smooth partner integration with minimal development effort.
- Backed by detailed documentation and hands-on support from the Wirex team.

**Compliance-Ready Infrastructure:**
- Built-in KYC hooks, including verification flows via Sumsub.
- Helps partners meet global compliance standards while retaining flexibility in user experience.

With the Wirex BaaS API, partners can launch next-gen financial experiences for their users—powered by Wirex's secure and scalable infrastructure, while keeping full control over branding, user engagement, and platform design.

## Onboarding

The onboarding process in the Wirex BaaS API is divided into two distinct but interconnected parts: on-chain onboarding and off-chain onboarding. Both are required to enable a fully functional non-custodial user experience within the Wirex ecosystem.

### On-Chain Onboarding

On-chain onboarding involves the creation of a smart wallet infrastructure for the user and their registration in the Wirex Accounts Contract. This is the foundation of the non-custodial model—ensuring that the user maintains full ownership and control over their assets through a decentralized Account Abstraction.

Each user must be provisioned with an Account Abstraction wallet, which can be created using ZeroDev. Once the wallet is created, the user must be registered on-chain in the Wirex Accounts Contract, linking their wallet to the system for identity and permission verification.

#### Key Components

**Account Abstraction Wallet:** A smart wallet owned by the user, deployed using ZeroDev. This wallet is used to authorize and execute on-chain transactions.

**ExecutionDelayPolicy:** A custom validation module that introduces a time-lock mechanism for specific user actions (e.g., fund transfers). This prevents users from front-running or reversing transactions after a card charge is initiated, adding a layer of fraud protection.

**FundsManagementExecutor:** A custom executor module that allows the Wirex platform to securely execute on-chain charge operations on behalf of the user for off-chain activities (e.g., card transactions, withdrawals).

**Contract Registry:** A smart contract deployed per supported chain that exposes addresses of key system components (like the Accounts contract, ExecutionDelayPolicy, and FundsManagementExecutor). The address of the registry will be provided by the Wirex team for each chain.

#### Requirements

To create an Account Abstraction wallet, the partner must either:
- Control a per-user private key, or
- Use an embedded wallet provider, such as Privy, which can return a signer via a connected wallet instance, or
- Use a form of wallet connection that would allow access to EIP1193 provider.

#### Steps to Complete On-Chain Onboarding

1. Create the Account Abstraction Wallet using ZeroDev SDK.
2. Install Custom Modules:
   - ExecutionDelayPolicy for time-locked security
   - FundsManagementExecutor for Wirex-controlled charges
3. Register the Wallet in the Accounts Contract, linking it with your PartnerId to finalize onboarding.

⚠️ The wallet must be fully deployed and both modules installed before registering the user on-chain.

#### Complete Example (JavaScript)

```javascript
import {ConnectedWallet} from '@privy-io/react-auth';
import {baseSepolia} from 'viem/chains';

// Complete implementation example would go here
// This shows integration with Privy SDK and ZeroDev
```

### Off-Chain Onboarding

Off-chain onboarding handles the user's presence in the Wirex backend, allowing the system to manage non-sensitive metadata, orchestrate KYC flows, and enable services such as card issuance and transaction monitoring.

Partners can choose between server-side onboarding using Auth0 or frontend integration via Privy SDK. This flow includes registering the user in the off-chain system and obtaining authorization tokens for subsequent operations.

#### Server-Side Onboarding (Auth0-Based)

**Description:** This method is ideal for partners with their own backend infrastructure and existing user authentication systems. Partners collect and manage all required user information (e.g., email, wallet address, personal details) and use their Auth0 server token to perform onboarding actions via API.

**Key Requirements:**
- Partner must have a secure authentication system in place to authorize each individual user.
- Partner is responsible for collecting user details and ensuring data compliance.

**Typical Flow:**
1. Authenticate via Auth0 to obtain a server token (see Authorization > Auth0).
2. Register the user by making server-side API call to Create user with necessary data.

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

3. Continue the onboarding flow (e.g., KYC, card issuance) using either Auth0 server token authorization or Wirex token authorization.

**Best For:** Platforms that already manage their own user databases and require full backend control.

#### Privy SDK Integration

**Description:** This method allows partners to offload identity and session management by integrating Privy SDK directly into their client application. Wirex provides a dedicated AppId that enables Privy to handle login, identity verification, and session persistence on behalf of the partner.

**Key Benefits:**
- No need to implement or maintain a custom login flow.
- Privy handles user authentication and provides tokens required for authorized API calls.
- Reduced compliance and data handling overhead for the partner.

**Typical Flow:**
1. Integrate the Privy SDK using the AppId provided by Wirex. For details on integrating SDK please follow Privy SDK docs
2. Onboard the user via Privy to obtain access and identity tokens. Please note that as a result of onboarding the registered user must have a linked email account and either a linked or an embedded wallet.
3. Register the user by making client-side API call to Create retail user with necessary data.

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

4. Exchange Privy tokens for a Wirex Token (see Authorization > Wirex Token).
5. Use the Wirex Token to complete onboarding and initiate other user-specific operations (e.g., card activation, transaction initiation).

**Best For:** Partners looking for a seamless, secure, and low-maintenance user onboarding experience.

## Authorization

The Wirex BaaS API supports multiple authorization flows to meet varying integration needs. Whether you operate a backend system or embed authentication directly into your frontend, the platform supports flexible and secure methods for accessing user-specific resources.

### Anonymous
**Description:** Public routes that require no authentication or authorization. These are typically informational or infrastructure-level endpoints.

**Example Use Case:** Checking system status or retrieving static documentation.

### Auth0
**Description:** Best suited for partners with their own backend, user database, and established authentication methods. This flow uses a server-side token to access and act on behalf of any user managed by the partner.

**How to Obtain the Token:**
Use the Client Credentials Grant flow by making a request to Auth0's token endpoint:

```bash
curl --request POST \
  --url https://{authorization_provider_domain}/oauth/token \
  --header 'content-type: application/json' \
  --data '{
    "client_id": "{your_client_id}",
    "client_secret": "{your_client_secret}",
    "audience": "{api_host_you_want_to_access}",
    "grant_type": "client_credentials"
  }'
```

**Example for Wirex BaaS Sandbox:**

```bash
curl --request POST \
  --url https://wirex-pay-dev.eu.auth0.com/oauth/token \
  --header 'content-type: application/json' \
  --data '{
    "client_id": "{your_client_id}",
    "client_secret": "{your_client_secret}",
    "audience": "https://api-business.wirexpaychain.tech",
    "grant_type": "client_credentials"
  }'
```

**Example Response:**

```json
{
  "access_token": "{your_access_token}",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

**Required authorization credentials:**
- Authorization: Auth0 server access token.
- One of:
  - X-User-Email: Email associated with the user on whose behalf the request should be made.
  - X-User-Wallet: Crypto wallet address associated with the user on whose behalf the request should be made.
  - X-User-Id: Wirex system identifier of the user.
- X-Chain-Id: EIP155 id of the chain for which you want this request to be executed

**Use Cases:**
- Performing any requests on behalf of any the user
- Registering new users

### Wirex Token
**Description:** This token is issued by Wirex and is tied to a specific user. It's used to authorize direct, user-specific operations—typically in frontend or delegated flows.

**How to Obtain the Token:**
You can obtain a Wirex token in two ways:

#### Using Auth0 Server Token

```bash
curl --request POST \
  --url https://api-business.wirexpaychain.tech/api/v1/user/authorize \
  --header 'Authorization: Bearer {your_auth0_access_token}' \
  --header 'X-User-Email: a.grey@wirexpaychain.com' \
  --header 'X-Chain-Id: 1001996' \
  --header 'Content-Type: application/json'
```

**Response:**

```json
{
  "token": "{wirex_pay_user_token}"
}
```

#### Using Privy SDK

```javascript
import {useIdentityToken, useToken, usePrivy} from '@privy-io/react-auth';

function getPrivyTokens() {
  const {getAccessToken} = useToken();
  const {identityToken} = useIdentityToken();
  const {ready, user} = usePrivy();
  useEffect(() => {
    if (user && ready) {
      getAccessToken().then((accessToken) => {
        console.log('access token: ', accessToken);
        console.log('identity token: ', identityToken);
      });
    }
  }, [ready, user]);
}
```

### Summary of Authorization Flows

| Flow Type | Headers | Use Case |
|-----------|---------|----------|
| Anonymous | None | Public routes, no authentication required |
| Auth0 | Authorization (Auth0 server token) + (X-User-Email/X-User-Wallet/X-User-Id) + X-Chain-Id | Server-side access to perform operations on behalf of any user |
| Wirex Token | Authorization (user token) | Frontend or delegated access for specific user actions |

## API Endpoints

### Activity Feed

#### GET /api/v1/activity/feed

**Get activity feed**

Retrieves both transactional and non-transactional activities for the user

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| page_number | query | string |  | PageNumber number |
| page_size | query | string |  | Size of the page. If no page size is provided, default page size is used (25). |
| subject | query | string |  | Filter by subject (wallet address, card ID, or account reference) (<span style="color:red">SHOULD NOT</span> be provided if types are provided) |
| types | query | string |  | Filter by activity types (<span style="color:red">SHOULD NOT</span> be provided if subject is provided) |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### GET /api/v1/withdrawal/requests

**Get requested erc withdrawals**

Retrieves requested erc withdrawals for provided account address

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

### Authorization

#### POST /api/v1/user/authorize

**Login as user**

Retrieve access token for a specific user that can be used to interact with all other APIs on his behalf

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string |  | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

### Bank

#### GET /api/v1/bank/accounts

**Get bank accounts**

Retrieves a list of bank accounts that belong to the user

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| page_number | query | string |  | PageNumber number |
| page_size | query | string |  | Size of the page. If no page size is provided, default page size is used (25). |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### POST /api/v1/bank/accounts

**Create bank account**

Activates bank account details for the specified account type

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string | ✓ | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### POST /api/v1/bank/transfer

**Execute bank transfer**

Executes the bank transfer either according to the estimation made previously or using current market rates.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string | ✓ | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### POST /api/v1/bank/transfer/estimate

**Estimate bank transfer**

Estimates the amounts that would be charged for a bank transfer according to the current market rates.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string | ✓ | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### POST /api/v2/bank/transfer/estimate

**Estimate bank transfer**

Estimates the amounts that would be charged for a bank transfer according to the current market rates.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string | ✓ | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

### Cards

#### GET /api/v1/cards

**Get cards**

Retrieves list of cards that belong to the user

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| page_number | query | string |  | PageNumber number |
| page_size | query | string |  | Size of the page. If no page size is provided, default page size is used (25). |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

### Cards/3DS

#### GET /api/v1/cards/3ds/requests

**Get active requests**

Retrieves active 3DS requests that need to be either approved or declined

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### POST /api/v1/cards/3ds/requests/{transactionId}/approve

**Approve request**

Approves 3DS request allowing the transaction to proceed

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| transactionId | path | string | ✓ | Identifier of transaction for which 3DS decision is made |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### POST /api/v1/cards/3ds/requests/{transactionId}/decline

**Decline request**

Declines 3DS request blocking the transaction from proceeding

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| transactionId | path | string | ✓ | Identifier of transaction for which 3DS decision is made |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

### Cards/Delivery

#### GET /api/v1/cards/delivery/countries

**Get delivery countries**

Retrieves list of countries where the card can be delivered for the current corporation</br> > **Note:** This method is applicable only if your account manager has advised you to incorporate card fee handling as part of your integration process.

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### GET /api/v1/cards/delivery/methods/{country}

**Get delivery methods**

Retrieves list of courier providers that can deliver the card to the specified country</br> > **Note:** This method is applicable only if your account manager has advised you to incorporate card fee handling as part of your integration process.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| country | path | string | ✓ | Country where the card should be delivered (ISO 3166-1 alpha-2) |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

### Cards/Details

#### POST /api/v1/cards/{cardId}/cvv

**Get card CVV**

Retrieves CVV code for the card using the action confirmation token generated using the **Confirmation** flow

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| cardId | path | string | ✓ | Id of the card on which the action should be performed |
| bodyData | body | string | ✓ | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### POST /api/v1/cards/{cardId}/details

**Get card details**

Retrieves card PAN and expiry date using the action confirmation token generated using the **Confirmation** flow

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| cardId | path | string | ✓ | Id of the card on which the action should be performed |
| bodyData | body | string | ✓ | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### POST /api/v1/cards/{cardId}/pin

**Get card pin**

Retrieves card Pin code using the action confirmation token generated using the **Confirmation** flow

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| cardId | path | string | ✓ | Id of the card on which the action should be performed |
| bodyData | body | string | ✓ | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

### Cards/Fees

#### GET /api/v1/cards/{type}/fees/{country}

**Get order fees**

Retrieves estimation of fees that should be paid for the card order</br> > **Note:** This method is applicable only if your account manager has advised you to incorporate card fee handling as part of your integration process.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| country | path | string | ✓ | Country in which the card will be issued (ISO 3166-1 alpha-2) |
| type | path | string | ✓ | Format of the card the fees should be calculated for |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### POST /api/v1/cards/{type}/fees/{country}/payment

**Create order fees invoice**

Creates an invoice for payment of the card order fees.</br> > **Note:** This method is applicable only if your account manager has advised you to incorporate card fee handling as part of your integration process.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| country | path | string | ✓ | Country in which the card will be issued (ISO 3166-1 alpha-2) |
| type | path | string | ✓ | Format of the card the fees should be calculated for |
| bodyData | body | string | ✓ | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

### Cards/Issuance

#### POST /api/v1/cards/plastic

**Issue plastic card**

Issues a plastic card for the specified user and sends it to the provided address.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string | ✓ | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### POST /api/v1/cards/virtual

**Issue virtual card**

Issues a virtual card for the specified user

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string | ✓ | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### PUT /api/v1/cards/{cardId}/activate

**Activate card**

Activates a card that has been issues to a user and is currently in **NotActivated** state. </br> **Note:** This endpoint is needed only for physical cards to provide additional layer of security in case the card is stolen during delivery.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string | ✓ | Body data |
| cardId | path | string | ✓ | Id of the card on which the action should be performed |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

### Cards/Management

#### PUT /api/v1/cards/{cardId}/block

**Block card**

Blocks selected card making it impossible to use it for any transactions.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| cardId | path | string | ✓ | Id of the card on which the action should be performed |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### PUT /api/v1/cards/{cardId}/close

**Close card**

Closes the card. This action cannot be undone and the card will be permanently closed.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| cardId | path | string | ✓ | Id of the card on which the action should be performed |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### PUT /api/v1/cards/{cardId}/limit

**Change card limit**

Updates maximum amount that can be spent using the card within a day

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| cardId | path | string | ✓ | Id of the card on which the action should be performed |
| bodyData | body | string | ✓ | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### PUT /api/v1/cards/{cardId}/name

**Change card name**

Updates the display name of the card

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| cardId | path | string | ✓ | Id of the card on which the action should be performed |
| bodyData | body | string | ✓ | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### PUT /api/v1/cards/{cardId}/unblock

**Unblock card**

Unblocks selected card allowing it to be used for transactions once again.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| cardId | path | string | ✓ | Id of the card on which the action should be performed |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

### Confirmation

#### POST /api/v1/confirmation/sms

**Request SMS code**

Sends an SMS to the phone number that was provided by user during KYC process with OTP code.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string | ✓ | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### POST /api/v1/confirmation/sms/verify

**Verify SMS code**

Exchanges an OTP code send via SMS for an action token that can be used to confirm that the action being executed is approved by end-user

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string | ✓ | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

### KYC

#### GET /api/v1/user/sharing-token

**Get KYC sharing token**

Returns a SumSub sharing token that can be used to retrieve the information submitted by the user during the KYC process.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| sumsub_client_id | query | string | ✓ | Identifier of the partner in SumSub system. This identifier is used to tell SumSub with which entity the information should be shared. Please consult SumSub docs on where to get this id. |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### POST /api/v1/user/sharing-token

**Set KYC sharing token**

Uses KYC sharing token retrieved from SumSub to ingest user data and perform verification

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string |  | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### POST /api/v1/user/verification-link

**Get KYC SDK link**

Generates a verification link for the user to verify his account. </br>

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string |  | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### POST /api/v1/user/verification-token

**Get KYC SDK token**

Retrieves an SDK token for initializing the SumSub SDK. </br>

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string |  | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

### Onboarding/OffChain

#### POST /api/v1/user

**Create user**

Creates a new user in the Wirex system using server side Auth0 authorization.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string |  | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### POST /api/v1/user/retail

**Create retail user**

Creates a new user in the Wirex system using client side Privy SDK authorization.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string |  | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### POST /api/v1/user/retail/validate

**Create retail user**

Creates a new user in the Wirex system using client side Privy SDK authorization.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string |  | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

### Rates

#### GET /api/v1/rates

**Get rates**

Retrieves real-time exchange rates for a list of provided tickers. Each ticker represents a currency or asset pair (e.g., `USDT/USD`, `DAI/EUR`). The response includes the latest conversion rate for each requested

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| tickers | query | string | ✓ |  |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

### Recipients

#### GET /api/v1/recipients

**Get recipients**

Retrieves all recipients sorted by the full name

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| page_number | query | string |  | PageNumber number |
| page_size | query | string |  | Size of the page. If no page size is provided, default page size is used (25). |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### POST /api/v1/recipients

**Create recipient**

Creates a new recipient with provided personal information

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string | ✓ | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### GET /api/v1/recipients/filter/catalog

**Get by catalog**

Retrieves recipients filtered by the catalog index. Catalog index is the first letter of the full name, so basically filtering by catalog index provides you with pretty much old yellow pages experience.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| catalog_index | query | string | ✓ | First letter in the recipient full name. You can treat this parameter as a phone book index |
| page_number | query | string |  | PageNumber number |
| page_size | query | string |  | Size of the page. If no page size is provided, default page size is used (25). |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### GET /api/v1/recipients/filter/currency

**Get by currency**

Retrieves recipients filtered by the availability of the requested currency among existing recipient payment details.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| currency | query | string | ✓ | Currency in which the recipient should have details |
| page_number | query | string |  | PageNumber number |
| page_size | query | string |  | Size of the page. If no page size is provided, default page size is used (25). |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### GET /api/v1/recipients/filter/name

**Get by name**

Retrieves recipients filtered by the presence of passed name substring in the full name of the recipient.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| name | query | string | ✓ | String containing part of the recipient name that should be used to search for the recipient |
| page_number | query | string |  | PageNumber number |
| page_size | query | string |  | Size of the page. If no page size is provided, default page size is used (25). |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### GET /api/v1/recipients/filter/type

**Get by type**

Retrieves recipients filtered by availability of the payment details of the passed type.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| page_number | query | string |  | PageNumber number |
| page_size | query | string |  | Size of the page. If no page size is provided, default page size is used (25). |
| type | query | string | ✓ | Type of the details recipient should have |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### DELETE /api/v1/recipients/{recipientId}

**Delete recipient**

Deletes selected recipient

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| recipientId | path | string | ✓ | Unique identifier of the recipient on which the operation is to be performed |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### GET /api/v1/recipients/{recipientId}

**Get by catalog**

Retrieves single recipient by its id.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| recipientId | path | string | ✓ | Unique identifier of the recipient on which the operation is to be performed |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### PUT /api/v1/recipients/{recipientId}

**Update recipient**

Updates recipient with provided personal information

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string | ✓ | Body data |
| recipientId | path | string | ✓ | Unique identifier of the recipient on which the operation is to be performed |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### POST /api/v1/recipients/{recipientId}/payment_details

**Create payment details**

Creates new payment details for existing recipient

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string | ✓ | Body data |
| recipientId | path | string | ✓ | Unique identifier of the recipient on which the operation is to be performed |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### DELETE /api/v1/recipients/{recipientId}/payment_details/{paymentDetailsId}

**Delete payment details**

Deletes payment details from existing recipient

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| paymentDetailsId | path | string | ✓ | Unique identifier of the payment details on which the operation is to be performed |
| recipientId | path | string | ✓ | Unique identifier of the recipient on which the operation is to be performed |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### PUT /api/v1/recipients/{recipientId}/payment_details/{paymentDetailsId}

**Update payment details**

Updates existing payment details for existing recipient

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string | ✓ | Body data |
| paymentDetailsId | path | string | ✓ | Unique identifier of the payment details on which the operation is to be performed |
| recipientId | path | string | ✓ | Unique identifier of the recipient on which the operation is to be performed |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### POST /api/v1/recipients/{recipientId}/usage

**Increment recipient usage**

Increments usage index on specified recipient. Usage index is later used to determine recipient's priority in the list of recipients.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| recipientId | path | string | ✓ | Unique identifier of the recipient on which the operation is to be performed |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

### Statements

#### POST /api/v1/statements

**Get financial statement**

Retrieves financial statement for given period. Returns statement_id in case statement is pending to generate, otherwise returns full object. Upon statement generation ws server will notify with id and owner

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string | ✓ | Body data |

**Responses:**

- **200:** OK
- **202:** Accepted
- **400:** Bad Request
- **500:** Internal Server Error

---

### Test

#### GET /api/v1/test/{type}

**Test api request parsing**

This one exists only to test that API request parsing works correctly from body, query, path and header

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| status | query | string | ✓ |  |
| type | path | string | ✓ |  |
| X-Aud | header | string | ✓ |  |
| bodyData | body | string | ✓ | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

### Transactions

#### GET /api/v1/transactions/card

**Get card transactions**

Reads a page of card transactions associated with user

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| page_number | query | string |  | PageNumber number |
| page_size | query | string |  | Size of the page. If no page size is provided, default page size is used (25). |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

### User Management

#### GET /api/v1/user

**Get user**

Retrieves the user data stored in Wirex system

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string |  | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### PUT /api/v1/user/freshdesk-id

**Update freshdesk id**

Updates freshdesk id of the user that can be used to restore omni-chats down the road.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string |  | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### PUT /api/v1/user/phone-number

**Update phone number**

Update the phone number of a specific user in the system.</br>This endpoint allows updating and validating the user's phone number to maintain account security and contact accuracy.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string |  | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

#### PUT /api/v1/user/phone-number/confirm

**Confirm phone number**

Update the phone number of a specific user in the system.</br>This endpoint allows updating and validating the user's phone number to maintain account security and contact accuracy.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string |  | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

### Wallet

#### GET /api/v1/wallet

**Get wallets**

Retrieves user wallet along with its balances. By wallet this API suggests a valid Account Abstraction wallet that was linked during the registration.

**Parameters:**

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string | ✓ | Body data |

**Responses:**

- **200:** OK
- **400:** Bad Request
- **500:** Internal Server Error

---

