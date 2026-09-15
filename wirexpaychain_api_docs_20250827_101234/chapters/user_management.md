# User Management

The **User Management APIs** provide partners with essential tools to manage user identity and contact information within the Wirex ecosystem. These endpoints are focused on reading user profiles, updating key data, and confirming contact details to ensure a secure and compliant user experience.

---

### Key Features:

- **User Data Retrieval**:
  - Fetch detailed user profile information, including status, identifiers, and associated wallet data.
  - Ensure your system remains synchronized with the Wirex platform.

- **Phone Number Management**:
  - Update a user’s phone number with support for country codes and formatting.
  - Supports user-driven or admin-initiated contact information updates.

- **Phone Number Confirmation**:
  - Confirm the user’s phone number via OTP-based verification.
  - Ensures that users have validated, active contact details for compliance and support purposes.

---

By integrating these User APIs, partners can maintain accurate user records, streamline contact verification, and enhance the overall reliability and integrity of user data within their applications.

## GET /api/v1/user

**Summary:** Get user

**Description:** Retrieves the user data stored in Wirex system

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

## PUT /api/v1/user/freshdesk-id

**Summary:** Update freshdesk id

**Description:** Updates freshdesk id of the user that can be used to restore omni-chats down the road.

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

## PUT /api/v1/user/phone-number

**Summary:** Update phone number

**Description:** Update the phone number of a specific user in the system.</br>This endpoint allows updating and validating the user's phone number to maintain account security and contact accuracy.

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

## PUT /api/v1/user/phone-number/confirm

**Summary:** Confirm phone number

**Description:** Update the phone number of a specific user in the system.</br>This endpoint allows updating and validating the user's phone number to maintain account security and contact accuracy.

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

