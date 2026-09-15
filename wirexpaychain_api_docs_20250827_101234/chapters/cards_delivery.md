# Cards/Delivery

The **Card Delivery APIs** provide details of available delivery providers and their associated costs for physical (non-virtual) card
orders.  
They support region-based delivery rules and courier-specific pricing structures.

> **Note:** Include this section only if your account manager has specifically requested delivery option selection as part of your card
> issuance process.

## GET /api/v1/cards/delivery/countries

**Summary:** Get delivery countries

**Description:** Retrieves list of countries where the card can be delivered for the current corporation</br> > **Note:** This method is applicable only if your account manager has advised you to incorporate card fee handling as part of your integration process.

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

## GET /api/v1/cards/delivery/methods/{country}

**Summary:** Get delivery methods

**Description:** Retrieves list of courier providers that can deliver the card to the specified country</br> > **Note:** This method is applicable only if your account manager has advised you to incorporate card fee handling as part of your integration process.

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| country | path | string | ✓ | Country where the card should be delivered (ISO 3166-1 alpha-2) |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

