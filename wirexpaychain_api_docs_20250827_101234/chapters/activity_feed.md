# Activity Feed

The **Activity Feed APIs** enable partners to access a detailed, chronological view of a retail user's actions within the platform. These APIs provide transparency into key transactional and operational events, helping partners deliver real-time insights and enhanced user experiences.

### Key Features:

- **Comprehensive Activity Tracking**:
    - Access a full history of user activity, including payments, transfers, and operational events.
    - Ensure transparency across key user interactions with the platform.

- **Event Filtering & Categorization**:
    - Filter activities by action type (e.g., card payment, bank transfer) and activity subject (e.g., card, account).
    - Enable tailored views of user behavior for reporting or support use cases.

- **Chronological Feed Structure**:
    - Events are presented in a time-ordered format for clear activity timelines.
    - Easily integrate with user dashboards or support tools.

- **Real-Time Synchronization**:
    - Designed for near real-time updates to reflect the most recent user actions.
    - Ideal for monitoring recent transactions or building dynamic activity interfaces.

---

With the Activity Feed APIs, partners gain a powerful tool to monitor user behavior, enhance visibility into platform usage, and build features that promote trust, engagement, and support responsiveness.

## GET /api/v1/activity/feed

**Summary:** Get activity feed

**Description:** Retrieves both transactional and non-transactional activities for the user

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| page_number | query | string |  | PageNumber number |
| page_size | query | string |  | Size of the page. If no page size is provided, default page size is used (25). |
| subject | query | string |  | Filter by subject (wallet address, card ID, or account reference) (<span style="color:red">SHOULD NOT</span> be provided if types are provided) |
| types | query | string |  | Filter by activity types (<span style="color:red">SHOULD NOT</span> be provided if subject is provided) |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

## GET /api/v1/withdrawal/requests

**Summary:** Get requested erc withdrawals

**Description:** Retrieves requested erc withdrawals for provided account address

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

