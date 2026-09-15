# Confirmation

The **Confirmation APIs** enable partners to securely validate user actions through OTP-based verification mechanisms. These endpoints support SMS delivery and OTP token exchange, ensuring end-user authorization for sensitive operations.

### Key Features:

- **OTP via SMS**:
  - Trigger the sending of an OTP code via SMS to the user’s registered phone number.
  - Designed to support actions such as phone verification or viewing sensitive card details.

- **Secure Verification Flow**:
  - Verify the submitted OTP code and receive an action token in return.
  - Ensures that only authorized users can complete critical operations.

- **Action-Based Context**:
  - Each OTP session is linked to a specific action type (e.g., verifying phone or accessing card data).
  - Prevents unauthorized use of tokens outside their intended context.

---

With the Confirmation APIs, partners can implement robust second-factor verification flows that protect sensitive user operations, enhance compliance, and build trust with minimal integration overhead.

## POST /api/v1/confirmation/sms

**Summary:** Request SMS code

**Description:** Sends an SMS to the phone number that was provided by user during KYC process with OTP code.

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

## POST /api/v1/confirmation/sms/verify

**Summary:** Verify SMS code

**Description:** Exchanges an OTP code send via SMS for an action token that can be used to confirm that the action being executed is approved by end-user

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

