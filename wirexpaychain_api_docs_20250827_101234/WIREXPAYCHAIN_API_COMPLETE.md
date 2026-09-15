# Wirex BaaS API
**Version:** 1.0
**Base URL:** `https://api-business.wirexpaychain.tech`
**Generated:** 2025-08-27T10:12:34.330514

## Description

The **Wirex BaaS API** enables partners to deliver non-custodial financial services directly to their retail users. Through a single integration, partners can onboard users, verify identities, issue smart wallet–linked cards, and enable crypto-backed bank transfers—without ever handling fiat or taking custody of user funds.</br>All transactions are powered by **user-owned smart wallets**, ensuring security, transparency, and full user control. Wirex acts as the infrastructure provider, so you can focus on building exceptional user experiences while we handle the heavy lifting.

## Table of Contents

- [Activity Feed](#activity-feed)
- [Authorization](#authorization)
- [Bank](#bank)
- [Cards](#cards)
- [Cards/3DS](#cards/3ds)
- [Cards/Delivery](#cards/delivery)
- [Cards/Details](#cards/details)
- [Cards/Fees](#cards/fees)
- [Cards/Issuance](#cards/issuance)
- [Cards/Management](#cards/management)
- [Confirmation](#confirmation)
- [KYC](#kyc)
- [Onboarding/OffChain](#onboarding/offchain)
- [Rates](#rates)
- [Recipients](#recipients)
- [Statements](#statements)
- [Test](#test)
- [Transactions](#transactions)
- [User Management](#user-management)
- [Wallet](#wallet)

## Activity Feed

### GET /api/v1/activity/feed

**Get activity feed**

Retrieves both transactional and non-transactional activities for the user

---

### GET /api/v1/withdrawal/requests

**Get requested erc withdrawals**

Retrieves requested erc withdrawals for provided account address

---

## Authorization

### POST /api/v1/user/authorize

**Login as user**

Retrieve access token for a specific user that can be used to interact with all other APIs on his behalf

---

## Bank

### GET /api/v1/bank/accounts

**Get bank accounts**

Retrieves a list of bank accounts that belong to the user

---

### POST /api/v1/bank/accounts

**Create bank account**

Activates bank account details for the specified account type

---

### POST /api/v1/bank/transfer

**Execute bank transfer**

Executes the bank transfer either according to the estimation made previously or using current market rates.

---

### POST /api/v1/bank/transfer/estimate

**Estimate bank transfer**

Estimates the amounts that would be charged for a bank transfer according to the current market rates.

---

### POST /api/v2/bank/transfer/estimate

**Estimate bank transfer**

Estimates the amounts that would be charged for a bank transfer according to the current market rates.

---

## Cards

### GET /api/v1/cards

**Get cards**

Retrieves list of cards that belong to the user

---

## Cards/3DS

### GET /api/v1/cards/3ds/requests

**Get active requests**

Retrieves active 3DS requests that need to be either approved or declined

---

### POST /api/v1/cards/3ds/requests/{transactionId}/approve

**Approve request**

Approves 3DS request allowing the transaction to proceed

---

### POST /api/v1/cards/3ds/requests/{transactionId}/decline

**Decline request**

Declines 3DS request blocking the transaction from proceeding

---

## Cards/Delivery

### GET /api/v1/cards/delivery/countries

**Get delivery countries**

Retrieves list of countries where the card can be delivered for the current corporation</br> > **Note:** This method is applicable only if your account manager has advised you to incorporate card fee handling as part of your integration process.

---

### GET /api/v1/cards/delivery/methods/{country}

**Get delivery methods**

Retrieves list of courier providers that can deliver the card to the specified country</br> > **Note:** This method is applicable only if your account manager has advised you to incorporate card fee handling as part of your integration process.

---

## Cards/Details

### POST /api/v1/cards/{cardId}/cvv

**Get card CVV**

Retrieves CVV code for the card using the action confirmation token generated using the **Confirmation** flow

---

### POST /api/v1/cards/{cardId}/details

**Get card details**

Retrieves card PAN and expiry date using the action confirmation token generated using the **Confirmation** flow

---

### POST /api/v1/cards/{cardId}/pin

**Get card pin**

Retrieves card Pin code using the action confirmation token generated using the **Confirmation** flow

---

## Cards/Fees

### GET /api/v1/cards/{type}/fees/{country}

**Get order fees**

Retrieves estimation of fees that should be paid for the card order</br> > **Note:** This method is applicable only if your account manager has advised you to incorporate card fee handling as part of your integration process.

---

### POST /api/v1/cards/{type}/fees/{country}/payment

**Create order fees invoice**

Creates an invoice for payment of the card order fees.</br> > **Note:** This method is applicable only if your account manager has advised you to incorporate card fee handling as part of your integration process.

---

## Cards/Issuance

### POST /api/v1/cards/plastic

**Issue plastic card**

Issues a plastic card for the specified user and sends it to the provided address.

---

### POST /api/v1/cards/virtual

**Issue virtual card**

Issues a virtual card for the specified user

---

### PUT /api/v1/cards/{cardId}/activate

**Activate card**

Activates a card that has been issues to a user and is currently in **NotActivated** state. </br> **Note:** This endpoint is needed only for physical cards to provide additional layer of security in case the card is stolen during delivery.

---

## Cards/Management

### PUT /api/v1/cards/{cardId}/block

**Block card**

Blocks selected card making it impossible to use it for any transactions.

---

### PUT /api/v1/cards/{cardId}/close

**Close card**

Closes the card. This action cannot be undone and the card will be permanently closed.

---

### PUT /api/v1/cards/{cardId}/limit

**Change card limit**

Updates maximum amount that can be spent using the card within a day

---

### PUT /api/v1/cards/{cardId}/name

**Change card name**

Updates the display name of the card

---

### PUT /api/v1/cards/{cardId}/unblock

**Unblock card**

Unblocks selected card allowing it to be used for transactions once again.

---

## Confirmation

### POST /api/v1/confirmation/sms

**Request SMS code**

Sends an SMS to the phone number that was provided by user during KYC process with OTP code.

---

### POST /api/v1/confirmation/sms/verify

**Verify SMS code**

Exchanges an OTP code send via SMS for an action token that can be used to confirm that the action being executed is approved by end-user

---

## KYC

### GET /api/v1/user/sharing-token

**Get KYC sharing token**

Returns a SumSub sharing token that can be used to retrieve the information submitted by the user during the KYC process.

---

### POST /api/v1/user/sharing-token

**Set KYC sharing token**

Uses KYC sharing token retrieved from SumSub to ingest user data and perform verification

---

### POST /api/v1/user/verification-link

**Get KYC SDK link**

Generates a verification link for the user to verify his account. </br>

---

### POST /api/v1/user/verification-token

**Get KYC SDK token**

Retrieves an SDK token for initializing the SumSub SDK. </br>

---

## Onboarding/OffChain

### POST /api/v1/user

**Create user**

Creates a new user in the Wirex system using server side Auth0 authorization.

---

### POST /api/v1/user/retail

**Create retail user**

Creates a new user in the Wirex system using client side Privy SDK authorization.

---

### POST /api/v1/user/retail/validate

**Create retail user**

Creates a new user in the Wirex system using client side Privy SDK authorization.

---

## Rates

### GET /api/v1/rates

**Get rates**

Retrieves real-time exchange rates for a list of provided tickers. Each ticker represents a currency or asset pair (e.g., `USDT/USD`, `DAI/EUR`). The response includes the latest conversion rate for each requested

---

## Recipients

### GET /api/v1/recipients

**Get recipients**

Retrieves all recipients sorted by the full name

---

### POST /api/v1/recipients

**Create recipient**

Creates a new recipient with provided personal information

---

### GET /api/v1/recipients/filter/catalog

**Get by catalog**

Retrieves recipients filtered by the catalog index. Catalog index is the first letter of the full name, so basically filtering by catalog index provides you with pretty much old yellow pages experience.

---

### GET /api/v1/recipients/filter/currency

**Get by currency**

Retrieves recipients filtered by the availability of the requested currency among existing recipient payment details.

---

### GET /api/v1/recipients/filter/name

**Get by name**

Retrieves recipients filtered by the presence of passed name substring in the full name of the recipient.

---

### GET /api/v1/recipients/filter/type

**Get by type**

Retrieves recipients filtered by availability of the payment details of the passed type.

---

### DELETE /api/v1/recipients/{recipientId}

**Delete recipient**

Deletes selected recipient

---

### GET /api/v1/recipients/{recipientId}

**Get by catalog**

Retrieves single recipient by its id.

---

### PUT /api/v1/recipients/{recipientId}

**Update recipient**

Updates recipient with provided personal information

---

### POST /api/v1/recipients/{recipientId}/payment_details

**Create payment details**

Creates new payment details for existing recipient

---

### DELETE /api/v1/recipients/{recipientId}/payment_details/{paymentDetailsId}

**Delete payment details**

Deletes payment details from existing recipient

---

### PUT /api/v1/recipients/{recipientId}/payment_details/{paymentDetailsId}

**Update payment details**

Updates existing payment details for existing recipient

---

### POST /api/v1/recipients/{recipientId}/usage

**Increment recipient usage**

Increments usage index on specified recipient. Usage index is later used to determine recipient's priority in the list of recipients.

---

## Statements

### POST /api/v1/statements

**Get financial statement**

Retrieves financial statement for given period. Returns statement_id in case statement is pending to generate, otherwise returns full object. Upon statement generation ws server will notify with id and owner

---

## Test

### GET /api/v1/test/{type}

**Test api request parsing**

This one exists only to test that API request parsing works correctly from body, query, path and header

---

## Transactions

### GET /api/v1/transactions/card

**Get card transactions**

Reads a page of card transactions associated with user

---

## User Management

### GET /api/v1/user

**Get user**

Retrieves the user data stored in Wirex system

---

### PUT /api/v1/user/freshdesk-id

**Update freshdesk id**

Updates freshdesk id of the user that can be used to restore omni-chats down the road.

---

### PUT /api/v1/user/phone-number

**Update phone number**

Update the phone number of a specific user in the system.</br>This endpoint allows updating and validating the user's phone number to maintain account security and contact accuracy.

---

### PUT /api/v1/user/phone-number/confirm

**Confirm phone number**

Update the phone number of a specific user in the system.</br>This endpoint allows updating and validating the user's phone number to maintain account security and contact accuracy.

---

## Wallet

### GET /api/v1/wallet

**Get wallets**

Retrieves user wallet along with its balances. By wallet this API suggests a valid Account Abstraction wallet that was linked during the registration.

---

