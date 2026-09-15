# Recipients

## GET /api/v1/recipients

**Get recipients**

Retrieves all recipients sorted by the full name

---

## POST /api/v1/recipients

**Create recipient**

Creates a new recipient with provided personal information

---

## GET /api/v1/recipients/filter/catalog

**Get by catalog**

Retrieves recipients filtered by the catalog index. Catalog index is the first letter of the full name, so basically filtering by catalog index provides you with pretty much old yellow pages experience.

---

## GET /api/v1/recipients/filter/currency

**Get by currency**

Retrieves recipients filtered by the availability of the requested currency among existing recipient payment details.

---

## GET /api/v1/recipients/filter/name

**Get by name**

Retrieves recipients filtered by the presence of passed name substring in the full name of the recipient.

---

## GET /api/v1/recipients/filter/type

**Get by type**

Retrieves recipients filtered by availability of the payment details of the passed type.

---

## DELETE /api/v1/recipients/{recipientId}

**Delete recipient**

Deletes selected recipient

---

## GET /api/v1/recipients/{recipientId}

**Get by catalog**

Retrieves single recipient by its id.

---

## PUT /api/v1/recipients/{recipientId}

**Update recipient**

Updates recipient with provided personal information

---

## POST /api/v1/recipients/{recipientId}/payment_details

**Create payment details**

Creates new payment details for existing recipient

---

## DELETE /api/v1/recipients/{recipientId}/payment_details/{paymentDetailsId}

**Delete payment details**

Deletes payment details from existing recipient

---

## PUT /api/v1/recipients/{recipientId}/payment_details/{paymentDetailsId}

**Update payment details**

Updates existing payment details for existing recipient

---

## POST /api/v1/recipients/{recipientId}/usage

**Increment recipient usage**

Increments usage index on specified recipient. Usage index is later used to determine recipient's priority in the list of recipients.

---

