# KYC

The **KYC section** of the Wirex BaaS API enables partners to seamlessly integrate user identity verification into their onboarding flow using **SumSub**. It provides tools for both **forward-facing verification** (users submit their KYC data) and **reverse sharing** (partners retrieve submitted KYC data).

---

### Key Features

- **SumSub SDK Integration**:
  - Generate a secure **SumSub SDK token** to embed the identity verification widget directly into your frontend.
  - Alternatively, retrieve a **hosted SumSub redirect link** to send users to a pre-built verification experience.

- **Flexible Verification Options**:
  - Support for both embedded and redirect-based SumSub experiences.
  - Allows partners to choose the UX that best fits their product architecture.

- **KYC Data Access via Sharing Token**:
  - Retrieve a **SumSub sharing token** that grants read-only access to KYC data previously submitted by the user.
  - Enables compliance, reporting, or customer support flows on the partner side.

---

By leveraging this section, partners can provide a secure and compliant identity verification experience for users while maintaining flexibility in how and where KYC is presented. Wirex handles all backend integration with SumSub, so partners can focus on delivering a smooth user journey.

## GET /api/v1/user/sharing-token

**Summary:** Get KYC sharing token

**Description:** Returns a SumSub sharing token that can be used to retrieve the information submitted by the user during the KYC process.

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| sumsub_client_id | query | string | ✓ | Identifier of the partner in SumSub system. This identifier is used to tell SumSub with which entity the information should be shared. Please consult SumSub docs on where to get this id. |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

## POST /api/v1/user/sharing-token

**Summary:** Set KYC sharing token

**Description:** Uses KYC sharing token retrieved from SumSub to ingest user data and perform verification

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

## POST /api/v1/user/verification-link

**Summary:** Get KYC SDK link

**Description:** Generates a verification link for the user to verify his account. </br>

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

## POST /api/v1/user/verification-token

**Summary:** Get KYC SDK token

**Description:** Retrieves an SDK token for initializing the SumSub SDK. </br>

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

