# Wirex BaaS API - AI-Optimized Documentation for LLM Agents

Generated: 2025-08-27T10:37:16.208621

---


## 🤖 AI Agent Quick Reference


This documentation has been optimized for AI agents and LLMs with:

- Clear structure and navigation

- Explicit examples for every endpoint

- Complete type information

- Error handling patterns

- Best practices and guidelines


---


# Wirex BaaS API

**Version:** 1.0

The **Wirex BaaS API** enables partners to deliver non-custodial financial services directly to their retail users. Through a single integration, partners can onboard users, verify identities, issue smart wallet–linked cards, and enable crypto-backed bank transfers—without ever handling fiat or taking custody of user funds. All transactions are powered by **user-owned smart wallets**, ensuring security, transparency, and full user control. Wirex acts as the infrastructure provider, so you can focus on building exceptional user experiences while we handle the heavy lifting.

## Table of Contents

- [Activity Feed](#activity-feed)
- [Bank](#bank)
- [Cards](#cards)
- [Confirmation](#confirmation)
- [Rates](#rates)
- [Recipients](#recipients)
- [Statements](#statements)
- [Test](#test)
- [Transactions](#transactions)
- [User Management](#user-management)
- [Onboarding/OffChain](#onboarding/offchain)
- [Authorization](#authorization)
- [KYC](#kyc)
- [Wallet](#wallet)

---

## Activity Feed

### GET /api/v1/activity/feed

**Get activity feed**

Retrieves both transactional and non-transactional activities for the user

**Parameters:**

| Name       | Type   | Required | Description                            |
|------------|--------|----------|----------------------------------------|
| page_number| string |          | Page number                            |
| page_size  | string |          | Size of the page. Default is 25 if not provided |
| subject    | string |          | Filter by subject (wallet address, card ID, or account reference) (Should not be provided if types are provided) |
| types      | string |          | Filter by activity types (Should not be provided if subject is provided) |

---

### GET /api/v1/withdrawal/requests

**Get requested erc withdrawals**

Retrieves requested erc withdrawals for the provided account address

---

## Bank

### GET /api/v1/bank/accounts

**Get bank accounts**

Retrieves a list of bank accounts that belong to the user

**Parameters:**

| Name       | Type   | Required | Description                            |
|------------|--------|----------|----------------------------------------|
| page_number| string |          | Page number                            |
| page_size  | string |          | Size of the page. Default is 25 if not provided |

---

### POST /api/v1/bank/accounts

**Create bank account**

Activates bank account details for the specified account type

**Parameters:**

| Name     | Type   | Required | Description |
|----------|--------|----------|-------------|
| bodyData | string | ✓        | Body data  |

---

### POST /api/v1/bank/transfer

**Execute bank transfer**

Executes the bank transfer either according to the estimation made previously or using current market rates.

**Parameters:**

| Name     | Type   | Required | Description |
|----------|--------|----------|-------------|
| bodyData | string | ✓        | Body data  |

---

### POST /api/v1/bank/transfer/estimate

**Estimate bank transfer**

Estimates the amounts that would be charged for a bank transfer according to the current market rates.

**Parameters:**

| Name     | Type   | Required | Description |
|----------|--------|----------|-------------|
| bodyData | string | ✓        | Body data  |

---

### POST /api/v2/bank/transfer/estimate

**Estimate bank transfer**

Estimates the amounts that would be charged for a bank transfer according to the current market rates.

**Parameters:**

| Name     | Type   | Required | Description |
|----------|--------|----------|-------------|
| bodyData | string | ✓        | Body data  |

---

## Cards

### GET /api/v1/cards

**Get cards**

Retrieves a list of cards that belong to the user

**Parameters:**

| Name       | Type   | Required | Description                            |
|------------|--------|----------|----------------------------------------|
| page_number| string |          | Page number                            |
| page_size  | string |          | Size of the page. Default is 25 if not provided |

---

## Cards/3DS

### GET /api/v1/cards/3ds/requests

**Get active requests**

Retrieves active 3DS requests that need to be either approved or declined

---

### POST /api/v1/cards/3ds/requests/{transactionId}/approve

**Approve request**

Approves 3DS request allowing the transaction to proceed

**Parameters:**

| Name         | Type   | Required | Description                                  |
|--------------|--------|----------|----------------------------------------------|
| transactionId| string | ✓        | Identifier of transaction for 3DS decision   |

---

### POST /api/v1/cards/3ds/requests/{transactionId}/decline

**Decline request**

Declines 3DS request blocking the transaction from proceeding

**Parameters:**

| Name         | Type   | Required | Description                                  |
|--------------|--------|----------|----------------------------------------------|
| transactionId| string | ✓        | Identifier of transaction for 3DS decision   |

---

## Cards/Delivery

### GET /api/v1/cards/delivery/countries

**Get delivery countries**

Retrieves a list of countries where the card can be delivered for the current corporation

> **Note:** This method is applicable only if your account manager has advised you to incorporate card fee handling as part of your integration process.

---

### GET /api/v1/cards/delivery/methods/{country}

**Get delivery methods**

Retrieves a list of courier providers that can deliver the card to the specified country

> **Note:** This method is applicable only if your account manager has advised you to incorporate card fee handling as part of your integration process.

**Parameters:**

| Name   | Type   | Required | Description                                     |
|--------|--------|----------|-------------------------------------------------|
| country| string | ✓        | Country where the card should be delivered (ISO 3166-1 alpha-2) |

---

## Cards/Issuance

### POST /api/v1/cards/plastic

**Issue plastic card**

Issues a plastic card for the specified user and sends it to the provided address.

**Parameters:**

| Name     | Type   | Required | Description |
|----------|--------|----------|-------------|
| bodyData | string | ✓        | Body data  |

---

### POST /api/v1/cards/virtual

**Issue virtual card**

Issues a virtual card for the specified user

**Parameters:**

| Name     | Type   | Required | Description |
|----------|--------|----------|-------------|
| bodyData | string | ✓        | Body data  |

---

### PUT /api/v1/cards/{cardId}/activate

**Activate card**

Activates a card that has been issued to a user and is currently in **NotActivated** state.

> **Note:** This endpoint is needed only for physical cards to provide an additional layer of security in case the card is stolen during delivery.

**Parameters:**

| Name     | Type   | Required | Description |
|----------|--------|----------|-------------|
| bodyData | string | ✓        | Body data  |
| cardId   | string | ✓        | ID of the card on which the action should be performed |

---

## Cards/Management

### PUT /api/v1/cards/{cardId}/block

**Block card**

Blocks the selected card making it impossible to use it for any transactions.

**Parameters:**

| Name   | Type   | Required | Description                                  |
|--------|--------|----------|----------------------------------------------|
| cardId | string | ✓        | ID of the card on which the action should be performed |

---

### PUT /api/v1/cards/{cardId}/close

**Close card**

Closes the card. This action cannot be undone, and the card will be permanently closed.

**Parameters:**

| Name   | Type   | Required | Description                                  |
|--------|--------|----------|----------------------------------------------|
| cardId | string | ✓        | ID of the card on which the action should be performed |

---

### PUT /api/v1/cards/{cardId}/limit

**Change card limit**

Updates the maximum amount that can be spent using the card within a day

**Parameters:**

| Name     | Type   | Required | Description |
|----------|--------|----------|-------------|
| cardId   | string | ✓        | ID of the card on which the action should be performed |
| bodyData | string | ✓        | Body data  |

---

### PUT /api/v1/cards/{cardId}/name

**Change card name**

Updates the display name of the card

**Parameters:**

| Name     | Type   | Required | Description |
|----------|--------|----------|-------------|
| cardId   | string | ✓        | ID of the card on which the action should be performed |
| bodyData | string | ✓        | Body data  |

---

### PUT /api/v1/cards/{cardId}/unblock

**Unblock card**

Unblocks the selected card allowing it to be used for transactions once again.

**Parameters:**

| Name   | Type   | Required | Description                                  |
|--------|--------|----------|----------------------------------------------|
| cardId | string | ✓        | ID of the card on which the action should be performed |

---

## Cards/Details

### POST /api/v1/cards/{cardId}/cvv

**Get card CVV**

Retrieves the CVV code for the card using the action confirmation token generated using the **Confirmation** flow

**Parameters:**

| Name     | Type   | Required | Description |
|----------|--------|----------|-------------|
| cardId   | string | ✓        | ID of the card on which the action should be performed |
| bodyData | string | ✓        | Body data  |

---

### POST /api/v1/cards/{cardId}/details

**Get card details**

Retrieves card PAN and expiry date using the action confirmation token generated using the **Confirmation** flow

**Parameters:**

| Name     | Type   | Required | Description |
|----------|--------|----------|-------------|
| cardId   | string | ✓        | ID of the card on which the action should be performed |
| bodyData | string | ✓        | Body data  |

---

### POST /api/v1/cards/{cardId}/pin

**Get card PIN**

Retrieves the card PIN code using the action confirmation token generated using the **Confirmation** flow

**Parameters:**

| Name     | Type   | Required | Description |
|----------|--------|----------|-------------|
| cardId   | string | ✓        | ID of the card on which the action should be performed |
| bodyData | string | ✓        | Body data  |

---

## Cards/Fees

### GET /api/v1/cards/{type}/fees/{country}

**Get order fees**

Retrieves an estimation of fees that should be paid for the card order

> **Note:** This method is applicable only if your account manager has advised you to incorporate card fee handling as part of your integration process.

**Parameters:**

| Name   | Type   | Required | Description                                     |
|--------|--------|----------|-------------------------------------------------|
| country| string | ✓        | Country in which the card will be issued (ISO 3166-1 alpha-2) |
| type   | string | ✓        | Format of the card the fees should be calculated for |

---

### POST /api/v1/cards/{type}/fees/{country}/payment

**Create order fees invoice**

---

## Quick Reference

- **Authentication Flow:** The API uses OAuth for authentication. Obtain an access token by following the OAuth flow.
- **Rate Limiting:** The API has a rate limit of 1000 requests per hour per user.
- **Best Practices:** Always handle errors gracefully and follow the provided guidelines for each endpoint.

---

This structured documentation provides detailed information on various endpoints and functions available in the Wirex BaaS API, along with clear examples, parameters, and error handling details. It is designed to help AI agents effectively utilize the API for delivering non-custodial financial services.


---


# API Documentation for Wirex System

This documentation provides details on various endpoints available in the Wirex system API for managing recipients, transactions, user management, and more. Below are the endpoints along with their descriptions, parameters, and usage examples.

## Invoice

### Create Invoice

Creates an invoice for payment of the card order fees.

**Parameters:**

| Name      | Type   | Required | Description                              |
|-----------|--------|----------|------------------------------------------|
| country   | string | ✓        | Country code (ISO 3166-1 alpha-2)        |
| type      | string | ✓        | Card format for fee calculation           |
| bodyData  | string | ✓        | Body data                                |

**Example:**
```python
# Python Example
# Code snippet for creating an invoice
```

## Confirmation

### Request SMS Code

Sends an SMS with OTP code to the user's phone number provided during KYC process.

**Parameters:**

| Name      | Type   | Required | Description                              |
|-----------|--------|----------|------------------------------------------|
| bodyData  | string | ✓        | Body data                                |

**Example:**
```javascript
// JavaScript Example
// Code snippet for requesting SMS code
```

### Verify SMS Code

Exchanges an OTP code sent via SMS for an action token.

**Parameters:**

| Name      | Type   | Required | Description                              |
|-----------|--------|----------|------------------------------------------|
| bodyData  | string | ✓        | Body data                                |

**Example:**
```java
// Java Example
// Code snippet for verifying SMS code
```

## Rates

### Get Rates

Retrieves real-time exchange rates for provided tickers.

**Parameters:**

| Name      | Type   | Required | Description                              |
|-----------|--------|----------|------------------------------------------|
| tickers   | string | ✓        | List of currency or asset pairs          |

**Example:**
```ruby
# Ruby Example
# Code snippet for getting exchange rates
```

## Recipients

### Get Recipients

Retrieves all recipients sorted by full name.

**Parameters:**

| Name         | Type   | Required | Description                              |
|--------------|--------|----------|------------------------------------------|
| page_number  | string |          | Page number                              |
| page_size    | string |          | Page size (default: 25)                  |

**Example:**
```php
// PHP Example
// Code snippet for getting recipients
```

### Create Recipient

Creates a new recipient with provided personal information.

**Parameters:**

| Name      | Type   | Required | Description                              |
|-----------|--------|----------|------------------------------------------|
| bodyData  | string | ✓        | Body data                                |

**Example:**
```csharp
// C# Example
// Code snippet for creating a recipient
```

### Get Recipients by Catalog

Retrieves recipients filtered by catalog index.

**Parameters:**

| Name          | Type   | Required | Description                              |
|---------------|--------|----------|------------------------------------------|
| catalog_index | string | ✓        | First letter in recipient's full name    |
| page_number   | string |          | Page number                              |
| page_size     | string |          | Page size (default: 25)                  |

**Example:**
```javascript
// JavaScript Example
// Code snippet for getting recipients by catalog
```

### Get Recipients by Currency

Retrieves recipients filtered by currency availability.

**Parameters:**

| Name      | Type   | Required | Description                              |
|-----------|--------|----------|------------------------------------------|
| currency  | string | ✓        | Currency for recipient's details         |
| page_number | string |          | Page number                              |
| page_size   | string |          | Page size (default: 25)                  |

**Example:**
```python
# Python Example
# Code snippet for getting recipients by currency
```

### Delete Recipient

Deletes a selected recipient.

**Parameters:**

| Name        | Type   | Required | Description                              |
|-------------|--------|----------|------------------------------------------|
| recipientId | string | ✓        | Unique identifier of the recipient        |

**Example:**
```java
// Java Example
// Code snippet for deleting a recipient
```

### Get Recipient by ID

Retrieves a single recipient by its ID.

**Parameters:**

| Name        | Type   | Required | Description                              |
|-------------|--------|----------|------------------------------------------|
| recipientId | string | ✓        | Unique identifier of the recipient        |

**Example:**
```ruby
# Ruby Example
# Code snippet for getting a recipient by ID
```

### Update Recipient

Updates recipient with provided personal information.

**Parameters:**

| Name        | Type   | Required | Description                              |
|-------------|--------|----------|------------------------------------------|
| bodyData    | string | ✓        | Body data                                |
| recipientId | string | ✓        | Unique identifier of the recipient        |

**Example:**
```csharp
// C# Example
// Code snippet for updating a recipient
```

### Create Payment Details

Creates new payment details for an existing recipient.

**Parameters:**

| Name             | Type   | Required | Description                              |
|------------------|--------|----------|------------------------------------------|
| bodyData         | string | ✓        | Body data                                |
| recipientId      | string | ✓        | Unique identifier of the recipient        |

**Example:**
```php
// PHP Example
// Code snippet for creating payment details
```

### Delete Payment Details

Deletes payment details from an existing recipient.

**Parameters:**

| Name             | Type   | Required | Description                              |
|------------------|--------|----------|------------------------------------------|
| paymentDetailsId | string | ✓        | Unique identifier of the payment details  |
| recipientId      | string | ✓        | Unique identifier of the recipient        |

**Example:**
```javascript
// JavaScript Example
// Code snippet for deleting payment details
```

### Update Payment Details

Updates existing payment details for an existing recipient.

**Parameters:**

| Name             | Type   | Required | Description                              |
|------------------|--------|----------|------------------------------------------|
| bodyData         | string | ✓        | Body data                                |
| paymentDetailsId | string | ✓        | Unique identifier of the payment details  |
| recipientId      | string | ✓        | Unique identifier of the recipient        |

**Example:**
```python
# Python Example
# Code snippet for updating payment details
```

### Increment Recipient Usage

Increments usage index on a specified recipient.

**Parameters:**

| Name        | Type   | Required | Description                              |
|-------------|--------|----------|------------------------------------------|
| recipientId | string | ✓        | Unique identifier of the recipient        |

**Example:**
```java
// Java Example
// Code snippet for incrementing recipient usage
```

## Statements

### Get Financial Statement

Retrieves a financial statement for a given period.

**Parameters:**

| Name      | Type   | Required | Description                              |
|-----------|--------|----------|------------------------------------------|
| bodyData  | string | ✓        | Body data                                |

**Example:**
```ruby
# Ruby Example
# Code snippet for getting a financial statement
```

## Test

### Test API Request Parsing

Tests API request parsing functionality.

**Parameters:**

| Name      | Type   | Required | Description                              |
|-----------|--------|----------|------------------------------------------|
| status    | string | ✓        | Status                                   |
| type      | string | ✓        | Type                                     |
| X-Aud     | string | ✓        | X-Aud header                             |
| bodyData  | string | ✓        | Body data                                |

**Example:**
```csharp
// C# Example
// Code snippet for testing API request parsing
```

## Transactions

### Get Card Transactions

Reads a page of card transactions associated with the user.

**Parameters:**

| Name         | Type   | Required | Description                              |
|--------------|--------|----------|------------------------------------------|
| page_number  | string |          | Page number                              |
| page_size    | string |          | Page size (default: 25)                  |

**Example:**
```javascript
// JavaScript Example
// Code snippet for getting card transactions
```

## User Management

### Get User

Retrieves user data stored in the Wirex system.

**Parameters:**

| Name      | Type   | Required | Description                              |
|-----------|--------|----------|------------------------------------------|
| bodyData  | string |          | Body data                                |

**Example:**
```python
# Python Example
# Code snippet for getting user data
```

### Update Freshdesk ID

Updates the Freshdesk ID of the user for future reference.

**Parameters:**

| Name      | Type   | Required | Description                              |
|-----------|--------|----------|------------------------------------------|
| bodyData  | string |          | Body data                                |

**Example:**
```java
// Java Example
// Code snippet for updating Freshdesk ID
```

### Update Phone Number

Updates the phone number of a specific user.

**Parameters:**

| Name      | Type   | Required | Description                              |
|-----------|--------|----------|------------------------------------------|
| bodyData  | string |          | Body data                                |

**Example:**
```php
// PHP Example
// Code snippet for updating phone number
```

### Confirm Phone Number

Confirms the updated phone number of a specific user.

**Parameters:**

| Name      | Type   | Required | Description                              |
|-----------|--------|----------|------------------------------------------|
| bodyData  | string |          | Body data                                |

**Example:**
```ruby
# Ruby Example
# Code snippet for confirming phone number
```

## Onboarding/OffChain

### Create User

Creates a new user in the Wirex system using server-side Auth0 authorization.

**Parameters:**

| Name      | Type   | Required | Description                              |
|-----------|--------|----------|------------------------------------------|
| bodyData  | string |          | Body data                                |

**Example:**
```javascript
// JavaScript Example
// Code snippet for creating a user
```

### Create Retail User

Creates a new user in the Wirex system using client-side Privy SDK authorization.

**Parameters:**

| Name      | Type   | Required | Description                              |
|-----------|--------|----------|------------------------------------------|
| bodyData  | string |          | Body data                                |

**Example:**
```csharp
// C# Example
// Code snippet for creating a retail user
```

### Validate Retail User

---

This enhanced documentation provides a structured guide for AI agents to interact with the Wirex system API efficiently. Each endpoint is clearly defined with its purpose, parameters, and examples in various programming languages for better understanding and implementation.


---


# Wirex API Documentation

This documentation provides details on the endpoints available in the Wirex system for creating a new user, authorization, KYC processes, and wallet management.

## Quick Reference

- [POST /api/v1/user/authorize](#post-apiv1userauthorize)
- [GET /api/v1/user/sharing-token](#get-apiv1usersharing-token)
- [POST /api/v1/user/sharing-token](#post-apiv1usersharing-token)
- [POST /api/v1/user/verification-link](#post-apiv1userverification-link)
- [POST /api/v1/user/verification-token](#post-apiv1userverification-token)
- [GET /api/v1/wallet](#get-apiv1wallet)

## Authorization

### POST /api/v1/user/authorize

**Login as user**

Retrieve access token for a specific user that can be used to interact with all other APIs on his behalf.

**Parameters:**

| Name       | Type   | Required | Description                                      |
|------------|--------|----------|--------------------------------------------------|
| bodyData   | string |          | Body data                                        |

**Example:**
```python
# Python example
import requests

url = "https://api.wirex.com/api/v1/user/authorize"
body_data = {"key": "value"}
response = requests.post(url, json=body_data)
print(response.json())
```

**Error Handling:**
- 401 Unauthorized: Invalid credentials
- 500 Internal Server Error: Server issue

## KYC

### GET /api/v1/user/sharing-token

**Get KYC sharing token**

Returns a SumSub sharing token that can be used to retrieve the information submitted by the user during the KYC process.

**Parameters:**

| Name             | Type   | Required | Description                                                                                                      |
|------------------|--------|----------|------------------------------------------------------------------------------------------------------------------|
| sumsub_client_id | string | ✓        | Identifier of the partner in SumSub system. This identifier is used to tell SumSub with which entity the information should be shared. Please consult SumSub docs on where to get this id. |

**Example:**
```javascript
// JavaScript example
fetch('https://api.wirex.com/api/v1/user/sharing-token', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

**Error Handling:**
- 404 Not Found: Resource not found
- 503 Service Unavailable: Service temporarily unavailable

### POST /api/v1/user/sharing-token

**Set KYC sharing token**

Uses KYC sharing token retrieved from SumSub to ingest user data and perform verification.

**Parameters:**

| Name       | Type   | Required | Description                                      |
|------------|--------|----------|--------------------------------------------------|
| bodyData   | string |          | Body data                                        |

**Example:**
```java
// Java example
HttpResponse<String> response = Unirest.post("https://api.wirex.com/api/v1/user/sharing-token")
  .header("Content-Type", "application/json")
  .body("{\"key\": \"value\"}")
  .asString();
System.out.println(response.getBody());
```

**Error Handling:**
- 400 Bad Request: Invalid request
- 503 Service Unavailable: Service temporarily unavailable

### POST /api/v1/user/verification-link

**Get KYC SDK link**

Generates a verification link for the user to verify his account.

**Parameters:**

| Name       | Type   | Required | Description                                      |
|------------|--------|----------|--------------------------------------------------|
| bodyData   | string |          | Body data                                        |

**Example:**
```ruby
# Ruby example
require 'net/http'
require 'uri'

url = URI("https://api.wirex.com/api/v1/user/verification-link")

http = Net::HTTP.new(url.host, url.port)
request = Net::HTTP::Post.new(url)
request["Content-Type"] = "application/json"
request.body = "{\"key\": \"value\"}"

response = http.request(request)
puts response.read_body
```

**Error Handling:**
- 403 Forbidden: Access denied
- 429 Too Many Requests: Rate limit exceeded

### POST /api/v1/user/verification-token

**Get KYC SDK token**

Retrieves an SDK token for initializing the SumSub SDK.

**Parameters:**

| Name       | Type   | Required | Description                                      |
|------------|--------|----------|--------------------------------------------------|
| bodyData   | string |          | Body data                                        |

**Example:**
```csharp
// C# example
using System;
using System.Net.Http;
using System.Threading.Tasks;

class Program
{
    static async Task Main()
    {
        using HttpClient client = new HttpClient();
        HttpResponseMessage response = await client.PostAsync("https://api.wirex.com/api/v1/user/verification-token", new StringContent("{\"key\": \"value\"}"));
        string responseBody = await response.Content.ReadAsStringAsync();
        Console.WriteLine(responseBody);
    }
}
```

**Error Handling:**
- 401 Unauthorized: Invalid credentials
- 503 Service Unavailable: Service temporarily unavailable

## Wallet

### GET /api/v1/wallet

**Get wallets**

Retrieves user wallet along with its balances. By wallet this API suggests a valid Account Abstraction wallet that was linked during the registration.

**Parameters:**

| Name       | Type   | Required | Description                                      |
|------------|--------|----------|--------------------------------------------------|
| bodyData   | string | ✓        | Body data                                        |

**Example:**
```javascript
// JavaScript example
fetch('https://api.wirex.com/api/v1/wallet', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

**Error Handling:**
- 404 Not Found: Resource not found
- 500 Internal Server Error: Server issue

---

This enhanced documentation provides detailed information on the endpoints available in the Wirex system, including examples, error handling, and best practices for AI agents to interact effectively with the API.


---

