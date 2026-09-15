# Rates

The **Rate APIs** offers real-time access to currency and token exchange rates based on a list of requested tickers. This API enables partners to retrieve precise conversion rates for assets supported by the platform, supporting pricing, trading, and balance calculations.

### Key Features:

- **Batch Ticker Support**:
    - Retrieve exchange rates for multiple tickers in a single request.
    - Designed for efficient use in dashboards, pricing engines, or portfolio summaries.

- **Real-Time Rate Data**:
    - Get the latest exchange rates between fiat currencies and supported crypto assets.
    - Optimized for high-frequency access with minimal latency.

---

With the Rate API, partners can offer accurate and dynamic asset pricing, power user interfaces with live data, and support conversion logic across a wide range of assets.

## GET /api/v1/rates

**Summary:** Get rates

**Description:** Retrieves real-time exchange rates for a list of provided tickers. Each ticker represents a currency or asset pair (e.g., `USDT/USD`, `DAI/EUR`). The response includes the latest conversion rate for each requested

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| tickers | query | string | ✓ |  |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

